# FormXml Authoring Library

A Python library and CLI tool for programmatically manipulating Dataverse Model-Driven App FormXml files. This allows you to add, remove, and modify form elements (tabs, sections, fields, subgrids) without using the Dataverse UI.

## Files

- **`formxml_constants.py`** - Constants for control types (classids), form presentation types, and field type mappings
- **`formxml_parser.py`** - Core parser and object model for reading, manipulating, and writing FormXml files
- **`formxml_tool.py`** - Command-line interface for common form manipulation tasks

## Features

### Supported Operations

- ✅ **Parse FormXml files** - Read existing form definitions into Python objects
- ✅ **Add tabs** - Create new tabs with custom names and labels
- ✅ **Remove tabs** - Delete tabs by name
- ✅ **Add sections** - Create new sections within tabs
- ✅ **Add fields** - Add field controls (text, lookup, optionset, datetime, etc.)
- ✅ **Remove fields** - Delete fields from sections
- ✅ **Add subgrids** - Add related entity subgrids with relationship configuration
- ✅ **Validate forms** - Check form structure for common issues
- ✅ **List structure** - Display form hierarchy and field inventory
- ✅ **Write FormXml** - Save modified forms back to XML files

### Supported Control Types

**Text Controls:**
- Single-line text (`text`, `singleline`)
- Multi-line text (`multiline`, `memo`, `richtext`)

**Numeric Controls:**
- Whole number (`integer`, `wholenumber`)
- Decimal number (`decimal`, `float`)
- Currency (`currency`, `money`)

**Date/Time:**
- Date and time (`datetime`, `date`)

**Choice Controls:**
- Option set (`optionset`, `picklist`, `choice`)
- Two options / Boolean (`twooptions`, `boolean`, `yesno`)
- Status (`status`, `statuscode`)

**Lookup Controls:**
- Lookup (`lookup`, `customer`, `owner`)

**Other Controls:**
- Subgrid (`subgrid`)
- Notes (`notes`)
- Quick view form (`quickview`)
- iFrame (`iframe`)
- Web resource (`webresource`)
- Spacer (`spacer`)

## Usage

### Command-Line Interface

#### List Form Structure

```bash
python formxml_tool.py list path/to/form.xml

# Verbose mode (shows all fields)
python formxml_tool.py list path/to/form.xml --verbose
```

#### Add a Tab

```bash
python formxml_tool.py add-tab path/to/form.xml \
  --name "tab_evidence" \
  --label "Evidence"

# Insert at specific position
python formxml_tool.py add-tab path/to/form.xml \
  --name "tab_summary" \
  --label "Summary" \
  --index 0
```

#### Remove a Tab

```bash
python formxml_tool.py remove-tab path/to/form.xml \
  --name "tab_evidence"
```

#### Add a Section

```bash
python formxml_tool.py add-section path/to/form.xml \
  --tab "General" \
  --name "contact_info" \
  --label "Contact Information" \
  --columns 2
```

#### Add a Field

```bash
python formxml_tool.py add-field path/to/form.xml \
  --tab "General" \
  --section "Details" \
  --field "appbase_priority" \
  --label "Priority" \
  --type "optionset"

# Add to specific row and position
python formxml_tool.py add-field path/to/form.xml \
  --tab "General" \
  --section "Details" \
  --field "appbase_casenumber" \
  --label "Case Number" \
  --type "text" \
  --row-index 1 \
  --cell-position 0
```

#### Remove a Field

```bash
python formxml_tool.py remove-field path/to/form.xml \
  --tab "General" \
  --section "Details" \
  --field "appbase_priority"
```

#### Add a Subgrid

```bash
python formxml_tool.py add-subgrid path/to/form.xml \
  --tab "Parties" \
  --section "Related" \
  --id "Subgrid_parties" \
  --label "Parties" \
  --relationship "appbase_courtcaseparty_CourtCase" \
  --target-entity "appbase_courtcaseparty" \
  --view-id "{DE397E6C-80E1-48A7-A89C-5B06E1F0ABE7}"
```

