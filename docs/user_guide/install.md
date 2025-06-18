# Installation

Presently, there are two ways of running the app: using the binary or from the source. In the future, installers will also be provided. 

To run the app using the binary, the OS-appropriate binary can be downloaded [here](https://github.com/rodinalex/TiBi/releases), if available. In this case, no further installations are necessary and the app can be launched by double clicking on the executable. If the binary is not available, it is possible to build it locally using [PyInstaller](https://www.pyinstaller.org/) and the source obtained from the same [link](https://github.com/rodinalex/TiBi/releases) or run the source code directly.

## Running from the Source

### 1. Download the Source

Get a compressed source folder [here](https://github.com/rodinalex/TiBi/releases).

### 2. Set Up Python Environment

**Option A: Using Conda (Recommended)**

```bash
conda env create -f environment.yml
conda activate TiBi-env
```

**Option B: Using venv**

If Option A does not work (the app does not start or crashes), Option B may resolve the issue. For macOS or Linux, run

```bash
python -m venv venv

# Activate the environment:
source venv/bin/activate

pip install -r requirements.txt
```

For Windows, run


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

## Running the Built Application

### macOS
```bash
./dist/TiBi.app/Contents/macOS/TiBi
```
Or navigate to `dist/` and double-click the TiBi.app icon

### Windows
```cmd
dist\TiBi.exe
```
Or double-click `dist\TiBi.exe`

### Linux
```bash
./dist/TiBi/TiBi
```
