[![Docs](https://img.shields.io/badge/docs-online-blue)](https://rodinalex.github.io/TiBi/)


# TiBi

Welcome! This README guides you through setting up, building, and running **TiBi** on your machine.

---

## What is TiBi?

TiBi is an app that performs **Ti**ght **Bi**nding calculations. It allows the User to construct the system using graphical means with no coding.

---

## Supported Platforms

- ✅ macOS (Apple Silicon & Intel): binary available
- 🚧 Windows (in progress)
- ✅ Linux

---

## Prerequisites

- **Python 3.12** or higher
- [PyInstaller](https://www.pyinstaller.org/)
- Git (to clone the repo)

---

## Quick Start

### 1. Get the Source code

**Option A: Clone the Repository**

```bash
git clone git@github.com:rodinalex/TiBi.git
cd TiBi
```

**Option B: Download a release**

Get a compressed source folder [here](https://github.com/rodinalex/TiBi/releases)

**Option C: Download a binary**

Get the OS-appropriate binary [here](https://github.com/rodinalex/TiBi/releases)

### 2. Set Up Python Environment

**Option A: Using Conda (Recommended)**
```bash
conda env create -f environment.yml
conda activate TiBi-env
```

**Option B: Using venv**

If Option A does not work (the app does not start or crashes), Option B may resolve the issue.

```bash
python -m venv venv

# Activate the environment:
source venv/bin/activate         # macOS/Linux
# OR
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3. Run from Source

**macOS/Linux:**
```bash
python3 -m TiBi.app
```

**Windows:**
```cmd
python -m TiBi.app
```

---

## Building the Application

Use the PyInstaller spec file for your platform:

**macOS:**
```bash
pyinstaller app_mac.spec
```

**Windows:**
```cmd
pyinstaller app_win.spec
```

**Linux:**
```bash
pyinstaller app_linux.spec
```

This creates a bundled application in the `dist/` directory.

---

## Running the Built Application

### macOS
```bash
./dist/TiBi.app/Contents/MacOS/TiBi
```
*Or navigate to `dist/` and double-click the TiBi.app icon*

### Windows
```cmd
dist\TiBi.exe
```
*Or double-click `dist\TiBi.exe`*

### Linux
```bash
./dist/TiBi/TiBi
```

---

## Troubleshooting

### Common Issues

**"Module not found" errors:**
- Ensure your virtual environment is activated
- Try reinstalling dependencies: `pip install -r requirements.txt --upgrade`

**PyInstaller build fails:**
- Check that you're using the correct spec file for your platform
- Ensure all dependencies are installed in your environment

**App won't start after building:**
- Try running from terminal to see error messages (see commands above)
- Check that all required files are included in your spec file

---

## Development

### Updating Dependencies

**For Conda environments:**
```bash
conda env update -f environment.yml
```

**For pip environments:**
```bash
pip install -r requirements.txt --upgrade
```

### Project Structure
```
TiBi/
├── TiBi/                 # Main package
│   ├── app.py            # Entry point
│   ├── assets/           # Styling resources
│   ├── controllers/      # Application controllers
│   ├── core/             # Physics functions
│   ├── logic/            # App commands and data serialization
│   ├── models/           # Data models
│   ├── ui/               # UI resources (styles, etc.)
│   └── views/            # UI views
├── app_mac.spec          # macOS build config
├── app_win.spec          # Windows build config
├── app_linux.spec        # Linux build config
├── environment.yml       # Conda dependencies
├── requirements.txt      # pip dependencies
└── README.md
```

---

## Support

If you encounter issues:
1. Check the [Troubleshooting](#troubleshooting) section above
2. Search existing [issues](https://github.com/rodinalex/TiBi/issues)
3. Open a new issue with:
   - Your operating system
   - Python version (`python --version`)
   - Error message (if any)
   - Steps to reproduce

---

Thank you for trying **TiBi**! Your feedback helps make it better.
