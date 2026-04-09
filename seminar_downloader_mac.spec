# -*- mode: python ; coding: utf-8 -*-
# macOS 전용 PyInstaller 스펙 파일

a = Analysis(
    ['seminar_downloader.py'],
    pathex=[],
    binaries=[('build_temp/ffmpeg', '.')],  # ffmpeg을 .app 내부에 번들
    datas=[],
    hiddenimports=[
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.common.by',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support.expected_conditions',
        'webdriver_manager',
        'webdriver_manager.chrome',
        'webdriver_manager.core.driver_cache',
        'requests',
        'certifi',
        'urllib3',
        'charset_normalizer',
        'idna',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='DodioDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='DodioDownloader',
)

app = BUNDLE(
    coll,
    name='DodioDownloader.app',
    icon=None,
    bundle_identifier='com.doogiekang.dodiodownloader',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSAppleScriptEnabled': False,
        'CFBundleDisplayName': 'DodioDownloader',
        'CFBundleShortVersionString': '1.0',
        'NSHighResolutionCapable': True,
    },
)
