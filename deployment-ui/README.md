# Deployment UI

FastAPI + Svelte web application for deploying Dataverse modules.

## Quick Start

### Option 1: VS Code Tasks (Recommended)
Press `Ctrl+Shift+P` and run:
- **"Tasks: Run Task"** → **"Start Deployment UI (Both)"**

This starts both servers in split terminals within VS Code.

### Option 2: Command Line
```cmd
cd deployment-ui
start-ui.cmd
```

### Option 3: PowerShell Script (from root)
```powershell
.\Start-DeploymentUI.ps1
```
Note: May require execution policy adjustment.

### Option 4: Manual Servers
```powershell
# Terminal 1: Backend
cd deployment-ui\backend
python main.py

# Terminal 2: Frontend
cd deployment-ui\frontend
npm run dev
```

## Debugging

To debug the Python backend with breakpoints:
1. Press `F5` or go to Run and Debug
2. Select **"Python: Backend (FastAPI)"**

The frontend will need to be started separately using one of the methods above.

## Manual Setup

### Backend

```powershell
cd deployment-ui\backend
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

### Frontend

```powershell
cd deployment-ui\frontend
npm install
npm run dev
```

## Features

- 🎯 Select deployment target (Development, Test, etc.)
- 📁 Browse modules by category
- 🚀 Deploy modules to environments
- 🔄 Sync modules from environments
- 📺 Real-time output streaming
- 🎨 Clean, modern UI

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Svelte + Vite
- **Communication**: Server-Sent Events for real-time streaming
