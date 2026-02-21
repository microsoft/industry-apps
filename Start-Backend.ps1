# Start Backend (FastAPI)
# Run this in one terminal

Write-Host "Starting Backend Server..." -ForegroundColor Cyan
Write-Host ""

$backendPath = "$PSScriptRoot\ui-tools\backend"

# Navigate to backend
Set-Location $backendPath

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $backendPath ".venv\Scripts\Activate.ps1"

if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "[ERROR] Virtual environment not found. Run Start-UITools.ps1 first for initial setup." -ForegroundColor Red
    exit 1
}

# Start backend with hot reload
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Backend running on: http://localhost:8000" -ForegroundColor Green
Write-Host "  Hot Reload: ENABLED" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
