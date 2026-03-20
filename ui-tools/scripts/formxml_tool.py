#!/usr/bin/env python3
"""
Command-line tool for manipulating Dataverse FormXml files.

This tool provides commands for adding, removing, and modifying form elements
such as tabs, sections, fields, and subgrids in FormXml files.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional

from formxml_parser import FormXmlParser, FormDefinition
from formxml_constants import get_classid_for_field_type, FIELD_TYPE_TO_CLASSID


def list_structure(args):
    """List the structure of a FormXml file."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        print(f"Form: {form.form_name}")
        print(f"Form ID: {form.formid}")
        print(f"Presentation: {form.form_presentation}")
        print(f"Activation State: {form.form_activation_state}")
        print(f"\nTabs ({len(form.tabs)}):")
        
        for i, tab in enumerate(form.tabs):
            tab_label = tab.labels[0].description if tab.labels else tab.name or "(No label)"
            print(f"  [{i}] {tab_label} (ID: {tab.id})")
            
            for col_idx, column in enumerate(tab.columns):
                print(f"      Column {col_idx} ({len(column.sections)} sections):")
                
                for sec_idx, section in enumerate(column.sections):
                    section_label = section.labels[0].description if section.labels else section.name or "(No label)"
                    field_count = sum(1 for row in section.rows for cell in row.cells if cell.control)
                    print(f"        [{sec_idx}] {section_label} ({field_count} controls)")
                    
                    if args.verbose:
                        for row in section.rows:
                            for cell in row.cells:
                                if cell.control:
                                    field_label = cell.labels[0].description if cell.labels else "(No label)"
                                    field_name = cell.control.datafieldname or cell.control.id
                                    print(f"          - {field_label}: {field_name}")
        
        if form.header:
            print(f"\nHeader (ID: {form.header.id})")
            
        if form.footer:
            print(f"Footer (ID: {form.footer.id})")
            
        return 0
        
    except Exception as e:
        print(f"Error parsing form: {e}")
        return 1


def add_tab(args):
    """Add a new tab to a form."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        # Add the tab
        tab = form.add_tab(args.name, args.label, args.index)
        
        print(f"Added tab '{args.label}' with ID: {tab.id}")
        
        # Write back
        output_path = Path(args.output) if args.output else file_path
        FormXmlParser.write_file(form, output_path)
        print(f"Saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error adding tab: {e}")
        return 1


def remove_tab(args):
    """Remove a tab from a form."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        # Remove the tab
        if form.remove_tab(args.name):
            print(f"Removed tab '{args.name}'")
            
            # Write back
            output_path = Path(args.output) if args.output else file_path
            FormXmlParser.write_file(form, output_path)
            print(f"Saved to: {output_path}")
            
            return 0
        else:
            print(f"Error: Tab '{args.name}' not found")
            return 1
        
    except Exception as e:
        print(f"Error removing tab: {e}")
        return 1


def add_section(args):
    """Add a new section to a tab."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        # Find the tab
        tab = form.get_tab_by_name(args.tab)
        if not tab:
            print(f"Error: Tab '{args.tab}' not found")
            return 1
            
        # Add the section
        section = tab.add_section(args.name, args.label, args.columns)
        
        print(f"Added section '{args.label}' to tab '{args.tab}' with ID: {section.id}")
        
        # Write back
        output_path = Path(args.output) if args.output else file_path
        FormXmlParser.write_file(form, output_path)
        print(f"Saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error adding section: {e}")
        return 1


def add_field(args):
    """Add a new field to a section."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        # Find the tab
        tab = form.get_tab_by_name(args.tab)
        if not tab:
            print(f"Error: Tab '{args.tab}' not found")
            return 1
            
        # Find the section
        section = tab.get_section_by_name(args.section)
        if not section:
            print(f"Error: Section '{args.section}' not found in tab '{args.tab}'")
            return 1
            
        # Add the field
        cell = section.add_field(
            field_name=args.field,
            field_label=args.label,
            field_type=args.type,
            row_index=args.row_index,
            cell_position=args.cell_position
        )
        
        print(f"Added field '{args.label}' ({args.field}) to section '{args.section}' with cell ID: {cell.id}")
        
        # Write back
        output_path = Path(args.output) if args.output else file_path
        FormXmlParser.write_file(form, output_path)
        print(f"Saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error adding field: {e}")
        import traceback
        traceback.print_exc()
        return 1


