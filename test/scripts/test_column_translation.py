"""Test script to verify column count translation works correctly."""
import sys
from pathlib import Path

# Add ui-tools/scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "ui-tools" / "scripts"))

from formxml_parser import translate_column_count

def test_translate_column_count():
    """Test the translate_column_count function."""
    print("Testing column count translation...")
    
    # Test 1: Single column
    result = translate_column_count(1)
    print(f"  columns=1 -> {result} (expected 1)")
    assert result == 1, f"Expected 1, got {result}"
    
    # Test 2: Two columns
    result = translate_column_count(2)
    print(f"  columns=2 -> {result} (expected 11)")
    assert result == 11, f"Expected 11, got {result}"
    
    # Test 3: Invalid value should raise ValueError
    print(f"  columns=3 -> should raise ValueError")
    try:
        translate_column_count(3)
        assert False, "Should have raised ValueError for columns=3"
    except ValueError as e:
        print(f"    ✓ Raised ValueError: {e}")
    
    print("\n✅ All column translation tests passed!")

if __name__ == "__main__":
    test_translate_column_count()
