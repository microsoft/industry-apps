"""
Test script for execution context manager

Run from workspace root:
python ui-tools/backend/services/test_execution_context.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.execution_context import ExecutionContext, DryRunContext, TemplateResolutionError, create_execution_context


def test_basic_storage_and_retrieval():
    """Test storing and retrieving records"""
    print("\n" + "="*80)
    print("TEST 1: Basic Storage and Retrieval")
    print("="*80)
    
    ctx = ExecutionContext()
    
    # Simulate a Web API response for a court case
    case_record = {
        "id": "12345678-1234-1234-1234-123456789012",
        "@odata.id": "/appbase_courtcases(12345678-1234-1234-1234-123456789012)",
        "appbase_casenumber": "CC-2026-1547",
        "appbase_casetitle": "Johnson v. Chen",
        "appbase_casetype": 147130000
    }
    
    ctx.store_record("case_record", case_record, step=1)
    
    # Verify storage
    assert ctx.has_record("case_record"), "Record should exist"
    assert not ctx.has_record("nonexistent"), "Nonexistent record should not exist"
    
    retrieved = ctx.get_record("case_record")
    assert retrieved == case_record, "Retrieved record should match stored"
    
    print("✅ Storage and retrieval working correctly")
    print(f"   Stored record: {ctx.get_record('case_record')['appbase_casetitle']}")


def test_template_variable_parsing():
    """Test parsing template variables"""
    print("\n" + "="*80)
    print("TEST 2: Template Variable Parsing")
    print("="*80)
    
    ctx = ExecutionContext()
    
    # Test simple variable
    record_name, field_name = ctx.parse_template_variable("case_record.id")
    assert record_name == "case_record", f"Expected 'case_record', got '{record_name}'"
    assert field_name == "id", f"Expected 'id', got '{field_name}'"
    
    # Test variable without field
    record_name, field_name = ctx.parse_template_variable("plaintiff_contact")
    assert record_name == "plaintiff_contact"
    assert field_name is None
    
    # Test nested field with underscore
    record_name, field_name = ctx.parse_template_variable("contact.address1_line1")
    assert record_name == "contact"
    assert field_name == "address1_line1"
    
    print("✅ Template variable parsing working correctly")
    print(f"   'case_record.id' -> record='{record_name}', field='{field_name}'")


def test_variable_resolution():
    """Test resolving template variables"""
    print("\n" + "="*80)
    print("TEST 3: Variable Resolution")
    print("="*80)
    
    ctx = ExecutionContext()
    
    # Store some test records
    case_record = {
        "id": "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb",
        "appbase_casenumber": "CC-2026-1547",
        "appbase_settlementamount": 2500.00
    }
    
    contact_record = {
        "contactid": "cccccccc-4444-5555-6666-dddddddddddd",
        "firstname": "Sarah",
        "lastname": "Johnson",
        "emailaddress1": "sarah.johnson@email.com"
    }
    
    ctx.store_record("case_record", case_record)
    ctx.store_record("plaintiff_contact", contact_record)
    
    # Test ID resolution
    case_id = ctx.resolve_variable("case_record.id")
    assert case_id == "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
    print(f"✅ Resolved case_record.id: {case_id}")
    
    # Test text field resolution
    email = ctx.resolve_variable("plaintiff_contact.emailaddress1")
    assert email == "sarah.johnson@email.com"
    print(f"✅ Resolved plaintiff_contact.emailaddress1: {email}")
    
    # Test numeric field
    amount = ctx.resolve_variable("case_record.appbase_settlementamount")
    assert amount == 2500.00
    print(f"✅ Resolved case_record.appbase_settlementamount: {amount}")
    
    # Test full record resolution
    full_contact = ctx.resolve_variable("plaintiff_contact")
    assert full_contact == contact_record
    print(f"✅ Resolved full record: plaintiff_contact")


def test_template_string_resolution():
    """Test resolving template variables in strings"""
    print("\n" + "="*80)
    print("TEST 4: Template String Resolution")
    print("="*80)
    
    ctx = ExecutionContext()
    
    case_record = {
        "id": "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb",
        "appbase_casenumber": "CC-2026-1547"
    }
    
    ctx.store_record("case_record", case_record)
    
    # Test single variable
    text1 = "{{case_record.id}}"
    resolved1 = ctx.resolve_template_string(text1)
    assert resolved1 == "aaaaaaaa-1111-2222-3333-bbbbbbbbbbbb"
    print(f"✅ '{text1}' -> '{resolved1}'")
    
    # Test embedded variable
    text2 = "Case number is {{case_record.appbase_casenumber}}"
    resolved2 = ctx.resolve_template_string(text2)
    assert resolved2 == "Case number is CC-2026-1547"
    print(f"✅ '{text2}' -> '{resolved2}'")
    
    # Test multiple variables
    ctx.store_record("other", {"value": "test"})
    text3 = "ID: {{case_record.id}}, Value: {{other.value}}"
    resolved3 = ctx.resolve_template_string(text3)
    print(f"✅ Multiple variables resolved: '{resolved3}'")


def test_error_handling():
    """Test error handling for invalid variables"""
    print("\n" + "="*80)
    print("TEST 5: Error Handling")
    print("="*80)
    
    ctx = ExecutionContext()
    
    # Test missing record
    try:
        ctx.resolve_variable("nonexistent.id")
        assert False, "Should have raised TemplateResolutionError"
    except TemplateResolutionError as e:
        print(f"✅ Caught expected error for missing record: {e.reason}")
    
    # Test missing field
    ctx.store_record("test", {"field1": "value1"})
    try:
        ctx.resolve_variable("test.missing_field")
        assert False, "Should have raised TemplateResolutionError"
    except TemplateResolutionError as e:
        print(f"✅ Caught expected error for missing field: {e.reason}")


def test_dry_run_context():
    """Test dry-run context with mock record creation"""
    print("\n" + "="*80)
    print("TEST 6: Dry Run Context")
    print("="*80)
    
    dry_ctx = DryRunContext()
    
    # Simulate creating a court case
    case_fields = {
        "appbase_casenumber": "CC-2026-1547",
        "appbase_casetitle": "Johnson v. Chen",
        "appbase_casetype": 147130000
    }
    
    mock_case = dry_ctx.simulate_record_creation(
        store_as="case_record",
        table="Court Case",
        fields=case_fields,
        step=1
    )
    
    print(f"✅ Simulated case creation with mock ID: {mock_case['id']}")
    
    # Simulate creating a contact
    contact_fields = {
        "firstname": "Sarah",
        "lastname": "Johnson",
        "emailaddress1": "sarah.johnson@email.com"
    }
    
    mock_contact = dry_ctx.simulate_record_creation(
        store_as="plaintiff_contact",
        table="Contact",
        fields=contact_fields,
        step=2
    )
    
    print(f"✅ Simulated contact creation with mock ID: {mock_contact['id']}")
    
    # Test template resolution with mock data
    resolved_id = dry_ctx.resolve_variable("case_record.id")
    print(f"✅ Resolved template variable from mock data: {resolved_id}")
    
    # Get dry-run summary
    summary = dry_ctx.get_dry_run_summary()
    print(f"✅ Dry-run summary:")
    print(f"   Total records: {summary['total_records_created']}")
    print(f"   Simulated: {len(summary['simulated_records'])}")
    print(f"   Record names: {summary['record_names']}")


def test_execution_tracking():
    """Test execution progress tracking"""
    print("\n" + "="*80)
    print("TEST 7: Execution Progress Tracking")
    print("="*80)
    
    ctx = ExecutionContext()
    
    # Simulate multi-step execution
    ctx.store_record("rec1", {"id": "1"}, step=1)
    ctx.mark_step_complete(1)
    
    ctx.store_record("rec2", {"id": "2"}, step=2)
    ctx.mark_step_complete(2)
    
    ctx.store_record("rec3", {"id": "3"}, step=3)
    ctx.mark_step_complete(3)
    
    summary = ctx.get_execution_summary()
    
    assert summary['current_step'] == 3
    assert len(summary['completed_steps']) == 3
    assert summary['total_records_created'] == 3
    
    print(f"✅ Execution tracking:")
    print(f"   Current step: {summary['current_step']}")
    print(f"   Completed steps: {summary['completed_steps']}")
    print(f"   Records created: {summary['total_records_created']}")


def test_factory_function():
    """Test the factory function"""
    print("\n" + "="*80)
    print("TEST 8: Factory Function")
    print("="*80)
    
    # Normal context
    normal_ctx = create_execution_context(dry_run=False)
    assert isinstance(normal_ctx, ExecutionContext)
    assert not isinstance(normal_ctx, DryRunContext)
    print("✅ Created normal ExecutionContext")
    
    # Dry-run context
    dry_ctx = create_execution_context(dry_run=True)
    assert isinstance(dry_ctx, DryRunContext)
    print("✅ Created DryRunContext")


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("EXECUTION CONTEXT MANAGER TESTS")
    print("="*80)
    
    try:
        test_basic_storage_and_retrieval()
        test_template_variable_parsing()
        test_variable_resolution()
        test_template_string_resolution()
        test_error_handling()
        test_dry_run_context()
        test_execution_tracking()
        test_factory_function()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED")
        print("="*80)
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
