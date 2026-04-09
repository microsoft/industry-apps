"""
High-level operations for modifying Dataverse form XML files.

This module provides convenient functions for common form modification tasks,
handling both unmanaged and managed form files automatically.
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Union

from formxml_parser import FormXmlParser, FormDefinition, generate_section_name, Row, Cell, Control, Label, generate_guid
from formxml_constants import get_classid_for_field_type


def backup_forms(unmanaged_path: Path, managed_path: Optional[Path] = None, 
                 backups_dir: Optional[Path] = None) -> Tuple[Path, Optional[Path]]:
    """
    Create timestamped backups of form files.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        managed_path: Path to the managed form XML file (optional)
        backups_dir: Directory for backups (defaults to test/backups/)
        
    Returns:
        Tuple of (unmanaged_backup_path, managed_backup_path)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Default backups directory
    if backups_dir is None:
        # Assume we're in a test/scripts context, go up to test/backups
        backups_dir = Path(__file__).resolve().parent.parent / "backups"
    
    backups_dir.mkdir(exist_ok=True)
    
    # Backup unmanaged
    unmanaged_backup_name = f"{unmanaged_path.stem}_{timestamp}.bak.xml"
    unmanaged_backup = backups_dir / unmanaged_backup_name
    shutil.copy2(unmanaged_path, unmanaged_backup)
    
    # Backup managed if provided
    managed_backup = None
    if managed_path and managed_path.exists():
        managed_backup_name = f"{managed_path.stem}_{timestamp}.bak.xml"
        managed_backup = backups_dir / managed_backup_name
        shutil.copy2(managed_path, managed_backup)
    
    return unmanaged_backup, managed_backup


def save_forms(form: FormDefinition, unmanaged_path: Path, 
               managed_path: Optional[Path] = None) -> None:
    """
    Save a FormDefinition to both unmanaged and managed files.
    
    Args:
        form: The FormDefinition to save
        unmanaged_path: Path to the unmanaged form XML file
        managed_path: Path to the managed form XML file (optional)
    """
    # Save unmanaged
    FormXmlParser.write_file(form, unmanaged_path)
    
    # Save managed if provided
    if managed_path and managed_path.exists():
        FormXmlParser.write_file(form, managed_path)


