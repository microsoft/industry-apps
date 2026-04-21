# Business Process Simulation

A tool for generating realistic test data by simulating business workflows with persona-driven decision-making.

## Overview

The Process Simulation system allows you to:

1. **Define reusable business processes** - Step-by-step workflows for common business scenarios
2. **Create test scenarios** - Specific contexts and personas for running processes
3. **Generate event streams** - Use GitHub Copilot to simulate process execution with realistic data
4. **Inspect and validate** - Review generated steps before execution
5. **Replay to Dataverse** - Execute event streams to create actual records via Web API

## Workflow

```
1. Generate Data Models (auto from Entity.xml)
   ↓
2. Create Process Definitions (manual YAML)
   ↓
3. Create Scenario Definitions (manual YAML)
   ↓
4. Generate Event Stream (GitHub Copilot in VS Code)
   ↓
5. Import Event Stream (paste YAML into UI)
   ↓
6. Dry-Run Validation (validate without executing)
   ↓
7. Execute (create records in Dataverse)
```

## Directory Structure

Each module has a `design/` folder with four sub-folders:

```
<module>/
  design/
    data-models/        # Auto-generated table schemas (one file per table)
      court-case.yaml
      court-case-party.yaml
      court-case-hearing.yaml
    processes/          # Business process definitions
      file-court-case.yaml
      assign-case-officer.yaml
    scenarios/          # Test scenarios with personas
      small-claims-dispute.yaml
      criminal-case-filing.yaml
    event-streams/      # Generated execution traces
      small-claims-001.yaml
      criminal-case-001.yaml
```

---

## File Format Specifications

### 1. Data Models (Auto-Generated)

**Location**: `<module>/design/data-models/*.yaml` (one file per table)

**Purpose**: Reference documentation for available tables and fields. Auto-generated from Entity.xml files.

**Schema** (per table file):
```yaml
name: Court Case
schema_name: appbase_CourtCase
description: >
  The primary record representing a legal matter before the court.
  Tracks case number, type, jurisdiction, status, assigned judge, and overall lifecycle of the matter.

fields:
  - Case Number: Text; appbase_casenumber
  - Case Title: Text; appbase_casetitle
  - Case Type: Choice; appbase_casetype
  - Filing Date: Date Time; appbase_filingdate
  - Assigned Judge: Lookup (Contact); appbase_assignedjudge
  - Court Location: Lookup (appbase_Location); appbase_courtlocation
  - Description: Memo; appbase_description
```

**Field Format**: Each field is formatted as `Display Name: Type; schema_name`
- Standard types: Text, Memo, Integer, Decimal, Currency, Date Time, Choice, Yes / No
- Lookup format: `Lookup (Target Table Name)` where target is identified from relationship files

**Generation**:
- Command: `python ui-tools/scripts/data_model_generator.py <module-path>`
- UI: Click "Generate Data Models" button
- Automatically reads descriptions from BUILD.md
- Parses relationship XML files to determine lookup targets
- Deletes old `entities.yaml` if present
        target_entity: appbase_courtcase
      
      - logical_name: appbase_partytype
        display_name: Party Type
        type: choice
        required: business_required
        options:
          - value: 147130000
            label: Plaintiff
          - value: 147130001
            label: Defendant
```

**Regeneration**: Use "Refresh Data Models" button in UI to regenerate when entities change.

---

### 2. Process Definitions

**Location**: `<module>/design/processes/<process-name>.yaml`

**Purpose**: Define reusable business workflows with steps and decision points.

**Schema**:
```yaml
process_name: file-new-court-case
display_name: File New Court Case
module: government/court-case-management
description: Complete workflow for filing a new court case including parties and initial documents
version: 1.0

# Personas involved in this process
personas:
  - role: court_clerk
    name: Filing Clerk
    responsibilities:
      - Receive case filing documents
      - Create case record
      - Assign case number
      - Record parties
  
  - role: case_supervisor
    name: Case Supervisor
    responsibilities:
      - Review case assignment criteria
      - Assign cases to judges/officers

