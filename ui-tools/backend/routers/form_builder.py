"""
Form Builder Router - API endpoints for form building operations.

This module contains all the form builder endpoints for:
- Listing modules and entities
- Extracting fields from entities
- Generating YAML templates
- Validating YAML configurations
- Building forms from YAML
"""

from fastapi import APIRouter
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import yaml

# Import from parent (backend) directory
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import PROJECT_ROOT
from models import (
    ListEntitiesRequest,
    ExtractFieldsRequest,
    ValidateYamlRequest,
    BuildFormRequest,
    ExtractAllEntitiesRequest,
    ExtractSingleEntityRequest,
    BuildAllFormsRequest,
    AddQuickCreateSectionsRequest,
    UpdateQuickCreateSectionRequest,
    BuildQuickCreateRequest,
    BuildAllQuickCreateFormsRequest
)

# Import scripts for entity/form operations
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from entity_schema_reader import read_entity_definition, generate_yaml_template
from formxml_parser import FormXmlParser
from quickcreate_builder import (
    create_quickcreate_form_files,
    get_smart_default_fields
)

# Import validation service
from services.form_builder_service import validate_yaml_field_references

# Import helper function from utils
from utils import read_solution_display_name


router = APIRouter(prefix="/api/formbuilder", tags=["Form Builder"])


@router.get("/list-modules")
async def list_modules_for_formbuilder():
    """
    List all modules in the repository for form building.
    
    Scans the repository root for module directories that contain
    src/Entities folders.
    """
    try:
        modules = []
        
        # Scan common module categories
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


@router.post("/list-entities")
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


@router.post("/extract-fields")
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


@router.post("/extract-all-entities")
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


@router.post("/extract-single-entity")
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


@router.get("/list-layouts")
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


@router.post("/validate-yaml")
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
                    
                    # Add system fields that are always valid
                    valid_field_names.add('ownerid')
                    # Add entity name field (e.g., appbase_name for appbase_* entities)
                    if '_' in config['entity']:
                        entity_prefix = config['entity'].split('_')[0]
                        valid_field_names.add(f"{entity_prefix}_name")
                    
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
                                    
                                    # Validate fields in 'fields' mode
                                    if 'fields' in section and isinstance(section['fields'], list):
                                        for field_name in section['fields']:
                                            if field_name not in valid_field_names:
                                                errors.append(f"Field '{field_name}' does not exist in entity '{config['entity']}'")
                                    
                                    # Validate fields in 'rows' mode
                                    if 'rows' in section and isinstance(section['rows'], list):
                                        for row_idx, row_spec in enumerate(section['rows']):
                                            if not isinstance(row_spec, list):
                                                errors.append(f"Tab {tab_idx + 1}, Section {section_idx + 1}, Row {row_idx + 1} is not a list")
                                                continue
                                            
                                            for cell_spec in row_spec:
                                                field_name = None
                                                
                                                # Extract field name from cell spec
                                                if isinstance(cell_spec, str):
                                                    field_name = cell_spec
                                                elif isinstance(cell_spec, dict) and 'field' in cell_spec:
                                                    field_name = cell_spec['field']
                                                
                                                # Validate field exists (skip null placeholders)
                                                if field_name and field_name != 'null' and field_name not in valid_field_names:
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


@router.post("/build-form")
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
        
        # VALIDATE FIELD REFERENCES: Check that all fields used in tabs exist in the YAML header
        validation_errors = validate_yaml_field_references(yaml_content, config)
        if validation_errors:
            error_msg = "Invalid field references found:\n" + "\n".join(f"  • {err}" for err in validation_errors)
            return {
                "success": False,
                "error": error_msg,
                "validation_errors": validation_errors
            }
        
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


