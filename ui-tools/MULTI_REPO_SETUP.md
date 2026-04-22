# Multi-Repo Configuration Guide

The ui-tools in this repository can now manage solutions across multiple repositories.

## Quick Start

### 1. Enable Additional Repos

Edit [.config/repos.json](.config/repos.json) and set `enabled: true` for the repos you want to manage:

```json
{
    "repos": [
        {
            "name": "industry-apps",
            "path": ".",
            "enabled": true,
            "type": "model-driven-apps"
        },
        {
            "name": "industry-agents",
            "path": "../industry-agents",
            "enabled": true,  // ← Change this
            "type": "copilot-agents"
        },
        {
            "name": "industry-portals",
            "path": "../industry-portals",
            "enabled": true,  // ← Change this
            "type": "power-pages"
        }
    ]
}
```

### 2. Open the Workspace (Optional but Recommended)

For the best experience, open [industry-workspace.code-workspace](industry-workspace.code-workspace) in VS Code instead of opening individual repos. This gives you:
- All repos visible in the Explorer
- Unified search across repos
- Single ui-tools instance managing everything

```powershell
code industry-workspace.code-workspace
```

### 3. Verify Detection

Restart the backend and check the startup logs:

```
🚀 Industry Apps Backend Starting
Multi-repo mode: true
Enabled repos: 3
  - industry-apps (model-driven-apps) at C:\Users\...\industry-apps
  - industry-agents (copilot-agents) at C:\Users\...\industry-agents
  - industry-portals (power-pages) at C:\Users\...\industry-portals
```

Or check via API:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/config" | Select-Object -ExpandProperty repos
```

## Requirements

### Each Repo Must Have:
- `.config/deployments.json` - Deployment configuration
- Solution folders with `.cdsproj` files
- Similar structure to industry-apps (categories → modules)

### Repo Structure Example:

```
industry-agents/
├── .config/
│   └── deployments.json
├── customer-service-agents/
│   └── support-agent/
│       └── App-Agent-Support.cdsproj
└── sales-agents/
    └── lead-qualifier/
        └── App-Agent-LeadQualifier.cdsproj
```

## What Gets Merged

When multi-repo mode is enabled, the ui-tools will:

✅ **Modules**: Discover all `.cdsproj` solutions across all repos  
✅ **Environments**: Merge all deployment configurations  
✅ **Tenants**: Combine tenant definitions (conflicts are prefixed)  

Each module in the UI shows:
- Which repo it comes from (`repo` field)
- Its category and version
- Deployment targets from its repo's config

## Deployment

When deploying a module from another repo:
1. The PowerShell scripts receive the correct `-RepoRoot` parameter
2. PAC CLI runs in the context of that repo
3. Paths are resolved relative to the correct repo

## Single-Repo Mode

If you only enable `industry-apps`, everything works exactly as before:
- ✅ No breaking changes
- ✅ Backward compatible
- ✅ Same UI and behavior

## Troubleshooting

### Repo Not Detected

**Check:**
1. Path in `repos.json` is correct (relative to industry-apps)
2. Repo has `.config/deployments.json`
3. `enabled: true` in config
4. Backend was restarted after config change

**View logs:**
```powershell
# Backend startup shows detected repos
```

### Modules Not Showing

**Check:**
1. Repo has proper folder structure (categories → modules)
2. Modules contain `.cdsproj` files
3. Module has config in `deployments.json` or uses DefaultModule

## Implementation Status

**✅ Backend Complete (Phase 1 & 2):**
- ✅ Repo configuration and detection ([.config/repos.json](.config/repos.json))
- ✅ Workspace manager ([workspace.py](ui-tools/backend/workspace.py))
- ✅ Multi-repo module discovery (all repos scanned)
- ✅ Config and environment merging
- ✅ API endpoints updated ([main.py](ui-tools/backend/main.py))
- ✅ PowerShell scripts with `-RepoRoot` parameter (6 scripts)
- ✅ Deployment router passes repo paths ([deployment.py](ui-tools/backend/routers/deployment.py))
- ✅ Models support `repoPath` field ([models.py](ui-tools/backend/models.py))
- ✅ Startup logging shows detected repos

**🚧 Frontend (Phase 3 - Pending):**
- 🚧 Deploy UI: Repo badges and filtering
- 🚧 Stores: Pass repoPath to API calls
- 🚧 Form Builder: Repo selector
- 🚧 Process Simulation: Repo context

**Backend is fully multi-repo ready!** You can now:
- Enable multiple repos in [.config/repos.json](.config/repos.json)
- API will discover modules from all repos
- PowerShell scripts will operate on correct repo
- Frontend will need updates to show repo context

## Files Changed

- [.config/repos.json](.config/repos.json) - Repo configuration
- [ui-tools/backend/workspace.py](ui-tools/backend/workspace.py) - Workspace manager
- [ui-tools/backend/config.py](ui-tools/backend/config.py) - Workspace integration
- [ui-tools/backend/main.py](ui-tools/backend/main.py) - Multi-repo endpoints
- [industry-workspace.code-workspace](industry-workspace.code-workspace) - VS Code workspace
