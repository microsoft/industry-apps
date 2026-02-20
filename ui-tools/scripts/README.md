# UI Tools PowerShell Scripts

Non-interactive PowerShell scripts for the UI Tools web application.

## Deployment Scripts

### Deploy-Module-UI.ps1
Builds and deploys a module to an environment.

**Parameters:**
- `-Deployment` - Deployment name from config
- `-Category` - Module category folder
- `-Module` - Module name
- `-Environment` - Target environment (optional)
- `-Managed` - Deploy as managed solution (switch)
- `-Upgrade` - Upgrade mode, delete removed components (switch)

**Usage:**
```powershell
.\Deploy-Module-UI.ps1 -Deployment "Development" -Category "cross-industry" -Module "core" -Managed -Upgrade
```

### Sync-Module-UI.ps1
Syncs a module from an environment to your local workspace.

**Parameters:**
- `-Deployment` - Deployment name
- `-Category` - Module category
- `-Module` - Module name

**Usage:**
```powershell
.\Sync-Module-UI.ps1 -Deployment "Development" -Category "cross-industry" -Module "core"
```

### Ship-Module-UI.ps1
Ships solutions by creating managed versions for external tenants.

**Parameters:**
- `-Deployment` - Deployment name
- `-Category` - Module category
- `-Module` - Module name
- `-Environment` - Target environment

**Usage:**
```powershell
.\Ship-Module-UI.ps1 -Deployment "Production" -Category "cross-industry" -Module "core" -Environment "PROD"
```

### New-Module-UI.ps1
Creates a new module structure.

**Parameters:**
- `-Category` - Category for the new module
- `-ModuleName` - Name of the new module
- `-Deploy` - Whether to deploy after creation (switch)
- `-Deployment` - Deployment name (required if -Deploy)
- `-Environment` - Source environment (required if -Deploy)

**Usage:**
```powershell
.\New-Module-UI.ps1 -Category "workforce" -ModuleName "training" -Deploy -Deployment "Development" -Environment "DEV"
```

### Update-Version-UI.ps1
Updates module version numbers.

**Parameters:**
- `-Deployment` - Deployment name
- `-Category` - Module category
- `-Module` - Module name
- `-Environment` - Target environment
- `-Version` - New version number (e.g., "1.2.0.0")

**Usage:**
```powershell
.\Update-Version-UI.ps1 -Deployment "Development" -Category "cross-industry" -Module "core" -Environment "DEV" -Version "1.2.0.0"
```

### Release-Module-UI.ps1
Creates release packages for a module.

**Parameters:**
- `-Category` - Module category
- `-Module` - Module name

**Usage:**
```powershell
.\Release-Module-UI.ps1 -Category "cross-industry" -Module "core"
```

## Helper Scripts

### Create-Fields-UI.ps1
Mass creates fields on a Dataverse table.

**Parameters:**
- `-Deployment` - Deployment name
- `-Environment` - Target environment
- `-TableName` - Logical name of the target table
- `-FieldsJson` - JSON string array of field definitions

**Field Definition Format:**
```json
[
  {
    "schemaName": "cr09x_fieldname",
    "displayName": "Field Display Name",
    "type": "Text",
    "required": false,
    "maxLength": 100
  }
]
```

**Supported Field Types:**
- Text
- Number (Whole Number, Decimal, Float, Currency)
- Date
- DateTime
- Boolean (Yes/No)
- Choice (Option Set)
- MultiChoice
- Lookup
- Customer
- Owner
- Image
- File

**Usage:**
```powershell
$fields = @'
[
  {"schemaName": "cr09x_customtext", "displayName": "Custom Text", "type": "Text", "required": false, "maxLength": 100},
  {"schemaName": "cr09x_customnumber", "displayName": "Custom Number", "type": "Number", "required": false}
]
'@

.\Create-Fields-UI.ps1 -Deployment "Development" -Environment "DEV" -TableName "cr09x_customtable" -FieldsJson $fields
```

## Features

- ✅ **Non-interactive** - No prompts, fully automated
- ✅ **Command-line arguments** - All parameters via command line
- ✅ **Reuses existing functions** - Leverages `.scripts/Util.ps1` for common operations
- ✅ **Proper error handling** - Returns exit codes (0 = success, 1 = error)
- ✅ **Colored output** - Uses Write-Host with colors for readability
- ✅ **Config-driven** - Reads from `.config/deployments.json`
- ✅ **Progress indicators** - Shows progress for multi-step operations

## How It Works

All scripts follow a common pattern:
1. Parse command-line parameters
2. Load deployment configuration from `.config/deployments.json`
3. Determine target tenant and environment
4. Connect to Dataverse using PAC CLI (via Util.ps1 functions)
5. Execute the operation
6. Provide colored output and progress updates
7. Exit with appropriate code (0 or 1)

## Called By

These scripts are invoked by the FastAPI backend (`ui-tools/backend/main.py`) which:
- Spawns PowerShell process with the script and arguments
- Streams output line-by-line via Server-Sent Events
- Reports completion status to the frontend

The Svelte frontend displays the streaming output in real-time in a modal dialog.

## Common Functions (from Util.ps1)

Scripts use these helper functions from `.scripts/Util.ps1`:

- `Connect-DataverseTenant` - Selects PAC CLI auth profile
- `Connect-DataverseEnvironment` - Selects target environment
- `Get-EnvironmentUrl` - Gets environment URL from config
- Additional utility functions for solution management

## Adding New Scripts

To add a new helper script:

1. Create `<FunctionName>-UI.ps1` in `ui-tools/scripts/`
2. Follow the parameter pattern with clear documentation
3. Source `.scripts/Util.ps1` at the beginning
4. Use colored Write-Host output for readability
5. Handle errors and exit with appropriate codes
6. Add endpoint in `ui-tools/backend/main.py`
7. Create route component in `ui-tools/frontend/src/routes/`
8. Update sidebar navigation

See `Create-Fields-UI.ps1` as an example of a helper script.
