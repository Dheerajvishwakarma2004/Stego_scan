# 🔍 StegoScan – Automated Steganography Detection & Analysis

StegoScan is a **web-based forensic and academic tool** for detecting hidden messages in images using *Least Significant Bit (LSB) steganalysis*.
It enables users to upload images, analyze embedded stego data, and visualize patterns with **interactive reports** for deeper inspection.

---

## 📖 Table of Contents
- [✨ Key Features](#-key-features)
- [🚀 Live Demo](#-live-demo)
- [🛠 Tech Stack](#-tech-stack)
- [⚙️ Installation](#️-installation)
- [▶️ Usage](#️-usage)
- [📄 Report Formats](#-report-formats)
- [📊 Example Analysis Workflow](#-example-analysis-workflow)
- [👨‍💻 Developers](#-developers)

---

## ✨ Key Features

- 🖼 **Upload & Preview**: Supports `.jpg`, `.jpeg`, `.png` images.
- 🔬 **Bit-Plane Analysis**: Inspect LSB data across **RGB channels**.
- 📊 **Visualizations**:
    - LSB grayscale maps
    - Frequency histograms
- 🧠 **Confidence Score**: Stego likelihood estimation via statistical deviation.
- 🔓 **Hidden Text Decoder**: Attempts extraction from:
    - Red channel LSB
    - Sequential RGB channels
- 📄 **Report Export Options**:
    - **PDF** → Multi-page, styled with charts, tables, decoded text & hex dump.
    - **TXT** → Raw text summary.
    - **CSV** → Structured numeric/statistical data.

---

## 🚀 Live Demo

👉 [Try StegoScan on Streamlit Cloud](https://stegoscan.streamlit.app)

---

## 🛠 Tech Stack

- **Python 3.10+**
- [Streamlit](https://streamlit.io/) – UI Framework
- [Pillow (PIL)](https://python-pillow.org/) – Image Processing
- [NumPy](https://numpy.org/) – Matrix Operations
- [Matplotlib](https://matplotlib.org/) – Data Visualization
- [Pandas](https://pandas.pydata.org/) – Structured Data Handling
- [ReportLab](https://www.reportlab.com/) – Professional PDF Generation

---

## ⚙️ Installation

Clone the repository and install the dependencies:

```bash
# Clone the repository
git clone https://github.com/Dheerajvishwakarma2004/Stego_scan.git
cd Stego_scan

# Install dependencies
pip install -r requirements.txt
````

-----

## ▶️ Usage

1.  Launch the app with:
    ```bash
    streamlit run app.py
    ```
2.  Upload an image file (`.jpg`, `.jpeg`, `.png`).
3.  Inspect the analysis outputs:
      * LSB map visualization
      * Frequency histogram
      * Stego confidence score
      * Attempted decoded text
4.  Export findings into PDF, TXT, or CSV.

-----

## 📄 Report Formats

  * **PDF (Recommended)**: Formatted, multi-page document with visuals & tables.
  * **TXT**: Plain text version of results.
  * **CSV**: Spreadsheet-ready structured numerical data.

-----

## 📊 Example Analysis Workflow

1.  **Upload**: Provide a sample `.png` image.
2.  **Analyze**: View LSB bit-planes & histograms.
3.  **Interpret**: Check the confidence score to detect hidden data.
4.  **Decode**: Attempt extraction of hidden text from channel LSBs.
5.  **Export**: Save the investigation as PDF/TXT/CSV for further reporting.

-----

## 👨‍💻 Developers

StegoScan is developed & maintained by:

  * [Dheeraj Vishwakarma](https://github.com/Dheerajvishwakarma2004)
  * [Sourajeet Sahoo](https://github.com/SourajeetOfficial)
  * [Reeti Vyas](https://github.com/reetivyas)

-----