# Sequential steps in the process
steps:
  - step: 1
    action: create_court_case
    description: Clerk creates initial court case record
    performed_by: court_clerk
    entities:
      - appbase_courtcase
    required_fields:
      - appbase_name  # Case number
      - appbase_casetype
      - appbase_filingdate
    optional_fields:
      - appbase_description
      - appbase_jurisdiction
    business_rules:
      - Case number follows format: CC-YYYY-NNNN
      - Filing date defaults to today
      - Case type determines downstream processing
  
  - step: 2
    action: add_plaintiff
    description: Clerk adds plaintiff information
    performed_by: court_clerk
    entities:
      - contact  # or create new
      - appbase_courtcaseparty
    required_fields:
      - appbase_courtcase  # Link to step 1
      - appbase_partytype  # = Plaintiff (147130000)
      - appbase_contact    # Link to contact
    business_rules:
      - Must link to existing contact or create new contact first
      - Party type must be Plaintiff
  
  - step: 3
    action: add_defendant
    description: Clerk adds defendant information
    performed_by: court_clerk
    entities:
      - contact
      - appbase_courtcaseparty
    required_fields:
      - appbase_courtcase
      - appbase_partytype  # = Defendant (147130001)
      - appbase_contact
    business_rules:
      - Can have multiple defendants
      - At least one defendant required
  
  - step: 4
    action: assign_case_officer
    description: Supervisor assigns case to officer/judge
    performed_by: case_supervisor
    entities:
      - appbase_courtcase  # Update existing
    required_fields:
      - appbase_assignedto  # Lookup to contact (judge/officer)
    optional_fields:
      - appbase_assignmentdate
      - appbase_assignmentnotes
    business_rules:
      - Assignment based on case type and workload
      - Officer must have appropriate role and availability

# Expected outcomes
outcomes:
  - outcome: success
    description: Case successfully filed with all parties and assignment
    required_records:
      - appbase_courtcase: 1
      - appbase_courtcaseparty: 2+  # At least plaintiff and defendant
  
  - outcome: partial
    description: Case filed but not yet assigned
    required_records:
      - appbase_courtcase: 1
      - appbase_courtcaseparty: 2+

# Variations and decision points
variations:
  - variation: multiple_defendants
    description: Case with multiple defendant parties
    affects_steps: [3]
  
  - variation: organizational_party
    description: Party is organization not individual
    affects_steps: [2, 3]
    notes: Use account entity instead of contact
```

---

### 3. Scenario Definitions

**Location**: `<module>/design/scenarios/<scenario-name>.yaml`

**Purpose**: Specific test scenarios with narrative context for LLM-based event stream generation. Provides realistic business situations to generate test data.

**Schema**:
```yaml
scenario_name: small-claims-dispute
display_name: Small Claims Property Dispute
module: government/court-case-management
process: court-case-lifecycle
version: "1.0"

# Scenario description (2-3 paragraphs with all context)
description: >
  This scenario involves a small claims civil dispute between two neighbors in Municipal District 5.
  Ms. Sarah Johnson is filing a case against her neighbor Mr. Robert Chen over property damage.
  Sarah claims that when Robert hired a tree removal service to cut down a large oak tree on his
  property at 125 Oak Street, the work caused significant damage to the shared fence between their
  properties. She is seeking $2,500 for fence repair and replacement costs. Robert maintains that
  the tree removal was necessary for safety reasons after the tree showed signs of disease.
  
  The case is filed by Maria Rodriguez, an experienced court clerk with 5 years on the job, during
  a busy morning where she has already processed 12 other cases. She works efficiently but carefully,
  ensuring all filing requirements are met including proper fee collection and document validation.
  The case number assigned is CC-2026-1547, filed on April 15, 2026 at 9:30 AM.
  
  The case is reviewed later that day by Case Supervisor James Patterson, who has 15 years of
  experience and is known for his methodical approach to following assignment rules. He assigns
  the case to Judge Milton Hayes, who specializes in small claims matters and currently has the
  lowest caseload in that category. This is a straightforward small claims case with low complexity,
  expected to proceed through the standard court case lifecycle without requiring any special
  variations or emergency procedures.

# Data generation hints for LLM
generation_hints:
  - Use realistic timestamps showing progression through a single business day
  - Clerk works quickly but carefully - show realistic data entry patterns
  - Include minor realistic variations in data formatting (abbreviations, capitalization)
  - Supervisor should include brief assignment notes referencing workload balancing
  - All contact information should be realistic but clearly test data
  - Small claims cases typically move faster than complex litigation
  - Keep monetary amounts and dates consistent with narrative details
```

**Key Principles**:
- **Natural language focus**: Description contains all context in prose form for LLM consumption
- **No rigid structure**: Avoid domain-specific keys (parties, plaintiff, etc.) for maximum reusability across modules
- **Rich narrative**: Include personalities, working conditions, timing, and realistic details
- **Generation hints**: Guide the LLM on realistic data patterns and constraints
- **Module-agnostic**: Format works across different business domains (court cases, HR, assets, etc.)

---

### 4. Event Streams (LLM-Generated)

**Location**: `<module>/design/event-streams/<stream-name>.yaml`

**Purpose**: Step-by-step execution trace generated by Copilot based on process + scenario.

**Schema**:
```yaml
event_stream_name: small-claims-001
display_name: Small Claims Dispute - Johnson v. Chen
module: government/court-case-management
based_on_process: file-new-court-case
based_on_scenario: small-claims-dispute
generated: 2026-04-12T14:30:00Z
generated_by: github-copilot

