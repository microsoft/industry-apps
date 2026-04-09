# FormXML Patterns Learned from UI Captures

This document records patterns observed when comparing UI-generated FormXML changes.

---

## Capture 02 - Add Tab

**Operation**: Added a new tab via Dataverse form designer, renamed to "Test Tab", with default section renamed to "Test Section"

**Files Compared**:
- Baseline: `captures/01 - Baseline/src/Entities/appbase_Test/FormXml/main/{3fa70a65-3d83-4337-a3de-def80061a5e4}.xml`
- Modified: `captures/02 - Add Tab/src/Entities/appbase_Test/FormXml/main/{3fa70a65-3d83-4337-a3de-def80061a5e4}.xml`

### Changes Observed

#### 1. Form Element
**Added attribute**: `headerdensity="HighWithControls"`

```xml
<!-- Before -->
<form>

<!-- After -->
<form headerdensity="HighWithControls">
```

**Note**: This attribute appears when any tab is added beyond the default. It controls header display style.

#### 2. New Tab Structure
**Added entire tab element**:

```xml
<tab name="tab_2" id="f0644517-cbfc-42e7-8e02-0025af9c349d" IsUserDefined="0" locklevel="0" showlabel="true">
  <labels>
    <label description="Test Tab" languagecode="1033" />
  </labels>
  <columns>
    <column width="100%">
      <sections>
        <!-- section content -->
      </sections>
    </column>
  </columns>
</tab>
```

**Key Tab Attributes**:
- `name="tab_2"` — System-generated name (incremental: tab_2, tab_3, etc.)
- `id="{GUID}"` — Unique GUID for the tab
- `IsUserDefined="0"` — Indicates user-created tab (vs. system default)
- `locklevel="0"` — Security level (0 = no lock)
- `showlabel="true"` — Display the tab label
- **Missing `verticallayout` attribute** (present in General tab but NOT in new tabs)

**Differences from General Tab**:
- General tab has: `verticallayout="true"` and `IsUserDefined="1"`
- New tabs have: NO verticallayout attribute, `IsUserDefined="0"`

#### 3. Section Structure (Default in New Tab)
**Section element**:

```xml
<section name="tab_2_section_1" id="cba6fe36-1809-4fd9-a6cf-40f097171d52" 
         IsUserDefined="0" locklevel="0" showlabel="true" showbar="false" 
         layout="varwidth" celllabelalignment="Left" celllabelposition="Left" 
         columns="1" labelwidth="115">
  <labels>
    <label description="Test Section" languagecode="1033" />
  </labels>
  <rows>
    <row />
  </rows>
</section>
```

**Key Section Attributes** (vs. General tab's section which has minimal attributes):
- `name="tab_2_section_1"` — System-generated name linked to tab
- `id="{GUID}"` — Unique GUID
- `IsUserDefined="0"` — User-created
- `locklevel="0"` — No lock
- `showlabel="true"` — Display section label
- `showbar="false"` — Don't show separator bar
- `layout="varwidth"` — Variable width layout
- `celllabelalignment="Left"` — Field label alignment
- `celllabelposition="Left"` — Field label position
- `columns="1"` — Number of columns in section
- `labelwidth="115"` — Width of field labels

**Empty Section**: Contains single empty `<row />` element

#### 4. Header and Footer Auto-Generation
When `headerdensity="HighWithControls"` is added, header and footer sections are auto-generated:

**Header**:
```xml
<header id="{0fe073e9-96be-41d6-8362-e4accd60920e}" 
        celllabelposition="Top" columns="111" labelwidth="115" 
        celllabelalignment="Left">
  <rows>
    <row>
      <cell id="{...}" showlabel="false">
        <labels><label description="" languagecode="1033" /></labels>
      </cell>
      <!-- 2 more cells -->
    </row>
  </rows>
</header>
```

**Footer**: Similar structure to header

**Note**: Header/footer contain empty cells with `showlabel="false"` and empty description labels.

---

## Patterns Summary for "Add Tab"

To replicate UI behavior when adding a tab programmatically:

1. **If first non-default tab**: Add `headerdensity="HighWithControls"` to `<form>` element
2. **If first non-default tab**: Generate header and footer sections
3. **Tab attributes required**:
   - `name` — Generate as "tab_N" (incremental)
   - `id` — Generate new GUID
   - `IsUserDefined="0"` (not "1" like General)
   - `locklevel="0"`
   - `showlabel="true"`
   - Do NOT add `verticallayout` attribute
4. **Default section in new tab**:
   - `name` — Generate as "{tab_name}_section_1"
   - All layout attributes: `layout="varwidth"`, `celllabelalignment="Left"`, `celllabelposition="Left"`, `columns="1"`, `labelwidth="115"`
   - `showlabel="true"`, `showbar="false"`
   - Empty row: `<row />`
5. **Label elements**: Always include languagecode="1033"

---

## Open Questions

1. Does `headerdensity` always use "HighWithControls" or are there other values?
2. How are tab names numbered if tabs are deleted/reordered?
3. Are header/footer cell GUIDs specific or randomly generated?
4. What happens to header/footer if all non-default tabs are removed?

---

## Next Captures Needed

- **Add Field to Section** — Understand control/cell structure, field-specific attributes
- **Add Subgrid** — Understand subgrid control parameters and structure
- **Modify Field Properties** — See attribute changes for read-only, required, visibility
- **Remove Field** — Understand if cell is removed or just control
- **Add Multi-Column Section** — See how columns>1 affects structure
