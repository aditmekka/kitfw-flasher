# KitFW_Flasher.spec
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('tools/esptool.exe', 'tools'),
        ('tools/avrdude', 'tools/avrdude'),
        ('assets/logo.ico', 'assets'),
    ],
    hiddenimports=[],  # Let PyInstaller auto-detect
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='KitFW_Flasher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,
    upx=True,
    upx_exclude=['vcruntime140.dll'],
    console=False,
    disable_windowed_traceback=False,
    icon='assets/logo.ico'
)