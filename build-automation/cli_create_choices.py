#!/usr/bin/env python3
"""
Choice Set Creation CLI

Creates global option sets (choice fields) in Dataverse directly via DataverseClient.

Usage:
    python cli_create_choices.py --deployment "CDX FAST" --environment Development --solution appbase_eventmanagement --prefix appbase_ --choices choices.json
"""

import argparse
import json
import sys
from pathlib import Path

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient
from config import (
    load_deployment_config,
    get_deployment_auth,
    get_solution_info,
    get_next_option_value,
    assign_option_values
)
from schema_helpers import generate_schema_name


def create_choice_sets(
    deployment: str,
    environment: str,
    solution: str,
    prefix: str,
    choice_sets: list[dict]
) -> dict:
    """
    Create choice sets in Dataverse.
    
    Args:
        deployment: Deployment name
        environment: Environment name
        solution: Solution unique name
        prefix: Publisher prefix (e.g., "appbase_")
        choice_sets: List of {name, description, values}
    
    Returns:
        {
            "created": [{"name": "...", "schemaName": "...", "metadataId": "..."}],
            "failed": [{"name": "...", "error": "..."}]
        }
    """
    results = {
        'created': [],
        'failed': []
    }
    
    try:
        # Load deployment configuration
        config = load_deployment_config()
        deployments = config.get("Deployments", {})
        
        auth = get_deployment_auth(deployments, deployment, environment)
        
        # Get solution information
        solution_info = get_solution_info(solution)
        if not solution_info:
            raise ValueError(f"Solution '{solution}' not found in workspace")
        
        # Extract option value prefix from solution metadata or use default
        # TODO: Get this from solution metadata when available
        option_value_prefix = "14713"  # Default prefix
        
        # Get solution path for scanning existing option values
        workspace_root = Path(__file__).parent.parent
        solution_path = workspace_root / solution_info['category'] / solution_info['module']
        
        # Get next available option value
        next_value = get_next_option_value(solution_path, option_value_prefix)
        
        # Create Dataverse client
        client = DataverseClient(
            environment_url=auth['environment_url'],
            tenant_id=auth['tenant_id'],
            client_id=auth['client_id'],
            client_secret=auth['client_secret']
        )
        
        # Authenticate
        client.authenticate()
        
        print(f"✓ Connected to Dataverse", file=sys.stderr, flush=True)
        
        # Create each choice set
        for choice_set in choice_sets:
            name = choice_set['name']
            description = choice_set.get('description', '')
            values = choice_set['values']
            
            # Generate schema name
            schema_name = generate_schema_name(name, prefix)
            
            print(f"Creating choice set '{name}' → {schema_name}...", file=sys.stderr, flush=True)
            
            # Convert string values to option format with auto-assigned values
            options = [{'label': value, 'value': None} for value in values]
            options_with_values = assign_option_values(options, next_value)
            next_value += len(options_with_values)
            
            try:
                # Create the global option set
                print(f"  → Calling create_global_optionset...", file=sys.stderr, flush=True)
                sys.stderr.flush()
                
                result = client.create_global_optionset(
                    schema_name=schema_name,
                    display_name=name,
                    description=description,
                    options=options_with_values,
                    solution_unique_name=solution
                )
                
                print(f"  → Got result: {result.get('success')}", file=sys.stderr, flush=True)
                sys.stderr.flush()
                
                if result.get('success'):
                    print(f"✓ Created '{name}' → {schema_name}", file=sys.stderr, flush=True)
                    results['created'].append({
                        'name': name,
                        'schemaName': schema_name,
                        'metadataId': result.get('metadata_id', '')
                    })
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"✗ Failed to create '{name}': {error}", file=sys.stderr, flush=True)
                    results['failed'].append({
                        'name': name,
                        'error': error
                    })
                    
            except Exception as e:
                error_msg = str(e)
                print(f"✗ Failed to create '{name}': {error_msg}", file=sys.stderr, flush=True)
                results['failed'].append({
                    'name': name,
                    'error': error_msg
                })
    
    except Exception as e:
        # Top-level error (config, auth, etc.)
        print(f"✗ Fatal error: {e}", file=sys.stderr, flush=True)
        return {
            'created': [],
            'failed': [{'name': 'ALL', 'error': str(e)}]
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Create global option sets in Dataverse'
    )
    parser.add_argument(
        '--deployment',
        required=True,
        help='Deployment name'
    )
    parser.add_argument(
        '--environment',
        required=True,
        help='Environment name'
    )
    parser.add_argument(
        '--solution',
        required=True,
        help='Solution unique name (e.g., appbase_eventmanagement)'
    )
    parser.add_argument(
        '--prefix',
        required=True,
        help='Publisher prefix (e.g., appbase_)'
    )
    parser.add_argument(
        '--choices',
        required=True,
        type=Path,
        help='JSON file with choice set definitions'
    )
    
    args = parser.parse_args()
    
    if not args.choices.exists():
        print(json.dumps({'error': f'File not found: {args.choices}'}), file=sys.stderr)
        import os
        os._exit(1)
    
    try:
        choice_sets = json.loads(args.choices.read_text())
        
        if not isinstance(choice_sets, list):
            print(json.dumps({'error': 'Choice sets must be a JSON array'}), file=sys.stderr)
            import os
            os._exit(1)
        
        results = create_choice_sets(args.deployment, args.environment, args.solution, args.prefix, choice_sets)
        
        print("\n" + "="*60, file=sys.stderr)
        print(f"Summary: {len(results['created'])} created, {len(results['failed'])} failed", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
        
        print(json.dumps(results, indent=2))
        
        # Flush all output before exit
        sys.stdout.flush()
        sys.stderr.flush()
        
        # Use os._exit to force termination (MSAL may keep background threads alive)
        import os
        os._exit(0 if len(results['failed']) == 0 else 1)
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.stderr.flush()
        import os
        os._exit(2)


if __name__ == '__main__':
    main()
