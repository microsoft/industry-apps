"""
Simulation Parser and Validator Service

Parses simulation YAML files and validates:
- Table references exist in data models
- Field references exist on tables
- Template variables reference valid store_as names
- Choice values exist in choices.yaml
- Field types match expected formats
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import yaml
import re
from datetime import datetime


class ValidationError:
    """Represents a validation error with context"""
    
    def __init__(self, step: int, action_index: int, field: str, message: str, severity: str = "error"):
        self.step = step
        self.action_index = action_index
        self.field = field
        self.message = message
        self.severity = severity  # "error" or "warning"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "action_index": self.action_index,
            "field": self.field,
            "message": self.message,
            "severity": self.severity
        }


class ValidationResult:
    """Result of simulation validation"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
        self.is_valid = True
        self.metadata = {}
    
    def add_error(self, step: int, action_index: int, field: str, message: str):
        self.errors.append(ValidationError(step, action_index, field, message, "error"))
        self.is_valid = False
    
    def add_warning(self, step: int, action_index: int, field: str, message: str):
        self.warnings.append(ValidationError(step, action_index, field, message, "warning"))
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "metadata": self.metadata
        }


class DataModelLoader:
    """Loads and caches data models for a module"""
    
    def __init__(self, module_path: Path):
        self.module_path = module_path
        self.data_models_path = module_path / "design" / "data-models"
        self.tables: Dict[str, Dict[str, Any]] = {}
        self.choices: Dict[str, Dict[str, int]] = {}
        self.loaded = False
    
    def load(self) -> bool:
        """Load all data models and choices"""
        if self.loaded:
            return True
        
        if not self.data_models_path.exists():
            return False
        
        # Load choices.yaml
        choices_path = self.data_models_path / "choices.yaml"
        if choices_path.exists():
            try:
                with open(choices_path, 'r', encoding='utf-8') as f:
                    self.choices = yaml.safe_load(f) or {}
                    # Remove comments if present
                    self.choices = {k: v for k, v in self.choices.items() if isinstance(v, dict)}
            except Exception as e:
                print(f"Error loading choices.yaml: {e}")
                return False
        
        # Load all table YAML files
        for table_file in self.data_models_path.glob("*.yaml"):
            if table_file.name == "choices.yaml":
                continue
            
            try:
                with open(table_file, 'r', encoding='utf-8') as f:
                    table_data = yaml.safe_load(f)
                    if table_data and "name" in table_data and "schema_name" in table_data:
                        # Store by both display name and schema name for lookup flexibility
                        self.tables[table_data["name"]] = table_data
                        self.tables[table_data["schema_name"]] = table_data
            except Exception as e:
                print(f"Error loading {table_file.name}: {e}")
                continue
        
        self.loaded = True
        return True
    
    def get_table(self, name: str) -> Optional[Dict[str, Any]]:
        """Get table by display name or schema name"""
        return self.tables.get(name)
    
    def parse_field_string(self, field_str: str) -> Optional[Tuple[str, str, str, Optional[str]]]:
        """
        Parse field string format: "Display Name: Type; schema_name" or "Display Name: Type; schema_name; optionset=name"
        Returns: (display_name, field_type, schema_name, optionset_name) or None if invalid
        """
        # Match pattern with optional optionset: "Display Name: Type; schema_name; optionset=name"
        match = re.match(r'^(.+?):\s*(.+?);\s*(\S+)(?:;\s*optionset=(\S+))?$', field_str.strip())
        if match:
            display_name = match.group(1).strip()
            field_type = match.group(2).strip()
            schema_name = match.group(3).strip()
            optionset_name = match.group(4).strip() if match.group(4) else None
            return display_name, field_type, schema_name, optionset_name
        return None
    
    def get_table_field(self, table_name: str, field_schema_name: str) -> Optional[Tuple[str, str, Optional[str]]]:
        """
        Get field info from table by schema name.
        Returns: (display_name, field_type, optionset_name) or None if not found
        """
        table = self.get_table(table_name)
        if not table or "fields" not in table:
            return None
        
        for field_str in table["fields"]:
            parsed = self.parse_field_string(field_str)
            if parsed and parsed[2] == field_schema_name:
                return parsed[0], parsed[1], parsed[3]  # display_name, field_type, optionset_name
        
        return None
    
    def get_choice_value(self, field_schema_name: str, label: str) -> Optional[int]:
        """Get numeric value for a choice field label"""
        if field_schema_name not in self.choices:
            return None
        
        choice_map = self.choices[field_schema_name]
        return choice_map.get(label)
    
    def get_plural_name(self, table_name: str) -> Optional[str]:
        """Get plural name for Web API endpoint"""
        table = self.get_table(table_name)
        if table:
            return table.get("plural_name")
        return None