def remove_field(args):
    """Remove a field from a section."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        # Find the tab
        tab = form.get_tab_by_name(args.tab)
        if not tab:
            print(f"Error: Tab '{args.tab}' not found")
            return 1
            
        # Find the section
        section = tab.get_section_by_name(args.section)
        if not section:
            print(f"Error: Section '{args.section}' not found in tab '{args.tab}'")
            return 1
            
        # Remove the field
        if section.remove_field(args.field):
            print(f"Removed field '{args.field}' from section '{args.section}'")
            
            # Write back
            output_path = Path(args.output) if args.output else file_path
            FormXmlParser.write_file(form, output_path)
            print(f"Saved to: {output_path}")
            
            return 0
        else:
            print(f"Error: Field '{args.field}' not found in section '{args.section}'")
            return 1
        
    except Exception as e:
        print(f"Error removing field: {e}")
        return 1


def add_subgrid(args):
    """Add a new subgrid to a section."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        # Find the tab
        tab = form.get_tab_by_name(args.tab)
        if not tab:
            print(f"Error: Tab '{args.tab}' not found")
            return 1
            
        # Find the section
        section = tab.get_section_by_name(args.section)
        if not section:
            print(f"Error: Section '{args.section}' not found in tab '{args.tab}'")
            return 1
            
        # Add the subgrid
        cell = section.add_subgrid(
            subgrid_id=args.id,
            subgrid_label=args.label,
            relationship_name=args.relationship,
            target_entity=args.target_entity,
            view_id=args.view_id,
            row_index=args.row_index
        )
        
        print(f"Added subgrid '{args.label}' ({args.id}) to section '{args.section}' with cell ID: {cell.id}")
        
        # Write back
        output_path = Path(args.output) if args.output else file_path
        FormXmlParser.write_file(form, output_path)
        print(f"Saved to: {output_path}")
        
        return 0
        
    except Exception as e:
        print(f"Error adding subgrid: {e}")
        import traceback
        traceback.print_exc()
        return 1


def validate_form(args):
    """Validate a FormXml file."""
    file_path = Path(args.file)
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
        
    try:
        form = FormXmlParser.parse_file(file_path)
        
        errors = []
        warnings = []
        
        # Basic validation
        if not form.formid:
            errors.append("Form is missing formid")
            
        if not form.tabs:
            warnings.append("Form has no tabs")
            
        # Validate tabs
        for tab_idx, tab in enumerate(form.tabs):
            if not tab.labels:
                warnings.append(f"Tab {tab_idx} has no label")
                
            if not tab.columns:
                warnings.append(f"Tab {tab_idx} has no columns")
                
            # Validate sections
            for col_idx, column in enumerate(tab.columns):
                for sec_idx, section in enumerate(column.sections):
                    if not section.labels:
                        warnings.append(f"Section {sec_idx} in tab {tab_idx}, column {col_idx} has no label")
                        
                    # Validate controls
                    for row_idx, row in enumerate(section.rows):
                        for cell_idx, cell in enumerate(row.cells):
                            if cell.control:
                                # Check classid is valid
                                if not cell.control.classid:
                                    errors.append(
                                        f"Control in tab {tab_idx}, section {sec_idx}, "
                                        f"row {row_idx}, cell {cell_idx} has no classid"
                                    )
                                    
                                # Check subgrid has parameters
                                if cell.control.indication_of_subgrid and not cell.control.subgrid_params:
                                    errors.append(
                                        f"Subgrid control in tab {tab_idx}, section {sec_idx}, "
                                        f"row {row_idx}, cell {cell_idx} has no parameters"
                                    )
        
        # Report results
        if errors:
            print("VALIDATION FAILED")
            print(f"\nErrors ({len(errors)}):")
            for error in errors:
                print(f"  - {error}")
        else:
            print("VALIDATION PASSED")
            
        if warnings:
            print(f"\nWarnings ({len(warnings)}):")
            for warning in warnings:
                print(f"  - {warning}")
                
        if not errors and not warnings:
            print("No issues found.")
            
        return 1 if errors else 0
        
    except Exception as e:
        print(f"VALIDATION FAILED")
        print(f"Error parsing form: {e}")
        import traceback
        traceback.print_exc()
        return 1


def list_field_types(args):
    """List all available field types."""
    print("Available field types:")
    print()
    
    # Group by category
    categories = {
        "Text": ["text", "singleline", "multiline", "memo", "richtext"],
        "Number": ["integer", "wholenumber", "decimal", "float", "currency", "money"],
        "Date/Time": ["datetime", "date"],
        "Choice": ["optionset", "picklist", "choice", "twooptions", "boolean", "yesno", "status", "statuscode"],
        "Lookup": ["lookup", "customer", "owner"],
        "Other": ["subgrid", "notes", "quickview", "iframe", "webresource", "spacer"]
    }
    
    for category, types in categories.items():
        print(f"{category}:")
        for field_type in types:
            if field_type in FIELD_TYPE_TO_CLASSID:
                classid = FIELD_TYPE_TO_CLASSID[field_type]
                print(f"  - {field_type:20} {classid}")
        print()
    
    return 0


