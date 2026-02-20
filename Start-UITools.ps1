# UI Tools Launcher
# Starts both the FastAPI backend and Svelte frontend

Write-Host "Starting UI Tools..." -ForegroundColor Cyan
Write-Host ""

$uiPath = "$PSScriptRoot\ui-tools"
$backendPath = "$uiPath\backend"
$frontendPath = "$uiPath\frontend"

# Find Python executable
$pythonCmd = $null
foreach ($cmd in @("py", "python", "python3")) {
    try {
        $version = & $cmd --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = $cmd
            Write-Host "[OK] Python: $version" -ForegroundColor Green
            break
        }
    }
    catch {}
}

if (-not $pythonCmd) {
    Write-Host "[ERROR] Python not found. Please install Python 3.8+" -ForegroundColor Red
    Write-Host "  Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node/npm
try {
    $nodeVersion = node --version
    Write-Host "[OK] Node: $nodeVersion" -ForegroundColor Green
}
catch {
    Write-Host "[ERROR] Node.js not found. Please install Node.js" -ForegroundColor Red
    Write-Host "  Download from: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Setup backend
Write-Host ""
Write-Host "Setting up backend..." -ForegroundColor Cyan
Set-Location $backendPath

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    & $pythonCmd -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

Write-Host "Activating virtual environment..." -ForegroundColor Yellow
$activateScript = Join-Path $backendPath ".venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "[ERROR] Virtual environment activation script not found" -ForegroundColor Red
    exit 1
}

Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install -q --upgrade pip
python -m pip install -q -r requirements.txt

# Setup frontend
Write-Host ""
Write-Host "Setting up frontend..." -ForegroundColor Cyan
Set-Location $frontendPath

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing npm dependencies..." -ForegroundColor Yellow
    npm install
}

# Start backend in background
Write-Host ""
Write-Host "Starting backend server..." -ForegroundColor Cyan
Set-Location $backendPath
$backendJob = Start-Job -ScriptBlock {
    param($path, $pythonCmd)
    Set-Location $path
    $activateScript = Join-Path $path ".venv\Scripts\Activate.ps1"
    & $activateScript
    python main.py
} -ArgumentList $backendPath, $pythonCmd

Start-Sleep -Seconds 2

# Start frontend
Write-Host "Starting frontend server..." -ForegroundColor Cyan
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop both servers" -ForegroundColor Yellow
Write-Host ""

Set-Location $frontendPath

# Open browser after delay
Start-Sleep -Seconds 3
Start-Process "http://localhost:5173"

# Run frontend (blocking)
npm run dev

# Cleanup when frontend stops
Write-Host ""
Write-Host "Stopping backend..." -ForegroundColor Yellow
Stop-Job $backendJob
Remove-Job $backendJob

Write-Host "Shutdown complete." -ForegroundColor Green
