#!/usr/bin/env python3
"""
BUILD.md Updater CLI

Moves successfully created fields or choice sets from "Planned:" to "Completed:" section in BUILD.md.

Usage:
    python cli_update_buildmd.py --file BUILD.md --entity "Event" --fields "Name,Event Code"
    python cli_update_buildmd.py --file BUILD.md --choice "Event Status"
"""

import argparse
import json
import sys
from pathlib import Path

# Import from shared dataverse-client library
sys.path.insert(0, str(Path(__file__).parent.parent / 'dataverse-client'))
from buildmd_updater import update_buildmd, update_choice_buildmd


def main():
    parser = argparse.ArgumentParser(
        description='Update BUILD.md by moving fields or choices from Planned to Completed'
    )
    parser.add_argument(
        '--file',
        required=True,
        type=Path,
        help='Path to BUILD.md file'
    )
    parser.add_argument(
        '--entity',
        help='Entity name (e.g., "Event")'
    )
    parser.add_argument(
        '--fields',
        help='Comma-separated list of field names to move (required with --entity)'
    )
    parser.add_argument(
        '--choice',
        help='Choice set name to move (e.g., "Event Status")'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show changes without writing to file'
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(json.dumps({'error': f'File not found: {args.file}'}), file=sys.stderr)
        sys.exit(1)
    
    # Must specify either entity+fields OR choice
    if not args.choice and not (args.entity and args.fields):
        print(json.dumps({'error': 'Must specify either --choice or (--entity and --fields)'}), file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.choice:
            updated_content, diff = update_choice_buildmd(args.file, args.choice)
        else:
            field_names = [name.strip() for name in args.fields.split(',')]
            updated_content, diff = update_buildmd(args.file, args.entity, field_names)
        
        print(diff, file=sys.stderr)
        
        if not args.dry_run:
            args.file.write_text(updated_content, encoding='utf-8')
            print(f"\n✓ Updated {args.file}", file=sys.stderr)
        else:
            print("\n(Dry run - no changes written)", file=sys.stderr)
        
        print(json.dumps({
            'success': True,
            'diff': diff
        }))
        
    except Exception as e:
        print(json.dumps({'error': str(e)}), file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
