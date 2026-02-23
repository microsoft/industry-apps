"""
Configuration utilities for Dataverse operations.

Handles loading deployment configurations, extracting authentication credentials,
and scanning solution files for publisher information.
"""

import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any


def load_deployment_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load deployment configuration from deployments.json.
    
    Args:
        config_path: Path to deployments.json (defaults to .config/deployments.json)
    
    Returns:
        Dictionary with deployment configuration
    """
    if config_path is None:
        config_path = Path('.config/deployments.json')
        
        # Try from current directory, then parent
        if not config_path.exists():
            config_path = Path(__file__).parent.parent / '.config' / 'deployments.json'
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    # Remove _comment key if present
    config_data.pop('_comment', None)
    
    return config_data


def get_deployment_auth(
    config: Dict[str, Any],
    deployment_name: str,
    environment_name: str
) -> Dict[str, str]:
    """
    Extract authentication credentials for a specific deployment and environment.
    
    Args:
        config: Deployment configuration dictionary
        deployment_name: Name of deployment (e.g., "CDX FAST")
        environment_name: Name of environment (e.g., "Development")
    
    Returns:
        Dictionary with tenant_id, client_id, client_secret, environment_url
        
    Raises:
        KeyError: If deployment or environment not found
        ValueError: If authentication configuration incomplete
    """
    if deployment_name not in config:
        raise KeyError(f"Deployment '{deployment_name}' not found in configuration")
    
    deployment = config[deployment_name]
    
    if 'Auth' not in deployment:
        raise ValueError(f"No Auth configuration for deployment '{deployment_name}'")
    
    auth = deployment['Auth']
    
    if 'EnvironmentUrls' not in auth or environment_name not in auth['EnvironmentUrls']:
        raise KeyError(f"Environment '{environment_name}' not found in deployment '{deployment_name}'")
    
    environment_url = auth['EnvironmentUrls'][environment_name]
    
    # Validate required auth fields
    required_fields = ['TenantId', 'ClientId', 'ClientSecret']
    missing = [f for f in required_fields if f not in auth]
    if missing:
        raise ValueError(f"Missing auth fields for '{deployment_name}': {missing}")
    
    return {
        'tenant_id': auth['TenantId'],
        'client_id': auth['ClientId'],
        'client_secret': auth['ClientSecret'],
        'environment_url': environment_url
    }


def read_solution_version(solution_xml_path: Path) -> str:
    """
    Read version from Solution.xml file.
    
    Args:
        solution_xml_path: Path to Solution.xml
    
    Returns:
        Version string in format X.X.X.X (defaults to "1.0.0.0" if not found)
    """
    if not solution_xml_path.exists():
        return "1.0.0.0"
    
    try:
        tree = ET.parse(solution_xml_path)
        root = tree.getroot()
        
        # Find the Version element (with or without namespace)
        version_elem = root.find(".//{http://www.w3.org/2001/XMLSchema-instance}Version")
        if version_elem is None:
            version_elem = root.find(".//Version")
        
        if version_elem is not None and version_elem.text:
            version = version_elem.text.strip()
            
            # Normalize to 4-part version
            parts = version.split('.')
            while len(parts) < 4:
                parts.append('0')
            
            return '.'.join(parts[:4])
        
        return "1.0.0.0"
    except Exception:
        return "1.0.0.0"


def scan_solutions(workspace_root: Optional[Path] = None) -> List[Dict[str, str]]:
    """
    Scan workspace for Power Platform solutions and extract metadata.
    
    Args:
        workspace_root: Root directory of workspace (defaults to current directory)
    
    Returns:
        List of dictionaries with solution metadata:
        - name: Solution unique name
        - prefix: Publisher prefix
        - module: Module directory name
        - category: Category directory name
        - version: Solution version
    """
    if workspace_root is None:
        workspace_root = Path('.')
    
    solutions = []
    
    # Find all Solution.xml files
    solution_files = list(workspace_root.glob('**/src/Other/Solution.xml'))
    
    for solution_file in solution_files:
        try:
            tree = ET.parse(solution_file)
            root = tree.getroot()
            
            # Extract publisher prefix
            publisher_elem = root.find('.//Publisher/CustomizationPrefix')
            if publisher_elem is None:
                publisher_elem = root.find('.//{*}Publisher/{*}CustomizationPrefix')
            
            # Extract solution unique name
            unique_name_elem = root.find('.//UniqueName')
            if unique_name_elem is None:
                unique_name_elem = root.find('.//{*}UniqueName')
            
            if publisher_elem is not None and unique_name_elem is not None:
                prefix = publisher_elem.text
                unique_name = unique_name_elem.text
                
                # Extract category and module from path
                # Path format: category/module/src/Other/Solution.xml
                parts = solution_file.parts
                if len(parts) >= 4:
                    module = parts[-4]
                    category = parts[-5]
                    
                    version = read_solution_version(solution_file.parent.parent.parent)
                    
                    solutions.append({
                        'name': unique_name,
                        'prefix': prefix + '_',
                        'module': module,
                        'category': category,
                        'version': version
                    })
        except Exception:
            # Skip files that can't be parsed
            continue
    
    return solutions


def get_solution_info(solution_unique_name: str, workspace_root: Optional[Path] = None) -> Optional[Dict[str, str]]:
    """
    Get information about a specific solution.
    
    Args:
        solution_unique_name: Solution unique name (e.g., "appbase_eventmanagement")
        workspace_root: Root directory of workspace
    
    Returns:
        Dictionary with solution metadata, or None if not found
    """
    solutions = scan_solutions(workspace_root)
    
    for solution in solutions:
        if solution['name'] == solution_unique_name:
            return solution
    
    return None


def get_next_option_value(solution_path: Path, option_value_prefix: str) -> int:
    """
    Find the next available option value by scanning existing option sets.
    
    Args:
        solution_path: Path to solution directory (containing src/)
        option_value_prefix: Option value prefix (e.g., "14713")
    
    Returns:
        Next available option value (integer)
    """
    option_sets_dir = solution_path / "src" / "OptionSets"
    
    # Find the maximum existing value
    max_value = 0
    if option_sets_dir.exists():
        for xml_file in option_sets_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                for option_elem in tree.findall(".//option"):
                    value_str = option_elem.get("value", "0")
                    try:
                        value_int = int(value_str)
                        if value_int > max_value:
                            max_value = value_int
                    except ValueError:
                        pass
            except Exception:
                # Skip files that can't be parsed
                pass
    
    # Return max + 1, or start from prefix + "0000" if no existing values
    base_value = int(option_value_prefix + "0000")
    return max(max_value + 1, base_value)


def assign_option_values(
    options: List[Dict[str, Any]],
    starting_value: int
) -> List[Dict[str, Any]]:
    """
    Assign integer values to option definitions.
    
    Args:
        options: List of option dictionaries with 'label' and optional 'value' keys
        starting_value: Starting value for auto-assignment
    
    Returns:
        List of options with 'value' assigned as integers
    """
    result = []
    current_value = starting_value
    
    for opt in options:
        if opt.get('value') is not None:
            try:
                result.append({
                    'label': opt['label'],
                    'value': int(opt['value'])
                })
            except (ValueError, TypeError):
                # If conversion fails, auto-assign
                result.append({
                    'label': opt['label'],
                    'value': current_value
                })
                current_value += 1
        else:
            result.append({
                'label': opt['label'],
                'value': current_value
            })
            current_value += 1
    
    return result
