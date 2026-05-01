# Icon Assignment System

This folder contains scripts and tools for assigning icons to Dataverse entities using Tabler Icons, Material Design Icons, and Lucide icons.

## Overview

The system provides two workflows:
1. **Automated matching** - Tag-based scoring for initial suggestions
2. **Manual selection** - Interactive Icon Selector web tool for curated assignments

Icons are applied as WebResources and linked via Entity.xml IconVectorName references.

## Quick Start - Manual Selection (Recommended)

### 1. Start the Icon Selector Tool
```powershell
# Start backend and frontend servers
cd ui-tools
.\Start-UITools.ps1
```

### 2. Select Icons
- Open http://localhost:5173/#/icon-selector
- Select a module from the dropdown
- Browse entities and search for icons
- Click icons to preview, then "Confirm Selection"
- Track progress in the top bar

### 3A. Apply from UI (Recommended for Quick Testing)
- Click **"⚙️ Apply to Module"** button in the top bar
- Confirms and runs both scripts for just that module
- Shows results (WebResources created, files updated)
- Review changes with `git diff <module-path>`

### 3B. Apply from Command Line (For Advanced Control)
```powershell
# Scripts are in ui-tools/backend/scripts/
cd ui-tools/backend/scripts

# In the Icon Selector, click "Export" button
# This saves .icons/approved_icons.json

# Option A: Process ALL modules
python process_icon_approvals.py
python create_icon_webresources.py

# Option B: Process ONE module at a time (recommended for testing)
python process_icon_approvals.py --module operations/asset-management
python create_icon_webresources.py --module operations/asset-management

# Skip confirmation prompt (use with caution)
python create_icon_webresources.py --module operations/asset-management -y
```

### 4. Review Changes
```powershell
git diff  # Review Entity.xml, Solution.xml, and WebResource files
git diff operations/asset-management  # Review just one module
```

### 5. Test Import (Per Module)
```powershell
# Build the solution for the specific module
cd operations/asset-management
msbuild /t:Rebuild

# Import to test environment
pac solution import --path bin/Release/YourSolution.zip

# Verify icons appear in Power Platform
```

## Icon Libraries

The system uses three MIT/Apache-licensed icon libraries:
- **Tabler Icons**: 5,039 icons (MIT License)
- **Material Design Icons**: 7,447 icons (Apache 2.0 License)
- **Lucide Icons**: 1,703 icons (ISC License)

**Total: 14,189 icons**

## Files Generated

**Input:**
- `merged_icons_cache_clean.json` - Combined library (14,189 icons)
- `entity_inventory.json` - All entities across modules
- `entities_with_context.json` - Entities with descriptions

**Output from Icon Selector:**
- `icon_selections.json` - Work-in-progress selections
- `approved_icons.json` - Exported final selections

**Output from Scripts:**
- `approved_icons_validated.json` - Validated with SVG content
- WebResource files in `<module>/src/WebResources/`
- Updated `Entity.xml` files with IconVectorName
- Updated `Solution.xml` files with RootComponents

## Script Reference

**Location:** `ui-tools/backend/scripts/`

### process_icon_approvals.py
Validates icon selections exported from Icon Selector and prepares them for application.

**Input:** `approved_icons.json` (from Icon Selector export)
**Output:** `approved_icons_validated.json` (with SVG content and paths)

**What it does:**
- Loads approved selections from Icon Selector
- Validates entity and icon existence
- Fetches SVG content from merged icon cache
- Resolves module paths and Entity.xml locations
- Generates WebResource names (`appbase_<entity>icon`)

### create_icon_webresources.py
Creates WebResource files and updates XML files to apply icons to entities.

**Input:** `approved_icons_validated.json`
**Output:** WebResource files + XML updates

**What it does:**
1. Creates `.data.xml` files (WebResource metadata)
2. Creates SVG content files (icon artwork)
3. Updates `Entity.xml` with `<IconVectorName>`
4. Updates `Solution.xml` with `<RootComponent type="61">`

**Safety:** Prompts for confirmation before making file changes

