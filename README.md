# LogBook
# 🛢️ Bina Refinery Voice-Enabled Log Book

A Streamlit-based log book application designed for real-time tracking of equipment parameters at **Bina Refinery**. Operators can input values using **voice commands**, and each entry is **automatically timestamped** and saved to an **Excel sheet**. The app is tailored to handle multiple equipments, each with different sets of parameters.

---

## 🚀 Features

- 🎙️ **Voice Input** for parameter logging (SpeechRecognition integrated)
- ⏱️ **Automatic Timestamping** for each entry
- 🧾 **Excel-based Logging** (`.xlsx`) using `openpyxl` and `pandas`
- ⚙️ **Supports 10 Equipments** – Each can have different parameters
- 🔐 **Future Scope**: Secure access with face authentication

---

## 📸 Demo

_Coming soon..._

---

## 📁 Folder Structure

📦 LogBook
┣ 📄 app.py # Main Streamlit application
┣ 📄 refinery_log.xlsx # Excel file storing logs
┣ 📄 requirements.txt # Dependencies
┣ 📄 utils.py # (Optional) helper functions
┗ 📄 README.md # This file

## 🧪 Example Use Case

1. Operator selects an equipment (e.g., **Pump #3**).
2. Chooses a parameter (e.g., **Temperature**).
3. Clicks "Record via Voice" → Speaks the value.
4. App transcribes input, logs it along with timestamp in Excel.

---

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/harshitaa18/LogBook.git
cd LogBook
