"""
Create Icon WebResources

Creates WebResource files (.data.xml and content files) for approved icons,
updates Entity.xml files with IconVectorName references, and registers
WebResources in Solution.xml.

Requires:
- approved_icons_validated.json (from process_icon_approvals.py)

Output:
- WebResource files in <module>/src/WebResources/
- Updated Entity.xml files with IconVectorName
- Updated Solution.xml files with WebResource RootComponents
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict
import uuid
import sys
import argparse


def generate_webresource_files(
    entity_display_name: str,
    webresource_name: str,
    svg_content: str,
    module_path: Path
) -> tuple[Path, Path]:
    """
    Generate WebResource .data.xml and content files.
    
    Args:
        entity_display_name: Entity display name (e.g., "Asset Acquisition")
        webresource_name: WebResource name (e.g., "appbase_courtcaseicon")
        svg_content: Raw SVG content
        module_path: Path to module root (e.g., government/court-case-management)
        
    Returns:
        Tuple of (data_xml_path, content_file_path)
    """
    # Ensure WebResources directory exists
    webresources_dir = module_path / 'src' / 'WebResources'
    webresources_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if WebResource .data.xml already exists and extract GUID if so
    data_xml_path = webresources_dir / f'{webresource_name}.data.xml'
    existing_guid = None
    
    if data_xml_path.exists():
        # Parse existing .data.xml to extract GUID
        try:
            tree = ET.parse(data_xml_path)
            root = tree.getroot()
            guid_elem = root.find('.//{*}WebResourceId')
            if guid_elem is not None and guid_elem.text:
                # Extract GUID without braces
                existing_guid = guid_elem.text.strip('{}')
                print(f"    Reusing existing GUID: {existing_guid}")
        except Exception as e:
            print(f"    WARNING: Could not parse existing .data.xml: {e}")
    
    # Use existing GUID or generate new one
    if existing_guid:
        resource_guid = existing_guid
    else:
        resource_guid = str(uuid.uuid4())
        print(f"    Generated new GUID: {resource_guid}")
    
    guid_upper = resource_guid.upper()
    guid_no_hyphens = guid_upper.replace('-', '')
    
    # Use entity display name for WebResource DisplayName with "Icon" suffix
    display_name = entity_display_name + " Icon"
    
    # Create .data.xml file
    data_xml_content = f'''<?xml version="1.0" encoding="utf-8"?>
<WebResource xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <WebResourceId>{{{resource_guid}}}</WebResourceId>
  <Name>{webresource_name}</Name>
  <DisplayName>{display_name}</DisplayName>
  <WebResourceType>11</WebResourceType>
  <IntroducedVersion>1.0</IntroducedVersion>
  <IsEnabledForMobileClient>1</IsEnabledForMobileClient>
  <IsAvailableForMobileOffline>0</IsAvailableForMobileOffline>
  <IsCustomizable>1</IsCustomizable>
  <CanBeDeleted>1</CanBeDeleted>
  <IsHidden>0</IsHidden>
  <FileName>/WebResources/{webresource_name}{guid_no_hyphens}</FileName>
</WebResource>'''
    
    data_xml_path = webresources_dir / f'{webresource_name}.data.xml'
    with open(data_xml_path, 'w', encoding='utf-8') as f:
        f.write(data_xml_content)
    
    # Create content file (SVG without .data.xml extension)
    content_file_path = webresources_dir / webresource_name
    with open(content_file_path, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    return data_xml_path, content_file_path


def update_solution_xml(module_path: Path, webresource_name: str) -> bool:
    """
    Update Solution.xml to register the WebResource as a RootComponent.
    
    Args:
        module_path: Path to module root (e.g., government/court-case-management)
        webresource_name: WebResource name (e.g., "appbase_courtcaseicon")
        
    Returns:
        True if updated successfully
    """
    try:
        solution_xml_path = module_path / 'src' / 'Other' / 'Solution.xml'
        
        if not solution_xml_path.exists():
            print(f"    WARNING: Solution.xml not found at {solution_xml_path}")
            return False
        
        # Parse Solution.xml
        tree = ET.parse(solution_xml_path)
        root = tree.getroot()
        
        # Find RootComponents element
        root_components = root.find('.//{*}RootComponents')
        if root_components is None:
            print(f"    WARNING: No RootComponents element found")
            return False
        
        # Check if WebResource is already registered
        for component in root_components.findall('.//{*}RootComponent'):
            if component.get('schemaName') == webresource_name and component.get('type') == '61':
                print(f"    WebResource already registered in Solution.xml")
                return True
        
        # Create new RootComponent element for WebResource (type="61")
        new_component = ET.Element('RootComponent')
        new_component.set('type', '61')
        new_component.set('schemaName', webresource_name)
        new_component.set('behavior', '0')
        
        # Find appropriate insertion point (after other WebResources or before other types)
        insert_index = 0
        for idx, component in enumerate(root_components):
            comp_type = component.get('type')
            if comp_type == '61':  # WebResource
                insert_index = idx + 1
            elif int(comp_type or '0') > 61:
                break
        
        # Insert the new component
        root_components.insert(insert_index, new_component)
        
        # Write back to file with proper formatting
        tree.write(solution_xml_path, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except Exception as e:
        print(f"    ERROR: Failed to update Solution.xml: {e}")
        return False


def ensure_webresources_in_customizations(module_path: Path) -> bool:
    """
    Ensure Customizations.xml has a <WebResources /> element.
    This is required for the solution packager to include WebResource files.
    
    Args:
        module_path: Path to module root (e.g., government/court-case-management)
        
    Returns:
        True if element exists or was added successfully
    """
    try:
        customizations_xml_path = module_path / 'src' / 'Other' / 'Customizations.xml'
        
        if not customizations_xml_path.exists():
            print(f"    WARNING: Customizations.xml not found at {customizations_xml_path}")
            return False
        
        # Parse Customizations.xml
        tree = ET.parse(customizations_xml_path)
        root = tree.getroot()
        
        # Check if WebResources element already exists
        webresources_elem = root.find('.//WebResources')
        if webresources_elem is not None:
            return True  # Already exists
        
        # Need to add <WebResources /> element
        # Find the insertion point (after CustomControls, before AppModuleSiteMaps)
        insert_index = len(root)  # Default to end
        
        for idx, child in enumerate(root):
            # Insert after CustomControls or optionsets
            if child.tag in ['AppModuleSiteMaps', 'AppModules', 'EntityDataProviders']:
                insert_index = idx
                break
        
        # Create and insert WebResources element
        webresources_elem = ET.Element('WebResources')
        root.insert(insert_index, webresources_elem)
        
        # Write back to file with proper formatting
        tree.write(customizations_xml_path, encoding='utf-8', xml_declaration=True)
        
        print(f"    [OK] Added <WebResources /> to Customizations.xml")
        return True
        
    except Exception as e:
        print(f"    ERROR: Failed to update Customizations.xml: {e}")
        return False


def update_entity_icon(entity_xml_path: Path, icon_vector_name: str) -> bool:
    """
    Update Entity.xml with IconVectorName.
    
    Args:
        entity_xml_path: Path to Entity.xml file
        icon_vector_name: WebResource name to set
        
    Returns:
        True if updated successfully
    """
    try:
        # Parse Entity.xml
        tree = ET.parse(entity_xml_path)
        root = tree.getroot()
        
        # Find or create IconVectorName element
        # It should be inside EntityInfo/entity element
        icon_vector_elem = root.find('.//IconVectorName')
        
        if icon_vector_elem is None:
            # Find the entity element inside EntityInfo
            entity_elem = root.find('.//EntityInfo/entity')
            if entity_elem is None:
                print(f"    WARNING: No EntityInfo/entity element found")
                return False
            
            # Find insertion point - typically after CanEnableSyncToExternalSearchIndex
            # or before EnforceStateTransitions, or at the end of entity metadata
            insert_index = len(entity_elem)  # Default to end
            
            for idx, child in enumerate(entity_elem):
                # Insert after sync settings or before state transitions
                if child.tag in ['EnforceStateTransitions', 'CanChangeHierarchicalRelationship', 
                                 'EntityHelpUrlEnabled', 'ChangeTrackingEnabled']:
                    insert_index = idx
                    break
            
            # Create new IconVectorName element
            icon_vector_elem = ET.Element('IconVectorName')
            entity_elem.insert(insert_index, icon_vector_elem)
        
        # Set the value
        icon_vector_elem.text = icon_vector_name
        
        # Write back to file with proper formatting
        tree.write(entity_xml_path, encoding='utf-8', xml_declaration=True)
        
        return True
        
    except Exception as e:
        print(f"    ERROR: Failed to update {entity_xml_path}: {e}")
        return False


def create_webresources_and_update_entities(
    validated_approvals_path: Path,
    repo_root: Path,
    module_filter: str = None
):
    """
    Main function to create WebResources and update Entity.xml files.
    
    Args:
        validated_approvals_path: Path to approved_icons_validated.json
        repo_root: Root path of industry-apps repository
        module_filter: Optional module path to filter (e.g., "operations/asset-management")
    """
    print("="*70)
    print("Creating Icon WebResources")
    if module_filter:
        print(f"Module Filter: {module_filter}")
    print("="*70)
    
    # Load validated approvals
    print("\nLoading validated approvals...")
    with open(validated_approvals_path, 'r', encoding='utf-8') as f:
        all_validated = json.load(f)
    
    # Filter by module if specified
    if module_filter:
        # Normalize path separators to forward slashes for consistent comparison
        module_filter_normalized = module_filter.replace('\\', '/')
        validated = {
            k: v for k, v in all_validated.items()
            if v['module_path'].replace('\\', '/') == module_filter_normalized
        }
        print(f"Loaded {len(validated)} approved icons for module: {module_filter}")
        print(f"(Total across all modules: {len(all_validated)})")
    else:
        validated = all_validated
        print(f"Loaded {len(validated)} approved icons across all modules")
    
    # Check if any entities to process
    if not validated:
        print("\nWARNING: No entities to process after filtering!")
        if module_filter:
            print(f"   Module '{module_filter}' has no approved icons.")
            print(f"   Available modules in approved_icons_validated.json:")
            modules_available = set(v['module_path'] for v in all_validated.values())
            for mod in sorted(modules_available):
                count = sum(1 for v in all_validated.values() if v['module_path'] == mod)
                print(f"     - {mod} ({count} icons)")
        return
    
    # Process each approval
    created_count = 0
    updated_entity_count = 0
    updated_solution_count = 0
    failed_count = 0
    
    by_module = {}
    modules_customizations_checked = set()  # Track which modules we've checked
    
    for logical_name, approval_data in validated.items():
        icon_name = approval_data['icon_name']
        webresource_name = approval_data['webresource_name']
        svg_content = approval_data['svg_content']
        module_path_str = approval_data['module_path']
        entity_xml_path_str = approval_data['entity_xml_path']
        
        print(f"\nProcessing: {approval_data['entity_display_name']}")
        print(f"  Icon: {icon_name}")
        print(f"  WebResource: {webresource_name}")
        
        # Get paths
        module_path = repo_root / module_path_str
        entity_xml_path = Path(entity_xml_path_str)
        
        # Ensure Customizations.xml has WebResources element (once per module)
        if module_path_str not in modules_customizations_checked:
            ensure_webresources_in_customizations(module_path)
            modules_customizations_checked.add(module_path_str)
        
        try:
            # Create WebResource files
            data_xml_path, content_path = generate_webresource_files(
                approval_data['entity_display_name'],
                webresource_name,
                svg_content,
                module_path
            )
            print(f"  [OK] Created WebResource files")
            created_count += 1
            
            # Update Entity.xml
            if update_entity_icon(entity_xml_path, webresource_name):
                print(f"  [OK] Updated Entity.xml")
                updated_entity_count += 1
            else:
                print(f"  [ERROR] Failed to update Entity.xml")
                failed_count += 1
            
            # Update Solution.xml
            if update_solution_xml(module_path, webresource_name):
                print(f"  [OK] Updated Solution.xml")
                updated_solution_count += 1
            else:
                print(f"  [ERROR] Failed to update Solution.xml")
                failed_count += 1
            
            # Track by module
            by_module[module_path_str] = by_module.get(module_path_str, 0) + 1
            
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed_count += 1
    
    # Summary
    print("\n" + "="*70)
    print("WebResource Creation Complete!")
    print("="*70)
    print(f"WebResources created: {created_count}")
    print(f"Entity.xml files updated: {updated_entity_count}")
    print(f"Solution.xml files updated: {updated_solution_count}")
    print(f"Failed: {failed_count}")
    
    print(f"\nWebResources created by module:")
    for module, count in sorted(by_module.items()):
        print(f"  {module}: {count}")
    
    print("\n" + "="*70)
    print("\nNext steps:")
    print("1. Review the generated WebResource files")
    print("2. Review Entity.xml and Solution.xml changes (git diff)")
    print("3. Build and test the solution")
    print("4. Commit changes to git")
    print("="*70)


if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Create WebResource files and update XML for icon assignments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process all modules:
  python create_icon_webresources.py
  
  # Process only Asset Management module:
  python create_icon_webresources.py --module operations/asset-management
  
  # Process only Court Case Management module:
  python create_icon_webresources.py --module government/court-case-management
'''
    )
    parser.add_argument(
        '--module',
        type=str,
        help='Filter by module path (e.g., "operations/asset-management")'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )
    
    args = parser.parse_args()
    
    # Paths - data files are in .icons folder at repo root
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent.parent.parent  # ui-tools/backend/scripts -> repo root
    icons_dir = repo_root / '.icons'
    validated_approvals_path = icons_dir / 'approved_icons_validated.json'
    
    # Check if required file exists
    if not validated_approvals_path.exists():
        print(f"ERROR: Required file not found: {validated_approvals_path}")
        print("Run process_icon_approvals.py first.")
        sys.exit(1)
    
    # Show what will be processed
    if args.module:
        print("="*70)
        print(f"Module Filter: {args.module}")
        print("="*70)
    
    # Confirm before making changes
    if not args.yes:
        print("="*70)
        print("WARNING: This will create WebResource files and modify XML files")
        print("="*70)
        print("\nThis script will:")
        print("1. Create WebResource .data.xml files")
        print("2. Create WebResource SVG content files")
        print("3. Update Entity.xml IconVectorName elements")
        print("4. Update Solution.xml RootComponent elements")
        if args.module:
            print(f"\nProcessing ONLY module: {args.module}")
        else:
            print("\nProcessing ALL modules")
        print("\nMake sure you have a backup or are in a git branch!")
        
        response = input("\nContinue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    # Create WebResources and update entities
    create_webresources_and_update_entities(validated_approvals_path, repo_root, args.module)
