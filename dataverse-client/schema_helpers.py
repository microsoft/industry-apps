"""
Schema Helpers

Utilities for generating and validating Dataverse schema names.
"""

import re


def generate_schema_name(display_name: str, prefix: str, pascal_case: bool = True) -> str:
    """
    Generate schema name from display name.
    
    Args:
        display_name: Human-readable display name (e.g., "Position Number")
        prefix: Publisher prefix (e.g., "appbase_")
        pascal_case: If True, generates PascalCase (appbase_PositionNumber). 
                     If False, generates lowercase (appbase_positionnumber)
    
    Returns:
        Schema name in PascalCase format (for SchemaName property) or lowercase (for LogicalName)
    
    Examples:
        >>> generate_schema_name("Position Number", "appbase_", pascal_case=True)
        'appbase_PositionNumber'
        >>> generate_schema_name("HR Job Classification", "appbase_", pascal_case=True)
        'appbase_HRJobClassification'
        >>> generate_schema_name("Position Number", "appbase_", pascal_case=False)
        'appbase_positionnumber'
    """
    # Remove special characters, keep letters, numbers, and spaces
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', display_name)
    
    # Ensure prefix ends with underscore
    if prefix and not prefix.endswith('_'):
        prefix += '_'
    
    if pascal_case:
        # Split on whitespace
        words = clean.split()
        pascal_words = []
        
        for word in words:
            if not word:
                continue
            # Preserve acronyms (all uppercase, 2-4 letters like HR, IT, API, etc.)
            if word.isupper() and 2 <= len(word) <= 4:
                pascal_words.append(word)
            else:
                # Regular word: capitalize first letter, lowercase rest
                pascal_words.append(word.capitalize())
        
        pascal = ''.join(pascal_words)
        return f"{prefix}{pascal}"
    else:
        # Lowercase, remove all spaces
        clean = clean.lower().replace(' ', '')
        return f"{prefix}{clean}"


def validate_schema_name(schema_name: str) -> bool:
    """
    Validate that a schema name follows Dataverse naming conventions.
    
    Rules:
    - Must start with a letter
    - Can contain only letters, numbers, and underscores
    - No spaces or special characters
    - Typically includes publisher prefix
    
    Args:
        schema_name: Schema name to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not schema_name:
        return False
    
    # Must start with letter
    if not schema_name[0].isalpha():
        return False
    
    # Only alphanumeric and underscores
    if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', schema_name):
        return False
    
    return True


def extract_publisher_prefix(schema_name: str) -> str:
    """
    Extract publisher prefix from a schema name.
    
    Assumes prefix is everything before the first underscore.
    
    Args:
        schema_name: Full schema name (e.g., "appbase_customername")
    
    Returns:
        Publisher prefix including underscore (e.g., "appbase_"), or empty string if no underscore
    """
    if '_' in schema_name:
        prefix = schema_name.split('_')[0]
        return f"{prefix}_"
    
    return ""
