"""
Quick Create Form Builder - Creates new Quick Create form XML files from field lists.

This module provides functions for creating brand new Quick Create form XML files
with generated GUIDs. Unlike the main form builder which rebuilds existing forms,
this creates entirely new form files from scratch.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple, Optional
from datetime import datetime

from formxml_parser import generate_guid, Label, FormDefinition, Tab, Column, Section, Row, Cell, Control
from formxml_constants import ControlClassId, FormPresentation, FormActivationState, DEFAULT_LANGUAGE_CODE
from entity_schema_reader import read_entity_definition, EntityField


# Standard security role IDs used in Quick Create forms
DEFAULT_QUICKCREATE_ROLES = [
    "{627090ff-40a3-4053-8790-584edc5be201}",
    "{119f245c-3cc8-4b62-b31c-d1a046ced15d}"
]


def create_quickcreate_xml_structure(
    entity_name: str,
    fields: List[str],
    entity_fields: List[EntityField],
    form_guid: Optional[str] = None,
    introduced_version: str = "1.0.0.0",
    use_single_column: bool = True
) -> str:
    """
    Create a complete Quick Create form XML from scratch.
    
    Args:
        entity_name: Logical name of the entity (e.g., "appbase_DisputeParty")
        fields: List of field logical names to include in the form
        entity_fields: List of EntityField objects with field metadata
        form_guid: Optional form GUID (generates new one if not provided)
        introduced_version: Solution version where form was introduced
        use_single_column: If True, use single column layout; if False, use 3-column template
        
    Returns:
        Complete XML string for Quick Create form
    """
    if not form_guid:
        form_guid = generate_guid()
    
    # Ensure GUID has braces
    if not form_guid.startswith('{'):
        form_guid = '{' + form_guid
    if not form_guid.endswith('}'):
        form_guid = form_guid + '}'
    
    # Create root elements
    root = ET.Element('forms')
    root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
    
    systemform = ET.SubElement(root, 'systemform')
    
    # Add form metadata
    ET.SubElement(systemform, 'formid').text = form_guid
    ET.SubElement(systemform, 'IntroducedVersion').text = introduced_version
    ET.SubElement(systemform, 'FormPresentation').text = '1'  # QuickCreate form type
    ET.SubElement(systemform, 'FormActivationState').text = '1'  # Active
    
    # Create form structure
    form_elem = ET.SubElement(systemform, 'form')
    tabs_elem = ET.SubElement(form_elem, 'tabs')
    
    # Create single tab (no label shown for Quick Create)
    tab_id = generate_guid()[1:-1]  # Remove braces for tab id
    tab_elem = ET.SubElement(tabs_elem, 'tab')
    tab_elem.set('id', tab_id)
    tab_elem.set('name', 'tab_1')
    tab_elem.set('showlabel', 'false')
    tab_labelid = generate_guid()
    tab_elem.set('labelid', tab_labelid)
    
    # Add tab labels
    tab_labels = ET.SubElement(tab_elem, 'labels')
    tab_label = ET.SubElement(tab_labels, 'label')
    tab_label.set('description', 'New Tab')
    tab_label.set('languagecode', '1033')
    
    # Create columns structure
    columns_elem = ET.SubElement(tab_elem, 'columns')
    
    if use_single_column:
        # Single column layout (100% width) - simpler for Quick Create
        _add_quickcreate_column_with_fields(
            columns_elem, 
            width="100%", 
            column_num=1,
            fields=fields,
            entity_fields=entity_fields,
            entity_name=entity_name
        )
    else:
        # Three-column template layout (like existing Quick Create forms)
        # First column gets all the fields, other columns are empty placeholders
        _add_quickcreate_column_with_fields(
            columns_elem,
            width="34%",
            column_num=1,
            fields=fields,
            entity_fields=entity_fields,
            entity_name=entity_name
        )
        
        # Add two empty placeholder columns
        _add_empty_quickcreate_column(columns_elem, width="33%", column_num=2)
        _add_empty_quickcreate_column(columns_elem, width="33%", column_num=3)
    
    # Add DisplayConditions with standard security roles
    display_conditions = ET.SubElement(form_elem, 'DisplayConditions')
    display_conditions.set('Order', '0')
    display_conditions.set('FallbackForm', 'true')
    
    for role_id in DEFAULT_QUICKCREATE_ROLES:
        role_elem = ET.SubElement(display_conditions, 'Role')
        role_elem.set('Id', role_id)
    
    # Add form customization settings
    ET.SubElement(systemform, 'IsCustomizable').text = '1'
    ET.SubElement(systemform, 'CanBeDeleted').text = '1'
    
    # Add localized name
    localized_names = ET.SubElement(systemform, 'LocalizedNames')
    localized_name = ET.SubElement(localized_names, 'LocalizedName')
    localized_name.set('description', 'Quick Create')
    localized_name.set('languagecode', '1033')
    
    # Convert to string with proper formatting
    xml_str = _prettify_xml(root)
    return xml_str


def _add_quickcreate_column_with_fields(
    columns_elem: ET.Element,
    width: str,
    column_num: int,
    fields: List[str],
    entity_fields: List[EntityField],
    entity_name: str
) -> None:
    """
    Add a column with a section containing the specified fields.
    
    Args:
        columns_elem: Parent columns XML element
        width: Column width (e.g., "100%", "34%")
        column_num: Column number (1, 2, 3)
        fields: List of field logical names
        entity_fields: List of EntityField objects with metadata
        entity_name: Entity logical name
    """
    column = ET.SubElement(columns_elem, 'column')
    column.set('width', width)
    
    sections = ET.SubElement(column, 'sections')
    section = ET.SubElement(sections, 'section')
    
    section_id = generate_guid()[1:-1]  # Remove braces
    section.set('id', section_id)
    section.set('name', f'tab_1_column_{column_num}_section_1')
    section.set('columns', '1')  # Single column within section
    section.set('showlabel', 'true')
    section.set('showbar', 'false')
    section.set('IsUserDefined', '0')
    section.set('labelwidth', '130')
    section_labelid = generate_guid()
    section.set('labelid', section_labelid)
    
    # Add section labels
    section_labels = ET.SubElement(section, 'labels')
    section_label = ET.SubElement(section_labels, 'label')
    section_label.set('description', 'New Section')
    section_label.set('languagecode', '1033')
    
    # Add rows with fields
    rows_elem = ET.SubElement(section, 'rows')
    
    # If no fields provided, add one empty row
    if not fields:
        _add_empty_row(rows_elem)
        return
    
    # Create field metadata lookup
    field_metadata = {f.logical_name: f for f in entity_fields}
    
    # Add system fields if they're commonly available
    entity_prefix = entity_name.split('_')[0] if '_' in entity_name else entity_name
    name_field = f"{entity_prefix}_name"
    field_metadata['ownerid'] = EntityField(
        name='ownerid',
        logical_name='ownerid',
        display_name='Owner',
        type='lookup',
        format=None,
        is_custom=False,
        required_level='required'
    )
    if name_field not in field_metadata:
        field_metadata[name_field] = EntityField(
            name=name_field,
            logical_name=name_field,
            display_name='Name',
            type='text',
            format=None,
            is_custom=False,
            required_level='required'
        )
    
    # Add one row per field
    for field_name in fields:
        field_meta = field_metadata.get(field_name)
        if not field_meta:
            # Skip unknown fields
            continue
        
        _add_field_row(rows_elem, field_name, field_meta)


def _add_empty_quickcreate_column(
    columns_elem: ET.Element,
    width: str,
    column_num: int
) -> None:
    """
    Add an empty placeholder column (used in 3-column template).
    
    Args:
        columns_elem: Parent columns XML element
        width: Column width (e.g., "33%")
        column_num: Column number (2, 3)
    """
    column = ET.SubElement(columns_elem, 'column')
    column.set('width', width)
    
    sections = ET.SubElement(column, 'sections')
    section = ET.SubElement(sections, 'section')
    
    section_id = generate_guid()[1:-1]
    section.set('id', section_id)
    section.set('name', f'tab_1_column_{column_num}_section_1')
    section.set('columns', '1')
    section.set('showlabel', 'true')
    section.set('showbar', 'false')
    section.set('IsUserDefined', '0')
    section.set('labelwidth', '130')
    section_labelid = generate_guid()
    section.set('labelid', section_labelid)
    
    # Add section labels
    section_labels = ET.SubElement(section, 'labels')
    section_label = ET.SubElement(section_labels, 'label')
    section_label.set('description', 'New Section')
    section_label.set('languagecode', '1033')
    
    # Add one empty row
    rows_elem = ET.SubElement(section, 'rows')
    _add_empty_row(rows_elem)


def _add_empty_row(rows_elem: ET.Element) -> None:
    """Add an empty row with a placeholder cell."""
    row = ET.SubElement(rows_elem, 'row')
    cell = ET.SubElement(row, 'cell')
    
    cell_id = generate_guid()[1:-1]
    cell.set('id', cell_id)
    cell_labelid = generate_guid()
    cell.set('labelid', cell_labelid)
    
    # Add cell labels
    cell_labels = ET.SubElement(cell, 'labels')
    cell_label = ET.SubElement(cell_labels, 'label')
    cell_label.set('description', '')
    cell_label.set('languagecode', '1033')


def _add_field_row(rows_elem: ET.Element, field_name: str, field_meta: EntityField) -> None:
    """
    Add a row with a field control.
    
    Args:
        rows_elem: Parent rows XML element
        field_name: Field logical name
        field_meta: EntityField object with field metadata
    """
    row = ET.SubElement(rows_elem, 'row')
    cell = ET.SubElement(row, 'cell')
    
    cell_id = generate_guid()
    cell.set('id', cell_id)
    cell.set('locklevel', '0')
    cell.set('colspan', '1')
    cell.set('rowspan', '1')
    
    # Special handling for memo fields (multi-line text) - they should span multiple rows
    if field_meta.form_field_type in ['memo', 'multiline']:
        cell.set('rowspan', '4')
    
    cell_labelid = generate_guid()
    cell.set('labelid', cell_labelid)
    
    # Add cell labels
    cell_labels = ET.SubElement(cell, 'labels')
    cell_label = ET.SubElement(cell_labels, 'label')
    cell_label.set('description', field_meta.display_name)
    cell_label.set('languagecode', '1033')
    
    # Add control
    control = ET.SubElement(cell, 'control')
    control.set('id', field_name)
    
    # Get the appropriate classid for this field type
    from formxml_constants import get_classid_for_field_type
    classid = get_classid_for_field_type(field_meta.form_field_type)
    control.set('classid', classid)
    control.set('datafieldname', field_name)
    control.set('disabled', 'false')


def _prettify_xml(elem: ET.Element) -> str:
    """
    Return a pretty-printed XML string with proper indentation.
    
    Args:
        elem: Root XML element
        
    Returns:
        Formatted XML string
    """
    # Use minidom for pretty printing
    from xml.dom import minidom
    
    rough_string = ET.tostring(elem, encoding='utf-8')
    reparsed = minidom.parseString(rough_string)
    
    # Get pretty XML but skip the XML declaration (we'll add our own)
    pretty = reparsed.toprettyxml(indent='  ', encoding='utf-8').decode('utf-8')
    
    # Remove extra blank lines
    lines = [line for line in pretty.split('\n') if line.strip()]
    
    return '\n'.join(lines)


def create_quickcreate_form_files(
    entity_name: str,
    fields: List[str],
    entity_xml_path: Path,
    quickcreate_dir: Path,
    introduced_version: str = "1.0.0.0",
    use_single_column: bool = True
) -> Tuple[str, Path, Path]:
    """
    Create both managed and unmanaged Quick Create form XML files.
    
    Args:
        entity_name: Logical name of the entity
        fields: List of field logical names
        entity_xml_path: Path to Entity.xml file
        quickcreate_dir: Directory for Quick Create forms (will be created if doesn't exist)
        introduced_version: Solution version
        use_single_column: Use single column (True) or 3-column template (False)
        
    Returns:
        Tuple of (form_guid, unmanaged_path, managed_path)
    """
    # Read entity definition to get field metadata
    entity_fields = read_entity_definition(entity_xml_path)
    
    # Generate new GUID for this form
    form_guid = generate_guid()
    
    # Create the XML content
    xml_content = create_quickcreate_xml_structure(
        entity_name=entity_name,
        fields=fields,
        entity_fields=entity_fields,
        form_guid=form_guid,
        introduced_version=introduced_version,
        use_single_column=use_single_column
    )
    
    # Create quickCreate directory if it doesn't exist
    quickcreate_dir.mkdir(parents=True, exist_ok=True)
    
    # Define file paths
    unmanaged_path = quickcreate_dir / f"{form_guid}.xml"
    managed_path = quickcreate_dir / f"{form_guid}_managed.xml"
    
    # Write both files (content is identical)
    with open(unmanaged_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    with open(managed_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
    
    return form_guid, unmanaged_path, managed_path


def get_smart_default_fields(entity_fields: List[EntityField], entity_name: str, max_fields: int = 5) -> List[str]:
    """
    Select smart default fields for a Quick Create form.
    
    Logic:
    1. Always include name field (required)
    2. Always include ownerid (required)
    3. Add required custom fields
    4. Add important text/lookup fields
    5. Limit to max_fields total
    
    Args:
        entity_fields: List of EntityField objects
        entity_name: Entity logical name
        max_fields: Maximum number of fields to include
        
    Returns:
        List of field logical names
    """
    selected = []
    
    # Add name field (always first)
    entity_prefix = entity_name.split('_')[0] if '_' in entity_name else entity_name
    name_field = f"{entity_prefix}_name"
    selected.append(name_field)
    
    # Add owner field (always second)
    selected.append('ownerid')
    
    # Get required custom fields
    required_fields = [
        f for f in entity_fields 
        if f.required_level == 'required' and f.is_custom
    ]
    
    # Add required fields (up to limit)
    for field in required_fields:
        if len(selected) >= max_fields:
            break
        if field.logical_name not in selected:
            selected.append(field.logical_name)
    
    # If we still have room, add important field types (text, lookup, choice)
    if len(selected) < max_fields:
        important_types = ['text', 'email', 'lookup', 'optionset', 'choice']
        important_fields = [
            f for f in entity_fields
            if f.form_field_type in important_types and f.is_custom
        ]
        
        for field in important_fields:
            if len(selected) >= max_fields:
                break
            if field.logical_name not in selected:
                selected.append(field.logical_name)
    
    return selected
