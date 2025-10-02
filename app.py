import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
# Import ReportLab components
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# -----------------------------
# 🔧 Utility Functions (Kept same for brevity)
# -----------------------------
def extract_lsb_plane(image: Image.Image):
    img = image.convert('RGB')
    img_array = np.array(img)
    lsb_r = img_array[:, :, 0] & 1
    lsb_g = img_array[:, :, 1] & 1
    lsb_b = img_array[:, :, 2] & 1
    lsb_combined = (lsb_r + lsb_g + lsb_b) / 3.0
    return lsb_combined

def plot_lsb_map(lsb_array):
    fig, ax = plt.subplots()
    ax.imshow(lsb_array, cmap='gray')
    ax.set_title("LSB Map")
    ax.axis('off')
    return fig

def plot_bit_histogram(image: Image.Image):
    gray_img = image.convert('L')
    pixels = np.array(gray_img).flatten()
    lsb = pixels & 1
    zeros = np.count_nonzero(lsb == 0)
    ones = np.count_nonzero(lsb == 1)
    fig, ax = plt.subplots()
    ax.bar(['0 (even)', '1 (odd)'], [zeros, ones], color=['blue', 'red'])
    ax.set_title("LSB Bit Frequency")
    return fig, zeros, ones

def detect_stego_score(zeros, ones):
    total = zeros + ones
    if total == 0:
        return 0.0
    deviation = abs(zeros - ones) / total
    confidence = (1 - deviation) * 100
    return confidence

