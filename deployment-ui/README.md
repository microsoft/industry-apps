# Deployment UI

FastAPI + Svelte web application for deploying Dataverse modules.

## Quick Start

```powershell
.\Start-DeploymentUI.ps1
```

This will:
1. Set up Python virtual environment (.venv)
2. Install backend dependencies
3. Install frontend dependencies
4. Start both servers
5. Open your browser to http://localhost:5173

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
