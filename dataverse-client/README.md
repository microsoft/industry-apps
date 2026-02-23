# Dataverse Client Library

Shared Python library for interacting with Microsoft Dataverse Web API.

## Purpose

This library provides a unified interface for Dataverse operations used by:
- **build-automation** CLI tools for the Power Platform Agent
- **ui-tools/backend** FastAPI server for the web UI

## Features

- **DataverseClient**: Complete Dataverse Web API wrapper
  - Authentication via MSAL
  - Field creation (all types: Text, Choice, Lookup, etc.)
  - Global option set creation
  - Metadata queries

- **Configuration**: Utilities for reading deployment config
  - Load deployments.json
  - Extract authentication credentials
  - Scan solution files

- **BUILD.md Parsing**: Extract field/choice definitions from BUILD.md files
  - Parse entity sections
  - Parse choice fields sections
  - Support "Planned" and "Completed" tracking

- **BUILD.md Updating**: Move items from Planned to Completed
  - Update entity fields
  - Update choice sets

- **Schema Helpers**: Generate schema names, validate formats

## Installation

### For Development

From ui-tools/backend or build-automation directories:

```bash
pip install -e ../dataverse-client
```

### Dependencies

Automatically installs:
- msal (Microsoft Authentication Library)
- httpx (HTTP client)
- pydantic (Data validation)

## Usage

### DataverseClient

```python
from dataverse_client import DataverseClient, get_deployment_auth, load_deployment_config

# Load configuration
config = load_deployment_config()
auth = get_deployment_auth(config, "CDX FAST", "Development")

# Create client
client = DataverseClient(
    environment_url=auth['environment_url'],
    tenant_id=auth['tenant_id'],
    client_id=auth['client_id'],
    client_secret=auth['client_secret']
)

# Authenticate
client.authenticate()

# Create a field
result = client.create_string_field(
    table_name="appbase_event",
    schema_name="appbase_eventname",
    display_name="Event Name",
    max_length=200,
    required=True
)

# Create a global option set
result = client.create_global_optionset(
    schema_name="appbase_eventstatus",
    display_name="Event Status",
    description="Status of an event",
    options=[
        {"label": "Draft", "value": 147130000},
        {"label": "Published", "value": 147130001}
    ],
    solution_unique_name="appbase_eventmanagement"
)
```

### BUILD.md Parsing

```python
from dataverse_client import parse_buildmd

result = parse_buildmd(Path("event-management/BUILD.md"))

print(f"Entities: {len(result['entities'])}")
print(f"Choice Sets: {len(result['choiceSets'])}")

for entity in result['entities']:
    print(f"{entity['name']}: {len(entity['fields'])} fields")
```

### Configuration

```python
from dataverse_client import load_deployment_config, scan_solutions

config = load_deployment_config()
print(f"Deployments: {list(config.keys())}")

solutions = scan_solutions()
for solution in solutions:
    print(f"{solution['name']} - prefix: {solution['prefix']}")
```

## Architecture

This library eliminates the need for CLI tools to make HTTP calls to the backend server. Instead, both CLI and backend import this shared library directly:

**Before:**
```
CLI → HTTP → Backend API → DataverseClient → Dataverse
```

**After:**
```
CLI → DataverseClient → Dataverse
Backend API → DataverseClient → Dataverse
```

Benefits:
- Faster CLI execution (no HTTP overhead)
- Simplified deployment (CLI doesn't need backend running)
- Single source of truth for Dataverse operations
- Better error handling (direct exceptions)
