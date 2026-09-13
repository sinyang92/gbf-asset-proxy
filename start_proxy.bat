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

mitmdump -s "%MAIN_SCRIPT%" -p %PROXY_PORT% > "%SCRIPT_DIR%proxy_console.log" 2>&1

endlocal