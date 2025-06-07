# -*- mode: python ; coding: utf-8 -*-
import os
import pathlib
app_dir = pathlib.Path.cwd() / "TiBi"

datas = [
    (os.path.join(app_dir, "assets"), "TiBi/assets"),
    (os.path.join(app_dir, "ui", "styles"), "TiBi/ui/styles"),
]

a = Analysis(
    ["TiBi/app.py"],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "copy",
        "dataclasses",
        "itertools",
        "json",
        "functools",
        "matplotlib",
        "matplotlib.backends.backend_qt5agg",
        "matplotlib.figure",
        "numpy",
        "numpy.typing",
        "OpenGL.platform.glx",
        "OpenGL.platform.egl",
        "OpenGL.arrays.vbo",
        "OpenGL.raw.GL.VERSION.GL_1_1",
        "OpenGL.GL",
        "OpenGL.GLU",
        "os",
        "pyqtgraph",
        "pyqtgraph.opengl",
        "sympy",
        "typing",
        "uuid",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="TiBi",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="TiBi",
)
app = BUNDLE(
    coll,
    name="TiBi.app",
    icon=None,
    bundle_identifier=None,
)
