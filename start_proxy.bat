@echo off
if "%~1"=="hidden" goto :run

powershell -WindowStyle Hidden -Command "Start-Process -FilePath '%~f0' -ArgumentList 'hidden' -WindowStyle Hidden"
exit /b

:run
chcp 65001 >nul
setlocal

:: ===== 可按需修改的配置 =====
set PROXY_PORT=8888
set SCRIPT_DIR=%~dp0
set MAIN_SCRIPT=%SCRIPT_DIR%main.py
:: ============================

powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %PROXY_PORT% -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"

mitmdump -s "%MAIN_SCRIPT%" -p %PROXY_PORT%

endlocal