#!/usr/bin/env python3
"""
Example script demonstrating programmatic usage of the FormXml library.

This script shows how to:
1. Parse an existing FormXml file
2. Inspect the form structure
3. Add new tabs, sections, and fields
4. Save the modified form

Run this script with a FormXml file path as argument:
    python formxml_example.py path/to/form.xml
"""

import sys
from pathlib import Path
from formxml_parser import FormXmlParser, generate_guid


def inspect_form(form):
    """Print detailed information about a form."""
    print("=" * 80)
    print("FORM INSPECTION")
    print("=" * 80)
    print(f"\nForm Name: {form.form_name}")
    print(f"Form ID: {form.formid}")
    print(f"Presentation Type: {form.form_presentation}")
    print(f"Activation State: {form.form_activation_state}")
    print(f"Header Density: {form.headerdensity}")
    print(f"\nNumber of Tabs: {len(form.tabs)}")
    
    for i, tab in enumerate(form.tabs):
        tab_label = tab.labels[0].description if tab.labels else tab.name or "(No label)"
        print(f"\n  Tab {i + 1}: {tab_label}")
        print(f"    ID: {tab.id}")
        print(f"    User Defined: {tab.is_user_defined}")
        print(f"    Columns: {len(tab.columns)}")
        
        for col_idx, column in enumerate(tab.columns):
            print(f"    Column {col_idx + 1}: {len(column.sections)} sections")
            
            for sec_idx, section in enumerate(column.sections):
                section_label = section.labels[0].description if section.labels else section.name or "(No label)"
                row_count = len(section.rows)
                control_count = sum(1 for row in section.rows for cell in row.cells if cell.control)
                
                print(f"      Section {sec_idx + 1}: {section_label}")
                print(f"        ID: {section.id}")
                print(f"        Rows: {row_count}, Controls: {control_count}")
                print(f"        Layout Columns: {section.columns}")
                
                # List some fields
                field_names = []
                for row in section.rows:
                    for cell in row.cells:
                        if cell.control and cell.control.datafieldname:
                            field_names.append(cell.control.datafieldname)
                
                if field_names:
                    print(f"        Fields: {', '.join(field_names[:5])}")
                    if len(field_names) > 5:
                        print(f"                ... and {len(field_names) - 5} more")


def add_custom_tab_example(form):
    """Example: Add a custom tab with sections and fields."""
    print("\n" + "=" * 80)
    print("ADDING CUSTOM TAB")
    print("=" * 80)
    
    # Add a new tab
    print("\n1. Adding new 'Custom Data' tab...")
    custom_tab = form.add_tab("tab_custom", "Custom Data")
    print(f"   Created tab with ID: {custom_tab.id}")
    
    # Add sections to the tab
    print("\n2. Adding 'Basic Information' section...")
    basic_section = custom_tab.add_section("section_basic", "Basic Information", columns=2)
    print(f"   Created section with ID: {basic_section.id}")
    
    print("\n3. Adding 'Advanced Details' section...")
    advanced_section = custom_tab.add_section("section_advanced", "Advanced Details", columns=1)
    print(f"   Created section with ID: {advanced_section.id}")
    
    # Add fields to basic section
    print("\n4. Adding fields to 'Basic Information' section...")
    fields_to_add = [
        ("appbase_customtext", "Custom Text Field", "text"),
        ("appbase_custompriority", "Custom Priority", "optionset"),
        ("appbase_customdate", "Custom Date", "datetime"),
        ("appbase_customowner", "Custom Owner", "lookup"),
    ]
    
    for field_name, field_label, field_type in fields_to_add:
        cell = basic_section.add_field(field_name, field_label, field_type)
        print(f"   Added {field_type} field '{field_label}' ({field_name})")
    
    # Add fields to advanced section
    print("\n5. Adding fields to 'Advanced Details' section...")
    advanced_section.add_field("appbase_customamount", "Custom Amount", "currency")
    print(f"   Added currency field 'Custom Amount'")
    
    advanced_section.add_field("appbase_customnotes", "Custom Notes", "multiline")
    print(f"   Added multiline field 'Custom Notes'")
    
    # Add a subgrid (example with placeholder IDs)
    print("\n6. Adding subgrid to 'Advanced Details' section...")
    try:
        # Note: In a real scenario, you'd use actual relationship names and view IDs
        subgrid_cell = advanced_section.add_subgrid(
            subgrid_id="Subgrid_custom_items",
            subgrid_label="Related Custom Items",
            relationship_name="appbase_customitem_parent",
            target_entity="appbase_customitem",
            view_id=generate_guid()  # In reality, this should be an existing view GUID
        )
        print(f"   Added subgrid 'Related Custom Items'")
        print(f"   Note: The view GUID is generated and should be replaced with an actual view ID")
    except Exception as e:
        print(f"   Error adding subgrid: {e}")
    
    print("\n✓ Custom tab creation complete!")


