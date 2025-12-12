
# target: dist/Tetris/Tetris.exe
# double click Tetris.exe

$ErrorActionPreference = 'Stop'
Set-Location -Path $PSScriptRoot

$venv = '.tetris-build-venv'
$app = 'Tetris'
$entry = 'tetris.py'

$py = 'py -3'
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { $py = 'python' }

& $py -m venv $venv

. "$venv/Scripts/Activate.ps1"

# 使用 python -m 方式避免在非 ASCII 路径下的 pip/pyinstaller 启动器问题
python -m pip install --upgrade pip
python -m pip install pygame pyinstaller

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
Remove-Item -Force "$app.spec" -ErrorAction SilentlyContinue

python -m PyInstaller --noconfirm --clean --windowed --name $app $entry

Write-Host "`n finish: $(Resolve-Path "dist/$app/$app.exe")"
