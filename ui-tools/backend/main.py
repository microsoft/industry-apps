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

# Cache directory for pending option sets
CACHE_DIR = Path(__file__).parent / ".cache"
PENDING_CACHE_FILE = CACHE_DIR / "pending_optionsets.json"

def load_pending_optionsets():
    """Load pending option sets from cache file"""
    if not PENDING_CACHE_FILE.exists():
        return []
    try:
        with open(PENDING_CACHE_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("pending", [])
    except Exception as e:
        print(f"Error loading pending option sets: {e}", file=sys.stderr)
        return []

def save_pending_optionsets(pending_list):
    """Save pending option sets to cache file"""
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        with open(PENDING_CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                "pending": pending_list,
                "lastUpdated": asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else None
            }, f, indent=2)
        print(f"[DEBUG] Saved {len(pending_list)} pending option sets to cache")
    except Exception as e:
        print(f"Error saving pending option sets: {e}", file=sys.stderr)

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
    managed: bool = True

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
    """Stream PowerShell script output in real-time using async subprocess"""
    try:
        # Try pwsh first, fall back to powershell
        powershell_cmd = "pwsh"
        if not shutil.which("pwsh"):
            powershell_cmd = "powershell"
        
        # Build PowerShell command
        cmd = [powershell_cmd, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + list(args)
        
        print(f"[DEBUG] Running command: {' '.join(cmd)}")
        
        # Start async process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,  # Merge stderr into stdout
            cwd=str(PROJECT_ROOT)
        )
        
        # Stream stdout (includes stderr now) using async readline
        while True:
            line = await process.stdout.readline()
            if not line:
                break
            
            line_str = line.decode('utf-8', errors='replace').rstrip()
            if line_str:
                yield f"data: {json.dumps({'type': 'output', 'line': line_str})}\n\n"
                await asyncio.sleep(0)  # Yield control to event loop
        
        # Wait for process to complete
        await process.wait()
        
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
    
    args = [
        str(script_path),
        "-Deployment", request.tenant,
        "-Environment", request.environment,
        "-Category", request.category,
        "-Module", request.module
    ]
    
    if request.managed:
        args.append("-Managed")
    
    print(f"[DEBUG] Ship args: {args}")  # Debug logging
    print(f"[DEBUG] request.managed: {request.managed}, type: {type(request.managed)}")
    
    return StreamingResponse(
        stream_powershell_output(*args),
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

# ============================================================================
# GLOBAL CHOICE / OPTION SET MANAGEMENT
# ============================================================================

@app.get("/api/helpers/solutions/list")
async def list_solutions():
    """Scan all modules for Solution.xml files and extract solution information"""
    solutions = []
    
    # Scan all category/module folders
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools"}
    
    for category_dir in PROJECT_ROOT.iterdir():
        if not category_dir.is_dir() or category_dir.name in exclude_folders:
            continue
        
        for module_dir in category_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            solution_xml = module_dir / "src" / "Other" / "Solution.xml"
            if solution_xml.exists():
                try:
                    tree = ET.parse(solution_xml)
                    root = tree.getroot()
                    
                    # Extract solution details
                    manifest = root.find(".//SolutionManifest")
                    if manifest is not None:
                        unique_name = manifest.find("UniqueName")
                        localized_name = manifest.find(".//LocalizedName")
                        publisher = manifest.find(".//Publisher")
                        
                        solution_info = {
                            "uniqueName": unique_name.text if unique_name is not None else "",
                            "displayName": localized_name.get("description") if localized_name is not None else "",
                            "category": category_dir.name,
                            "module": module_dir.name,
                            "path": str(module_dir.relative_to(PROJECT_ROOT))
                        }
                        
                        # Extract publisher prefix and option value prefix
                        if publisher is not None:
                            prefix_elem = publisher.find("CustomizationPrefix")
                            option_prefix_elem = publisher.find("CustomizationOptionValuePrefix")
                            solution_info["prefix"] = prefix_elem.text if prefix_elem is not None else ""
                            solution_info["optionValuePrefix"] = option_prefix_elem.text if option_prefix_elem is not None else ""
                        
                        solutions.append(solution_info)
                        
                except Exception as e:
                    print(f"Error parsing solution XML {solution_xml}: {e}", file=sys.stderr)
    
    return {"solutions": sorted(solutions, key=lambda s: (s.get("category", ""), s.get("module", "")))}

@app.get("/api/helpers/option-sets/scan")
async def scan_option_sets():
    """Scan all modules for existing global option sets"""
    option_sets = []
    
    # Scan all OptionSets folders
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools"}
    
    print(f"[DEBUG] Starting option sets scan in {PROJECT_ROOT}")
    
    for category_dir in PROJECT_ROOT.iterdir():
        if not category_dir.is_dir() or category_dir.name in exclude_folders:
            continue
        
        for module_dir in category_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            option_sets_dir = module_dir / "src" / "OptionSets"
            if option_sets_dir.exists():
                print(f"[DEBUG] Found OptionSets dir: {option_sets_dir}")
                for optionset_xml in option_sets_dir.glob("*.xml"):
                    try:
                        tree = ET.parse(optionset_xml)
                        root = tree.getroot()
                        
                        # Extract option set details
                        schema_name = root.get("Name", "")
                        display_name = root.get("localizedName", "")
                        
                        # Extract options
                        options = []
                        for option_elem in root.findall(".//option"):
                            value = option_elem.get("value", "")
                            label_elem = option_elem.find(".//label")
                            label = label_elem.get("description", "") if label_elem is not None else ""
                            
                            if label:  # Only include options with labels
                                options.append({
                                    "value": value,
                                    "label": label
                                })
                        
                        option_set_info = {
                            "schemaName": schema_name,
                            "displayName": display_name,
                            "options": options,
                            "category": category_dir.name,
                            "module": module_dir.name,
                            "filePath": str(optionset_xml.relative_to(PROJECT_ROOT))
                        }
                        option_sets.append(option_set_info)
                        print(f"[DEBUG] Parsed option set: {display_name} ({schema_name}) with {len(options)} options")
                        
                    except Exception as e:
                        print(f"Error parsing option set XML {optionset_xml}: {e}", file=sys.stderr)
    
    print(f"[DEBUG] Scan complete. Found {len(option_sets)} option sets")
    return {"optionSets": sorted(option_sets, key=lambda o: (o.get("category", ""), o.get("module", ""), o.get("displayName", "")))}

class OptionSetSearchRequest(BaseModel):
    displayName: Optional[str] = None
    optionLabels: Optional[list[str]] = None

@app.post("/api/helpers/option-sets/search")
async def search_option_sets(request: OptionSetSearchRequest):
    """Search for similar option sets based on name or option values"""
    print(f"[DEBUG] Search request: displayName={request.displayName}, optionLabels={request.optionLabels}")
    
    # First, get all option sets
    all_option_sets_response = await scan_option_sets()
    all_option_sets = all_option_sets_response["optionSets"]
    
    print(f"[DEBUG] Searching through {len(all_option_sets)} option sets")
    
    matches = []
    
    for option_set in all_option_sets:
        match_score = 0
        match_reasons = []
        matched_count = 0  # Initialize here for use across all matching logic
        
        # Name matching
        if request.displayName:
            search_name = request.displayName.lower()
            display_name = option_set.get("displayName", "").lower()
            schema_name = option_set.get("schemaName", "").lower()
            
            # Exact match
            if search_name == display_name or search_name == schema_name:
                match_score += 100
                match_reasons.append("Exact name match")
            # Contains match
            elif search_name in display_name or search_name in schema_name:
                match_score += 50
                match_reasons.append("Partial name match")
            # Word match
            elif any(word in display_name or word in schema_name for word in search_name.split()):
                match_score += 25
                match_reasons.append("Word match")
        
        # Option label matching
        if request.optionLabels and len(request.optionLabels) > 0:
            existing_labels = [opt["label"].lower() for opt in option_set.get("options", [])]
            search_terms = [label.lower() for label in request.optionLabels]
            
            print(f"[DEBUG] Matching option set '{option_set.get('displayName')}' - search terms: {search_terms}, existing labels: {existing_labels}")
            
            # Check for exact matches AND partial matches (for multi-word labels)
            matched_count = 0
            matched_labels = []
            
            for search_term in search_terms:
                # Check if search term matches any label exactly or partially
                for existing_label in existing_labels:
                    # Exact match
                    if search_term == existing_label:
                        matched_count += 1
                        matched_labels.append(existing_label)
                        print(f"[DEBUG]   Exact match: '{search_term}' == '{existing_label}'")
                        break
                    # Partial match (search term appears in label, e.g., "Progress" matches "In Progress")
                    elif search_term in existing_label or existing_label in search_term:
                        matched_count += 1
                        matched_labels.append(existing_label)
                        print(f"[DEBUG]   Partial match: '{search_term}' <-> '{existing_label}'")
                        break
            
            print(f"[DEBUG]   Matched {matched_count}/{len(search_terms)} terms")
            
            overlap_percentage = (matched_count / len(search_terms) * 100) if search_terms else 0
            
            if overlap_percentage >= 75:
                match_score += 80
                match_reasons.append(f"{int(overlap_percentage)}% option values match ({matched_count}/{len(search_terms)})")
            elif overlap_percentage >= 50:
                match_score += 50
                match_reasons.append(f"{int(overlap_percentage)}% option values match ({matched_count}/{len(search_terms)})")
            elif overlap_percentage >= 25:
                match_score += 25
                match_reasons.append(f"{int(overlap_percentage)}% option values match ({matched_count}/{len(search_terms)})")
            elif matched_count > 0:
                # Even a single match should show up with a small score
                match_score += 15
                match_reasons.append(f"Partial match ({matched_count}/{len(search_terms)} values)")
        
        # Only include results that actually matched something
        if match_score > 0 or matched_count > 0:
            if match_score == 0 and matched_count > 0:
                match_score = 1  # Give minimal score for sorting
                
            matches.append({
                **option_set,
                "matchScore": match_score,
                "matchReasons": match_reasons if match_reasons else ["Result"]
            })
    
    # Sort by match score descending
    matches.sort(key=lambda m: m["matchScore"], reverse=True)
    
    print(f"[DEBUG] Search complete. Found {len(matches)} matches")
    
    return {"matches": matches}

class OptionSetCreateRequest(BaseModel):
    schemaName: str
    displayName: str
    description: str = ""
    options: list[dict]  # [{label: str, value: Optional[str]}]
    targetSolution: str  # solution unique name
    deployment: str
    environment: str

@app.post("/api/helpers/option-sets/create")
async def create_option_set(request: OptionSetCreateRequest):
    """Create a new global option set in Dataverse"""
    try:
        # Find the target solution
        solutions_response = await list_solutions()
        target_solution = None
        
        for solution in solutions_response["solutions"]:
            if solution["uniqueName"] == request.targetSolution:
                target_solution = solution
                break
        
        if not target_solution:
            return {"success": False, "error": f"Solution '{request.targetSolution}' not found"}
        
        # Validate schema name
        if not request.schemaName or not request.schemaName.replace('_', '').isalnum():
            return {"success": False, "error": "Invalid schema name. Use only letters, numbers, and underscores."}
        
        # Load deployment configuration
        config_path = PROJECT_ROOT / ".config" / "deployments.json"
        if not config_path.exists():
            return {"success": False, "error": f"Configuration not found at {config_path}"}
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Get the deployment configuration
        if request.deployment not in config.get("Deployments", {}):
            return {"success": False, "error": f"Deployment '{request.deployment}' not found in configuration"}
        
        deployment_config = config["Deployments"][request.deployment]
        
        # Get authentication configuration
        if "Auth" not in deployment_config:
            return {"success": False, "error": f"Auth configuration missing for deployment '{request.deployment}'"}
        
        auth_config = deployment_config["Auth"]
        tenant_id = auth_config.get("TenantId")
        client_id = auth_config.get("ClientId")
        client_secret = auth_config.get("ClientSecret")
        
        if not all([tenant_id, client_id, client_secret]):
            return {"success": False, "error": "Incomplete auth configuration. TenantId, ClientId, and ClientSecret are required."}
        
        # Get environment URL
        environment_url = auth_config.get("EnvironmentUrls", {}).get(request.environment)
        if not environment_url:
            return {"success": False, "error": f"Environment URL not configured for '{request.environment}'"}
        
        # Get option value prefix and find next available value
        option_value_prefix = target_solution.get("optionValuePrefix", "14713")
        solution_path = PROJECT_ROOT / target_solution["path"]
        option_sets_dir = solution_path / "src" / "OptionSets"
        
        # Scan existing option sets to find max value
        max_value = 0
        if option_sets_dir.exists():
            for existing_xml in option_sets_dir.glob("*.xml"):
                try:
                    tree = ET.parse(existing_xml)
                    for option_elem in tree.findall(".//option"):
                        value_str = option_elem.get("value", "0")
                        try:
                            value_int = int(value_str)
                            if value_int > max_value:
                                max_value = value_int
                        except ValueError:
                            pass
                except Exception:
                    pass
        
        # Generate values for options
        next_value = max_value + 1 if max_value >= int(option_value_prefix + "0000") else int(option_value_prefix + "0000")
        
        options_with_values = []
        for opt in request.options:
            if opt.get("value"):
                try:
                    options_with_values.append({
                        "label": opt["label"],
                        "value": int(opt["value"])
                    })
                except ValueError:
                    options_with_values.append({
                        "label": opt["label"],
                        "value": next_value
                    })
                    next_value += 1
            else:
                options_with_values.append({
                    "label": opt["label"],
                    "value": next_value
                })
                next_value += 1
        
        # Create Dataverse client and create the option set
        print(f"[DEBUG] Creating global option set '{request.schemaName}' in Dataverse")
        client = DataverseClient(
            environment_url=environment_url,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        # Authenticate
        client.authenticate()
        
        # Create the global option set
        result = client.create_global_optionset(
            schema_name=request.schemaName,
            display_name=request.displayName,
            description=request.description,
            options=options_with_values,
            solution_unique_name=request.targetSolution
        )
        
        if result["success"]:
            # Return complete information for caching
            return {
                "success": True,
                "message": f"Option set '{request.displayName}' created successfully in Dataverse",
                "schemaName": request.schemaName,
                "displayName": request.displayName,
                "description": request.description,
                "category": target_solution["category"],
                "module": target_solution["module"],
                "path": target_solution["path"],
                "options": [{"label": opt["label"], "value": str(opt["value"])} for opt in options_with_values],
                "optionCount": len(options_with_values),
                "deployment": request.deployment,
                "environment": request.environment
            }
        else:
            return result
        
    except Exception as e:
        print(f"Error creating option set: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.get("/api/helpers/option-sets/pending")
async def get_pending_optionsets():
    """Get all pending option sets from cache"""
    try:
        pending = load_pending_optionsets()
        
        # Clean up any that now exist in filesystem
        if pending:
            # Scan filesystem for existing option sets
            all_scanned = []
            exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools"}
            
            for category_dir in PROJECT_ROOT.iterdir():
                if not category_dir.is_dir() or category_dir.name in exclude_folders:
                    continue
                
                for module_dir in category_dir.iterdir():
                    if not module_dir.is_dir():
                        continue
                    
                    option_sets_dir = module_dir / "src" / "OptionSets"
                    if option_sets_dir.exists():
                        for xml_file in option_sets_dir.glob("*.xml"):
                            try:
                                tree = ET.parse(xml_file)
                                root = tree.getroot()
                                schema_name = root.get("Name")
                                if schema_name:
                                    all_scanned.append(schema_name)
                            except Exception:
                                pass
            
            # Filter out pending items that now exist
            scanned_set = set(all_scanned)
            original_count = len(pending)
            pending = [p for p in pending if p.get("schemaName") not in scanned_set]
            
            if len(pending) != original_count:
                save_pending_optionsets(pending)
                print(f"[DEBUG] Cleaned up {original_count - len(pending)} synced items from pending cache")
        
        return {"pending": pending}
    except Exception as e:
        print(f"Error getting pending option sets: {e}", file=sys.stderr)
        return {"pending": []}

class PendingOptionSetRequest(BaseModel):
    schemaName: str
    displayName: str
    description: str = ""
    category: str
    module: str
    path: str
    options: list[dict]
    deployment: str
    environment: str

@app.post("/api/helpers/option-sets/pending")
async def add_pending_optionset(request: PendingOptionSetRequest):
    """Add a pending option set to cache"""
    try:
        pending = load_pending_optionsets()
        
        # Check if already exists
        for item in pending:
            if item.get("schemaName") == request.schemaName:
                return {"success": False, "error": "Option set already in pending cache"}
        
        # Add new item
        from datetime import datetime
        pending.append({
            "schemaName": request.schemaName,
            "displayName": request.displayName,
            "description": request.description,
            "category": request.category,
            "module": request.module,
            "path": request.path,
            "options": request.options,
            "deployment": request.deployment,
            "environment": request.environment,
            "createdAt": datetime.utcnow().isoformat(),
            "isPending": True
        })
        
        save_pending_optionsets(pending)
        
        return {"success": True, "message": f"Added '{request.displayName}' to pending cache"}
    except Exception as e:
        print(f"Error adding pending option set: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

@app.delete("/api/helpers/option-sets/pending/{schema_name}")
async def delete_pending_optionset(schema_name: str):
    """Remove a specific pending option set from cache"""
    try:
        pending = load_pending_optionsets()
        original_count = len(pending)
        
        pending = [p for p in pending if p.get("schemaName") != schema_name]
        
        if len(pending) == original_count:
            return {"success": False, "error": "Option set not found in pending cache"}
        
        save_pending_optionsets(pending)
        
        return {"success": True, "message": f"Removed '{schema_name}' from pending cache"}
    except Exception as e:
        print(f"Error deleting pending option set: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

@app.delete("/api/helpers/option-sets/pending")
async def clear_pending_optionsets():
    """Clear all pending option sets from cache"""
    try:
        save_pending_optionsets([])
        return {"success": True, "message": "Cleared all pending option sets"}
    except Exception as e:
        print(f"Error clearing pending option sets: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
