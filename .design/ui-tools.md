# UI Tools

UI Tools is a web-based management interface for Microsoft Dataverse operations, providing solution deployment capabilities and administrative helper functions. The application uses a Svelte frontend with client-side routing and a Python FastAPI backend that streams real-time output to the UI. It's configuration-driven through a centralized deployments.json file that manages multiple tenants, environments, and authentication credentials, allowing teams to work across different Azure AD tenants and Dataverse organizations.

## Core Features

### Deploy
Solution lifecycle management using PowerShell and PAC CLI:
- **Drag-and-drop operations**: Drag modules to environments for deployment/shipping, or drag environments to modules for reverse sync
- **Bidirectional sync**: Push changes from local to Dataverse (deploy/ship) or pull changes from Dataverse to local (sync-from for hotfixes)
- **Operation queue**: Review and reorder operations before execution with support for managed/unmanaged deployments
- **Multi-tenant shipping**: Deploy solutions across Azure AD tenants with authentication profiles
- **Version management**: Auto-increment solution versions during sync operations

### Field Creator
Bulk field creation on Dataverse tables using Python with direct Dataverse Web API access:
- **Multi-format parsing**: BUILD.md format, pipe-delimited, or quick-add form for rapid field definition
- **Template system**: Save and reuse common field patterns across tables
- **Real-time creation**: Stream field creation progress with instant feedback
- **Type support**: Text, Memo, Integer, Float, Currency, Date, DateTime, YesNo (Boolean), Choice, Lookup
- **Choice fields**: Reference existing global option sets with automatic validation and name resolution (display name or schema name)
- **Lookup fields**: Create N:1 relationships with RemoveLink cascade delete, auto-detect self-referential hierarchies, proper schema/logical name formatting

### Choice Creator
Global option set (choice field) management with intelligent reuse:
- **Smart search**: Find existing option sets by name or choice values with relevance scoring
- **Live suggestions**: As you create new option sets, see similar existing ones to encourage reuse
- **Direct Dataverse creation**: Creates global option sets via Dataverse API and adds them to solutions
- **Pending sync tracking**: Backend-cached pending items persist across restarts until solution sync completes
- **Browse repository**: Tree view of all option sets organized by category/module

## Architecture

Each deployment in the configuration contains its own Azure AD app registration credentials, enabling secure, app-based authentication to Dataverse environments. The modular architecture makes it easy to add additional helper functions while maintaining the existing deployment workflows. Hot-reload is enabled for both frontend (Vite) and backend (uvicorn) for rapid development iteration.
