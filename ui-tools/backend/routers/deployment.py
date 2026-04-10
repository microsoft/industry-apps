"""
Deployment Router - API endpoints for module deployment operations.

This module contains endpoints for:
- Deploying modules to environments
- Syncing modules from Dataverse
- Syncing from specific environments
- Updating module versions
"""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pathlib import Path
import sys

# Import from parent (backend) directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from models import (
    DeployRequest,
    SyncRequest,
    SyncFromRequest,
    UpdateVersionRequest
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