# Execution metadata
execution:
  dry_run_only: false
  clear_before_run: true  # Delete existing test records
  stop_on_error: true

# Sequential operations/events
events:
  # Event 1: Create court case
  - event_id: 1
    timestamp: 2026-04-15T09:30:00Z
    operation: create
    entity: appbase_courtcase
    performed_by: Maria Rodriguez (court_clerk)
    
    # Persona's thought process (optional, for inspection)
    reasoning: >
      Filing clerk Maria receives the case filing documents from Sarah Johnson.
      She creates a new case record, assigns the next available case number
      following the CC-2026-#### format. It's a straightforward civil small
      claims case, so she selects Civil case type and enters today's date
      as filing date. She adds a clear description based on the filing docs.
    
    # Field values to create
    fields:
      appbase_name: CC-2026-1547
      appbase_casetype: 147130000  # Civil
      appbase_filingdate: 2026-04-15T09:30:00Z
      appbase_description: Property damage claim - fence damage from tree removal
      appbase_jurisdiction: Municipal District 5
      statuscode: 1  # Active
    
    # Store created record ID for later reference
    store_as: court_case_record

  # Event 2: Create/lookup plaintiff contact
  - event_id: 2
    timestamp: 2026-04-15T09:32:00Z
    operation: create
    entity: contact
    performed_by: Maria Rodriguez (court_clerk)
    
    reasoning: >
      Maria enters plaintiff Sarah Johnson's contact information.
      She checks for existing contact but doesn't find one, so creates new.
      She carefully enters the contact details from the filing documents.
    
    fields:
      firstname: Sarah
      lastname: Johnson
      emailaddress1: sarah.johnson@email.com
      telephone1: 555-0123
      address1_line1: 123 Oak Street
      appbase_contacttype: 147130000  # Individual (if such field exists)
    
    store_as: plaintiff_contact

  # Event 3: Create plaintiff party record
  - event_id: 3
    timestamp: 2026-04-15T09:33:00Z
    operation: create
    entity: appbase_courtcaseparty
    performed_by: Maria Rodriguez (court_clerk)
    
    reasoning: >
      Now Maria links Sarah Johnson as the plaintiff. She creates a court case
      party record with Party Type set to Plaintiff and links both the court
      case and the contact record.
    
    fields:
      appbase_name: Sarah Johnson - Plaintiff
      appbase_CourtCase@odata.bind: "/appbase_courtcases({{court_case_record.id}})"
      appbase_Contact@odata.bind: "/contacts({{plaintiff_contact.id}})"
      appbase_partytype: 147130000  # Plaintiff
    
    store_as: plaintiff_party

  # Event 4: Create defendant contact
  - event_id: 4
    timestamp: 2026-04-15T09:35:00Z
    operation: create
    entity: contact
    performed_by: Maria Rodriguez (court_clerk)
    
    reasoning: >
      Maria enters defendant Robert Chen's information. Again, no existing
      contact found, so she creates a new contact record. She notes both
      parties live on the same street as neighbors.
    
    fields:
      firstname: Robert
      lastname: Chen
      emailaddress1: robert.chen@email.com
      telephone1: 555-0456
      address1_line1: 125 Oak Street
      appbase_contacttype: 147130000  # Individual
    
    store_as: defendant_contact

  # Event 5: Create defendant party record
  - event_id: 5
    timestamp: 2026-04-15T09:36:00Z
    operation: create
    entity: appbase_courtcaseparty
    performed_by: Maria Rodriguez (court_clerk)
    
    reasoning: >
      Maria creates the defendant party record for Robert Chen, linking
      him to the case with Party Type set to Defendant. The case filing
      is now complete with both parties recorded.
    
    fields:
      appbase_name: Robert Chen - Defendant
      appbase_CourtCase@odata.bind: "/appbase_courtcases({{court_case_record.id}})"
      appbase_Contact@odata.bind: "/contacts({{defendant_contact.id}})"
      appbase_partytype: 147130001  # Defendant
    
    store_as: defendant_party

  # Event 6: Assign case officer
  - event_id: 6
    timestamp: 2026-04-15T11:15:00Z
    operation: update
    entity: appbase_courtcase
    record_reference: "{{court_case_record.id}}"
    performed_by: James Patterson (case_supervisor)
    
    reasoning: >
      Later in the morning, supervisor James Patterson reviews new filings
      for assignment. He sees this is a small claims civil case under $5K.
      He checks current caseloads for small claims specialists and assigns
      it to Judge Milton Hayes who has the lightest small claims load and
      specializes in property disputes. He adds a note about the assignment.
    
    fields:
      appbase_AssignedTo@odata.bind: "/contacts(lookup:milton.hayes@court.gov)"  # Or use existing ID
      appbase_assignmentdate: 2026-04-15T11:15:00Z
      appbase_assignmentnotes: Assigned to Judge Hayes - small claims property dispute specialty
      statuscode: 2  # Assigned
    
    store_as: null  # Updating existing record

