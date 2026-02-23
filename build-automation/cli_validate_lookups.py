#!/usr/bin/env python3
"""
Lookup Validation CLI

Validates that target tables exist in Dataverse before creating lookup fields.

Usage:
    python cli_validate_lookups.py --deployment "CDX FAST" --environment "FAST APPS" --targets "appbase_location,appbase_organizationunit"
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient
from config import load_deployment_config, get_deployment_auth


def validate_lookup_targets(
    deployment: str,
    environment: str,
    target_tables: List[str]
) -> Dict[str, any]:
    """
    Validate that target tables exist in Dataverse.
    
    Args:
        deployment: Deployment name
        environment: Environment name
        target_tables: List of logical table names (e.g., ["appbase_location", "appbase_hrposition"])
    
    Returns:
        {
            "valid": [logical names that exist],
            "invalid": [logical names that don't exist],
            "allEntities": [all custom entities in environment]
        }
    """
    results = {
        'valid': [],
        'invalid': [],
        'allEntities': []
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
        
        print(f"✓ Connected to Dataverse", file=sys.stderr, flush=True)
        print(f"Validating {len(target_tables)} lookup target(s)...\n", file=sys.stderr, flush=True)
        
        # Get all entity definitions from Dataverse
        entities = client.get_entity_definitions()
        entity_logical_names = {e['logicalName'].lower() for e in entities}
        
        # Store all entities for reference
        results['allEntities'] = [
            {
                "logicalName": e['logicalName'],
                "displayName": e['displayName']
            }
            for e in entities
        ]
        
        # Validate each target table
        for target in target_tables:
            target_lower = target.lower()
            if target_lower in entity_logical_names:
                results['valid'].append(target)
                print(f"✓ Found: {target}", file=sys.stderr, flush=True)
            else:
                results['invalid'].append(target)
                print(f"✗ Not found: {target}", file=sys.stderr, flush=True)
        
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"Summary: {len(results['valid'])} valid, {len(results['invalid'])} invalid", file=sys.stderr)
        print(f"{'='*60}\n", file=sys.stderr)
        
    except Exception as e:
        print(f"✗ Fatal error: {e}", file=sys.stderr, flush=True)
        return {
            'valid': [],
            'invalid': target_tables,
            'allEntities': [],
            'error': str(e)
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Validate lookup target tables exist in Dataverse'
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
        '--targets',
        required=True,
        help='Comma-separated list of target table logical names'
    )
    parser.add_argument(
        '--list-all',
        action='store_true',
        help='Include all entities in output (for reference)'
    )
    
    args = parser.parse_args()
    
    # Parse comma-separated targets
    target_tables = [t.strip() for t in args.targets.split(',') if t.strip()]
    
    if not target_tables:
        print(json.dumps({'error': 'No target tables specified'}), file=sys.stderr)
        sys.exit(1)
    
    # Validate targets
    results = validate_lookup_targets(
        deployment=args.deployment,
        environment=args.environment,
        target_tables=target_tables
    )
    
    # Remove allEntities unless --list-all flag is used
    if not args.list_all:
        results.pop('allEntities', None)
    
    # Print JSON result to stdout
    print(json.dumps(results, indent=2))
    
    # Exit with error code if any targets are invalid
    if results.get('invalid'):
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