def decode_lsb_text(image: Image.Image, max_chars: int = 500, mode: str = 'R') -> bytes:
    img_array = np.array(image.convert('RGB'))
    if mode == 'R':
        lsb_bits = (img_array[:, :, 0] & 1).flatten()
    elif mode == 'RGB':
        R_lsb = (img_array[:, :, 0] & 1).flatten()
        G_lsb = (img_array[:, :, 1] & 1).flatten()
        B_lsb = (img_array[:, :, 2] & 1).flatten()
        total_pixels = R_lsb.size
        lsb_bits = np.empty(total_pixels * 3, dtype=np.uint8)
        lsb_bits[0::3] = R_lsb
        lsb_bits[1::3] = G_lsb
        lsb_bits[2::3] = B_lsb
    else:
        return b""

    bits_to_extract = min(len(lsb_bits), max_chars * 8)
    lsb_bits = lsb_bits[:bits_to_extract]
    bit_string = ''.join(map(str, lsb_bits))
    decoded_bytes = bytearray()
    
    for i in range(0, len(bit_string) // 8 * 8, 8):
        byte_bits = bit_string[i:i+8]
        byte_val = int(byte_bits, 2)
        decoded_bytes.append(byte_val)
        if byte_val == 0:
            break
            
    return bytes(decoded_bytes)


# -----------------------------
# 📄 PDF Generation Function (Improved UI)
# -----------------------------
def generate_pdf_report(uploaded_file, image: Image.Image, lsb_map_fig, hist_fig, zeros, ones, confidence, result_text, report_decoded_text, hex_report_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            title="StegoScan Report",
                            leftMargin=inch/2, rightMargin=inch/2,
                            topMargin=inch/2, bottomMargin=inch/2)
    
    styles = getSampleStyleSheet()
    
    # Customize standard styles
    styles['Heading1'].fontSize = 18
    styles['Heading1'].leading = 22
    styles['Heading1'].spaceAfter = 12
    styles['Heading1'].fontName = 'Helvetica-Bold'
    
    styles['Heading2'].fontSize = 14
    styles['Heading2'].leading = 18
    styles['Heading2'].spaceAfter = 8
    styles['Heading2'].fontName = 'Helvetica-Bold'
    
    # Style for headings within the section (like 'Decoded Text')
    styles.add(ParagraphStyle(name='SectionHeading', 
                              fontSize=12, 
                              leading=14, 
                              fontName='Helvetica-Bold', # Bolded for visibility
                              spaceBefore=10, 
                              spaceAfter=5,
                              textColor=colors.darkred)) # Use a distinct color

    # CodeStyle for the box around hex/decoded text
    styles.add(ParagraphStyle(name='CodeStyle', 
                              fontSize=10, 
                              leading=12, 
                              fontName='Courier',
                              textColor=colors.blue,
                              borderPadding=(6, 6, 6, 6), # Increased padding
                              borderColor=colors.HexColor('#CCCCCC'),
                              borderWidth=1,
                              backColor=colors.HexColor('#F0F0FF'))) # Light blue background for emphasis

    elements = []
    
    # --- Title Section ---
    elements.append(Paragraph("StegoScan Detection Report", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    # --- Summary Table ---
    summary_data = [
        ["Metric", "Value"],
        ["File Name:", uploaded_file.name],
        ["Result:", result_text],
        ["Confidence Score:", f"{confidence:.2f}%"],
        ["Image Dimensions:", f"{image.size[0]}x{image.size[1]}"],
        ["Total Pixels:", f"{image.size[0]*image.size[1]}"],
        ["LSB Zeros (0):", f"{zeros}"],
        ["LSB Ones (1):", f"{ones}"],
    ]
    summary_table = Table(summary_data, colWidths=[2.5*inch, 4.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DDDDDD')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(Paragraph("## Analysis Summary", styles['Heading2']))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.2 * inch))
    
    # --- Visual Analysis ---
    elements.append(Paragraph("## Visual LSB Analysis", styles['Heading2']))
    
    # Save Matplotlib figures to buffers
    lsb_img_buffer = io.BytesIO()
    lsb_map_fig.savefig(lsb_img_buffer, format='png', bbox_inches='tight')
    lsb_img_buffer.seek(0)
    
    hist_img_buffer = io.BytesIO()
    hist_fig.savefig(hist_img_buffer, format='png', bbox_inches='tight')
    hist_img_buffer.seek(0)
    
    # Add LSB Map
    elements.append(Paragraph("LSB Map:", styles['Normal']))
    elements.append(RLImage(lsb_img_buffer, width=3*inch, height=3*inch))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Add Bit Histogram
    elements.append(Paragraph("LSB Bit Frequency Histogram:", styles['Normal']))
    elements.append(RLImage(hist_img_buffer, width=3*inch, height=2.5*inch))
    elements.append(Spacer(1, 0.2 * inch))

    # --- Hidden Content Section (IMPROVED UI) ---
    # The main heading is bolded by using styles['Heading2']
    elements.append(Paragraph("## Hidden Content Extraction", styles['Heading2'])) 
    
    # Decoded Text Sub-Section (Bolded Title)
    elements.append(Paragraph("Decoded Text (UTF-8/ASCII - BEST ATTEMPT):", styles['SectionHeading']))
    
    # The Decoded Text is formatted using a Preformatted block for monospace and boxed look
    # Preformatted respects newlines, so we replace <br/> with actual newlines for presentation.
    decoded_text_for_preformatted = report_decoded_text.replace('<br/>', '\n') 
    
    elements.append(Preformatted(decoded_text_for_preformatted, styles['CodeStyle']))
    elements.append(Spacer(1, 0.1 * inch))
    
    # Raw Hex Data Sub-Section (Bolded Title)
    elements.append(Paragraph("Raw Hex Data (First 1KB - R,G,B Sequential):", styles['SectionHeading']))
    
    # The Hex Data is formatted using a Preformatted block for monospace and boxed look
    # Break hex data into multiple lines for PDF readability
    hex_lines = [hex_report_data[i:i+90] for i in range(0, len(hex_report_data), 90)]
    hex_data_for_preformatted = '\n'.join(hex_lines)
    
    elements.append(Preformatted(hex_data_for_preformatted, styles['CodeStyle']))
        
    elements.append(Spacer(1, 0.5 * inch))

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()


# -----------------------------
# 🖥 Streamlit UI (Rest of the script is unchanged logic-wise)
# -----------------------------
st.set_page_config(page_title="StegoScan - LSB Steganography Detector", layout="centered")
st.title("🔍 StegoScan")
st.markdown("Upload an image and detect possible hidden content using LSB analysis.")

uploaded_file = st.file_uploader("📁 Upload an Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    
    # --- LSB Analysis & Histogram ---
    st.subheader("🔬 LSB Analysis")
    lsb_array = extract_lsb_plane(image)
    lsb_map_fig = plot_lsb_map(lsb_array)
    st.pyplot(lsb_map_fig)
    
    st.subheader("📊 Bit Histogram")
    hist_fig, zeros, ones = plot_bit_histogram(image)
    st.pyplot(hist_fig)

    confidence = detect_stego_score(zeros, ones)
    result_text = "✅ Possible Stego Content Detected" if confidence > 65 else "🟩 No Significant Stego Evidence"

    # --- Detection Result ---
    st.subheader("🔎 Detection Result")
    st.markdown(f"*Result:* **{result_text}**")
    st.markdown(f"*Confidence Score:* **{confidence:.2f}%**")

    r_channel_text_result = ""
    rgb_channel_text_result = ""

    # --- Hidden Text Decoder ---
    st.markdown("---")
    st.header("🔓 Possible Hidden Text Decoder")
    st.markdown("This section attempts to **extract and decode** the LSB data, as the exact encoding method (channel, encryption, compression, stop-marker) is usually unknown.")
    
    extracted_bytes_r = decode_lsb_text(image, max_chars=1000, mode='R')
    extracted_bytes_rgb = decode_lsb_text(image, max_chars=1000, mode='RGB')
    extracted_bytes_combined = extracted_bytes_rgb if len(extracted_bytes_rgb) > len(extracted_bytes_r) else extracted_bytes_r

    if extracted_bytes_r or extracted_bytes_rgb:
        
        # --- Decoding Attempt 1: Red Channel Only ---
        st.subheader("1️⃣ Attempt: ASCII/UTF-8 Text (Red Channel LSB)")
        try:
            text_result_raw = extracted_bytes_r.decode('utf-8', errors='ignore')
            r_channel_text_result = text_result_raw.rstrip('\x00').strip()
            if r_channel_text_result:
                st.code(r_channel_text_result, language='text')
            else:
                st.code("no text hidden using this format", language='text')
        except Exception:
            st.code("no text hidden using this format", language='text')


        # --- Decoding Attempt 2: R, G, B Channels Sequentially (Direct Binary) ---
        st.subheader("2️⃣ Attempt: ASCII/UTF-8 Text (R, G, B Sequential LSB)")
        try:
            text_result_raw = extracted_bytes_rgb.decode('utf-8', errors='ignore')
            rgb_channel_text_result = text_result_raw.rstrip('\x00').strip()
            
            if rgb_channel_text_result:
                st.code(rgb_channel_text_result, language='text')
            else:
                st.code("no text hidden using this format", language='text')
        except Exception:
            st.code("no text hidden using this format", language='text')
            
        # --- Raw Data View ---
        st.subheader("3️⃣ Raw Data: Hexadecimal Format (From R, G, B Sequential)")
        hex_data = extracted_bytes_combined[:1024].hex()
        formatted_hex = ' '.join(hex_data[i:i+2] for i in range(0, len(hex_data), 2))
        st.code(formatted_hex, language='text')
        st.caption(f"Showing the first {len(extracted_bytes_combined)} bytes of the most extracted LSB data (R, G, B Sequential).")
        
    else:
        st.info("The carrier image is too small or no data was extracted for decoding.")
        st.subheader("1️⃣ Attempt: ASCII/UTF-8 Text (Red Channel LSB)")
        st.code("no text hidden using this format", language='text')
        st.subheader("2️⃣ Attempt: ASCII/UTF-8 Text (R, G, B Sequential LSB)")
        st.code("no text hidden using this format", language='text')
    
    # -----------------------------
    # REPORT GENERATION SECTION (WITH FORMAT SELECTION)
    # -----------------------------
    st.markdown("---")
    st.header("📄 Export Detailed Report")
    
    # --- Format Selection ---
    report_format = st.selectbox(
        "**Select Report Format**",
        ("PDF (Formatted Report)", "TXT (Raw Text)", "CSV (Data Table)"),
        index=0,
        help="Choose the desired format for your analysis report."
    )
    st.markdown("<br>", unsafe_allow_html=True) # Add a little space

    # Logic to consolidate results for report generation
    report_decoded_text = "No recognizable text found in any tested format."
    if rgb_channel_text_result:
        report_decoded_text = f"Mode: R, G, B Sequential LSB\nContent: {rgb_channel_text_result}"
    elif r_channel_text_result:
        report_decoded_text = f"Mode: Red Channel Only LSB\nContent: {r_channel_text_result}"
    
    hex_report_data = 'N/A - No LSB data extracted.'
    if extracted_bytes_combined:
        hex_report_data = ' '.join(extracted_bytes_combined[:1024].hex()[i:i+2] for i in range(0, len(extracted_bytes_combined[:1024].hex()), 2))
            
    # --- 1. Generate TXT Report ---
    if report_format == "TXT (Raw Text)":
        report_txt = f"""
StegoScan Detection Report
---------------------------
File: {uploaded_file.name}
Result: {result_text}
Confidence Score: {confidence:.2f}%
Image Dimensions: {image.size[0]}x{image.size[1]}
Total Pixels: {image.size[0]*image.size[1]}

LSB BIT ANALYSIS (Grayscale LSB):
Even bits (0): {zeros}
Odd bits (1): {ones}

--- Hidden Content Attempt (LSB Decoding) ---
Decoded Text (UTF-8/ASCII - BEST ATTEMPT):
{report_decoded_text}

Raw Hex Data (First 1KB - R,G,B Sequential):
{hex_report_data}
"""
        st.download_button(
            label="📥 Download Report as TXT",
            data=report_txt,
            file_name="stegoscan_report.txt",
            mime="text/plain",
            help="Download the raw text version of the analysis."
        )
    
    # --- 2. Generate CSV Report (Numerical Data) ---
    elif report_format == "CSV (Data Table)":
        data = {
            'Metric': ['File Name', 'Stego Result', 'Confidence Score (%)', 'Image Width', 'Image Height', 'Total Pixels', 'LSB Zeros (0)', 'LSB Ones (1)'],
            'Value': [uploaded_file.name, result_text, f"{confidence:.2f}", image.size[0], image.size[1], image.size[0]*image.size[1], zeros, ones]
        }
        df = pd.DataFrame(data)
        
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue().encode()
        
        st.download_button(
            label="📊 Download Report as CSV",
            data=csv_data,
            file_name="stegoscan_report.csv",
            mime="text/csv",
            help="Download the core numerical analysis data as a spreadsheet."
        )

    # --- 3. Generate PDF Report (Properly Formatted) ---
    elif report_format == "PDF (Formatted Report)":
        try:
            # Re-run plotting functions to get fresh figures for PDF generation
            # (Ensuring they are not the ones already displayed in the Streamlit UI)
            lsb_array_pdf = extract_lsb_plane(image)
            lsb_map_fig_pdf = plot_lsb_map(lsb_array_pdf)
            hist_fig_pdf, _, _ = plot_bit_histogram(image)

            pdf_data = generate_pdf_report(uploaded_file, image, lsb_map_fig_pdf, hist_fig_pdf, zeros, ones, confidence, result_text, report_decoded_text, hex_report_data)

            st.download_button(
                label="📄 Download Report as PDF",
                data=pdf_data,
                file_name="stegoscan_report.pdf",
                mime="application/pdf",
                help="Download a formal, visually formatted PDF report including graphs."
            )
            
            # Ensure figures used *only* for PDF are closed immediately after use
            plt.close(lsb_map_fig_pdf)
            plt.close(hist_fig_pdf)
            
        except Exception as e:
            st.error(f"Error generating PDF: {e}. Ensure 'reportlab' is installed (`pip install reportlab`).")
            
else:
    st.info("Please upload an image to begin analysis.")