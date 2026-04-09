# Field Type Patterns in Dataverse FormXML

This document catalogs the control class IDs and XML patterns for different field types based on captures from the Test form.

## Source Capture
- **Form**: Test (appbase_Test)
- **Tab**: Test Tab
- **Sections**: Test Section (1 column), One Column Section (1 column), Two Column Section (2 columns)
- **Capture Date**: 2026-04-09

## Field Type Control Class IDs

### Text-Based Fields

| Field Type | Control ClassId | Notes |
|------------|----------------|-------|
| **Text** (Single Line) | `{4273EDBD-AC1D-40D3-9FB2-095C621B552D}` | Standard single-line text field |
| **Email** | `{ADA2203E-B4CD-49BE-9DDF-234642B43B52}` | Email address with validation |
| **URL** | `{71716B6C-711E-476C-8AB8-5D11542BFB47}` | Hyperlink field |
| **Memo** (Multi-line) | `{E0DECE4B-6FC8-4A8F-A065-082708572369}` | Multi-line text field |

### Numeric Fields

| Field Type | Control ClassId | Notes |
|------------|----------------|-------|
| **Whole Number** | `{C6D124CA-7EDA-4A60-AEA9-7FB8D318B68F}` | Integer values |
| **Decimal** | `{C3EFE0C3-0EC6-42BE-8349-CBD9079DFD8E}` | Decimal precision numbers |
| **Float** | `{0D2C745A-E5A8-4C8F-BA63-C6D3BB604660}` | Floating point numbers |
| **Currency** | `{533B9E00-756B-4312-95A0-DC888637AC78}` | Money values with currency symbol |

### Date/Time Fields

| Field Type | Control ClassId | Notes |
|------------|----------------|-------|
| **Date** | `{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}` | Date only |
| **Date Time** | `{5B773807-9FB2-42DB-97C3-7A91EFF8ADFF}` | Date and time (same classid as Date) |

### Choice and Lookup Fields

| Field Type | Control ClassId | Notes |
|------------|----------------|-------|
| **Choice** (OptionSet) | `{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}` | Dropdown/picklist |
| **Lookup** | `{270BD3DB-D9AF-4782-9025-509E298DEC0A}` | Reference to another entity |

## XML Structure Patterns

### 1-Column Section - Fields in Separate Rows

Each field gets its own row:

```xml
<section columns="1" ...>
  <rows>
    <row />  <!-- Empty row for spacing -->
    <row>
      <cell id="{guid}" locklevel="0" colspan="1" rowspan="1">
        <labels>
          <label description="Text Field" languagecode="1033" />
        </labels>
        <control id="appbase_textfield" 
                 classid="{4273EDBD-AC1D-40D3-9FB2-095C621B552D}" 
                 datafieldname="appbase_textfield" 
                 disabled="false" />
      </cell>
    </row>
    <row>
      <cell id="{guid}" locklevel="0" colspan="1" rowspan="1">
        <labels>
          <label description="Email Field" languagecode="1033" />
        </labels>
        <control id="appbase_emailfield" 
                 classid="{ADA2203E-B4CD-49BE-9DDF-234642B43B52}" 
                 datafieldname="appbase_emailfield" 
                 disabled="false" />
      </cell>
    </row>
  </rows>
</section>
```

### 2-Column Section - Multiple Fields Per Row

Two fields side-by-side in the same row:

```xml
<section columns="11" ...>
  <rows>
    <row />  <!-- Empty row for spacing -->
    <row>
      <cell id="{guid}" locklevel="0" colspan="1" rowspan="1">
        <labels>
          <label description="Choice Field" languagecode="1033" />
        </labels>
        <control id="appbase_choicefield" 
                 classid="{3EF39988-22BB-4F0B-BBBE-64B5A3748AEE}" 
                 datafieldname="appbase_choicefield" 
                 disabled="false" />
      </cell>
      <cell id="{guid}" locklevel="0" colspan="1" rowspan="1">
        <labels>
          <label description="Lookup Field" languagecode="1033" />
        </labels>
        <control id="appbase_lookupfield" 
                 classid="{270BD3DB-D9AF-4782-9025-509E298DEC0A}" 
                 datafieldname="appbase_lookupfield" 
                 disabled="false" />
      </cell>
    </row>
  </rows>
</section>
```

## Key Observations

1. **Cell Attributes**: All field cells have consistent attributes:
   - `locklevel="0"`
   - `colspan="1"`
   - `rowspan="1"`

2. **Control Attributes**: All controls have:
   - `id`: Matches the field schema name
   - `classid`: Specific to field type
   - `datafieldname`: Matches the field schema name
   - `disabled="false"`

3. **Row Structure**:
   - Sections typically start with an empty `<row />` for spacing
   - In 1-column sections: one cell per row
   - In 2-column sections: two cells per row (side-by-side)

4. **Labels**:
   - Each cell has a `<labels>` element
   - Contains `<label>` with `description` (display text) and `languagecode="1033"` (English)

## Implementation Guidelines

### Adding Fields to 1-Column Sections
- Add each field in a new row
- Use `Section.add_field(field_name, field_label, field_type)` with default parameters
- This creates a new row automatically

### Adding Fields to 2-Column Sections
- Add two fields to the same row for side-by-side layout
- First field: `Section.add_field(field_name, field_label, field_type, row_index=None)`
- Second field: `Section.add_field(field_name, field_label, field_type, row_index=-1, cell_position=1)`
  - `row_index=-1` means last row
  - `cell_position=1` means second cell in the row

### Field Type Mapping
All field type mappings are stored in `formxml_constants.py`:
- `FIELD_TYPE_TO_CLASSID`: Maps friendly names to classids
- `ControlClassId` enum: Contains all control type constants
- Supported friendly names: "text", "email", "url", "memo", "integer", "decimal", "float", "currency", "date", "datetime", "choice", "lookup", etc.
