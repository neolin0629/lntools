@echo off
call conda activate dev

set WHEEL_DIR=E:/project/wheels
set PACKAGE_NAME=lntools

del /q "%WHEEL_DIR%\%PACKAGE_NAME%-*.whl" 2>nul

pip wheel --no-deps --wheel-dir="%WHEEL_DIR%" ./

pip show %PACKAGE_NAME% >nul 2>&1 && pip uninstall %PACKAGE_NAME% -y

for /f "delims=" %%i in ('dir /b /od "%WHEEL_DIR%\%PACKAGE_NAME%-*.whl"') do set LATEST_WHL=%%i
pip install -e "%WHEEL_DIR%\%LATEST_WHL%"

echo Cleaning up build directories...
if exist build rmdir /s /q build
if exist lntools.egg-info rmdir /s /q lntools.egg-info
if exist dist rmdir /s /q dist

echo Build directories cleaned.