#### Validate Form

```bash
python formxml_tool.py validate path/to/form.xml
```

#### List Available Field Types

```bash
python formxml_tool.py list-types
```

### Python API

#### Parse an Existing Form

```python
from pathlib import Path
from formxml_parser import FormXmlParser

# Parse a FormXml file
form = FormXmlParser.parse_file(Path("CourtCase.xml"))

# Access form properties
print(f"Form Name: {form.form_name}")
print(f"Form ID: {form.formid}")
print(f"Number of Tabs: {len(form.tabs)}")
```

#### Create a New Form

```python
from formxml_parser import FormDefinition, generate_guid
from formxml_constants import FormPresentation

# Create a new form
form = FormDefinition(
    formid=generate_guid(),
    form_name="My Custom Form",
    form_presentation=FormPresentation.MAIN.value
)

# Add a tab
tab = form.add_tab("tab_general", "General Information")

# Add a section
section = tab.add_section("section_details", "Details", columns=2)

# Add fields
section.add_field("new_name", "Name", "text")
section.add_field("new_priority", "Priority", "optionset")
section.add_field("new_duedate", "Due Date", "datetime")

# Save to file
FormXmlParser.write_file(form, Path("new_form.xml"))
```

#### Modify an Existing Form

```python
from pathlib import Path
from formxml_parser import FormXmlParser

# Load form
form = FormXmlParser.parse_file(Path("CourtCase.xml"))

# Find a tab
tab = form.get_tab_by_name("General")

# Find a section
section = tab.get_section_by_name("Details")

# Add a field to the section
section.add_field("appbase_customfield", "Custom Field", "text")

# Add a subgrid
section.add_subgrid(
    subgrid_id="Subgrid_custom",
    subgrid_label="Related Records",
    relationship_name="new_relationship",
    target_entity="new_entity",
    view_id="{12345678-1234-1234-1234-123456789012}"
)

# Remove a field
section.remove_field("appbase_oldfield")

# Save changes
FormXmlParser.write_file(form, Path("CourtCase_modified.xml"))
```

#### Work with Multiple Sections

```python
# Iterate through all tabs and sections
for tab in form.tabs:
    tab_label = tab.labels[0].description if tab.labels else "Unknown"
    print(f"Tab: {tab_label}")
    
    for column in tab.columns:
        for section in column.sections:
            section_label = section.labels[0].description if section.labels else "Unknown"
            field_count = sum(1 for row in section.rows for cell in row.cells if cell.control)
            print(f"  Section: {section_label} ({field_count} fields)")
```

## Object Model

### Hierarchy

```
FormDefinition
├── Tab (list)
│   └── Column (list)
│       └── Section (list)
│           └── Row (list)
│               └── Cell (list)
│                   ├── Label (list)
│                   └── Control (optional)
│                       └── SubgridParameters (for subgrids)
├── FormHeader (optional)
│   └── Row (list)
└── FormFooter (optional)
    └── Row (list)
```

### Key Classes

- **`FormDefinition`** - Root object representing the entire form
- **`Tab`** - A tab on the form
- **`Column`** - A column within a tab (most forms have one column per tab)
- **`Section`** - A section containing rows of fields
- **`Row`** - A horizontal row of cells
- **`Cell`** - A container for a control with label
- **`Control`** - A field control (text box, lookup, subgrid, etc.)
- **`Label`** - A localized label with languagecode
- **`SubgridParameters`** - Configuration for subgrid controls

## Technical Details

### GUID Generation

All new elements (tabs, sections, cells) receive unique GUIDs in the format `{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}` (uppercase with braces).

### Control Class IDs

Each control type is identified by a GUID `classid`. The library maps friendly names to these GUIDs:

