from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from pathlib import Path
from typing import Optional
import sys
import subprocess
import shutil

app = FastAPI(title="Module Deployment API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get project root (go up from backend to repo root)
PROJECT_ROOT = Path(__file__).parent.parent.parent

class DeployRequest(BaseModel):
    deployment: str
    category: str
    module: str
    targetEnvironment: str = None
    managed: bool = True

class SyncRequest(BaseModel):
    deployment: str
    category: str
    module: str

class ShipRequest(BaseModel):
    tenant: str
    environment: str
    category: str
    module: str

class CreateModuleRequest(BaseModel):
    category: str
    moduleName: str
    deployment: str
    sourceEnvironment: str
    targetEnvironments: list[str] = []
    deploy: bool = False

class ReleaseRequest(BaseModel):
    category: str
    module: str

@app.get("/api/config")
async def get_config():
    """Get deployment configuration and available modules"""
    config_path = PROJECT_ROOT / ".config" / "deployments.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Get categories and modules
    categories = {}
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "deployment-ui"}
    
    for item in PROJECT_ROOT.iterdir():
        if item.is_dir() and item.name not in exclude_folders:
            # Check if this directory has modules (subdirs with .cdsproj files)
            modules = []
            for module_dir in item.iterdir():
                if module_dir.is_dir() and list(module_dir.glob("*.cdsproj")):
                    modules.append(module_dir.name)
            
            if modules:
                categories[item.name] = sorted(modules)
    
    return {
        "deployments": config.get("Deployments", {}),
        "categories": categories,
        "modules": config.get("Modules", {}),
        "defaultModule": config.get("DefaultModule", {})
    }

@app.get("/api/modules")
async def get_modules():
    """Get all modules with their metadata, source environments, and targets"""
    config_path = PROJECT_ROOT / ".config" / "deployments.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    deployments = config.get("Deployments", {})
    module_configs = config.get("Modules", {})
    default_config = config.get("DefaultModule", {})
    
    modules = []
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "deployment-ui", "releases"}
    
    # Recursively scan for all modules (handles nested folder structures)
    def scan_for_modules(base_path, relative_path=""):
        for item in base_path.iterdir():
            if item.is_dir() and item.name not in exclude_folders:
                # Check if this directory contains a .cdsproj file (it's a module)
                if list(item.glob("*.cdsproj")):
                    module_name = item.name
                    category = relative_path if relative_path else item.parent.name
                    
                    # Get module-specific config or use default
                    mod_config = module_configs.get(module_name, default_config)
                    
                    if mod_config:
                        deployment_name = mod_config.get("Tenant")
                        source_env_key = mod_config.get("Environment")
                        target_env_keys = mod_config.get("DeploymentTargets", [])
                        
                        # Resolve environment names
                        deployment = deployments.get(deployment_name, {})
                        tenant = deployment.get("Tenant", "")
                        environments = deployment.get("Environments", {})
                        
                        source_env = environments.get(source_env_key, source_env_key)
                        target_envs = [environments.get(key, key) for key in target_env_keys]
                        
                        modules.append({
                            "name": module_name,
                            "category": category,
                            "tenant": tenant,
                            "deployment": deployment_name,
                            "sourceEnvironment": source_env,
                            "sourceEnvironmentKey": source_env_key,
                            "targetEnvironments": target_envs,
                            "targetEnvironmentKeys": target_env_keys
                        })
                else:
                    # Recursively scan subdirectories
                    new_relative = f"{relative_path}/{item.name}" if relative_path else item.name
                    scan_for_modules(item, new_relative)
    
    # Scan for all modules starting from project root
    for category_dir in PROJECT_ROOT.iterdir():
        if category_dir.is_dir() and category_dir.name not in exclude_folders:
            scan_for_modules(category_dir, category_dir.name)
    
    return {"modules": modules}

@app.get("/api/environments")
async def get_environments():
    """Get environment topology organized by tenant"""
    config_path = PROJECT_ROOT / ".config" / "deployments.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    deployments = config.get("Deployments", {})
    
    # Organize by tenant
    tenants = {}
    for deployment_name, deployment_data in deployments.items():
        tenant = deployment_data.get("Tenant", "Unknown")
        environments = deployment_data.get("Environments", {})
        
        if tenant not in tenants:
            tenants[tenant] = {
                "name": tenant,
                "deployments": []
            }
        
        tenants[tenant]["deployments"].append({
            "name": deployment_name,
            "environments": [
                {"key": key, "name": value}
                for key, value in environments.items()
            ]
        })
    
    return {"tenants": list(tenants.values())}

async def stream_powershell_output(script_path: str, *args):
    """Stream PowerShell script output in real-time"""
    try:
        # Try pwsh first, fall back to powershell
        powershell_cmd = "pwsh"
        if not shutil.which("pwsh"):
            powershell_cmd = "powershell"
        
        # Build PowerShell command
        cmd = [powershell_cmd, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + list(args)
        
        print(f"[DEBUG] Running command: {' '.join(cmd)}")
        
        # Start process using subprocess.Popen (synchronous but non-blocking)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            cwd=str(PROJECT_ROOT),
            text=True,
            bufsize=1,  # Line buffered
            universal_newlines=True
        )
        
        # Stream stdout (includes stderr now)
        for line in iter(process.stdout.readline, ''):
            if line:
                yield f"data: {json.dumps({'type': 'output', 'line': line.rstrip()})}\n\n"
                await asyncio.sleep(0)  # Yield control to allow async processing
        
        # Wait for process to complete
        process.wait()
        
        # Send completion status
        yield f"data: {json.dumps({'type': 'complete', 'exitCode': process.returncode})}\n\n"
        
    except Exception as e:
        error_msg = str(e) if str(e) else f"{type(e).__name__}: {repr(e)}"
        print(f"[ERROR] Stream exception: {error_msg}")  # Debug logging
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"

@app.post("/api/deploy")
async def deploy_module(request: DeployRequest):
    """Deploy a module to the selected environment"""
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "Deploy-Module-UI.ps1"
    
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
    
    print(f"[DEBUG] Deploy args: {args}")  # Debug logging
    
    return StreamingResponse(
        stream_powershell_output(*args),
        media_type="text/event-stream"
    )

@app.post("/api/sync")
async def sync_module(request: SyncRequest):
    """Sync a module from the selected environment"""
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "Sync-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module
        ),
        media_type="text/event-stream"
    )

@app.post("/api/ship")
async def ship_module(request: ShipRequest):
    """Ship a module to an external tenant/environment"""
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "Ship-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.tenant,
            "-Environment", request.environment,
            "-Category", request.category,
            "-Module", request.module
        ),
        media_type="text/event-stream"
    )

@app.post("/api/modules/create")
async def create_module(request: CreateModuleRequest):
    """Create a new module"""
    
    # Debug logging
    print(f"DEBUG: Received create module request:")
    print(f"  - category: {request.category}")
    print(f"  - moduleName: {request.moduleName}")
    print(f"  - deployment: {request.deployment}")
    print(f"  - sourceEnvironment: {request.sourceEnvironment}")
    print(f"  - targetEnvironments: {request.targetEnvironments}")
    print(f"  - deploy: {request.deploy}")
    
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "New-Module-UI.ps1"
    
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
        stream_powershell_output(*args),
        media_type="text/event-stream"
    )

@app.post("/api/modules/release")
async def create_release(request: ReleaseRequest):
    """Create a release for a module"""
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "Release-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Category", request.category,
            "-Module", request.module
        ),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
