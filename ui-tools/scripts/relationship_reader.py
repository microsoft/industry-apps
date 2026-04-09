"""
Read and parse entity relationship information from Dataverse solution files.

This module extracts 1:N (One-to-Many) relationships where an entity is the parent (referenced entity),
and finds the default views for displaying related records in subgrids.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class OneToManyRelationship:
    """Represents a 1:N relationship where this entity is the referenced (parent) entity."""
    name: str  # Relationship schema name (e.g., "appbase_widget_Sample_appbase_sample")
    target_entity: str  # The related entity (e.g., "appbase_Widget")
    referencing_attribute: str  # The lookup field on the related entity
    default_view_id: Optional[str] = None  # GUID of default view for this entity
    default_view_name: Optional[str] = None  # Name of the default view


def read_relationships(relationships_xml_path: Path, entity_name: str) -> List[OneToManyRelationship]:
    """
    Read 1:N relationships where the entity is the referenced (parent) entity.
    
    Args:
        relationships_xml_path: Path to the entity's relationships XML file
                               (e.g., .../Other/Relationships/appbase_Sample.xml)
        entity_name: Logical name of the entity (e.g., "appbase_Sample")
        
    Returns:
        List of OneToManyRelationship objects
    """
    if not relationships_xml_path.exists():
        return []
    
    relationships = []
    
    try:
        tree = ET.parse(relationships_xml_path)
        root = tree.getroot()
        
        # Find all EntityRelationship elements
        for rel_elem in root.findall(".//{*}EntityRelationship"):
            # Check if this is a OneToMany relationship
            rel_type = rel_elem.find(".//{*}EntityRelationshipType")
            if rel_type is None or rel_type.text != "OneToMany":
                continue
            
            # Check if this entity is the referenced (parent) entity
            referenced_entity = rel_elem.find(".//{*}ReferencedEntityName")
            if referenced_entity is None or referenced_entity.text != entity_name:
                continue
            
            # Extract relationship details
            name_elem = rel_elem.get("Name")
            referencing_entity_elem = rel_elem.find(".//{*}ReferencingEntityName")
            referencing_attribute_elem = rel_elem.find(".//{*}ReferencingAttributeName")
            
            if not name_elem or referencing_entity_elem is None or referencing_attribute_elem is None:
                continue
            
            relationship = OneToManyRelationship(
                name=name_elem,
                target_entity=referencing_entity_elem.text,
                referencing_attribute=referencing_attribute_elem.text
            )
            
            relationships.append(relationship)
    
    except ET.ParseError as e:
        print(f"Warning: Could not parse relationships XML: {e}")
        return []
    
    return relationships


def find_default_view(entity_saved_queries_path: Path) -> Optional[tuple[str, str]]:
    """
    Find the default view for an entity to use in subgrids.
    
    Prefers:
    1. Associated View (querytype=2) with isdefault=1
    2. Main view (querytype=0) with isdefault=1
    3. First Associated View found
    4. First Main view found
    
    Args:
        entity_saved_queries_path: Path to the entity's SavedQueries directory
                                   (e.g., .../Entities/appbase_Widget/SavedQueries/)
    
    Returns:
        Tuple of (view_id, view_name) or None if no views found
    """
    if not entity_saved_queries_path.exists():
        return None
    
    # Scan all view XML files
    view_files = list(entity_saved_queries_path.glob("*.xml"))
    if not view_files:
        return None
    
    # Track views by priority
    associated_default = None
    main_default = None
    first_associated = None
    first_main = None
    
    for view_file in view_files:
        try:
            tree = ET.parse(view_file)
            root = tree.getroot()
            
            # Extract view details
            saved_query = root.find(".//{*}savedquery")
            if saved_query is None:
                continue
            
            view_id_elem = saved_query.find(".//{*}savedqueryid")
            view_name_elem = saved_query.find(".//{*}LocalizedName")
            query_type_elem = saved_query.find(".//{*}querytype")
            is_default_elem = saved_query.find(".//{*}isdefault")
            
            if view_id_elem is None or view_name_elem is None:
                continue
            
            view_id = view_id_elem.text
            view_name = view_name_elem.get("description", "Unknown View")
            query_type = query_type_elem.text if query_type_elem is not None else "0"
            is_default = is_default_elem.text == "1" if is_default_elem is not None else False
            
            # Categorize the view
            if query_type == "2":  # Associated View
                if is_default and associated_default is None:
                    associated_default = (view_id, view_name)
                elif first_associated is None:
                    first_associated = (view_id, view_name)
            elif query_type == "0":  # Main view
                if is_default and main_default is None:
                    main_default = (view_id, view_name)
                elif first_main is None:
                    first_main = (view_id, view_name)
        
        except ET.ParseError:
            continue
    
    # Return in priority order
    return associated_default or main_default or first_associated or first_main


def get_relationships_with_views(module_path: Path, entity_name: str) -> List[OneToManyRelationship]:
    """
    Get all 1:N relationships for an entity with default view information populated.
    
    Args:
        module_path: Path to the module root (e.g., .../test/Test/)
        entity_name: Logical name of the entity (e.g., "appbase_Sample")
        
    Returns:
        List of OneToManyRelationship objects with view information
    """
    # Read relationships
    relationships_xml = module_path / "src" / "Other" / "Relationships" / f"{entity_name}.xml"
    relationships = read_relationships(relationships_xml, entity_name)
    
    # For each relationship, find the default view for the target entity
    for rel in relationships:
        saved_queries_path = module_path / "src" / "Entities" / rel.target_entity / "SavedQueries"
        view_info = find_default_view(saved_queries_path)
        
        if view_info:
            rel.default_view_id, rel.default_view_name = view_info
    
    return relationships
