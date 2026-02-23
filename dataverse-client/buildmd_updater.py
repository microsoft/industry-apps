"""
BUILD.md Updater

Moves successfully created fields and choice sets from "Planned:" to "Completed:" sections.
"""

import re
from pathlib import Path
from typing import Tuple, List


def update_choice_buildmd(file_path: Path, choice_name: str) -> Tuple[str, str]:
    """
    Move choice set from Planned to Completed section in choice fields area.
    
    Args:
        file_path: Path to BUILD.md file
        choice_name: Name of the choice set to move
    
    Returns:
        Tuple of (updated_content, diff_summary)
        
    Raises:
        ValueError: If sections or choice set not found
    """
    content = file_path.read_text(encoding='utf-8')
    
    # Find the choice fields section
    choice_pattern = r'(##\s+[✅]?\s*(?:New\s+)?Choice Fields[^\n]*\n)([\s\S]+?)(?=\n##(?!#)|\Z)'
    choice_match = re.search(choice_pattern, content)
    
    if not choice_match:
        raise ValueError("Choice Fields section not found in BUILD.md")
    
    section_header = choice_match.group(1)
    section_content = choice_match.group(2)
    
    # Find Completed and Planned sections
    completed_match = re.search(r'(\*\*Completed:\*\*\s*\n)([\s\S]*?)(?=\*\*Planned|\Z)', section_content)
    planned_match = re.search(r'(\*\*Planned:\*\*\s*\n)([\s\S]*)', section_content)
    
    if not planned_match:
        raise ValueError("Planned section not found in Choice Fields")
    
    planned_header = planned_match.group(1)
    planned_content = planned_match.group(2).strip()
    
    # Find the specific choice set in planned content
    choice_set_pattern = rf'(### {re.escape(choice_name)}\s*\n(?:- [^\n]+\n)+\s*)'
    choice_set_match = re.search(choice_set_pattern, planned_content, re.MULTILINE)
    
    if not choice_set_match:
        raise ValueError(f"Choice set '{choice_name}' not found in Planned section")
    
    choice_set_text = choice_set_match.group(0).rstrip()
    
    # Remove from planned
    new_planned = planned_content.replace(choice_set_text, '').strip()
    
    # Add to completed (just the name as a bullet)
    if completed_match:
        completed_header = completed_match.group(1)
        completed_content = completed_match.group(2).strip()
        if completed_content:
            new_completed = f"{completed_content}\n- {choice_name}\n"
        else:
            new_completed = f"- {choice_name}\n"
    else:
        # No completed section yet, create it
        completed_header = "**Completed:**\n"
        new_completed = f"- {choice_name}\n"
    
    # Reconstruct section
    new_section_content = f"{completed_header}{new_completed}\n{planned_header}{new_planned}\n"
    
    # Replace in full content
    new_full_content = content.replace(
        choice_match.group(0),
        section_header + new_section_content
    )
    
    diff = f"Moved choice set '{choice_name}' from Planned to Completed\n"
    
    return new_full_content, diff


def update_buildmd(file_path: Path, entity_name: str, field_names: List[str]) -> Tuple[str, str]:
    """
    Move fields from Planned to Completed section for an entity.
    
    Args:
        file_path: Path to BUILD.md file
        entity_name: Name of the entity
        field_names: List of field display names to move
    
    Returns:
        Tuple of (updated_content, diff_summary)
        
    Raises:
        ValueError: If entity or sections not found
    """
    content = file_path.read_text(encoding='utf-8')
    
    # Find the entity section
    entity_pattern = rf'(### {re.escape(entity_name)}\s*\n)([\s\S]*?)(?=###|##|\Z)'
    entity_match = re.search(entity_pattern, content)
    
    if not entity_match:
        raise ValueError(f"Entity '{entity_name}' not found in BUILD.md")
    
    entity_start = entity_match.group(1)
    entity_content = entity_match.group(2)
    
    # Find Completed and Planned sections
    completed_match = re.search(r'(\*\*Completed:\*\*\s*\n)([\s\S]*?)(?=\*\*Planned|\Z)', entity_content)
    planned_match = re.search(r'(\*\*Planned:\*\*\s*\n)([\s\S]*?)(?=\*\*|###|##|\Z)', entity_content)
    
    if not completed_match or not planned_match:
        raise ValueError(f"Could not find Completed/Planned sections for entity '{entity_name}'")
    
    completed_header = completed_match.group(1)
    completed_content = completed_match.group(2).strip()
    planned_header = planned_match.group(1)
    planned_content = planned_match.group(2).strip()
    
    # Extract field lines from planned
    planned_lines = [line for line in planned_content.split('\n') if line.strip()]
    
    # Find and move matching fields
    fields_to_move = []
    remaining_planned = []
    
    for line in planned_lines:
        # Extract field display name from line
        field_match = re.match(r'^[-•]\s*(.+?)(?::|$)', line)
        if field_match:
            field_display = field_match.group(1).strip()
            # Check if this field should be moved
            if any(fname.lower() in field_display.lower() for fname in field_names):
                fields_to_move.append(line)
            else:
                remaining_planned.append(line)
        else:
            remaining_planned.append(line)
    
    if not fields_to_move:
        return content, "No matching fields found"
    
    # Build updated sections
    new_completed = completed_content
    if new_completed and not new_completed.endswith('\n'):
        new_completed += '\n'
    if new_completed:
        new_completed += '\n'.join(fields_to_move)
    else:
        new_completed = '\n'.join(fields_to_move)
    
    new_planned = '\n'.join(remaining_planned) if remaining_planned else ''
    
    # Reconstruct entity section
    new_entity_content = f"{completed_header}{new_completed}\n\n{planned_header}{new_planned}\n"
    
    # Replace in full content
    new_full_content = content.replace(
        entity_match.group(0),
        entity_start + new_entity_content
    )
    
    # Generate diff summary
    diff = f"Moved {len(fields_to_move)} field(s) from Planned to Completed:\n"
    for field in fields_to_move:
        diff += f"  {field}\n"
    
    return new_full_content, diff
