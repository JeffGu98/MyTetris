@echo off
setlocal enableextensions enabledelayedexpansion

REM 打包 pygame 俄罗斯方块为 Windows 可执行程序
REM 产物路径: dist\Tetris\Tetris.exe
REM 运行方式: 双击 Tetris.exe

cd /d "%~dp0"
set VENV_DIR=.tetris-build-venv
set APP_NAME=Tetris
set ENTRY=tetris.py

REM 选择 Python 启动器（优先 py，再退化到 python）
where py >nul 2>nul
if %errorlevel%==0 (
  set PY=py -3
) else (
  set PY=python
)

REM 创建虚拟环境
%PY% -m venv "%VENV_DIR%"
call "%VENV_DIR%\Scripts\activate.bat"

REM 安装依赖
python -m pip install --upgrade pip
pip install pygame pyinstaller

REM 清理旧产物
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist %APP_NAME%.spec del /f /q %APP_NAME%.spec

REM 打包
pyinstaller --noconfirm --clean --windowed --name "%APP_NAME%" "%ENTRY%"

echo.
echo ✅ 打包完成: %cd%\dist\%APP_NAME%\%APP_NAME%.exe
echo    建议将 dist\%APP_NAME% 整个文件夹打包为 zip 后分发。
pause
