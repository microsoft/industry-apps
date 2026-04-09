#!/usr/bin/env python3
"""
Test script to add a section to the Sample form.
"""

import sys
from pathlib import Path

# Add ui-tools/scripts to path
scripts_dir = Path(__file__).resolve().parent.parent.parent / "ui-tools" / "scripts"
sys.path.insert(0, str(scripts_dir))

from form_operations import add_section_to_tab


def main():
    """Add a one-column section to the Custom Tab in Sample form."""
    
    # Paths to Sample entity's main form
    form_dir = Path(__file__).resolve().parent.parent / "Test" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main"
    unmanaged_path = form_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"
    managed_path = form_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}_managed.xml"
    
    if not unmanaged_path.exists():
        print(f"❌ ERROR: Sample form not found at {unmanaged_path}")
        return 1
    
    print(f"Adding 'Details' section to Custom Tab in Sample form...")
    print("=" * 80)
    
    try:
        # Add section (section name will be auto-generated as "secDetails")
        form = add_section_to_tab(
            unmanaged_path=unmanaged_path,
            tab_name="Custom Tab",
            section_label="Details",
            columns=1,
            managed_path=managed_path,
            create_backup=True
        )
        
        print("=" * 80)
        print("✅ SUCCESS! Section added to Sample form.")
        
        # Show the section name that was generated
        custom_tab = form.get_tab_by_name("Custom Tab")
        if custom_tab and custom_tab.columns and custom_tab.columns[0].sections:
            print(f"\nSections in Custom Tab:")
            for i, section in enumerate(custom_tab.columns[0].sections):
                section_label = section.labels[0].description if section.labels else "(No label)"
                print(f"  [{i}] {section.name} - '{section_label}'")
        
        print(f"\nNext steps:")
        print(f"1. Review the changes in git diff")
        print(f"2. Import the Test solution to Dataverse")
        print(f"3. Verify the 'Details' section appears in Custom Tab")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
