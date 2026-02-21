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
import xml.etree.ElementTree as ET
from dataverse_client import DataverseClient

app = FastAPI(title="Module Deployment API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get project root (go up from backend to repo root)
PROJECT_ROOT = Path(__file__).parent.parent.parent

def read_solution_version(module_path: Path) -> str:
    """Read version from Solution.xml file"""
    solution_xml_path = module_path / "src" / "Other" / "Solution.xml"
    
    if not solution_xml_path.exists():
        print(f"Version file not found: {solution_xml_path}", file=sys.stderr)
        return "1.0.0.0"  # Default version if not found
    
    try:
        tree = ET.parse(solution_xml_path)
        root = tree.getroot()
        
        # Find the Version element (no namespace in these files)
        version_elem = root.find(".//{http://www.w3.org/2001/XMLSchema-instance}Version")
        if version_elem is None:
            # Try without namespace
            version_elem = root.find(".//Version")
        
        if version_elem is not None and version_elem.text:
            version = version_elem.text.strip()
            
            # Normalize to 4-part version
            parts = version.split('.')
            while len(parts) < 4:
                parts.append('0')
            
            normalized = '.'.join(parts[:4])
            print(f"Read version {version} -> {normalized} from {solution_xml_path}", file=sys.stderr)
            return normalized
        
        print(f"Version element not found in {solution_xml_path}", file=sys.stderr)
        return "1.0.0.0"
    except Exception as e:
        print(f"Error reading version from {solution_xml_path}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return "1.0.0.0"

class DeployRequest(BaseModel):
    deployment: str
    category: str
    module: str
    targetEnvironment: str = None
    managed: bool = True
    upgrade: bool = False

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

class UpdateVersionRequest(BaseModel):
    deployment: str
    category: str
    module: str

class CreateFieldsRequest(BaseModel):
    deployment: str
    environment: str
    tableName: str
    fields: list[dict]

class FieldTemplateRequest(BaseModel):
    name: str
    description: str = ""
    publisherPrefix: str = ""
    fields: list[dict]

@app.get("/api/config")
async def get_config():
    """Get deployment configuration and available modules"""
    config_path = PROJECT_ROOT / ".config" / "deployments.json"
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Get categories and modules
    categories = {}
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools"}
    
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
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools", "releases"}
    
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
                        
                        # Read version from Solution.xml
                        version = read_solution_version(item)
                        
                        modules.append({
                            "name": module_name,
                            "category": category,
                            "tenant": tenant,
                            "deployment": deployment_name,
                            "sourceEnvironment": source_env,
                            "sourceEnvironmentKey": source_env_key,
                            "targetEnvironments": target_envs,
                            "targetEnvironmentKeys": target_env_keys,
                            "version": version
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
    
    print(f"[DEBUG] Deploy args: {args}")  # Debug logging
    
    return StreamingResponse(
        stream_powershell_output(*args),
        media_type="text/event-stream"
    )

@app.post("/api/sync")
async def sync_module(request: SyncRequest):
    """Sync a module from the selected environment"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Sync-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module
        ),
        media_type="text/event-stream"
    )

@app.post("/api/version")
async def update_version(request: UpdateVersionRequest):
    """Update a module's version (online and local)"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Update-Version-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Deployment", request.deployment,
            "-Category", request.category,
            "-Module", request.module,
            "-Version", request.version
        ),
        media_type="text/event-stream"
    )

@app.post("/api/ship")
async def ship_module(request: ShipRequest):
    """Ship a module to an external tenant/environment"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Ship-Module-UI.ps1"
    
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
        stream_powershell_output(*args),
        media_type="text/event-stream"
    )

@app.post("/api/modules/release")
async def create_release(request: ReleaseRequest):
    """Create a release for a module"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Release-Module-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-Category", request.category,
            "-Module", request.module
        ),
        media_type="text/event-stream"
    )