def add_tab_to_form(unmanaged_path: Path, tab_name: str, tab_label: str,
                    managed_path: Optional[Path] = None,
                    create_backup: bool = True,
                    skip_if_exists: bool = True,
                    create_default_section: bool = True) -> FormDefinition:
    """
    Add a new tab to a form with an optional default section.
    
    This function:
    - Creates backups of both files (if create_backup=True)
    - Loads the unmanaged form
    - Checks if tab already exists (if skip_if_exists=True)
    - Adds a new tab with the specified name and label
    - Optionally includes a default section following UI conventions (create_default_section=True)
    - Auto-generates header/footer if this is the first user tab
    - Saves to both unmanaged and managed files
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Internal name for the tab (e.g., "tab_custom")
        tab_label: Display label for the tab (e.g., "Custom Tab")
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        skip_if_exists: If True, skip adding tab if it already exists (default: True)
        create_default_section: Whether to create a default section in the tab (default: True)
                               Set to False when building from YAML with explicit sections
        
    Returns:
        The modified FormDefinition
        
    Example:
        >>> unmanaged = Path("test/Test/src/Entities/appbase_Sample/FormXml/main/form.xml")
        >>> managed = Path("test/Test/src/Entities/appbase_Sample/FormXml/main/form_managed.xml")
        >>> form = add_tab_to_form(unmanaged, "tab_details", "Details", managed)
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Check if tab already exists
    existing_tab = form.get_tab_by_name(tab_name)
    if existing_tab:
        if skip_if_exists:
            print(f"Tab '{tab_name}' already exists, skipping...")
            return form
        else:
            raise ValueError(f"Tab '{tab_name}' already exists in form")
    
    # Add tab (optionally creates default section and header/footer)
    form.add_tab(tab_name, tab_label, create_default_section=create_default_section)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def add_section_to_tab(unmanaged_path: Path, tab_name: str, 
                       section_label: str,
                       section_name: Optional[str] = None,
                       columns: int = 1,
                       managed_path: Optional[Path] = None,
                       create_backup: bool = True,
                       skip_if_exists: bool = True) -> FormDefinition:
    """
    Add a new section to an existing tab.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab to add the section to
        section_label: Display label for the section
        section_name: Internal name for the section (optional, auto-generated from label if not provided)
                      Example: "My Section" -> "secMySection"
        columns: Number of columns in the section - accepts 1 or 2 (default: 1)
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        skip_if_exists: If True, skip adding section if it already exists (default: True)
        
    Returns:
        The modified FormDefinition
        
    Example:
        # Add a 1-column section
        add_section_to_tab(form_path, "General", "Contact Information")
        
        # Add a 2-column section
        add_section_to_tab(form_path, "General", "Address", columns=2)
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Auto-generate section name if not provided
    if section_name is None:
        section_name = generate_section_name(section_label)
    
    # Check if section already exists
    existing_section = tab.get_section_by_name(section_name)
    if existing_section:
        if skip_if_exists:
            print(f"Section '{section_name}' already exists in tab '{tab_name}', skipping...")
            return form
        else:
            raise ValueError(f"Section '{section_name}' already exists in tab '{tab_name}'")
    
    # Add section to the tab
    tab.add_section(section_name, section_label, columns)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def add_field_to_section(unmanaged_path: Path, tab_name: str, section_name: str,
                         field_name: str, field_label: str, field_type: str,
                         managed_path: Optional[Path] = None,
                         create_backup: bool = True) -> FormDefinition:
    """
    Add a field control to a section.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab containing the section
        section_name: Name or label of the section to add the field to
        field_name: Schema name of the field (e.g., "appbase_status")
        field_label: Display label for the field (e.g., "Status")
        field_type: Type of field (e.g., "text", "optionset", "lookup", "datetime")
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        
    Returns:
        The modified FormDefinition
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Find the section
    section = tab.get_section_by_name(section_name)
    if not section:
        raise ValueError(f"Section '{section_name}' not found in tab '{tab_name}'")
    
    # Add field to the section
    section.add_field(field_name, field_label, field_type)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def add_subgrid_to_section(unmanaged_path: Path, tab_name: str, section_name: str,
                           subgrid_id: str, subgrid_label: str,
                           relationship_name: str, target_entity: str, view_id: str,
                           managed_path: Optional[Path] = None,
                           create_backup: bool = True) -> FormDefinition:
    """
    Add a subgrid control to a section.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab containing the section
        section_name: Name or label of the section to add the subgrid to
        subgrid_id: Unique ID for the subgrid control
        subgrid_label: Display label for the subgrid
        relationship_name: Schema name of the relationship
        target_entity: Logical name of the related entity
        view_id: GUID of the view to display
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        
    Returns:
        The modified FormDefinition
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Find the section
    section = tab.get_section_by_name(section_name)
    if not section:
        raise ValueError(f"Section '{section_name}' not found in tab '{tab_name}'")
    
    # Add subgrid to the section
    section.add_subgrid(subgrid_id, subgrid_label, relationship_name, target_entity, view_id)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def update_section_columns(unmanaged_path: Path, tab_name: str, section_id: str,
                           new_columns: int,
                           managed_path: Optional[Path] = None,
                           create_backup: bool = True) -> FormDefinition:
    """
    Update the column count for a section (typically to convert a 1-column OOB section to 2 columns).
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab containing the section
        section_id: GUID of the section to modify
        new_columns: Number of columns (1 or 2)
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        
    Returns:
        The modified FormDefinition
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Update section columns
    success = tab.update_section_columns(section_id, new_columns)
    if not success:
        raise ValueError(f"Section with ID '{section_id}' not found in tab '{tab_name}'")
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def add_fields_to_section_by_rows(unmanaged_path: Path, tab_name: str, section_name: str,
                                   rows: List[List[Union[str, dict, None]]],
                                   field_metadata: Dict[str, Tuple[str, str]],
                                   managed_path: Optional[Path] = None,
                                   create_backup: bool = False,
                                   skip_if_exists: bool = True) -> FormDefinition:
    """
    Add fields to a section using explicit row/column positioning.
    
    This function provides precise control over field placement in multi-column sections.
    Each row is a list that can contain:
    - str: Field schema name (creates a cell with that field's control)
    - None: Empty cell (creates a cell with an empty label, no control)
    - dict: Field with spanning, e.g., {'field': 'fieldname', 'colspan': 2, 'rowspan': 1}
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab containing the section
        section_name: Name or label of the section to add fields to
        rows: List of rows, where each row is a list of field specifications
        field_metadata: Dict mapping field schema name to (display_name, field_type)
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: False)
        skip_if_exists: Skip fields that already exist in the section (default: True)
        
    Returns:
        The modified FormDefinition
        
    Example:
        rows = [
            ['appbase_name', 'appbase_textfield'],      # Row 1: Name and Text in 2 columns
            ['ownerid', None],                           # Row 2: Owner and empty cell
            [{'field': 'appbase_memo', 'colspan': 2}]   # Row 3: Memo spanning both columns
        ]
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Find the section
    section = tab.get_section_by_name(section_name)
    if not section:
        raise ValueError(f"Section '{section_name}' not found in tab '{tab_name}'")
    
    # Get existing field names if skip_if_exists is True
    existing_fields = set()
    if skip_if_exists:
        for row in section.rows:
            for cell in row.cells:
                if cell.control:
                    existing_fields.add(cell.control.datafieldname)
    
    # Build rows
    for row_spec in rows:
        row = Row()
        
        for cell_spec in row_spec:
            # Determine cell specifications
            field_name = None
            colspan = 1
            rowspan = 1
            
            if isinstance(cell_spec, str):
                # Simple field name
                field_name = cell_spec
            elif isinstance(cell_spec, dict):
                # Field with spanning attributes
                field_name = cell_spec.get('field')
                colspan = cell_spec.get('colspan', 1)
                rowspan = cell_spec.get('rowspan', 1)
            elif cell_spec is None:
                # Empty cell - just create a cell with empty label
                pass
            else:
                raise ValueError(f"Invalid cell specification: {cell_spec}. Must be str, dict, or None.")
            
            # Create the cell
            if field_name:
                # Skip if field already exists
                if skip_if_exists and field_name in existing_fields:
                    print(f"Field '{field_name}' already exists in section '{section_name}', skipping")
                    continue
                
                # Get field metadata
                if field_name not in field_metadata:
                    raise ValueError(f"Field '{field_name}' not found in field_metadata")
                
                display_name, field_type = field_metadata[field_name]
                classid = get_classid_for_field_type(field_type)
                
                # Auto-set rowspan for memo fields (default to 4 rows) if not explicitly specified
                if field_type == 'memo' and isinstance(cell_spec, str):
                    # Only auto-set if field was specified as simple string (not dict with explicit rowspan)
                    rowspan = 4
                
                # Create control
                control = Control(
                    id=field_name,
                    classid=classid,
                    datafieldname=field_name,
                    disabled=False
                )
                
                # Create label
                label = Label(description=display_name, languagecode="1033")
                
                # Create cell with control
                cell = Cell(
                    id=generate_guid(),
                    control=control,
                    labels=[label],
                    locklevel=0,
                    colspan=colspan,
                    rowspan=rowspan
                )
            else:
                # Empty cell - no control, just label
                label = Label(description="", languagecode="1033")
                cell = Cell(
                    id=generate_guid(),
                    labels=[label],
                    locklevel=0,
                    colspan=colspan,
                    rowspan=rowspan
                )
            
            row.cells.append(cell)
        
        # Add row to section
        if row.cells:  # Only add non-empty rows
            section.rows.append(row)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def remove_tab_from_form(unmanaged_path: Path, tab_name: str,
                         managed_path: Optional[Path] = None,
                         create_backup: bool = True) -> FormDefinition:
    """
    Remove a tab from a form.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab to remove
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        
    Returns:
        The modified FormDefinition
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Remove tab
    success = form.remove_tab(tab_name)
    if not success:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def remove_field_from_section(unmanaged_path: Path, tab_name: str, section_name: str,
                               field_name: str,
                               managed_path: Optional[Path] = None,
                               create_backup: bool = True) -> FormDefinition:
    """
    Remove a field from a section.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab containing the section
        section_name: Name or label of the section containing the field
        field_name: Schema name of the field to remove
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        
    Returns:
        The modified FormDefinition
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Find the section
    section = tab.get_section_by_name(section_name)
    if not section:
        raise ValueError(f"Section '{section_name}' not found in tab '{tab_name}'")
    
    # Remove field from the section
    success = section.remove_field(field_name)
    if not success:
        raise ValueError(f"Field '{field_name}' not found in section '{section_name}'")
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def add_fields_to_section(unmanaged_path: Path, tab_name: str, section_name: str,
                          fields: list[tuple[str, str, str]],
                          managed_path: Optional[Path] = None,
                          create_backup: bool = True,
                          skip_if_exists: bool = True) -> FormDefinition:
    """
    Add multiple fields to a section. 
    
    For 1-column sections: each field is added in a new row.
    For 2-column sections: fields are added two per row (side-by-side).
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab containing the section
        section_name: Name or label of the section to add fields to
        fields: List of (field_name, field_label, field_type) tuples
                Example: [("appbase_name", "Name", "text"), 
                         ("appbase_email", "Email", "email")]
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        skip_if_exists: If True, skip fields that already exist in the section (default: True)
        
    Returns:
        The modified FormDefinition
        
    Example:
        # Add fields to a 1-column section (each in its own row)
        add_fields_to_section(
            form_path, 
            "General", 
            "Contact Info",
            [
                ("appbase_firstname", "First Name", "text"),
                ("appbase_lastname", "Last Name", "text"),
                ("appbase_email", "Email", "email")
            ]
        )
        
        # Add fields to a 2-column section (two per row)
        add_fields_to_section(
            form_path,
            "Details", 
            "Address",
            [
                ("appbase_city", "City", "text"),
                ("appbase_state", "State", "text"),
                ("appbase_zip", "Zip", "text"),
                ("appbase_country", "Country", "text")
            ]
        )
    """
    # Create backups
    if create_backup:
        backup_forms(unmanaged_path, managed_path)
    
    # Load form
    form = FormXmlParser.parse_file(unmanaged_path)
    
    # Find the tab
    tab = form.get_tab_by_name(tab_name)
    if not tab:
        raise ValueError(f"Tab '{tab_name}' not found in form")
    
    # Find the section
    section = tab.get_section_by_name(section_name)
    if not section:
        raise ValueError(f"Section '{section_name}' not found in tab '{tab_name}'")
    
    # If skip_if_exists, filter out fields that already exist in the section
    if skip_if_exists:
        # Get existing field names in the section
        existing_fields = set()
        for row in section.rows:
            for cell in row.cells:
                if cell.control and cell.control.datafieldname:
                    existing_fields.add(cell.control.datafieldname)
        
        # Filter out existing fields
        fields_to_add = []
        for field_name, field_label, field_type in fields:
            if field_name in existing_fields:
                print(f"Field '{field_name}' already exists in section '{section_name}', skipping...")
            else:
                fields_to_add.append((field_name, field_label, field_type))
        
        # If no fields to add, return early
        if not fields_to_add:
            print(f"All fields already exist in section '{section_name}', nothing to add.")
            return form
        
        fields = fields_to_add
    
    # Determine if this is a 2-column section
    is_two_column = section.columns == 11
    
    # Add fields
    if is_two_column:
        # Add two fields per row
        for i in range(0, len(fields), 2):
            # Add first field in the pair (creates new row)
            field_name, field_label, field_type = fields[i]
            section.add_field(field_name, field_label, field_type)
            
            # Add second field if it exists (adds to last row)
            if i + 1 < len(fields):
                field_name, field_label, field_type = fields[i + 1]
                section.add_field(field_name, field_label, field_type, 
                                row_index=-1, cell_position=1)
    else:
        # Add each field in its own row
        for field_name, field_label, field_type in fields:
            section.add_field(field_name, field_label, field_type)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form
