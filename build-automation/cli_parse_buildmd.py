#!/usr/bin/env python3
"""
BUILD.md Parser CLI

Extracts entity field definitions and choice field definitions from BUILD.md files.
Outputs structured JSON for processing by the Power Platform Agent.

Usage:
    python cli_parse_buildmd.py --file path/to/BUILD.md [--entity EntityName] [--choice ChoiceName]
"""

import argparse
import json
import sys
from pathlib import Path

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from buildmd_parser import parse_buildmd


def main():
    parser = argparse.ArgumentParser(
        description='Parse BUILD.md files to extract entity fields and choice definitions'
    )
    parser.add_argument(
        '--file',
        required=True,
        type=Path,
        help='Path to BUILD.md file'
    )
    parser.add_argument(
        '--entity',
        type=str,
        help='Extract only this specific entity (optional)'
    )
    parser.add_argument(
        '--choice',
        type=str,
        help='Extract only this specific choice set (optional)'
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(json.dumps({'error': f'File not found: {args.file}'}), file=sys.stderr)
        sys.exit(1)
    
    try:
        # Use shared library function with filters
        result = parse_buildmd(args.file, entity_filter=args.entity, choice_filter=args.choice)
        
        # Check if filters found anything
        if args.entity and not result['entities']:
            print(json.dumps({'error': f'Entity "{args.entity}" not found in BUILD.md'}), file=sys.stderr)
            sys.exit(1)
        
        if args.choice and not result['choiceSets']:
            print(json.dumps({'error': f'Choice set "{args.choice}" not found in BUILD.md'}), file=sys.stderr)
            sys.exit(1)
        
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
