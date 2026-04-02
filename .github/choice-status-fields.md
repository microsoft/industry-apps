# Status Fields — Design Guidelines

Status fields capture **semantic state, outcomes, and decision results** of a record, while Stage fields track **workflow progression**. Together, they provide complete state management for transactional records.

---

## Status vs. Stage

| Aspect | **Stage** | **Status** |
|--------|-----------|------------|
| **Purpose** | Where in the workflow | Outcome or semantic state |
| **Values** | Workflow steps (Planning, Submitted, Under Review, Booking) | Results (Approved, Rejected, Validated, Blocked) |
| **Changes** | Sequential, forward-moving through process | Independent state changes based on decisions or conditions |
| **Examples** | Draft → Submitted → Processing → Posted | Pending → Approved, Not Started → Blocked |
| **Domain-Specific** | Yes, tailored to each entity's workflow | No, reusable across modules via Core |

---

## Canonical Status Fields

All canonical Status fields are defined in the **Core module** with the prefix **"Item"**. Use these instead of creating custom status fields.

### Item Lifecycle Status
**When to use:** Track whether a record has entered active workflow and if it's finished.

**Question:** Has this record entered workflow, and is it finished?

**Values:**
- **Draft** — Record is being created but not yet submitted
- **Submitted** — Record has entered the formal workflow
- **Complete** — Record processing is finished

---

### Item Decision Status
**When to use:** Track decision outcomes from approval processes, reviews, or formal determinations.

**Question:** Which decision has been made?

**Values:**
- **Pending** — Awaiting a decision
- **Approved** — Decision maker has approved
- **Rejected** — Decision maker has rejected
- **Deferred** — Decision postponed to later date
- **Canceled** — Decision process stopped

---

### Item Completion Status
**When to use:** Track work progress independent of workflow stage.

**Question:** How far along is the work?

**Values:**
- **Not Started** — No work has begun
- **Planned** — Work is scheduled but not started
- **In Progress** — Work is actively being performed
- **Blocked** — Work cannot proceed due to impediment
- **Completed** — Work is finished

---

### Item Validation Status
**When to use:** Track whether results, outputs, or data have been verified for accuracy or compliance.

**Question:** Has the result been verified?

**Values:**
- **Not Required** — Validation is not needed for this record
- **Pending Validation** — Ready for validation but not yet performed
- **Validated** — Successfully verified and confirmed
- **Failed Validation** — Did not pass verification checks

---

### Item Disposition
**When to use:** Track final outcome or how a record was closed. Typically used with closed/archived records.

**Question:** How did this record end?

**Values:**
- **Completed** — Finished through normal process
- **Accepted** — Accepted as final
- **Rejected** — Rejected and closed
- **Withdrawn** — Removed by submitter/creator
- **Duplicate** — Identified as duplicate of another record
- **Superseded** — Replaced by newer version or record
- **Amended** — Modified and resubmitted
- **Canceled** — Process canceled before completion

---

### Item Assignment Status
**When to use:** Track whether responsibility has been assigned to a person or team.

**Question:** Has responsibility been assigned?

**Values:**
- **Unassigned** — No one assigned yet
- **Assigned** — Assigned to person/team but not acknowledged
- **Accepted** — Assignee has accepted responsibility
- **Declined** — Assignee has declined responsibility

---

### Item Readiness Status
**When to use:** Assess preparedness for an event, inspection, audit, or milestone.

**Question:** How ready is the subject being assessed?

**Values:**
- **Fully Ready** — Completely prepared and ready
- **Partially Ready** — Some preparation complete, more needed
- **Marginally Ready** — Minimal preparation, significant gaps remain
- **Not Ready** — Unprepared

---

### Item Performance Rating
**When to use:** Evaluate performance against standards or expectations.

**Question:** How well did this meet standards?

**Values:**
- **Exceeds Standards** — Performance surpasses expectations
- **Meets Standards** — Performance meets expectations
- **Partially Meets Standards** — Some standards met, others not
- **Does Not Meet Standards** — Performance below expectations
- **Needs Improvement** — Requires corrective action

