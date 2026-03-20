# FormXml Library - Quick Start Guide

Simple guide to get started with local FormXml authoring in Python.

## Installation

No installation needed! The library uses Python standard library only (Python 3.9+).

All files are in `ui-tools/scripts/`:
- `formxml_constants.py` - Control type constants
- `formxml_parser.py` - Core library
- `formxml_tool.py` - CLI tool
- `formxml_example.py` - Example script

## Quick Examples

### 1. View a Form's Structure

```bash
cd ui-tools/scripts
python formxml_tool.py list ../../government/court-case-management/src/Entities/appbase_CourtCase/FormXml/main/*.xml
```

### 2. Add a Field to an Existing Form

```bash
python formxml_tool.py add-field path/to/form.xml \
  --tab "General" \
  --section "Details" \
  --field "appbase_mynewfield" \
  --label "My New Field" \
  --type "text"
```

### 3. Create a Complete Tab Programmatically

```python
from pathlib import Path
from formxml_parser import FormXmlParser

# Load form
form = FormXmlParser.parse_file(Path("form.xml"))

# Add tab
tab = form.add_tab("tab_evidence", "Evidence")

# Add section
section = tab.add_section("section_items", "Evidence Items", columns=2)

# Add fields
section.add_field("appbase_evidencetype", "Type", "optionset")
section.add_field("appbase_collecteddate", "Collected Date", "datetime")
section.add_field("appbase_custodian", "Custodian", "lookup")

# Save
FormXmlParser.write_file(form, Path("form_modified.xml"))
```

## Common Field Types

| Type | Use For |
|------|---------|
| `text` | Single-line text |
| `multiline` | Multi-line text / notes |
| `optionset` | Dropdown choice |
| `lookup` | Reference to another record |
| `datetime` | Date and time |
| `currency` | Money amounts |
| `integer` | Whole numbers |
| `twooptions` | Yes/No or True/False |

See full list: `python formxml_tool.py list-types`

## Complete Workflow Example

```bash
# 1. Check current structure
python formxml_tool.py list MyEntity.xml --verbose

# 2. Add new tab
python formxml_tool.py add-tab MyEntity.xml \
  --name "tab_custom" --label "Custom Info"

# 3. Add section to tab
python formxml_tool.py add-section MyEntity.xml \
  --tab "Custom Info" \
  --name "section_details" \
  --label "Details" \
  --columns 2

# 4. Add fields
python formxml_tool.py add-field MyEntity.xml \
  --tab "Custom Info" \
  --section "Details" \
  --field "new_status" \
  --label "Status" \
  --type "optionset"

python formxml_tool.py add-field MyEntity.xml \
  --tab "Custom Info" \
  --section "Details" \
  --field "new_notes" \
  --label "Notes" \
  --type "multiline"

# 5. Validate
python formxml_tool.py validate MyEntity.xml

# 6. Check updated structure
python formxml_tool.py list MyEntity.xml
```

## Run the Example Script

```bash
# This will add a complete custom tab to a form
python formxml_example.py path/to/form.xml

# Output: form_modified.xml
```

## Tips

1. **Always validate** after making changes: `python formxml_tool.py validate form.xml`
2. **Test on a copy** first before modifying production forms
3. **Use `--verbose`** to see all fields: `python formxml_tool.py list form.xml --verbose`
4. **Tab/section names** are case-insensitive when searching
5. **GUIDs** are generated automatically for new elements
6. **Original file is overwritten** unless you use `-o output.xml`

## Next Steps

- Read [FORMXML_README.md](FORMXML_README.md) for complete documentation
- Check [formxml_example.py](formxml_example.py) for Python API examples
- Explore [formxml_constants.py](formxml_constants.py) for all control types

## Need Help?

```bash
# Show all CLI commands
python formxml_tool.py --help

# Show help for specific command
python formxml_tool.py add-field --help
```

## Common Issues

**Issue: "Error: Tab 'General' not found"**
- Solution: Check exact tab name with `python formxml_tool.py list form.xml`

**Issue: "Unknown field type"**
- Solution: Use `python formxml_tool.py list-types` to see valid types

**Issue: "Error parsing form"**
- Solution: Verify XML is valid FormXml from a Dataverse solution
