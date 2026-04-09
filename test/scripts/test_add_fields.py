"""Test script to add various field types to the Sample form."""
import sys
from pathlib import Path

# Add ui-tools/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui-tools" / "scripts"))

from form_operations import add_section_to_tab, add_fields_to_section
from formxml_parser import FormXmlParser

# Define paths
test_dir = Path(__file__).parent.parent
sample_entity_dir = test_dir / "Test" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main"
unmanaged_path = sample_entity_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"
managed_path = sample_entity_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}_managed.xml"

def test_add_fields():
    """Test adding various field types to 1-column and 2-column sections."""
    print("Testing field additions to Sample form...")
    print("=" * 80)
    
    # First, add a new tab with sections for testing
    print("\n1. Adding 'Field Test Tab' with 1-column and 2-column sections...")
    
    # Add tab (creates default section)
    from form_operations import add_tab_to_form
    form = add_tab_to_form(
        unmanaged_path=unmanaged_path,
        tab_name="tab_fieldtest",
        tab_label="Field Test Tab",
        managed_path=managed_path,
        create_backup=True
    )
    
    # Add a 1-column section for text fields
    print("   Adding 'Text Fields' section (1 column)...")
    form = add_section_to_tab(
        unmanaged_path=unmanaged_path,
        tab_name="Field Test Tab",
        section_label="Text Fields",
        columns=1,
        managed_path=managed_path,
        create_backup=False  # Already backed up
    )
    
    # Add a 2-column section for numeric fields
    print("   Adding 'Numeric Fields' section (2 columns)...")
    form = add_section_to_tab(
        unmanaged_path=unmanaged_path,
        tab_name="Field Test Tab",
        section_label="Numeric Fields",
        columns=2,
        managed_path=managed_path,
        create_backup=False
    )
    
    # Test adding text fields to 1-column section
    print("\n2. Adding text fields to 'Text Fields' section...")
    text_fields = [
        ("appbase_sampletext", "Sample Text", "text"),
        ("appbase_sampleemail", "Sample Email", "email"),
        ("appbase_sampleurl", "Sample URL", "url"),
        ("appbase_samplememo", "Sample Memo", "memo"),
    ]
    
    form = add_fields_to_section(
        unmanaged_path=unmanaged_path,
        tab_name="Field Test Tab",
        section_name="secTextFields",  # Auto-generated name
        fields=text_fields,
        managed_path=managed_path,
        create_backup=False
    )
    print(f"   ✓ Added {len(text_fields)} text fields")
    
    # Test adding numeric fields to 2-column section
    print("\n3. Adding numeric fields to 'Numeric Fields' section...")
    numeric_fields = [
        ("appbase_samplewholenumber", "Whole Number", "integer"),
        ("appbase_sampledecimal", "Decimal", "decimal"),
        ("appbase_samplefloat", "Float", "float"),
        ("appbase_samplecurrency", "Currency", "currency"),
        ("appbase_sampledate", "Date", "date"),
        ("appbase_sampledatetime", "Date Time", "datetime"),
    ]
    
    form = add_fields_to_section(
        unmanaged_path=unmanaged_path,
        tab_name="Field Test Tab",
        section_name="secNumericFields",  # Auto-generated name
        fields=numeric_fields,
        managed_path=managed_path,
        create_backup=False
    )
    print(f"   ✓ Added {len(numeric_fields)} numeric fields (3 rows in 2-column layout)")
    
    # Verify the structure
    print("\n4. Verifying form structure...")
    form = FormXmlParser.parse_file(unmanaged_path)
    
    tab = form.get_tab_by_name("Field Test Tab")
    if not tab:
        print("   ❌ ERROR: Field Test Tab not found")
        return 1
    
    # Check Text Fields section
    text_section = tab.get_section_by_name("secTextFields")
    if text_section:
        print(f"   ✓ Text Fields section: columns={text_section.columns}, rows={len(text_section.rows)}")
        field_count = sum(len(row.cells) for row in text_section.rows if row.cells)
        print(f"     - Found {field_count} fields")
    else:
        print("   ❌ ERROR: Text Fields section not found")
    
    # Check Numeric Fields section
    numeric_section = tab.get_section_by_name("secNumericFields")
    if numeric_section:
        print(f"   ✓ Numeric Fields section: columns={numeric_section.columns}, rows={len(numeric_section.rows)}")
        field_count = sum(len(row.cells) for row in numeric_section.rows if row.cells)
        print(f"     - Found {field_count} fields")
        
        # Check row structure for 2-column layout
        for i, row in enumerate(numeric_section.rows):
            if row.cells:
                cells_in_row = len(row.cells)
                print(f"     - Row {i}: {cells_in_row} cells")
    else:
        print("   ❌ ERROR: Numeric Fields section not found")
    
    print("\n" + "=" * 80)
    print("✅ SUCCESS! Fields added to Sample form.")
    print("\nNext steps:")
    print("1. Review the changes in git diff")
    print("2. Compare with the Test form's field structure")
    print("3. Import the Test solution to Dataverse to verify")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(test_add_fields())
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
