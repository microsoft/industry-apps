# UI Tools

FastAPI + Svelte web application for Dataverse solution management and utilities.

## Quick Start

### Option 1: VS Code Tasks (Recommended)
Press `Ctrl+Shift+P` and run:
- **"Tasks: Run Task"** → **"Start UI Tools (Both)"**

This starts both servers in split terminals within VS Code.

### Option 2: Command Line
```cmd
cd ui-tools
start-ui.cmd
```

### Option 3: PowerShell Script
```powershell
cd ui-tools
.\Start-UITools.ps1
```

### Option 4: Manual Servers
```powershell
# Terminal 1: Backend
cd ui-tools\backend
python main.py

# Terminal 2: Frontend
cd ui-tools\frontend
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
cd ui-tools\backend
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

### Frontend

```powershell
cd ui-tools\frontend
npm install
npm run dev
```

### Dataverse Authentication (for Field Creator)

The Field Creator requires app-based authentication to Dataverse:

1. **Register an application in Azure AD**
2. **Create client secret**
3. **Grant Dynamics CRM API permissions**
4. **Create application user in Dataverse**
5. **Configure `.config/dataverse-auth.json`**

📖 **See [DATAVERSE_AUTH_SETUP.md](DATAVERSE_AUTH_SETUP.md) for complete setup instructions**

## Features

### Deployment Management
- 🎯 Select deployment target (Development, Test, etc.)
- 📁 Browse modules by category
- 🚀 Deploy modules to environments
- 🔄 Sync modules from environments
- � Create new modules with wizard
- 🔢 Version management with inline editing
- 📺 Real-time output streaming
- 🎨 Clean, modern UI with drag-and-drop

### Field Creator
- 📋 Mass create fields on Dataverse tables
- 🎛️ Support for all standard field types (Text, Number, Date, Boolean)
- ✅ Structured input format with validation
- 📊 Real-time creation progress
- 🎯 Target any environment in your deployments
- 🔐 **App-based authentication** via Azure AD
- 🐍 **Python Dataverse Web API integration** (no PAC CLI required)
- ⚡ Direct API calls for better performance and error handling

### Future Utilities
- 🔧 Additional solution management utilities
- 📊 Data migration tools
- ⚙️ Configuration helpers

## Architecture

The application now uses a modern, scalable architecture:

**Frontend:**
- **Framework**: Svelte 4 with component-based architecture
- **Routing**: svelte-spa-router for client-side navigation
- **State Management**: Svelte stores for shared state
- **Components**: Modular, reusable UI components
- **Build Tool**: Vite for fast development

**Backend:**
- **Framework**: FastAPI (Python)
- **Streaming**: Server-Sent Events (SSE) for real-time output
- **Integration**: PowerShell script orchestration for deployments
- **Dataverse**: Direct Web API integration with MSAL authentication
- **HTTP Client**: httpx for async Dataverse API calls

**Infrastructure:**
- PowerShell scripts for solution deployment operations
- PAC CLI integration for solution management
- Python Dataverse client for field/table operations
- App-based authentication (client credentials flow)

## Project Structure

```
ui-tools/
├── backend/
│   ├── main.py                 # FastAPI application with all endpoints
│   ├── dataverse_client.py     # Dataverse Web API client
│   ├── requirements.txt        # Python dependencies
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── routes/            # Page components (routed)
│   │   │   ├── Deploy.svelte          # Deployment management page
│   │   │   └── FieldCreator.svelte    # Field creator page
│   │   ├── lib/               # Shared components
│   │   │   ├── Sidebar.svelte         # Navigation sidebar
│   │   │   ├── Modal.svelte           # Reusable modal
│   │   │   ├── OutputStream.svelte    # Output display
│   │   │   ├── Header.svelte          # Page header
│   │   │   └── stores.js              # Svelte stores
│   │   ├── App.svelte         # Root layout with routing
│   │   └── main.js            # Entry point
│   ├── package.json
│   └── README.md
├── scripts/                    # PowerShell scripts
│   ├── Deploy-Module-UI.ps1
│   ├── Sync-Module-UI.ps1
│   ├── Ship-Module-UI.ps1
│   ├── Create-Module-UI.ps1
│   ├── Create-Fields-UI.ps1   # Field creation script
│   └── README.md
├── start-ui.cmd               # Windows batch starter
└── README.md                  # This file
```

## Adding New Helper Functions

The architecture makes it easy to add new helper functions. For each new feature:

1. **Create a route component**: Add a new `.svelte` file in `frontend/src/routes/`
   - Import shared stores for config/data access
   - Use `OutputStream` component for operation output
   - Call backend API endpoints

2. **Add API endpoint**: Add a new endpoint in `backend/main.py`
   - Create a Pydantic model for request data
   - Use `StreamingResponse` with `stream_powershell_output`
   - Follow existing patterns

3. **Create PowerShell script**: Add corresponding script in `scripts/`
   - Source `.scripts/Util.ps1` for common functions
   - Use `Connect-DataverseTenant` and `Connect-DataverseEnvironment`
   - Provide colored output and progress indicators

4. **Update sidebar**: Add navigation link in `frontend/src/lib/Sidebar.svelte`

Example pattern for any helper:
```
User Action → Route Component → API Endpoint → PowerShell Script → SSE Stream → Output Display
```

## Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: Svelte + Vite
- **Communication**: Server-Sent Events for real-time streaming
