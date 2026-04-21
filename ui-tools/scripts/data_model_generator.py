"""
Utility to generate data-models YAML from Entity.xml files.

This module scans a module's src/Entities directory and generates individual
YAML files (one per table) documenting entity metadata and fields for use in
process simulation.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import yaml
import re


def read_entity_fields(entity_xml_path: Path, entity_logical_name: str, lookup_map: Dict[tuple, str]) -> List[Dict[str, Any]]:
    """
    Read field definitions from an Entity.xml file.
    
    Args:
        entity_xml_path: Path to the Entity.xml file
        entity_logical_name: Logical name of the entity
        lookup_map: Dictionary mapping (entity, field) to target entity
        
    Returns:
        List of field dictionaries with field metadata
    """
    if not entity_xml_path.exists():
        return []
    
    tree = ET.parse(entity_xml_path)
    root = tree.getroot()
    
    fields = []
    
    # Find all attribute elements
    for attribute in root.findall(".//attribute"):
        # Check if it's a custom field
        is_custom_elem = attribute.find("IsCustomField")
        if is_custom_elem is None or is_custom_elem.text != "1":
            continue  # Skip system fields
        
        # Skip base currency fields (auto-generated for money fields)
        physical_name = attribute.get("PhysicalName", "")
        if physical_name.endswith("_Base"):
            continue
        
        # Extract field metadata
        type_elem = attribute.find("Type")
        name_elem = attribute.find("Name")
        logical_name_elem = attribute.find("LogicalName")
        required_elem = attribute.find("RequiredLevel")
        max_length_elem = attribute.find("MaxLength")
        
        # Get display name from displaynames section
        display_name = None
        displayname_elem = attribute.find(".//displayname[@languagecode='1033']")
        if displayname_elem is not None:
            display_name = displayname_elem.get("description")
        
        if type_elem is not None and name_elem is not None:
            field_type = type_elem.text.lower()
            
            field_data = {
                "logical_name": logical_name_elem.text if logical_name_elem is not None else name_elem.text,
                "display_name": display_name or name_elem.text,
                "type": map_dataverse_type(field_type),
                "required": required_elem.text.lower() if required_elem is not None else "none"
            }
            
            # Add max_length for string fields
            if max_length_elem is not None and field_type in ["nvarchar", "ntext"]:
                try:
                    field_data["max_length"] = int(max_length_elem.text)
                except ValueError:
                    pass
            
            # Handle picklist (choice) fields
            if field_type == "picklist":
                options = read_choice_options(attribute)
                if options:
                    field_data["options"] = options
                
                # Get optionset name (may differ from field logical name)
                optionset_name_elem = attribute.find("OptionSetName")
                if optionset_name_elem is not None:
                    field_data["optionset_name"] = optionset_name_elem.text
            
            # Handle lookup fields
            elif field_type in ["lookup", "customer", "owner"]:
                # Try to get target from relationships first
                logical_name_val = logical_name_elem.text if logical_name_elem is not None else name_elem.text
                lookup_key = (entity_logical_name, logical_name_val.lower())
                target_entity = lookup_map.get(lookup_key)
                
                # Fallback to getting target from attribute element
                if not target_entity:
                    target_entity = get_lookup_target(attribute)
                
                if target_entity:
                    field_data["target_entity"] = target_entity
            
            fields.append(field_data)
    
    return fields


def map_dataverse_type(dataverse_type: str) -> str:
    """
    Map Dataverse type to simplified type name for YAML.
    
    Args:
        dataverse_type: Dataverse type (e.g., "nvarchar", "picklist")
        
    Returns:
        Simplified type name (e.g., "Text", "Choice")
    """
    type_map = {
        "nvarchar": "Text",
        "ntext": "Memo",
        "int": "Integer",
        "decimal": "Decimal",
        "float": "Float",
        "money": "Currency",
        "datetime": "Date Time",
        "picklist": "Choice",
        "lookup": "Lookup",
        "customer": "Lookup",
        "owner": "Lookup",
        "boolean": "Yes / No",
    }
    return type_map.get(dataverse_type.lower(), dataverse_type)


def read_choice_options(attribute_element) -> List[Dict[str, Any]]:
    """
    Extract choice options from a picklist attribute.
    
    Args:
        attribute_element: XML element for the attribute
        
    Returns:
        List of option dictionaries with value and label
    """
    options = []
    
    # Look for optionset element
    optionset_elem = attribute_element.find(".//optionset")
    if optionset_elem is not None:
        for option_elem in optionset_elem.findall(".//option"):
            value_elem = option_elem.find("value")
            label_elem = option_elem.find(".//label[@languagecode='1033']")
            
            if value_elem is not None:
                option_data = {
                    "value": int(value_elem.text)
                }
                
                if label_elem is not None:
                    option_data["label"] = label_elem.get("description", "")
                
                options.append(option_data)
    
    return options


def derive_plural_name(entity_logical_name: str) -> str:
    """
    Derive the plural form of an entity logical name for Web API.
    
    Args:
        entity_logical_name: Entity logical name (e.g., appbase_CourtCase)
        
    Returns:
        Pluralized form (e.g., appbase_courtcases)
    """
    # Convert to lowercase
    name_lower = entity_logical_name.lower()
    
    # Handle special cases
    special_cases = {
        "contact": "contacts",
        "account": "accounts",
        "systemuser": "systemusers",
        "businessunit": "businessunits",
        "team": "teams",
        "owner": "owners",
    }
    
    if name_lower in special_cases:
        return special_cases[name_lower]
    
    # For custom entities, just add 's' (Dataverse typically doesn't use complex pluralization)
    if not name_lower.endswith('s'):
        return name_lower + 's'
    
    return name_lower


def read_relationships_from_folder(module_path: Path) -> Dict[tuple, str]:
    """
    Read all relationship XML files and build a mapping of lookup fields to target entities.
    
    Args:
        module_path: Path to the module directory
        
    Returns:
        Dictionary mapping (referencing_entity, referencing_attribute) to referenced_entity
    """
    relationships_dir = module_path / "src" / "Other" / "Relationships"
    
    if not relationships_dir.exists():
        return {}
    
    lookup_map = {}
    
    # Read all relationship XML files
    for rel_file in relationships_dir.glob("*.xml"):
        try:
            tree = ET.parse(rel_file)
            root = tree.getroot()
            
            # Find all EntityRelationship elements
            for rel in root.findall(".//EntityRelationship"):
                rel_type = rel.find("EntityRelationshipType")
                
                # We only care about OneToMany relationships (lookup fields)
                if rel_type is not None and rel_type.text == "OneToMany":
                    referencing_entity = rel.find("ReferencingEntityName")
                    referenced_entity = rel.find("ReferencedEntityName")
                    referencing_attr = rel.find("ReferencingAttributeName")
                    
                    if all([referencing_entity is not None, referenced_entity is not None, referencing_attr is not None]):
                        # Store mapping: (entity, field) -> target entity
                        key = (referencing_entity.text, referencing_attr.text.lower())
                        lookup_map[key] = referenced_entity.text
        except Exception as e:
            # Silently skip files that can't be parsed
            pass
    
    return lookup_map


def get_lookup_target(attribute_element) -> Optional[str]:
    """
    Extract target entity for a lookup field.
    
    Args:
        attribute_element: XML element for the attribute
        
    Returns:
        Target entity logical name or None
    """
    # Look for Targets element
    targets_elem = attribute_element.find("Targets")
    if targets_elem is not None and targets_elem.text:
        # Return first target (most lookups have single target)
        targets = targets_elem.text.split(",")
        return targets[0].strip() if targets else None
    
    return None


def read_entity_relationships(entity_xml_path: Path) -> List[Dict[str, Any]]:
    """
    Read relationship definitions from an Entity.xml file.
    
    Args:
        entity_xml_path: Path to the Entity.xml file
        
    Returns:
        List of relationship dictionaries
    """
    if not entity_xml_path.exists():
        return []
    
    tree = ET.parse(entity_xml_path)
    root = tree.getroot()
    
    relationships = []
    
    # Find 1:N relationships
    for rel in root.findall(".//EntityRelationship[@RelationshipType='OneToManyRelationship']"):
        name_elem = rel.find("Name")
        referenced_entity_elem = rel.find("ReferencedEntity")
        referencing_entity_elem = rel.find("ReferencingEntity")
        referencing_attr_elem = rel.find("ReferencingAttribute")
        
        if name_elem is not None and referenced_entity_elem is not None:
            rel_data = {
                "name": name_elem.text,
                "type": "one_to_many",
                "target_entity": referencing_entity_elem.text if referencing_entity_elem is not None else ""
            }
            
            if referencing_attr_elem is not None:
                rel_data["referencing_field"] = referencing_attr_elem.text
            
            relationships.append(rel_data)
    
    return relationships


def get_entity_metadata(entity_xml_path: Path) -> Dict[str, str]:
    """
    Extract entity metadata from Entity.xml.
    
    Args:
        entity_xml_path: Path to the Entity.xml file
        
    Returns:
        Dictionary with entity metadata
    """
    tree = ET.parse(entity_xml_path)
    root = tree.getroot()
    
    metadata = {}
    
    # Get logical name
    name_elem = root.find(".//Name[@LocalizedName]")
    if name_elem is not None:
        metadata["logical_name"] = name_elem.text
    
    # Get display name
    localized_elem = root.find(".//LocalizedNames/LocalizedName[@languagecode='1033']")
    if localized_elem is not None:
        metadata["display_name"] = localized_elem.get("description", "")
    
    # Get primary field
    primary_field_elem = root.find(".//PrimaryName[@PrimaryImage='0']")
    if primary_field_elem is not None:
        metadata["primary_field"] = primary_field_elem.text
    
    # Get description
    desc_elem = root.find(".//Descriptions/Description[@languagecode='1033']")
    if desc_elem is not None:
        desc = desc_elem.get("description", "")
        if desc:
            metadata["description"] = desc
    
    return metadata


def extract_description_from_build_md(module_path: Path, entity_display_name: str) -> str:
    """
    Extract entity description from BUILD.md file.
    
    Args:
        module_path: Path to the module directory
        entity_display_name: Display name of the entity to find
        
    Returns:
        Description text or empty string if not found
    """
    build_md_path = module_path / "BUILD.md"
    
    try:
        if not build_md_path.exists():
            return ""
        
        content = build_md_path.read_text(encoding="utf-8")
        
        # Find the section for this entity (## Entity Name)
        pattern = rf"^## {re.escape(entity_display_name)}\s*$"
        match = re.search(pattern, content, re.MULTILINE)
        
        if not match:
            return ""
        
        # Extract description (lines between heading and **Completed:** or next ##)
        start_pos = match.end()
        
        # Find the end of the description section (before **Completed:** or next ##)
        end_match = re.search(r"\*\*Completed:\*\*|^##", content[start_pos:], re.MULTILINE)
        
        if end_match:
            description_text = content[start_pos:start_pos + end_match.start()]
        else:
            description_text = content[start_pos:]
        
        # Clean up the description
        description_text = description_text.strip()
        
        # Remove empty lines and extra whitespace
        lines = [line.strip() for line in description_text.split("\n") if line.strip()]
        description_text = "\n".join(lines)
        
        return description_text
        
    except Exception as e:
        # Silently fail and return empty string
        return ""


def format_field_for_yaml(field: Dict[str, Any], entity_name_map: Dict[str, str]) -> str:
    """
    Format a field dictionary as a YAML list item string.
    
    Args:
        field: Field dictionary with display_name, type, and logical_name
        entity_name_map: Map of entity logical names to display names
        
    Returns:
        Formatted string like "Display Name: Type; schema_name" or "Display Name: Lookup (Target Table); schema_name"
    """
    display_name = field.get("display_name", "Unknown")
    field_type = field.get("type", "Text")
    logical_name = field.get("logical_name", "")
    
    # For lookup fields, include the target entity display name
    if field_type == "Lookup" and "target_entity" in field:
        target_logical_name = field["target_entity"]
        target_display_name = entity_name_map.get(target_logical_name, target_logical_name)
        field_type = f"Lookup ({target_display_name})"
    
    # For choice fields with different optionset name, append it
    result = f"{display_name}: {field_type}; {logical_name}"
    if field_type == "Choice" and "optionset_name" in field:
        optionset_name = field["optionset_name"]
        # Only append if different from logical name
        if optionset_name != logical_name:
            result += f"; optionset={optionset_name}"
    
    return result


def generate_table_yaml(entity_metadata: Dict[str, Any], fields: List[Dict[str, Any]], description: str, entity_name_map: Dict[str, str]) -> str:
    """
    Generate YAML content for a single table file.
    
    Args:
        entity_metadata: Entity metadata dict
        fields: List of field dictionaries
        description: Description text from BUILD.md
        entity_name_map: Map of entity logical names to display names
        
    Returns:
        YAML string for the table
    """
    # Build the table data structure
    logical_name = entity_metadata.get("logical_name", "")
    table_data = {
        "name": entity_metadata.get("display_name", ""),
        "schema_name": logical_name,
        "plural_name": derive_plural_name(logical_name),
    }
    
    # Add description if available
    if description:
        table_data["description"] = description
    else:
        table_data["description"] = ""
    
    # Format fields
    field_strings = [format_field_for_yaml(field, entity_name_map) for field in fields]
    
    # Build YAML manually for better formatting
    yaml_lines = [
        f"name: {table_data['name']}",
        f"schema_name: {table_data['schema_name']}",
        f"plural_name: {table_data['plural_name']}",
    ]
    
    # Add description with proper multiline formatting if present
    if description:
        yaml_lines.append("description: >")
        # Split description into lines and indent
        desc_lines = description.split("\n")
        for line in desc_lines:
            yaml_lines.append(f"  {line}")
    else:
        yaml_lines.append("description:")
    
    # Add blank line before fields
    yaml_lines.append("")
    
    # Add fields (quoted to prevent YAML parsing issues with colons)
    yaml_lines.append("fields:")
    for field_str in field_strings:
        yaml_lines.append(f"  - \"{field_str}\"")
    
    return "\n".join(yaml_lines) + "\n"


def generate_data_models(module_path: Path) -> Dict[str, str]:
    """
    Generate data-models YAML files from all Entity.xml files in a module.
    
    Args:
        module_path: Path to the module directory
        
    Returns:
        Dictionary mapping filename to YAML content
    """
    entities_dir = module_path / "src" / "Entities"
    
    if not entities_dir.exists():
        raise FileNotFoundError(f"Entities directory not found: {entities_dir}")
    
    table_files = {}
    
    # First pass: Build entity name mapping (logical name -> display name)
    entity_name_map = {}
    for entity_dir in entities_dir.iterdir():
        if not entity_dir.is_dir():
            continue
        entity_xml = entity_dir / "Entity.xml"
        if entity_xml.exists():
            try:
                metadata = get_entity_metadata(entity_xml)
                logical_name = metadata.get("logical_name", "")
                display_name = metadata.get("display_name", "")
                if logical_name and display_name:
                    entity_name_map[logical_name] = display_name
            except Exception:
                pass
    
    # Build lookup field mapping from relationship files
    lookup_map = read_relationships_from_folder(module_path)
    
    # Second pass: Generate YAML files
    for entity_dir in sorted(entities_dir.iterdir()):
        if not entity_dir.is_dir():
            continue
        
        entity_xml = entity_dir / "Entity.xml"
        if not entity_xml.exists():
            continue
        
        # Skip entities that don't have FormXml or SavedQueries (external references)
        has_forms = (entity_dir / "FormXml").exists()
        has_views = (entity_dir / "SavedQueries").exists()
        
        if not has_forms and not has_views:
            print(f"Skipping {entity_dir.name}: No FormXml or SavedQueries (external entity reference)")
            continue
        
        try:
            # Read entity metadata
            metadata = get_entity_metadata(entity_xml)
            entity_logical_name = metadata.get("logical_name", "")
            display_name = metadata.get("display_name", "")
            
            # Skip entities without display names (unlikely at this point, but kept for safety)
            if not display_name:
                print(f"Skipping {entity_dir.name}: No display name found")
                continue
            
            # Read fields
            fields = read_entity_fields(entity_xml, entity_logical_name, lookup_map)
            
            # Get description from BUILD.md
            description = extract_description_from_build_md(module_path, display_name)
            
            # Generate YAML content
            yaml_content = generate_table_yaml(metadata, fields, description, entity_name_map)
            
            # Create filename from display name (lowercase, hyphenated)
            filename = display_name.lower().replace(" ", "-") + ".yaml"
            
            table_files[filename] = yaml_content
            
        except Exception as e:
            print(f"Error processing {entity_dir.name}: {e}")
            continue
    
    return table_files


def generate_choices_yaml(module_path: Path) -> str:
    """
    Generate choices.yaml file containing all choice field options from a module.
    
    Args:
        module_path: Path to the module directory
        
    Returns:
        YAML string mapping field schema names to label->value dictionaries
    """
    optionsets_dir = module_path / "src" / "OptionSets"
    
    if not optionsets_dir.exists():
        return "# No OptionSets found\n"
    
    choices_dict = {}
    
    # Iterate through all optionset XML files
    for optionset_file in sorted(optionsets_dir.glob("*.xml")):
        try:
            # Parse optionset XML
            tree = ET.parse(optionset_file)
            root = tree.getroot()
            
            # Get the optionset name (this is the field logical name)
            optionset_name = root.get("Name")
            if not optionset_name:
                continue
            
            # Build label -> value dictionary
            label_value_map = {}
            
            for option_elem in root.findall(".//option"):
                value_str = option_elem.get("value")
                if value_str is None:
                    continue
                
                # Get the label
                label_elem = option_elem.find(".//label[@languagecode='1033']")
                if label_elem is None:
                    continue
                
                label = label_elem.get("description", "")
                if not label:
                    continue
                
                # Convert value to int
                try:
                    value = int(value_str)
                    label_value_map[label] = value
                except ValueError:
                    continue
            
            if label_value_map:
                choices_dict[optionset_name] = label_value_map
                    
        except Exception as e:
            print(f"Error processing optionset {optionset_file.name}: {e}")
            continue
    
    # Generate YAML manually for better formatting
    if not choices_dict:
        return "# No choice fields found\n"
    
    yaml_lines = ["# Choice Field Options", "# Format: field_schema_name:", "#   Label: Value", ""]
    
    for field_name in sorted(choices_dict.keys()):
        yaml_lines.append(f"{field_name}:")
        label_value_map = choices_dict[field_name]
        
        for label in sorted(label_value_map.keys()):
            value = label_value_map[label]
            yaml_lines.append(f"  {label}: {value}")
        
        yaml_lines.append("")  # Blank line between fields
    
    return "\n".join(yaml_lines)


def save_data_models(module_path: Path, output_dir: Optional[Path] = None) -> List[Path]:
    """
    Generate and save individual data-model YAML files for each table in a module,
    plus choices.yaml with all choice field options.
    
    Args:
        module_path: Path to the module directory
        output_dir: Optional custom output directory (defaults to module/design/data-models/)
        
    Returns:
        List of paths where files were saved
    """
    table_files = generate_data_models(module_path)
    
    if output_dir is None:
        output_dir = module_path / "design" / "data-models"
    
    # Create directories if needed
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Delete old entities.yaml file if it exists
    old_file = output_dir / "entities.yaml"
    if old_file.exists():
        old_file.unlink()
        print(f"Deleted old file: {old_file}")
    
    # Write individual table files
    saved_files = []
    for filename, yaml_content in table_files.items():
        file_path = output_dir / filename
        file_path.write_text(yaml_content, encoding="utf-8")
        saved_files.append(file_path)
    
    # Generate and save choices.yaml
    choices_yaml = generate_choices_yaml(module_path)
    choices_path = output_dir / "choices.yaml"
    choices_path.write_text(choices_yaml, encoding="utf-8")
    saved_files.append(choices_path)
    print(f"Generated choices file: {choices_path}")
    
    return saved_files


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python data_model_generator.py <module_path>")
        sys.exit(1)
    
    module_path = Path(sys.argv[1])
    
    try:
        output_files = save_data_models(module_path)
        print(f"Generated {len(output_files)} table files:")
        for file_path in output_files:
            print(f"  - {file_path}")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
