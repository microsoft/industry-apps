"""
Deployment Router - API endpoints for module deployment operations.

This module contains endpoints for:
- Deploying modules to environments
- Syncing modules from Dataverse
- Syncing from specific environments
- Updating module versions
- Shipping modules to external tenants
- Creating new modules
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
import sys
import json

# Import from parent (backend) directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from models import (
    DeployRequest,
    SyncRequest,
    SyncFromRequest,
    UpdateVersionRequest,
    ShipRequest,
    CreateModuleRequest,
    ImportDataRequest
)

# Import helper functions from utils
from utils import stream_powershell_output


router = APIRouter(tags=["Deployment"])


@router.post("/api/deploy")
async def deploy_module(request: DeployRequest):
    """Deploy a module to the selected environment"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Deploy-Module-UI.ps1"
    
    args = [
        str(script_path),
        "-Deployment", request.deployment,
        "-Category", request.category,
        "-Module", request.module
    ]
    
    if request.targetEnvironment:
        args.extend(["-Environment", request.targetEnvironment])
    
    if request.managed:
        args.append("-Managed")
    
    if request.upgrade:
        args.append("-Upgrade")
    
    # print(f"[DEBUG] Deploy args: {args}")  # Debug logging
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
        media_type="text/event-stream"
    )

@router.post("/api/sync")
async def sync_module(request: SyncRequest):
    """Sync a module from the selected environment"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Sync-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@router.post("/api/sync-from")
async def sync_module_from_environment(request: SyncFromRequest):
    """Sync a module FROM a specific environment (bidirectional sync for hotfixes)"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Sync-Module-From-Environment-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module,
            "-SourceEnvironment", request.sourceEnvironment,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@router.post("/api/version")
async def update_version(request: UpdateVersionRequest):
    """Update a module's version (online and local)"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Update-Version-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module,
            "-Version", request.version,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@router.post("/api/ship")
async def ship_module(request: ShipRequest):
    """Ship a module to an external tenant/environment"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Ship-Module-UI.ps1"
    
    args = [
        str(script_path),
        "-Deployment", request.tenant,
        "-Environment", request.environment,
        "-Category", request.category,
        "-Module", request.module
    ]
    
    if request.managed:
        args.append("-Managed")
    
    if request.upgrade:
        args.append("-Upgrade")
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
        media_type="text/event-stream"
    )

@router.post("/api/modules/create")
async def create_module(request: CreateModuleRequest):
    """Create a new module"""
    
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "New-Module-UI.ps1"
    
    # First, save the module configuration to deployments.json
    config_path = PROJECT_ROOT / ".config" / "deployments.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Determine the module folder name (lowercase with hyphens)
    module_folder = request.moduleName.lower()
    module_folder = ''.join(c if c.isalnum() else '-' for c in module_folder)
    module_folder = '-'.join(filter(None, module_folder.split('-')))
    
    # Check if module configuration matches DefaultModule
    default_module = config.get("DefaultModule", {})
    matches_default = (
        default_module.get("Tenant") == request.deployment and
        default_module.get("Environment") == request.sourceEnvironment and
        default_module.get("DeploymentTargets", []) == request.targetEnvironments
    )
    
    # Only add to Modules if it differs from DefaultModule
    if not matches_default:
        if "Modules" not in config:
            config["Modules"] = {}
        
        config["Modules"][module_folder] = {
            "Tenant": request.deployment,
            "Environment": request.sourceEnvironment,
            "DeploymentTargets": request.targetEnvironments
        }
        
        # Save updated config
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)
    
    # Run the creation script
    args = [
        str(script_path),
        "-Category", request.category,
        "-ModuleName", request.moduleName
    ]
    
    if request.deploy:
        if not request.deployment or not request.sourceEnvironment:
            raise HTTPException(status_code=400, detail="Deployment and sourceEnvironment are required when deploy=true")
        args.append("-Deploy")
        args.extend(["-Deployment", request.deployment])
        args.extend(["-Environment", request.sourceEnvironment])
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
        media_type="text/event-stream"
    )

@router.post("/api/deployment/import-data")
async def import_data(request: ImportDataRequest):
    """Import sample data for a module into an environment"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Import-Data.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-EnvironmentKey", request.environment_key,
            "-ModulePath", request.module_path,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@router.get("/api/deployment/check-sample-data")
async def check_sample_data(module_path: str):
    """Check if a module has sample data available"""
    full_path = PROJECT_ROOT / module_path / "sample-data"
    data_zip = full_path / "data.zip"
    gov_data_zip = full_path / "gov-data.zip"
    
    has_data = data_zip.exists() or gov_data_zip.exists()
    
    data_file = None
    if data_zip.exists():
        data_file = "data.zip"
    elif gov_data_zip.exists():
        data_file = "gov-data.zip"
    
    return {
        "exists": has_data,
        "path": str(full_path) if has_data else None,
        "data_file": data_file
    }

