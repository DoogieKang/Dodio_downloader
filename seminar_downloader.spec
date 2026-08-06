# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all
ttkbs_datas, ttkbs_binaries, ttkbs_hiddenimports = collect_all('ttkbootstrap')
selenium_datas, selenium_binaries, selenium_hiddenimports = collect_all('selenium')
openpyxl_datas, openpyxl_binaries, openpyxl_hiddenimports = collect_all('openpyxl')

a = Analysis(
    ['seminar_downloader.py'],
    pathex=[],
    binaries=ttkbs_binaries + selenium_binaries + openpyxl_binaries,
    datas=[('default_config.json', '.')] + ttkbs_datas + selenium_datas + openpyxl_datas,
    hiddenimports=ttkbs_hiddenimports + selenium_hiddenimports + openpyxl_hiddenimports + [
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome',
        'selenium.webdriver.chrome.webdriver',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.chrome.options',
        'selenium.webdriver.remote.webdriver',
        'selenium.webdriver.remote.remote_connection',
        'selenium.webdriver.remote.errorhandler',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.utils',
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
        'paramiko',
        'paramiko.transport',
        'paramiko.sftp_client',
        'cryptography',
        'bcrypt',
        'pynacl',
        'openpyxl',
        'openpyxl.styles',
        'openpyxl.styles.stylesheet',
        'openpyxl.reader',
        'openpyxl.reader.excel',
        'openpyxl.workbook',
        'openpyxl.worksheet',
        'et_xmlfile',
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
    console=False,          # GUI 앱이므로 콘솔 창 없음
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # 아이콘 파일 경로로 교체 가능: icon='app.ico'
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
