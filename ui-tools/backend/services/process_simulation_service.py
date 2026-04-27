"""
Business logic for Process Simulation operations.

This service handles data model generation, file operations, validation,
dry-run simulation, and event stream execution against Dataverse.
"""

import yaml
import re
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sys

logger = logging.getLogger(__name__)

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

# Add dataverse-client directory to path
dataverse_client_dir = Path(__file__).parent.parent.parent / "dataverse-client"
sys.path.insert(0, str(dataverse_client_dir))

from data_model_generator import save_data_models
from client import DataverseClient


class ProcessSimulationService:
    """Service for process simulation operations."""
    
    # Class-level storage for execution states (in-memory session storage)
    execution_states: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, workspace_root: Path):
        """
        Initialize the service.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = workspace_root
    
    # ========================================================================
    # Module and File Discovery
    # ========================================================================
    
    def list_modules_with_processes(self) -> List[Dict[str, Any]]:
        """
        List all modules that have design/processes directories.
        
        Returns:
            List of module dictionaries with metadata
        """
        modules = []
        
        # Scan all category directories
        for category_dir in self.workspace_root.iterdir():
            if not category_dir.is_dir():
                continue
            
            # Skip non-module directories
            if category_dir.name in ['.design', '.venv', 'ui-tools', 'data-generator', 'test', 'shared']:
                continue
            
            # Scan modules in category
            for module_dir in category_dir.iterdir():
                if not module_dir.is_dir():
                    continue
                
                design_dir = module_dir / "design"
                has_processes = design_dir.exists() and any(design_dir.iterdir())
                
                module_info = {
                    "name": module_dir.name,
                    "category": category_dir.name,
                    "path": str(module_dir.relative_to(self.workspace_root)),
                    "has_processes": has_processes
                }
                
                modules.append(module_info)
        
        return modules
    
    def list_files(self, module_path: str, file_type: str) -> List[Dict[str, str]]:
        """
        List files of a specific type in a module.
        
        Args:
            module_path: Relative path to module from workspace root
            file_type: One of 'data-models', 'processes', 'scenarios', 'simulations'
            
        Returns:
            List of file dictionaries
        """
        module_dir = self.workspace_root / module_path
        # Map old 'event-streams' to 'simulations' for backward compatibility
        folder_name = "simulations" if file_type in ("event-streams", "simulations") else file_type
        type_dir = module_dir / "design" / folder_name
        
        if not type_dir.exists():
            return []
        
        files = []
        for file_path in sorted(type_dir.glob("*.yaml")):
            files.append({
                "name": file_path.stem,
                "filename": file_path.name,
                "path": str(file_path.relative_to(self.workspace_root)),
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
        
        return files
    
    # ========================================================================
    # File Operations
    # ========================================================================
    
    def read_file(self, file_path: str) -> str:
        """
        Read a YAML file.
        
        Args:
            file_path: Relative path from workspace root
            
        Returns:
            File contents as string
        """
        full_path = self.workspace_root / file_path
        
        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        return full_path.read_text(encoding="utf-8")
    
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> None:
        """
        Write a YAML file.
        
        Args:
            file_path: Relative path from workspace root
            content: File contents to write
            create_dirs: Create parent directories if they don't exist
        """
        full_path = self.workspace_root / file_path
        
        if create_dirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)
        
        full_path.write_text(content, encoding="utf-8")
    
    # ========================================================================
    # Data Model Generation
    # ========================================================================
    
    def generate_data_models(self, module_path: str) -> List[str]:
        """
        Generate individual data-model YAML files from Entity.xml files.
        
        Args:
            module_path: Relative path to module from workspace root
            
        Returns:
            List of paths to generated files (relative to workspace root)
        """
        module_dir = self.workspace_root / module_path
        
        output_paths = save_data_models(module_dir)
        
        return [str(p.relative_to(self.workspace_root)) for p in output_paths]
    
    def _load_data_models(self, module_path: str) -> Dict[str, Any]:
        """
        Load all data model table files and consolidate into a single structure.
        
        Args:
            module_path: Relative path to module from workspace root
            
        Returns:
            Dictionary containing all entities and their fields
        """
        module_dir = self.workspace_root / module_path
        data_models_dir = module_dir / "design" / "data-models"
        
        if not data_models_dir.exists():
            raise FileNotFoundError("Data models directory not found. Generate them first.")
        
        # Load all YAML files in the data-models directory
        entities = []
        for yaml_file in data_models_dir.glob("*.yaml"):
            try:
                table_data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
                
                # Parse fields from the "Display Name: Type; schema_name" format
                # or "Display Name: Type; schema_name; optionset=name"
                fields = []
                for field_line in table_data.get("fields", []):
                    # Parse format: "Display Name: Type; schema_name"
                    # or "Display Name: Lookup (Target); schema_name"
                    # or "Display Name: Choice; schema_name; optionset=name"
                    parts = field_line.split(";")
                    if len(parts) < 2:
                        continue
                    
                    schema_name = parts[1].strip()
                    name_type = parts[0].strip()
                    
                    # Split display name and type
                    if ":" not in name_type:
                        continue
                    
                    display_name, field_type = name_type.split(":", 1)
                    display_name = display_name.strip()
                    field_type = field_type.strip()
                    
                    fields.append({
                        "logical_name": schema_name,
                        "display_name": display_name,
                        "type": field_type.lower().replace(" ", "_"),
                        "required": "none"
                    })
                
                # Build entity structure
                entity = {
                    "logical_name": table_data.get("schema_name", ""),
                    "display_name": table_data.get("name", ""),
                    "fields": fields
                }
                
                entities.append(entity)
                
            except Exception as e:
                # Skip files that can't be parsed
                continue
        
        # Add standard Dataverse entities (Contact, Account, etc.)
        standard_entities = [
            {
                "logical_name": "Contact",
                "display_name": "Contact",
                "fields": [
                    {"logical_name": "firstname", "display_name": "First Name", "type": "text", "required": "none"},
                    {"logical_name": "lastname", "display_name": "Last Name", "type": "text", "required": "none"},
                    {"logical_name": "emailaddress1", "display_name": "Email", "type": "text", "required": "none"},
                    {"logical_name": "telephone1", "display_name": "Phone", "type": "text", "required": "none"},
                    {"logical_name": "mobilephone", "display_name": "Mobile Phone", "type": "text", "required": "none"},
                    {"logical_name": "jobtitle", "display_name": "Job Title", "type": "text", "required": "none"},
                    {"logical_name": "department", "display_name": "Department", "type": "text", "required": "none"},
                    {"logical_name": "address1_line1", "display_name": "Address Line 1", "type": "text", "required": "none"},
                    {"logical_name": "address1_city", "display_name": "City", "type": "text", "required": "none"},
                    {"logical_name": "address1_stateorprovince", "display_name": "State/Province", "type": "text", "required": "none"},
                    {"logical_name": "address1_postalcode", "display_name": "Postal Code", "type": "text", "required": "none"},
                ]
            },
            {
                "logical_name": "Account",
                "display_name": "Account",
                "fields": [
                    {"logical_name": "name", "display_name": "Account Name", "type": "text", "required": "none"},
                    {"logical_name": "emailaddress1", "display_name": "Email", "type": "text", "required": "none"},
                    {"logical_name": "telephone1", "display_name": "Phone", "type": "text", "required": "none"},
                ]
            }
        ]
        
        entities.extend(standard_entities)
        
        return {"entities": entities}
    
    # ========================================================================
    # Validation
    # ========================================================================
    
    def validate_event_stream(self, module_path: str, event_stream_yaml: str) -> Tuple[bool, List[str], List[str], List[Dict]]:
        """
        Validate an event stream against entity schemas.
        
        Args:
            module_path: Relative path to module
            event_stream_yaml: Event stream YAML content
            
        Returns:
            Tuple of (valid, errors, warnings, event_validations)
        """
        try:
            # Parse event stream
            event_stream = yaml.safe_load(event_stream_yaml)
        except yaml.YAMLError as e:
            return False, [f"Invalid YAML: {str(e)}"], [], []
        
        # Load data models from individual table files
        try:
            data_models = self._load_data_models(module_path)
        except FileNotFoundError as e:
            return False, [str(e)], [], []
        except Exception as e:
            return False, [f"Error loading data models: {str(e)}"], [], []
        
        # Build entity lookup with case-insensitive keys
        entities_by_name = {entity["logical_name"]: entity for entity in data_models.get("entities", [])}
        # Create case-insensitive lookup: lowercase -> actual name
        entity_name_map = {name.lower(): name for name in entities_by_name.keys()}
        
        # Validate each event
        errors = []
        warnings = []
        event_validations = []
        
        events = event_stream.get("events", [])
        for event in events:
            event_id = event.get("event_id", "unknown")
            entity_name = event.get("entity")
            operation = event.get("operation")
            fields = event.get("fields", {})
            
            event_errors = []
            event_warnings = []
            
            # Normalize entity name (case-insensitive lookup)
            entity_name_lower = entity_name.lower() if entity_name else ""
            actual_entity_name = entity_name_map.get(entity_name_lower)
            
            # Check entity exists
            if not actual_entity_name:
                event_errors.append(f"Unknown entity: {entity_name}")
            else:
                entity = entities_by_name[actual_entity_name]
                entity_fields = {f["logical_name"]: f for f in entity.get("fields", [])}
                # Case-insensitive field lookup
                field_name_map = {name.lower(): name for name in entity_fields.keys()}
                
                # Check fields
                for field_name, field_value in fields.items():
                    # Skip OData bind fields (lookups)
                    if field_name.endswith("@odata.bind"):
                        base_field = field_name.replace("@odata.bind", "")
                        base_field_lower = base_field.lower()
                        if base_field_lower not in field_name_map:
                            event_warnings.append(f"Lookup field not in schema: {base_field}")
                        continue
                    
                    # Skip system fields (case-insensitive)
                    if field_name.lower() in ["statuscode", "statecode"]:
                        continue
                    
                    # Check if field exists (case-insensitive)
                    field_name_lower = field_name.lower()
                    if field_name_lower not in field_name_map:
                        event_errors.append(f"Unknown field: {field_name}")
            
            # Check operation is valid
            if operation not in ["create", "update", "delete"]:
                event_errors.append(f"Invalid operation: {operation}")
            
            # Store validation result
            event_validations.append({
                "event_id": event_id,
                "valid": len(event_errors) == 0,
                "errors": event_errors,
                "warnings": event_warnings
            })
            
            errors.extend([f"Event {event_id}: {e}" for e in event_errors])
            warnings.extend([f"Event {event_id}: {w}" for w in event_warnings])
        
        valid = len(errors) == 0
        
        return valid, errors, warnings, event_validations
    
    # ========================================================================
    # Dry Run
    # ========================================================================
    
    def dry_run(self, module_path: str, event_stream_yaml: str) -> Tuple[bool, int, int, List[str], List[str], List[Dict]]:
        """
        Simulate event stream execution without actually creating records.
        
        Args:
            module_path: Relative path to module
            event_stream_yaml: Event stream YAML content
            
        Returns:
            Tuple of (success, total_events, valid_events, errors, warnings, event_results)
        """
        # First validate
        valid, errors, warnings, event_validations = self.validate_event_stream(module_path, event_stream_yaml)
        
        if not valid:
            return False, 0, 0, errors, warnings, []
        
        # Parse event stream
        event_stream = yaml.safe_load(event_stream_yaml)
        events = event_stream.get("events", [])
        
        # Track stored records for template resolution
        stored_records = {}
        
        event_results = []
        
        for event in events:
            event_id = event.get("event_id", 0)
            operation = event.get("operation")
            entity = event.get("entity")
            fields = event.get("fields", {})
            store_as = event.get("store_as")
            
            event_errors = []
            event_warnings = []
            resolved_fields = {}
            
            # Resolve template variables
            for field_name, field_value in fields.items():
                resolved_value = self._resolve_template_vars(field_value, stored_records)
                resolved_fields[field_name] = resolved_value
                
                # Check if resolution failed
                if isinstance(field_value, str) and "{{" in field_value:
                    if resolved_value == field_value:  # Didn't resolve
                        event_warnings.append(f"Template variable not resolved: {field_value}")
            
            # Simulate storing record
            if store_as:
                stored_records[store_as] = {
                    "id": f"simulated-{event_id}-guid",
                    **resolved_fields
                }
            
            event_results.append({
                "event_id": event_id,
                "operation": operation,
                "entity": entity,
                "success": len(event_errors) == 0,
                "errors": event_errors,
                "warnings": event_warnings,
                "resolved_fields": resolved_fields
            })
        
        success = all(r["success"] for r in event_results)
        
        return success, len(events), len(event_results), errors, warnings, event_results
    
    def analyze_prerequisites(self, event_stream_yaml: str) -> Dict[str, Any]:
        """
        Analyze event stream to identify prerequisite records.
        
        Extracts:
        - Lookup references (lookup:...) that expect existing records
        - Template variables ({{...}}) not created by previous events
        
        Args:
            event_stream_yaml: Event stream YAML content
            
        Returns:
            Dictionary with lookup_prerequisites and template_prerequisites
        """
        try:
            data = yaml.safe_load(event_stream_yaml)
        except yaml.YAMLError as e:
            return {
                "error": f"Invalid YAML: {str(e)}",
                "lookup_prerequisites": [],
                "template_prerequisites": []
            }
        
        events = data.get("events", [])
        lookup_prerequisites = []
        template_prerequisites = []
        stored_variables = set()
        
        # Pattern for lookup references
        lookup_pattern = r'lookup:([^)]+)'
        # Pattern for template variables
        template_pattern = r'\{\{([^}]+)\}\}'
        
        for event in events:
            event_id = event.get("event_id", 0)
            operation = event.get("operation", "")
            entity = event.get("entity", "")
            fields = event.get("fields", {})
            store_as = event.get("store_as")
            
            # Track variables created by this event
            if store_as:
                stored_variables.add(store_as)
            
            # Scan fields for lookup and template references
            for field_name, field_value in fields.items():
                if not isinstance(field_value, str):
                    continue
                
                # Find lookup references
                lookup_matches = re.findall(lookup_pattern, field_value)
                for lookup_value in lookup_matches:
                    # Extract entity from @odata.bind syntax
                    # Example: /contacts(lookup:email) or /appbase_organizationunits(lookup:name)
                    entity_match = re.search(r'/(\w+)\(lookup:', field_value)
                    target_entity = entity_match.group(1) if entity_match else "unknown"
                    
                    # Determine search field from field name pattern
                    search_field = "name"  # Default
                    if "email" in field_name.lower() or "@" in lookup_value:
                        search_field = "emailaddress1"
                    elif target_entity == "contacts" and "." in lookup_value:
                        search_field = "emailaddress1"
                    
                    lookup_prerequisites.append({
                        "event_id": event_id,
                        "operation": operation,
                        "entity": entity,
                        "field_name": field_name,
                        "target_entity": target_entity,
                        "search_field": search_field,
                        "search_value": lookup_value.strip(),
                        "full_reference": field_value
                    })
                
                # Find template variable references
                template_matches = re.findall(template_pattern, field_value)
                for template_ref in template_matches:
                    # Parse variable name (before first dot)
                    var_name = template_ref.split('.')[0].strip()
                    
                    # Only flag as prerequisite if not created by previous event
                    if var_name not in stored_variables:
                        template_prerequisites.append({
                            "event_id": event_id,
                            "operation": operation,
                            "entity": entity,
                            "field_name": field_name,
                            "variable_name": var_name,
                            "template_reference": f"{{{{{template_ref}}}}}",
                            "field_value": field_value
                        })
        
        # Deduplicate lookup prerequisites
        unique_lookups = []
        seen = set()
        for lookup in lookup_prerequisites:
            key = (lookup["target_entity"], lookup["search_field"], lookup["search_value"])
            if key not in seen:
                seen.add(key)
                unique_lookups.append(lookup)
        
        # Deduplicate template prerequisites
        unique_templates = []
        seen_templates = set()
        for template in template_prerequisites:
            key = template["variable_name"]
            if key not in seen_templates:
                seen_templates.add(key)
                unique_templates.append(template)
        
        return {
            "lookup_prerequisites": unique_lookups,
            "template_prerequisites": unique_templates,
            "total_prerequisites": len(unique_lookups) + len(unique_templates)
        }
    
    def _resolve_template_vars(self, value: Any, stored_records: Dict) -> Any:
        """
        Resolve template variables in a value.
        
        Args:
            value: Value that may contain template variables
            stored_records: Dictionary of stored record data
            
        Returns:
            Resolved value
        """
        if not isinstance(value, str):
            return value
        
        # Pattern: {{var_name.field_name}} or {{var_name}}
        pattern = r'\{\{([^}]+)\}\}'
        
        def replace_var(match):
            var_path = match.group(1).strip()
            parts = var_path.split(".")
            
            # Navigate to the value
            current = stored_records
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return match.group(0)  # Return original if not found
            
            return str(current)
        
        return re.sub(pattern, replace_var, value)
    
    # ========================================================================
    # Deployment Configuration
    # ========================================================================
    
    def _load_deployments_config(self) -> Dict[str, Any]:
        """Load deployments configuration from .config/deployments.json"""
        config_path = self.workspace_root / ".config" / "deployments.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Deployments config not found: {config_path}")
        
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _get_dataverse_client(self, deployment: str, environment_key: str) -> DataverseClient:
        """
        Get initialized DataverseClient for specified deployment and environment.
        
        Args:
            deployment: Deployment name (e.g., "CDX FAST", "GLOWS DEV")
            environment_key: Environment key (e.g., "FAST CORE", "GOV INDUSTRY APPS")
            
        Returns:
            Initialized DataverseClient
            
        Raises:
            ValueError: If deployment or environment not found or auth not configured
        """
        config = self._load_deployments_config()
        
        # Get deployment config
        if deployment not in config.get("Deployments", {}):
            raise ValueError(f"Deployment '{deployment}' not found in config")
        
        deployment_config = config["Deployments"][deployment]
        
        # Check if auth is configured
        if "Auth" not in deployment_config:
            raise ValueError(f"Deployment '{deployment}' does not have Auth configured")
        
        auth = deployment_config["Auth"]
        
        # Get environment URL
        if "EnvironmentUrls" not in auth:
            raise ValueError(f"Deployment '{deployment}' does not have EnvironmentUrls configured")
        
        if environment_key not in auth["EnvironmentUrls"]:
            raise ValueError(f"Environment '{environment_key}' not found in EnvironmentUrls for deployment '{deployment}'")
        
        environment_url = auth["EnvironmentUrls"][environment_key]
        
        # Ensure URL has https:// prefix
        if not environment_url.startswith("http"):
            environment_url = f"https://{environment_url}"
        
        # Initialize and return DataverseClient
        client = DataverseClient(
            environment_url=environment_url,
            tenant_id=auth["TenantId"],
            client_id=auth["ClientId"],
            client_secret=auth["ClientSecret"]
        )
        
        return client
    
    def _entity_to_entity_set(self, entity_logical_name: str) -> str:
        """
        Convert entity logical name to entity set name.
        
        Dataverse Web API uses pluralized entity set names.
        For custom entities, this is typically the logical name + 's'.
        
        Args:
            entity_logical_name: Entity logical name (e.g., "appbase_disputeintake")
            
        Returns:
            Entity set name (e.g., "appbase_disputeintakes")
        """
        # Standard entities have special pluralization
        standard_plurals = {
            "contact": "contacts",
            "account": "accounts",
            "user": "systemusers",
            "team": "teams",
            "organization": "organizations",
        }
        
        entity_lower = entity_logical_name.lower()
        if entity_lower in standard_plurals:
            return standard_plurals[entity_lower]
        
        # For custom entities, add 's' unless it already ends in 's'
        if entity_logical_name.endswith('s'):
            return entity_logical_name
        
        return entity_logical_name + "s"
    
    def _resolve_lookup(self, client: DataverseClient, entity_set_name: str, search_field: str, search_value: str) -> Optional[str]:
        """
        Resolve a lookup by searching for a record.
        
        Args:
            client: DataverseClient instance
            entity_set_name: Entity set name to search in (e.g., "contacts")
            search_field: Field to search by (e.g., "emailaddress1", "appbase_name")
            search_value: Value to search for
            
        Returns:
            GUID of found record, or None if not found
        """
        try:
            # Common lookup field mappings
            if entity_set_name == "contacts" and not search_field:
                # Default to email for contacts
                search_field = "emailaddress1"
            elif not search_field:
                # Default to name field for custom entities
                search_field = "appbase_name"
            
            # Build filter query
            filter_query = f"{search_field} eq '{search_value}'"
            
            # Query for the record
            records = client.query_records(
                entity_set_name=entity_set_name,
                filter_query=filter_query,
                top=1
            )
            
            if records and len(records) > 0:
                record = records[0]
                # Find the primary key field (ends with 'id')
                record_id = None
                for key, value in record.items():
                    if key.endswith("id") and isinstance(value, str) and len(value) == 36:
                        record_id = value
                        break
                
                if record_id:
                    logger.info(f"Resolved lookup: {entity_set_name}({search_field}='{search_value}') -> {record_id}")
                    return record_id
                else:
                    logger.warning(f"Found record in {entity_set_name} but no GUID field")
            else:
                logger.warning(f"No record found: {entity_set_name} where {search_field}='{search_value}'")
            
            return None
            
        except Exception as e:
            logger.error(f"Error resolving lookup for {entity_set_name}: {e}")
            return None
    
    def _resolve_lookup_fields(self, client: DataverseClient, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve lookup fields that use the 'lookup:' syntax.
        
        Converts:
            "/contacts(lookup:email@example.com)" 
        To:
            "/contacts(12345678-1234-1234-1234-123456789abc)"
        
        Args:
            client: DataverseClient instance
            fields: Dictionary of field names to values
            
        Returns:
            Dictionary with resolved lookup values
        """
        resolved_fields = {}
        
        for field_name, field_value in fields.items():
            if isinstance(field_value, str) and "@odata.bind" in field_name and "lookup:" in field_value:
                # Parse the lookup syntax: /entity_set(lookup:search_value)
                match = re.match(r'/([^(]+)\(lookup:([^)]+)\)', field_value)
                if match:
                    entity_set_name = match.group(1)
                    search_value = match.group(2)
                    
                    # Determine search field (could be enhanced later)
                    search_field = None
                    
                    # Resolve the lookup
                    record_id = self._resolve_lookup(client, entity_set_name, search_field, search_value)
                    
                    if record_id:
                        # Replace with actual GUID
                        resolved_fields[field_name] = f"/{entity_set_name}({record_id})"
                        logger.info(f"Resolved {field_name}: {field_value} -> /{entity_set_name}({record_id})")
                    else:
                        # Keep original value and log warning (will likely fail)
                        resolved_fields[field_name] = field_value
                        logger.warning(f"Could not resolve lookup: {field_value}")
                else:
                    # Invalid syntax, keep original
                    resolved_fields[field_name] = field_value
            else:
                # Not a lookup field, keep original
                resolved_fields[field_name] = field_value
        
        return resolved_fields
    
    # ========================================================================
    # Execution State Management
    # ========================================================================
    
    def _get_simulation_key(self, module_path: str, simulation_name: str) -> str:
        """Generate unique key for simulation execution state."""
        return f"{module_path}:{simulation_name}"
    
    def get_execution_state(self, module_path: str, simulation_name: str) -> Optional[Dict[str, Any]]:
        """
        Get execution state for a simulation.
        
        Returns:
            Dict with execution state or None if not found
        """
        key = self._get_simulation_key(module_path, simulation_name)
        return self.execution_states.get(key)
    
    def _initialize_execution_state(self, module_path: str, simulation_name: str, 
                                    deployment: str, environment: str) -> Dict[str, Any]:
        """Initialize new execution state for a simulation."""
        key = self._get_simulation_key(module_path, simulation_name)
        state = {
            "simulation_key": key,
            "module_path": module_path,
            "simulation_name": simulation_name,
            "deployment": deployment,
            "environment": environment,
            "stored_records": {},  # Template variables: {variable_name: {id: guid, **fields}}
            "executed_events": [],  # List of executed event results
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        self.execution_states[key] = state
        logger.info(f"Initialized execution state for {key}")
        return state
    
    def _update_execution_state(self, key: str, event_result: Dict[str, Any], 
                                stored_record: Optional[Dict[str, Any]] = None):
        """Update execution state with new event result."""
        if key not in self.execution_states:
            logger.warning(f"Attempted to update non-existent state: {key}")
            return
        
        state = self.execution_states[key]
        state["executed_events"].append(event_result)
        
        if stored_record:
            variable_name = event_result.get("store_as")
            if variable_name:
                state["stored_records"][variable_name] = stored_record
        
        state["last_updated"] = datetime.now().isoformat()
        logger.info(f"Updated execution state for {key}, event #{event_result.get('event_id')}")
    
    def reset_execution_state(self, module_path: str, simulation_name: str) -> bool:
        """
        Reset/clear execution state for a simulation.
        
        Returns:
            True if state was reset, False if no state existed
        """
        key = self._get_simulation_key(module_path, simulation_name)
        if key in self.execution_states:
            del self.execution_states[key]
            logger.info(f"Reset execution state for {key}")
            return True
        return False
    
    def clear_all_execution_states(self):
        """Clear all execution states (for testing/cleanup)."""
        count = len(self.execution_states)
        self.execution_states.clear()
        logger.info(f"Cleared {count} execution states")
    
    # ========================================================================
    # Execution - Create Real Dataverse Records
    # ========================================================================
    
    def execute(self, module_path: str, event_stream_yaml: str, deployment: str, 
                environment: str, clear_before_run: bool = True) -> Tuple[bool, int, int, List[str], List[str], List[Dict]]:
        """
        Execute event stream against Dataverse, creating real records.
        
        Args:
            module_path: Relative path to module
            event_stream_yaml: Event stream YAML content
            deployment: Deployment name
            environment: Environment key
            clear_before_run: Whether to clear existing test records first (not yet implemented)
            
        Returns:
            Tuple of (success, total_events, executed_events, errors, warnings, event_results)
        """
        start_time = time.time()
        errors = []
        warnings = []
        
        # First validate the event stream
        try:
            valid, validation_errors, validation_warnings, _ = self.validate_event_stream(module_path, event_stream_yaml)
            
            if not valid:
                errors.extend(validation_errors)
                warnings.extend(validation_warnings)
                return False, 0, 0, errors, warnings, []
            
            warnings.extend(validation_warnings)
        except Exception as e:
            errors.append(f"Validation failed: {str(e)}")
            return False, 0, 0, errors, warnings, []
        
        # Parse event stream
        try:
            data = yaml.safe_load(event_stream_yaml)
        except yaml.YAMLError as e:
            errors.append(f"Invalid YAML: {str(e)}")
            return False, 0, 0, errors, warnings, []
        
        events = data.get("events", [])
        execution_config = data.get("execution", {})
        stop_on_error = execution_config.get("stop_on_error", True)
        
        if not events:
            errors.append("No events found in event stream")
            return False, 0, 0, errors, warnings, []
        
        # Initialize Dataverse client
        try:
            client = self._get_dataverse_client(deployment, environment)
        except Exception as e:
            errors.append(f"Failed to initialize Dataverse client: {str(e)}")
            return False, 0, 0, errors, warnings, []
        
        # Execute events
        event_results = []
        stored_records = {}  # Store created records for template resolution
        
        for event in events:
            event_start = time.time()
            event_id = event.get("event_id", "unknown")
            operation = event.get("operation", "").lower()
            entity = event.get("entity", "")
            store_as = event.get("store_as")
            fields = event.get("fields", {})
            
            event_errors = []
            
            # Resolve template variables in field values
            resolved_fields = {}
            for field_name, field_value in fields.items():
                try:
                    resolved_fields[field_name] = self._resolve_template_vars(field_value, stored_records)
                except Exception as e:
                    event_errors.append(f"Error resolving template for field '{field_name}': {str(e)}")
            
            # Resolve lookup fields (lookup: syntax to actual GUIDs)
            if not event_errors:
                try:
                    resolved_fields = self._resolve_lookup_fields(client, resolved_fields)
                except Exception as e:
                    event_errors.append(f"Error resolving lookups: {str(e)}")
                    logger.exception(f"Event {event_id}: Lookup resolution error")
            
            # Execute operation
            record_id = None
            if operation == "create" and not event_errors:
                try:
                    entity_set_name = self._entity_to_entity_set(entity)
                    
                    # Log the request details for debugging
                    logger.info(f"Creating record in {entity_set_name}")
                    logger.debug(f"Payload: {json.dumps(resolved_fields, indent=2)}")
                    
                    record_id = client.create_record(entity_set_name, resolved_fields)
                    
                    if record_id:
                        # Store record for future template references
                        if store_as:
                            stored_records[store_as] = {
                                "id": record_id,
                                **resolved_fields
                            }
                        logger.info(f"Successfully created record {record_id}")
                    else:
                        error_msg = f"Failed to create record in {entity_set_name} (no GUID returned). Check backend logs for details."
                        event_errors.append(error_msg)
                        logger.error(f"Event {event_id}: {error_msg}")
                        logger.error(f"Payload was: {json.dumps(resolved_fields, indent=2)}")
                        
                except Exception as e:
                    error_msg = f"Error creating record: {str(e)}"
                    event_errors.append(error_msg)
                    logger.exception(f"Event {event_id}: {error_msg}")
            
            elif operation == "update":
                event_errors.append("Update operation not yet implemented")
            
            elif operation == "delete":
                event_errors.append("Delete operation not yet implemented")
            
            else:
                if operation not in ["create", "update", "delete"]:
                    event_errors.append(f"Unknown operation: {operation}")
            
            # Record event result
            event_duration = time.time() - event_start
            event_result = {
                "event_id": event_id,
                "operation": operation,
                "entity": entity,
                "success": len(event_errors) == 0 and record_id is not None,
                "record_id": record_id,
                "errors": event_errors,
                "duration_seconds": event_duration
            }
            event_results.append(event_result)
            
            # Stop on error if configured
            if stop_on_error and event_errors:
                errors.append(f"Execution stopped at event {event_id} due to error")
                break
        
        # Calculate summary
        total_duration = time.time() - start_time
        success = all(r["success"] for r in event_results)
        executed_events = len([r for r in event_results if r["success"]])
        
        return success, len(events), executed_events, errors, warnings, event_results
    
    def execute_single_event(self, module_path: str, event_stream_yaml: str, event_id: int,
                            deployment: str, environment: str) -> Dict[str, Any]:
        """
        Execute a single event from an event stream.
        
        This maintains execution state across multiple single-event calls,
        allowing step-by-step debugging and testing.
        
        Args:
            module_path: Relative path to module
            event_stream_yaml: Complete event stream YAML content
            event_id: ID of the specific event to execute
            deployment: Deployment name
            environment: Environment key
            
        Returns:
            Dict with execution result for this event
        """
        start_time = time.time()
        
        # Parse event stream
        try:
            data = yaml.safe_load(event_stream_yaml)
        except yaml.YAMLError as e:
            return {
                "success": False,
                "event_id": event_id,
                "record_id": None,
                "errors": [f"Invalid YAML: {str(e)}"],
                "duration_seconds": 0.0
            }
        
        simulation_name = data.get("event_stream_name", "unknown")
        events = data.get("events", [])
        
        # Find the target event
        target_event = None
        for event in events:
            if event.get("event_id") == event_id:
                target_event = event
                break
        
        if not target_event:
            return {
                "success": False,
                "event_id": event_id,
                "record_id": None,
                "errors": [f"Event #{event_id} not found in simulation"],
                "duration_seconds": 0.0
            }
        
        # Get or initialize execution state
        state = self.get_execution_state(module_path, simulation_name)
        if not state:
            state = self._initialize_execution_state(module_path, simulation_name, deployment, environment)
        
        # Check if event already executed
        for executed in state["executed_events"]:
            if executed.get("event_id") == event_id and executed.get("success"):
                logger.info(f"Event #{event_id} already executed successfully")
                return executed
        
        # Validate deployment/environment match
        if state["deployment"] != deployment or state["environment"] != environment:
            return {
                "success": False,
                "event_id": event_id,
                "record_id": None,
                "errors": [f"State exists for different deployment/environment. Reset state to change target."],
                "duration_seconds": 0.0
            }
        
        # Initialize Dataverse client
        try:
            client = self._get_dataverse_client(deployment, environment)
        except Exception as e:
            return {
                "success": False,
                "event_id": event_id,
                "record_id": None,
                "errors": [f"Failed to initialize Dataverse client: {str(e)}"],
                "duration_seconds": 0.0
            }
        
        # Extract event details
        operation = target_event.get("operation", "").lower()
        entity = target_event.get("entity", "")
        store_as = target_event.get("store_as")
        fields = target_event.get("fields", {})
        
        event_errors = []
        stored_records = state["stored_records"]
        
        # Resolve template variables in field values
        resolved_fields = {}
        for field_name, field_value in fields.items():
            try:
                resolved_fields[field_name] = self._resolve_template_vars(field_value, stored_records)
            except Exception as e:
                event_errors.append(f"Error resolving template for field '{field_name}': {str(e)}")
        
        # Resolve lookup fields
        if not event_errors:
            try:
                resolved_fields = self._resolve_lookup_fields(client, resolved_fields)
            except Exception as e:
                event_errors.append(f"Error resolving lookups: {str(e)}")
        
        # Execute operation
        record_id = None
        if operation == "create" and not event_errors:
            try:
                entity_set_name = self._entity_to_entity_set(entity)
                logger.info(f"Executing event #{event_id}: Creating record in {entity_set_name}")
                
                record_id = client.create_record(entity_set_name, resolved_fields)
                
                if record_id:
                    logger.info(f"Event #{event_id} successfully created record {record_id}")
                else:
                    error_msg = f"Failed to create record in {entity_set_name} (no GUID returned)"
                    event_errors.append(error_msg)
                    logger.error(f"Event #{event_id}: {error_msg}")
                        
            except Exception as e:
                error_msg = f"Error creating record: {str(e)}"
                event_errors.append(error_msg)
                logger.exception(f"Event #{event_id}: {error_msg}")
        
        elif operation == "update":
            event_errors.append("Update operation not yet implemented")
        
        elif operation == "delete":
            event_errors.append("Delete operation not yet implemented")
        
        else:
            if operation not in ["create", "update", "delete"]:
                event_errors.append(f"Unknown operation: {operation}")
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Build result
        event_result = {
            "event_id": event_id,
            "operation": operation,
            "entity": entity,
            "success": len(event_errors) == 0 and record_id is not None,
            "record_id": record_id,
            "errors": event_errors,
            "duration_seconds": duration,
            "store_as": store_as,
            "timestamp": datetime.now().isoformat()
        }
        
        # Update state if successful
        if event_result["success"] and store_as:
            stored_record = {
                "id": record_id,
                **resolved_fields
            }
            self._update_execution_state(state["simulation_key"], event_result, stored_record)
        elif event_result["success"]:
            self._update_execution_state(state["simulation_key"], event_result)
        
        return event_result
