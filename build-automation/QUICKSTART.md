# Quick Start Guide

## Setup

1. **Install dependencies**:
   ```bash
   cd build-automation
   pip install -r requirements.txt
   ```

2. **Configure deployments**:
   - Ensure `.config/deployments.json` has your Dataverse environment details
   - Tools connect directly to Dataverse (no backend server needed)

## Test the Parser

Test on an existing BUILD.md file:

```bash
python cli_parse_buildmd.py --file ../external-engagement/event-management/BUILD.md
```

This will output JSON with extracted entities and choice sets.

## Test Configuration Helper

Get available deployments and solutions:

```bash
python cli_get_config.py
```

## Test Duplicate Checker

Check for existing choice sets (requires valid deployment configuration):

```bash
python cli_check_duplicates.py \
  --choice-names "Event Status,Payment Status" \
  --deployment "CDX FAST" \
  --environment "FAST APPS"
```

## Use with GitHub Copilot

The Power Platform Agent is configured in `.github/agents/Power Platform Builder.agent.md`.

**In VS Code:**

1. Open any BUILD.md file
2. Open Copilot Chat (Ctrl+Shift+I or Cmd+Shift+I)
3. Type: `@Power Platform Agent current file`
4. Review the generated plan
5. Confirm when prompted
6. Wait for completion

## Example Workflow (Single Entity)

1. **Open BUILD.md**: `external-engagement/event-management/BUILD.md`

2. **Invoke agent**: `@Power Platform Agent create Event entity fields from current file`

3. **Agent will**:
   - Parse the file for Event entity only
   - Show execution plan for Event's planned fields
   - Ask for deployment/environment/solution
   - Wait for approval

4. **After approval, agent executes**:
   - Creates fields on Event entity
   - Updates BUILD.md moving Event's fields from Planned to Completed

5. **Review results** in Copilot Chat and verify in Dataverse

## Example Workflow (Single Choice)

1. **Open BUILD.md**: `external-engagement/event-management/BUILD.md`

2. **Invoke agent**: `@Power Platform Agent create Event Status choice from current file`

3. **Agent will**:
   - Parse the file for Event Status choice set
   - Check for duplicates
   - Show execution plan
   - Ask for deployment/environment/solution
   - Wait for approval

4. **After approval, agent executes**:
   - Creates "Event Status" global option set
   - Updates BUILD.md moving choice from Planned to Completed

5. **Use the choice** in subsequent field creation

## Troubleshooting

**BUILD.md Format for Choices**:
- Choice fields section should have **Completed:** and **Planned:** markers
- Example format:
  ```markdown
  ## ✅ New Choice Fields for Module Name
  
  **Completed:**
  - Previously Created Choice
  
  **Planned:**
  
  ### Event Status
  - Draft
  - Published
  - Cancelled
  ```
- If your BUILD.md doesn't have these sections, add them manually before using the agent

**Parser returns empty results**:
- Check BUILD.md format: entities must have `### Entity Name` headers
- Planned section must have `**Planned:**` marker
- Fields must use `- Name: Type` or `- Name: Type (Details)` format

**Backend connection errors**:
- Verify `http://localhost:8000` is accessible
- Check ui-tools backend is running: `cd ui-tools/backend && python main.py`
- Check `.config/deployments.json` exists

**Choice creation fails**:
- Verify deployment/environment names match `.config/deployments.json`
- Check authentication credentials in config file
- Verify solution unique name is correct

**Agent doesn't appear**:
- Restart VS Code
- Check `.github/agents/Power Platform Builder.agent.md` exists
- Verify GitHub Copilot extension is enabled
