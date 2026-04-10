"""
Form Builder Service - Business logic for form building operations.

This module contains the validation and helper functions for building forms.
"""

import sys


def validate_yaml_field_references(yaml_content: str, config: dict) -> list[str]:
    """
    Validate that all field references in the YAML tabs/sections exist in the
    'Available Custom Fields' comment section at the top of the file.
    Also validates that all relationship references in subgrids exist in the
    'Available Relationships' comment section.
    
    Returns a list of error messages for invalid field references.
    """
    errors = []
    
    # Extract available field names from YAML comments
    available_fields = set()
    available_relationships = set()
    lines = yaml_content.split('\n')
    in_fields_section = False
    in_relationships_section = False
    
    for line in lines:
        # Look for the Available Custom Fields section
        if '# Available Custom Fields' in line:
            in_fields_section = True
            in_relationships_section = False
            continue
        
        # Look for the Available Relationships section
        if '# Available Relationships' in line:
            in_fields_section = False
            in_relationships_section = True
            continue
        
        # Stop parsing when we hit the tabs section (actual YAML content we care about)
        if line.strip().startswith('tabs:'):
            in_fields_section = False
            in_relationships_section = False
            break
        
        # Extract field names from comment lines like "#   - appbase_fieldname (...)"
        if in_fields_section and line.strip().startswith('#   - '):
            # Parse field name (between "- " and first space or parenthesis)
            field_line = line.strip()[5:]  # Remove "#   - "
            if '(' in field_line:
                field_name = field_line.split('(')[0].strip()
            else:
                field_name = field_line.split()[0].strip()
            available_fields.add(field_name)
        
        # Extract relationship names from comment lines like "# - relationship_name"
        if in_relationships_section and line.strip().startswith('# - '):
            # Parse relationship name
            rel_line = line.strip()[4:]  # Remove "# - "
            relationship_name = rel_line.split()[0].strip()
            available_relationships.add(relationship_name)
    
    # Add system fields that are always available
    available_fields.add('ownerid')
    
    # Add entity name field (e.g., appbase_name for appbase_* entities)
    entity_name = config.get('entity', '')
    if '_' in entity_name:
        entity_prefix = entity_name.split('_')[0]
        available_fields.add(f"{entity_prefix}_name")
    
    # Collect all field references from tabs
    referenced_fields = set()
    referenced_relationships = set()
    
    for tab in config.get('tabs', []):
        for section in tab.get('sections', []):
            # Check fields in rows mode
            if 'rows' in section:
                for row_spec in section['rows']:
                    for cell_spec in row_spec:
                        if isinstance(cell_spec, str):
                            # Simple field name
                            referenced_fields.add(cell_spec)
                        elif isinstance(cell_spec, dict):
                            # Field with attributes like colspan
                            if 'field' in cell_spec:
                                referenced_fields.add(cell_spec['field'])
            
            # Check fields in fields mode
            if 'fields' in section:
                for field_name in section['fields']:
                    referenced_fields.add(field_name)
            
            # Check relationships in subgrids
            if 'subgrids' in section:
                for subgrid_spec in section['subgrids']:
                    if 'relationship' in subgrid_spec:
                        referenced_relationships.add(subgrid_spec['relationship'])
    
    print(f"\nTotal referenced fields: {len(referenced_fields)}", file=sys.stderr)
    print(f"Referenced fields: {sorted(referenced_fields)}", file=sys.stderr)
    
    # Validate each referenced field exists in available fields
    for field_name in sorted(referenced_fields):
        # Skip null/None placeholders
        if field_name is None or field_name == 'null':
            continue
        
        # Check if field exists in available fields
        if field_name not in available_fields:
            errors.append(f"Field '{field_name}' not found in Available Custom Fields list")
    
    # Validate each referenced relationship exists in available relationships
    for rel_name in sorted(referenced_relationships):
        if rel_name not in available_relationships:
            errors.append(f"Relationship '{rel_name}' not found in Available Relationships list")
    
    return errors
