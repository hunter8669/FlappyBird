# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['../game-desktop/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('../game-desktop/src', 'src'),
        ('../assets', 'assets'),
        ('../data', 'data'),
    ],
    hiddenimports=[
        'pygame',
        'pygame.locals',
        'pygame.mixer',
        'pygame.font',
        'pygame.image',
        'pygame.transform',
        'pygame.sprite',
        'pygame.rect',
        'pygame.surface',
        'pygame.display',
        'pygame.event',
        'pygame.key',
        'pygame.time',
        'pygame.math',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FlapPyBird',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 无控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='../flappy.ico',  # 使用项目图标
)
