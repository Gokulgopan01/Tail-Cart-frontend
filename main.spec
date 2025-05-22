# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
<<<<<<< HEAD
    datas=[('assets\\\\*', 'assets'), ('screens/json/portal_map.json', 'json'), ('.env', '.')],
=======
    datas=[('assets\\\\*', 'assets'), ('json/portal_map.json', 'json'), ('.env', '.')],
>>>>>>> 65823027fe6d5a072993a4e95e569e4735465a0f
    hiddenimports=[],
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
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
