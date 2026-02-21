# Starting FAST Tools

## Quick Start (First Time Setup)
Run this once to install dependencies:
```powershell
.\Start-UITools.ps1
```
This sets up the virtual environment, installs Python packages, and npm modules.

## Development Workflow (Recommended)

For active development with full log visibility and independent restarts:

**Terminal 1 - Backend:**
```powershell
.\Start-Backend.ps1
```
- Shows all Python logs and debug output
- Press Ctrl+C to stop, re-run to restart
- Runs on http://localhost:8000

**Terminal 2 - Frontend:**
```powershell
.\Start-Frontend.ps1
```
- Shows Vite dev server output
- Press Ctrl+C to stop, re-run to restart
- Runs on http://localhost:5173

**Benefits:**
- ✅ See all backend debug logs (`[DEBUG]` statements)
- ✅ See frontend build/error messages
- ✅ Restart backend without affecting frontend (and vice versa)
- ✅ Easy to debug issues
- ✅ No hidden background jobs

## Production/Demo Mode

For quick demos or when you don't need to see logs:
```powershell
.\Start-UITools.ps1
```
Starts both servers, opens browser automatically, runs frontend in terminal and backend as background job.

## Troubleshooting

**Python cache issues:**
```powershell
Get-ChildItem -Path ui-tools\backend -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

**Port already in use:**
```powershell
# Kill Python processes
Get-Process python -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*industry-apps*"} | Stop-Process -Force

# Kill Node processes
Get-Process node -ErrorAction SilentlyContinue | Where-Object {$_.Path -like "*industry-apps*"} | Stop-Process -Force
```
