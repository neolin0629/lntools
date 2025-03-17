@echo off
call activate base

set WHEEL_DIR=E:/project/wheels
set PACKAGE_NAME=lntools

:: 清理旧包文件（可选）
del /q "%WHEEL_DIR%\%PACKAGE_NAME%-*.whl" 2>nul

:: 构建新wheel
pip wheel --no-deps --wheel-dir="%WHEEL_DIR%" ./

:: 智能卸载（仅在已安装时执行）
pip show %PACKAGE_NAME% >nul 2>&1 && pip uninstall %PACKAGE_NAME% -y

:: 自动匹配最新版本安装
for /f "delims=" %%i in ('dir /b /od "%WHEEL_DIR%\%PACKAGE_NAME%-*.whl"') do set LATEST_WHL=%%i
pip install "%WHEEL_DIR%\%LATEST_WHL%"

echo Cleaning up build directories...
if exist build rmdir /s /q build
if exist lntools.egg-info rmdir /s /q lntools.egg-info
if exist dist rmdir /s /q dist

echo Build directories cleaned.