"""
Test script for simulation parser

Run from workspace root:
python ui-tools/backend/services/test_simulation_parser.py
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from services.simulation_parser import validate_simulation


def main():
    """Test the simulation parser"""
    
    # Paths
    workspace_root = Path(__file__).parent.parent.parent.parent
    simulation_path = workspace_root / "government" / "court-case-management" / "design" / "simulations" / "small-claims-johnson-chen.yaml"
    module_path = workspace_root / "government" / "court-case-management"
    
    print(f"Validating simulation: {simulation_path.name}")
    print(f"Module: {module_path.name}")
    print("-" * 80)
    
    # Validate
    result = validate_simulation(simulation_path, module_path)
    
    # Print results
    print(f"\nValidation Result:")
    print(f"  Valid: {result['is_valid']}")
    print(f"  Errors: {result['error_count']}")
    print(f"  Warnings: {result['warning_count']}")
    print()
    
    if result['errors']:
        print("ERRORS:")
        for error in result['errors']:
            print(f"  Step {error['step']}, Action {error['action_index']}, Field '{error['field']}':")
            print(f"    {error['message']}")
        print()
    
    if result['warnings']:
        print("WARNINGS:")
        for warning in result['warnings']:
            print(f"  Step {warning['step']}, Action {warning['action_index']}, Field '{warning['field']}':")
            print(f"    {warning['message']}")
        print()
    
    print("Metadata:")
    for key, value in result['metadata'].items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    if result['is_valid']:
        print("✅ Simulation is VALID")
    else:
        print("❌ Simulation has ERRORS")
    
    return 0 if result['is_valid'] else 1


if __name__ == "__main__":
    sys.exit(main())
