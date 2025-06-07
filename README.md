# TiBi

Welcome! This README guides you through setting up, building, and running **TiBi** on your machine.

---

## Supported Platforms

- macOS
- Windows (in progress)
- Linux

---

## Prerequisites

- **Python 3.12**
- [PyInstaller](https://www.pyinstaller.org/)
- Git (to clone the repo)

---

## Setup Instructions

### 1. Clone the Repository

### 2. Create a Python Environment
We recommend using Conda to create a clean environment with the necessary dependencies:

```bash
conda env create -f environment.yml
conda activate TiBi-env
```

If you don't have Conda, you can use venv and pip:

```
python -m venv venv
source venv/bin/activate         # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Build the Application
Use the PyInstaller spec file tailored for your platform:

macOS (Apple Silicon / Intel):
```
pyinstaller app_mac.spec
```

Windows:
```
pyinstaller app_win.spec
```

Linux:
```
pyinstaller app_linux.spec
```

This will create a bundled app inside the dist/ directory.

### 4. Run the Application
On macOS:
```
./dist/TiBi.app/Contents/MacOS/TiBi
```
Or navigate to /dist and double click on the app icon.

On Windows:
Double-click dist\TiBi.exe or run:
```
dist\TiBi.exe
```
On Linux:
```
./dist/TiBi/TiBi
```

### Notes

If you encounter issues with missing packages, double-check your environment and try reinstalling dependencies.
The .spec files are platform-specific to ensure correct bundling.
If you need help, please open an issue in this repo.

### Updating Dependencies

If dependencies are updated:

For Conda environments:
```
conda env update -f environment.yml
```
For pip environments:
```
pip install -r requirements.txt --upgrade
```
Thank you for testing **TiBi**! Your feedback is appreciated.
