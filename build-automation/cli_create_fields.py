#!/usr/bin/env python3
"""
Field Creation CLI

Creates fields on a Dataverse entity directly via DataverseClient.
Uses fire-and-forget submission with polling verification for reliability.

Usage:
    python cli_create_fields.py --deployment "CDX FAST" --environment "FAST APPS" --table appbase_event --prefix appbase_ --fields fields.json
"""

import argparse
import json
import sys
import os
import subprocess
from pathlib import Path
from typing import List, Dict

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
    fields: list[dict],
    verify: bool = True,
    poll_interval: int = 5,
    max_wait: int = 180
) -> dict:
    """
    Create fields on a Dataverse entity using fire-and-forget with verification.
    
    Submits all field creation requests, then polls to verify they were created.
    This approach is more reliable than waiting for HTTP responses which can timeout
    even when Dataverse successfully processes the request.
    
    Args:
        deployment: Deployment name
        environment: Environment name
        table_name: Logical name of the entity
        prefix: Publisher prefix (e.g., "appbase_")
        fields: List of field definitions from parser
        verify: Whether to poll Dataverse to verify creation (default: True)
        poll_interval: Seconds between verification polls (default: 5)
        max_wait: Maximum seconds to wait for verification (default: 180)
    
    Returns:
        {
            "submitted": [schema names],
            "verified": [schema names],
            "failed": [{"displayName": "...", "error": "..."}]
        }
    """
    results = {
        'submitted': [],
        'verified': [],
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
        
        print(f"Submitting {len(fields)} field creation requests to {table_name}...\n", file=sys.stderr, flush=True)
        
        # Submit each field creation request
        expected_schema_names = []
        
        for field in fields:
            # Generate PascalCase schema name for proper Dataverse naming
            schema_name = generate_schema_name(field['displayName'], prefix, pascal_case=True)
            expected_schema_names.append(schema_name)
            
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
            
            print(f"Submitting '{field['displayName']}' → {schema_name}...", file=sys.stderr, flush=True)
            
            try:
                # Submit the field creation request (non-blocking)
                result = client.create_field(table_name, field_def)
                
                # Evaluate response to determine if we should verify
                if result.get('success'):
                    # Success - mark submitted and verify
                    results['submitted'].append(schema_name)
                    print(f"  ✓ Submitted", file=sys.stderr, flush=True)
                    
                elif result.get('error'):
                    error = result.get('error', 'Unknown error')
                    
                    # "Already exists" or "not unique" = recoverable, verify it exists
                    if 'not unique' in error.lower() or 'already exists' in error.lower():
                        results['submitted'].append(schema_name)
                        print(f"  ℹ Already exists (will verify)", file=sys.stderr, flush=True)
                    
                    # Validation errors = definite failure, don't verify
                    elif any(x in error.lower() for x in [
                        'invalid', 'unsupported', 'required', 'missing',
                        'cannot', 'not found', 'does not exist'
                    ]):
                        print(f"  ✗ Rejected: {error}", file=sys.stderr, flush=True)
                        results['failed'].append({
                            'displayName': field['displayName'],
                            'error': error
                        })
                    
                    # Other errors = uncertain, mark submitted and verify
                    else:
                        results['submitted'].append(schema_name)
                        print(f"  ⚠ Error (will verify): {error}", file=sys.stderr, flush=True)
                    
            except Exception as e:
                error_msg = str(e)
                
                # Timeouts = uncertain, mark submitted and verify
                if 'timeout' in error_msg.lower() or 'timed out' in error_msg.lower():
                    results['submitted'].append(schema_name)
                    print(f"  ℹ Timed out (will verify)", file=sys.stderr, flush=True)
                
                # Connection/network errors = uncertain, mark submitted and verify
                elif any(x in error_msg.lower() for x in ['connection', 'network', 'socket']):
                    results['submitted'].append(schema_name)
                    print(f"  ⚠ Connection issue (will verify)", file=sys.stderr, flush=True)
                
                # Other exceptions = definite failure
                else:
                    print(f"  ✗ Failed: {error_msg}", file=sys.stderr, flush=True)
                    results['failed'].append({
                        'displayName': field['displayName'],
                        'error': error_msg
                    })
        
        print(f"\n✓ Submitted {len(results['submitted'])} field creation requests", file=sys.stderr, flush=True)
        
        # Verify what actually got created by polling Dataverse
        if verify and results['submitted']:
            print(f"\n{'='*60}", file=sys.stderr, flush=True)
            print(f"Verifying field creation (polling every {poll_interval}s)...", file=sys.stderr, flush=True)
            print(f"{'='*60}\n", file=sys.stderr, flush=True)
            
            # Import and run verification
            import importlib.util
            verify_script = Path(__file__).parent / 'cli_verify_fields.py'
            spec = importlib.util.spec_from_file_location("cli_verify_fields", verify_script)
            verify_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(verify_module)
            
            verify_results = verify_module.verify_fields(
                deployment=deployment,
                environment=environment,
                table_logical_name=table_name,
                expected_fields=expected_schema_names,
                poll_interval=poll_interval,
                max_wait=max_wait
            )
            
            results['verified'] = verify_results.get('found', [])
            
            # Update failed list based on verification
            missing = verify_results.get('missing', [])
            for field_name in missing:
                orig_field = next((f for f in fields if generate_schema_name(f['displayName'], prefix, pascal_case=True) == field_name), None)
                display_name = orig_field['displayName'] if orig_field else field_name
                
                if not any(f['displayName'] == display_name for f in results['failed']):
                    results['failed'].append({
                        'displayName': display_name,
                        'error': 'Not found after verification timeout'
                    })
        else:
            # No verification - assume submitted = verified
            results['verified'] = results['submitted']
    
    except Exception as e:
        print(f"✗ Fatal error: {e}", file=sys.stderr, flush=True)
        return {
            'submitted': [],
            'verified': [],
            'failed': [{'displayName': 'ALL', 'error': str(e)}]
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Create fields on a Dataverse entity with verification'
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
    parser.add_argument(
        '--no-verify',
        action='store_true',
        help='Skip verification polling (faster but less reliable)'
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=5,
        help='Seconds between verification polls (default: 5)'
    )
    parser.add_argument(
        '--max-wait',
        type=int,
        default=180,
        help='Maximum seconds to wait for verification (default: 180)'
    )
    
    args = parser.parse_args()
    
    if not args.fields.exists():
        print(json.dumps({'error': f'File not found: {args.fields}'}), file=sys.stderr, flush=True)
        os._exit(1)
    
    try:
        fields = json.loads(args.fields.read_text())
        
        if not isinstance(fields, list):
            print(json.dumps({'error': 'Fields must be a JSON array'}), file=sys.stderr, flush=True)
            os._exit(1)
        
        results = create_fields(
            args.deployment,
            args.environment,
            args.table,
            args.prefix,
            fields,
            verify=not args.no_verify,
            poll_interval=args.poll_interval,
            max_wait=args.max_wait
        )
        
        print("\n" + "="*60, file=sys.stderr, flush=True)
        print(f"Summary: {len(results['verified'])} verified, {len(results['failed'])} failed", file=sys.stderr, flush=True)
        print("="*60 + "\n", file=sys.stderr, flush=True)
        
        print(json.dumps(results, indent=2), flush=True)
        
        # Exit with proper code
        os._exit(0 if len(results['failed']) == 0 else 1)
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr, flush=True)
        os._exit(2)


if __name__ == '__main__':
    main()

