# SiAdin & Kulino Auto Login (Firefox/Chrome)

Automates login to [SiAdin](https://mhs.dinus.ac.id/) and [Kulino](https://kulino.dinus.ac.id/) using Selenium WebDriver in Firefox or Chrome.

This tool is useful for students of **Universitas Dian Nuswantoro (UDINUS)** to quickly log into their academic portals without manually entering credentials.

---

## 📑 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Dependencies](#dependencies)
- [Contributors](#contributors)
- [License](#license)

---

## 📌 Introduction

This Python-based automation project logs you into:
- **SiAdin**: [https://mhs.dinus.ac.id](https://mhs.dinus.ac.id)
- **Kulino**: [https://kulino.dinus.ac.id](https://kulino.dinus.ac.id)

It uses Selenium with either **Firefox** (`geckodriver.exe`) or **Chrome** (`chromedriver.exe`) to open the browser and complete the login steps.

---

## ✨ Features

- Automated login to SiAdin and Kulino.
- Supports both **Firefox** and **Chrome**.
- Downloads missing WebDriver binaries automatically.
- Lightweight and configurable.
- Compatible with Windows systems.

---

## 💾 Installation

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/yourusername/SiAdin_Login_Firefox.git
   ```

2. **Navigate to the folder**
   ```bash
   cd SiAdin_Login_Firefox
   ```

3. **Install Python dependencies**
   ```bash
   python install_selenium.py
   ```

4. Ensure you have:
   - Python 3.x installed
   - Firefox or Chrome browser installed
   - WebDriver executables in the same directory (`geckodriver.exe` / `chromedriver.exe`)

  

---

## ⚙️ Configuration

Edit the `config.json` file and replace placeholders with your credentials:

```json
{
  "siadin": {
    "nim": "YOUR_NIM_SIADIN",
    "password": "YOUR_PASSWORD"
  },
  "kulino": {
    "nim": "YOUR_NIM_KULINO",
    "password": "YOUR_PASSWORD"
  }
}
```

Keep this file safe — it contains your personal credentials.

---

## 🚀 Usage

Run the appropriate script depending on the browser you want to use:

### Default:
just double-click `run.bat`(Windows only and script is run in firefox by default you can modify the run.bat depending on the browser you want to use ).
```bash
run.bat
```

### For Firefox:
```bash
python login_firefox.py
```

### For Chrome:
```bash
python login_chrome.py
```


---

## 🧪 Examples

```bash
# Run Firefox automation
> python login_firefox.py
```

```bash
# Run Chrome automation
> python login_chrome.py
```

---

## 🛠️ Troubleshooting

- **Selenium not installed?**
  - Run: `python install_selenium.py`
- **WebDriver errors?**
  - Ensure `geckodriver.exe` or `chromedriver.exe` matches your browser version.
- **Timeouts or site not loading?**
  - Check your internet connection.
  - The site may be undergoing maintenance.

---

## 📦 Dependencies

- Python 3.x
- [Selenium](https://pypi.org/project/selenium/)
- Web browsers:
  - Firefox (for `geckodriver.exe`)
  - Chrome (for `chromedriver.exe`)

---

## 👨‍💻 Contributors

- 👤 Original Author: *[Your Name Here]*  
- 🛠️ Contributions welcome! Feel free to submit a PR or open an issue.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---
