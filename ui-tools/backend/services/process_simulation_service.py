"""
Business logic for Process Simulation operations.

This service handles data model generation, file operations, validation,
dry-run simulation, and event stream execution against Dataverse.
"""

import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import sys

# Add scripts directory to path for imports
scripts_dir = Path(__file__).parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))

from data_model_generator import save_data_models


class ProcessSimulationService:
    """Service for process simulation operations."""
    
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
                fields = []
                for field_line in table_data.get("fields", []):
                    # Parse format: "Display Name: Type; schema_name"
                    # or "Display Name: Lookup (Target); schema_name"
                    parts = field_line.split(";")
                    if len(parts) != 2:
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
        
        # Build entity lookup
        entities_by_name = {entity["logical_name"]: entity for entity in data_models.get("entities", [])}
        
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
            
            # Check entity exists
            if entity_name not in entities_by_name:
                event_errors.append(f"Unknown entity: {entity_name}")
            else:
                entity = entities_by_name[entity_name]
                entity_fields = {f["logical_name"]: f for f in entity.get("fields", [])}
                
                # Check fields
                for field_name, field_value in fields.items():
                    # Skip OData bind fields  (lookups)
                    if field_name.endswith("@odata.bind"):
                        base_field = field_name.replace("@odata.bind", "")
                        if base_field not in entity_fields:
                            event_warnings.append(f"Lookup field not in schema: {base_field}")
                        continue
                    
                    # Skip system fields
                    if field_name in ["statuscode", "statecode"]:
                        continue
                    
                    # Check if field exists
                    if field_name not in entity_fields:
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
    # Execution (placeholder - requires Dataverse client integration)
    # ========================================================================
    
    def execute(self, module_path: str, event_stream_yaml: str, deployment: str, environment: str, clear_before_run: bool = True):
        """
        Execute event stream against Dataverse.
        
        NOTE: This is a placeholder. Full implementation requires integrating
        with the Dataverse client to actually create/update records.
        
        Args:
            module_path: Relative path to module
            event_stream_yaml: Event stream YAML content
            deployment: Deployment name
            environment: Environment name
            clear_before_run: Whether to clear existing test records first
            
        Returns:
            Tuple of execution results
        """
        # For now, return dry-run results
        # TODO: Integrate with Dataverse client to execute actual operations
        return self.dry_run(module_path, event_stream_yaml)
