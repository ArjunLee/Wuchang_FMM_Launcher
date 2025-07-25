@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 自动检查Python环境、安装依赖并运行程序

echo.
echo ╔══════════════════════════════════════════════════════════════════════════════════╗
echo ║                    🎮 Wuchang FMM Launcher 安装和运行工具 🎮                       ║
echo ╚══════════════════════════════════════════════════════════════════════════════════╝
echo.

REM 检查Python是否安装
echo 🔍 检查Python环境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 未检测到Python环境
    echo 📥 请先安装Python 3.7或更高版本: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM 显示Python版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%

REM 检查pip是否可用
echo 🔍 检查pip工具...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip工具不可用
    echo 📥 请确保pip已正确安装
    pause
    exit /b 1
)
echo ✅ pip工具可用

REM 检查requirements.txt是否存在
if not exist "requirements.txt" (
    echo ❌ 未找到requirements.txt文件
    echo 📁 请确保文件在当前目录下
    pause
    exit /b 1
)

REM 安装依赖包
echo.
echo 📦 安装依赖包...
echo ────────────────────────────────────────────────────────────────────────────────
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ 依赖包安装失败
    echo 🔧 请检查网络连接或手动安装: pip install watchdog colorama
    pause
    exit /b 1
)
echo ✅ 依赖包安装完成

REM 检查主程序文件
if not exist "Wuchang_FMM_Launcher.py" (
    echo ❌ 未找到Wuchang_FMM_Launcher.py文件
    echo 📁 请确保主程序文件在当前目录下
    pause
    exit /b 1
)

REM 运行程序
echo.
echo 🚀 启动Wuchang FMM Launcher...
echo ────────────────────────────────────────────────────────────────────────────────
echo.
python Wuchang_FMM_Launcher.py

REM 程序结束后的处理
echo.
echo ────────────────────────────────────────────────────────────────────────────────
echo 📋 程序已退出
echo 💡 如需重新运行，请再次执行此批处理文件
echo.
pause