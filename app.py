import streamlit as st
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import io
import base64

# -----------------------------
# 🔧 Utility Functions
# -----------------------------
def extract_lsb_plane(image: Image.Image):
    img = image.convert('RGB')
    img_array = np.array(img)

    lsb_r = img_array[:, :, 0] & 1
    lsb_g = img_array[:, :, 1] & 1
    lsb_b = img_array[:, :, 2] & 1

    # Combine channels to average LSB pattern
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
    deviation = abs(zeros - ones) / total
    confidence = (1 - deviation) * 100  # Closer to 50-50 means more suspicious
    return confidence

# -----------------------------
# 🖥 Streamlit UI
# -----------------------------
st.set_page_config(page_title="StegoScan - LSB Steganography Detector", layout="centered")
st.title("🔍 StegoScan")
st.markdown("Upload an image and detect possible hidden content using LSB analysis.")

uploaded_file = st.file_uploader("📁 Upload an Image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    st.subheader("🔬 LSB Analysis")
    lsb_array = extract_lsb_plane(image)
    lsb_map_fig = plot_lsb_map(lsb_array)
    st.pyplot(lsb_map_fig)

    st.subheader("📊 Bit Histogram")
    hist_fig, zeros, ones = plot_bit_histogram(image)
    st.pyplot(hist_fig)

    confidence = detect_stego_score(zeros, ones)
    result_text = "✅ Possible Stego Content Detected" if confidence > 65 else "🟩 No Significant Stego Evidence"

    st.subheader("🔎 Detection Result")
    st.markdown(f"*Result:* {result_text}")
    st.markdown(f"*Confidence Score:* {confidence:.2f}%")

    # Optional: Generate download link for simple report
    if st.button("📄 Generate Report"):
        report = f"""
StegoScan Detection Report
---------------------------
File: {uploaded_file.name}
Result: {result_text}
Confidence Score: {confidence:.2f}%
Even bits (0): {zeros}
Odd bits (1): {ones}
Image Size: {image.size[0]}x{image.size[1]}
"""
        st.download_button(
            label="📥 Download Report as TXT",
            data=report,
            file_name="stegoscan_report.txt",
            mime="text/plain"
        )

else:
    st.info("Please upload an image to begin analysis.")