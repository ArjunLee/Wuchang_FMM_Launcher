# -*- mode: python ; coding: utf-8 -*-

import os
block_cipher = None

# 版本信息配置
version_info = {
    'version': (1, 0, 0, 0),
    'company_name': 'Arjun520',
    'file_description': '明末：渊虚之羽-FMM_MOD启动器',
    'internal_name': '明末：渊虚之羽-FMM_MOD启动器',
    'legal_copyright': 'Copyright © 2025 Arjun520. All rights reserved.',
    'original_filename': 'Wuchang FMM Launcher.exe',
    'product_name': '明末：渊虚之羽-FMM_MOD启动器',
    'product_version': (1, 0, 0, 0)
}

a = Analysis(
    ['Wuchang_FMM_Launcher.py', 'common_operations.py'],
    pathex=[],
    binaries=[],
    datas=[('src/GameInfo.bin', 'src')],
    hiddenimports=[
        'watchdog',
        'watchdog.observers',
        'watchdog.events',
        'watchdog.observers.polling',
        'watchdog.observers.winapi',
        'watchdog.utils',
        'watchdog.utils.dirsnapshot',
        'colorama',
        'json',
        'os',
        'shutil',
        'pathlib',
        'subprocess',
        'threading',
        'time',
        'datetime',
        'hashlib',
        'configparser',
        'sys',
        'platform'
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
    name='Wuchang FMM Launcher',
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
    icon='src/exec.png',
    version='Wuchang_FMM_Launcher-version_info.txt'
)