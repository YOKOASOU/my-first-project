@echo off
setlocal

REM 1) Build exe with PyInstaller
cd /d %~dp0\..
python -m PyInstaller --noconfirm installer\truck_paint_lead_researcher.spec
if errorlevel 1 (
  echo [ERROR] PyInstaller build failed.
  exit /b 1
)

REM 2) Build installer with Inno Setup (ISCC.exe)
set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC_PATH% (
  echo [ERROR] Inno Setup compiler not found: %ISCC_PATH%
  echo Install Inno Setup 6 and retry.
  exit /b 1
)

%ISCC_PATH% installer\installer.iss
if errorlevel 1 (
  echo [ERROR] Inno Setup build failed.
  exit /b 1
)

echo [OK] Installer created in dist_installer.
exit /b 0