@router.post("/build-all-forms")
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
                
                # VALIDATE FIELD REFERENCES: Check that all fields used in tabs exist in the YAML header
                validation_errors = validate_yaml_field_references(yaml_content, config)
                if validation_errors:
                    error_msg = "Invalid field references: " + "; ".join(validation_errors)
                    results.append({
                        "entity": entity_name,
                        "success": False,
                        "error": error_msg,
                        "validation_errors": validation_errors
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
                                section_name=section_label,
                                rows=rows_spec,
                                field_metadata=field_metadata,
                                managed_path=managed_path if managed_path.exists() else None,
                                create_backup=False,
                                skip_if_exists=False
                            )
                        elif fields:
                            entity_xml = entity_dir / "Entity.xml"
                            entity_fields = read_entity_definition(entity_xml)
                            
                            # System fields
                            system_fields = {
                                'ownerid': ('Owner', 'lookup'),
                            }
                            entity_prefix = config['entity'].split('_')[0]
                            system_fields[f"{entity_prefix}_name"] = ('Name', 'text')
                            
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
                            
                            fields_added += len(field_tuples)
                            
                            add_fields_to_section(
                                unmanaged_path=unmanaged_path,
                                tab_name=tab_name,
                                section_name=section_label,
                                fields=field_tuples,
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


# ================================================================================
# QUICK CREATE FORM BUILDER ENDPOINTS
# ================================================================================

@router.post("/add-quickcreate-sections")
async def add_quickcreate_sections(request: AddQuickCreateSectionsRequest):
    """
    Add quick_create sections to all entity YAML files in a module.
    
    For each entity YAML file without a quick_create section, appends one
    with smart default fields. Preserves all existing YAML content.
    """
    try:
        module_path = Path(request.module_path)
        layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_path.name
        
        if not layouts_dir.exists():
            return {
                "success": False,
                "error": f"Layouts directory not found: {layouts_dir}"
            }
        
        layout_files = list(layouts_dir.glob("*.yaml"))
        if not layout_files:
            return {
                "success": False,
                "error": f"No YAML files found in {layouts_dir}"
            }
        
        updated_count = 0
        skipped_count = 0
        updated = []
        
        for layout_file in layout_files:
            entity_name = layout_file.stem
            
            try:
                # Read existing YAML
                with open(layout_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check if quick_create section already exists
                if 'quick_create:' in content and not request.overwrite:
                    skipped_count += 1
                    continue
                
                # Load YAML to extract entity info
                config = yaml.safe_load(content)
                if not config or 'entity' not in config:
                    skipped_count += 1
                    continue
                
                # Read entity definition to get fields
                entity_xml = module_path / "src" / "Entities" / entity_name / "Entity.xml"
                if not entity_xml.exists():
                    skipped_count += 1
                    continue
                
                entity_fields = read_entity_definition(entity_xml)
                
                # Generate smart default quick_create fields
                qc_fields = get_smart_default_fields(entity_fields, entity_name, max_fields=5)
                
                # Remove existing quick_create section if overwrite
                if request.overwrite and 'quick_create:' in content:
                    # Find and remove the quick_create section
                    lines = content.split('\n')
                    new_lines = []
                    in_qc_section = False
                    skip_comments = False
                    
                    for i, line in enumerate(lines):
                        if 'QUICK CREATE FORM' in line:
                            skip_comments = True
                            continue
                        if skip_comments and line.strip().startswith('#'):
                            continue
                        if 'quick_create:' in line:
                            in_qc_section = True
                            skip_comments = False
                            continue
                        if in_qc_section:
                            if line and not line.startswith('  '):
                                # End of quick_create section
                                in_qc_section = False
                                skip_comments = False
                            elif line.strip().startswith('#'):
                                # Skip comments after quick_create
                                continue
                            else:
                                # Skip quick_create field lines
                                continue
                        new_lines.append(line)
                    
                    content = '\n'.join(new_lines).rstrip()
                
                # Append quick_create section
                qc_section = [
                    "\n",
                    "# " + "=" * 76,
                    "# QUICK CREATE FORM (Optional)",
                    "# " + "=" * 76,
                    "#",
                    "# This section defines fields for a Quick Create form.",
                    "# Edit the field list below and use 'Build Quick Create Form' to generate",
                    "# the XML files in FormXml/quickCreate/.",
                    "#",
                    "quick_create:"
                ]
                
                for field_name in qc_fields:
                    qc_section.append(f"  - {field_name}")
                
                qc_section.extend([
                    "",
                    "# To disable Quick Create, comment out or remove the quick_create section.",
                    ""
                ])
                
                updated_content = content.rstrip() + '\n' + '\n'.join(qc_section)
                
                # Write back to file
                with open(layout_file, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                updated_count += 1
                updated.append({
                    "entity": entity_name,
                    "field_count": len(qc_fields),
                    "fields": qc_fields
                })
                
            except Exception as e:
                print(f"Error processing {entity_name}: {e}", file=sys.stderr)
                skipped_count += 1
                continue
        
        return {
            "success": True,
            "total": len(layout_files),
            "updated": updated_count,
            "skipped": skipped_count,
            "updated_entities": updated
        }
    
    except Exception as e:
        print(f"Error in add_quickcreate_sections: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/build-quickcreate-form")
async def build_quickcreate_form(request: BuildQuickCreateRequest):
    """
    Build a Quick Create form for a single entity.
    
    Creates new XML files in FormXml/quickCreate/ with unique GUID.
    """
    try:
        module_path = Path(request.module_path)
        entity_name = request.entity_name
        
        # Determine YAML file path
        if request.file_path:
            yaml_file = Path(request.file_path)
        else:
            layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_path.name
            yaml_file = layouts_dir / f"{entity_name}.yaml"
        
        if not yaml_file.exists():
            return {
                "success": False,
                "error": f"YAML file not found: {yaml_file}"
            }
        
        # Read YAML file
        with open(yaml_file, 'r', encoding='utf-8') as f:
            content = f.read()
            config = yaml.safe_load(content)
        
        if not config:
            return {
                "success": False,
                "error": "Empty YAML file"
            }
        
        # Check for quick_create section
        if 'quick_create' not in config:
            return {
                "success": False,
                "error": "No quick_create section found in YAML. Add one first using 'Add Quick Create Sections'."
            }
        
        qc_fields = config['quick_create']
        if not qc_fields or not isinstance(qc_fields, list):
            return {
                "success": False,
                "error": "quick_create section must be a list of field names"
            }
        
        # Check if Quick Create form already exists
        entity_dir = module_path / "src" / "Entities" / entity_name
        quickcreate_dir = entity_dir / "FormXml" / "quickCreate"
        
        if quickcreate_dir.exists():
            existing_forms = list(quickcreate_dir.glob("{*}.xml"))
            if existing_forms and not request.force:
                return {
                    "success": False,
                    "error": f"Quick Create form already exists. Use force=true to rebuild.",
                    "existing_form": str(existing_forms[0])
                }
        
        # Get entity XML path
        entity_xml = entity_dir / "Entity.xml"
        if not entity_xml.exists():
            return {
                "success": False,
                "error": f"Entity.xml not found: {entity_xml}"
            }
        
        # Get introduced version from Solution.xml
        solution_xml = module_path / "src" / "Other" / "Solution.xml"
        introduced_version = "1.0.0.0"
        if solution_xml.exists():
            try:
                tree = ET.parse(solution_xml)
                root = tree.getroot()
                version_elem = root.find('.//Version')
                if version_elem is not None and version_elem.text:
                    introduced_version = version_elem.text
            except:
                pass
        
        # Create Quick Create form
        form_guid, unmanaged_path, managed_path = create_quickcreate_form_files(
            entity_name=entity_name,
            fields=qc_fields,
            entity_xml_path=entity_xml,
            quickcreate_dir=quickcreate_dir,
            introduced_version=introduced_version,
            use_single_column=request.use_single_column
        )
        
        return {
            "success": True,
            "form_guid": form_guid,
            "field_count": len(qc_fields),
            "fields": qc_fields,
            "unmanaged_file": str(unmanaged_path.relative_to(PROJECT_ROOT)),
            "managed_file": str(managed_path.relative_to(PROJECT_ROOT)),
            "introduced_version": introduced_version
        }
    
    except Exception as e:
        print(f"Error in build_quickcreate_form: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/build-all-quickcreate-forms")
async def build_all_quickcreate_forms(request: BuildAllQuickCreateFormsRequest):
    """
    Build Quick Create forms for all entities in a module that have quick_create sections.
    """
    try:
        module_path = Path(request.module_path)
        layouts_dir = PROJECT_ROOT / ".design" / "layouts" / module_path.name
        
        if not layouts_dir.exists():
            return {
                "success": False,
                "error": f"Layouts directory not found: {layouts_dir}"
            }
        
        layout_files = list(layouts_dir.glob("*.yaml"))
        if not layout_files:
            return {
                "success": False,
                "error": f"No YAML files found in {layouts_dir}"
            }
        
        # Get solution version
        solution_xml = module_path / "src" / "Other" / "Solution.xml"
        introduced_version = "1.0.0.0"
        if solution_xml.exists():
            try:
                tree = ET.parse(solution_xml)
                root = tree.getroot()
                version_elem = root.find('.//Version')
                if version_elem is not None and version_elem.text:
                    introduced_version = version_elem.text
            except:
                pass
        
        results = []
        success_count = 0
        skipped_count = 0
        error_count = 0
        
        for layout_file in layout_files:
            entity_name = layout_file.stem
            
            try:
                # Read YAML
                with open(layout_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                if not config:
                    skipped_count += 1
                    continue
                
                # Check for quick_create section
                if 'quick_create' not in config:
                    skipped_count += 1
                    results.append({
                        "entity": entity_name,
                        "status": "skipped",
                        "reason": "No quick_create section"
                    })
                    continue
                
                qc_fields = config['quick_create']
                if not qc_fields or not isinstance(qc_fields, list):
                    error_count += 1
                    results.append({
                        "entity": entity_name,
                        "status": "error",
                        "error": "Invalid quick_create section (must be a list)"
                    })
                    continue
                
                # Check if already exists
                entity_dir = module_path / "src" / "Entities" / entity_name
                quickcreate_dir = entity_dir / "FormXml" / "quickCreate"
                
                if quickcreate_dir.exists():
                    existing_forms = list(quickcreate_dir.glob("{*}.xml"))
                    if existing_forms and not request.force:
                        skipped_count += 1
                        results.append({
                            "entity": entity_name,
                            "status": "skipped",
                            "reason": "Quick Create form already exists (use force to rebuild)"
                        })
                        continue
                
                # Get entity XML
                entity_xml = entity_dir / "Entity.xml"
                if not entity_xml.exists():
                    error_count += 1
                    results.append({
                        "entity": entity_name,
                        "status": "error",
                        "error": "Entity.xml not found"
                    })
                    continue
                
                # Create Quick Create form
                form_guid, unmanaged_path, managed_path = create_quickcreate_form_files(
                    entity_name=entity_name,
                    fields=qc_fields,
                    entity_xml_path=entity_xml,
                    quickcreate_dir=quickcreate_dir,
                    introduced_version=introduced_version,
                    use_single_column=request.use_single_column
                )
                
                success_count += 1
                results.append({
                    "entity": entity_name,
                    "status": "created",
                    "form_guid": form_guid,
                    "field_count": len(qc_fields),
                    "fields": qc_fields
                })
                
                print(f"✓ Created Quick Create form for {entity_name}: {form_guid}")
                
            except Exception as e:
                error_count += 1
                results.append({
                    "entity": entity_name,
                    "status": "error",
                    "error": str(e)
                })
                print(f"✗ Error building Quick Create for {entity_name}: {e}")
        
        return {
            "success": True,
            "total": len(layout_files),
            "success_count": success_count,
            "skipped_count": skipped_count,
            "error_count": error_count,
            "results": results
        }
    
    except Exception as e:
        print(f"Error in build_all_quickcreate_forms: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return {
            "success": False,
            "error": str(e)
        }