**Command-line Options:**
```powershell
# Show help
python ui-tools/backend/scripts/process_icon_approvals.py --help
python ui-tools/backend/scripts/create_icon_webresources.py --help

# Process specific module
python ui-tools/backend/scripts/process_icon_approvals.py --module operations/asset-management
python ui-tools/backend/scripts/create_icon_webresources.py --module operations/asset-management

# Skip confirmation (automation)
python ui-tools/backend/scripts/create_icon_webresources.py --module operations/asset-management --yes

# Common module paths:
# - operations/asset-management
# - government/court-case-management
# - workforce/hr-administration
# - financial/financial-management
# - external-engagement/event-management
```

**Workflow for Testing One Module:**
```powershell
# 1. Select icons for just one module in Icon Selector
# 2. Export approved_icons.json
# 3. Validate and apply to that module only
python ui-tools/backend/scripts/process_icon_approvals.py --module operations/asset-management
python ui-tools/backend/scripts/create_icon_webresources.py --module operations/asset-management

# 4. Review changes
git diff operations/asset-management

# 5. Build and test import
cd operations/asset-management
msbuild /t:Rebuild
# Import to test environment and verify

# 6. If successful, repeat for next module
# 7. When all done, commit all changes together
```

## Icon Selector Tool

The Icon Selector is a web-based tool built into the `ui-tools` app:

**Frontend:** Svelte component at `ui-tools/frontend/src/routes/IconSelector.svelte`
**Backend:** FastAPI router at `ui-tools/backend/routers/icon_selector.py`

**Features:**
- Browse 378 entities across 27 modules
- Search 14,189 icons with fuzzy matching
- Preview icons inline with entity list
- Track completion progress (0/378)
- Export approved selections to JSON
- **Apply to Module** - One-click apply for selected module

**API Endpoints:**
- `GET /api/icon-selector/modules` - List modules
- `GET /api/icon-selector/modules/{path}/entities` - Get entities
- `POST /api/icon-selector/icons/search` - Search icons
- `GET /api/icon-selector/icons/{name}/svg` - Serve SVG
- `POST /api/icon-selector/entities/{name}/icon` - Save selection
- `GET /api/icon-selector/selections/export` - Export to JSON
- `POST /api/icon-selector/apply-to-module` - Apply icons to module

## Dependencies

**Python:**
- Python 3.8+
- Standard library only (json, pathlib, xml.etree.ElementTree, uuid)

**UI Tools:**
- FastAPI (backend)
- Svelte (frontend)
- See `ui-tools/backend/requirements.txt`

## WebResource Format

Each icon generates two files:

**1. Metadata (.data.xml):**
```xml
<WebResource>
  <WebResourceId>{GUID}</WebResourceId>
  <Name>appbase_asseticon</Name>
  <DisplayName>Asset Icon</DisplayName>
  <WebResourceType>11</WebResourceType>
  <FileName>/WebResources/appbase_asseticon{GUID-NO-HYPHENS}</FileName>
</WebResource>
```

**2. Content (no extension):**
```xml
<svg xmlns="http://www.w3.org/2000/svg" ...>
  <!-- SVG paths -->
</svg>
```

## Troubleshooting

**Icon Selector won't start:**
- Ensure both backend and frontend servers are running
- Check http://localhost:8000 (backend) and http://localhost:5173 (frontend)

**process_icon_approvals.py fails:**
- Ensure `approved_icons.json` exists (export from Icon Selector first)
- Check `merged_icons_cache_clean.json` exists in `.icons/`
- Verify `entity_inventory.json` exists in `.icons/`

**create_icon_webresources.py fails:**
- Run `ui-tools/backend/scripts/process_icon_approvals.py` first
- Ensure you have write permissions to module directories
- Check Solution.xml and Entity.xml files are valid XML

**Icons don't appear in Power Platform:**
- Ensure solution is built and imported
- Clear browser cache
- Check WebResource is registered in Solution.xml
- Verify IconVectorName matches WebResource name exactly
