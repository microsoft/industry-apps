# BUILD.md Automation Tools

Python CLI tools for automating field and choice creation from BUILD.md files. Used by the GitHub Copilot Custom Agent "Power Platform Agent".

## Prerequisites

- Python 3.9+
- Configured deployments in `.config/deployments.json`
- MSAL library for Azure AD authentication (installed via requirements.txt)

## Installation

```bash
cd build-automation
pip install -r requirements.txt
```

## CLI Tools

### cli_parse_buildmd.py
Extracts entities, fields, and choice definitions from BUILD.md files.

```bash
# Parse entire BUILD.md
python cli_parse_buildmd.py --file ../external-engagement/event-management/BUILD.md

# Parse specific entity only
python cli_parse_buildmd.py --file BUILD.md --entity "Event"

# Parse specific choice set only
python cli_parse_buildmd.py --file BUILD.md --choice "Event Status"
```

Output: JSON with `entities` (name, fields) and `choiceSets` (name, values)

### cli_check_duplicates.py
Checks for existing similar choice sets in Dataverse.

```bash
python cli_check_duplicates.py --choice-names "Event Status,Payment Status" --deployment "CDX FAST" --environment Development
```

Output: JSON with match results per choice name

### cli_create_choices.py
Creates global option sets in Dataverse.

```bash
python cli_create_choices.py \
  --deployment "CDX FAST" \
  --environment "FAST APPS" \
  --solution appbase_eventmanagement \
  --prefix appbase_ \
  --choices choices.json
```

**Parameters:**
- `--deployment`: Deployment name from config (e.g., "CDX FAST")
- `--environment`: Environment name (e.g., "Development", "FAST APPS")
- `--solution`: Solution unique name (e.g., "appbase_eventmanagement")
- `--prefix`: Publisher prefix for schema names (e.g., "appbase_")
  - Schema names are auto-generated: "HR Position Status" → "appbase_hrpositionstatus"
- `--choices`: JSON file with choice set array: `[{"name":"...", "description":"", "values":["..."]}]`

**Output:** Streaming progress + JSON summary

**Note:** Uses `os._exit()` for clean termination (MSAL background threads otherwise cause hanging)

### cli_create_fields.py
Creates fields on a Dataverse entity.

```bash
python cli_create_fields.py --deployment "CDX FAST" --environment Development --table appbase_event --prefix appbase_ --fields fields.json
```

Output: Streaming progress + JSON summary

### cli_update_buildmd.py
Moves created fields or choice sets from "Planned:" to "Completed:" in BUILD.md.

```bash
# Move entity fields
python cli_update_buildmd.py --file BUILD.md --entity "Event" --fields "Name,Event Code,Event Type"

# Move choice set
python cli_update_buildmd.py --file BUILD.md --choice "Event Status"
```

Output: Updated BUILD.md + diff

### cli_get_config.py
Retrieves available deployments, environments, and solutions.

```bash
python cli_get_config.py
```

Output: JSON with configuration options

## Architecture

These CLI tools connect directly to Dataverse using the shared `dataverse-client` library. They:
- Use MSAL for Azure AD authentication
- Connect directly to Dataverse Web API
- Format input data from BUILD.md parsing
- Generate schema names automatically with configurable prefix
- Use `os._exit()` for clean process termination (MSAL keeps background threads)

**Key Components:**
- `dataverse-client/client.py` - DataverseClient class for API calls
- `dataverse-client/config.py` - Configuration loading and management
- `dataverse-client/schema_helpers.py` - Schema name generation utilities
- `dataverse-client/buildmd_parser.py` - BUILD.md parsing logic
- Make HTTP requests to `http://localhost:8000/api/*` endpoints
- Stream progress output for real-time feedback
- Return structured JSON for agent parsing

## Usage with Custom Agent

Invoke the Power Platform Agent in VS Code:

```
@Power Platform Agent current file
```

The agent will:
1. Parse the BUILD.md file
2. Check for duplicates
3. Generate an execution plan
4. Wait for approval
5. Execute creation via these CLI tools
6. Update BUILD.md tracking
