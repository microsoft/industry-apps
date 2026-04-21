"""
Record Operations Service

Handles creating and updating records in Dataverse via Web API.
Builds payloads with proper field mapping, choice value conversion,
and OData binding for lookups.
"""

from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import re
from datetime import datetime

from services.simulation_parser import DataModelLoader
from services.execution_context import ExecutionContext, TemplateResolutionError


class PayloadBuildError(Exception):
    """Raised when a payload cannot be built"""
    
    def __init__(self, field: str, reason: str):
        self.field = field
        self.reason = reason
        super().__init__(f"Cannot build payload for field '{field}': {reason}")


class RecordOperations:
    """
    Builds Web API payloads and handles record creation/update operations.
    
    Responsibilities:
    - Map display names to schema names
    - Convert choice labels to numeric values
    - Format field values (dates, booleans, numbers)
    - Build OData bindings for lookups
    - Resolve template variables using execution context
    """
    
    def __init__(self, module_path: Path, data_loader: Optional[DataModelLoader] = None):
        """
        Initialize record operations.
        
        Args:
            module_path: Path to module directory
            data_loader: Optional pre-loaded DataModelLoader (will create if not provided)
        """
        self.module_path = module_path
        
        if data_loader is None:
            self.data_loader = DataModelLoader(module_path)
            self.data_loader.load()
        else:
            self.data_loader = data_loader
    
    def get_field_info(self, table_name: str, schema_name: str) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        Get the field information from data model.
        
        Args:
            table_name: Table display name or schema name
            schema_name: Field schema name
            
        Returns:
            Tuple of (field_type, display_name, optionset_name) or None
        """
        field_info = self.data_loader.get_table_field(table_name, schema_name)
        if field_info:
            # field_info is (display_name, field_type, optionset_name)
            return field_info[1], field_info[0], field_info[2]  # field_type, display_name, optionset_name
        return None
    
    def convert_choice_value(self, field_schema_name: str, label: str) -> int:
        """
        Convert choice label to numeric value.
        
        Args:
            field_schema_name: Schema name of the choice field
            label: Display label (e.g., "Civil", "Active")
            
        Returns:
            Numeric value for the choice
            
        Raises:
            PayloadBuildError: If choice value not found
        """
        value = self.data_loader.get_choice_value(field_schema_name, label)
        if value is None:
            raise PayloadBuildError(
                field_schema_name,
                f"Choice value '{label}' not found in choices.yaml"
            )
        return value
    
    def format_boolean_value(self, value: str) -> bool:
        """
        Convert string to boolean.
        
        Args:
            value: String like "Yes", "No", "True", "False", "1", "0"
            
        Returns:
            Boolean value
        """
        value_lower = value.lower().strip()
        
        if value_lower in ["yes", "true", "1"]:
            return True
        elif value_lower in ["no", "false", "0"]:
            return False
        else:
            # Default to treating any non-empty string as True
            return bool(value)
    
    def format_datetime_value(self, value: str) -> str:
        """
        Ensure datetime is in ISO 8601 format for Web API.
        
        Args:
            value: Datetime string
            
        Returns:
            ISO 8601 formatted string
        """
        # If already looks like ISO 8601, return as-is
        if re.match(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', value):
            return value
        
        # Try to parse and format
        try:
            # Handle date-only format
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return f"{value}T00:00:00Z"
            
            # Return as-is if we can't confidently convert
            return value
        except Exception:
            return value
    
    def format_number_value(self, value: str, field_type: str) -> float:
        """
        Convert string to number.
        
        Args:
            value: String representation of number
            field_type: Field type (for context)
            
        Returns:
            Float or int value
        """
        try:
            # Try to detect if it should be an integer
            if '.' not in value:
                return int(value)
            return float(value)
        except ValueError:
            raise PayloadBuildError(value, f"Cannot convert '{value}' to number for {field_type}")
    
    def build_lookup_binding(self, plural_name: str, record_id: str) -> str:
        """
        Build OData binding reference for a lookup field.
        
        Args:
            plural_name: Plural name of the target entity (e.g., "contacts", "appbase_courtcases")
            record_id: GUID of the record to reference
            
        Returns:
            OData binding string like "/contacts(guid)"
        """
        # Remove braces if present in GUID
        clean_id = record_id.strip('{}')
        return f"/{plural_name}({clean_id})"
    
    def resolve_lookup_field(self, value: str, field_type: str, context: ExecutionContext, 
                            step: int) -> str:
        """
        Resolve a lookup field value to an OData binding.
        
        Args:
            value: Field value (template variable or literal)
            field_type: Field type string like "Lookup (Contact)"
            context: Execution context for template resolution
            step: Current step number
            
        Returns:
            OData binding string
            
        Raises:
            PayloadBuildError: If lookup cannot be resolved
        """
        # Extract target entity from field type: "Lookup (Contact)" -> "Contact"
        match = re.match(r'Lookup \((.+?)\)', field_type)
        if not match:
            raise PayloadBuildError(
                value,
                f"Invalid lookup field type format: '{field_type}'"
            )
        
        target_entity = match.group(1)
        
        # Check if value contains template variable
        if context.has_template_variables(value):
            # Resolve the template variable to get the ID
            try:
                record_id = context.resolve_template_string(value, step)
            except TemplateResolutionError as e:
                raise PayloadBuildError(value, f"Template resolution failed: {e.reason}")
        else:
            # Check if it looks like a GUID (already resolved)
            guid_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
            if re.match(guid_pattern, value.lower()):
                # It's already a GUID, use it directly
                record_id = value
            else:
                # Literal value - would need to query by name
                raise PayloadBuildError(
                    value,
                    f"Literal lookup value '{value}' requires name-based lookup (not yet implemented)"
                )
        
        # Get plural name for target entity
        plural_name = self.data_loader.get_plural_name(target_entity)
        if not plural_name:
            # If not found in data models, try to derive it
            plural_name = target_entity.lower() + 's'
        
        return self.build_lookup_binding(plural_name, record_id)
    
    def build_field_value(self, field_schema_name: str, value: str, field_type: str,
                         context: ExecutionContext, step: int, optionset_name: Optional[str] = None) -> Any:
        """
        Build the appropriate value for a field based on its type.
        
        Args:
            field_schema_name: Schema name of the field
            value: Raw value from simulation
            field_type: Field type from data model
            context: Execution context for template resolution
            step: Current step number
            optionset_name: Optional optionset name for choice fields
            
        Returns:
            Properly formatted value for Web API
        """
        # First, resolve any template variables in the value
        if context.has_template_variables(value):
            value = context.resolve_template_string(value, step)
        
        # Handle based on field type
        if field_type.startswith("Choice"):
            # Use optionset_name if provided, otherwise fall back to field_schema_name
            lookup_name = optionset_name if optionset_name else field_schema_name
            return self.convert_choice_value(lookup_name, value)
        
        elif field_type.startswith("Lookup"):
            # Return the full binding string (will be used with @odata.bind suffix)
            return self.resolve_lookup_field(value, field_type, context, step)
        
        elif field_type in ["Date Time", "DateTime"]:
            return self.format_datetime_value(value)
        
        elif field_type == "Yes/No":
            return self.format_boolean_value(value)
        
        elif field_type in ["Whole Number", "Decimal", "Currency", "Float"]:
            return self.format_number_value(value, field_type)
        
        elif field_type in ["Text", "Memo", "Email", "Phone", "URL"]:
            return value  # Return as string
        
        else:
            # Unknown type - return as-is
            return value
    
    def build_payload(self, table_name: str, fields: Dict[str, Any], 
                     context: ExecutionContext, step: int) -> Dict[str, Any]:
        """
        Build a Web API payload from field dictionary.
        
        Args:
            table_name: Table display name or schema name
            fields: Dictionary of {field_schema_name: value}
            context: Execution context for template resolution
            step: Current step number
            
        Returns:
            Dictionary ready for Web API POST/PATCH
            
        Raises:
            PayloadBuildError: If payload cannot be built
        """
        payload = {}
        
        for field_schema_name, value in fields.items():
            # Get field info from data model
            field_info = self.get_field_info(table_name, field_schema_name)
            
            if not field_info:
                # Field not found in data model - might be system field or external entity
                # Use it anyway with minimal processing
                if context.has_template_variables(str(value)):
                    value = context.resolve_template_string(str(value), step)
                payload[field_schema_name] = value
                continue
            
            field_type, field_display_name, optionset_name = field_info
            
            # Build the appropriate value
            field_value = self.build_field_value(field_schema_name, str(value), field_type, context, step, optionset_name)
            
            # For lookup fields, use @odata.bind suffix
            if field_type.startswith("Lookup"):
                payload[f"{field_schema_name}@odata.bind"] = field_value
            else:
                payload[field_schema_name] = field_value
        
        return payload
    
    def create_record_payload(self, action: Dict[str, Any], context: ExecutionContext, 
                              step: int) -> Tuple[str, Dict[str, Any]]:
        """
        Build payload for creating a new record.
        
        Args:
            action: Action dictionary from simulation
            context: Execution context
            step: Current step number
            
        Returns:
            Tuple of (entity_plural_name, payload)
        """
        table_name = action.get("table", "")
        schema_name = action.get("schema_name", "")
        fields = action.get("fields", {})
        
        # Get plural name for the entity
        plural_name = self.data_loader.get_plural_name(table_name)
        if not plural_name:
            # Try using schema name
            plural_name = self.data_loader.get_plural_name(schema_name)
        
        if not plural_name:
            # Fall back to simple pluralization
            plural_name = schema_name.lower() + 's' if schema_name else table_name.lower() + 's'
        
        # Build the payload
        payload = self.build_payload(table_name, fields, context, step)
        
        return plural_name, payload
    
    def update_record_payload(self, action: Dict[str, Any], context: ExecutionContext,
                             step: int) -> Tuple[str, str, Dict[str, Any]]:
        """
        Build payload for updating an existing record.
        
        Args:
            action: Action dictionary from simulation
            context: Execution context
            step: Current step number
            
        Returns:
            Tuple of (entity_plural_name, record_id, payload)
        """
        table_name = action.get("table", "")
        schema_name = action.get("schema_name", "")
        fields = action.get("fields", {})
        record_reference = action.get("record_reference", "")
        
        # Resolve the record reference to get ID
        if not record_reference:
            raise PayloadBuildError("record_reference", "Missing record_reference for update action")
        
        record_id = context.resolve_template_string(record_reference, step)
        
        # Get plural name
        plural_name = self.data_loader.get_plural_name(table_name)
        if not plural_name:
            plural_name = self.data_loader.get_plural_name(schema_name)
        if not plural_name:
            plural_name = schema_name.lower() + 's' if schema_name else table_name.lower() + 's'
        
        # Build the payload
        payload = self.build_payload(table_name, fields, context, step)
        
        return plural_name, record_id, payload


class DryRunRecordOperations(RecordOperations):
    """
    Record operations for dry-run mode.
    
    Simulates Web API calls without actually making them.
    Returns mock responses for validation purposes.
    """
    
    def __init__(self, module_path: Path, data_loader: Optional[DataModelLoader] = None):
        super().__init__(module_path, data_loader)
        self.simulated_operations: List[Dict[str, Any]] = []
    
    def simulate_create(self, action: Dict[str, Any], context: ExecutionContext,
                       step: int) -> Dict[str, Any]:
        """
        Simulate creating a record.
        
        Args:
            action: Action dictionary from simulation
            context: Execution context (must be DryRunContext)
            step: Current step number
            
        Returns:
            Mock Web API response
        """
        from services.execution_context import DryRunContext
        
        plural_name, payload = self.create_record_payload(action, context, step)
        
        # Record the operation
        self.simulated_operations.append({
            "action": "create",
            "entity": plural_name,
            "step": step,
            "payload": payload,
            "store_as": action.get("store_as")
        })
        
        # If context is DryRunContext, use its simulate method
        if isinstance(context, DryRunContext):
            return context.simulate_record_creation(
                store_as=action.get("store_as", "unnamed"),
                table=action.get("table", ""),
                fields=payload,
                step=step
            )
        else:
            # Fallback for regular context
            import uuid
            mock_id = str(uuid.uuid4())
            return {
                "id": mock_id,
                "@odata.id": f"/{plural_name}({mock_id})",
                **payload
            }
    
    def simulate_update(self, action: Dict[str, Any], context: ExecutionContext,
                       step: int) -> Dict[str, Any]:
        """
        Simulate updating a record.
        
        Args:
            action: Action dictionary from simulation
            context: Execution context
            step: Current step number
            
        Returns:
            Mock Web API response
        """
        plural_name, record_id, payload = self.update_record_payload(action, context, step)
        
        # Record the operation
        self.simulated_operations.append({
            "action": "update",
            "entity": plural_name,
            "record_id": record_id,
            "step": step,
            "payload": payload
        })
        
        # Return mock response (update typically returns 204 No Content, but we'll return data)
        return {
            "id": record_id,
            "@odata.id": f"/{plural_name}({record_id})",
            **payload
        }
    
    def get_simulation_summary(self) -> Dict[str, Any]:
        """Get summary of simulated operations"""
        return {
            "total_operations": len(self.simulated_operations),
            "creates": sum(1 for op in self.simulated_operations if op["action"] == "create"),
            "updates": sum(1 for op in self.simulated_operations if op["action"] == "update"),
            "operations": self.simulated_operations
        }
