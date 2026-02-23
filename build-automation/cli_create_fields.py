#!/usr/bin/env python3
"""
Field Creation CLI

Creates fields on a Dataverse entity directly via DataverseClient.

Usage:
    python cli_create_fields.py --deployment "CDX FAST" --environment Development --table appbase_event --prefix appbase_ --fields fields.json
"""

import argparse
import json
import sys
from pathlib import Path

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient
from config import load_deployment_config, get_deployment_auth
from schema_helpers import generate_schema_name


def create_fields(
    deployment: str,
    environment: str,
    table_name: str,
    prefix: str,
    fields: list[dict]
) -> dict:
    """
    Create fields on a Dataverse entity.
    
    Args:
        deployment: Deployment name
        environment: Environment name
        table_name: Logical name of the entity
        prefix: Publisher prefix (e.g., "appbase_")
        fields: List of field definitions from parser
    
    Returns:
        {
            "created": [schema names],
            "failed": [{"displayName": "...", "error": "..."}]
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
        
        # Create Dataverse client
        client = DataverseClient(
            environment_url=auth['environment_url'],
            tenant_id=auth['tenant_id'],
            client_id=auth['client_id'],
            client_secret=auth['client_secret']
        )
        
        # Authenticate
        client.authenticate()
        
        print(f"Creating {len(fields)} fields on {table_name}...\n", file=sys.stderr, flush=True)
        
        # Create each field
        for field in fields:
            # Generate PascalCase schema name for proper Dataverse naming
            schema_name = generate_schema_name(field['displayName'], prefix, pascal_case=True)
            
            # Special handling for Yes/No fields: Convert to Choice field referencing appbase_yesno
            field_type = field['type']
            if field_type == "Yes / No":
                field_type = "Choice"
                field['optionSetSchemaName'] = "appbase_yesno"
            
            # Build field definition
            field_def = {
                "schemaName": schema_name,
                "displayName": field['displayName'],
                "type": field_type,
                "required": field.get('required', False),
                "description": ""
            }
            
            # Add type-specific parameters
            if field.get('maxLength'):
                field_def['maxLength'] = field['maxLength']
            
            if field.get('optionSetSchemaName'):
                field_def['optionSetSchemaName'] = field['optionSetSchemaName']
            
            if field.get('targetTableLogicalName'):
                field_def['targetTableLogicalName'] = field['targetTableLogicalName']
            
            print(f"Creating field '{field['displayName']}' → {schema_name}...", file=sys.stderr, flush=True)
            
            try:
                # Create the field using generic create_field method
                result = client.create_field(table_name, field_def)
                
                if result.get('success'):
                    print(f"✓ Created {schema_name}", file=sys.stderr, flush=True)
                    results['created'].append(schema_name)
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"✗ Failed to create '{field['displayName']}': {error}", file=sys.stderr, flush=True)
                    results['failed'].append({
                        'displayName': field['displayName'],
                        'error': error
                    })
                    
            except Exception as e:
                error_msg = str(e)
                print(f"✗ Failed to create '{field['displayName']}': {error_msg}", file=sys.stderr, flush=True)
                results['failed'].append({
                    'displayName': field['displayName'],
                    'error': error_msg
                })
    
    except Exception as e:
        # Top-level error (config, auth, etc.)
        print(f"✗ Fatal error: {e}", file=sys.stderr, flush=True)
        return {
            'created': [],
            'failed': [{'displayName': 'ALL', 'error': str(e)}]
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Create fields on a Dataverse entity'
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
        '--table',
        required=True,
        help='Entity logical name (e.g., appbase_event)'
    )
    parser.add_argument(
        '--prefix',
        required=True,
        help='Publisher prefix (e.g., appbase_)'
    )
    parser.add_argument(
        '--fields',
        required=True,
        type=Path,
        help='JSON file with field definitions'
    )
    
    args = parser.parse_args()
    
    if not args.fields.exists():
        print(json.dumps({'error': f'File not found: {args.fields}'}), file=sys.stderr)
        sys.exit(1)
    
    try:
        fields = json.loads(args.fields.read_text())
        
        if not isinstance(fields, list):
            print(json.dumps({'error': 'Fields must be a JSON array'}), file=sys.stderr)
            sys.exit(1)
        
        results = create_fields(args.deployment, args.environment, args.table, args.prefix, fields)
        
        print("\n" + "="*60, file=sys.stderr)
        print(f"Summary: {len(results['created'])} created, {len(results['failed'])} failed", file=sys.stderr)
        print("="*60 + "\n", file=sys.stderr)
        
        print(json.dumps(results, indent=2))
        
        sys.exit(0 if len(results['failed']) == 0 else 1)
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(2)


if __name__ == '__main__':
    main()
