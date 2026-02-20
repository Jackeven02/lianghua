# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['quant_analyzer_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[('strategy_layer', 'strategy_layer'), ('ui_layer', 'ui_layer')],
    hiddenimports=['PyQt5', 'pandas', 'numpy', 'efinance'],
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
    name='QuantAnalyzer',
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
    name='QuantAnalyzer',
)
