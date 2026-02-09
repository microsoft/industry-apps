# UI Scripts

Non-interactive PowerShell scripts designed for the Deployment UI web application.

## Scripts

### Sync-Module-UI.ps1
Syncs a module from an environment to your local workspace.

**Usage:**
```powershell
.\Sync-Module-UI.ps1 -Deployment "Development" -Category "cross-industry" -Module "core"
```

### Deploy-Module-UI.ps1
Builds and deploys a module to an environment.

**Usage:**
```powershell
.\Deploy-Module-UI.ps1 -Deployment "Development" -Category "cross-industry" -Module "core"
```

## Features

- ✅ **Non-interactive** - No prompts, fully automated
- ✅ **Command-line arguments** - Accept deployment, category, and module names
- ✅ **Reuses existing functions** - Leverages `Util.ps1` for tenant/environment connections
- ✅ **Proper error handling** - Exits with code 1 on errors
- ✅ **Colored output** - Easy to read in the UI
- ✅ **Config-driven** - Reads from `.config/deployments.json`

## How It Works

Both scripts:
1. Load the deployment configuration
2. Determine the target environment based on module config
3. Connect to the tenant and environment using PAC CLI
4. Execute the operation (sync or deploy)

## Called By

These scripts are invoked by the FastAPI backend (`deployment-ui/backend/main.py`) which streams their output to the Svelte frontend in real-time.
