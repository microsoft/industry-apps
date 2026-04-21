"""
Execution Context Manager

Manages execution state during simulation execution, including:
- Storing created records by store_as name
- Resolving template variables ({{record.field}})
- Tracking execution progress
- Providing resolved values for Web API calls
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime


class TemplateResolutionError(Exception):
    """Raised when a template variable cannot be resolved"""
    
    def __init__(self, variable: str, reason: str, step: int = None):
        self.variable = variable
        self.reason = reason
        self.step = step
        super().__init__(f"Cannot resolve template variable '{{{{{variable}}}}}': {reason}")


class ExecutionContext:
    """
    Manages execution state and template variable resolution.
    
    Stores created records and resolves template variables like:
    - {{case_record.id}} -> GUID of created record
    - {{plaintiff_contact.emailaddress1}} -> Email field value
    - {{case_record}} -> Full record object (for debugging)
    """
    
    def __init__(self):
        # Store records by their store_as name
        self.records: Dict[str, Dict[str, Any]] = {}
        
        # Track execution progress
        self.current_step = 0
        self.completed_steps: List[int] = []
        self.execution_log: List[Dict[str, Any]] = []
        
        # Template variable regex pattern
        self.template_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    def store_record(self, store_as: str, record_data: Dict[str, Any], step: int = None):
        """
        Store a created record for future reference.
        
        Args:
            store_as: Variable name to store under
            record_data: Full record data from Web API response
            step: Optional step number for tracking
        """
        self.records[store_as] = record_data
        
        # Log the storage
        self.execution_log.append({
            "action": "store_record",
            "store_as": store_as,
            "step": step,
            "timestamp": datetime.utcnow().isoformat(),
            "record_id": record_data.get("id") or record_data.get("@odata.id")
        })
    
    def has_record(self, store_as: str) -> bool:
        """Check if a record exists by store_as name"""
        return store_as in self.records
    
    def get_record(self, store_as: str) -> Optional[Dict[str, Any]]:
        """Get a stored record by store_as name"""
        return self.records.get(store_as)
    
    def parse_template_variable(self, variable: str) -> tuple[str, Optional[str]]:
        """
        Parse a template variable into record name and field.
        
        Args:
            variable: Variable string like "case_record.id" or "plaintiff_contact.emailaddress1"
            
        Returns:
            Tuple of (record_name, field_name) where field_name may be None
            
        Examples:
            "case_record.id" -> ("case_record", "id")
            "plaintiff_contact" -> ("plaintiff_contact", None)
            "contact.address1_line1" -> ("contact", "address1_line1")
        """
        parts = variable.split(".", 1)
        record_name = parts[0].strip()
        field_name = parts[1].strip() if len(parts) > 1 else None
        
        return record_name, field_name
    
    def resolve_variable(self, variable: str, step: int = None) -> Any:
        """
        Resolve a template variable to its value.
        
        Args:
            variable: Variable string like "case_record.id"
            step: Current step number for error reporting
            
        Returns:
            Resolved value (string, dict, etc.)
            
        Raises:
            TemplateResolutionError: If variable cannot be resolved
        """
        record_name, field_name = self.parse_template_variable(variable)
        
        # Check if record exists
        if not self.has_record(record_name):
            raise TemplateResolutionError(
                variable,
                f"Record '{record_name}' not found in context. Available: {list(self.records.keys())}",
                step
            )
        
        record = self.get_record(record_name)
        
        # If no field specified, return full record
        if field_name is None:
            return record
        
        # Resolve field value
        if field_name in record:
            return record[field_name]
        
        # Check for common variations
        # Web API often returns fields with different casing or @odata annotations
        
        # Try lowercase
        field_lower = field_name.lower()
        for key in record:
            if key.lower() == field_lower:
                return record[key]
        
        # Special case for 'id' - check multiple possible locations
        if field_name.lower() == "id":
            if "id" in record:
                return record["id"]
            if "@odata.id" in record:
                # Extract GUID from @odata.id like "/appbase_courtcases(guid)"
                odata_id = record["@odata.id"]
                match = re.search(r'\(([a-f0-9-]+)\)', odata_id)
                if match:
                    return match.group(1)
                return odata_id
            if "activityid" in record:  # Some entities use specific ID fields
                return record["activityid"]
            if "contactid" in record:
                return record["contactid"]
            if "accountid" in record:
                return record["accountid"]
        
        # Field not found
        raise TemplateResolutionError(
            variable,
            f"Field '{field_name}' not found in record '{record_name}'. Available fields: {list(record.keys())}",
            step
        )
    
    def resolve_template_string(self, text: str, step: int = None) -> str:
        """
        Resolve all template variables in a string.
        
        Args:
            text: Text containing template variables like "Case {{case_record.id}}"
            step: Current step number for error reporting
            
        Returns:
            Text with all variables resolved
            
        Raises:
            TemplateResolutionError: If any variable cannot be resolved
        """
        if not isinstance(text, str):
            return text
        
        def replace_match(match):
            variable = match.group(1)
            value = self.resolve_variable(variable, step)
            return str(value)
        
        return self.template_pattern.sub(replace_match, text)
    
    def has_template_variables(self, text: str) -> bool:
        """Check if text contains template variables"""
        if not isinstance(text, str):
            return False
        return bool(self.template_pattern.search(text))
    
    def extract_template_variables(self, text: str) -> List[str]:
        """Extract all template variable names from text"""
        if not isinstance(text, str):
            return []
        return self.template_pattern.findall(text)
    
    def mark_step_complete(self, step: int):
        """Mark a step as completed"""
        if step not in self.completed_steps:
            self.completed_steps.append(step)
        self.current_step = step
        
        self.execution_log.append({
            "action": "step_complete",
            "step": step,
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get summary of execution state"""
        return {
            "total_records_created": len(self.records),
            "record_names": list(self.records.keys()),
            "completed_steps": self.completed_steps,
            "current_step": self.current_step,
            "log_entries": len(self.execution_log)
        }
    
    def clear(self):
        """Clear all execution state"""
        self.records.clear()
        self.completed_steps.clear()
        self.execution_log.clear()
        self.current_step = 0


