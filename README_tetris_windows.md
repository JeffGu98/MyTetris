# Tetris 打包与分发（Windows）

本目录已包含 `tetris.py`（pygame 俄罗斯方块）。你可以在 Windows 上一键打包为可执行程序，发给没有 Python 环境的朋友。

## 一键打包（.bat，适合双击）
1) 在 Windows 资源管理器中进入本目录，双击运行：
   - `package_tetris_windows.bat`

或在命令行执行：
```bat
cd /d %USERPROFILE%\path\to\俄罗斯方块
package_tetris_windows.bat
```

## PowerShell 方式
```powershell
cd $HOME\path\to\俄罗斯方块
./package_tetris_windows.ps1
```
若遇到执行策略限制，可临时放开：
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
./package_tetris_windows.ps1
```

## 产物位置
- 生成路径：`dist/Tetris/Tetris.exe`
- 分享建议：将 `dist/Tetris` 整个文件夹压缩为 zip 后分享（需保留 SDL、DLL 等依赖文件）。

## 运行被拦截的处理
- 如果 Windows Defender SmartScreen 提示阻止：点击“更多信息”->“仍要运行”。

## 说明与注意
- 本打包需在 Windows 上执行；PyInstaller 不支持在 macOS 上交叉编译 Windows EXE。
- 游戏最高分保存位置跨平台统一为：`%USERPROFILE%\.tetris_highscore.json`。
- 如需自定义图标，准备 `icon.ico`，并在打包命令加上：`--icon icon.ico`。