class SimulationParser:
    """Parses and validates simulation YAML files"""
    
    def __init__(self, simulation_path: Path, module_path: Path):
        self.simulation_path = simulation_path
        self.module_path = module_path
        self.data_loader = DataModelLoader(module_path)
        self.simulation_data: Dict[str, Any] = {}
        self.template_var_pattern = re.compile(r'\{\{([^}]+)\}\}')
    
    def load_simulation(self) -> bool:
        """Load simulation YAML file"""
        if not self.simulation_path.exists():
            return False
        
        try:
            with open(self.simulation_path, 'r', encoding='utf-8') as f:
                self.simulation_data = yaml.safe_load(f)
            return True
        except Exception as e:
            print(f"Error loading simulation: {e}")
            return False
    
    def parse_template_variables(self, text: str) -> List[str]:
        """Extract template variable names from text (e.g., {{record.field}})"""
        if not isinstance(text, str):
            return []
        
        matches = self.template_var_pattern.findall(text)
        return matches
    
    def validate(self) -> ValidationResult:
        """Validate the simulation against data models"""
        result = ValidationResult()
        
        # Load simulation
        if not self.load_simulation():
            result.add_error(0, 0, "file", f"Failed to load simulation file: {self.simulation_path}")
            return result
        
        # Load data models
        if not self.data_loader.load():
            result.add_error(0, 0, "data_models", f"Failed to load data models from: {self.module_path}")
            return result
        
        # Track store_as names to validate template variables
        available_vars = set()
        
        # Validate steps
        steps = self.simulation_data.get("steps", [])
        if not steps:
            result.add_error(0, 0, "steps", "No steps found in simulation")
            return result
        
        for step_data in steps:
            step_num = step_data.get("step", 0)
            actions = step_data.get("actions", [])
            
            for action_idx, action in enumerate(actions):
                self._validate_action(action, step_num, action_idx, available_vars, result)
                
                # Track store_as for future template variable validation
                if "store_as" in action:
                    available_vars.add(action["store_as"])
        
        # Add metadata
        result.metadata = {
            "simulation_name": self.simulation_data.get("execution_name", ""),
            "module": self.simulation_data.get("module", ""),
            "steps_count": len(steps),
            "available_vars": list(available_vars)
        }
        
        return result
    
    def _validate_action(self, action: Dict[str, Any], step: int, action_idx: int, 
                        available_vars: set, result: ValidationResult):
        """Validate a single action"""
        
        # Check table exists
        table_name = action.get("table", "")
        schema_name = action.get("schema_name", "")
        
        if not table_name:
            result.add_error(step, action_idx, "table", "Missing table name")
            return
        
        table = self.data_loader.get_table(table_name)
        if not table:
            result.add_error(step, action_idx, "table", f"Table '{table_name}' not found in data models")
            return
        
        # Verify schema_name matches
        if schema_name and table.get("schema_name") != schema_name:
            result.add_warning(step, action_idx, "schema_name", 
                             f"Schema name mismatch: expected '{table.get('schema_name')}', got '{schema_name}'")
        
        # Validate fields (now dictionary format: {schema_name: value})
        fields = action.get("fields", {})
        if not isinstance(fields, dict):
            result.add_error(step, action_idx, "fields", 
                           f"Fields must be a dictionary (got {type(fields).__name__})")
            return
            
        for field_schema_name, field_value in fields.items():
            self._validate_field(field_schema_name, field_value, table_name, step, action_idx, available_vars, result)
    
    def _validate_field(self, field_schema_name: str, field_value: Any, table_name: str, step: int, action_idx: int,
                       available_vars: set, result: ValidationResult):
        """Validate a single field entry (dictionary format)"""
        
        # Check field exists on table
        field_info = self.data_loader.get_table_field(table_name, field_schema_name)
        if not field_info:
            result.add_error(step, action_idx, field_schema_name, 
                           f"Field '{field_schema_name}' not found on table '{table_name}'")
            return
        
        expected_display_name, field_type, optionset_name = field_info
        
        # Convert value to string for template variable parsing
        value_str = str(field_value) if field_value is not None else ""
        
        # Validate template variables in value
        template_vars = self.parse_template_variables(value_str)
        for var in template_vars:
            # Parse variable: "record_name.field" or just "record_name.id"
            var_parts = var.split(".", 1)
            var_name = var_parts[0]
            
            if var_name not in available_vars:
                result.add_error(step, action_idx, field_schema_name,
                               f"Template variable '{{{{{var}}}}}' references undefined store_as name '{var_name}'")
        
        # Validate choice values
        if "Choice" in field_type and not template_vars:
            # This is a choice field with a literal value
            base_field_type = field_type.split("(")[0].strip()
            if base_field_type == "Choice":
                # Use optionset_name if available, otherwise fall back to field_schema_name
                lookup_name = optionset_name if optionset_name else field_schema_name
                choice_value = self.data_loader.get_choice_value(lookup_name, field_value)
                if choice_value is None:
                    result.add_error(step, action_idx, field_schema_name,
                                   f"Choice value '{field_value}' not found for field '{lookup_name}'")
        
        # Validate lookup format
        if "Lookup" in field_type and not template_vars:
            # Lookup fields should either have template variables or be validated separately
            # For now, just warn if it's a plain string (might need to be looked up)
            if not field_value.startswith("{{"):
                result.add_warning(step, action_idx, field_schema_name,
                                 f"Lookup field '{field_schema_name}' has literal value - will require lookup by name")


def validate_simulation(simulation_path: Path, module_path: Path) -> Dict[str, Any]:
    """
    Validate a simulation file against data models.
    
    Args:
        simulation_path: Path to simulation YAML file
        module_path: Path to module directory
        
    Returns:
        Validation result dictionary
    """
    parser = SimulationParser(simulation_path, module_path)
    result = parser.validate()
    return result.to_dict()
