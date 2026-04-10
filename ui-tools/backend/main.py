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

# Add shared dataverse-client library to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient

# Add scripts to path for form builder and entity schema reader
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from entity_schema_reader import read_entity_definition, get_entity_name_from_xml, generate_yaml_template
from formxml_parser import FormXmlParser, generate_section_name
import yaml

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

# Track active processes for cancellation
active_processes = {}

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
        # print(f"[DEBUG] Saved {len(pending_list)} pending option sets to cache")
    except Exception as e:
        print(f"Error saving pending option sets: {e}", file=sys.stderr)

def read_solution_display_name(module_path: Path) -> str:
    """Read display name from Solution.xml file"""
    solution_xml_path = module_path / "src" / "Other" / "Solution.xml"
    
    if not solution_xml_path.exists():
        return None
    
    try:
        tree = ET.parse(solution_xml_path)
        root = tree.getroot()
        
        # Find the LocalizedName element with description attribute
        localized_name = root.find(".//LocalizedName[@languagecode='1033']")
        if localized_name is not None:
            display_name = localized_name.get('description')
            if display_name:
                display_name = display_name.strip()
                # Remove "App Base - " prefix if present
                if display_name.startswith("App Base - "):
                    display_name = display_name[11:]  # Remove "App Base - " (11 characters)
                return display_name
        
        return None
    except Exception as e:
        print(f"Error reading display name from {solution_xml_path}: {e}", file=sys.stderr)
        return None

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
            # print(f"Read version {version} -> {normalized} from {solution_xml_path}", file=sys.stderr)
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
    operationId: Optional[str] = None

class SyncRequest(BaseModel):
    deployment: str
    category: str
    module: str
    operationId: Optional[str] = None

class SyncFromRequest(BaseModel):
    deployment: str
    category: str
    module: str
    sourceEnvironment: str
    operationId: Optional[str] = None

class ShipRequest(BaseModel):
    tenant: str
    environment: str
    category: str
    module: str
    managed: bool = True
    upgrade: bool = False
    operationId: Optional[str] = None

class CreateModuleRequest(BaseModel):
    category: str
    moduleName: str
    deployment: str
    sourceEnvironment: str
    targetEnvironments: list[str] = []
    deploy: bool = False
    operationId: Optional[str] = None

class ReleaseRequest(BaseModel):
    category: str
    module: str
    operationId: Optional[str] = None

class UpdateVersionRequest(BaseModel):
    deployment: str
    category: str
    module: str
    version: str
    operationId: Optional[str] = None

class CreateFieldsRequest(BaseModel):
    deployment: str
    environment: str
    tableName: str
    fields: list[dict]

class CancelRequest(BaseModel):
    operationId: str

class FieldTemplateRequest(BaseModel):
    name: str
    description: str = ""
    publisherPrefix: str = ""
    fields: list[dict]

class ReleaseValidationRequest(BaseModel):
    module_path: str

class ReleaseExecutionRequest(BaseModel):
    module_path: str

class BatchCreateFieldsRequest(BaseModel):
    deployment: str
    environment: str
    modulePath: str
    publisherPrefix: str = "appbase_"
    mode: str = "interactive"  # or "auto"
    operationId: str

class SingleTableFieldsRequest(BaseModel):
    deployment: str
    environment: str
    modulePath: str
    tableName: str
    publisherPrefix: str = "appbase_"
    operationId: str

class DetectExistingFieldsRequest(BaseModel):
    deployment: str
    environment: str
    modulePath: str
    publisherPrefix: str = "appbase_"
    module_name: str
    module_display_name: Optional[str] = None
    release_type: str
    new_version: str
    release_notes: str
    enabled_steps: list[str]
    sync_tenant: Optional[str] = None
    sync_environment: Optional[str] = None

class StepExecutionRequest(BaseModel):
    module_path: str
    module_name: str
    module_display_name: Optional[str] = None
    step: str
    version: str
    release_notes: str
    sync_tenant: Optional[str] = None
    sync_environment: Optional[str] = None
    operationId: str

class BuildPackagesRequest(BaseModel):
    module_path: str
    module_name: str
    version: str
    operationId: str

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
                        
                        # Read version and display name from Solution.xml
                        version = read_solution_version(item)
                        display_name = read_solution_display_name(item)
                        
                        # Calculate relative path from project root
                        relative_module_path = str(item.relative_to(PROJECT_ROOT))
                        
                        modules.append({
                            "name": module_name,
                            "displayName": display_name,
                            "category": category,
                            "path": relative_module_path,
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

async def stream_powershell_output(script_path: str, *args, operation_id: str = None):
    """Stream PowerShell script output in real-time using subprocess with threading"""
    import subprocess
    import threading
    from queue import Queue
    
    try:
        # Try pwsh first, fall back to powershell
        powershell_cmd = "pwsh"
        if not shutil.which("pwsh"):
            powershell_cmd = "powershell"
        
        # Build PowerShell command
        cmd = [powershell_cmd, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)] + list(args)
        
        # print(f"[DEBUG] Running command: {' '.join(cmd)}")
        
        # Use synchronous subprocess (Windows-compatible)
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,  # Merge stderr into stdout
            text=True,
            bufsize=1,
            cwd=str(PROJECT_ROOT)
        )
        
        # Track process for cancellation if operation_id provided
        if operation_id:
            active_processes[operation_id] = process
        
        # Use a queue to communicate between threads
        output_queue = Queue()
        
        def read_output():
            """Read output in a separate thread"""
            try:
                for line in process.stdout:
                    output_queue.put(('line', line.rstrip()))
            except Exception as e:
                output_queue.put(('error', str(e)))
            finally:
                output_queue.put(('done', None))
        
        # Start reading thread
        reader_thread = threading.Thread(target=read_output, daemon=True)
        reader_thread.start()
        
        # Stream output from queue
        while True:
            # Check queue with timeout to allow asyncio event loop to run
            try:
                import queue
                msg_type, msg_data = output_queue.get(timeout=0.1)
                
                if msg_type == 'line':
                    if msg_data:
                        yield f"data: {json.dumps({'type': 'output', 'line': msg_data})}\n\n"
                elif msg_type == 'error':
                    yield f"data: {json.dumps({'type': 'error', 'message': msg_data})}\n\n"
                    break
                elif msg_type == 'done':
                    break
                    
                await asyncio.sleep(0)  # Yield control to event loop
            except:
                # Timeout - continue loop to allow event loop to process
                await asyncio.sleep(0.01)
        
        # Wait for process to complete
        process.wait()
        
        # Remove from active processes
        if operation_id and operation_id in active_processes:
            del active_processes[operation_id]
        
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
    
    # print(f"[DEBUG] Deploy args: {args}")  # Debug logging
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
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
            "-Module", request.module,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@app.post("/api/sync-from")
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
            "-Version", request.version,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@app.post("/api/release/build")
