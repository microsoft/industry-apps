#!/usr/bin/env python3
"""
Test script to validate formxml_parser.py works correctly.
Compares programmatic output with UI-generated FormXML from captures.
"""

import sys
from pathlib import Path

# Add ui-tools/scripts to path to import formxml modules
scripts_dir = Path(__file__).resolve().parent.parent.parent / "ui-tools" / "scripts"
sys.path.insert(0, str(scripts_dir))

from formxml_parser import FormXmlParser, FormDefinition


def test_parse_sample_form():
    """Test parsing the Sample entity's baseline form."""
    print("=" * 80)
    print("TEST 1: Parse Sample Form (Baseline)")
    print("=" * 80)
    
    sample_form_path = Path(__file__).resolve().parent.parent / "Test" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main" / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"
    
    if not sample_form_path.exists():
        print(f"❌ ERROR: Sample form not found at {sample_form_path}")
        return False
    
    try:
        form = FormXmlParser.parse_file(sample_form_path)
        
        print(f"✓ Successfully parsed Sample form")
        print(f"  Form ID: {form.formid}")
        print(f"  Presentation: {form.form_presentation}")
        print(f"  Tabs: {len(form.tabs)}")
        
        for i, tab in enumerate(form.tabs):
            tab_label = tab.labels[0].description if tab.labels else "(No label)"
            print(f"    Tab {i}: {tab_label} (ID: {tab.id})")
            
            for col in tab.columns:
                print(f"      Sections: {len(col.sections)}")
                for section in col.sections:
                    section_label = section.labels[0].description if section.labels else "(No label)"
                    field_count = sum(1 for row in section.rows for cell in row.cells if cell.control)
                    print(f"        - {section_label}: {field_count} fields")
        
        print(f"\n✓ Sample form parsed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR parsing Sample form: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_parse_capture02_form():
    """Test parsing the capture 02 form (after adding tab via UI)."""
    print("=" * 80)
    print("TEST 2: Parse Capture 02 Form (UI-Generated Tab)")
    print("=" * 80)
    
    capture02_path = Path(__file__).resolve().parent.parent / "captures" / "02 - Add Tab" / "src" / "Entities" / "appbase_Test" / "FormXml" / "main" / "{3fa70a65-3d83-4337-a3de-def80061a5e4}.xml"
    
    if not capture02_path.exists():
        print(f"❌ ERROR: Capture 02 form not found at {capture02_path}")
        return False
    
    try:
        form = FormXmlParser.parse_file(capture02_path)
        
        print(f"✓ Successfully parsed Capture 02 form")
        print(f"  Form ID: {form.formid}")
        print(f"  Header Density: {getattr(form, 'headerdensity', 'Not set')}")
        print(f"  Tabs: {len(form.tabs)}")
        
        for i, tab in enumerate(form.tabs):
            tab_label = tab.labels[0].description if tab.labels else "(No label)"
            print(f"    Tab {i}: {tab_label}")
            print(f"      ID: {tab.id}")
            print(f"      Name: {tab.name}")
            print(f"      IsUserDefined: {tab.is_user_defined}")
            
            for col in tab.columns:
                for section in col.sections:
                    section_label = section.labels[0].description if section.labels else "(No label)"
                    print(f"      Section: {section_label}")
                    print(f"        Name: {section.name}")
                    print(f"        Layout: {section.layout}")
                    print(f"        Columns: {section.columns}")
        
        if form.header:
            print(f"  Header: Present (ID: {form.header.id})")
        
        if form.footer:
            print(f"  Footer: Present (ID: {form.footer.id})")
        
        print(f"\n✓ Capture 02 form parsed successfully\n")
        return True
        
    except Exception as e:
        print(f"❌ ERROR parsing Capture 02 form: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_add_tab_programmatically():
    """Test adding a tab programmatically to Sample form and compare structure."""
    print("=" * 80)
    print("TEST 3: Add Tab Programmatically to Sample Form")
    print("=" * 80)
    
    sample_form_path = Path(__file__).resolve().parent.parent / "Test" / "src" / "Entities" / "appbase_Sample" / "FormXml" / "main" / "{dafd3ef2-a996-45ea-8d28-4d1afef35e3f}.xml"
    
    if not sample_form_path.exists():
        print(f"❌ ERROR: Sample form not found")
        return False
    
    try:
        # Parse Sample form
        form = FormXmlParser.parse_file(sample_form_path)
        print(f"✓ Loaded Sample form (currently {len(form.tabs)} tab)")
        
        # Add a tab using formxml_parser
        print(f"  Adding new tab 'Sample Tab'...")
        new_tab = form.add_tab("tab_sample", "Sample Tab")
        
        print(f"✓ Tab added via formxml_parser")
        print(f"  Tab ID: {new_tab.id}")
        print(f"  Tab name: {new_tab.name}")
        print(f"  Tab label: {new_tab.labels[0].description if new_tab.labels else '(none)'}")
        print(f"  Total tabs: {len(form.tabs)}")
        
        # Check if default section was created
        if new_tab.columns and new_tab.columns[0].sections:
            section = new_tab.columns[0].sections[0]
            print(f"  Default section created: {section.labels[0].description if section.labels else '(none)'}")
        
        # Write to temporary file for comparison
        output_path = Path(__file__).resolve().parent / "sample_with_tab_programmatic.xml"
        FormXmlParser.write_file(form, output_path)
        print(f"\n✓ Modified Sample form saved to: {output_path}")
        print(f"\n📝 NEXT STEP: Manually compare this file with Capture 02 to see differences:")
        print(f"   Right-click both files in VS Code and select 'Compare Selected'")
        print(f"   Capture 02: captures/02 - Add Tab/src/Entities/appbase_Test/FormXml/main/*.xml")
        print(f"   Programmatic: {output_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ ERROR adding tab programmatically: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "FormXML Parser Validation Tests" + " " * 26 + "║")
    print("╚" + "=" * 78 + "╝")
    print("\n")
    
    results = []
    
    # Test 1: Parse Sample form
    results.append(("Parse Sample Form", test_parse_sample_form()))
    
    # Test 2: Parse Capture 02 form
    results.append(("Parse Capture 02 Form", test_parse_capture02_form()))
    
    # Test 3: Add tab programmatically
    results.append(("Add Tab Programmatically", test_add_tab_programmatically()))
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nResults: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! FormXML parser is working.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed. Review errors above.")
    
    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
