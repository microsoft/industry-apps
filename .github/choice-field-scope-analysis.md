# Choice Field Scope Analysis — Design Guidelines

Choice fields should be defined at the **appropriate scope** to maximize reusability while avoiding over-generalization. This document provides guidelines for determining whether a choice field belongs in **Core** (shared across modules) or remains **module-specific**.

---

## Three-Category Analysis

When reviewing choice fields in a module, categorize each into:

### Category A: Replace with Existing Core Field
The choice field **already exists in Core** with the same or very similar values.

**Action:** Delete the module-specific field and use the Core version.

### Category B: Promote to Core
The choice field has **broad applicability** across multiple modules and should be added to Core for reuse.

**Action:** Move the field definition to Core and reference it from the module.

### Category C: Keep in Module
The choice field is **domain-specific** and unlikely to be reused outside the current module.

**Action:** Keep the definition in the module's choice field section.

---

## Decision Criteria

### When to Use Existing Core Fields (Category A)

**Indicators:**
- ✅ Values are identical or nearly identical to a Core field
- ✅ Semantic meaning is the same (not just coincidentally similar values)
- ✅ Same usage context (e.g., both describe frequency, both describe ratings)
- ✅ Core field has all or most of the values you need

**Examples:**
- Module has "Training Frequency" with Daily/Weekly/Monthly → Use Core **Schedule Frequency**
- Module has "Assessment Result" with Pass/Fail → Use Core **Pass Fail Status**
- Module has "Request Status" with Pending/Approved/Rejected → Use Core **Approval Status**

