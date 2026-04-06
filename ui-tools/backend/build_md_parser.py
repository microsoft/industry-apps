"""
BUILD.md Parser for Batch Field Creation

Parses BUILD.md files to extract table definitions and field specifications
from Planned sections only. Returns data in format compatible with existing
Field Creator endpoint.
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Union


def parse_build_md_tables(
    module_path: Union[str, Path],
    publisher_prefix: str = "appbase_",
    include_all_sections: bool = False
) -> List[Dict[str, Any]]:
    """
    Parse BUILD.md to extract table definitions from Planned sections.
    
    Args:
        module_path: Path to module directory (contains BUILD.md) - can be str or Path
        publisher_prefix: Publisher prefix for generating schema names
        include_all_sections: If True, include Completed and Completed Last Round sections
    
    Returns:
        List of table definitions:
        [
            {
                "tableName": "Time Period",
                "tableDisplayName": "Time Period", 
                "fields": [
                    "Period Code: Text",
                    "Period Type: Choice (Schedule Frequency)",
                    "Person: Lookup (Person)",
                    ...
                ],
                # Only if include_all_sections=True:
                "sections": {
                    "completed": [...],
                    "completedLastRound": [...],
                    "planned": [...]
                }
            },
            ...
        ]
    """
    # Convert to Path if string
    if isinstance(module_path, str):
        module_path = Path(module_path)
    
    build_md_path = module_path / "BUILD.md"
    
    if not build_md_path.exists():
        raise FileNotFoundError(f"BUILD.md not found: {build_md_path}")
    
    with open(build_md_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    tables = []
    
    # Split content by table headers (### Table Name)
    table_pattern = r'^### (.+?)$'
    table_matches = list(re.finditer(table_pattern, content, re.MULTILINE))
    
    for i, match in enumerate(table_matches):
        table_name = match.group(1).strip()
        start_pos = match.end()
        
        # Find end position (next ### or end of file)
        if i + 1 < len(table_matches):
            end_pos = table_matches[i + 1].start()
        else:
            end_pos = len(content)
        
        table_section = content[start_pos:end_pos]
        
        if include_all_sections:
            # Extract all sections
            sections = _extract_all_sections(table_section, table_name)
            
            # Only include tables that have at least one section with fields
            if sections['planned'] or sections['completed'] or sections['completedLastRound']:
                tables.append({
                    "tableName": table_name,
                    "tableDisplayName": table_name,
                    "fields": sections['planned'],  # For backward compatibility
                    "sections": sections
                })
        else:
            # Extract fields from Planned section only
            fields = _extract_planned_fields(table_section, table_name)
            
            if fields:  # Only include tables that have planned fields
                tables.append({
                    "tableName": table_name,
                    "tableDisplayName": table_name,
                    "fields": fields
                })
    
    return tables


def _extract_planned_fields(table_section: str, table_name: str) -> List[str]:
    """
    Extract field definitions from Planned section of a table.
    
    Skips:
    - Completed sections
    - Completed Last Round sections
    - Any content before **Planned:** marker
    
    Args:
        table_section: Content of the table section
        table_name: Name of the table (for context in errors)
    
    Returns:
        List of field definition strings in BUILD.md format
    """
    # Find the **Planned:** section
    # Match from **Planned:** until we hit:
    # - Another ** section (like **Completed Last Round:** or **Notes:**)
    # - A line with --- (horizontal rule)
    # - End of the section
    # IMPORTANT: Don't require \n before ** to handle empty sections correctly
    planned_pattern = r'\*\*Planned:\*\*\s*\n(.*?)(?=---|\*\*|\Z)'
    planned_match = re.search(planned_pattern, table_section, re.DOTALL)
    
    if not planned_match:
        # No Planned section found
        return []
    
    planned_content = planned_match.group(1)
    
    # Extract field lines (lines starting with "- ")
    field_lines = []
    for line in planned_content.split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for field definition format: "- FieldName: Type"
        if line.startswith('-') and ':' in line:
            # Remove leading dash and whitespace
            field_def = line.lstrip('- ').strip()
            
            # Skip non-field lines (configuration notes, etc.)
            if field_def.startswith('Configure') or field_def.startswith('Create'):
                continue
            
            field_lines.append(field_def)
    
    return field_lines


def _extract_all_sections(table_section: str, table_name: str) -> Dict[str, List[str]]:
    """
    Extract field definitions from all sections of a table.
    
    Args:
        table_section: Content of the table section
        table_name: Name of the table (for context)
    
    Returns:
        Dictionary with keys: 'completed', 'completedLastRound', 'planned'
        Each value is a list of field definition strings
    """
    sections = {
        'completed': [],
        'completedLastRound': [],
        'planned': []
    }
    
    # Extract Completed section - match content until we hit the next section header
    # Using \s* in lookahead to handle any whitespace/blank lines before next section
    # Don't require \n before ** to handle empty sections correctly
    completed_pattern = r'\*\*Completed:\*\*\s*\n(.*?)(?=\s*\*\*(?:Completed Last Round|Planned):\*\*|---|\Z)'
    completed_match = re.search(completed_pattern, table_section, re.DOTALL)
    if completed_match:
        sections['completed'] = _extract_field_lines(completed_match.group(1))
    
    # Extract Completed Last Round section 
    # Don't require \n before ** to handle empty sections correctly
    completed_last_pattern = r'\*\*Completed Last Round:\*\*\s*\n(.*?)(?=\s*\*\*Planned:\*\*|---|\Z)'
    completed_last_match = re.search(completed_last_pattern, table_section, re.DOTALL)
    if completed_last_match:
        sections['completedLastRound'] = _extract_field_lines(completed_last_match.group(1))
    
    # Extract Planned section - stop at separator or end of table section
    # Don't require \n before --- or ** to handle empty sections correctly
    planned_pattern = r'\*\*Planned:\*\*\s*\n(.*?)(?=---|\*\*|\Z)'
    planned_match = re.search(planned_pattern, table_section, re.DOTALL)
    if planned_match:
        sections['planned'] = _extract_field_lines(planned_match.group(1))
    
    return sections


def _extract_field_lines(content: str) -> List[str]:
    """
    Extract field lines from section content.
    
    Args:
        content: Section content (text after **SectionName:**)
    
    Returns:
        List of field definition strings
    """
    field_lines = []
    for line in content.split('\n'):
        line = line.strip()
        
        # Skip empty lines and comments
        if not line or line.startswith('#'):
            continue
        
        # Check for field definition format: "- FieldName: Type"
        if line.startswith('-') and ':' in line:
            # Remove leading dash and whitespace
            field_def = line.lstrip('- ').strip()
            
            # Skip non-field lines (configuration notes, etc.)
            if field_def.startswith('Configure') or field_def.startswith('Create'):
                continue
            
            field_lines.append(field_def)
    
    return field_lines


def move_fields_to_completed_last_round(
    module_path: Union[str, Path],
    table_name: str,
    field_names: List[str]
) -> bool:
    """
    Move specified fields from Planned section to Completed Last Round section.
    
    Args:
        module_path: Path to module directory (contains BUILD.md)
        table_name: Name of the table (e.g., "Dispute")
        field_names: List of field display names to move (e.g., ["Case Title", "Case Number"])
    
    Returns:
        True if successful, False otherwise
    """
    import sys
    
    # Convert to Path if string
    if isinstance(module_path, str):
        module_path = Path(module_path)
    
    build_md_path = module_path / "BUILD.md"
    
    if not build_md_path.exists():
        print(f"BUILD.md not found at {build_md_path}", file=sys.stderr)
        return False
    
    try:
        # Read the entire file
        with open(build_md_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Find the table section
        table_pattern = f'^### {re.escape(table_name)}$'
        table_matches = list(re.finditer(table_pattern, content, re.MULTILINE))
        
        if not table_matches:
            print(f"Table {table_name} not found", file=sys.stderr)
            return False
        
        # Get the table section
        table_match = table_matches[0]
        start_pos = table_match.start()
        
        # Find next table (###) or major section (##) or end of file
        next_table_pattern = r'^### '
        next_section_pattern = r'^## '
        
        remaining_content = content[start_pos + len(table_match.group()):]
        next_table_matches = list(re.finditer(next_table_pattern, remaining_content, re.MULTILINE))
        next_section_matches = list(re.finditer(next_section_pattern, remaining_content, re.MULTILINE))
        
        if next_table_matches:
            end_pos = start_pos + len(table_match.group()) + next_table_matches[0].start()
        elif next_section_matches:
            end_pos = start_pos + len(table_match.group()) + next_section_matches[0].start()
        else:
            end_pos = len(content)
        
        table_content = content[start_pos:end_pos]
        
        # Split into lines for easier processing
        lines = table_content.split('\n')
        
        # Find section boundaries
        completed_idx = None
        completed_last_idx = None
        planned_idx = None
        planned_next_idx = None
        
        for i, line in enumerate(lines):
            if line.strip() == '**Completed:**':
                completed_idx = i
            elif line.strip() == '**Completed Last Round:**':
                completed_last_idx = i
            elif line.strip() == '**Planned:**':
                planned_idx = i
            elif line.strip() == '**Planned Next:**':
                planned_next_idx = i
            elif line.startswith('---') and i > 0:
                # This marks the end of the table
                if planned_next_idx is None:
                    planned_next_idx = i
                break
        
        if planned_idx is None:
            print(f"No Planned section found", file=sys.stderr)
            return False
        
        # Extract fields from Planned section
        planned_end = planned_next_idx if planned_next_idx else len(lines)
        planned_fields = []
        remaining_planned_fields = []
        
        for i in range(planned_idx + 1, planned_end):
            line = lines[i]
            stripped = line.strip()
            
            # Check if this is a field line
            if stripped.startswith('-') and ':' in stripped:
                field_def = stripped.lstrip('- ').strip()
                field_display_name = field_def.split(':')[0].strip()
                
                if field_display_name in field_names:
                    planned_fields.append(line)
                else:
                    remaining_planned_fields.append(line)
            elif stripped and not stripped.startswith('**'):
                # Preserve non-field lines (but not section headers)
                remaining_planned_fields.append(line)
        
        if not planned_fields:
            print(f"No fields found to move", file=sys.stderr)
            return False
        
        # Get existing Completed Last Round fields
        completed_last_fields = []
        if completed_last_idx is not None:
            completed_last_end = planned_idx
            for i in range(completed_last_idx + 1, completed_last_end):
                line = lines[i]
                stripped = line.strip()
                if stripped and not stripped.startswith('**'):
                    completed_last_fields.append(line)
        
        # Rebuild the table section
        new_lines = []
        
        # Everything before Completed Last Round
        if completed_last_idx is not None:
            new_lines.extend(lines[:completed_last_idx + 1])
        else:
            # No Completed Last Round section exists, add it before Planned
            new_lines.extend(lines[:planned_idx])
            new_lines.append('**Completed Last Round:**')
            completed_last_idx = len(new_lines) - 1
        
        # Add existing Completed Last Round fields
        new_lines.extend(completed_last_fields)
        
        # Add newly moved fields
        new_lines.extend(planned_fields)
        new_lines.append('')  # Blank line after Completed Last Round
        
        # Add Planned section header
        new_lines.append('**Planned:**')
        
        # Add remaining Planned fields
        new_lines.extend(remaining_planned_fields)
        
        # Add everything after Planned section
        if planned_next_idx:
            new_lines.append('')  # Blank line before Planned Next
            new_lines.extend(lines[planned_next_idx:])
        
        # Reconstruct the table content
        new_table_content = '\n'.join(new_lines)
        
        # Replace in full content
        new_content = content[:start_pos] + new_table_content + content[end_pos:]
        
        # Write back to file
        with open(build_md_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        print(f"✓ Moved {len(planned_fields)} fields to Completed Last Round", file=sys.stderr)
        return True
        
    except Exception as e:
        print(f"Error moving fields: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return False


def generate_schema_name(display_name: str, publisher_prefix: str = "appbase_") -> str:
    """
    Generate schema name from display name following Dataverse conventions.
    
    Args:
        display_name: Field display name (e.g., "HR Request")
        publisher_prefix: Publisher prefix (e.g., "appbase_")
    
    Returns:
        Schema name in PascalCase with prefix (e.g., "appbase_HRRequest")
    """
    if not display_name or not publisher_prefix:
        return ''
    
    # Convert display name to PascalCase without spaces/underscores
    # Preserve acronyms: "HR Request" -> "appbase_HRRequest"
    
    # Remove special chars, keep letters, numbers, spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', display_name)
    words = cleaned.split()
    
    # Build PascalCase: preserve uppercase acronyms, capitalize others  
    pascal_parts = []
    for word in words:
        if not word:
            continue
        # If word is all uppercase (acronym like "HR"), keep it
        if word.isupper():
            pascal_parts.append(word)
        else:
            # Capitalize first letter, lowercase rest
            pascal_parts.append(word.capitalize())
    
    pascal_case = ''.join(pascal_parts)
    return publisher_prefix + pascal_case


def get_available_modules(workspace_root: Path) -> List[Dict[str, str]]:
    """
    Scan workspace for modules with BUILD.md files.
    
    Args:
        workspace_root: Root path of the workspace
    
    Returns:
        List of module info:
        [
            {
                "path": "workforce/time-travel-expenses",
                "displayName": "Time, Travel, and Expenses",
                "category": "workforce"
            },
            ...
        ]
    """
    modules = []
    
    # Common category folders
    categories = [
        'workforce', 'operations', 'compliance-security',
        'external-engagement', 'administrative', 'financial',
        'government', 'shared'
    ]
    
    for category in categories:
        category_path = workspace_root / category
        if not category_path.exists():
            continue
        
        # Find all BUILD.md files in subdirectories
        for build_md in category_path.rglob('BUILD.md'):
            module_path = build_md.parent
            module_name = module_path.name
            relative_path = module_path.relative_to(workspace_root)
            
            # Try to extract display name from BUILD.md title
            display_name = _extract_module_display_name(build_md) or module_name
            
            modules.append({
                'path': str(relative_path).replace('\\', '/'),
                'displayName': display_name,
                'category': category,
                'moduleName': module_name
            })
    
    return sorted(modules, key=lambda m: (m['category'], m['moduleName']))


def _extract_module_display_name(build_md_path: Path) -> str:
    """Extract module display name from BUILD.md title (first # heading)."""
    try:
        with open(build_md_path, 'r', encoding='utf-8') as f:
            for line in f:
                # Match: # Icon Module Name — Description
                if line.startswith('# '):
                    title = line[2:].strip()
                    # Remove emoji/icon and extract name before —
                    if '—' in title:
                        title = title.split('—')[0].strip()
                    # Remove leading emoji
                    title = re.sub(r'^[\U0001F300-\U0001F9FF]\s*', '', title)
                    return title
        return ""
    except Exception:
        return ""
