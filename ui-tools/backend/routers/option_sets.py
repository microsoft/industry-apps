"""
Option Sets Router - API endpoints for option sets and table management.

This module contains endpoints for:
- Table scanning from Dataverse
- Option set searching, creation, and management
- Pending option sets cache management
- Global option sets scanning
"""

from fastapi import APIRouter
from pathlib import Path
import sys
import json
import xml.etree.ElementTree as ET

# Import from parent (backend) directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from models import (
    TableScanRequest,
    OptionSetSearchRequest,
    OptionSetCreateRequest,
    PendingOptionSetRequest
)

# Import Dataverse client
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'dataverse-client'))
from client import DataverseClient

# Import helper functions from main
import main as main_module


router = APIRouter(prefix="/api/helpers", tags=["Option Sets"])


@router.post("/tables/scan")
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

@router.post("/option-sets/search")
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

@router.post("/option-sets/create")
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

@router.get("/option-sets/pending")
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

@router.post("/option-sets/pending")
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

@router.delete("/option-sets/pending/{schema_name}")
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

@router.delete("/option-sets/pending")
async def clear_pending_optionsets():
    """Clear all pending option sets from cache"""
    try:
        save_pending_optionsets([])
        return {"success": True, "message": "Cleared all pending option sets"}
    except Exception as e:
        print(f"Error clearing pending option sets: {e}", file=sys.stderr)
        return {"success": False, "error": str(e)}

# ============================================================================


@router.get("/option-sets/scan")
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
