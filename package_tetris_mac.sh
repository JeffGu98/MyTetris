#!/usr/bin/env zsh
set -euo pipefail

# 打包 pygame 俄罗斯方块为 macOS 应用 (.app)
# 产物路径: ./dist/Tetris.app
# 运行方式: 双击 Tetris.app；如被系统阻止，右键->打开（或在“系统设置 > 隐私与安全性”里允许）

cd "$(dirname "$0")"

VENV_DIR=".tetris-build-venv"
APP_NAME="Tetris"
BUNDLE_ID="local.tetris"
ENTRY="tetris.py"

# 创建独立虚拟环境
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

# 安装依赖
python -m pip install --upgrade pip
pip install pygame pyinstaller

# 清理旧产物
rm -rf build dist "$APP_NAME.spec" || true

# 打包
pyinstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  --osx-bundle-identifier "$BUNDLE_ID" \
  "$ENTRY"

# 结果提示
echo "\n✅ 打包完成: $(pwd)/dist/$APP_NAME.app"
echo "   提示: 首次运行如被阻止，可右键->打开，或在‘隐私与安全性’中允许。"
