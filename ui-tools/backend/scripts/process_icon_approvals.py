"""
Process Icon Approvals

Validates and processes the approved_icons.json file exported from the Icon Selector tool.

Requires:
- approved_icons.json (exported from Icon Selector)
- merged_icons_cache_clean.json (for icon SVG content)
- entity_inventory.json (for entity info)

Output: approved_icons_validated.json
"""

import json
from pathlib import Path
from typing import Dict
import sys
import argparse


def process_approvals(
    approvals_path: Path,
    icons_cache_path: Path,
    inventory_path: Path,
    output_path: Path,
    module_filter: str = None
):
    """
    Validate and process approved icon selections.
    
    Args:
        approvals_path: Path to approved_icons.json from Icon Selector
        icons_cache_path: Path to merged_icons_cache_clean.json
        inventory_path: Path to entity_inventory.json
        output_path: Path to save validated approvals
        module_filter: Optional module path to filter (e.g., "operations/asset-management")
    """
    print("="*70)
    print("Processing Icon Approvals")
    if module_filter:
        print(f"Module Filter: {module_filter}")
    print("="*70)
    
    # Load data
    print("\nLoading data files...")
    
    with open(approvals_path, 'r', encoding='utf-8') as f:
        all_approvals = json.load(f)
    
    # Filter by module if specified
    if module_filter:
        approvals = {
            k: v for k, v in all_approvals.items()
            if v.get('module', '').startswith(module_filter)
        }
        print(f"Filtered to {len(approvals)} approvals for module: {module_filter}")
        print(f"(Total across all modules: {len(all_approvals)})")
    else:
        approvals = all_approvals
    
    with open(icons_cache_path, 'r', encoding='utf-8') as f:
        icons_data = json.load(f)
    
    with open(inventory_path, 'r', encoding='utf-8') as f:
        inventory = json.load(f)
    
    # Build icon lookup by (name, source)
    icons_cache = {}
    for icon in icons_data['icons']:
        key = (icon['name'], icon['source'])
        icons_cache[key] = icon
    
    print(f"Loaded {len(approvals)} approved icon selections")
    print(f"Loaded {len(icons_cache)} icons from {len(icons_data['sources'])} sources")
    print(f"Loaded {len(inventory)} entities")
    
    # Validate approvals
    validated = {}
    errors = []
    
    for logical_name, approval_info in approvals.items():
        # Icon Selector exports with display_name, icon_name, icon_source, module
        icon_name = approval_info['icon_name']
        icon_source = approval_info['icon_source']
        
        # Check if entity exists
        if logical_name not in inventory:
            errors.append(f"Entity not found: {logical_name}")
            continue
        
        # Check if icon exists
        icon_key = (icon_name, icon_source)
        if icon_key not in icons_cache:
            errors.append(f"Icon not found: {icon_name} ({icon_source}) for entity {logical_name}")
            continue
        
        # Get entity info
        entity_data = inventory[logical_name]
        icon_data = icons_cache[icon_key]
        
        # Get SVG content based on source
        if icon_source == 'tabler':
            # Tabler stores SVG inline in cache
            if 'svg_content' not in icon_data:
                errors.append(f"Icon {icon_name} ({icon_source}) missing svg_content field")
                continue
            svg_content = icon_data['svg_content']
        elif icon_source == 'material-design':
            # Material Design - load from repo file
            svg_path = icons_dir / "material-repo" / "svg" / f"{icon_name}.svg"
            if not svg_path.exists():
                errors.append(f"Icon {icon_name} ({icon_source}) SVG file not found: {svg_path}")
                continue
            svg_content = svg_path.read_text(encoding='utf-8')
        elif icon_source == 'lucide':
            # Lucide - load from repo file
            svg_path = icons_dir / "lucide-repo" / "icons" / f"{icon_name}.svg"
            if not svg_path.exists():
                errors.append(f"Icon {icon_name} ({icon_source}) SVG file not found: {svg_path}")
                continue
            svg_content = svg_path.read_text(encoding='utf-8')
        elif icon_source == 'phosphor':
            # Phosphor - load from repo file
            svg_path = icons_dir / "phosphor-repo" / "assets" / "regular" / f"{icon_name}.svg"
            if not svg_path.exists():
                errors.append(f"Icon {icon_name} ({icon_source}) SVG file not found: {svg_path}")
                continue
            svg_content = svg_path.read_text(encoding='utf-8')
        else:
            errors.append(f"Unknown icon source: {icon_source}")
            continue
        
        # Create validated entry
        validated[logical_name] = {
            'icon_name': icon_name,
            'icon_source': icon_source,
            'entity_display_name': entity_data['display_name'],
            'module_path': entity_data['module_path'],
            'webresource_name': f"appbase_{logical_name.replace('appbase_', '')}icon".lower(),
            'svg_content': svg_content,
            'entity_xml_path': entity_data['entity_xml_path']
        }
    
    # Save validated approvals
    print(f"\nSaving validated approvals to {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)
    
    # Report
    print("\n" + "="*70)
    print("Validation Complete!")
    print("="*70)
    print(f"Total approvals: {len(approvals)}")
    print(f"Valid approvals: {len(validated)}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print(f"\nValidation errors:")
        for error in errors[:10]:  # Show first 10
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    # Show modules that will be updated
    modules = {}
    for data in validated.values():
        module = data['module_path']
        modules[module] = modules.get(module, 0) + 1
    
    print(f"\nIcons approved by module:")
    for module, count in sorted(modules.items()):
        print(f"  {module}: {count}")
    
    print("\n" + "="*70)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Validate and process icon selections from Icon Selector',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process all modules:
  python process_icon_approvals.py
  
  # Process only Asset Management module:
  python process_icon_approvals.py --module operations/asset-management
  
  # Process only Court Case Management module:
  python process_icon_approvals.py --module government/court-case-management
'''
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Filter by module path (e.g., "operations/asset-management")'
    )
    
    args = parser.parse_args()
    
    # Paths - data files are in .icons folder at repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent  # ui-tools/backend/scripts -> repo root
    icons_dir = repo_root / '.icons'
    
    approvals_path = icons_dir / 'approved_icons.json'
    icons_cache_path = icons_dir / 'merged_icons_cache_clean.json'
    inventory_path = icons_dir / 'entity_inventory.json'
    output_path = icons_dir / 'approved_icons_validated.json'
    
    # Check if approved_icons.json exists
    if not approvals_path.exists():
        print(f"ERROR: {approvals_path.name} not found")
        print("\nPlease:")
        print("1. Open the Icon Selector tool (http://localhost:5173/#/icon-selector)")
        print("2. Select icons for your entities")
        print("3. Click 'Export' button in the top bar")
        print("4. The file will be saved to .icons/approved_icons.json")
        sys.exit(1)
    
    # Check other required files
    if not icons_cache_path.exists():
        print(f"ERROR: Required file not found: {icons_cache_path}")
        print("Run merge_icon_libraries.py first.")
        sys.exit(1)
    
    if not inventory_path.exists():
        print(f"ERROR: Required file not found: {inventory_path}")
        print("Run inventory_entities.py first.")
        sys.exit(1)
    
    # Process approvals
    process_approvals(approvals_path, icons_cache_path, inventory_path, output_path, args.module)
