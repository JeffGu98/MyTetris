# Tetris 打包与分发（macOS）

本目录包含 `tetris.py`（pygame 俄罗斯方块）。本指南帮助你在 macOS 上打包为独立可运行的 `.app`，方便分发给没有 Python 环境的用户。

## 一键打包（推荐）

1) 打开终端，进入本目录：
```bash
cd "/Users/shukun/Documents/脚本"
```

2) 赋予脚本执行权限并运行：
```bash
chmod +x package_tetris_mac.sh
./package_tetris_mac.sh
```

运行完成后生成：
- `dist/Tetris.app`：双击即可运行。

首次运行如果出现“无法验证开发者”，请：
- 右键 `Tetris.app` -> 打开；或
- 系统设置 -> 隐私与安全性 -> 允许来自未识别开发者的应用。

## 注意事项
- 最高分会保存在 `~/.tetris_highscore.json`（用户主目录），打包/未打包都通用。
- 该 `.app` 目标架构与本机一致（Intel 或 ARM）。如需通用二进制（universal2），需要在两台不同架构机器上分别构建并合并，或使用更复杂的构建流程（本脚本未覆盖）。
- 如果要分发为压缩包，建议：
```bash
cd dist && zip -r Tetris.zip Tetris.app
```
将 `Tetris.zip` 发给对方即可。

## 常见问题
- 运行时黑屏/无窗口：请安装显卡驱动更新（少见）或确保 `pygame` 正常工作。
- 打包失败：先尝试清理并重试：
```bash
rm -rf build dist Tetris.spec .tetris-build-venv
./package_tetris_mac.sh
```
- 需要应用图标：准备一张 `icon.icns`，打包命令添加 `--icon icon.icns` 参数。
