"""
High-level operations for modifying Dataverse form XML files.

This module provides convenient functions for common form modification tasks,
handling both unmanaged and managed form files automatically.
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple

from formxml_parser import FormXmlParser, FormDefinition


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
                    create_backup: bool = True) -> FormDefinition:
    """
    Add a new tab to a form with a default section.
    
    This function:
    - Creates backups of both files (if create_backup=True)
    - Loads the unmanaged form
    - Adds a new tab with the specified name and label
    - The tab includes a default section following UI conventions
    - Auto-generates header/footer if this is the first user tab
    - Saves to both unmanaged and managed files
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Internal name for the tab (e.g., "tab_custom")
        tab_label: Display label for the tab (e.g., "Custom Tab")
        managed_path: Path to the managed form XML file (optional)
        create_backup: Whether to create backup files (default: True)
        
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
    
    # Add tab (formxml_parser's add_tab already creates default section and header/footer)
    form.add_tab(tab_name, tab_label)
    
    # Save forms
    save_forms(form, unmanaged_path, managed_path)
    
    return form


def add_section_to_tab(unmanaged_path: Path, tab_name: str, 
                       section_name: str, section_label: str,
                       columns: int = 1,
                       managed_path: Optional[Path] = None,
                       create_backup: bool = True) -> FormDefinition:
    """
    Add a new section to an existing tab.
    
    Args:
        unmanaged_path: Path to the unmanaged form XML file
        tab_name: Name or label of the tab to add the section to
        section_name: Internal name for the section
        section_label: Display label for the section
        columns: Number of columns in the section (default: 1)
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
