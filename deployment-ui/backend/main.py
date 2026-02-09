from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import asyncio
import json
from pathlib import Path
from typing import Optional

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
    
    # Scan for all modules
    for category_dir in PROJECT_ROOT.iterdir():
        if category_dir.is_dir() and category_dir.name not in exclude_folders:
            for module_dir in category_dir.iterdir():
                if module_dir.is_dir() and list(module_dir.glob("*.cdsproj")):
                    module_name = module_dir.name
                    
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
                            "category": category_dir.name,
                            "tenant": tenant,
                            "deployment": deployment_name,
                            "sourceEnvironment": source_env,
                            "sourceEnvironmentKey": source_env_key,
                            "targetEnvironments": target_envs,
                            "targetEnvironmentKeys": target_env_keys
                        })
    
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
        # Build PowerShell command
        cmd = ["pwsh", "-NoProfile", "-File", str(script_path)] + list(args)
        
        # Start process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(PROJECT_ROOT)
        )
        
        # Stream stdout
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            yield f"data: {json.dumps({'type': 'output', 'line': line.decode('utf-8', errors='replace').rstrip()})}\n\n"
        
        # Wait for process to complete
        await process.wait()
        
        # Send completion status
        yield f"data: {json.dumps({'type': 'complete', 'exitCode': process.returncode})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"

@app.post("/api/deploy")
async def deploy_module(request: DeployRequest):
    """Deploy a module to the selected environment"""
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "Deploy-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module
        ),
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
    script_path = PROJECT_ROOT / "deployment-ui" / "scripts" / "New-Module-UI.ps1"
    
    args = [
        str(script_path),
        "-Category", request.category,
        "-ModuleName", request.moduleName
    ]
    
    if request.deploy:
        args.append("-Deploy")
    
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
