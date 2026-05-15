@echo off
setlocal enabledelayedexpansion

:: 获取脚本所在目录
set "script_dir=%~dp0"
cd /d "%script_dir%"

:: 定义临时 whl 路径
set "WHL_DIR=%script_dir%dist"

echo 清理旧的构建目录...
if exist "%WHL_DIR%" rmdir /s /q "%WHL_DIR%"
if exist build rmdir /s /q build
if exist lntools.egg-info rmdir /s /q lntools.egg-info

echo 使用 uv 构建 wheel...
uv build --wheel --out-dir "%WHL_DIR%"

:: 获取最新的 whl 文件
set "WHL_FILE="
for /f "delims=" %%i in ('dir /b /od "%WHL_DIR%\lntools-*.whl" 2^>nul') do (
    set "WHL_FILE=%WHL_DIR%\%%i"
)

if "%WHL_FILE%"=="" (
    echo 错误: 未找到构建的 wheel 文件。
    exit /b 1
)

echo 使用 uv pip 安装 %WHL_FILE% ...
uv pip install "%WHL_FILE%" --force-reinstall

echo 清理临时构建文件...
if exist build rmdir /s /q build
if exist lntools.egg-info rmdir /s /q lntools.egg-info

echo 安装完成。
