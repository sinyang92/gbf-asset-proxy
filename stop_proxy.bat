@echo off
chcp 65001 >nul
setlocal

:: ===== 可按需修改的配置 =====
set PROXY_PORT=8888
:: ============================

echo 正在查找并关闭代理进程...

taskkill /IM mitmdump.exe /F >nul 2>&1
taskkill /IM mitmproxy.exe /F >nul 2>&1
taskkill /IM mitmweb.exe /F >nul 2>&1

powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %PROXY_PORT% -State Listen -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }"

powershell -NoProfile -Command "if (Get-NetTCPConnection -LocalPort %PROXY_PORT% -State Listen -ErrorAction SilentlyContinue) { Write-Host '警告: 端口 %PROXY_PORT% 仍被占用,可能需要手动检查任务管理器。' } else { Write-Host '完成: 端口 %PROXY_PORT% 已释放,代理已全部关闭。' }"

echo.
pause
endlocal