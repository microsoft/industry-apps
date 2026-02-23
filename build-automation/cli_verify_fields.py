#!/usr/bin/env python3
"""
Field Verification CLI

Polls Dataverse to verify which fields exist on a table. Used after field creation
to confirm success without relying on HTTP timeouts.

Usage:
    python cli_verify_fields.py --deployment "CDX FAST" --environment "FAST APPS" --table appbase_hrposition --expected "appbase_PositionNumber,appbase_FTE,appbase_Location"
    
    Or just check all fields:
    python cli_verify_fields.py --deployment "CDX FAST" --environment "FAST APPS" --table appbase_hrposition
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Set, Optional

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient
from config import load_deployment_config, get_deployment_auth


def get_table_fields(client: DataverseClient, table_logical_name: str) -> Set[str]:
    """
    Get all custom field logical names for a table.
    
    Returns:
        Set of lowercase field logical names (e.g., {"appbase_positionnumber", "appbase_fte"})
    """
    url = f"{client.environment_url}/api/data/{client.API_VERSION}/EntityDefinitions(LogicalName='{table_logical_name}')/Attributes"
    params = {
        "$select": "LogicalName,DisplayName,AttributeType,IsCustomAttribute"
    }
    
    try:
        import httpx
        with httpx.Client() as http_client:
            response = http_client.get(
                url,
                headers=client._get_headers(),
                params=params,
                timeout=30.0
            )
            
            if response.status_code == 200:
                data = response.json()
                fields = set()
                
                for attr in data.get("value", []):
                    # Only include custom attributes
                    if attr.get("IsCustomAttribute", False):
                        logical_name = attr.get("LogicalName", "")
                        if logical_name:
                            fields.add(logical_name.lower())
                
                return fields
            else:
                print(f"✗ Error fetching fields: HTTP {response.status_code}", file=sys.stderr, flush=True)
                return set()
                
    except Exception as e:
        print(f"✗ Error fetching fields: {e}", file=sys.stderr, flush=True)
        return set()


def verify_fields(
    deployment: str,
    environment: str,
    table_logical_name: str,
    expected_fields: Optional[List[str]] = None,
    poll_interval: int = 5,
    max_wait: int = 180
) -> Dict[str, any]:
    """
    Verify fields exist on a table, optionally polling until all are found.
    
    Args:
        deployment: Deployment name
        environment: Environment name
        table_logical_name: Logical name of table (e.g., "appbase_hrposition")
        expected_fields: Optional list of expected field schema names (if None, just returns current fields)
        poll_interval: Seconds between polling attempts
        max_wait: Maximum seconds to wait for all fields
        
    Returns:
        {
            "found": [field names that exist],
            "missing": [field names not found],
            "all_custom_fields": [all custom fields on the table]
        }
    """
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
        
        # If no expected fields, just return current state
        if not expected_fields:
            print(f"Fetching all custom fields on {table_logical_name}...\n", file=sys.stderr, flush=True)
            existing = get_table_fields(client, table_logical_name)
            return {
                "found": sorted(list(existing)),
                "missing": [],
                "all_custom_fields": sorted(list(existing))
            }
        
        # Convert expected fields to lowercase for comparison
        expected_lower = {f.lower() for f in expected_fields}
        
        print(f"Verifying {len(expected_fields)} fields on {table_logical_name}...", file=sys.stderr, flush=True)
        print(f"Will poll every {poll_interval}s for up to {max_wait}s\n", file=sys.stderr, flush=True)
        
        start_time = time.time()
        found = set()
        last_found_count = 0
        
        while True:
            elapsed = time.time() - start_time
            
            # Get current fields
            existing = get_table_fields(client, table_logical_name)
            
            # Check which expected fields exist
            found = expected_lower & existing
            missing = expected_lower - existing
            
            # Show progress if new fields appeared
            if len(found) > last_found_count:
                newly_found = found - {f.lower() for f in ([] if last_found_count == 0 else [])}
                for field in sorted(found):
                    if field.lower() not in [f.lower() for f in []]:
                        # Find original case from expected_fields
                        original = next((f for f in expected_fields if f.lower() == field), field)
                        print(f"  ✓ Found: {original}", file=sys.stderr, flush=True)
                last_found_count = len(found)
            
            # Check if all found or timeout
            if not missing:
                print(f"\n{'='*60}", file=sys.stderr, flush=True)
                print(f"✓ All {len(found)} fields verified in {elapsed:.1f}s", file=sys.stderr, flush=True)
                print(f"{'='*60}\n", file=sys.stderr, flush=True)
                break
            
            if elapsed >= max_wait:
                print(f"\n{'='*60}", file=sys.stderr, flush=True)
                print(f"⚠ Timeout after {elapsed:.1f}s", file=sys.stderr, flush=True)
                print(f"Found: {len(found)}/{len(expected_fields)}", file=sys.stderr, flush=True)
                print(f"{'='*60}\n", file=sys.stderr, flush=True)
                break
            
            # Show status
            if len(found) < len(expected_fields):
                print(f"  [{elapsed:.0f}s] Found {len(found)}/{len(expected_fields)} fields...", file=sys.stderr, flush=True)
            
            # Wait before next poll
            time.sleep(poll_interval)
        
        # Return results
        return {
            "found": sorted([f for f in expected_fields if f.lower() in found]),
            "missing": sorted([f for f in expected_fields if f.lower() in missing]),
            "all_custom_fields": sorted(list(existing))
        }
        
    except Exception as e:
        error_msg = f"Verification failed: {str(e)}"
        print(f"✗ {error_msg}", file=sys.stderr, flush=True)
        return {
            "found": [],
            "missing": expected_fields or [],
            "all_custom_fields": [],
            "error": error_msg
        }


def main():
    parser = argparse.ArgumentParser(
        description='Verify fields exist on a Dataverse table'
    )
    parser.add_argument(
        '--deployment',
        required=True,
        help='Deployment name (e.g., "CDX FAST")'
    )
    parser.add_argument(
        '--environment',
        required=True,
        help='Environment name (e.g., "FAST APPS")'
    )
    parser.add_argument(
        '--table',
        required=True,
        help='Table logical name (e.g., "appbase_hrposition")'
    )
    parser.add_argument(
        '--expected',
        help='Comma-separated list of expected field schema names (if omitted, lists all fields)'
    )
    parser.add_argument(
        '--poll-interval',
        type=int,
        default=5,
        help='Seconds between polling attempts (default: 5)'
    )
    parser.add_argument(
        '--max-wait',
        type=int,
        default=180,
        help='Maximum seconds to wait (default: 180)'
    )
    
    args = parser.parse_args()
    
    # Parse expected fields
    expected = None
    if args.expected:
        expected = [f.strip() for f in args.expected.split(',')]
    
    try:
        results = verify_fields(
            args.deployment,
            args.environment,
            args.table,
            expected,
            args.poll_interval,
            args.max_wait
        )
        
        print(json.dumps(results, indent=2), flush=True)
        
        # Exit code 0 if all found (or no expected fields specified)
        # Exit code 1 if any missing
        import os
        if not expected or not results.get('missing'):
            os._exit(0)
        else:
            os._exit(1)
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr, flush=True)
        import os
        os._exit(2)


if __name__ == '__main__':
    main()
