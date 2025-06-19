# Installation

There are currently two ways to run the app: using a prebuilt binary or directly from source. In the future, standalone installers will also be provided.

---

## Option 1: Run the Binary

Prebuilt binaries (if available) can be downloaded from the [Releases page](https://github.com/rodinalex/TiBi/releases). No installation is necessary—just download and double-click the executable for your operating system.

If no binary is available for your platform, you can either build one yourself using [PyInstaller](https://www.pyinstaller.org/) or run the app directly from source (see below).

---

## Option 2: Run from Source

### 1. Download the Source

Download and extract the source archive from the [Releases page](https://github.com/rodinalex/TiBi/releases), or clone the repository directly:

```bash
git clone https://github.com/rodinalex/TiBi.git
cd TiBi
```

### 2. Set up the Python Environment

**Option A: Using Conda (Recommended)**

```bash
conda env create -f environment.yml
conda activate TiBi-env
```

**Option B: Using venv (if Conda causes issues)**

macOS/Linux:

```bash
python -m venv venv

# Activate the environment:
source venv/bin/activate

pip install -r requirements.txt
```

Windows:

```cmd
python -m venv venv

# Activate the environment:
venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Launch the App

**macOS/Linux:**
```bash
python3 -m TiBi.app
```

**Windows:**
```cmd
python -m TiBi.app
```
If the app does not launch, ensure that your virtual environment is activated and all dependencies are installed correctly.

---

## Building a Standalone Binary

To build the app as a self-contained binary, use the appropriate PyInstaller `.spec` file:

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

This will generate a bundled application in the `dist/` directory.

---

## Running the Built Application

**macOS**
```bash
./dist/TiBi.app/Contents/macOS/TiBi
```
Or double-click `TiBi.app` in the `dist/` folder.

**Windows**
```cmd
dist\TiBi.exe
```
Or double-click the executable in your file browser.

**Linux**
```bash
./dist/TiBi/TiBi
```
Or launch from your file browser or terminal.

---

## Notes

* Python 3.12+ is supported, but older systems may require Python 3.10 or 3.11.
* If you encounter issues with fonts, OpenGL, or window display, please open an issue on GitHub.