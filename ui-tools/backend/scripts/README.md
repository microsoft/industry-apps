# Icon Assignment Scripts

This folder contains Python scripts used by the Icon Selector tool to apply icon assignments to Dataverse entities.

## Scripts

### process_icon_approvals.py
Validates icon selections exported from the Icon Selector and prepares them for application.

**Input:** `.icons/approved_icons.json` (from Icon Selector export)  
**Output:** `.icons/approved_icons_validated.json` (with SVG content and paths)

**What it does:**
- Loads approved selections from Icon Selector
- Validates entity and icon existence
- Fetches SVG content from merged icon cache
- Resolves module paths and Entity.xml locations
- Generates WebResource names (`appbase_<entity>icon`)

### create_icon_webresources.py
Creates WebResource files and updates XML files to apply icons to entities.

**Input:** `.icons/approved_icons_validated.json`  
**Output:** WebResource files + XML updates in module folders

**What it does:**
1. Creates `.data.xml` files (WebResource metadata)
2. Creates SVG content files (icon artwork)
3. Updates `Entity.xml` with `<IconVectorName>`
4. Updates `Solution.xml` with `<RootComponent type="61">`

## Data Files Location

Data files remain in the `.icons/` folder at repo root:
- `merged_icons_cache_clean.json` - 14,189 icons from Tabler, Material, Lucide
- `entity_inventory.json` - Entity metadata for all 378 entities
- `approved_icons.json` - Exported selections from Icon Selector
- `approved_icons_validated.json` - Validated selections ready for application

## Usage

### From Icon Selector UI (Recommended)
1. Select icons in Icon Selector
2. Click **"⚙️ Apply to Module"** button
3. Scripts run automatically via FastAPI backend

### From Command Line
```powershell
cd ui-tools/backend/scripts

# Process specific module
python process_icon_approvals.py --module operations/asset-management
python create_icon_webresources.py --module operations/asset-management

# Or all modules
python process_icon_approvals.py
python create_icon_webresources.py
```

## Architecture

```
industry-apps/
├── .icons/                          # Data files (not in ui-tools)
│   ├── merged_icons_cache_clean.json
│   ├── entity_inventory.json
│   └── approved_icons.json
│
├── ui-tools/
│   ├── backend/
│   │   ├── scripts/                 # Python scripts
│   │   │   ├── process_icon_approvals.py
│   │   │   └── create_icon_webresources.py
│   │   └── routers/
│   │       └── icon_selector.py     # API calls these scripts
│   └── frontend/
│       └── src/routes/
│           └── IconSelector.svelte   # UI
│
└── operations/asset-management/      # Module (example)
    └── src/
        ├── Entities/
        │   └── appbase_Asset/
        │       └── Entity.xml        # Updated with IconVectorName
        ├── Other/
        │   └── Solution.xml          # Updated with RootComponent
        └── WebResources/
            ├── appbase_asseticon.data.xml
            └── appbase_asseticon     # SVG content
```

## Path Resolution

Scripts use relative paths to find data:
```python
script_dir = Path(__file__).parent
repo_root = script_dir.parent.parent.parent  # ui-tools/backend/scripts -> repo root
icons_dir = repo_root / '.icons'
```

This allows scripts to:
- Run from Icon Selector UI (subprocess)
- Run from command line in any directory
- Access `.icons/` data files at repo root
- Write to module folders throughout the repo
