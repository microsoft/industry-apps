# FormXML Parser - Issues to Fix

Based on comparison between programmatic output and UI-generated FormXML (Capture 02).

## Test Results

✓ Parsing works correctly
✓ Can add tabs programmatically
✗ Generated XML doesn't match UI patterns exactly

---

## Issues Found

### Issue 1: Form Element - Extra `shownavigationbar` Attribute

**Current behavior**:
```xml
<form headerdensity="HighWithControls" shownavigationbar="false">
```

**Expected (from UI)**:
```xml
<form headerdensity="HighWithControls">
```

**Fix needed**: Don't add `shownavigationbar` attribute when writing form element (or only add if it was originally present and not default).

---

### Issue 2: Missing Header and Footer Sections

**Current behavior**: No header/footer sections generated

**Expected (from UI)**: When `headerdensity="HighWithControls"` is added, header and footer should be auto-generated:

```xml
<header id="{GUID}" celllabelposition="Top" columns="111" labelwidth="115" celllabelalignment="Left">
  <rows>
    <row>
      <cell id="{GUID}" showlabel="false">
        <labels><label description="" languagecode="1033" /></labels>
      </cell>
      <!-- 2 more cells -->
    </row>
  </rows>
</header>
<footer id="{GUID}" celllabelposition="Top" columns="111" labelwidth="115" celllabelalignment="Left">
  <!-- similar structure -->
</footer>
```

**Fix needed**: `add_tab()` method should check if this is the first non-default tab, and if so:
1. Set `headerdensity="HighWithControls"` on form
2. Create header section if not exists
3. Create footer section if not exists

---

### Issue 3: New Tab Has Wrong `IsUserDefined` Value

**Current behavior**: New tab has `IsUserDefined="1"`

```xml
<tab name="tab_sample" id="{...}" IsUserDefined="1" ...>
```

**Expected (from UI)**: New tabs should have `IsUserDefined="0"`

```xml
<tab name="tab_2" id="..." IsUserDefined="0" ...>
```

**Fix needed**: When creating new tabs in `add_tab()`, set `IsUserDefined="0"` (not "1"). The first tab (General) has IsUserDefined="1", but user-created tabs have "0".

---

### Issue 4: New Tab Has `verticallayout="true"` Attribute

**Current behavior**: New tab has `verticallayout="true"`

```xml
<tab name="tab_sample" ... verticallayout="true">
```

**Expected (from UI)**: New tabs do NOT have `verticallayout` attribute

```xml
<tab name="tab_2" ... >
```

**Fix needed**: Don't add `verticallayout` attribute to newly created tabs. This attribute only exists on the default General tab.

---

### Issue 5: New Tab Missing `showlabel="true"` Attribute

**Current behavior**: New tab missing `showlabel` attribute

**Expected (from UI)**:
```xml
<tab name="tab_2" ... showlabel="true">
```

**Fix needed**: Add `showlabel="true"` to newly created tabs.

---

### Issue 6: New Tab Has Empty Column

**Current behavior**:
```xml
<columns>
  <column width="100%" />
</columns>
```

**Expected (from UI)**: Column should contain a default section
```xml
<columns>
  <column width="100%">
    <sections>
      <section name="tab_2_section_1" ... >
        <!-- section content -->
      </section>
    </sections>
  </column>
</columns>
```

**Fix needed**: When `add_tab()` is called without a section, it should automatically create a default section. Or `add_tab()` should require a section label and always create one.

---

### Issue 7: Default Section Missing Proper Attributes

**When a default section is created, it needs these attributes**:

```xml
<section 
  name="{tab_name}_section_1" 
  id="{GUID}" 
  IsUserDefined="0" 
  locklevel="0" 
  showlabel="true" 
  showbar="false" 
  layout="varwidth" 
  celllabelalignment="Left" 
  celllabelposition="Left" 
  columns="1" 
  labelwidth="115">
```

And should contain an empty row:
```xml
<rows>
  <row />
</rows>
```

---

### Issue 8: General Tab Section Gained Extra Attributes

**Observation**: When parsing the baseline Sample form, the General tab's section had minimal attributes:
```xml
<section showlabel="false" showbar="false" IsUserDefined="0" id="{...}">
```

But after writing, it gained extra attributes:
```xml
<section ... layout="varwidth" celllabelalignment="Left" celllabelposition="Left" columns="1" labelwidth="115">
```

**Fix needed**: Parser should preserve original attributes and not add defaults when writing. Only add attributes that were explicitly set or are required.

---

## Priority Fixes

**High Priority** (breaks UI compatibility):
1. Issue 3: Fix `IsUserDefined` value for new tabs (should be "0")
2. Issue 4: Remove `verticallayout` from new tabs
3. Issue 6: Create default section when adding tab
4. Issue 7: Ensure default section has proper attributes

**Medium Priority** (improves compatibility):
5. Issue 2: Auto-generate header/footer when first tab is added
6. Issue 5: Add `showlabel="true"` to new tabs

**Low Priority** (cosmetic/optimization):
7. Issue 1: Don't add `shownavigationbar` unnecessarily
8. Issue 8: Preserve original attributes, don't add defaults

---

## Recommended Approach

1. **First**: Fix the `add_tab()` method in formxml_parser.py to:
   - Set correct default values (IsUserDefined="0", showlabel="true", no verticallayout)
   - Always create a default section in the tab
   - Check if this is first user tab and add header/footer

2. **Second**: Fix attribute preservation in write_file() to not add unnecessary defaults

3. **Third**: Re-run test and compare again

---

## Files to Modify

- [ui-tools/scripts/formxml_parser.py](../ui-tools/scripts/formxml_parser.py) — Main parser library
  - `FormDefinition.add_tab()` method
  - `Tab.to_xml()` method  
  - `Section.to_xml()` method
  - `Tab.__init__()` default values
  - Header/footer generation logic

---

## Next Steps

1. Review formxml_parser.py code to understand current implementation
2. Fix issues in priority order
3. Re-run test_formxml_parser.py
4. Compare output again until it matches UI exactly
