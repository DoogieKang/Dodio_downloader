@echo off
setlocal enabledelayedexpansion

echo.
echo ============================================
echo   Seminar Downloader - Build Script
echo ============================================
echo.

:: ── Step 1: Check Python ─────────────────────
echo [1/5] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Install from https://www.python.org/downloads/
    echo         Make sure to check "Add Python to PATH" during installation.
    pause & exit /b 1
)
for /f "tokens=*" %%v in ('python --version 2^>^&1') do echo [OK] %%v found

:: ── Step 2: Install packages ─────────────────
echo.
echo [2/5] Installing packages...
if not exist ".venv_build\" (
    python -m venv .venv_build
)
call .venv_build\Scripts\activate.bat

python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt pyinstaller --quiet
if errorlevel 1 (
    echo [ERROR] Package installation failed.
    pause & exit /b 1
)
echo [OK] Packages installed

:: ── Step 3: Check ffmpeg ─────────────────────
echo.
echo [3/5] Checking ffmpeg...
if exist "build_temp\ffmpeg.exe" (
    echo [OK] ffmpeg found in build_temp\
) else (
    echo [ERROR] build_temp\ffmpeg.exe not found.
    echo         Please put ffmpeg.exe in the build_temp\ folder and run again.
    pause & exit /b 1
)

:: ── Step 4: PyInstaller build ────────────────
echo.
echo [4/5] Building app with PyInstaller...
pyinstaller seminar_downloader.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] PyInstaller build failed.
    pause & exit /b 1
)
echo [OK] Build complete: dist\SeminarDownloader\

:: ── Step 5: Create installer with Inno Setup ─
echo.
echo [5/5] Creating installer...
set "ISCC="
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist "C:\Program Files\Inno Setup 6\ISCC.exe" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"

if defined ISCC (
    if not exist "installer_output\" mkdir installer_output
    "%ISCC%" installer.iss
    if errorlevel 1 (
        echo [ERROR] Inno Setup build failed.
    ) else (
        echo [OK] Installer created: installer_output\SeminarDownloader_Setup.exe
    )
) else (
    echo [WARNING] Inno Setup 6 not found. Install from https://jrsoftware.org/isdl.php
    echo           Or distribute the dist\SeminarDownloader\ folder as a zip.
)

call deactivate

echo.
echo ============================================
echo   Done!
echo   Executable : dist\SeminarDownloader\SeminarDownloader.exe
if defined ISCC echo   Installer  : installer_output\SeminarDownloader_Setup.exe
echo ============================================
echo.
pause