- Text box: `{4273EDBD-AC1D-40d3-9FB2-095C621B552D}`
- Option set: `{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}`
- Lookup: `{270BD3DB-D9AF-4782-9025-509E298DEC0A}`
- DateTime: `{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}`
- Currency: `{533B9E00-756B-4312-95A0-DC888637AC78}`
- Subgrid: `{E7A81278-8635-4D9E-8D4D-59480B391C5B}`

See `formxml_constants.py` for the complete mapping.

### Localization

Labels support multiple languages via the `languagecode` attribute. Default is `1033` (English - United States). Additional language support can be added by creating multiple `Label` objects with different language codes.

### XML Formatting

The library uses `xml.etree.ElementTree` for parsing and writing XML. Output files are formatted with 2-space indentation for readability.

## Workflow Example

### Scenario: Add a New Tab with Fields to a Court Case Form

```bash
# 1. List the current form structure
python formxml_tool.py list government/court-case-management/src/Entities/appbase_CourtCase/FormXml/main/form.xml

# 2. Add a new "Evidence" tab
python formxml_tool.py add-tab form.xml \
  --name "tab_evidence" \
  --label "Evidence"

# 3. Add a section to the new tab
python formxml_tool.py add-section form.xml \
  --tab "Evidence" \
  --name "section_evidence_details" \
  --label "Evidence Details" \
  --columns 2

# 4. Add fields to the section
python formxml_tool.py add-field form.xml \
  --tab "Evidence" \
  --section "Evidence Details" \
  --field "appbase_evidencetype" \
  --label "Evidence Type" \
  --type "optionset"

python formxml_tool.py add-field form.xml \
  --tab "Evidence" \
  --section "Evidence Details" \
  --field "appbase_collectiondate" \
  --label "Collection Date" \
  --type "datetime"

python formxml_tool.py add-field form.xml \
  --tab "Evidence" \
  --section "Evidence Details" \
  --field "appbase_custodian" \
  --label "Custodian" \
  --type "lookup"

# 5. Add a subgrid for related evidence items
python formxml_tool.py add-subgrid form.xml \
  --tab "Evidence" \
  --section "Evidence Details" \
  --id "Subgrid_evidence_items" \
  --label "Evidence Items" \
  --relationship "appbase_evidence_courtcase" \
  --target-entity "appbase_evidence" \
  --view-id "{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}"

# 6. Validate the modified form
python formxml_tool.py validate form.xml
```

## Limitations

### Current Limitations

- Header/footer manipulation is supported but limited to basic operations
- Business process flow controls are parsed but not fully manipulated
- Tab visibility rules and conditional formatting are not supported
- Form scripts and event handlers are not included in FormXml (those are separate files)
- View generation for subgrids must be done separately

### Future Enhancements

- Support for reordering tabs, sections, and fields
- Copy/move fields between sections
- Bulk operations (add multiple fields at once)
- Form diff and merge capabilities
- Integration with Dataverse API for direct deployment
- Template-based form generation
- Support for card forms, quick create forms, and quick view forms

## Dependencies

- Python 3.9+ (requires `xml.etree.ElementTree.indent`)
- No external packages required (uses standard library only)

## Integration with Dataverse

After modifying FormXml files locally:

1. The modified XML files become part of your Dataverse solution in the `src/Entities/{EntityName}/FormXml/` folders
2. Use the standard Dataverse solution packaging tools to deploy
3. Import the solution into your Dataverse environment
4. Publish customizations to make the form changes visible

## Error Handling

The CLI tool provides detailed error messages:

- File not found errors
- Tab/section not found
- Invalid field types
- Missing required parameters
- XML parsing errors

Use the `validate` command to check for common issues before deployment.

## Contributing

To extend the library:

1. Add new control types to `formxml_constants.py`
2. Extend the object model in `formxml_parser.py`
3. Add new commands to `formxml_tool.py`
4. Follow the existing patterns for parsing and serialization

## License

This library is part of the industry-apps workspace. See the root LICENSE file for details.