def modify_existing_tab_example(form):
    """Example: Modify an existing tab by adding a field."""
    print("\n" + "=" * 80)
    print("MODIFYING EXISTING TAB")
    print("=" * 80)
    
    # Try to find the "General" tab (common in many forms)
    tab = form.get_tab_by_name("General")
    
    if not tab:
        print("\n✗ 'General' tab not found. Trying first tab instead...")
        if form.tabs:
            tab = form.tabs[0]
            tab_name = tab.labels[0].description if tab.labels else "Unknown"
            print(f"✓ Using first tab: {tab_name}")
        else:
            print("✗ No tabs found in form!")
            return
    else:
        print("\n✓ Found 'General' tab")
    
    # Find a section in the tab
    if tab.columns and tab.columns[0].sections:
        section = tab.columns[0].sections[0]
        section_label = section.labels[0].description if section.labels else "Unknown"
        print(f"✓ Found section: {section_label}")
        
        # Add a new field to this section
        print(f"\nAdding new field to '{section_label}' section...")
        try:
            section.add_field(
                field_name="appbase_addedfield",
                field_label="Added Field",
                field_type="text",
                row_index=-1  # Add to last row
            )
            print("✓ Successfully added 'Added Field' to the section")
        except Exception as e:
            print(f"✗ Error adding field: {e}")
    else:
        print("✗ No sections found in tab!")


def remove_field_example(form):
    """Example: Remove a field from a section."""
    print("\n" + "=" * 80)
    print("REMOVING FIELD")
    print("=" * 80)
    
    # Find the custom tab we added earlier
    tab = form.get_tab_by_name("Custom Data")
    
    if not tab:
        print("\n✗ 'Custom Data' tab not found (was it added?)")
        return
    
    print("\n✓ Found 'Custom Data' tab")
    
    # Find the basic section
    section = tab.get_section_by_name("Basic Information")
    
    if not section:
        print("✗ 'Basic Information' section not found")
        return
    
    print("✓ Found 'Basic Information' section")
    
    # Remove a field
    field_to_remove = "appbase_customtext"
    print(f"\nRemoving field '{field_to_remove}'...")
    
    if section.remove_field(field_to_remove):
        print(f"✓ Successfully removed field '{field_to_remove}'")
    else:
        print(f"✗ Field '{field_to_remove}' not found in section")


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python formxml_example.py <path_to_formxml_file>")
        print("\nExample:")
        print("  python formxml_example.py government/court-case-management/src/Entities/appbase_CourtCase/FormXml/main/form.xml")
        return 1
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        return 1
    
    print(f"Loading FormXml file: {file_path}")
    print()
    
    try:
        # Parse the form
        form = FormXmlParser.parse_file(file_path)
        print("✓ Successfully parsed FormXml file")
        
        # Inspect the form
        inspect_form(form)
        
        # Add a custom tab with sections and fields
        add_custom_tab_example(form)
        
        # Modify an existing tab
        modify_existing_tab_example(form)
        
        # Remove a field
        remove_field_example(form)
        
        # Save the modified form
        output_path = file_path.parent / f"{file_path.stem}_modified{file_path.suffix}"
        print("\n" + "=" * 80)
        print("SAVING MODIFIED FORM")
        print("=" * 80)
        print(f"\nSaving to: {output_path}")
        
        FormXmlParser.write_file(form, output_path)
        print("✓ Successfully saved modified form")
        
        print("\n" + "=" * 80)
        print("COMPLETE")
        print("=" * 80)
        print(f"\nOriginal file: {file_path}")
        print(f"Modified file: {output_path}")
        print("\nYou can now:")
        print("  1. Compare the files to see the changes")
        print("  2. Use the modified file in your Dataverse solution")
        print("  3. Run 'python formxml_tool.py validate' to check the form")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