def main():
    """Main entry point for the CLI tool."""
    parser = argparse.ArgumentParser(
        description="Tool for manipulating Dataverse FormXml files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List form structure
  python formxml_tool.py list CourtCase.xml
  
  # Add a new tab
  python formxml_tool.py add-tab CourtCase.xml --name "tab_evidence" --label "Evidence"
  
  # Add a section to a tab
  python formxml_tool.py add-section CourtCase.xml --tab "General" --name "contact_info" --label "Contact Information"
  
  # Add a field to a section
  python formxml_tool.py add-field CourtCase.xml --tab "General" --section "Details" \\
      --field "appbase_priority" --label "Priority" --type "optionset"
  
  # Add a subgrid
  python formxml_tool.py add-subgrid CourtCase.xml --tab "Parties" --section "Related" \\
      --id "Subgrid_parties" --label "Parties" \\
      --relationship "appbase_courtcaseparty_CourtCase" \\
      --target-entity "appbase_courtcaseparty" \\
      --view-id "{DE397E6C-80E1-48A7-A89C-5B06E1F0ABE7}"
  
  # Validate a form
  python formxml_tool.py validate CourtCase.xml
  
  # List available field types
  python formxml_tool.py list-types
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List structure command
    list_parser = subparsers.add_parser("list", help="List the structure of a form")
    list_parser.add_argument("file", help="Path to the FormXml file")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed field information")
    list_parser.set_defaults(func=list_structure)
    
    # Add tab command
    add_tab_parser = subparsers.add_parser("add-tab", help="Add a new tab to a form")
    add_tab_parser.add_argument("file", help="Path to the FormXml file")
    add_tab_parser.add_argument("--name", required=True, help="Internal name for the tab")
    add_tab_parser.add_argument("--label", required=True, help="Display label for the tab")
    add_tab_parser.add_argument("--index", type=int, help="Position to insert the tab (default: append)")
    add_tab_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    add_tab_parser.set_defaults(func=add_tab)
    
    # Remove tab command
    remove_tab_parser = subparsers.add_parser("remove-tab", help="Remove a tab from a form")
    remove_tab_parser.add_argument("file", help="Path to the FormXml file")
    remove_tab_parser.add_argument("--name", required=True, help="Name of the tab to remove")
    remove_tab_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    remove_tab_parser.set_defaults(func=remove_tab)
    
    # Add section command
    add_section_parser = subparsers.add_parser("add-section", help="Add a new section to a tab")
    add_section_parser.add_argument("file", help="Path to the FormXml file")
    add_section_parser.add_argument("--tab", required=True, help="Name of the tab to add the section to")
    add_section_parser.add_argument("--name", required=True, help="Internal name for the section")
    add_section_parser.add_argument("--label", required=True, help="Display label for the section")
    add_section_parser.add_argument("--columns", type=int, default=1, help="Number of columns in the section (default: 1)")
    add_section_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    add_section_parser.set_defaults(func=add_section)
    
    # Add field command
    add_field_parser = subparsers.add_parser("add-field", help="Add a new field to a section")
    add_field_parser.add_argument("file", help="Path to the FormXml file")
    add_field_parser.add_argument("--tab", required=True, help="Name of the tab")
    add_field_parser.add_argument("--section", required=True, help="Name of the section")
    add_field_parser.add_argument("--field", required=True, help="Schema name of the field")
    add_field_parser.add_argument("--label", required=True, help="Display label for the field")
    add_field_parser.add_argument("--type", required=True, help="Type of field (use 'list-types' to see available types)")
    add_field_parser.add_argument("--row-index", type=int, help="Row index to add to (default: new row)")
    add_field_parser.add_argument("--cell-position", type=int, default=0, help="Position in row (default: 0)")
    add_field_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    add_field_parser.set_defaults(func=add_field)
    
    # Remove field command
    remove_field_parser = subparsers.add_parser("remove-field", help="Remove a field from a section")
    remove_field_parser.add_argument("file", help="Path to the FormXml file")
    remove_field_parser.add_argument("--tab", required=True, help="Name of the tab")
    remove_field_parser.add_argument("--section", required=True, help="Name of the section")
    remove_field_parser.add_argument("--field", required=True, help="Schema name of the field to remove")
    remove_field_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    remove_field_parser.set_defaults(func=remove_field)
    
    # Add subgrid command
    add_subgrid_parser = subparsers.add_parser("add-subgrid", help="Add a new subgrid to a section")
    add_subgrid_parser.add_argument("file", help="Path to the FormXml file")
    add_subgrid_parser.add_argument("--tab", required=True, help="Name of the tab")
    add_subgrid_parser.add_argument("--section", required=True, help="Name of the section")
    add_subgrid_parser.add_argument("--id", required=True, help="Unique ID for the subgrid control")
    add_subgrid_parser.add_argument("--label", required=True, help="Display label for the subgrid")
    add_subgrid_parser.add_argument("--relationship", required=True, help="Relationship schema name")
    add_subgrid_parser.add_argument("--target-entity", required=True, help="Target entity logical name")
    add_subgrid_parser.add_argument("--view-id", required=True, help="View GUID (with braces)")
    add_subgrid_parser.add_argument("--row-index", type=int, help="Row index to add to (default: new row)")
    add_subgrid_parser.add_argument("-o", "--output", help="Output file path (default: overwrite input)")
    add_subgrid_parser.set_defaults(func=add_subgrid)
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a FormXml file")
    validate_parser.add_argument("file", help="Path to the FormXml file")
    validate_parser.set_defaults(func=validate_form)
    
    # List field types command
    list_types_parser = subparsers.add_parser("list-types", help="List available field types")
    list_types_parser.set_defaults(func=list_field_types)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
        
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