class DryRunContext(ExecutionContext):
    """
    Execution context for dry-run mode.
    
    In dry-run mode, we simulate record creation with mock IDs
    and track what would be created without making actual API calls.
    """
    
    def __init__(self):
        super().__init__()
        self.mock_id_counter = 1000
        self.simulated_records: List[Dict[str, Any]] = []
    
    def generate_mock_id(self) -> str:
        """Generate a mock GUID for dry-run mode"""
        import uuid
        return str(uuid.uuid4())
    
    def simulate_record_creation(self, store_as: str, table: str, fields: Dict[str, Any], step: int = None) -> Dict[str, Any]:
        """
        Simulate record creation with mock data.
        
        Args:
            store_as: Variable name to store under
            table: Table name
            fields: Field values that would be sent to API
            step: Current step number
            
        Returns:
            Mock record data
        """
        # Generate mock ID
        mock_id = self.generate_mock_id()
        
        # Create mock record (simulating Web API response)
        mock_record = {
            "id": mock_id,
            "@odata.id": f"/{table.lower().replace(' ', '')}s({mock_id})",
            "@odata.context": f"$metadata#{table}/$entity",
            **fields  # Include all the fields that would be created
        }
        
        # Store in context
        self.store_record(store_as, mock_record, step)
        
        # Track for dry-run report
        self.simulated_records.append({
            "store_as": store_as,
            "table": table,
            "mock_id": mock_id,
            "step": step,
            "field_count": len(fields)
        })
        
        return mock_record
    
    def get_dry_run_summary(self) -> Dict[str, Any]:
        """Get summary of dry-run simulation"""
        summary = self.get_execution_summary()
        summary["simulated_records"] = self.simulated_records
        summary["dry_run_mode"] = True
        return summary


def create_execution_context(dry_run: bool = False) -> ExecutionContext:
    """
    Factory function to create appropriate execution context.
    
    Args:
        dry_run: If True, creates DryRunContext for simulation
        
    Returns:
        ExecutionContext or DryRunContext instance
    """
    if dry_run:
        return DryRunContext()
    return ExecutionContext()
