# 🔍 StegoScan - Automated Steganography Detection and Analysis

StegoScan is a lightweight, web-based tool that detects the presence of hidden messages in image files using **Least Significant Bit (LSB) steganalysis**. Built for academic and forensic purposes, this tool allows users to upload images, analyze embedded stego data, and visualize patterns for detailed inspection.

---

## 🎯 Features

- 🖼️ Upload and preview any `.jpg`, `.jpeg`, or `.png` image  
- 🔬 Perform LSB bit-plane analysis across RGB channels  
- 📊 Visualize stego patterns using grayscale maps and bit histograms  
- 🧠 Confidence score estimation based on statistical deviation  
- 📄 Downloadable detection report (TXT, CSV, PDF format)  

---

## 🚀 Live Demo

👉 [Launch App on Streamlit Cloud](https://stegoscan.streamlit.app)  


---

## 🛠️ Tech Stack

- **Python 3.10+**
- **Streamlit** – Frontend UI framework
- **Pillow (PIL)** – Image handling
- **NumPy** – Array operations
- **Matplotlib** – Visualization

---

## 📦 Installation (For Local Testing)

```bash
# Clone the repo
git clone https://github.com/Dheerajvishwakarma2004/Stego_scan.git
cd Stego_scan
```
```bash
# Install dependencies
pip install -r requirements.txt
```
```bash
# Run the Streamlit app
streamlit run app.py
```