async def build_packages(request: BuildPackagesRequest):
    """Build solution packages with streaming output"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Build-Packages-UI.ps1"
    
    return StreamingResponse(
        stream_powershell_output(
            str(script_path),
            "-ModulePath", request.module_path,
            "-ModuleName", request.module_name,
            "-Version", request.version,
            operation_id=request.operationId
        ),
        media_type="text/event-stream"
    )

@app.post("/api/cancel")
async def cancel_operation(request: CancelRequest):
    """Cancel a running operation"""
    operation_id = request.operationId
    
    if operation_id not in active_processes:
        return {"success": False, "message": "Operation not found or already completed"}
    
    try:
        process = active_processes[operation_id]
        
        # Terminate the process (on Windows, this is like SIGTERM)
        process.terminate()
        
        # Wait a bit for graceful termination
        try:
            process.wait(timeout=2)
        except:
            # If it doesn't terminate, kill it
            process.kill()
        
        # Remove from active processes
        del active_processes[operation_id]
        
        return {"success": True, "message": "Operation cancelled"}
    except Exception as e:
        return {"success": False, "message": f"Failed to cancel operation: {str(e)}"}

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
    
    if request.upgrade:
        args.append("-Upgrade")
    
    # print(f"[DEBUG] Ship args: {args}")  # Debug logging
    # print(f"[DEBUG] request.managed: {request.managed}, request.upgrade: {request.upgrade}")
    
    return StreamingResponse(
        stream_powershell_output(*args, operation_id=request.operationId),
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
        stream_powershell_output(*args, operation_id=request.operationId),
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
            "-Module", request.module,
            operation_id=request.operationId
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
            
            # Validate choice fields have existing option sets
            choice_fields = [f for f in request.fields if f.get("type") in ["Choice", "Picklist"]]
            if choice_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating choice fields...\"}}\n\n"
                
                # Get option sets from Dataverse (primary source)
                yield f"data: {{\"type\": \"output\", \"line\": \"  Querying Dataverse for global option sets...\"}}\n\n"
                dataverse_option_sets = client.get_global_optionset_definitions()
                
                # Also scan local workspace option sets
                option_sets_response = await scan_option_sets()
                local_option_sets = option_sets_response.get("optionSets", [])
                
                # Merge: Dataverse option sets + local option sets (deduplicate by schema name)
                all_option_sets = {os["schemaName"]: os for os in dataverse_option_sets}
                for os in local_option_sets:
                    if os["schemaName"] not in all_option_sets:
                        all_option_sets[os["schemaName"]] = os
                
                all_option_sets_list = list(all_option_sets.values())
                yield f"data: {{\"type\": \"output\", \"line\": \"  Found {len(dataverse_option_sets)} option sets in Dataverse, {len(local_option_sets)} local\"}}\n\n"
                
                # Build lookup maps: schema name -> schema name, display name -> schema name
                option_set_by_schema = {os["schemaName"]: os["schemaName"] for os in all_option_sets_list}
                option_set_by_display = {os["displayName"]: os["schemaName"] for os in all_option_sets_list}
                
                # Check each choice field and normalize option set references
                missing_option_sets = []
                for field in choice_fields:
                    option_set_name = field.get("optionSetSchemaName")
                    if not option_set_name:
                        missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - missing optionSetSchemaName")
                    else:
                        # Try to find by schema name first, then by display name
                        if option_set_name in option_set_by_schema:
                            # Already using schema name, no change needed
                            pass
                        elif option_set_name in option_set_by_display:
                            # Convert display name to schema name
                            schema_name = option_set_by_display[option_set_name]
                            field["optionSetSchemaName"] = schema_name
                            yield f"data: {{\"type\": \"output\", \"line\": \"  ℹ Resolved '{option_set_name}' to '{schema_name}'\"}}\n\n"
                        else:
                            # Not found by either name
                            missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - option set '{option_set_name}' not found")
                
                if missing_option_sets:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_option_sets:
                        error_escaped = error.replace('"', '\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced option sets exist (use Choice Creator to create them)\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All choice field option sets found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate lookup fields have existing target tables
            lookup_fields = [f for f in request.fields if f.get("type") in ["Lookup", "Reference"]]
            if lookup_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating lookup fields...\"}}\n\n"
                
                # Get all tables from Dataverse
                all_tables = client.get_entity_definitions()
                
                # Build lookup maps: logical name -> logical name, display name -> logical name
                table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                
                # Check each lookup field and normalize table references
                missing_tables = []
                for field in lookup_fields:
                    target_table = field.get("targetTableLogicalName")
                    if not target_table:
                        missing_tables.append(f"{field.get('schemaName', 'unknown')} - missing targetTableLogicalName")
                    else:
                        # Try to find by logical name first, then by display name
                        if target_table in table_by_logical:
                            # Already using logical name, no change needed
                            pass
                        elif target_table in table_by_display:
                            # Convert display name to logical name
                            logical_name = table_by_display[target_table]
                            field["targetTableLogicalName"] = logical_name
                            yield f"data: {{\"type\": \"output\", \"line\": \"  ℹ Resolved '{target_table}' to '{logical_name}'\"}}\n\n"
                        else:
                            # Not found by either name
                            missing_tables.append(f"{field.get('schemaName', 'unknown')} - target table '{target_table}' not found")
                
                if missing_tables:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_tables:
                        error_escaped = error.replace('"', '\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced tables exist\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All lookup field target tables found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Resolve table name to logical name
            all_tables = client.get_entity_definitions()
            table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
            table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
            
            table_logical_name = request.tableName
            if request.tableName in table_by_display:
                # Convert display name to logical name
                table_logical_name = table_by_display[request.tableName]
            elif request.tableName not in table_by_logical:
                # Table not found
                yield f"data: {{\"type\": \"error\", \"message\": \"Table '{request.tableName}' not found in Dataverse\"}}\n\n"
                return
            
            # Separate Name field renames from regular field creations
            name_field = None
            fields_to_create = []
            
            for field in request.fields:
                if field.get('operation') == 'rename_name_field':
                    if name_field:
                        yield f"data: {{\"type\": \"error\", \"message\": \"Multiple Name fields specified - only one allowed per table\"}}\n\n"
                        return
                    name_field = field
                else:
                    fields_to_create.append(field)
            
            # Calculate total operations
            total_operations = len(fields_to_create) + (1 if name_field else 0)
            
            # Process Name field rename first (if specified)
            name_rename_success = False
            if name_field:
                yield f"data: {{\"type\": \"output\", \"line\": \"Renaming table Name field...\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  New display name: {name_field['displayName']}\"}}\n\n"
                
                result = client.update_name_field_display_name(
                    table_logical_name=table_logical_name,
                    new_display_name=name_field['displayName']
                )
                
                if result.get('success'):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Name field renamed successfully\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    name_rename_success = True
                else:
                    error_msg = result.get('error', 'Unknown error').replace('\"', '\\\\\"')
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Now create regular fields
            if fields_to_create:
                yield f"data: {{\"type\": \"output\", \"line\": \"Creating fields...\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create fields
            success_count = 0
            fail_count = 0
            
            if name_rename_success:
                success_count += 1
            elif name_field and not name_rename_success:
                fail_count += 1
            
            for i, field in enumerate(fields_to_create, 1):
                schema_name = field.get("schemaName")
                display_name = field.get("displayName")
                field_type = field.get("type")
                
                yield f"data: {{\"type\": \"output\", \"line\": \"[{i}/{len(fields_to_create)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  Type: {field_type}\"}}\n\n"
                
                # Create the field using the resolved logical table name
                result = client.create_field(table_logical_name, field)
                
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
            yield f"data: {{\"type\": \"output\", \"line\": \"Total operations: {total_operations}\"}}\n\n"
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

@app.post("/api/helpers/create-single-table-fields")
async def create_single_table_fields(request: SingleTableFieldsRequest):
    """
    Create fields for a single table from BUILD.md Planned section.
    Simplified version of batch endpoint for single table operations.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import parse_build_md_tables, move_fields_to_completed_last_round
    
    async def stream_single_table_creation():
        try:
            # Parse BUILD.md to get the specific table
            module_path = PROJECT_ROOT / request.modulePath
            
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Creating Fields for {request.tableName} ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Module: {request.modulePath}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Deployment: {request.deployment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Environment: {request.environment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Parse BUILD.md
            yield f"data: {{\"type\": \"output\", \"line\": \"Parsing BUILD.md...\"}}\n\n"
            tables = parse_build_md_tables(module_path, request.publisherPrefix)
            
            # Find the specific table
            table = None
            for t in tables:
                if t['tableName'] == request.tableName:
                    table = t
                    break
            
            if not table:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Error: Table '{request.tableName}' not found in BUILD.md\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                return
            
            field_count = len(table['fields'])
            
            if field_count == 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"⊘ No planned fields found for this table\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 0}}\n\n"
                return
            
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Found {field_count} fields to create\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Parse fields from BUILD.md format to Field Creator format
            parsed_fields = []
            for field_line in table['fields']:
                try:
                    parsed_field = _parse_field_from_buildmd_format(field_line, request.publisherPrefix)
                    if parsed_field:
                        parsed_fields.append(parsed_field)
                except Exception as e:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ⚠ Warning: Could not parse field: {field_line} - {str(e)}\"}}\n\n"
            
            if not parsed_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ No valid fields to create\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                return
            
            # Call existing create-fields endpoint logic
            create_request = CreateFieldsRequest(
                deployment=request.deployment,
                environment=request.environment,
                tableName=request.tableName,
                fields=parsed_fields
            )
            
            # Stream output from create_fields - call the generator directly
            success_count = 0
            fail_count = 0
            successfully_created_fields = []
            
            # Inline field creation (same logic as create_fields endpoint)
            # Get deployment client config
            config_path = PROJECT_ROOT / ".config" / "deployments.json"
            with open(config_path) as f:
                config_data = json.load(f)
            
            deployment_config = config_data["Deployments"][request.deployment]
            auth_config = deployment_config["Auth"]
            
            environment_url = auth_config["EnvironmentUrls"][request.environment]
            tenant_id = auth_config["TenantId"]
            client_id = auth_config["ClientId"]
            client_secret = auth_config["ClientSecret"]
            
            # Create Dataverse client
            yield f"data: {{\"type\": \"output\", \"line\": \"Connecting to Dataverse...\"}}\n\n"
            client = DataverseClient(
                environment_url=environment_url,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            client.authenticate()
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Connected successfully\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate choice fields have existing option sets
            choice_fields = [f for f in parsed_fields if f.get("type") in ["Choice", "Picklist"]]
            if choice_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating choice fields...\"}}\n\n"
                dataverse_option_sets = client.get_global_optionset_definitions()
                option_sets_response = await scan_option_sets()
                local_option_sets = option_sets_response.get("optionSets", [])
                all_option_sets = {os["schemaName"]: os for os in dataverse_option_sets}
                for os in local_option_sets:
                    if os["schemaName"] not in all_option_sets:
                        all_option_sets[os["schemaName"]] = os
                all_option_sets_list = list(all_option_sets.values())
                option_set_by_schema = {os["schemaName"]: os["schemaName"] for os in all_option_sets_list}
                option_set_by_display = {os["displayName"]: os["schemaName"] for os in all_option_sets_list}
                missing_option_sets = []
                for field in choice_fields:
                    option_set_name = field.get("optionSetSchemaName")
                    if not option_set_name:
                        missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - missing optionSetSchemaName")
                    elif option_set_name in option_set_by_schema:
                        pass
                    elif option_set_name in option_set_by_display:
                        field["optionSetSchemaName"] = option_set_by_display[option_set_name]
                    else:
                        missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - option set '{option_set_name}' not found")
                if missing_option_sets:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_option_sets:
                        error_escaped = error.replace('"', '\\\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced option sets exist (use Choice Creator to create them)\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All choice field option sets found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Validate lookup fields have existing target tables
            lookup_fields = [f for f in parsed_fields if f.get("type") in ["Lookup", "Reference"]]
            if lookup_fields:
                yield f"data: {{\"type\": \"output\", \"line\": \"Validating lookup fields...\"}}\n\n"
                all_tables = client.get_entity_definitions()
                table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                missing_tables = []
                for field in lookup_fields:
                    target_table = field.get("targetTableLogicalName")
                    if not target_table:
                        missing_tables.append(f"{field.get('schemaName', 'unknown')} - missing targetTableLogicalName")
                    elif target_table in table_by_logical:
                        pass
                    elif target_table in table_by_display:
                        field["targetTableLogicalName"] = table_by_display[target_table]
                    else:
                        missing_tables.append(f"{field.get('schemaName', 'unknown')} - target table '{target_table}' not found")
                if missing_tables:
                    yield f"data: {{\"type\": \"output\", \"line\": \"✗ Validation failed:\"}}\n\n"
                    for error in missing_tables:
                        error_escaped = error.replace('"', '\\\\"')
                        yield f"data: {{\"type\": \"output\", \"line\": \"  - {error_escaped}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"Please ensure all referenced tables exist\"}}\n\n"
                    yield f"data: {{\"type\": \"complete\", \"exitCode\": 1}}\n\n"
                    return
                yield f"data: {{\"type\": \"output\", \"line\": \"✓ All lookup field target tables found\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Resolve table name to logical name
            all_tables = client.get_entity_definitions()
            table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
            table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
            table_logical_name = request.tableName
            if request.tableName in table_by_display:
                table_logical_name = table_by_display[request.tableName]
            elif request.tableName not in table_by_logical:
                yield f"data: {{\"type\": \"error\", \"message\": \"Table '{request.tableName}' not found in Dataverse\"}}\n\n"
                return
            
            # Separate Name field renames from regular field creations
            name_field = None
            fields_to_create = []
            for field in parsed_fields:
                if field.get('operation') == 'rename_name_field':
                    name_field = field
                else:
                    fields_to_create.append(field)
            
            # Process Name field rename first (if specified)
            if name_field:
                yield f"data: {{\"type\": \"output\", \"line\": \"Renaming table Name field...\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  New display name: {name_field['displayName']}\"}}\n\n"
                result = client.update_name_field_display_name(
                    table_logical_name=table_logical_name,
                    new_display_name=name_field['displayName']
                )
                if result.get('success'):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Name field renamed successfully\"}}\n\n"
                    successfully_created_fields.append(name_field['displayName'])
                else:
                    error_msg = result.get('error', 'Unknown error')
                    # Properly escape for JSON: backslashes first, then quotes, remove newlines
                    error_msg = error_msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Create fields
            for i, field in enumerate(fields_to_create, 1):
                schema_name = field.get("schemaName")
                display_name = field.get("displayName")
                field_type = field.get("type")
                
                yield f"data: {{\"type\": \"output\", \"line\": \"[{i}/{len(fields_to_create)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"  Type: {field_type}\"}}\n\n"
                
                # Create the field using resolved table logical name
                result = client.create_field(table_logical_name, field)
                
                if result.get("success"):
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Created field: {display_name} ({schema_name})\"}}\n\n"
                    success_count += 1
                    successfully_created_fields.append(display_name)
                else:
                    error_msg = result.get("error", "Unknown error")
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Failed: {error_msg}\"}}\n\n"
                    fail_count += 1
                
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Update BUILD.md file: move successfully created fields to Completed Last Round
            if successfully_created_fields:
                try:
                    moved = move_fields_to_completed_last_round(
                        module_path,
                        request.tableName,
                        successfully_created_fields
                    )
                    if moved:
                        yield f"data: {{\"type\": \"output\", \"line\": \"✓ Updated BUILD.md: Moved {len(successfully_created_fields)} fields to Completed Last Round\"}}\n\n"
                    else:
                        yield f"data: {{\"type\": \"output\", \"line\": \"⚠ Warning: Could not update BUILD.md\"}}\n\n"
                except Exception as e:
                    yield f"data: {{\"type\": \"output\", \"line\": \"⚠ Warning: Could not update BUILD.md: {str(e)}\"}}\n\n"
            
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Complete ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Successfully created: {success_count} fields\"}}\n\n"
            if fail_count > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Failed: {fail_count} fields\"}}\n\n"
            
            exit_code = 0 if fail_count == 0 else 1
            yield f"data: {{\"type\": \"complete\", \"exitCode\": {exit_code}}}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
            traceback.print_exc()
    
    return StreamingResponse(
        stream_single_table_creation(),
        media_type="text/event-stream"
    )

@app.post("/api/helpers/batch-create-fields-from-buildmd")
async def batch_create_fields_from_buildmd(request: BatchCreateFieldsRequest):
    """
    Batch create fields from BUILD.md file with interactive table-by-table control.
    Parses BUILD.md, extracts Planned sections, calls existing create-fields endpoint for each table.
    """
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import parse_build_md_tables
    
    async def stream_batch_creation():
        try:
            # Parse BUILD.md to get tables
            module_path = PROJECT_ROOT / request.modulePath
            
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Batch Field Creation from BUILD.md ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Module: {request.modulePath}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Deployment: {request.deployment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Environment: {request.environment}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Parse BUILD.md
            yield f"data: {{\"type\": \"output\", \"line\": \"Parsing BUILD.md...\"}}\n\n"
            tables = parse_build_md_tables(module_path, request.publisherPrefix)
            
            if not tables:
                yield f"data: {{\"type\": \"output\", \"line\": \"⚠ No tables with Planned fields found in BUILD.md\"}}\n\n"
                yield f"data: {{\"type\": \"complete\", \"exitCode\": 0}}\n\n"
                return
            
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Found {len(tables)} tables with Planned fields\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Track stats
            total_tables = len(tables)
            tables_completed = 0
            tables_failed = 0
            tables_skipped = 0
            total_fields_created = 0
            
            # Process each table
            for table_index, table in enumerate(tables, 1):
                table_name = table['tableName']
                field_count = len(table['fields'])
                
                yield f"data: {{\"type\": \"output\", \"line\": \"═══════════════════════════════════════\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"Table {table_index}/{total_tables}: {table_name}\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"{field_count} fields to process\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Interactive mode: pause for user input
                if request.mode == "interactive":
                    yield f"data: {{\"type\": \"prompt\", \"table\": \"{table_name.replace(chr(34), chr(92)+chr(34))}\", \"index\": {table_index}, \"total\": {total_tables}}}\n\n"
                    # Frontend will send continue signal via separate mechanism (not implemented yet - for now just proceed)
                
                # Parse fields from BUILD.md format to Field Creator format
                parsed_fields = []
                for field_line in table['fields']:
                    try:
                        parsed_field = _parse_field_from_buildmd_format(field_line, request.publisherPrefix)
                        if parsed_field:
                            parsed_fields.append(parsed_field)
                    except Exception as e:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ⚠ Warning: Could not parse field: {field_line} - {str(e)}\"}}\n\n"
                
                if not parsed_fields:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ⊘ No valid fields to create, skipping table\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    tables_skipped += 1
                    continue
                
                # Call existing create-fields endpoint logic
                create_request = CreateFieldsRequest(
                    deployment=request.deployment,
                    environment=request.environment,
                    tableName=table_name,
                    fields=parsed_fields
                )
                
                # Create fields for this table
                table_success_count = 0
                table_fail_count = 0
                successfully_created_fields = []
                
                # Get deployment client config (reuse from top-level scope if possible, or fetch here)
                config_path = PROJECT_ROOT / ".config" / "deployments.json"
                with open(config_path) as f:
                    config_data = json.load(f)
                
                deployment_config = config_data["Deployments"][request.deployment]
                auth_config = deployment_config["Auth"]
                
                environment_url = auth_config["EnvironmentUrls"][request.environment]
                tenant_id = auth_config["TenantId"]
                client_id = auth_config["ClientId"]
                client_secret = auth_config["ClientSecret"]
                
                # Create Dataverse client
                yield f"data: {{\"type\": \"output\", \"line\": \"  Connecting to Dataverse...\"}}\n\n"
                client = DataverseClient(
                    environment_url=environment_url,
                    tenant_id=tenant_id,
                    client_id=client_id,
                    client_secret=client_secret
                )
                client.authenticate()
                yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Connected successfully\"}}\n\n"
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Validate choice fields have existing option sets
                choice_fields = [f for f in parsed_fields if f.get("type") in ["Choice", "Picklist"]]
                if choice_fields:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Validating choice fields...\"}}\n\n"
                    dataverse_option_sets = client.get_global_optionset_definitions()
                    option_sets_response = await scan_option_sets()
                    local_option_sets = option_sets_response.get("optionSets", [])
                    all_option_sets = {os["schemaName"]: os for os in dataverse_option_sets}
                    for os in local_option_sets:
                        if os["schemaName"] not in all_option_sets:
                            all_option_sets[os["schemaName"]] = os
                    all_option_sets_list = list(all_option_sets.values())
                    option_set_by_schema = {os["schemaName"]: os["schemaName"] for os in all_option_sets_list}
                    option_set_by_display = {os["displayName"]: os["schemaName"] for os in all_option_sets_list}
                    missing_option_sets = []
                    for field in choice_fields:
                        option_set_name = field.get("optionSetSchemaName")
                        if not option_set_name:
                            missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - missing optionSetSchemaName")
                        elif option_set_name in option_set_by_schema:
                            pass
                        elif option_set_name in option_set_by_display:
                            field["optionSetSchemaName"] = option_set_by_display[option_set_name]
                        else:
                            missing_option_sets.append(f"{field.get('schemaName', 'unknown')} - option set '{option_set_name}' not found")
                    if missing_option_sets:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Validation failed:\"}}\n\n"
                        for error in missing_option_sets:
                            error_escaped = error.replace('"', '\\\\"')
                            yield f"data: {{\"type\": \"output\", \"line\": \"    - {error_escaped}\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"  Skipping table (please create missing option sets first)\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                        tables_failed += 1
                        continue
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ All choice field option sets found\"}}\n\n"
                
                # Validate lookup fields have existing target tables
                lookup_fields = [f for f in parsed_fields if f.get("type") in ["Lookup", "Reference"]]
                if lookup_fields:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Validating lookup fields...\"}}\n\n"
                    all_tables = client.get_entity_definitions()
                    table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                    table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                    missing_tables = []
                    for field in lookup_fields:
                        target_table = field.get("targetTableLogicalName")
                        if not target_table:
                            missing_tables.append(f"{field.get('schemaName', 'unknown')} - missing targetTableLogicalName")
                        elif target_table in table_by_logical:
                            pass
                        elif target_table in table_by_display:
                            field["targetTableLogicalName"] = table_by_display[target_table]
                        else:
                            missing_tables.append(f"{field.get('schemaName', 'unknown')} - target table '{target_table}' not found")
                    if missing_tables:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Validation failed:\"}}\n\n"
                        for error in missing_tables:
                            error_escaped = error.replace('"', '\\\\"')
                            yield f"data: {{\"type\": \"output\", \"line\": \"    - {error_escaped}\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"  Skipping table (please create missing target tables first)\"}}\n\n"
                        yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                        tables_failed += 1
                        continue
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ All lookup field target tables found\"}}\n\n"
                
                # Resolve table name to logical name
                all_tables = client.get_entity_definitions()
                table_by_logical = {t["logicalName"]: t["logicalName"] for t in all_tables}
                table_by_display = {t["displayName"]: t["logicalName"] for t in all_tables}
                table_logical_name = table_name
                if table_name in table_by_display:
                    table_logical_name = table_by_display[table_name]
                elif table_name not in table_by_logical:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  ✗ Error: Table '{table_name}' not found in Dataverse\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Skipping table\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                    tables_failed += 1
                    continue
                
                # Separate Name field renames from regular field creations
                name_field = None
                fields_to_create = []
                for field in parsed_fields:
                    if field.get('operation') == 'rename_name_field':
                        name_field = field
                    else:
                        fields_to_create.append(field)
                
                # Process Name field rename first (if specified)
                if name_field:
                    yield f"data: {{\"type\": \"output\", \"line\": \"  Renaming table Name field...\"}}\n\n"
                    result = client.update_name_field_display_name(
                        table_logical_name=table_logical_name,
                        new_display_name=name_field['displayName']
                    )
                    if result.get('success'):
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✓ Name field renamed to '{name_field['displayName']}'\"}}\n\n"
                        successfully_created_fields.append(name_field['displayName'])
                    else:
                        error_msg = result.get('error', 'Unknown error')
                        # Properly escape for JSON: backslashes first, then quotes, remove newlines
                        error_msg = error_msg.replace('\\', '\\\\').replace('"', '\\"').replace('\n', ' ').replace('\r', '')
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✗ Failed: {error_msg}\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Create fields
                for i, field in enumerate(fields_to_create, 1):
                    schema_name = field.get("schemaName")
                    display_name = field.get("displayName")
                    field_type = field.get("type")
                    
                    yield f"data: {{\"type\": \"output\", \"line\": \"  [{i}/{len(fields_to_create)}] Creating: {schema_name} ({display_name})\"}}\n\n"
                    yield f"data: {{\"type\": \"output\", \"line\": \"    Type: {field_type}\"}}\n\n"
                    
                    # Create the field using resolved table logical name
                    result = client.create_field(table_logical_name, field)
                    
                    if result.get("success"):
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✓ Created field: {display_name} ({schema_name})\"}}\n\n"
                        table_success_count += 1
                        successfully_created_fields.append(display_name)
                    else:
                        error_msg = result.get("error", "Unknown error")
                        yield f"data: {{\"type\": \"output\", \"line\": \"    ✗ Failed: {error_msg}\"}}\n\n"
                        table_fail_count += 1
                    
                    yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
                
                # Update BUILD.md file: move successfully created fields to Completed Last Round
                if successfully_created_fields:
                    try:
                        from build_md_parser import move_fields_to_completed_last_round
                        module_full_path = PROJECT_ROOT / request.modulePath
                        moved = move_fields_to_completed_last_round(
                            module_full_path,
                            table_name,
                            successfully_created_fields
                        )
                        if moved:
                            yield f"data: {{\"type\": \"output\", \"line\": \"  ✓ Updated BUILD.md: Moved {len(successfully_created_fields)} fields to Completed Last Round\"}}\n\n"
                    except Exception as e:
                        yield f"data: {{\"type\": \"output\", \"line\": \"  ⚠ Warning: Could not update BUILD.md: {str(e)}\"}}\n\n"
                
                # Update stats
                total_fields_created += table_success_count
                if table_fail_count > 0:
                    tables_failed += 1
                else:
                    tables_completed += 1
                
                yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            # Final summary
            yield f"data: {{\"type\": \"output\", \"line\": \"═══════════════════════════════════════\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"=== Batch Creation Complete ===\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Tables processed: {total_tables}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"✓ Completed: {tables_completed}\"}}\n\n"
            if tables_failed > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"✗ Failed: {tables_failed}\"}}\n\n"
            if tables_skipped > 0:
                yield f"data: {{\"type\": \"output\", \"line\": \"⊘ Skipped: {tables_skipped}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"Total fields created: {total_fields_created}\"}}\n\n"
            yield f"data: {{\"type\": \"output\", \"line\": \"\"}}\n\n"
            
            exit_code = 0 if tables_failed == 0 else 1
            yield f"data: {{\"type\": \"complete\", \"exitCode\": {exit_code}}}\n\n"
            
        except Exception as e:
            import traceback
            error_msg = str(e).replace('"', '\\"').replace('\n', ' ')
            yield f"data: {{\"type\": \"error\", \"message\": \"{error_msg}\"}}\n\n"
            traceback.print_exc()
    
    return StreamingResponse(
        stream_batch_creation(),
        media_type="text/event-stream"
    )

def _parse_field_from_buildmd_format(field_line: str, publisher_prefix: str) -> dict:
    """
    Parse a BUILD.md format field line into Field Creator format.
    
    Args:
        field_line: e.g., "Period Code: Text" or "Person: Lookup (Person)"
        publisher_prefix: e.g., "appbase_"
    
    Returns:
        Field definition dict for create_field endpoint
    """
    # Split on first colon
    if ': ' not in field_line:
        return None
    
    display_name, type_info = field_line.split(': ', 1)
    display_name = display_name.strip()
    type_info = type_info.strip()
    
    # Generate schema name
    from build_md_parser import generate_schema_name
    schema_name = generate_schema_name(display_name, publisher_prefix)
    
    # Parse type and parameters
    field_type = type_info
    option_set = None
    target_table = None
    
    # Handle Choice (OptionSet) and Lookup (Table) formats
    if '(' in type_info and ')' in type_info:
        paren_start = type_info.index('(')
        paren_end = type_info.rindex(')')
        field_type = type_info[:paren_start].strip()
        param = type_info[paren_start+1:paren_end].strip()
        
        if field_type == 'Choice':
            option_set = param
        elif field_type == 'Lookup':
            target_table = param
    
    # Normalize type names
    if field_type in ['Yes / No', 'Yes/No']:
        field_type = 'YesNo'
    
    # Build field definition
    # Special handling for Name field - it's a rename operation, not a field creation
    if field_type == 'Name':
        field_def = {
            'displayName': display_name,
            'operation': 'rename_name_field'
        }
    else:
        field_def = {
            'schemaName': schema_name,
            'displayName': display_name,
            'type': field_type,
            'required': False
        }
        
        if option_set:
            field_def['optionSetSchemaName'] = option_set
        if target_table:
            field_def['targetTableLogicalName'] = target_table
    
    return field_def

@app.get("/api/helpers/scan-modules")
async def scan_modules():
    """Scan workspace for modules with BUILD.md files"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import get_available_modules
    
    try:
        modules = get_available_modules(PROJECT_ROOT)
        return {"modules": modules}
    except Exception as e:
        return {"error": str(e), "modules": []}

@app.get("/api/helpers/preview-tables")
async def preview_tables(module_path: str, publisher_prefix: str = "appbase_"):
    """Preview tables and fields from a BUILD.md file without creating them"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import parse_build_md_tables
    
    try:
        # Parse BUILD.md with all sections for detailed preview
        full_path = PROJECT_ROOT / module_path
        tables = parse_build_md_tables(full_path, publisher_prefix, include_all_sections=True)
        
        # Format response with counts
        preview = {
            "tableCount": len(tables),
            "tables": [
                {
                    "tableName": table["tableName"],
                    "fieldCount": len(table["fields"]),
                    "fields": table["fields"],  # Planned fields only (for backward compatibility)
                    "sections": table.get("sections", {
                        "completed": [],
                        "completedLastRound": [],
                        "planned": table["fields"]
                    })
                }
                for table in tables
            ]
        }
        
        return preview
    except Exception as e:
        return {"error": str(e), "tableCount": 0, "tables": []}

@app.post("/api/helpers/update-build-md")
async def update_build_md(
    module_path: str,
    table_name: str,
    field_names: List[str]
):
    """Move successfully created fields from Planned to Completed Last Round in BUILD.md"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from build_md_parser import move_fields_to_completed_last_round
    
    try:
        full_path = PROJECT_ROOT / module_path
        success = move_fields_to_completed_last_round(full_path, table_name, field_names)
        
        if success:
            return {"success": True, "message": f"Moved {len(field_names)} fields to Completed Last Round"}
        else:
            return {"success": False, "error": "Failed to update BUILD.md"}
    except Exception as e:
        return {"success": False, "error": str(e)}

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
    
    # print(f"[DEBUG] Starting option sets scan in {PROJECT_ROOT}")
    
    for category_dir in PROJECT_ROOT.iterdir():
        if not category_dir.is_dir() or category_dir.name in exclude_folders:
            continue
        
        for module_dir in category_dir.iterdir():
            if not module_dir.is_dir():
                continue
            
            option_sets_dir = module_dir / "src" / "OptionSets"
            if option_sets_dir.exists():
                # print(f"[DEBUG] Found OptionSets dir: {option_sets_dir}")
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
                        # print(f"[DEBUG] Parsed option set: {display_name} ({schema_name}) with {len(options)} options")
                        
                    except Exception as e:
                        print(f"Error parsing option set XML {optionset_xml}: {e}", file=sys.stderr)
    
    # print(f"[DEBUG] Scan complete. Found {len(option_sets)} option sets")
    return {"optionSets": sorted(option_sets, key=lambda o: (o.get("category", ""), o.get("module", ""), o.get("displayName", "")))}

class TableScanRequest(BaseModel):
    deployment: str
    environment: str

@app.post("/api/helpers/tables/scan")
async def scan_tables(request: TableScanRequest):
    """Scan all tables from Dataverse environment"""
    try:
        # Load deployment configuration
        config_path = PROJECT_ROOT / ".config" / "deployments.json"
        if not config_path.exists():
            return {"error": f"Configuration not found at {config_path}", "tables": []}
        
        with open(config_path) as f:
            config = json.load(f)
        
        # Get the deployment configuration
        if request.deployment not in config.get("Deployments", {}):
            return {"error": f"Deployment '{request.deployment}' not found", "tables": []}
        
        deployment_config = config["Deployments"][request.deployment]
        
        # Get authentication configuration
        if "Auth" not in deployment_config:
            return {"error": "Auth configuration missing", "tables": []}
        
        auth_config = deployment_config["Auth"]
        tenant_id = auth_config.get("TenantId")
        client_id = auth_config.get("ClientId")
        client_secret = auth_config.get("ClientSecret")
        
        if not all([tenant_id, client_id, client_secret]):
            return {"error": "Incomplete auth configuration", "tables": []}
        
        # Get environment URL
        environment_url = auth_config.get("EnvironmentUrls", {}).get(request.environment)
        if not environment_url:
            return {"error": f"Environment URL not configured for '{request.environment}'", "tables": []}
        
        # Create Dataverse client and get entity definitions
        # print(f"[DEBUG] Scanning tables from {environment_url}")
        client = DataverseClient(
            environment_url=environment_url,
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        
        client.authenticate()
        tables = client.get_entity_definitions()
        
        # print(f"[DEBUG] Scan complete. Found {len(tables)} tables")
        return {"tables": sorted(tables, key=lambda t: t.get("displayName", ""))}
        
    except Exception as e:
        print(f"Error scanning tables: {e}", file=sys.stderr)
        return {"error": str(e), "tables": []}

class OptionSetSearchRequest(BaseModel):
    displayName: Optional[str] = None
    optionLabels: Optional[list[str]] = None

@app.post("/api/helpers/option-sets/search")
async def search_option_sets(request: OptionSetSearchRequest):
    """Search for similar option sets based on name or option values"""
    # print(f"[DEBUG] Search request: displayName={request.displayName}, optionLabels={request.optionLabels}")
    
    # First, get all option sets
    all_option_sets_response = await scan_option_sets()
    all_option_sets = all_option_sets_response["optionSets"]
    
    # print(f"[DEBUG] Searching through {len(all_option_sets)} option sets")
    
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
            # Word match (exclude common noise words)
            else:
                noise_words = {"status", "type", "category"}
                search_words = [w for w in search_name.split() if w not in noise_words and len(w) > 2]
                if search_words and any(word in display_name or word in schema_name for word in search_words):
                    match_score += 25
                    match_reasons.append("Word match")
        
        # Option label matching
        if request.optionLabels and len(request.optionLabels) > 0:
            # Exclude common noise values that don't indicate real similarity
            noise_values = {"active", "inactive", "completed"}
            
            existing_labels = [opt["label"].lower() for opt in option_set.get("options", []) if opt["label"].lower() not in noise_values]
            search_terms = [label.lower() for label in request.optionLabels if label.lower() not in noise_values]
            
            # print(f"[DEBUG] Matching option set '{option_set.get('displayName')}' - search terms: {search_terms}, existing labels: {existing_labels}")
            
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
                        # print(f"[DEBUG]   Exact match: '{search_term}' == '{existing_label}'")
                        break
                    # Partial match (search term appears in label, e.g., "Progress" matches "In Progress")
                    elif search_term in existing_label or existing_label in search_term:
                        matched_count += 1
                        matched_labels.append(existing_label)
                        # print(f"[DEBUG]   Partial match: '{search_term}' <-> '{existing_label}'")
                        break
            
            # print(f"[DEBUG]   Matched {matched_count}/{len(search_terms)} terms")
            
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
    
    # print(f"[DEBUG] Search complete. Found {len(matches)} matches")
    
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
        # print(f"[DEBUG] Creating global option set '{request.schemaName}' in Dataverse")
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
                # print(f"[DEBUG] Cleaned up {original_count - len(pending)} synced items from pending cache")
        
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

# ============================================================================
# Release Manager Endpoints
# ============================================================================

@app.get("/api/release/get-version")
async def get_module_version(module_path: str):
    """Get current version from a module's Solution.xml"""
    try:
        full_path = PROJECT_ROOT / module_path
        version = read_solution_version(full_path)
        return {"success": True, "version": version}
    except Exception as e:
        print(f"Error getting version: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "version": "Unknown"}

@app.post("/api/release/validate")
async def validate_release(request: ReleaseValidationRequest):
    """Validate pre-flight checks for release"""
    errors = []
    warnings = []
    
    try:
        # Check for uncommitted changes
        git_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if git_status.returncode == 0 and git_status.stdout.strip():
            errors.append("Repository has uncommitted changes. Please commit or stash changes before creating a release.")
        
        # Check for CHANGELOG.md with Unreleased section
        changelog_path = PROJECT_ROOT / request.module_path / "CHANGELOG.md"
        if not changelog_path.exists():
            errors.append(f"CHANGELOG.md not found at {changelog_path}")
        else:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if "## Unreleased" not in content:
                    errors.append("CHANGELOG.md does not contain an '## Unreleased' section")
                else:
                    # Check if Unreleased section has content
                    import re
                    unreleased_section = re.search(r'## Unreleased\s*(.*?)(?=\n##|\Z)', content, re.DOTALL)
                    if unreleased_section:
                        section_content = unreleased_section.group(1).strip()
                        if not section_content or len(section_content) < 10:
                            warnings.append("Unreleased section appears to be empty")
        
        return {
            "success": True,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    except Exception as e:
        print(f"Error validating release: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "valid": False,
            "errors": [f"Validation failed: {str(e)}"],
            "warnings": []
        }

@app.get("/api/release/get-changelog")
async def get_changelog(module_path: str):
    """Get the full CHANGELOG.md content"""
    try:
        changelog_path = PROJECT_ROOT / module_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            return {"success": False, "error": "CHANGELOG.md not found", "content": ""}
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return {"success": True, "content": content}
    except Exception as e:
        print(f"Error reading changelog: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "content": ""}

@app.post("/api/release/preview-changelog")
async def preview_changelog(request: dict):
    """Preview the changelog transformation (before/after)"""
    try:
        from datetime import datetime
        import re
        
        module_path = request.get("module_path")
        new_version = request.get("new_version")
        
        changelog_path = PROJECT_ROOT / module_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            return {"success": False, "error": "CHANGELOG.md not found"}
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Check if there's an Unreleased section
        if '## Unreleased' not in original_content:
            return {
                "success": False, 
                "error": "CHANGELOG.md does not contain an '## Unreleased' section. Please add one before creating a release."
            }
        
        # Transform the changelog
        current_date = datetime.now().strftime("%Y-%m-%d")
        transformed_content = re.sub(
            r'## Unreleased',
            f'## [{new_version}] - {current_date}',
            original_content,
            count=1
        )
        
        return {
            "success": True,
            "before": original_content,
            "after": transformed_content
        }
    except Exception as e:
        print(f"Error previewing changelog: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

@app.get("/api/release/extract-changelog")
async def extract_changelog(module_path: str, version: str = None):
    """Extract release notes from CHANGELOG.md - either Unreleased or specific version"""
    try:
        changelog_path = PROJECT_ROOT / module_path / "CHANGELOG.md"
        
        if not changelog_path.exists():
            return {"success": False, "error": "CHANGELOG.md not found", "content": ""}
        
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        import re
        
        if version:
            # Try versioned section first, fall back to Unreleased if not found
            # Extract from versioned section like ## [1.0.0.0] - 2026-02-26
            escaped_version = version.replace('.', r'\.')
            # Match the version header, then capture everything until the next ## header (not ###)
            version_section = re.search(rf'## \[{escaped_version}\][^\n]*\n+(.*?)(?=\n## (?:\[|\w)|\Z)', content, re.DOTALL)
            
            if version_section:
                section_content = version_section.group(1).strip()
                return {"success": True, "content": section_content, "source": "versioned"}
            
            # Fall back to Unreleased if version section not found
            unreleased_section = re.search(r'## Unreleased\s+(.*?)(?=\n## (?:\[|\w)|\Z)', content, re.DOTALL)
            
            if unreleased_section:
                section_content = unreleased_section.group(1).strip()
                return {"success": True, "content": section_content, "source": "unreleased"}
            else:
                return {"success": True, "content": "", "source": "none"}
        else:
            # Extract Unreleased section
            unreleased_section = re.search(r'## Unreleased\s+(.*?)(?=\n## (?:\[|\w)|\Z)', content, re.DOTALL)
            
            if unreleased_section:
                section_content = unreleased_section.group(1).strip()
                return {"success": True, "content": section_content, "source": "unreleased"}
            else:
                return {"success": True, "content": "", "source": "none"}
    except Exception as e:
        print(f"Error extracting changelog: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "content": ""}

@app.get("/api/release/check-packages")
async def check_packages(module_path: str):
    """Check for built solution packages in .releases folder and return their metadata"""
    try:
        from datetime import datetime
        import os
        
        # Extract module name from path (e.g., "shared/core" -> "core")
        module_name = Path(module_path).name
        
        # Check .releases/<module> folder instead of bin/Release
        releases_path = PROJECT_ROOT / ".releases" / module_name
        
        if not releases_path.exists():
            return {"success": True, "packages": [], "message": "No .releases folder found yet"}
        
        # Find .zip files in the .releases/<module> folder
        packages = []
        for file_path in releases_path.glob("*.zip"):
            stat_info = file_path.stat()
            modified_dt = datetime.fromtimestamp(stat_info.st_mtime)
            created_dt = datetime.fromtimestamp(stat_info.st_ctime)
            
            # Format: "Thu Feb-26, 2026 2:30 PM"
            modified_formatted = modified_dt.strftime("%a %b-") + str(modified_dt.day) + modified_dt.strftime(", %Y %I:%M %p")
            created_formatted = created_dt.strftime("%a %b-") + str(created_dt.day) + created_dt.strftime(", %Y %I:%M %p")
            
            packages.append({
                "name": file_path.name,
                "size": stat_info.st_size,
                "size_mb": round(stat_info.st_size / (1024 * 1024), 2),
                "created": created_formatted,
                "modified": modified_formatted,
                "modified_timestamp": stat_info.st_mtime
            })
        
        # Sort by modification time (newest first)
        packages.sort(key=lambda x: x["modified_timestamp"], reverse=True)
        
        return {
            "success": True,
            "packages": packages,
            "count": len(packages),
            "folder": str(releases_path.relative_to(PROJECT_ROOT))
        }
    except Exception as e:
        print(f"Error checking packages: {e}", file=sys.stderr)
        return {"success": False, "error": str(e), "packages": []}

@app.post("/api/release/execute")
async def execute_release(request: ReleaseExecutionRequest):
    """Execute the full release workflow"""
    try:
        from datetime import datetime
        
        # Build the script path
        script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Full-Release-UI.ps1"
        
        if not script_path.exists():
            return {
                "success": False,
                "error": f"Release script not found: {script_path}",
                "steps": []
            }
        
        # Build PowerShell command
        ps_command = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script_path),
            "-ModulePath", request.module_path,
            "-ModuleName", request.module_name,
            "-ReleaseType", request.release_type,
            "-NewVersion", request.new_version,
            "-ReleaseNotes", request.release_notes,
            "-EnabledSteps", ",".join(request.enabled_steps)
        ]
        
        # Add optional display name if provided
        if request.module_display_name:
            ps_command.extend(["-ModuleFriendlyName", request.module_display_name])
        
        print(f"Executing release command: {' '.join(ps_command)}", file=sys.stderr)
        
        # Execute the PowerShell script
        result = subprocess.run(
            ps_command,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"PowerShell stdout: {result.stdout}", file=sys.stderr)
        print(f"PowerShell stderr: {result.stderr}", file=sys.stderr)
        print(f"PowerShell return code: {result.returncode}", file=sys.stderr)
        
        # Try to parse JSON output from the script
        try:
            output_data = json.loads(result.stdout)
            return output_data
        except json.JSONDecodeError:
            # If not JSON, return a structured error
            if result.returncode == 0:
                return {
                    "success": True,
                    "steps": [{
                        "label": "Release execution",
                        "status": "success",
                        "message": result.stdout
                    }],
                    "github_release_url": ""
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or result.stdout or "Unknown error",
                    "steps": [{
                        "label": "Release execution",
                        "status": "error",
                        "message": result.stderr or "Failed to execute release"
                    }]
                }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Release execution timed out after 5 minutes",
            "steps": []
        }
    except Exception as e:
        print(f"Error executing release: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e),
            "steps": []
        }

@app.post("/api/release/execute-step")
async def execute_single_step(request: StepExecutionRequest):
    """Execute a single release step with streaming output"""
    script_path = PROJECT_ROOT / "ui-tools" / "scripts" / "Full-Release-UI.ps1"
    
    # Build args list for stream_powershell_output
    args = [
        "-ModulePath", request.module_path,
        "-ModuleName", request.module_name,
        "-ReleaseType", "standard",  # Doesn't matter for single steps
        "-NewVersion", request.version,
        "-ReleaseNotes", request.release_notes,
        "-EnabledSteps", request.step  # Only this step
    ]
    
    # Add optional display name if provided
    if request.module_display_name:
        args.extend(["-ModuleFriendlyName", request.module_display_name])
    
    return StreamingResponse(
        stream_powershell_output(str(script_path), *args, operation_id=request.operationId),
        media_type="text/event-stream"
    )


# ============================================================================
# FORM BUILDER API ENDPOINTS
# ============================================================================

class ListEntitiesRequest(BaseModel):
    module_path: str

class ExtractFieldsRequest(BaseModel):
    module_path: str
    entity_name: str
    form_guid: Optional[str] = None

class ValidateYamlRequest(BaseModel):
    yaml_config: str
    module_path: str

class BuildFormRequest(BaseModel):
    yaml_config: Optional[str] = None
    module_path: Optional[str] = None
    file_path: Optional[str] = None
    dry_run: bool = False

class ExtractAllEntitiesRequest(BaseModel):
    module_path: str
    overwrite: bool = False

class ExtractSingleEntityRequest(BaseModel):
    module_path: str
    entity_name: str

class BuildAllFormsRequest(BaseModel):
    module_path: str

@app.get("/api/formbuilder/list-modules")
async def list_modules_for_formbuilder():
    """
    List all modules in the repository for form building.
    
    Scans the repository root for module directories that contain
    src/Entities folders.
    """
    try:
        modules = []
        
        # Scan common module directories
        module_categories = [
            "administrative", "compliance-security", "external-engagement",
            "financial", "government", "operations", "workforce", "shared", "test"
        ]
        
        for category in module_categories:
            category_path = PROJECT_ROOT / category
            if not category_path.exists():
                continue
            
            # Scan for subdirectories with src/Entities
            for item in category_path.iterdir():
                if not item.is_dir():
                    continue
                
                entities_dir = item / "src" / "Entities"
                if entities_dir.exists():
                    # This is a valid module
                    module_name = f"{category}/{item.name}"
                    
                    # Try to get display name from Solution.xml
                    display_name = read_solution_display_name(item)
                    if not display_name:
                        display_name = item.name.replace("-", " ").title()
                    
                    modules.append({
                        "path": str(item),
                        "name": module_name,
                        "display_name": display_name
                    })
        
        # Sort by display name
        modules.sort(key=lambda x: x['display_name'])
        
        return {
            "success": True,
            "modules": modules
        }
    
    except Exception as e:
        print(f"Error listing modules: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/list-entities")
async def list_entities(request: ListEntitiesRequest):
    """
    List all entities in a module.
    
    Scans the module's src/Entities directory and returns entity names
    with display names.
    """
    try:
        module_path = Path(request.module_path)
        entities_dir = module_path / "src" / "Entities"
        
        if not entities_dir.exists():
            return {"success": False, "error": f"Entities directory not found: {entities_dir}"}
        
        entities = []
        
        for entity_dir in entities_dir.iterdir():
            if not entity_dir.is_dir():
                continue
            
            entity_xml = entity_dir / "Entity.xml"
            if not entity_xml.exists():
                continue
            
            entity_name = entity_dir.name
            
            # Try to get display name from Entity.xml
            try:
                tree = ET.parse(entity_xml)
                root = tree.getroot()
                localized_name = root.find(".//LocalizedName[@languagecode='1033']")
                display_name = localized_name.get('description') if localized_name is not None else entity_name
            except:
                display_name = entity_name
            
            entities.append({
                "name": entity_name,
                "display_name": display_name
            })
        
        # Sort by display name
        entities.sort(key=lambda x: x['display_name'])
        
        return {
            "success": True,
            "entities": entities
        }
    
    except Exception as e:
        print(f"Error listing entities: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/extract-fields")
async def extract_fields(request: ExtractFieldsRequest):
    """
    Extract custom fields from an entity and generate a YAML template.
    
    Reads the entity's Entity.xml file and generates a YAML configuration
    file that can be organized by AI (like GitHub Copilot) and used to
    build the form.
    """
    try:
        module_path = Path(request.module_path)
        entity_xml = module_path / "src" / "Entities" / request.entity_name / "Entity.xml"
        
        if not entity_xml.exists():
            return {"success": False, "error": f"Entity.xml not found: {entity_xml}"}
        
        # Read custom fields from entity
        fields = read_entity_definition(entity_xml)
        
        if not fields:
            return {
                "success": False,
                "error": "No custom fields found in entity. Add custom fields to the entity first."
            }
        
        # Get form GUID (auto-detect if not provided)
        form_guid = request.form_guid
        form_xml_path = None
        if not form_guid:
            # Try to find a main form
            form_dir = module_path / "src" / "Entities" / request.entity_name / "FormXml" / "main"
            if form_dir.exists():
                form_files = list(form_dir.glob("{*}.xml"))
                if form_files:
                    # Use first form found
                    form_guid = form_files[0].stem
                    form_xml_path = form_files[0]
                else:
                    form_guid = "{00000000-0000-0000-0000-000000000000}"
            else:
                form_guid = "{00000000-0000-0000-0000-000000000000}"
        else:
            # Form GUID provided, construct path
            form_xml_path = module_path / "src" / "Entities" / request.entity_name / "FormXml" / "main" / f"{form_guid}.xml"
            if not form_xml_path.exists():
                form_xml_path = None
        
        # Generate declarative YAML template
        yaml_template = generate_yaml_template(request.entity_name, form_guid, fields, module_path)
        
        return {
            "success": True,
            "yaml_template": yaml_template,
            "field_count": len(fields)
        }
    
    except Exception as e:
        print(f"Error extracting fields: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/extract-all-entities")
async def extract_all_entities(request: ExtractAllEntitiesRequest):
    """
    Extract all entities in a module to YAML layout files.
    
    Creates .design/layouts/<module>/ directory and generates one YAML file
    per entity. Skips existing files unless overwrite=True.
    """
    try:
        module_path = Path(request.module_path)
        module_name = module_path.name
        
        # Create layouts directory
        layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_name
        layouts_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all entities
        entities_dir = module_path / "src" / "Entities"
        if not entities_dir.exists():
            return {
                "success": False,
                "error": f"Entities directory not found: {entities_dir}"
            }
        
        extracted = []
        skipped_count = 0
        total_count = 0
        
        # Iterate through all entity folders
        for entity_dir in entities_dir.iterdir():
            if not entity_dir.is_dir():
                continue
            
            entity_xml = entity_dir / "Entity.xml"
            if not entity_xml.exists():
                continue
            
            total_count += 1
            entity_name = entity_dir.name
            layout_file = layouts_dir / f"{entity_name}.yaml"
            
            # Skip if file exists and overwrite is False
            if layout_file.exists() and not request.overwrite:
                skipped_count += 1
                extracted.append({
                    "entity": entity_name,
                    "file_path": str(layout_file),
                    "field_count": 0,
                    "existed": True
                })
                continue
            
            # Read entity definition
            try:
                fields = read_entity_definition(entity_xml)
                
                # Get form GUID (auto-detect first form)
                form_guid = "{00000000-0000-0000-0000-000000000000}"
                form_xml_path = None
                form_dir = entity_dir / "FormXml" / "main"
                if form_dir.exists():
                    form_files = list(form_dir.glob("{*}.xml"))
                    if form_files:
                        form_guid = form_files[0].stem
                        form_xml_path = form_files[0]
                
                # Generate declarative YAML template
                yaml_content = generate_yaml_template(entity_name, form_guid, fields, module_path)
                
                # Write to file
                with open(layout_file, 'w', encoding='utf-8') as f:
                    f.write(yaml_content)
                
                extracted.append({
                    "entity": entity_name,
                    "file_path": str(layout_file),
                    "field_count": len(fields),
                    "existed": False
                })
                
            except Exception as e:
                print(f"Error extracting {entity_name}: {e}", file=sys.stderr)
                continue
        
        return {
            "success": True,
            "extracted": extracted,
            "skipped_count": skipped_count,
            "total_count": total_count
        }
    
    except Exception as e:
        print(f"Error in extract_all_entities: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/extract-single-entity")
async def extract_single_entity(request: ExtractSingleEntityRequest):
    """
    Extract a single entity to a YAML layout file.
    
    Creates .design/layouts/<module>/<entity>.yaml file, overwriting if it exists.
    """
    try:
        module_path = Path(request.module_path)
        module_name = module_path.name
        
        # Create layouts directory
        layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_name
        layouts_dir.mkdir(parents=True, exist_ok=True)
        
        # Find entity directory
        entities_dir = module_path / "src" / "Entities"
        if not entities_dir.exists():
            return {
                "success": False,
                "error": f"Entities directory not found: {entities_dir}"
            }
        
        entity_dir = entities_dir / request.entity_name
        if not entity_dir.is_dir():
            return {
                "success": False,
                "error": f"Entity directory not found: {entity_dir}"
            }
        
        entity_xml = entity_dir / "Entity.xml"
        if not entity_xml.exists():
            return {
                "success": False,
                "error": f"Entity.xml not found: {entity_xml}"
            }
        
        layout_file = layouts_dir / f"{request.entity_name}.yaml"
        
        # Read entity definition
        fields = read_entity_definition(entity_xml)
        
        # Get form GUID (auto-detect first form)
        form_guid = "{00000000-0000-0000-0000-000000000000}"
        form_xml_path = None
        form_dir = entity_dir / "FormXml" / "main"
        if form_dir.exists():
            form_files = list(form_dir.glob("{*}.xml"))
            if form_files:
                form_guid = form_files[0].stem
                form_xml_path = form_files[0]
        
        # Generate declarative YAML template
        yaml_content = generate_yaml_template(request.entity_name, form_guid, fields, module_path)
        
        # Write to file (always overwrite for single entity recreate)
        with open(layout_file, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        
        return {
            "success": True,
            "entity": request.entity_name,
            "file_path": str(layout_file),
            "field_count": len(fields)
        }
    
    except Exception as e:
        print(f"Error extracting {request.entity_name}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.get("/api/formbuilder/list-layouts")
async def list_layouts(module_path: str):
    """
    List all layout files for a module.
    
    Returns YAML content, entity metadata, and file information.
    """
    try:
        module_path_obj = Path(module_path)
        module_name = module_path_obj.name
        
        layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_name
        
        # Return empty list if directory doesn't exist
        if not layouts_dir.exists():
            return {
                "success": True,
                "layouts": []
            }
        
        layouts = []
        
        # Read all YAML files
        for yaml_file in sorted(layouts_dir.glob("*.yaml")):
            entity_name = yaml_file.stem
            
            try:
                # Read YAML content
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                
                # Get entity display name from Entity.xml
                entity_xml = module_path_obj / "src" / "Entities" / entity_name / "Entity.xml"
                display_name = entity_name
                if entity_xml.exists():
                    try:
                        tree = ET.parse(entity_xml)
                        root = tree.getroot()
                        display_elem = root.find(".//LocalizedName[@languagecode='1033']")
                        if display_elem is not None:
                            display_name = display_elem.get('description', entity_name)
                    except:
                        pass
                
                # Get file modification time
                modified_time = yaml_file.stat().st_mtime
                from datetime import datetime
                modified_date = datetime.fromtimestamp(modified_time).isoformat()
                
                layouts.append({
                    "entity_name": entity_name,
                    "file_path": str(yaml_file),
                    "display_name": display_name,
                    "modified_date": modified_date,
                    "yaml_content": yaml_content
                })
                
            except Exception as e:
                print(f"Error reading layout {yaml_file}: {e}", file=sys.stderr)
                continue
        
        return {
            "success": True,
            "layouts": layouts
        }
    
    except Exception as e:
        print(f"Error listing layouts: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/validate-yaml")
async def validate_yaml_config(request: ValidateYamlRequest):
    """
    Validate a YAML form configuration.
    
    Checks:
    - YAML syntax is valid
    - Required fields are present
    - All referenced fields exist in the entity
    - Section structure is valid
    """
    try:
        # Parse YAML
        try:
            config = yaml.safe_load(request.yaml_config)
        except yaml.YAMLError as e:
            return {
                "success": False,
                "valid": False,
                "errors": [f"Invalid YAML syntax: {str(e)}"]
            }
        
        errors = []
        warnings = []
        
        # Check required fields in config
        if 'entity' not in config:
            errors.append("Missing required field: 'entity'")
        
        if 'form_guid' not in config:
            errors.append("Missing required field: 'form_guid'")
        
        if 'tabs' not in config:
            errors.append("Missing required field: 'tabs'")
        elif not isinstance(config['tabs'], list):
            errors.append("'tabs' must be a list")
        
        # Read entity definition to validate field names
        if 'entity' in config:
            module_path = Path(request.module_path)
            entity_xml = module_path / "src" / "Entities" / config['entity'] / "Entity.xml"
            
            if not entity_xml.exists():
                errors.append(f"Entity not found: {config['entity']}")
            else:
                try:
                    entity_fields = read_entity_definition(entity_xml)
                    valid_field_names = {f.logical_name for f in entity_fields}
                    
                    # Validate all field references in tabs/sections
                    if 'tabs' in config and isinstance(config['tabs'], list):
                        for tab_idx, tab in enumerate(config['tabs']):
                            if not isinstance(tab, dict):
                                errors.append(f"Tab {tab_idx + 1} is not a dictionary")
                                continue
                            
                            if 'label' not in tab:
                                errors.append(f"Tab {tab_idx + 1} missing 'label'")
                            
                            if 'sections' in tab and isinstance(tab['sections'], list):
                                for section_idx, section in enumerate(tab['sections']):
                                    if not isinstance(section, dict):
                                        errors.append(f"Tab {tab_idx + 1}, Section {section_idx + 1} is not a dictionary")
                                        continue
                                    
                                    if 'label' not in section:
                                        errors.append(f"Tab {tab_idx + 1}, Section {section_idx + 1} missing 'label'")
                                    
                                    if 'columns' not in section:
                                        warnings.append(f"Tab {tab_idx + 1}, Section {section_idx + 1} missing 'columns' (defaulting to 1)")
                                    elif section['columns'] not in [1, 2]:
                                        errors.append(f"Tab {tab_idx + 1}, Section {section_idx + 1} has invalid columns value (must be 1 or 2)")
                                    
                                    if 'fields' in section and isinstance(section['fields'], list):
                                        for field_name in section['fields']:
                                            if field_name not in valid_field_names:
                                                errors.append(f"Field '{field_name}' does not exist in entity '{config['entity']}'")
                except Exception as e:
                    errors.append(f"Error reading entity definition: {str(e)}")
        
        return {
            "success": True,
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    except Exception as e:
        print(f"Error validating YAML: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/build-form")
async def build_form_from_yaml(request: BuildFormRequest):
    """
    Build a form from a YAML configuration.
    
    This endpoint:
    1. Validates the YAML configuration
    2. Loads the form XML file
    3. Uses form_operations to add tabs, sections, and fields
    4. Saves the updated form XML
    
    If dry_run=True, returns a preview of operations without modifying files.
    
    Accepts either:
    - file_path: Read YAML from a saved layout file
    - yaml_config + module_path: Use YAML from request body (backward compatible)
    """
    try:
        # Determine source: file or request body
        if request.file_path:
            # Read YAML from file
            file_path = Path(request.file_path)
            if not file_path.exists():
                return {
                    "success": False,
                    "error": f"Layout file not found: {file_path}"
                }
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Error reading file: {str(e)}"
                }
            
            # Extract module path from file path pattern: .design/layouts/<module>/<entity>.yaml
            try:
                parts = file_path.parts
                layouts_idx = parts.index('layouts')
                module_name = parts[layouts_idx + 1]
                # Find module path in repository
                # First check direct match
                module_path = None
                for module_dir in PROJECT_ROOT.iterdir():
                    if module_dir.is_dir() and module_dir.name == module_name:
                        # Check if it has src/Entities
                        if (module_dir / 'src' / 'Entities').exists():
                            module_path = module_dir
                            break
                
                # If not found, check nested structures (e.g., test/Test/)
                if not module_path:
                    for parent_dir in PROJECT_ROOT.iterdir():
                        if parent_dir.is_dir():
                            for sub_dir in parent_dir.iterdir():
                                if sub_dir.is_dir() and (sub_dir / 'src' / 'Entities').exists():
                                    # Match by name (case-insensitive)
                                    if sub_dir.name.lower() == module_name.lower():
                                        module_path = sub_dir
                                        break
                            if module_path:
                                break
                
                if not module_path:
                    return {
                        "success": False,
                        "error": f"Could not find module '{module_name}' in repository. Searched for directory with src/Entities."
                    }
            except (ValueError, IndexError) as e:
                return {
                    "success": False,
                    "error": f"Invalid file path format: {file_path}"
                }
        else:
            # Use YAML from request body (backward compatible)
            if not request.yaml_config or not request.module_path:
                return {
                    "success": False,
                    "error": "Either file_path or (yaml_config + module_path) must be provided"
                }
            
            yaml_content = request.yaml_config
            module_path = Path(request.module_path)
        
        # Parse YAML
        try:
            config = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            return {
                "success": False,
                "error": f"Invalid YAML syntax: {str(e)}"
            }
        
        # Validate required fields
        if 'entity' not in config or 'form_guid' not in config or 'tabs' not in config:
            return {
                "success": False,
                "error": "YAML missing required fields: entity, form_guid, or tabs"
            }
        entity_name = config['entity']
        form_guid = config['form_guid'].strip('{}')  # Remove braces if present
        
        # Find form XML files
        form_dir = module_path / "src" / "Entities" / entity_name / "FormXml" / "main"
        unmanaged_path = form_dir / f"{{{form_guid}}}.xml"
        managed_path = form_dir / f"{{{form_guid}}}_managed.xml"
        
        if not unmanaged_path.exists():
            return {
                "success": False,
                "error": f"Form XML file not found: {unmanaged_path}"
            }
        
        # Dry run: return preview of operations
        if request.dry_run:
            operations = []
            
            for tab in config['tabs']:
                tab_name = tab.get('name', f"tab_{tab['label'].lower().replace(' ', '_')}")
                operations.append({
                    "type": "add_tab",
                    "tab_name": tab_name,
                    "tab_label": tab['label']
                })
                
                for section in tab.get('sections', []):
                    section_label = section['label']
                    columns = section.get('columns', 1)
                    field_count = len(section.get('fields', []))
                    
                    operations.append({
                        "type": "add_section",
                        "tab_name": tab_name,
                        "section_label": section_label,
                        "columns": columns
                    })
                    
                    operations.append({
                        "type": "add_fields",
                        "tab_name": tab_name,
                        "section_label": section_label,
                        "field_count": field_count,
                        "fields": section.get('fields', [])
                    })
            
            return {
                "success": True,
                "dry_run": True,
                "operations": operations
            }
        
        # Import form_operations (needed for actual execution)
        from form_operations import add_tab_to_form, add_section_to_tab, add_fields_to_section, add_fields_to_section_by_rows, update_section_columns, backup_forms, save_forms
        
        # Execute form building operations
        try:
            tabs_added = 0
            sections_added = 0
            fields_added = 0
            subgrids_to_add = []  # Collect all subgrids for batch processing at the end
            
            # DECLARATIVE REBUILD APPROACH: Clear existing form and rebuild from scratch
            # This ensures the YAML is the complete definition of the form
            print("Clearing existing form structure...")
            backup_forms(unmanaged_path, managed_path if managed_path.exists() else None)
            
            # Load form and clear all tabs
            form = FormXmlParser.parse_file(unmanaged_path)
            form.tabs.clear()
            
            # Save empty form
            save_forms(form, unmanaged_path, managed_path if managed_path.exists() else None)
            print(f"Cleared {len(form.tabs)} existing tabs. Rebuilding from YAML...")
            
            # Process each tab
            for tab_idx, tab in enumerate(config['tabs']):
                tab_name = tab.get('name')
                tab_label = tab['label']
                
                # Use tab name if provided, otherwise generate from label
                if not tab_name:
                    tab_name = f"tab_{tab_label.lower().replace(' ', '_')}"
                
                # Add tab (all tabs are new since we cleared the form)
                add_tab_to_form(
                    unmanaged_path=unmanaged_path,
                    tab_name=tab_name,
                    tab_label=tab_label,
                    managed_path=managed_path if managed_path.exists() else None,
                    create_backup=False,  # Already backed up when clearing
                    skip_if_exists=False,  # No tabs exist - we cleared them all
                    create_default_section=False  # YAML explicitly defines sections
                )
                tabs_added += 1
                
                # Add sections to tab
                for section in tab.get('sections', []):
                    section_label = section['label']
                    section_name = section.get('name')  # Optional, will auto-generate if not provided
                    columns = section.get('columns', 1)
                    
                    # Add section (all sections are new since we cleared the form)
                    add_section_to_tab(
                        unmanaged_path=unmanaged_path,
                        tab_name=tab_name,
                        section_label=section_label,
                        section_name=section_name,
                        columns=columns,
                        managed_path=managed_path if managed_path.exists() else None,
                        create_backup=False,  # Already backed up
                        skip_if_exists=False  # No sections exist - we cleared them all
                    )
                    sections_added += 1
                    
                    # Check if section uses row-based or field-based layout
                    rows_spec = section.get('rows')
                    fields = section.get('fields', [])
                    
                    if rows_spec:
                        # Row-based layout (advanced mode with explicit positioning)
                        # Read entity schema to get field types
                        entity_xml = module_path / "src" / "Entities" / entity_name / "Entity.xml"
                        entity_fields = read_entity_definition(entity_xml)
                        
                        # Build field_metadata dict for row-based function
                        field_metadata = {
                            field.logical_name: (field.display_name, field.form_field_type)
                            for field in entity_fields
                        }
                        
                        # Add system fields that are always available
                        field_metadata['ownerid'] = ('Owner', 'lookup')
                        # Name field uses entity prefix
                        entity_prefix = entity_name.split('_')[0] if '_' in entity_name else entity_name
                        name_field = f"{entity_prefix}_name"
                        field_metadata[name_field] = ('Name', 'text')
                        
                        # Count all fields that will be added
                        for row_spec in rows_spec:
                            for cell_spec in row_spec:
                                if isinstance(cell_spec, str):
                                    fields_added += 1
                                elif isinstance(cell_spec, dict):
                                    if cell_spec.get('field'):
                                        fields_added += 1
                        
                        # Add fields using row-based layout
                        add_fields_to_section_by_rows(
                            unmanaged_path=unmanaged_path,
                            tab_name=tab_name,
                            section_name=section_label,  # Use label - sections just created
                            rows=rows_spec,
                            field_metadata=field_metadata,
                            managed_path=managed_path if managed_path.exists() else None,
                            create_backup=False,
                            skip_if_exists=False  # No fields exist - we cleared them all
                        )
                    
                    elif fields:
                        # Field-based layout (simple auto-layout mode)
                        # Read entity schema to get field types
                        entity_xml = module_path / "src" / "Entities" / entity_name / "Entity.xml"
                        entity_fields = read_entity_definition(entity_xml)
                        
                        # Create system fields metadata
                        entity_prefix = entity_name.split('_')[0] if '_' in entity_name else entity_name
                        name_field = f"{entity_prefix}_name"
                        system_fields = {
                            'ownerid': ('Owner', 'lookup'),
                            name_field: ('Name', 'text')
                        }
                        
                        # Build list of (field_name, field_label, field_type) tuples
                        field_tuples = []
                        for field_name in fields:
                            # Check system fields first, then entity fields
                            if field_name in system_fields:
                                field_label, field_type = system_fields[field_name]
                            else:
                                field_type = next((f.form_field_type for f in entity_fields if f.logical_name == field_name), 'text')
                                field_label = next((f.display_name for f in entity_fields if f.logical_name == field_name), field_name)
                            field_tuples.append((field_name, field_label, field_type))
                            fields_added += 1
                        
                        add_fields_to_section(
                            unmanaged_path=unmanaged_path,
                            tab_name=tab_name,
                            section_name=section_label,  # Use label - sections just created
                            fields=field_tuples,
                            managed_path=managed_path if managed_path.exists() else None,
                            create_backup=False,
                            skip_if_exists=False  # No fields exist - we cleared them all
                        )
                    
                    # Check for subgrids in the section - collect them for batch processing
                    subgrids_spec = section.get('subgrids', [])
                    if subgrids_spec:
                        subgrids_to_add.append({
                            'tab_name': tab_name,
                            'section_label': section_label,
                            'subgrids': subgrids_spec
                        })
            
            # Process all subgrids in one batch (avoids multiple save/load cycles)
            if subgrids_to_add:
                print(f"Adding {len(subgrids_to_add)} subgrid sections...")
                from relationship_reader import get_relationships_with_views
                
                # Get relationships with view information ONCE
                all_relationships = get_relationships_with_views(module_path, entity_name)
                rel_map = {rel.name: rel for rel in all_relationships}
                
                # Load form ONCE
                form = FormXmlParser.parse_file(unmanaged_path)
                
                # Add all subgrids to the in-memory form
                subgrids_added = 0
                for subgrid_section in subgrids_to_add:
                    tab_name = subgrid_section['tab_name']
                    section_label = subgrid_section['section_label']
                    
                    # Find the tab
                    tab = form.get_tab_by_name(tab_name)
                    if not tab:
                        print(f"Warning: Tab '{tab_name}' not found for subgrids")
                        continue
                    
                    # Find the section  
                    section = tab.get_section_by_name(section_label)
                    if not section:
                        print(f"Warning: Section '{section_label}' not found in tab '{tab_name}'")
                        continue
                    
                    # Add each subgrid to the section
                    for subgrid_spec in subgrid_section['subgrids']:
                        relationship_name = subgrid_spec.get('relationship')
                        subgrid_label = subgrid_spec.get('label', 'Related Records')
                        
                        if not relationship_name:
                            print(f"Warning: Subgrid missing 'relationship' field, skipping")
                            continue
                        
                        # Look up relationship metadata
                        if relationship_name not in rel_map:
                            print(f"Warning: Relationship '{relationship_name}' not found in entity relationships")
                            continue
                        
                        rel = rel_map[relationship_name]
                        
                        # Check if we have a default view
                        if not rel.default_view_id:
                            print(f"Warning: No default view found for relationship '{relationship_name}', skipping subgrid")
                            continue
                        
                        # Generate unique subgrid ID
                        subgrid_id = f"subgrid_{relationship_name}"
                        
                        # Add subgrid directly to the section (in-memory)
                        section.add_subgrid(
                            subgrid_id=subgrid_id,
                            subgrid_label=subgrid_label,
                            relationship_name=relationship_name,
                            target_entity=rel.target_entity.lower(),
                            view_id=rel.default_view_id
                        )
                        subgrids_added += 1
                        print(f"Added subgrid '{subgrid_label}' for relationship '{relationship_name}'")
                
                # Save form ONCE with all subgrids
                save_forms(form, unmanaged_path, managed_path if managed_path.exists() else None)
                print(f"Successfully added {subgrids_added} subgrids")
            
            return {
                "success": True,
                "message": f"Form rebuilt successfully! Added {tabs_added} tabs, {sections_added} sections, {fields_added} fields.",
                "form_path": str(unmanaged_path),
                "stats": {
                    "tabs_added": tabs_added,
                    "sections_added": sections_added,
                    "fields_added": fields_added
                }
            }
        
        except Exception as e:
            print(f"Error building form: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            return {
                "success": False,
                "error": f"Error building form: {str(e)}"
            }
    
    except Exception as e:
        print(f"Error in build_form_from_yaml: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

@app.post("/api/formbuilder/build-all-forms")
async def build_all_forms(request: BuildAllFormsRequest):
    """
    Build forms for all entities in a module.
    
    Reads all YAML files from .design/layouts/<module>/ and builds each form.
    """
    try:
        module_path = Path(request.module_path)
        module_name = module_path.name
        
        # Find layout files
        layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_name
        if not layouts_dir.exists():
            return {
                "success": False,
                "error": f"Layouts directory not found: {layouts_dir}"
            }
        
        layout_files = list(layouts_dir.glob("*.yaml"))
        if not layout_files:
            return {
                "success": False,
                "error": f"No layout files found in {layouts_dir}"
            }
        
        # Build each form
        results = []
        success_count = 0
        error_count = 0
        
        for layout_file in sorted(layout_files):
            entity_name = layout_file.stem
            print(f"\nBuilding form for {entity_name}...")
            
            try:
                # Read and parse YAML
                with open(layout_file, 'r', encoding='utf-8') as f:
                    yaml_content = f.read()
                
                config = yaml.safe_load(yaml_content)
                if not config:
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": "Empty YAML file"
                    })
                    error_count += 1
                    continue
                
                # Validate required fields
                if 'entity' not in config:
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": "Missing 'entity' field in YAML"
                    })
                    error_count += 1
                    continue
                
                if 'form_guid' not in config:
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": "Missing 'form_guid' field in YAML"
                    })
                    error_count += 1
                    continue
                
                if 'tabs' not in config or not config['tabs']:
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": "Missing or empty 'tabs' field in YAML"
                    })
                    error_count += 1
                    continue
                
                # Find form XML file
                form_guid = config['form_guid'].strip('{}')
                entity_dir = module_path / "src" / "Entities" / config['entity']
                
                if not entity_dir.exists():
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": f"Entity directory not found: {entity_dir}"
                    })
                    error_count += 1
                    continue
                
                form_xml_dir = entity_dir / "FormXml" / "main"
                unmanaged_path = form_xml_dir / f"{{{form_guid}}}.xml"
                managed_path = form_xml_dir / f"{{{form_guid}}}_managed.xml"
                
                if not unmanaged_path.exists():
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": f"Form XML not found: {unmanaged_path}"
                    })
                    error_count += 1
                    continue
                
                # Import form operations
                from formxml_parser import FormXmlParser
                from form_operations import add_tab_to_form, add_section_to_tab, add_fields_to_section, add_fields_to_section_by_rows, update_section_columns, backup_forms, save_forms
                from entity_schema_reader import read_entity_definition
                
                # Build the form (same logic as build-form endpoint)
                tabs_added = 0
                sections_added = 0
                fields_added = 0
                subgrids_to_add = []
                
                # Backup and clear form
                backup_forms(unmanaged_path, managed_path if managed_path.exists() else None)
                form = FormXmlParser.parse_file(unmanaged_path)
                form.tabs.clear()
                save_forms(form, unmanaged_path, managed_path if managed_path.exists() else None)
                
                # Process tabs
                for tab in config['tabs']:
                    tab_name = tab.get('name') or f"tab_{tab['label'].lower().replace(' ', '_')}"
                    
                    add_tab_to_form(
                        unmanaged_path=unmanaged_path,
                        tab_name=tab_name,
                        tab_label=tab['label'],
                        managed_path=managed_path if managed_path.exists() else None,
                        create_backup=False,
                        skip_if_exists=False,
                        create_default_section=False
                    )
                    tabs_added += 1
                    
                    # Add sections
                    for section in tab.get('sections', []):
                        section_label = section['label']
                        section_name = section.get('name')
                        columns = section.get('columns', 1)
                        
                        add_section_to_tab(
                            unmanaged_path=unmanaged_path,
                            tab_name=tab_name,
                            section_label=section_label,
                            section_name=section_name,
                            columns=columns,
                            managed_path=managed_path if managed_path.exists() else None,
                            create_backup=False,
                            skip_if_exists=False
                        )
                        sections_added += 1
                        
                        # Add fields
                        rows_spec = section.get('rows')
                        fields = section.get('fields', [])
                        
                        if rows_spec:
                            entity_xml = entity_dir / "Entity.xml"
                            entity_fields = read_entity_definition(entity_xml)
                            field_metadata = {f.logical_name: (f.display_name, f.form_field_type) for f in entity_fields}
                            
                            # Add system fields
                            field_metadata['ownerid'] = ('Owner', 'lookup')
                            entity_prefix = config['entity'].split('_')[0]
                            field_metadata[f"{entity_prefix}_name"] = ('Name', 'text')
                            
                            for row_spec in rows_spec:
                                for cell_spec in row_spec:
                                    if isinstance(cell_spec, str):
                                        fields_added += 1
                                    elif isinstance(cell_spec, dict) and 'field' in cell_spec:
                                        fields_added += 1
                            
                            add_fields_to_section_by_rows(
                                unmanaged_path=unmanaged_path,
                                tab_name=tab_name,
                                section_label=section_label,
                                rows=rows_spec,
                                field_metadata=field_metadata,
                                managed_path=managed_path if managed_path.exists() else None,
                                create_backup=False,
                                skip_if_exists=False
                            )
                        elif fields:
                            fields_added += len(fields)
                            entity_xml = entity_dir / "Entity.xml"
                            entity_fields = read_entity_definition(entity_xml)
                            field_types = {f.logical_name: f.form_field_type for f in entity_fields}
                            
                            field_types['ownerid'] = 'lookup'
                            entity_prefix = config['entity'].split('_')[0]
                            field_types[f"{entity_prefix}_name"] = 'text'
                            
                            add_fields_to_section(
                                unmanaged_path=unmanaged_path,
                                tab_name=tab_name,
                                section_label=section_label,
                                fields=fields,
                                field_types=field_types,
                                managed_path=managed_path if managed_path.exists() else None,
                                create_backup=False,
                                skip_if_exists=False
                            )
                        
                        # Collect subgrids
                        subgrids_spec = section.get('subgrids', [])
                        if subgrids_spec:
                            subgrids_to_add.append({
                                'tab_name': tab_name,
                                'section_label': section_label,
                                'subgrids': subgrids_spec
                            })
                
                # Process subgrids
                if subgrids_to_add:
                    from relationship_reader import get_relationships_with_views
                    
                    all_relationships = get_relationships_with_views(module_path, config['entity'])
                    rel_map = {rel.name: rel for rel in all_relationships}
                    
                    form = FormXmlParser.parse_file(unmanaged_path)
                    subgrids_added = 0
                    
                    for subgrid_section in subgrids_to_add:
                        tab_name = subgrid_section['tab_name']
                        section_label = subgrid_section['section_label']
                        
                        tab = form.get_tab_by_name(tab_name)
                        if not tab:
                            continue
                        
                        section = tab.get_section_by_name(section_label)
                        if not section:
                            continue
                        
                        for subgrid_spec in subgrid_section['subgrids']:
                            relationship_name = subgrid_spec.get('relationship')
                            subgrid_label = subgrid_spec.get('label', 'Related Records')
                            
                            if not relationship_name or relationship_name not in rel_map:
                                continue
                            
                            rel = rel_map[relationship_name]
                            if not rel.default_view_id:
                                continue
                            
                            subgrid_id = f"subgrid_{relationship_name}"
                            section.add_subgrid(
                                subgrid_id=subgrid_id,
                                subgrid_label=subgrid_label,
                                relationship_name=relationship_name,
                                target_entity=rel.target_entity.lower(),
                                view_id=rel.default_view_id
                            )
                            subgrids_added += 1
                    
                    save_forms(form, unmanaged_path, managed_path if managed_path.exists() else None)
                
                # Success
                results.append({
                    "entity": entity_name,
                    "success": True,
                    "stats": {
                        "tabs": tabs_added,
                        "sections": sections_added,
                        "fields": fields_added
                    }
                })
                success_count += 1
                print(f"✓ Built {entity_name}: {tabs_added} tabs, {sections_added} sections, {fields_added} fields")
                
            except Exception as e:
                results.append({
                    "entity": entity_name,
                    "success": False,
                    "error": str(e)
                })
                error_count += 1
                print(f"✗ Error building {entity_name}: {e}")
        
        return {
            "success": True,
            "total": len(layout_files),
            "success_count": success_count,
            "error_count": error_count,
            "results": results
        }
    
    except Exception as e:
        print(f"Error in build_all_forms: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
