#!/usr/bin/env python3
"""
Configuration Helper CLI

Retrieves available deployments, environments, and solutions from config files and workspace.

Usage:
    python cli_get_config.py
"""

import json
import sys
from pathlib import Path

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from config import load_deployment_config, scan_solutions


def get_config() -> dict:
    """
    Get configuration options from deployments.json and workspace solutions.
    
    Returns:
        {
            "deployments": ["CDX FAST", ...],
            "environments": {
                "CDX FAST": ["Development", "Test", ...]
            },
            "solutions": [
                {
                    "name": "appbase_eventmanagement",
                    "prefix": "appbase_",
                    "module": "event-management",
                    "category": "external-engagement"
                }
            ]
        }
    """
    result = {
        'deployments': [],
        'environments': {},
        'solutions': []
    }
    
    # Load deployment configuration
    try:
        config_data = load_deployment_config()
        deployments = config_data.get("Deployments", {})
        
        for deployment_name, deployment_data in deployments.items():
            result['deployments'].append(deployment_name)
            
            # Extract environment names
            env_urls = deployment_data.get('Auth', {}).get('EnvironmentUrls', {})
            result['environments'][deployment_name] = list(env_urls.keys())
    
    except Exception as e:
        print(f"Warning: Could not read deployment configuration: {e}", file=sys.stderr)
    
    # Scan workspace for solutions
    try:
        workspace_root = Path(__file__).parent.parent
        solutions = scan_solutions(workspace_root)
        
        result['solutions'] = [
            {
                'name': solution['name'],
                'prefix': solution['prefix'],
                'module': solution['module'],
                'category': solution['category']
            }
            for solution in solutions
        ]
    
    except Exception as e:
        print(f"Warning: Could not scan workspace for solutions: {e}", file=sys.stderr)
    
    return result


def main():
    try:
        config = get_config()
        print(json.dumps(config, indent=2))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