---

### Item Acceptance Status
**When to use:** Track acceptance decisions for deliverables, proposals, or submissions.

**Question:** Has this been accepted?

**Values:**
- **Pending** — Awaiting acceptance review
- **Accepted** — Accepted without modification
- **Accepted with Modifications** — Accepted with required changes
- **Rejected** — Not accepted
- **Deferred** — Acceptance decision postponed

---

## Implementation Guidelines

### 1. When to Add Status Fields
- **Transactional records with decisions:** Use Item Decision Status or Item Acceptance Status
- **Work-oriented records:** Use Item Completion Status
- **Records requiring verification:** Use Item Validation Status
- **Records with final outcomes:** Use Item Disposition
- **Records with assignments:** Use Item Assignment Status
- **Assessment/evaluation records:** Use Item Readiness Status or Item Performance Rating

### 2. Multiple Status Fields
A single table may use **multiple Status fields** when tracking different dimensions:

**Example: Training Session**
- Stage: Choice (Training Session Stage) — workflow steps
- Completion Status: Choice (Item Completion Status) — track work progress
- Readiness Status: Choice (Item Readiness Status) — assess preparation
- Decision Status: Choice (Item Decision Status) — track approval outcome

### 3. Status without Stage
Configuration tables and reference data typically use Status fields **without Stage**:
- **Example:** Credential Type, Organization Unit Type, Compliance Framework Category
- These don't have workflows, but may track Item Lifecycle Status (Draft, Published, Complete)

### 4. Stage without Status
Simple workflow records may use **Stage alone** when semantic state is implicit:
- **Example:** Travel Segment with stages: Planned → Booking → Reserved → Confirmed → In Progress → Completed
- The Stage value itself conveys sufficient state information

### 5. Field Placement in Table Definitions
Place Status fields **after Stage** in the Planned section:

```
- Name: Text
- Record Number: Text
- Organization Unit: Lookup (Organization Unit)
- Stage: Choice (Training Session Stage)
- Completion Status: Choice (Item Completion Status)
- Decision Status: Choice (Item Decision Status)
- Priority: Choice (Priority)
```

### 6. Do Not Create Custom Status Fields
❌ **Don't create:**
- Course Status
- Application Status  
- Assessment Status
- Verification Status

✅ **Instead use:**
- Item Lifecycle Status
- Item Decision Status
- Item Completion Status
- Item Validation Status

---

## Common Patterns

### Approval Workflow Pattern
```
Stage: Draft → Submitted → Under Review → Processing → Finalized
Decision Status: Pending → Approved/Rejected/Deferred
```

### Work Execution Pattern
```
Stage: Planning → Assigned → Execution → Review → Closed
Completion Status: Not Started → In Progress → Blocked/Completed
Assignment Status: Unassigned → Assigned → Accepted
```

### Submission and Validation Pattern
```
Stage: Draft → Submitted → Validation → Published
Lifecycle Status: Draft → Submitted → Complete
Validation Status: Pending Validation → Validated/Failed Validation
```

### Final Disposition Pattern
```
Stage: [reaches final stage] → Closed
Disposition: Completed/Accepted/Rejected/Withdrawn/Canceled
```

---

## Review Checklist

When designing tables with Status/Stage fields:

- [ ] Does this table represent a transactional record with a workflow? → Add **Stage**
- [ ] Are there decision outcomes to track? → Add **Item Decision Status**
- [ ] Does work need to be completed? → Add **Item Completion Status**
- [ ] Are assignments involved? → Add **Item Assignment Status**
- [ ] Does validation occur? → Add **Item Validation Status**
- [ ] Is there a final outcome to record? → Add **Item Disposition**
- [ ] Is readiness being assessed? → Add **Item Readiness Status**
- [ ] Is performance being evaluated? → Add **Item Performance Rating**
- [ ] Are deliverables being accepted? → Add **Item Acceptance Status**
- [ ] Have I avoided creating custom status fields?
- [ ] Are Stage values workflow steps, not outcomes?
- [ ] Are Status fields referencing Core "Item" choice fields?
