#!/usr/bin/env python3
"""
Duplicate Choice Set Checker CLI

Checks for existing similar choice sets in Dataverse to avoid creating duplicates.
Uses direct Dataverse API connection via dataverse-client library.

Usage:
    python cli_check_duplicates.py --choice-names "Event Status,Payment Status" --deployment "CDX FAST" --environment "FAST APPS"
"""

import argparse
import json
import sys
import os
from pathlib import Path
from difflib import SequenceMatcher

# Add dataverse-client directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from client import DataverseClient
from config import load_deployment_config, get_deployment_auth


def calculate_similarity(str1: str, str2: str) -> float:
    """Calculate similarity ratio between two strings (0-100)"""
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio() * 100


def check_duplicates(choice_names: list[str], deployment: str, environment: str) -> dict:
    """
    Check for duplicate choice sets.
    
    Returns:
        {
            "choiceName": {
                "exists": bool,
                "matches": [{"schemaName": "...", "displayName": "...", "similarity": 85}]
            }
        }
    """
    # Load configuration
    try:
        config = load_deployment_config()
        deployments = config.get("Deployments", {})
        
        auth = get_deployment_auth(deployments, deployment, environment)
    except Exception as e:
        error_msg = f"Configuration error: {str(e)}"
        print(f"✗ Fatal error: {error_msg}", flush=True)
        return {name: {"exists": False, "matches": [], "error": error_msg} for name in choice_names}
    
    # Initialize Dataverse client
    try:
        client = DataverseClient(
            environment_url=auth['environment_url'],
            tenant_id=auth['tenant_id'],
            client_id=auth['client_id'],
            client_secret=auth['client_secret']
        )
        client.authenticate()
        print("✓ Connected to Dataverse", flush=True)
    except Exception as e:
        error_msg = f"Failed to connect to Dataverse: {str(e)}"
        print(f"✗ Fatal error: {error_msg}", flush=True)
        return {name: {"exists": False, "matches": [], "error": error_msg} for name in choice_names}
    
    # Get all global option sets
    try:
        all_optionsets = client.get_global_optionset_definitions()
        print(f"Retrieved {len(all_optionsets)} global option sets", flush=True)
    except Exception as e:
        error_msg = f"Failed to retrieve global option sets: {str(e)}"
        print(f"✗ Fatal error: {json.dumps(error_msg)}", flush=True)
        return {name: {"exists": False, "matches": [], "error": error_msg} for name in choice_names}
    
    results = {}
    
    for choice_name in choice_names:
        matches = []
        
        # Check for exact or similar matches
        for optionset in all_optionsets:
            schema_name = optionset['schemaName']
            display_name = optionset['displayName']
            
            # Check for exact match on display name
            if choice_name.lower() == display_name.lower():
                matches.append({
                    'schemaName': schema_name,
                    'displayName': display_name,
                    'similarity': 100,
                    'reason': 'Exact display name match'
                })
                continue
            
            # Calculate similarity
            similarity = calculate_similarity(choice_name, display_name)
            
            if similarity > 70:
                matches.append({
                    'schemaName': schema_name,
                    'displayName': display_name,
                    'similarity': int(similarity),
                    'reason': f'Display name similarity ({int(similarity)}%)'
                })
        
        # Sort matches by similarity (highest first)
        matches.sort(key=lambda m: m['similarity'], reverse=True)
        
        results[choice_name] = {
            'exists': len(matches) > 0,
            'matches': matches
        }
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Check for duplicate choice sets in Dataverse'
    )
    parser.add_argument(
        '--choice-names',
        required=True,
        help='Comma-separated list of choice set names to check'
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
    
    args = parser.parse_args()
    
    choice_names = [name.strip() for name in args.choice_names.split(',')]
    
    try:
        results = check_duplicates(choice_names, args.deployment, args.environment)
        print(json.dumps(results, indent=2), flush=True)
        
        # Exit code 0 always (duplicates are informational, not errors)
        # Force immediate exit to avoid MSAL cleanup hang
        os._exit(0)
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr, flush=True)
        os._exit(2)


if __name__ == '__main__':
    main()