# Summary of what was created
summary:
  total_events: 6
  records_created:
    appbase_courtcase: 1
    contact: 2
    appbase_courtcaseparty: 2
  records_updated:
    appbase_courtcase: 1
  estimated_duration: 1h 45m
  process_completed: true
  variations_used: []
```

---

## Template Variable Syntax

Event streams use template variables to reference previously created records:

### Basic Syntax
```yaml
# Reference the ID of a stored record
field_name@odata.bind: "/entityplural({{store_name.id}})"

# Reference any field from a stored record
field_name: "{{store_name.field_name}}"

# Use in strings
description: "Case for {{plaintiff_contact.firstname}} {{plaintiff_contact.lastname}}"
```

### Lookup Values
```yaml
# Option 1: Reference created record
appbase_Contact@odata.bind: "/contacts({{plaintiff_contact.id}})"

# Option 2: Use query to lookup existing record
appbase_AssignedTo@odata.bind: "/contacts(lookup:milton.hayes@court.gov)"

# Option 3: Use known GUID
appbase_AssignedTo@odata.bind: "/contacts(12345678-1234-1234-1234-123456789012)"
```

### Execution Behavior
- The execution engine tracks all `store_as` values
- Before executing each event, it substitutes template variables
- Lookups prefixed with `lookup:` are resolved via Web API query
- If a template variable fails to resolve, execution stops with error

---

## Using the System

### 1. Generate Data Models

In the Process Simulation UI:
1. Select a module
2. Click "Refresh Data Models" on the Data Models tab
3. System reads all Entity.xml files and generates individual table YAML files
4. Review the generated fields and types

### 2. Create a Process Definition

1. Open the Processes tab
2. Click "New Process"
3. Fill in YAML following the schema above
4. Save the file (stored in `<module>/design/processes/`)

### 3. Create a Scenario

1. Open the Scenarios tab
2. Click "New Scenario"
3. Reference an existing process
4. Define personas, context, and test data
5. Save the file

### 4. Generate Event Stream (VS Code)

1. Open the process YAML file in VS Code
2. Open the scenario YAML file in VS Code
3. In Copilot Chat, prompt:
   ```
   Based on the process definition in [process file] and the scenario
   in [scenario file], generate a complete event stream following the
   event stream schema in ui-tools/PROCESS_SIMULATION.md. Include
   realistic timestamps, persona reasoning for each step, and proper
   template variable references for lookups.
   ```
4. Copy the generated YAML

### 5. Import and Validate Event Stream

1. Return to Process Simulation UI
2. Open Event Streams tab
3. Click "Import Event Stream"
4. Paste the Copilot-generated YAML
5. Save the file
6. Click "Dry Run" to validate
7. Review validation results

### 6. Execute Event Stream

1. After successful dry-run
2. Click "Execute"
3. Watch progress as each event is processed
4. Review execution results
5. Check created records in Dataverse

---

## Best Practices

### Process Definitions
- Keep processes focused on a single cohesive workflow
- Document business rules clearly
- Include all required and optional fields
- Define realistic personas with varied experience levels

### Scenario Definitions
- Make context rich and specific
- Use realistic names, dates, and values
- Include personality traits and working conditions for personas
- Provide generation hints for Copilot

### Event Streams
- Include persona reasoning to make streams understandable
- Use realistic timestamps showing process flow
- Store intermediate records for reference
- Test with dry-run before executing
- Clear old test data before running

### Data Generation with Copilot
- Provide both process and scenario files as context
- Ask for complete event streams, not partial
- Request realistic variation in data entry patterns
- Have Copilot explain persona decision-making

---

## Troubleshooting

### Validation Errors
- **Invalid entity**: Check logical_name in data-models.yaml
- **Invalid field**: Verify field exists in entity schema
- **Invalid choice value**: Check option set values in data-models.yaml
- **Missing required field**: Review entity schema for required_level
- **Invalid lookup reference**: Ensure template variable was stored in prior event

### Execution Errors
- **Template substitution failed**: Check store_as names match references
- **Lookup not found**: Verify lookup query or GUID is correct
- **Permission denied**: Check Dataverse user permissions
- **Validation failed**: Required field missing or invalid data type

### Performance
- **Slow execution**: Reduce number of events, or batch operations
- **Timeout**: Split large event streams into multiple files
- **Dry-run slow**: Data models may need refresh

---

## Future Enhancements

Potential features for future versions:
- Cross-module processes (reference entities from multiple modules)
- Rollback/cleanup on execution failure
- Batch execution of multiple event streams
- Event stream templates (reusable partial streams)
- Variable substitution from external data sources
- Integration with existing data-generator JSON files
- Automated scenario generation from process definitions
- Direct Copilot API integration (generate in-app)
