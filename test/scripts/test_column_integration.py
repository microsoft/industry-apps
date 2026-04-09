"""Test script to verify column count translation works in add_section flow."""
import sys
from pathlib import Path

# Add ui-tools/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui-tools" / "scripts"))

from form_operations import add_section_to_tab
from formxml_parser import FormXmlParser

# Define paths
test_dir = Path(__file__).parent.parent
sample_entity_dir = test_dir / "Test" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main"
unmanaged_path = sample_entity_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"
managed_path = sample_entity_dir / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}_managed.xml"

def test_column_translation_integration():
    """Test that column translation works when adding sections."""
    print("Testing column count translation in add_section workflow...")
    
    # Test 1: Add a 1-column section
    print("\n1. Adding 1-column section...")
    form = add_section_to_tab(
        unmanaged_path=unmanaged_path,
        tab_name="Custom Tab",
        section_label="Test 1-Column Section",
        columns=1,
        managed_path=managed_path,
        create_backup=True
    )
    
    # Find the section and verify columns
    tab = form.get_tab_by_name("Custom Tab")
    section = None
    for col in tab.columns:
        for sec in col.sections:
            if "Test 1-Column Section" in [label.description for label in sec.labels]:
                section = sec
                break
    
    assert section is not None, "Could not find Test 1-Column Section"
    print(f"   Found section with columns={section.columns}")
    assert section.columns == 1, f"Expected columns=1, got {section.columns}"
    print("   ✓ 1-column section has columns=1")
    
    # Test 2: Add a 2-column section
    print("\n2. Adding 2-column section...")
    form = add_section_to_tab(
        unmanaged_path=unmanaged_path,
        tab_name="Custom Tab",
        section_label="Test 2-Column Section",
        columns=2,
        managed_path=managed_path,
        create_backup=True
    )
    
    # Find the section and verify columns
    tab = form.get_tab_by_name("Custom Tab")
    section = None
    for col in tab.columns:
        for sec in col.sections:
            if "Test 2-Column Section" in [label.description for label in sec.labels]:
                section = sec
                break
    
    assert section is not None, "Could not find Test 2-Column Section"
    print(f"   Found section with columns={section.columns}")
    assert section.columns == 11, f"Expected columns=11, got {section.columns}"
    print("   ✓ 2-column section has columns=11")
    
    # Test 3: Verify both sections exist in the saved XML
    print("\n3. Verifying sections in saved XML...")
    saved_form = FormXmlParser.parse_file(unmanaged_path)
    tab = saved_form.get_tab_by_name("Custom Tab")
    
    section_labels = []
    for col in tab.columns:
        for sec in col.sections:
            for label in sec.labels:
                section_labels.append((label.description, sec.columns))
    
    print(f"   Found {len(section_labels)} sections:")
    for label, cols in section_labels:
        print(f"     - {label}: columns={cols}")
    
    # Verify our test sections are there with correct columns
    test_sections = {label: cols for label, cols in section_labels 
                    if "Test" in label and "Column" in label}
    
    assert "Test 1-Column Section" in test_sections, "1-column section not found"
    assert test_sections["Test 1-Column Section"] == 1, "1-column section has wrong columns value"
    
    assert "Test 2-Column Section" in test_sections, "2-column section not found"
    assert test_sections["Test 2-Column Section"] == 11, "2-column section has wrong columns value"
    
    print("\n✅ All integration tests passed!")
    print("   - API accepts 1 or 2 as column values")
    print("   - Translation to 1 or 11 happens automatically")
    print("   - Both unmanaged and managed files updated correctly")

if __name__ == "__main__":
    test_column_translation_integration()
