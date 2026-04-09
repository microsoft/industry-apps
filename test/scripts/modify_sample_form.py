#!/usr/bin/env python3
"""
Script to modify the Sample entity's form in the Test solution.
This modifies the actual form files so the solution can be imported to test changes.
"""

import sys
from pathlib import Path

# Add ui-tools/scripts to path to import formxml modules
scripts_dir = Path(__file__).resolve().parent.parent.parent / "ui-tools" / "scripts"
sys.path.insert(0, str(scripts_dir))

from form_operations import add_tab_to_form


def main():
    """Add a tab to the Sample entity's main form."""
    
    # Paths to Sample entity's main form (both unmanaged and managed versions)
    form_dir = Path(__file__).resolve().parent.parent / "Test" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main"
    unmanaged_path = form_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"
    managed_path = form_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}_managed.xml"
    
    if not unmanaged_path.exists():
        print(f"❌ ERROR: Sample form not found at {unmanaged_path}")
        return 1
    
    print(f"Adding 'Custom Tab' to Sample form...")
    print("=" * 80)
    
    try:
        # Add tab using the form_operations library
        # This handles: backups, loading, adding tab with default section, 
        # saving both unmanaged and managed files
        form = add_tab_to_form(
            unmanaged_path=unmanaged_path,
            tab_name="tab_custom",
            tab_label="Custom Tab",
            managed_path=managed_path,
            create_backup=True
        )
        
        print("=" * 80)
        print("✅ SUCCESS! Sample forms have been modified.")
        print(f"  Total tabs: {len(form.tabs)}")
        print(f"\nNext steps:")
        print(f"1. Review the changes in git diff")
        print(f"2. Import the Test solution to Dataverse")
        print(f"3. Open the Sample entity main form to verify the new 'Custom Tab'")
        
        return 0
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
