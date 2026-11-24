$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$backendDir = Join-Path $root 'backend'
$frontendDir = Join-Path $root 'frontend'

Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$backendDir'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$frontendDir'; npm install; npm run dev -- --host 0.0.0.0"

Write-Host 'Backend y frontend iniciados.'
Write-Host 'Abre http://localhost:5173 para usar la aplicación.'
