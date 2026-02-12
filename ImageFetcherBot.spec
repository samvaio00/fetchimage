# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('config', 'config')],
    hiddenimports=['src.api.replit_client', 'src.services.local_image_service', 'src.services.sku_processor', 'src.storage.state_manager', 'src.utils.config', 'src.utils.logger', 'PIL._tkinter_finder'],
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
    name='ImageFetcherBot',
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
