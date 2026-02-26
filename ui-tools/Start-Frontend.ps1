# Start Frontend (Vite)
# Run this in a separate terminal from the backend

Write-Host "Starting Frontend Server..." -ForegroundColor Cyan
Write-Host ""

$frontendPath = "$PSScriptRoot\frontend"

# Navigate to frontend
Set-Location $frontendPath

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "[WARNING] node_modules not found. Run Start-UITools.ps1 first for initial setup." -ForegroundColor Yellow
    exit 1
}

# Start frontend
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Frontend starting..." -ForegroundColor Green
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Start Vite directly with node to bypass execution policy issues
node node_modules\vite\bin\vite.js
