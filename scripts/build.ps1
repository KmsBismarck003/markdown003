$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $root 'backend'
$frontendDir = Join-Path $root 'frontend'

Set-Location $frontendDir
npm install
npm run build

Set-Location $backendDir
python -m pip install -r requirements.txt
pytest -q

Write-Host 'Validación finalizada.'
