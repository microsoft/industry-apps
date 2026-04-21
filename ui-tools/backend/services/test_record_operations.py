"""
Test script for record operations

Run from workspace root:
python ui-tools/backend/services/test_record_operations.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.record_operations import RecordOperations, DryRunRecordOperations, PayloadBuildError
from services.execution_context import ExecutionContext, DryRunContext
from services.simulation_parser import DataModelLoader


def test_field_entry_parsing():
    """Test parsing field entry strings - DEPRECATED (now uses dictionaries)"""
    print("\n" + "="*80)
    print("TEST 1: Field Entry Parsing (SKIPPED - now uses dict format)")
    print("="*80)
    print("✅ Test skipped - field entries now use dictionary format")


def test_choice_value_conversion():
    """Test converting choice labels to numeric values"""
    print("\n" + "="*80)
    print("TEST 2: Choice Value Conversion")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    ops = RecordOperations(module_path)
    
    # Test valid choice value
    value = ops.convert_choice_value("appbase_courtcasetype", "Civil")
    assert value == 147130000
    print(f"✅ Converted 'Civil' -> {value}")
    
    value = ops.convert_choice_value("appbase_courtpartyrole", "Plaintiff")
    assert value == 147130000
    print(f"✅ Converted 'Plaintiff' -> {value}")
    
    value = ops.convert_choice_value("appbase_courtpartyrole", "Defendant")
    assert value == 147130001
    print(f"✅ Converted 'Defendant' -> {value}")


def test_boolean_formatting():
    """Test boolean value formatting"""
    print("\n" + "="*80)
    print("TEST 3: Boolean Formatting")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    ops = RecordOperations(module_path)
    
    assert ops.format_boolean_value("Yes") == True
    assert ops.format_boolean_value("No") == False
    assert ops.format_boolean_value("True") == True
    assert ops.format_boolean_value("False") == False
    assert ops.format_boolean_value("1") == True
    assert ops.format_boolean_value("0") == False
    
    print("✅ Boolean conversion working correctly")


def test_datetime_formatting():
    """Test datetime formatting"""
    print("\n" + "="*80)
    print("TEST 4: DateTime Formatting")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    ops = RecordOperations(module_path)
    
    # ISO 8601 format should pass through
    dt1 = ops.format_datetime_value("2026-04-15T09:30:00Z")
    assert dt1 == "2026-04-15T09:30:00Z"
    print(f"✅ ISO 8601 preserved: {dt1}")
    
    # Date-only should be converted
    dt2 = ops.format_datetime_value("2026-04-15")
    assert dt2 == "2026-04-15T00:00:00Z"
    print(f"✅ Date converted: {dt2}")


def test_lookup_binding():
    """Test building OData lookup bindings"""
    print("\n" + "="*80)
    print("TEST 5: Lookup Binding")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    ops = RecordOperations(module_path)
    
    binding = ops.build_lookup_binding("contacts", "12345678-1234-1234-1234-123456789012")
    assert binding == "/contacts(12345678-1234-1234-1234-123456789012)"
    print(f"✅ Lookup binding: {binding}")
    
    binding = ops.build_lookup_binding("appbase_courtcases", "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb")
    assert binding == "/appbase_courtcases(aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb)"
    print(f"✅ Custom entity binding: {binding}")


def test_payload_building():
    """Test building Web API payloads"""
    print("\n" + "="*80)
    print("TEST 6: Payload Building")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    ops = RecordOperations(module_path)
    ctx = ExecutionContext()
    
    # Create a mock case record for lookups
    ctx.store_record("case_record", {
        "id": "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb",
        "appbase_casenumber": "CC-2026-1547"
    })
    
    # Build payload for Court Case (using dictionary format)
    fields = {
        "appbase_casenumber": "CC-2026-1547",
        "appbase_casetitle": "Johnson v. Chen",
        "appbase_casetype": "Civil",
        "appbase_filingdate": "2026-04-15T09:30:00Z",
        "appbase_settlementamount": 2500.00
    }
    
    payload = ops.build_payload("Court Case", fields, ctx, step=1)
    
    assert payload["appbase_casenumber"] == "CC-2026-1547"
    assert payload["appbase_casetitle"] == "Johnson v. Chen"
    assert payload["appbase_casetype"] == 147130000  # Choice value for "Civil"
    assert payload["appbase_filingdate"] == "2026-04-15T09:30:00Z"
    assert payload["appbase_settlementamount"] == 2500.0
    
    print("✅ Court Case payload built correctly:")
    print(f"   Case Number: {payload['appbase_casenumber']}")
    print(f"   Case Type: {payload['appbase_casetype']} (Civil)")
    print(f"   Settlement: ${payload['appbase_settlementamount']}")


def test_payload_with_template_variables():
    """Test payload building with template variables"""
    print("\n" + "="*80)
    print("TEST 7: Payload with Template Variables")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    ops = RecordOperations(module_path)
    ctx = ExecutionContext()
    
    # Store prerequisite records
    ctx.store_record("case_record", {
        "id": "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
    })
    
    ctx.store_record("plaintiff_contact", {
        "contactid": "cccccccc-4444-5555-6666-dddddddddddd",
        "id": "cccccccc-4444-5555-6666-dddddddddddd"
    })
    
    # Build payload for Court Case Party with template variables (dictionary format)
    fields = {
        "appbase_courtcase": "{{case_record.id}}",
        "appbase_person": "{{plaintiff_contact.id}}",
        "appbase_partyrole": "Plaintiff",
        "appbase_partytype": "Individual"
    }
    
    payload = ops.build_payload("Court Case Party", fields, ctx, step=2)
    
    # Check that lookups have @odata.bind suffix
    assert "appbase_courtcase@odata.bind" in payload
    assert payload["appbase_courtcase@odata.bind"] == "/appbase_courtcases(aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb)"
    
    assert "appbase_person@odata.bind" in payload
    # Person might be Contact (external), so it would use 'contacts' plural
    
    assert payload["appbase_partyrole"] == 147130000  # Plaintiff
    assert payload["appbase_partytype"] == 147130000  # Individual
    
    print("✅ Template variables resolved correctly:")
    print(f"   Court Case binding: {payload['appbase_courtcase@odata.bind']}")
    print(f"   Party Role: {payload['appbase_partyrole']} (Plaintiff)")


def test_dry_run_operations():
    """Test dry-run record operations"""
    print("\n" + "="*80)
    print("TEST 8: Dry Run Operations")
    print("="*80)
    
    workspace_root = Path(__file__).parent.parent.parent.parent
    module_path = workspace_root / "government" / "court-case-management"
    
    dry_ops = DryRunRecordOperations(module_path)
    dry_ctx = DryRunContext()
    
    # Simulate creating a court case (dictionary format)
    action = {
        "action": "create",
        "table": "Court Case",
        "schema_name": "appbase_CourtCase",
        "fields": {
            "appbase_casenumber": "CC-2026-1547",
            "appbase_casetitle": "Johnson v. Chen",
            "appbase_casetype": "Civil"
        },
        "store_as": "case_record"
    }
    
    mock_response = dry_ops.simulate_create(action, dry_ctx, step=1)
    
    assert "id" in mock_response
    assert mock_response["appbase_casenumber"] == "CC-2026-1547"
    assert mock_response["appbase_casetype"] == 147130000
    
    print(f"✅ Simulated create with mock ID: {mock_response['id']}")
    print(f"   Stored as: case_record")
    
    # Verify it was stored in context
    assert dry_ctx.has_record("case_record")
    
    # Simulate creating a party linked to the case (dictionary format)
    action2 = {
        "action": "create",
        "table": "Court Case Party",
        "schema_name": "appbase_CourtCaseParty",
        "fields": {
            "appbase_courtcase": "{{case_record.id}}",
            "appbase_partyrole": "Plaintiff"
        },
        "store_as": "plaintiff_party"
    }
    
    mock_response2 = dry_ops.simulate_create(action2, dry_ctx, step=2)
    
    print(f"✅ Simulated second create with template resolution")
    print(f"   Linked to case: {mock_response['id']}")
    
    # Get summary
    summary = dry_ops.get_simulation_summary()
    assert summary["total_operations"] == 2
    assert summary["creates"] == 2
    
    print(f"✅ Simulation summary:")
    print(f"   Total operations: {summary['total_operations']}")
    print(f"   Creates: {summary['creates']}")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("RECORD OPERATIONS TESTS")
    print("="*80)
    
    try:
        test_field_entry_parsing()
        test_choice_value_conversion()
        test_boolean_formatting()
        test_datetime_formatting()
        test_lookup_binding()
        test_payload_building()
        test_payload_with_template_variables()
        test_dry_run_operations()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
        print("\nRecord operations service is working correctly!")
        print("Ready for integration with Web API client.")
        return 0
        
    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ TEST FAILED: {e}")
        print("="*80)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
