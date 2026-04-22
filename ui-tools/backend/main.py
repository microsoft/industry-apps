from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from typing import List
import asyncio
import json
from pathlib import Path
import sys
import subprocess
import shutil
import xml.etree.ElementTree as ET

# Import configuration and models
from config import (
    PROJECT_ROOT,
    CACHE_DIR,
    PENDING_CACHE_FILE,
    ALLOWED_ORIGINS,
    WORKSPACE_MANAGER
)
from models import (
    DeployRequest,
    SyncRequest,
    SyncFromRequest,
    ShipRequest,
    CreateModuleRequest,
    ReleaseRequest,
    UpdateVersionRequest,
    CreateFieldsRequest,
    CancelRequest,
    FieldTemplateRequest,
    ReleaseValidationRequest,
    ReleaseExecutionRequest,
    BatchCreateFieldsRequest,
    SingleTableFieldsRequest,
    DetectExistingFieldsRequest,
    StepExecutionRequest,
    BuildPackagesRequest,
    TableScanRequest,
    OptionSetSearchRequest,
    OptionSetCreateRequest,
    PendingOptionSetRequest,
    ListEntitiesRequest,
    ExtractFieldsRequest,
    ValidateYamlRequest,
    BuildFormRequest,
    ExtractAllEntitiesRequest,
    ExtractSingleEntityRequest,
    BuildAllFormsRequest
)

# Import utility functions
from utils import (
    read_solution_display_name,
    read_solution_version,
    stream_powershell_output,
    active_processes
)

# Add shared dataverse-client library to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient

# Add scripts to path for form builder and entity schema reader
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from entity_schema_reader import read_entity_definition, get_entity_name_from_xml, generate_yaml_template
from formxml_parser import FormXmlParser, generate_section_name
import yaml

# Import routers
from routers.form_builder import router as form_builder_router
from routers.helpers import router as helpers_router
from routers.option_sets import router as option_sets_router
from routers.release import router as release_router
from routers.deployment import router as deployment_router
from routers.process_simulation import router as process_simulation_router

app = FastAPI(title="Module Deployment API")

# CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(form_builder_router)
app.include_router(helpers_router)
app.include_router(option_sets_router)
app.include_router(release_router)
app.include_router(deployment_router)
app.include_router(process_simulation_router)

# Startup event - log workspace info
@app.on_event("startup")
async def startup_event():
    """Log workspace configuration on startup"""
    repo_summary = WORKSPACE_MANAGER.get_repo_summary()
    print("=" * 60)
    print("🚀 Industry Apps Backend Starting")
    print("=" * 60)
    print(f"Multi-repo mode: {repo_summary['multi_repo_mode']}")
    print(f"Enabled repos: {repo_summary['count']}")
    for repo in repo_summary['repos']:
        print(f"  - {repo['name']} ({repo['type']}) at {repo['path']}")
    print("=" * 60)


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

@app.get("/api/config")
async def get_config():
    """Get deployment configuration and available modules from all repos"""
    all_categories = {}
    all_deployments = {}
    all_module_configs = {}
    all_default_configs = {}
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools"}
    
    # Iterate through all enabled repos
    for repo in WORKSPACE_MANAGER.get_all_repos():
        repo_path = repo.path
        config_path = repo_path / ".config" / "deployments.json"
        
        # Load repo's deployment config
        if config_path.exists():
            with open(config_path, "r") as f:
                config = json.load(f)
            
            # Merge deployments (with repo prefix if conflicts)
            deployments = config.get("Deployments", {})
            for dep_name, dep_data in deployments.items():
                key = f"{repo.name}:{dep_name}" if dep_name in all_deployments else dep_name
                all_deployments[key] = dep_data
            
            # Merge module configs
            all_module_configs.update(config.get("Modules", {}))
            
            # Keep default config from each repo (use primary repo's as fallback)
            if repo.name == "industry-apps":
                all_default_configs = config.get("DefaultModule", {})
        
        # Get categories and modules from this repo
        for item in repo_path.iterdir():
            if item.is_dir() and item.name not in exclude_folders:
                modules = []
                for module_dir in item.iterdir():
                    if module_dir.is_dir() and list(module_dir.glob("*.cdsproj")):
                        modules.append(module_dir.name)
                
                if modules:
                    # Prefix category with repo name if multi-repo and not from primary
                    category_key = item.name
                    if WORKSPACE_MANAGER.is_multi_repo() and repo.name != "industry-apps":
                        category_key = f"{repo.name}/{item.name}"
                    
                    all_categories[category_key] = sorted(modules)
    
    return {
        "deployments": all_deployments,
        "categories": all_categories,
        "modules": all_module_configs,
        "defaultModule": all_default_configs,
        "repos": WORKSPACE_MANAGER.get_repo_summary()
    }