**Red Flags (Don't Replace):**
- ❌ Values are similar but have **different semantic meanings** in your domain
- ❌ Core field is missing critical values for your use case
- ❌ Your field has more specific/granular values that would lose meaning
- ❌ The ordering or workflow logic differs

---

### When to Promote to Core (Category B)

**Indicators:**
- ✅ Values are **generic and widely applicable** (not domain-specific terminology)
- ✅ Likely to be used in **3+ modules** across different domains
- ✅ Represents a **common concept** (frequency, rating, level, mode, scope, etc.)
- ✅ Values are relatively **stable** (unlikely to change frequently)
- ✅ No existing Core field covers this concept

**Examples of Good Core Candidates:**
- **Proficiency Level** (Beginner, Intermediate, Advanced, Expert) — Used in training, recruiting, competencies
- **Frequency** (Daily, Weekly, Monthly, Quarterly, Annual) — Used in scheduling, reporting, compliance
- **Delivery Method** (In Person, Virtual, Hybrid, Self-Service) — Used in training, events, services
- **Education Level** (High School, Bachelor's, Master's, Doctoral) — Used in HR, recruiting, personnel
- **Participation Mode** (In Person, Virtual, Hybrid) — Already in Core, used in training, events, meetings

**Poor Core Candidates (Keep in Module):**
- Domain-specific terminology (e.g., "Recruiting Interview Type" with "Panel Interview")
- Values tied to specific workflow (e.g., "Application Stage" values)
- Highly specialized concepts (e.g., "Court Case Motion Type")
- Values that may evolve frequently based on business rules

**Analysis Questions:**
1. **Generality Test:** Could this choice field be used in a completely different module/domain without modification?
2. **Naming Test:** Can you name it without referencing the specific domain? (e.g., "Proficiency Level" not "Skill Proficiency")
3. **Reuse Test:** Can you identify 3+ realistic use cases across different modules?
4. **Stability Test:** Are these values likely to remain stable, or will they change based on specific business processes?
5. **Value Test:** Are the values generic descriptors (High/Medium/Low) or domain-specific terms (Voir Dire, Arraignment)?

---

### When to Keep in Module (Category C)

**Indicators:**
- ✅ Values use **domain-specific terminology** unique to this module
- ✅ Represents a **specialized concept** unlikely to appear elsewhere
- ✅ Values are tied to **specific workflows or processes** in this domain
- ✅ Values may need to **evolve based on module-specific requirements**

**Examples:**
- **Recruiting Interview Type** (Phone Screen, Panel Interview, Technical Interview, Case Interview)
  - Domain-specific to recruiting; other modules don't have "panel interviews"
  
- **Court Motion Type** (Motion to Dismiss, Motion for Summary Judgment, Motion in Limine)
  - Legal terminology; only applies to court case management
  
- **Investigation Finding Type** (Substantiated, Unsubstantiated, Inconclusive)
  - Specific to investigations; different from general assessment outcomes
  
- **Asset Maintenance Type** (Preventive, Corrective, Predictive, Emergency)
  - Asset management terminology; limited applicability elsewhere

---

## Analysis Methodology

### Step 1: Inventory Module Choice Fields
List all choice fields in the module's "Candidates" or similar section at the bottom of BUILD.md.

### Step 2: Compare Against Core
For each field, search Core BUILD.md for:
- **Exact name matches** (e.g., "Priority", "Approval Status")
- **Semantic equivalents** (e.g., "Request Status" vs "Approval Status")
- **Similar value sets** (even if named differently)

### Step 3: Categorize Using Decision Tree

```
For each choice field:

1. Does an equivalent field exist in Core?
   YES → Category A (Replace)
   NO  → Continue to 2

2. Are the values domain-specific terminology?
   YES → Category C (Keep in Module)
   NO  → Continue to 3

3. Can this be used in 3+ different modules/domains?
   YES → Category B (Promote to Core)
   NO  → Category C (Keep in Module)

4. Are values stable and unlikely to change frequently?
   NO  → Category C (Keep in Module)
   YES → Category B (Promote to Core)
```

### Step 4: Document Decisions
Create a categorized list with justification:

**Category A — Replace with Core:**
- Field Name → Core Field Name (reason)

**Category B — Promote to Core:**
- Field Name (justification for promotion, proposed uses)

**Category C — Keep in Module:**
- Field Name (reason for keeping)

---

## Common Patterns

### Generic Core Patterns
These concepts typically belong in Core:

- **Rating/Assessment Scales:** High/Medium/Low, Excellent/Good/Fair/Poor
- **Frequency/Recurrence:** Daily, Weekly, Monthly, Quarterly, Annual
- **Proficiency/Skill Levels:** Beginner, Intermediate, Advanced, Expert
- **Education Levels:** High School, Associate, Bachelor, Master, Doctoral
- **Delivery/Participation Modes:** In Person, Virtual, Hybrid, Remote
- **Priority Levels:** Low, Medium, High, Critical
- **Status Categories:** Active, Inactive, Pending, Suspended (when generic)
- **Scope Descriptors:** Local, Regional, State, National, International
- **Result/Outcome Types:** Pass/Fail, Met/Not Met, Approved/Rejected

### Module-Specific Patterns
These typically stay in modules:

- **Process Stage Values:** Specific workflow steps (e.g., "Voir Dire", "Sentencing")
- **Category Types:** Domain classifications (e.g., "Motion Type", "Interview Type")
- **Specialized Terminology:** Industry/domain-specific terms
- **Workflow-Dependent Values:** Steps tied to specific business processes
- **Role/Function Types:** Module-specific roles (e.g., "Party Role in Court Case")

---

## Examples by Domain

### Example 1: Education/Training Choice Fields

**Choice Field:** Training Delivery Method
**Values:** In Person, Virtual, Hybrid, Self-Service, Asynchronous

**Analysis:**
- ✅ Generic concept applicable across domains
- ✅ Already used in Events, could be used in Services, Programs
- ✅ Values are stable and standardized
- ✅ Not training-specific (events, consultations, services all have delivery methods)

**Decision:** Category B — Promote to Core as "Delivery Method"

---

### Example 2: HR/Recruiting Choice Fields

**Choice Field:** Recruiting Interview Type  
**Values:** Phone Screen, Video Interview, Panel Interview, Technical Interview, Case Interview

**Analysis:**
- ❌ "Panel Interview", "Case Interview" are recruiting-specific
- ❌ Other modules don't conduct these types of interviews
- ❌ Values may evolve based on recruiting best practices

**Decision:** Category C — Keep in HR Recruiting Module

---

**Choice Field:** Recruiting Proficiency Level  
**Values:** Beginner, Intermediate, Advanced, Expert, Subject Matter Expert

**Analysis:**
- ✅ Generic skill/competency levels applicable broadly
- ✅ Used in Training, Competency Management, Skill Assessment
- ✅ Stable, widely recognized progression
- ✅ Not recruiting-specific

**Decision:** Category B — Promote to Core (if doesn't already exist)

---

### Example 3: Compliance Choice Fields

**Choice Field:** Inspection Result  
**Values:** Pass, Pass with Conditions, Fail, Incomplete

**Analysis:**
- ✅ Generic outcome/result pattern
- ✅ Similar to Core "Pass Fail Status" but more granular
- ❌ Core has simpler version already

**Decision:** Category A — Use Core "Pass Fail Status" OR Category B if granularity is needed across modules

---

## Implementation Guidelines

### For Category A (Replace with Core)

1. **Update table field definitions** to reference Core field
2. **Remove module-specific definition** from choice fields section
3. **Add note in "Removed" section** documenting what was replaced

**Example:**
```markdown
## Removed Choice Fields

### Assessment Frequency → Replaced with Schedule Frequency (Core)
Previously defined module-specific frequency field; now using Core Schedule Frequency field.
```

### For Category B (Promote to Core)

1. **Verify field doesn't exist in Core** under a different name
2. **Add field definition to Core BUILD.md** in appropriate section
3. **Remove from module** and reference Core version
4. **Document in Core** which modules will use it

**Example in Core:**
```markdown
### Proficiency Level
Standardized skill or competency level descriptors.
Used by: Training, Recruiting, Competency Management, Skill Assessment
- Beginner
- Intermediate
- Advanced
- Expert
- Subject Matter Expert
```

### For Category C (Keep in Module)

1. **Keep definition in module** choice fields section
2. **Ensure naming follows convention** (Module prefix if needed)
3. **Add brief description** of why it's module-specific

**Example:**
```markdown
### Recruiting Interview Type
Types of interviews specific to hiring processes.
Domain-specific to recruiting and talent acquisition.
- Phone Screen
- Panel Interview
- Technical Interview
```

---

## Red Flags & Common Mistakes

### ❌ Don't Promote Based Only on Similar Names
Just because two fields have similar names doesn't mean they're the same concept.

**Example:** "Event Status" in Event Management vs "Status" used generically
- Event Status may have domain-specific values like "Registration Open"
- Generic Status might just be Active/Inactive

### ❌ Don't Over-Generalize
Creating overly generic Core fields that try to cover too many use cases leads to confusion.

**Bad:** A single "Type" field with 50+ values trying to cover all categorization needs  
**Good:** Specific typed fields (Event Type, Document Type, Agreement Type)

### ❌ Don't Keep Obvious Core Patterns in Modules
Common patterns should be in Core even if currently only used in one module.

**Example:** Priority (Low/Medium/High/Critical) belongs in Core even if only one module uses it initially.

---

## Review Checklist

- [ ] All module choice fields have been compared against Core
- [ ] Category A replacements identified with Core field names
- [ ] Category B promotions justified with 3+ use case examples
- [ ] Category C fields confirmed as domain-specific
- [ ] No duplicate concepts between module and Core
- [ ] Field names follow naming conventions (generic for Core, prefixed for module)
- [ ] Values are appropriate for the scope (generic for Core, specific for module)
