@echo off
chcp 65001 >nul 2>&1 || chcp 936 >nul 2>&1
echo 请输入数字选择操作:
echo 1 - 禁用网络连接
echo 2 - 启用网络连接
set /p choice=请选择(1或2):

if "%choice%"=="1" goto disable
if "%choice%"=="2" goto enable

:disable
echo 正在禁用网络连接...
wmic path win32_networkadapter where NetConnectionID="以太网" call disable
goto end

:enable
echo 正在启用网络连接...
wmic path win32_networkadapter where NetConnectionID="以太网" call enable
goto end

:end
echo 操作完成。
pause