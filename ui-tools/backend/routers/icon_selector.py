"""
Icon Selector API Router

Provides endpoints for the interactive icon selection tool:
- List modules and entities
- Search icons across libraries (Tabler, Material Design, Lucide)
- Save/load icon selections
- Export final approved_icons.json
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path
import json
import re
from collections import defaultdict

router = APIRouter(prefix="/api/icon-selector", tags=["Icon Selector"])

# Paths
REPO_ROOT = Path(__file__).parent.parent.parent.parent
ICONS_DIR = REPO_ROOT / ".icons"
MERGED_ICONS_CACHE = ICONS_DIR / "merged_icons_cache_clean.json"
ENTITY_INVENTORY = ICONS_DIR / "entity_inventory.json"
ENTITY_CONTEXT = ICONS_DIR / "entities_with_context.json"
SELECTIONS_FILE = ICONS_DIR / "icon_selections.json"

# Request/Response Models
class IconSearchRequest(BaseModel):
    query: str
    sources: Optional[List[str]] = None  # ["tabler", "material-design", "lucide"]
    limit: Optional[int] = 100

class IconSelectionRequest(BaseModel):
    entity_logical_name: str
    icon_name: str
    icon_source: str

class Icon(BaseModel):
    name: str
    display_name: str
    source: str
    category: str
    tags: List[str]
    
class Entity(BaseModel):
    logical_name: str
    display_name: str
    module: str
    current_icon: Optional[str] = None
    description: Optional[str] = None
    has_selection: bool = False
    
class Module(BaseModel):
    name: str
    display_name: str
    entity_count: int
    selected_count: int

# Cache for loaded data
_icons_cache = None
_entities_cache = None
_selections_cache = None

def load_icons() -> List[Dict[str, Any]]:
    """Load icons from merged cache"""
    global _icons_cache
    if _icons_cache is None:
        with open(MERGED_ICONS_CACHE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            _icons_cache = data['icons']
    return _icons_cache

def load_entities() -> Dict[str, Dict[str, Any]]:
    """Load entity inventory with context"""
    global _entities_cache
    if _entities_cache is None:
        # Load base inventory
        with open(ENTITY_INVENTORY, 'r', encoding='utf-8') as f:
            inventory = json.load(f)
        
        # Load context (descriptions)
        context = {}
        if ENTITY_CONTEXT.exists():
            with open(ENTITY_CONTEXT, 'r', encoding='utf-8') as f:
                context = json.load(f)
        
        # Merge
        _entities_cache = {}
        for logical_name, entity_data in inventory.items():
            _entities_cache[logical_name] = {
                **entity_data,
                'description': context.get(logical_name, {}).get('description', '')
            }
    
    return _entities_cache

def load_selections() -> Dict[str, Dict[str, str]]:
    """Load saved icon selections"""
    global _selections_cache
    if _selections_cache is None:
        if SELECTIONS_FILE.exists():
            with open(SELECTIONS_FILE, 'r', encoding='utf-8') as f:
                _selections_cache = json.load(f)
        else:
            _selections_cache = {}
    return _selections_cache

def save_selections(selections: Dict[str, Dict[str, str]]):
    """Save icon selections to file"""
    global _selections_cache
    _selections_cache = selections
    with open(SELECTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(selections, f, indent=2)

def search_icons(query: str, icons: List[Dict], sources: Optional[List[str]] = None, limit: int = 100) -> List[Dict]:
    """Search icons by query with fuzzy matching"""
    query_lower = query.lower().strip()
    
    # Filter by source if specified
    if sources:
        icons = [i for i in icons if i.get('source') in sources]
    
    if not query_lower:
        return icons[:limit]
    
    # Score each icon
    scored_icons = []
    query_words = set(re.findall(r'\b\w+\b', query_lower))
    
    for icon in icons:
        score = 0
        
        # Check name (highest weight)
        icon_name = icon.get('name', '').lower()
        if query_lower in icon_name:
            score += 10
        if query_lower == icon_name:
            score += 20
        
        # Check display name
        display_name = icon.get('display_name', '').lower()
        if query_lower in display_name:
            score += 5
        
        # Check tags
        icon_tags = [t.lower() for t in icon.get('tags', [])]
        for tag in icon_tags:
            if query_lower in tag:
                score += 3
            if query_lower == tag:
                score += 5
        
        # Check word matches
        icon_words = set(re.findall(r'\b\w+\b', f"{icon_name} {' '.join(icon_tags)}"))
        word_matches = query_words.intersection(icon_words)
        score += len(word_matches) * 2
        
        if score > 0:
            scored_icons.append((score, icon))
    
    # Sort by score descending
    scored_icons.sort(key=lambda x: x[0], reverse=True)
    
    return [icon for score, icon in scored_icons[:limit]]

@router.get("/modules")
async def get_modules() -> List[Module]:
    """Get list of all modules with entity counts"""
    entities = load_entities()
    selections = load_selections()
    
    # Group by module
    modules_data = defaultdict(lambda: {'entity_count': 0, 'selected_count': 0})
    
    for logical_name, entity_data in entities.items():
        module = entity_data.get('module_path', entity_data.get('module_name', 'Unknown'))
        modules_data[module]['entity_count'] += 1
        if logical_name in selections:
            modules_data[module]['selected_count'] += 1
    
    # Convert to list
    modules = []
    for module_name, data in sorted(modules_data.items()):
        # Create display name from module path
        display_name = module_name.split('/')[-1].replace('-', ' ').title()
        modules.append(Module(
            name=module_name,
            display_name=display_name,
            entity_count=data['entity_count'],
            selected_count=data['selected_count']
        ))
    
    return modules

@router.get("/modules/{module_name}/entities")
async def get_module_entities(module_name: str) -> List[Entity]:
    """Get all entities for a specific module
    
    Supports both:
    - entity_inventory paths (e.g., "test", "administrative/executive-coordination") 
    - global module paths (e.g., ".temp\\FSG", "government\\court-case-management")
    """
    entities = load_entities()
    selections = load_selections()
    
    # Decode module name (replace URL encoding and normalize slashes)
    module_name = module_name.replace('%2F', '/').replace('%5C', '/').replace('\\', '/')
    
    # Try to find entities by matching module_path or by scanning file system
    module_entities = []
    
    # First, try entity_inventory lookup
    for logical_name, entity_data in entities.items():
        entity_module = entity_data.get('module_path', entity_data.get('module_name', '')).replace('\\', '/')
        if entity_module == module_name:
            module_entities.append(Entity(
                logical_name=logical_name,
                display_name=entity_data.get('display_name', logical_name),
                module=entity_module,
                current_icon=entity_data.get('current_icon'),
                description=entity_data.get('description', ''),
                has_selection=logical_name in selections
            ))
    
    # If no entities found in inventory, try scanning the module path directly
    if not module_entities:
        module_path = REPO_ROOT / module_name.replace('/', '\\')
        entities_dir = module_path / "src" / "Entities"
        
        if entities_dir.exists():
            for entity_dir in entities_dir.iterdir():
                if entity_dir.is_dir():
                    entity_xml = entity_dir / "Entity.xml"
                    if entity_xml.exists():
                        # Parse Entity.xml for basic info
                        try:
                            import xml.etree.ElementTree as ET
                            tree = ET.parse(entity_xml)
                            root = tree.getroot()
                            
                            # Get LogicalName
                            logical_name_elem = root.find('.//Entity/Name/LocalizedName')
                            logical_name = logical_name_elem.get('description') if logical_name_elem is not None else entity_dir.name
                            
                            # Get DisplayName
                            display_name_elem = root.find('.//Entity/DisplayName/LocalizedName')
                            display_name = display_name_elem.get('description') if display_name_elem is not None else logical_name
                            
                            module_entities.append(Entity(
                                logical_name=logical_name,
                                display_name=display_name,
                                module=module_name,
                                current_icon=None,
                                description='',
                                has_selection=logical_name in selections
                            ))
                        except Exception as e:
                            print(f"Error parsing {entity_xml}: {e}")
                            continue
    
    # Sort by display name
    module_entities.sort(key=lambda e: e.display_name)
    
    return module_entities

@router.get("/entities/{logical_name}")
async def get_entity(logical_name: str) -> Dict[str, Any]:
    """Get entity details including current selection"""
    entities = load_entities()
    selections = load_selections()
    
    if logical_name not in entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    entity_data = entities[logical_name]
    selection = selections.get(logical_name, {})
    
    return {
        **entity_data,
        'selection': selection
    }

@router.post("/icons/search")
async def search_icons_endpoint(request: IconSearchRequest) -> List[Icon]:
    """Search icons by query"""
    icons = load_icons()
    results = search_icons(request.query, icons, request.sources, request.limit or 100)
    
    return [
        Icon(
            name=icon['name'],
            display_name=icon.get('display_name', icon['name']),
            source=icon['source'],
            category=icon.get('category', 'General'),
            tags=icon.get('tags', [])
        )
        for icon in results
    ]

@router.get("/icons/{icon_name}/svg")
async def get_icon_svg(icon_name: str, source: str) -> Response:
    """Get SVG content for an icon"""
    icons = load_icons()
    
    # Find the icon
    icon = next((i for i in icons if i['name'] == icon_name and i['source'] == source), None)
    
    if not icon:
        raise HTTPException(status_code=404, detail="Icon not found")
    
    # Get SVG content based on source
    if source == 'tabler':
        # Tabler stores SVG inline
        svg_content = icon.get('svg_content', '')
    elif source == 'material-design':
        # Material Design - need to load from repo
        svg_path = ICONS_DIR / "material-repo" / "svg" / f"{icon_name}.svg"
        if svg_path.exists():
            svg_content = svg_path.read_text(encoding='utf-8')
        else:
            svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text x="12" y="12" text-anchor="middle">{icon_name}</text></svg>'
    elif source == 'lucide':
        # Lucide - need to load from repo
        svg_path = ICONS_DIR / "lucide-repo" / "icons" / f"{icon_name}.svg"
        if svg_path.exists():
            svg_content = svg_path.read_text(encoding='utf-8')
        else:
            svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text x="12" y="12" text-anchor="middle">{icon_name}</text></svg>'
    else:
        svg_content = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><text x="12" y="12" text-anchor="middle">?</text></svg>'
    
    return Response(content=svg_content, media_type="image/svg+xml")

@router.post("/entities/{logical_name}/icon")
async def set_entity_icon(logical_name: str, request: IconSelectionRequest):
    """Set icon for an entity"""
    entities = load_entities()
    
    if logical_name not in entities:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    # Load selections
    selections = load_selections()
    
    # Save selection
    selections[logical_name] = {
        'icon_name': request.icon_name,
        'icon_source': request.icon_source
    }
    
    save_selections(selections)
    
    return {"success": True, "message": f"Icon set for {logical_name}"}

@router.delete("/entities/{logical_name}/icon")
async def clear_entity_icon(logical_name: str):
    """Clear icon selection for an entity"""
    selections = load_selections()
    
    if logical_name in selections:
        del selections[logical_name]
        save_selections(selections)
    
    return {"success": True, "message": f"Icon cleared for {logical_name}"}

@router.get("/progress")
async def get_progress() -> Dict[str, Any]:
    """Get selection progress statistics"""
    entities = load_entities()
    selections = load_selections()
    
    total = len(entities)
    selected = len(selections)
    remaining = total - selected
    percentage = (selected / total * 100) if total > 0 else 0
    
    return {
        'total': total,
        'selected': selected,
        'remaining': remaining,
        'percentage': round(percentage, 1)
    }

@router.get("/selections/all")
async def get_all_selections() -> Dict[str, Any]:
    """Get all icon selections"""
    selections = load_selections()
    return selections

@router.get("/selections/export")
async def export_selections() -> Dict[str, Any]:
    """Export selections in approved_icons.json format"""
    entities = load_entities()
    selections = load_selections()
    
    # Build export format
    approved_icons = {}
    
    for logical_name, selection in selections.items():
        if logical_name in entities:
            entity_data = entities[logical_name]
            approved_icons[logical_name] = {
                'display_name': entity_data.get('display_name', logical_name),
                'icon_name': selection['icon_name'],
                'icon_source': selection['icon_source'],
                'module': entity_data.get('module_path', entity_data.get('module_name', ''))
            }
    
    # Save to file
    export_file = ICONS_DIR / "approved_icons.json"
    with open(export_file, 'w', encoding='utf-8') as f:
        json.dump(approved_icons, f, indent=2)
    
    return {
        'success': True,
        'export_file': str(export_file),
        'count': len(approved_icons)
    }