@app.post("/api/helpers/create-fields")
async def create_fields(request: CreateFieldsRequest):
    """Mass create fields on a Dataverse table using Python Dataverse client"""
    
    async def stream_field_creation():
        try:
            # Load deployment configuration
            config_path = PROJECT_ROOT / ".config" / "deployments.json"
            if not config_path.exists():
                yield f"data: {{\"type\": \"error\", \"message\": \"Configuration not found at {config_path}\"}}\n\n"
                return
            
            with open(config_path) as f:
                config = json.load(f)
            
            # Get the deployment configuration
            if request.deployment not in config.get("Deployments", {}):
                yield f"data: {{\"type\": \"error\", \"message\": \"Deployment '{request.deployment}' not found in configuration\"}}\n\n"
                return
            
            deployment_config = config["Deployments"][request.deployment]
            
            # Get authentication configuration from deployment
            if "Auth" not in deployment_config:
                yield f"data: {{\"type\": \"error\", \"message\": \"Auth configuration missing for deployment '{request.deployment}'. Please add Auth section with TenantId, ClientId, ClientSecret, and EnvironmentUrls.\"}}\n\n"
                return
            
            auth_config = deployment_config["Auth"]
            tenant_id = auth_config.get("TenantId")
            client_id = auth_config.get("ClientId")
            client_secret = auth_config.get("ClientSecret")
            
            if not all([tenant_id, client_id, client_secret]):
                yield f"data: {{\"type\": \"error\", \"message\": \"Incomplete auth configuration for deployment '{request.deployment}'. TenantId, ClientId, and ClientSecret are required.\"}}\n\n"
                return
            
            # Get environment URL from auth configuration
            environment_url = auth_config.get("EnvironmentUrls", {}).get(request.environment)
            if not environment_url:
                yield f"data: {{\"type\": \"error\", \"message\": \"Environment URL not configured for '{request.environment}' in deployment '{request.deployment}'\"}}\n\n"
                return
            
            # Initialize message
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Create Fields on Table: {request.tableName} ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Deployment: {request.deployment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Environment: {request.environment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Table: {request.tableName}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Fields to create: {len(request.fields)}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create Dataverse client
            yield f"data: {{\"type\": \"output\", \"line\": \"Connecting to Dataverse...\"}}\n\n"
            client = DataverseClient(
                environment_url=environment_url,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            
            # Authenticate
            client.authenticate()
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Connected successfully\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Creating fields...\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create fields
            success_count = 0
            fail_count = 0
            
            for i, field in enumerate(request.fields, 1):
                schema_name = field.get("schemaName")
                display_name = field.get("displayName")
                field_type = field.get("type")
                
                yield f"data: {{\"type\": \"output\", \"line\": \"[{i}/{len(request.fields)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  Type: {field_type}\"}}\n\n"
                
                # Create the field
                result = client.create_field(request.tableName, field)
                
                if result.get("success"):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Field created successfully\"}}\n\n"
                    success_count += 1
                else:
                    error_msg = result.get("error", "Unknown error")
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                    fail_count += 1
                
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Summary
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Summary ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Total fields: {len(request.fields)}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Successful: {success_count}\"}}\n\n"
            if fail_count > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Failed: {fail_count}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Complete
            exit_code = 0 if fail_count == 0 else 1
            yield f"data: {{\"type\": \"complete\", \"exitCode\": {exit_code}}}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
            traceback.print_exc()
    
    return StreamingResponse(
        stream_field_creation(),
        media_type="text/event-stream"
    )

@app.get("/api/helpers/field-templates")
async def get_field_templates():
    """Get list of all saved field templates"""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    templates = []
    for template_file in templates_dir.glob("*.json"):
        try:
            with open(template_file) as f:
                template_data = json.load(f)
                templates.append({
                    "name": template_data.get("name", template_file.stem),
                    "description": template_data.get("description", ""),
                    "fieldCount": len(template_data.get("fields", []))
                })
        except Exception as e:
            print(f"Error reading template {template_file}: {e}", file=sys.stderr)
    
    return {"templates": templates}

@app.post("/api/helpers/field-templates")
async def save_field_template(request: FieldTemplateRequest):
    """Save a field template"""
    templates_dir = Path(__file__).parent / "templates"
    templates_dir.mkdir(exist_ok=True)
    
    # Sanitize filename
    safe_name = "".join(c for c in request.name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    template_file = templates_dir / f"{safe_name}.json"
    
    template_data = {
        "name": request.name,
        "description": request.description,
        "publisherPrefix": request.publisherPrefix,
        "fields": request.fields
    }
    
    try:
        with open(template_file, 'w') as f:
            json.dump(template_data, f, indent=2)
        return {"success": True, "message": f"Template '{request.name}' saved successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.delete("/api/helpers/field-templates/{name}")
async def delete_field_template(name: str):
    """Delete a field template"""
    templates_dir = Path(__file__).parent / "templates"
    
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    template_file = templates_dir / f"{safe_name}.json"
    
    if template_file.exists():
        try:
            template_file.unlink()
            return {"success": True, "message": f"Template '{name}' deleted successfully"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": f"Template '{name}' not found"}

@app.get("/api/helpers/field-templates/{name}")
async def get_field_template(name: str):
    """Get a specific field template"""
    templates_dir = Path(__file__).parent / "templates"
    
    # Sanitize filename
    safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_name = safe_name.replace(' ', '_').lower()
    template_file = templates_dir / f"{safe_name}.json"
    
    if template_file.exists():
        try:
            with open(template_file) as f:
                template_data = json.load(f)
            return template_data
        except Exception as e:
            return {"success": False, "error": str(e)}
    else:
        return {"success": False, "error": f"Template '{name}' not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
