"""
Demonstration of adding various field types to Dataverse forms.

This script shows how to add different field types to both 1-column and 2-column sections.
"""

import sys
from pathlib import Path

# Add ui-tools/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui-tools" / "scripts"))

from form_operations import add_fields_to_section

def demo_field_types():
    """Demonstrate all supported field types."""
    
    print("=" * 80)
    print("DATAVERSE FORM FIELD TYPES - Quick Reference")
    print("=" * 80)
    
    print("\n📝 TEXT-BASED FIELDS:")
    print("  • text      - Single line of text")
    print("  • email     - Email address with validation")
    print("  • url       - Hyperlink field")
    print("  • memo      - Multi-line text")
    
    print("\n🔢 NUMERIC FIELDS:")
    print("  • integer   - Whole numbers")
    print("  • decimal   - Decimal precision numbers")
    print("  • float     - Floating point numbers")
    print("  • currency  - Money values")
    
    print("\n📅 DATE/TIME FIELDS:")
    print("  • date      - Date only")
    print("  • datetime  - Date and time")
    
    print("\n🎯 CHOICE & LOOKUP FIELDS:")
    print("  • choice    - Dropdown/picklist (also: optionset, picklist)")
    print("  • lookup    - Reference to another entity")
    print("  • twooptions- Yes/No (also: boolean, yesno)")
    
    print("\n" + "=" * 80)
    print("USAGE EXAMPLES")
    print("=" * 80)
    
    print("\n1️⃣  Adding fields to a 1-COLUMN section:")
    print("   Each field appears in its own row, stacked vertically")
    print()
    print("   add_fields_to_section(")
    print("       form_path,")
    print('       tab_name="General",')
    print('       section_name="Contact Info",')
    print("       fields=[")
    print('           ("appbase_firstname", "First Name", "text"),')
    print('           ("appbase_lastname", "Last Name", "text"),')
    print('           ("appbase_email", "Email", "email"),')
    print('           ("appbase_phone", "Phone", "text"),')
    print("       ]")
    print("   )")
    
    print("\n2️⃣  Adding fields to a 2-COLUMN section:")
    print("   Fields appear side-by-side, two per row")
    print()
    print("   add_fields_to_section(")
    print("       form_path,")
    print('       tab_name="Details",')
    print('       section_name="Address",')
    print("       fields=[")
    print('           ("appbase_street", "Street", "text"),')
    print('           ("appbase_city", "City", "text"),        # Row 1')
    print('           ("appbase_state", "State", "text"),')
    print('           ("appbase_zip", "Zip", "text"),          # Row 2')
    print("       ]")
    print("   )")
    
    print("\n3️⃣  Using field type aliases:")
    print("   Multiple friendly names map to the same control type:")
    print()
    print('   "text" or "singleline" → Single-line text')
    print('   "memo" or "multiline" or "richtext" → Multi-line text')
    print('   "integer" or "wholenumber" → Whole number')
    print('   "choice" or "optionset" or "picklist" → Choice field')
    print('   "twooptions" or "boolean" or "yesno" → Yes/No field')
    
    print("\n" + "=" * 80)
    print()

if __name__ == "__main__":
    demo_field_types()
