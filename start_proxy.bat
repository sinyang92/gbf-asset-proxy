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
set UPSTREAM_PROXY=
:: ============================

powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %PROXY_PORT% -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"

set MODE_ARG=
if not "%UPSTREAM_PROXY%"=="" set MODE_ARG=--mode upstream:%UPSTREAM_PROXY%

mitmdump -s "%MAIN_SCRIPT%" -p %PROXY_PORT% %MODE_ARG%

endlocal