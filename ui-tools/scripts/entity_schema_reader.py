"""
Utility to read Dataverse entity definitions and extract field metadata.

This module provides functions to parse Entity.xml files from Dataverse solutions
and extract custom field information for form building workflows.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class EntityField:
    """Represents a field in a Dataverse entity."""
    name: str
    logical_name: str
    display_name: str
    type: str
    format: Optional[str] = None
    is_custom: bool = False
    required_level: str = "none"
    
    @property
    def form_field_type(self) -> str:
        """
        Convert Entity.xml type to form field type used in formxml_parser.
        
        Maps Dataverse data types to control types for form XML.
        
        Returns:
            String representing the form control type (e.g., "text", "email", "choice")
        """
        type_mapping = {
            "nvarchar": "text",
            "ntext": "memo",
            "int": "integer",
            "decimal": "decimal",
            "float": "float",
            "money": "currency",
            "datetime": "datetime",
            "picklist": "choice",
            "lookup": "lookup",
            "customer": "lookup",
            "owner": "lookup",
            "boolean": "twooptions",
        }
        
        base_type = self.type.lower()
        
        # Handle special cases based on format attribute
        if base_type == "nvarchar" and self.format:
            format_lower = self.format.lower()
            if format_lower == "email":
                return "email"
            elif format_lower == "url":
                return "url"
        
        # Handle datetime vs date
        if base_type == "datetime" and self.format:
            format_lower = self.format.lower()
            if format_lower == "dateonly":
                return "date"
        
        return type_mapping.get(base_type, "text")
    
    @property
    def type_category(self) -> str:
        """
        Get the category of this field type for grouping.
        
        Returns:
            Category name: "text", "numeric", "datetime", "choice", or "other"
        """
        form_type = self.form_field_type
        
        if form_type in ["text", "email", "url", "memo"]:
            return "text"
        elif form_type in ["integer", "decimal", "float", "currency"]:
            return "numeric"
        elif form_type in ["date", "datetime"]:
            return "datetime"
        elif form_type in ["choice", "lookup", "twooptions"]:
            return "choice"
        else:
            return "other"


def read_entity_definition(entity_xml_path: Path) -> List[EntityField]:
    """
    Read an Entity.xml file and extract field definitions.
    
    Args:
        entity_xml_path: Path to the Entity.xml file
        
    Returns:
        List of EntityField objects for custom fields (IsCustomField=1)
        
    Raises:
        FileNotFoundError: If entity_xml_path doesn't exist
        ET.ParseError: If XML is malformed
    """
    if not entity_xml_path.exists():
        raise FileNotFoundError(f"Entity.xml not found at: {entity_xml_path}")
    
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
        format_elem = attribute.find("Format")
        
        # Get display name from displaynames section
        display_name = None
        displayname_elem = attribute.find(".//displayname[@languagecode='1033']")
        if displayname_elem is not None:
            display_name = displayname_elem.get("description")
        
        if type_elem is not None and name_elem is not None:
            field = EntityField(
                name=name_elem.text,
                logical_name=logical_name_elem.text if logical_name_elem is not None else name_elem.text,
                display_name=display_name or name_elem.text,
                type=type_elem.text,
                format=format_elem.text if format_elem is not None else None,
                is_custom=True,
                required_level=required_elem.text if required_elem is not None else "none"
            )
            fields.append(field)
    
    return fields


def get_entity_name_from_xml(entity_xml_path: Path) -> Optional[str]:
    """
    Extract the entity name from an Entity.xml file.
    
    Args:
        entity_xml_path: Path to the Entity.xml file
        
    Returns:
        Entity logical name (e.g., "appbase_Sample") or None if not found
    """
    try:
        tree = ET.parse(entity_xml_path)
        root = tree.getroot()
        
        # Try to find Name element with LocalizedName attribute
        name_elem = root.find(".//Name[@LocalizedName]")
        if name_elem is not None:
            return name_elem.text
        
        # Fallback: find entity element with Name attribute
        entity_elem = root.find(".//entity[@Name]")
        if entity_elem is not None:
            return entity_elem.get("Name")
        
        return None
    except Exception:
        return None


def group_fields_by_type(fields: List[EntityField]) -> Dict[str, List[EntityField]]:
    """
    Group fields by their type category.
    
    Args:
        fields: List of EntityField objects
        
    Returns:
        Dictionary mapping category names to lists of fields
    """
    grouped = {
        "text": [],
        "numeric": [],
        "datetime": [],
        "choice": [],
        "other": []
    }
    
    for field in fields:
        category = field.type_category
        grouped[category].append(field)
    
    return grouped


def extract_form_default_tab(form_xml_path: Path) -> Optional[Dict]:
    """
    Extract the default (first) tab structure from a form XML file.
    
    This captures the out-of-box General tab with Name and Owner fields
    so we can preserve them in the YAML structure.
    
    Args:
        form_xml_path: Path to the form XML file
        
    Returns:
        Dictionary with tab structure or None if form doesn't exist
        {
            "id": "{tab-guid}",
            "label": "General", 
            "sections": [{
                "id": "{section-guid}",
                "label": "General",
                "fields": ["appbase_name", "ownerid"]
            }]
        }
    """
    if not form_xml_path.exists():
        return None
    
    try:
        tree = ET.parse(form_xml_path)
        root = tree.getroot()
        
        # Find the first tab (default General tab)
        first_tab = root.find(".//tab")
        if first_tab is None:
            return None
        
        tab_id = first_tab.get("id")
        tab_label_elem = first_tab.find(".//label[@languagecode='1033']")
        tab_label = tab_label_elem.get("description", "General") if tab_label_elem is not None else "General"
        
        # Extract sections from this tab
        sections = []
        for section_elem in first_tab.findall(".//section"):
            section_id = section_elem.get("id")
            section_label_elem = section_elem.find(".//label[@languagecode='1033']")
            section_label = section_label_elem.get("description", "") if section_label_elem is not None else ""
            
            # Extract existing fields from this section
            existing_fields = []
            for control in section_elem.findall(".//control"):
                datafieldname = control.get("datafieldname")
                if datafieldname:
                    existing_fields.append(datafieldname)
            
            if section_id and existing_fields:  # Only include sections with fields
                sections.append({
                    "id": section_id,
                    "label": section_label,
                    "fields": existing_fields
                })
        
        return {
            "id": tab_id,
            "label": tab_label,
            "sections": sections
        }
    
    except Exception as e:
        print(f"Warning: Could not parse form XML: {e}")
        return None


def generate_yaml_template(entity_name: str, form_guid: str, fields: List[EntityField], 
                           form_xml_path: Optional[Path] = None) -> str:
    """
    Generate a YAML template with all custom fields listed as comments.
    
    This template is designed to be organized by AI (like GitHub Copilot) into
    a proper form layout with tabs and sections.
    
    Args:
        entity_name: Logical name of the entity (e.g., "appbase_Sample")
        form_guid: GUID of the form (with braces)
        fields: List of custom EntityField objects
        form_xml_path: Optional path to form XML to extract default tab structure
        
    Returns:
        YAML string with template format
    """
    from datetime import datetime
    
    # Group fields by category
    grouped = group_fields_by_type(fields)
    
    # Extract default tab structure if form XML provided
    default_tab = None
    if form_xml_path:
        default_tab = extract_form_default_tab(form_xml_path)
    
    # Build YAML template
    yaml_lines = [
        f"# {entity_name}-form-config.yaml",
        f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"# Entity: {entity_name}",
        f"# Form: {form_guid}",
        "",
        f"entity: {entity_name}",
        f"form_guid: \"{form_guid}\"",
        "",
        "# " + "=" * 76,
        f"# Available Custom Fields ({len(fields)} total)",
        "# " + "=" * 76,
        "#"
    ]
    
    # Add text fields
    if grouped["text"]:
        yaml_lines.append(f"# TEXT FIELDS ({len(grouped['text'])}):")
        for field in grouped["text"]:
            required_marker = " [REQUIRED]" if field.required_level == "required" else ""
            yaml_lines.append(f"#   - {field.logical_name} ({field.display_name}) - {field.form_field_type}{required_marker}")
        yaml_lines.append("#")
    
    # Add numeric fields
    if grouped["numeric"]:
        yaml_lines.append(f"# NUMERIC FIELDS ({len(grouped['numeric'])}):")
        for field in grouped["numeric"]:
            required_marker = " [REQUIRED]" if field.required_level == "required" else ""
            yaml_lines.append(f"#   - {field.logical_name} ({field.display_name}) - {field.form_field_type}{required_marker}")
        yaml_lines.append("#")
    
    # Add date/time fields
    if grouped["datetime"]:
        yaml_lines.append(f"# DATE/TIME FIELDS ({len(grouped['datetime'])}):")
        for field in grouped["datetime"]:
            required_marker = " [REQUIRED]" if field.required_level == "required" else ""
            yaml_lines.append(f"#   - {field.logical_name} ({field.display_name}) - {field.form_field_type}{required_marker}")
        yaml_lines.append("#")
    
    # Add choice & lookup fields
    if grouped["choice"]:
        yaml_lines.append(f"# CHOICE & LOOKUP FIELDS ({len(grouped['choice'])}):")
        for field in grouped["choice"]:
            required_marker = " [REQUIRED]" if field.required_level == "required" else ""
            yaml_lines.append(f"#   - {field.logical_name} ({field.display_name}) - {field.form_field_type}{required_marker}")
        yaml_lines.append("#")
    
    # Add other fields
    if grouped["other"]:
        yaml_lines.append(f"# OTHER FIELDS ({len(grouped['other'])}):")
        for field in grouped["other"]:
            required_marker = " [REQUIRED]" if field.required_level == "required" else ""
            yaml_lines.append(f"#   - {field.logical_name} ({field.display_name}) - {field.form_field_type}{required_marker}")
        yaml_lines.append("#")
    
    yaml_lines.extend([
        "# " + "=" * 76,
        "",
        "tabs:",
    ])
    
    # Add default tab if extracted from form
    if default_tab:
        yaml_lines.append(f"  - id: \"{default_tab['id']}\"  # Existing OOB tab")
        yaml_lines.append(f"    label: {default_tab['label']}")
        yaml_lines.append("    sections:")
        
        for section in default_tab['sections']:
            yaml_lines.append(f"      - id: \"{section['id']}\"  # Existing section")
            yaml_lines.append(f"        label: \"{section['label']}\"")
            yaml_lines.append("        columns: 1")
            yaml_lines.append("        existing_fields:  # These fields will be preserved")
            for field in section['fields']:
                yaml_lines.append(f"          - {field}")
            yaml_lines.append("        fields:")
            yaml_lines.append("          # TODO: Add custom fields here")
            yaml_lines.append("")
    else:
        # Fallback to simple template if no form structure found
        yaml_lines.extend([
            "  - name: tab_general",
            "    label: General",
            "    sections:",
            "      - label: Basic Information",
            "        columns: 1",
            "        fields:",
            "          # TODO: Add fields here",
        ])
    
    return "\n".join(yaml_lines)


if __name__ == "__main__":
    # Test with Sample entity
    sample_entity_xml = Path(__file__).parent.parent.parent / "test" / "Test" / "src" / "Entities" / "appbase_Sample" / "Entity.xml"
    
    if sample_entity_xml.exists():
        print(f"Reading entity definition from: {sample_entity_xml}")
        print("=" * 80)
        
        fields = read_entity_definition(sample_entity_xml)
        
        print(f"\nFound {len(fields)} custom fields:")
        
        # Group by type
        grouped = group_fields_by_type(fields)
        
        for category, category_fields in grouped.items():
            if category_fields:
                print(f"\n{category.upper()} ({len(category_fields)}):")
                for field in category_fields:
                    required = " [REQUIRED]" if field.required_level == "required" else ""
                    print(f"  • {field.logical_name:<30} {field.display_name:<25} ({field.form_field_type}){required}")
        
        # Generate YAML template
        print("\n" + "=" * 80)
        print("YAML TEMPLATE:")
        print("=" * 80)
        yaml_template = generate_yaml_template("appbase_Sample", "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}", fields)
        print(yaml_template)
    else:
        print(f"Entity.xml not found at: {sample_entity_xml}")