@app.get("/api/modules")
async def get_modules():
    """Get all modules with their metadata from all repos"""
    all_modules = []
    seen_paths = set()  # Track paths to avoid duplicates
    exclude_folders = {"__pycache__", ".scripts", ".config", ".git", ".vscode", "bin", "obj", "ui-tools", "releases", ".design", "design", "test", "backups"}
    
    # Recursively scan for all modules (handles nested folder structures)
    def scan_for_modules(base_path, relative_path, repo_name, repo_path, deployments, module_configs, default_config):
        for item in base_path.iterdir():
            if item.is_dir() and item.name not in exclude_folders:
                # Check if this directory contains a .cdsproj file (it's a module)
                if list(item.glob("*.cdsproj")):
                    module_name = item.name
                    category = relative_path if relative_path else item.parent.name
                    
                    # Calculate relative path from repo root
                    relative_module_path = str(item.relative_to(repo_path))
                    
                    # Create unique path including repo name
                    unique_path = f"{repo_name}:{relative_module_path}"
                    
                    # Skip if we've already seen this path (avoid duplicates)
                    if unique_path in seen_paths:
                        continue
                    seen_paths.add(unique_path)
                    
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
                        
                        all_modules.append({
                            "name": module_name,
                            "displayName": display_name,
                            "category": category,
                            "path": relative_module_path,
                            "repo": repo_name,
                            "repoPath": str(repo_path),
                            "tenant": tenant,
                            "deployment": deployment_name,
                            "sourceEnvironment": source_env,
                            "sourceEnvironmentKey": source_env_key,
                            "targetEnvironments": target_envs,
                            "targetEnvironmentKeys": target_env_keys,
                            "version": version
                        })
                else:
                    # Recursively scan subdirectories only if no .cdsproj found
                    new_relative = f"{relative_path}/{item.name}" if relative_path else item.name
                    scan_for_modules(item, new_relative, repo_name, repo_path, deployments, module_configs, default_config)
    
    # Iterate through all enabled repos
    for repo in WORKSPACE_MANAGER.get_all_repos():
        repo_path = repo.path
        config_path = repo_path / ".config" / "deployments.json"
        
        # Load repo's deployment config
        if not config_path.exists():
            continue
        
        with open(config_path, "r") as f:
            config = json.load(f)
        
        deployments = config.get("Deployments", {})
        module_configs = config.get("Modules", {})
        default_config = config.get("DefaultModule", {})
        
        # Scan all directories in repo (no hardcoded category restrictions)
        for item in repo_path.iterdir():
            if item.is_dir() and item.name not in exclude_folders:
                scan_for_modules(item, item.name, repo.name, repo_path, deployments, module_configs, default_config)
    
    return {"modules": all_modules}

@app.get("/api/environments")
async def get_environments():
    """Get environment topology organized by tenant from all repos"""
    tenants = {}
    
    # Iterate through all enabled repos
    for repo in WORKSPACE_MANAGER.get_all_repos():
        config_path = repo.path / ".config" / "deployments.json"
        
        if not config_path.exists():
            continue
        
        with open(config_path, "r") as f:
            config = json.load(f)
        
        deployments = config.get("Deployments", {})
        
        # Organize by tenant
        for deployment_name, deployment_data in deployments.items():
            tenant = deployment_data.get("Tenant", "Unknown")
            environments = deployment_data.get("Environments", {})
            
            if tenant not in tenants:
                tenants[tenant] = {
                    "name": tenant,
                    "deployments": []
                }
            
            # Check if deployment already exists (same name from different repo)
            existing_dep = next((d for d in tenants[tenant]["deployments"] if d["name"] == deployment_name), None)
            if existing_dep:
                # Merge environments if deployment name conflicts
                for env_dict in [{"key": key, "name": value} for key, value in environments.items()]:
                    if env_dict not in existing_dep["environments"]:
                        existing_dep["environments"].append(env_dict)
            else:
                tenants[tenant]["deployments"].append({
                    "name": deployment_name,
                    "repo": repo.name,
                    "environments": [
                        {"key": key, "name": value}
                        for key, value in environments.items()
                    ]
                })
    
    return {"tenants": list(tenants.values())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
