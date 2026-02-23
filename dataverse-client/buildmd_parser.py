"""
BUILD.md Parser

Extracts entity field definitions and choice field definitions from BUILD.md files.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional


def parse_field_line(line: str) -> Optional[Dict]:
    """
    Parse a field definition line from BUILD.md.
    
    Formats supported:
    - Name: Text
    - Name: Text, Required
    - Name: Text, Required, Max Length: 200
    - Name: Choice (schema_name)
    - Name: Lookup (targettable)
    
    Args:
        line: Single line from BUILD.md entity section
    
    Returns:
        Dictionary with field definition, or None if not a valid field line
    """
    # Remove leading bullet/dash
    line = re.sub(r'^[-•]\s*', '', line).strip()
    
    # Must have colon separator
    if ': ' not in line:
        return None
    
    colon_idx = line.index(': ')
    display_name = line[:colon_idx].strip()
    type_info = line[colon_idx + 2:].strip()
    
    # Remove trailing " ok" markers
    type_info = re.sub(r'\s+ok\s*$', '', type_info)
    
    field_def = {
        'displayName': display_name,
        'type': '',
        'required': False,
        'maxLength': None,
        'optionSetSchemaName': None,
        'targetTableLogicalName': None
    }
    
    # Check for "Required" flag
    if re.search(r',\s*Required', type_info, re.IGNORECASE):
        field_def['required'] = True
        type_info = re.sub(r',\s*Required', '', type_info, flags=re.IGNORECASE).strip()
    
    # Check for "Max Length: X"
    max_length_match = re.search(r',\s*Max Length:\s*(\d+)', type_info, re.IGNORECASE)
    if max_length_match:
        field_def['maxLength'] = int(max_length_match.group(1))
        type_info = re.sub(r',\s*Max Length:\s*\d+', '', type_info, flags=re.IGNORECASE).strip()
    
    # Extract type and handle parentheses (Choice/Lookup)
    if '(' in type_info:
        paren_idx = type_info.index('(')
        field_type = type_info[:paren_idx].strip()
        paren_content = type_info[paren_idx + 1:type_info.rindex(')')].strip()
        
        field_def['type'] = field_type
        
        if field_type.lower() == 'choice':
            field_def['optionSetSchemaName'] = paren_content
        elif field_type.lower() == 'lookup':
            field_def['targetTableLogicalName'] = paren_content
    else:
        field_def['type'] = type_info
    
    return field_def


def parse_buildmd(file_path: Path, entity_filter: Optional[str] = None, choice_filter: Optional[str] = None) -> Dict:
    """
    Parse a BUILD.md file and extract entity definitions and choice fields.
    
    Args:
        file_path: Path to BUILD.md file
        entity_filter: Optional entity name to extract (case-insensitive)
        choice_filter: Optional choice set name to extract (case-insensitive)
    
    Returns:
        {
            "entities": [
                {
                    "name": "Entity Name",
                    "fields": [{"displayName": "...", "type": "...", ...}]
                }
            ],
            "choiceSets": [
                {
                    "name": "Choice Set Name",
                    "description": "Optional description",
                    "values": ["Value 1", "Value 2"]
                }
            ]
        }
    """
    content = file_path.read_text(encoding='utf-8')
    
    result = {
        'entities': [],
        'choiceSets': []
    }
    
    # Parse entity sections (### Entity Name)
    entity_pattern = r'### ([^\n]+)\n([\s\S]*?)(?=###|##|\Z)'
    entity_matches = re.finditer(entity_pattern, content)
    
    for match in entity_matches:
        entity_name = match.group(1).strip()
        entity_content = match.group(2)
        
        # Skip if filtering and name doesn't match
        if entity_filter and entity_name.lower() != entity_filter.lower():
            continue
        
        # Find "Planned:" section
        planned_match = re.search(r'\*\*Planned:\*\*\s*\n([\s\S]*?)(?=\*\*|###|##|\Z)', entity_content)
        
        if not planned_match:
            continue
        
        planned_content = planned_match.group(1)
        
        # Extract field lines (start with - or •)
        field_lines = re.findall(r'^[-•]\s*(.+)$', planned_content, re.MULTILINE)
        
        fields = []
        for line in field_lines:
            field_def = parse_field_line(line)
            if field_def:
                fields.append(field_def)
        
        if fields:
            result['entities'].append({
                'name': entity_name,
                'fields': fields
            })
    
    # Parse choice fields section (## ✅ New Choice Fields or ## Choice Fields)
    choice_section_pattern = r'##\s+[✅]?\s*(?:New\s+)?Choice Fields[^\n]*\n([\s\S]+)(?:\Z|##[^#])'
    choice_section_match = re.search(choice_section_pattern, content)
    
    if choice_section_match:
        choice_content = choice_section_match.group(1)
        
        # Find "Planned:" section within choice fields
        planned_match = re.search(r'\*\*Planned:\*\*\s*\n([\s\S]*?)(?=\*\*Completed|\Z)', choice_content)
        
        if planned_match:
            planned_content = planned_match.group(1)
        else:
            # Fallback: if no Planned section, treat entire content as planned
            planned_content = choice_content
        
        # Extract individual choice sets (### Choice Set Name)
        choice_pattern = r'### ([^\n]+)\n([\s\S]*?)(?=###|\Z)'
        choice_matches = re.finditer(choice_pattern, planned_content)
        
        for match in choice_matches:
            choice_name = match.group(1).strip()
            choice_body = match.group(2).strip()
            
            # Skip if filtering and name doesn't match
            if choice_filter and choice_name.lower() != choice_filter.lower():
                continue
            
            # First line might be a description (not starting with -)
            lines = choice_body.split('\n')
            description = ''
            values = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if re.match(r'^[-•]', line):
                    # This is a value
                    value = re.sub(r'^[-•]\s*', '', line).strip()
                    values.append(value)
                elif not values and not description:
                    # First non-bullet line is description
                    description = line
            
            if values:
                result['choiceSets'].append({
                    'name': choice_name,
                    'description': description,
                    'values': values
                })
    
    return result
