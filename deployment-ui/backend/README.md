# Backend

FastAPI backend for the Module Deployment UI.

## Setup

```powershell
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\Activate

# Install dependencies
pip install -r requirements.txt
```

## Run

```powershell
python main.py
```

Or with auto-reload:

```powershell
uvicorn main:app --reload --port 8000
```

## API Endpoints

- `GET /api/config` - Get deployment configuration and available modules
- `POST /api/deploy` - Deploy a module (Server-Sent Events)
- `POST /api/sync` - Sync a module from environment (Server-Sent Events)
