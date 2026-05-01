# Git Tracking Strategy for Icon Assignment System

## Overview
The Icon Assignment system is split between:
- **`.icons/`** - Data files only (icon caches, entity inventory)
- **`ui-tools/backend/scripts/`** - Python scripts (application code)

This separation keeps application code in the ui-tools app folder and data separate.

## ✅ Files That MUST Be Checked In

### In `ui-tools/backend/scripts/` (Application Scripts)
- `process_icon_approvals.py` - Validates icon selections
- `create_icon_webresources.py` - Applies icons to modules
- `README.md` - Script documentation

### In `.icons/` (Data Files Only)
- `merged_icons_cache_clean.json` - Combined library (14,189 icons, ~8MB)
- `entity_inventory.json` - Entity metadata for all 378 entities
- `README.md` - Documentation
- `GIT_TRACKING.md` - This file
- `.gitignore` - Exclusion rules

### Optional Working Files (User Choice)
- `icon_selections.json` - Work-in-progress selections (can check in for backup)
- `approved_icons.json` - Exported selections (can check in for reference)

## ❌ Files That Should NOT Be Checked In

### Cloned Repositories (Too Large)
- `tabler-repo/` - Cloned Tabler Icons repo
- `material-repo/` - Cloned Material Design Icons repo  
- `lucide-repo/` - Cloned Lucide Icons repo
- `fontawesome-repo/` - Cloned FontAwesome repo (removed from merged cache)

### Individual Library Caches (Can Be Regenerated)
- `tabler_icons_cache.json`
- `material_icons_cache.json`
- `lucide_icons_cache.json`
- `fontawesome_icons_cache.json`
- `tabler_tag_vocabulary.json`

### Generated/Temporary Files
- `icon_preview_report.html` - HTML report (generated)
- `entities_with_context.json` - Intermediate processing
- `entity_tags.json` - Generated tags
- `icon_suggestions.json` - Automated suggestions
- `approved_icons_validated.json` - Validated selections (regenerated)
- `merged_icons_cache.json` - Uncleaned version (use _clean instead)

## 🔧 Root .gitignore Configuration

The root `.gitignore` previously ignored the entire `.icons/` folder:
```
.icons  # ❌ This completely blocked the folder
```

Updated to:
```
# .icons - NOTE: Selectively tracked (see .icons/.gitignore for exclusions)
```

Now git will:
1. Look inside `.icons/` folder
2. Use `.icons/.gitignore` to selectively exclude files
3. Track Python scripts and essential data files
4. Ignore cloned repos and generated files

## 📦 What Gets Committed

After proper setup, `git status` should show:
```
modified:   .gitignore (root)
new file:   .icons/.gitignore
new file:   .icons/README.md
new file:   .icons/GIT_TRACKING.md
new file:   .icons/merged_icons_cache_clean.json
new file:   .icons/entity_inventory.json
new file:   ui-tools/backend/scripts/README.md
new file:   ui-tools/backend/scripts/process_icon_approvals.py
new file:   ui-tools/backend/scripts/create_icon_webresources.py
modified:   ui-tools/backend/routers/icon_selector.py (updated paths)
(plus Icon Selector UI files already in ui-tools/)
```

## 🚀 For New Developers

When cloning the repo, they get:
- ✅ Icon Selector UI (`ui-tools/frontend/`)
- ✅ Icon Selector API (`ui-tools/backend/routers/icon_selector.py`)
- ✅ Python scripts (`ui-tools/backend/scripts/`)
- ✅ Icon cache data (`.icons/merged_icons_cache_clean.json`)
- ✅ Entity inventory (`.icons/entity_inventory.json`)

They do NOT need to:
- ❌ Clone icon library repos
- ❌ Run icon extraction scripts
- ❌ Regenerate merged caches

They can **immediately**:
1. Start ui-tools servers
2. Use Icon Selector to pick icons
3. Click "Apply to Module"
4. Test import to Power Platform

## 📝 Notes

- The merged cache (`merged_icons_cache_clean.json`) is ~8MB but compresses well in git
- Icon library repos are ~500MB+ total, so they MUST stay excluded
- Individual cache files can be regenerated if needed via extraction scripts
- Working files (`icon_selections.json`) can be checked in for collaboration
