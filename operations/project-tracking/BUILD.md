# 📋 Project Tracking — Data Model Design

The **Project Tracking** module supports the structured intake, planning, execution, and control of work across initiatives of any size. It enables organizations to capture proposed work through Project Requests, formally manage approved Projects, plan delivery using Backlogs and Iterations, and execute work through categorized Work Items aligned to defined Roles and Resource Assignments. Milestones provide timeline checkpoints, while Change Requests ensure formal governance over scope, schedule, and cost adjustments. This module can be used for IT system implementations, policy initiatives, construction efforts, product development, operational improvements, research programs, or any structured body of work requiring visibility, accountability, and controlled delivery from initiation through completion.

---

## Project Intake & Approval

### Project Request
Represents an intake record used to propose or initiate a new project. Captures initial business need, justification, high-level scope, and evaluation prior to formal project approval.

**Completed:**

**Planned:**
- Name: Text
- Request Number: Text
- Stage: Choice (Project Request Stage)
- Decision Status: Choice (Item Decision Status)
- Request Type: Choice (Project Project Type)
- Request Priority: Choice (Priority)
- Submission Date: Date
- Submission Method: Choice (Method of Contact)
- Submitted By: Lookup (Person)
- Submitting Organization Unit: Lookup (Organization Unit)
- Business Need: Memo
- Problem Statement: Memo
- Proposed Solution: Memo
- Expected Benefits: Memo
- Strategic Alignment: Memo
- Organization Initiative: Lookup (Organization Initiative)
- Estimated Start Date: Date
- Estimated Completion Date: Date
- Estimated Cost: Currency
- Estimated Effort (Hours): Float
- Estimated Resources: Integer
- Requested Budget: Currency
- Funding Source: Text
- Executive Sponsor: Lookup (Person)
- Business Owner: Lookup (Person)
- Technical Contact: Lookup (Person)
- Impact If Not Done: Memo
- Alternative Approaches: Memo
- Dependencies: Memo
- Constraints: Memo
- Assumptions: Memo
- Risk Summary: Memo
- Evaluation Date: Date
- Evaluated By: Lookup (Person)
- Evaluation Score: Integer
- Evaluation Notes: Memo
- Decision Date: Date
- Decided By: Lookup (Person)
- Decision Rationale: Memo
- Approved Project: Lookup (Project)
- Rejection Reason: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

---

## Project Execution

### Project
Represents the primary delivery record for a defined body of work with scope, objectives, schedule, ownership, and overall status. Serves as the parent container for backlog items, iterations, milestones, resources, and change requests.

**Completed:**

**Planned:**
- Name: Text
- Project Code: Text
- Stage: Choice (Project Stage)
- Completion Status: Choice (Item Completion Status)
- Project Type: Choice (Project Project Type)
- Project Health: Choice (Initiative Health)
- Health Summary: Memo
- Parent Project: Lookup (Project)
- Project Request: Lookup (Project Request)
- Organization Initiative: Lookup (Organization Initiative)
- Owning Organization Unit: Lookup (Organization Unit)
- Delivery Organization Unit: Lookup (Organization Unit)
- Project Manager: Lookup (Person)
- Executive Sponsor: Lookup (Person)
- Business Owner: Lookup (Person)
- Technical Lead: Lookup (Person)
- Customer Account: Lookup (Account)
- Vendor Account: Lookup (Account)
- Planned Start Date: Date
- Planned End Date: Date
- Actual Start Date: Date
- Actual End Date: Date
- Forecast Completion Date: Date
- Current Phase: Text
- Lifecycle Stage: Choice (Lifecycle Stage)
- Priority: Choice (Priority)
- Visibility: Choice (Visibility)
- Is Confidential: Yes / No
- Project Objectives: Memo
- Project Scope: Memo
- Success Criteria: Memo
- Key Deliverables: Memo
- Assumptions: Memo
- Constraints: Memo
- Dependencies: Memo
- Approved Budget: Currency
- Budget Spent: Currency
- Budget Remaining: Currency
- Planned Effort (Hours): Float
- Actual Effort (Hours): Float
- Estimated Effort to Complete (Hours): Float
- Percent Complete: Integer
- Schedule Variance (Days): Integer
- Cost Variance: Currency
- Legal Authority: Lookup (Legal Authority)
- Master Agreement: Lookup (Agreement)
- Project Charter: Lookup (Document)
- Project Plan: Lookup (Document)
- Repository URL: Text
- Project Site URL: Text
- Lessons Learned: Memo
- Closeout Summary: Memo
- Notes: Memo

---

### Project Role
Represents standardized roles used within projects (e.g., Project Manager, Business Lead, Technical Lead). Supports consistent staffing structures and reporting.

**Completed:**

**Planned:**
- Name: Text
- Role Code: Text
- Role Category: Choice (Project Role Category)
- Description: Memo
- Responsibilities: Memo
- Standard Allocation Percentage: Integer

---

### Project Resource Assignment
Represents the assignment of a person or resource to a project (and optionally to specific work items), including role, allocation percentage, and assignment duration.

**Completed:**

**Planned:**
- Name: Text
- Assignment Number: Text
- Project: Lookup (Project)
- Assigned Person: Lookup (Person)
- Project Role: Lookup (Project Role)
- Stage: Choice (Project Resource Assignment Stage)
- Assignment Status: Choice (Item Assignment Status)
- Assignment Start Date: Date
- Assignment End Date: Date
- Allocation Percentage: Integer
- Planned Hours: Float
- Actual Hours: Float
- Remaining Hours: Float
- Assigned By: Lookup (Person)
- Assignment Date: Date
- Is Primary: Yes / No
- Is Billable: Yes / No
- Billing Rate: Currency
- Cost Rate: Currency
- Assignment Notes: Memo
- Notes: Memo

---

## Work Planning & Execution

### Project Backlog
Represents a planning container that groups and prioritizes future work items for a project. Used to manage the queue of pending work before assignment to an iteration or execution phase.

**Completed:**

**Planned:**
- Name: Text
- Backlog Code: Text
- Project: Lookup (Project)
- Stage: Choice (Project Backlog Stage)
- Backlog Type: Choice (Project Backlog Type)
- Backlog Owner: Lookup (Person)
- Description: Memo
- Target Iteration: Lookup (Project Iteration)
- Priority: Choice (Priority)
- Notes: Memo

---

### Project Iteration
Represents a defined timebox or execution cycle within a project (e.g., sprint, phase, increment). Used to organize and track work items scheduled for completion during that period.

**Completed:**

**Planned:**
- Name: Text
- Iteration Code: Text
- Project: Lookup (Project)
- Stage: Choice (Project Iteration Stage)
- Iteration Number: Integer
- Parent Iteration: Lookup (Project Iteration)
- Iteration Start Date: Date
- Iteration End Date: Date
- Planned Capacity (Hours): Float
- Committed Work Items: Integer
- Completed Work Items: Integer
- Iteration Goal: Memo
- Iteration Owner: Lookup (Person)
- Velocity: Float
- Burndown Rate: Float
- Review Date: Date
- Review Notes: Memo
- Retrospective Notes: Memo
- Notes: Memo

---

### Project Work Item Type
Represents the configuration table defining categories of work items (e.g., Epic, Feature, Task, Defect). Controls classification, reporting, and workflow behavior for Project Work Items.

**Completed:**

**Planned:**
- Name: Text
- Type Code: Text
- Type Category: Choice (Project Work Item Category)
- Description: Memo
- Icon: Text
- Color: Text
- Default Priority: Choice (Priority)
- Requires Acceptance Criteria: Yes / No
- Allows Time Tracking: Yes / No
- Allows Sub Items: Yes / No

---

### Project Work Item
Represents the core execution record for a unit of work within a project. May represent an epic, feature, task, defect, or other work category as defined by its type.

**Completed:**

**Planned:**
- Name: Text
- Work Item Number: Text
- Project: Lookup (Project)
- Project Work Item Type: Lookup (Project Work Item Type)
- Stage: Choice (Project Work Item Stage)
- Completion Status: Choice (Item Completion Status)
- Work Item Priority: Choice (Priority)
- Parent Work Item: Lookup (Project Work Item)
- Project Backlog: Lookup (Project Backlog)
- Project Iteration: Lookup (Project Iteration)
- Assigned To: Lookup (Person)
- Created By: Lookup (Person)
- Created Date: Date Time
- Owner: Lookup (Person)
- Description: Memo
- Acceptance Criteria: Memo
- Business Value: Integer
- Story Points: Integer
- Effort Estimate (Hours): Float
- Original Estimate (Hours): Float
- Remaining Work (Hours): Float
- Completed Work (Hours): Float
- Target Start Date: Date
- Target Completion Date: Date
- Actual Start Date: Date
- Actual Completion Date: Date
- Due Date: Date
- Blocked: Yes / No
- Blocked Reason: Memo
- Blocked Date: Date
- Severity: Choice (Severity Level)
- Found In Version: Text
- Fixed In Version: Text
- Resolution: Choice (Project Work Item Resolution)
- Resolution Notes: Memo
- Test Status: Choice (Simple Certification Status)
- Verified By: Lookup (Person)
- Verification Date: Date
- Tags: Text
- Discussion: Memo
- Related Risk: Lookup (Risk Item)
- Related Action Item: Lookup (Action Item)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

## Timeline & Change Management

### Project Milestone
Represents a significant event or checkpoint within a project timeline. Represents key delivery dates, approvals, or completion markers used for progress tracking and reporting.

**Completed:**

**Planned:**
- Name: Text
- Milestone Code: Text
- Parent Milestone: Lookup (Project Milestone)
- Project: Lookup (Project)
- Stage: Choice (Project Milestone Stage)
- Milestone Status: Choice (Milestone Status)
- Milestone Type: Choice (Project Milestone Type)
- Milestone Category: Choice (Project Milestone Category)
- Owner: Lookup (Person)
- Description: Memo
- Success Criteria: Memo
- Planned Date: Date
- Baseline Date: Date
- Forecast Date: Date
- Actual Date: Date
- Is Critical Path: Yes / No
- Is Deliverable: Yes / No
- Deliverable Description: Memo
- Requires Approval: Yes / No
- Approver: Lookup (Person)
- Approval Date: Date
- Approval Status: Choice (Approval Status)
- Variance (Days): Integer
- Variance Reason: Memo
- Dependencies: Memo
- Related Work Item: Lookup (Project Work Item)
- Related Document: Lookup (Document)
- Notes: Memo

---

### Project Change Request
Represents a formal proposal to modify approved project scope, schedule, cost, deliverables, or other baseline elements. Tracks impact analysis, review, approval decision, and implementation status.

**Completed:**

**Planned:**
- Name: Text
- Change Request Number: Text
- Project: Lookup (Project)
- Stage: Choice (Project Change Request Stage)
- Decision Status: Choice (Item Decision Status)
- Change Request Type: Choice (Project Change Request Type)
- Change Impact Level: Choice (Degree)
- Requested By: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Request Date: Date
- Required By Date: Date
- Change Description: Memo
- Change Justification: Memo
- Business Impact: Memo
- Risk If Not Approved: Memo
- Affected Work Items: Memo
- Affected Milestones: Memo
- Scope Impact: Memo
- Schedule Impact (Days): Integer
- Cost Impact: Currency
- Resource Impact: Memo
- Quality Impact: Memo
- Impact Analysis Date: Date
- Analyzed By: Lookup (Person)
- Impact Analysis: Memo
- Recommended Action: Memo
- Alternative Options: Memo
- Review Date: Date
- Reviewed By: Lookup (Person)
- Review Notes: Memo
- Decision Date: Date
- Decision: Choice (Approval Status)
- Decision Rationale: Memo
- Approved By: Lookup (Person)
- Implementation Status: Choice (Action Status)
- Implementation Date: Date
- Implemented By: Lookup (Person)
- Implementation Notes: Memo
- Priority: Choice (Priority)
- Supporting Document: Lookup (Document)
- Notes: Memo

## New Choice Fields - Semi-Reviewed

**Planned:**

### Project Type
- IT Implementation
- Infrastructure Project
- Policy Initiative
- Process Improvement
- Product Development
- Construction Project
- Research Project
- Organizational Change
- System Integration
- Maintenance Project
- Compliance Project

### Project Backlog Type
- Product Backlog
- Sprint Backlog
- Release Backlog
- Feature Backlog
- Maintenance Backlog

### Project Work Item Category
- Epic
- Feature
- User Story
- Task
- Defect
- Spike
- Technical Debt
- Documentation

**In Review:**

### Project Work Item Resolution
- Completed
- Fixed
- Verified
- Duplicate
- Won't Fix
- Cannot Reproduce
- By Design
- Deferred

### Project Milestone Type
- Project Start
- Project End
- Phase Gate
- Delivery
- Review
- Approval
- Go Live
- Customer Acceptance

### Project Milestone Category
- Schedule
- Deliverable
- Decision Point
- Funding
- Regulatory
- Contractual

### Project Role Category
- Management
- Leadership
- Technical
- Business
- Support
- Quality
- Subject Matter Expert

### Project Change Request Type
- Scope Change
- Schedule Change
- Budget Change
- Resource Change
- Quality Change
- Risk Response
- Requirement Change
- Technical Change
- Process Change

**New Stage Fields:**

### Project Request Stage
Tracks project request workflow from submission through evaluation to decision.
- Submitted
- Under Review
- Evaluation
- Decision
- Finalized

### Project Stage
Tracks project workflow from approval through planning, execution, and closure.
- Approved
- Planning
- Execution
- Closing
- Closed

### Project Resource Assignment Stage
Tracks resource assignment workflow from proposal through active assignment to completion.
- Proposed
- Confirmed
- Active
- Completed

### Project Backlog Stage
Tracks backlog workflow from planning through active use to archival.
- Planning
- Ready
- Active
- Archived

### Project Iteration Stage
Tracks iteration workflow from planning through execution to completion.
- Planned
- Active
- Completed

### Project Work Item Stage
Tracks work item workflow from creation through development, review, and completion.
- New
- Approved
- In Progress
- Review
- Testing
- Done

### Project Milestone Stage
Tracks milestone workflow and progress toward achievement.
- Planned
- In Progress
- Achieved

### Project Change Request Stage
Tracks change request workflow from submission through review, decision, and implementation.
- Submitted
- Impact Analysis
- Review
- Decision
- Implementation
- Closed

**Removed (Replaced with Stage and Core Status Fields):**

### Project Status → Replaced with Project Stage + Completion Status
Project Status mixed workflow (Proposed, Approved, Planning, In Progress) with work impediments (On Hold), health indicators (At Risk), and outcomes (Completed, Cancelled, Closed). Separated into:
- Project Stage for workflow (Approved → Planning → Execution → Closing → Closed)
- Item Completion Status (Core) for work tracking: Blocked (replaces On Hold)
- Project Health (Core: Initiative Health) for health tracking (On Track, At Risk, Off Track) - already in table
- Item Disposition (Core) for final outcomes: Completed, Canceled

Value mapping:
- Proposed → (removed from Project Status, belongs in Project Request)
- Approved → Stage: Approved
- Planning → Stage: Planning
- In Progress → Stage: Execution
- On Hold → Completion Status: Blocked
- At Risk → Project Health: At Risk (already tracked separately)
- Completed → Stage: Closed + Disposition: Completed
- Cancelled → Disposition: Canceled
- Closed → Stage: Closed

### Project Work Item Status → Replaced with Project Work Item Stage + Completion Status
Project Work Item Status mixed workflow (New, Proposed, Approved, In Progress, In Review, In Testing) with work impediments (Blocked) and outcomes (Completed, Cancelled, Deferred). Separated into:
- Project Work Item Stage for workflow (New → Approved → In Progress → Review → Testing → Done)
- Item Completion Status (Core) for work tracking: Blocked (already has "Blocked: Yes/No" field, Completion Status provides structured tracking)
- Item Disposition (Core) for final outcomes: Completed, Canceled, Deferred

Value mapping:
- New → Stage: New
- Proposed → Stage: New (work items start as New, approval happens via separate decision)
- Approved → Stage: Approved
- In Progress → Stage: In Progress
- In Review → Stage: Review
- In Testing → Stage: Testing
- Blocked → Completion Status: Blocked (supplements existing "Blocked: Yes/No" field)
- Completed → Stage: Done + Disposition: Completed
- Cancelled → Disposition: Canceled
- Deferred → Disposition: Deferred

### Project Backlog Status → Replaced with Project Backlog Stage
Project Backlog Status mixed workflow (Planning, Ready, Active) with outcomes (Archived, Closed). Separated into:
- Project Backlog Stage for workflow (Planning → Ready → Active → Archived)
- Item Disposition (Core) for closure: Completed, Canceled (if needed)

Value mapping:
- Planning → Stage: Planning
- Ready → Stage: Ready
- Active → Stage: Active
- Archived → Stage: Archived
- Closed → Stage: Archived + Disposition: Completed (if distinct from archived)

### Project Iteration Status → Replaced with Project Iteration Stage
Project Iteration Status mixed workflow (Planned, Active) with outcomes (Completed, Cancelled). Separated into:
- Project Iteration Stage for workflow (Planned → Active → Completed)
- Item Disposition (Core) for cancellations: Canceled

Value mapping:
- Planned → Stage: Planned
- Active → Stage: Active
- Completed → Stage: Completed
- Cancelled → Disposition: Canceled

### Project Milestone Status → Replaced with Project Milestone Stage + Milestone Status (Core)
Project Milestone Status mixed tracking status (Planned, On Track, At Risk) with outcomes (Achieved, Missed, Cancelled). Separated into:
- Project Milestone Stage for workflow (Planned → In Progress → Achieved)
- Milestone Status (Core) for progress tracking: Upcoming, Current, On Track, At Risk, Completed On Time, Completed Late, Missed, Cancelled
- Item Disposition (Core) for final outcomes: Completed, Canceled

Value mapping:
- Planned → Stage: Planned + Milestone Status: Upcoming
- On Track → Milestone Status: On Track
- At Risk → Milestone Status: At Risk
- Achieved → Stage: Achieved + Milestone Status: Completed On Time or Completed Late
- Missed → Milestone Status: Missed
- Cancelled → Disposition: Canceled + Milestone Status: Cancelled

**Note:** Core's Milestone Status field provides comprehensive tracking including timing (Upcoming, Current, Completed On Time, Completed Late, Acknowledged, Missed) which is more detailed than the original Project Milestone Status. Using Stage for workflow (Planned → In Progress → Achieved) plus Core Milestone Status for progress tracking provides better state management.

### Project Resource Assignment Status → Replaced with Project Resource Assignment Stage + Assignment Status + Duty Status
Project Resource Assignment Status mixed workflow (Proposed, Confirmed, Active) with assignment states (On Leave) and outcomes (Completed, Withdrawn, Cancelled). Separated into:
- Project Resource Assignment Stage for workflow (Proposed → Confirmed → Active → Completed)
- Item Assignment Status (Core) for assignment acceptance tracking: Unassigned, Assigned, Accepted, Declined
- Duty Status (Core) for active duty tracking: Active, Inactive, Suspended (replaces On Leave)
- Item Disposition (Core) for final outcomes: Completed, Withdrawn, Canceled

Value mapping:
- Proposed → Stage: Proposed + Assignment Status: Assigned
- Confirmed → Stage: Confirmed + Assignment Status: Accepted
- Active → Stage: Active + Duty Status: Active
- On Leave → Duty Status: Inactive or Suspended
- Completed → Stage: Completed + Disposition: Completed
- Withdrawn → Disposition: Withdrawn
- Cancelled → Disposition: Canceled

### Project Request: Approval Status field → Replaced with Project Request Stage + Decision Status
Project Request originally had "Approval Status: Choice (Approval Status)" at the top of the field list and "Decision: Choice (Approval Status)" later in the list. This mixed the overall request workflow state with the formal decision outcome. Separated into:
- Project Request Stage for workflow (Submitted → Under Review → Evaluation → Decision → Finalized)
- Item Decision Status (Core) for decision tracking: Pending, Approved, Rejected, Deferred, Canceled
- Renamed "Approved By" to "Decided By" for clarity

### Project Change Request: Duplicate Action Status field removed
Project Change Request had "Action Status: Choice (Action Status)" listed twice in the table definition (once near the top, once near the bottom). Separated into:
- Project Change Request Stage for workflow (Submitted → Impact Analysis → Review → Decision → Implementation → Closed)
- Item Decision Status (Core) for decision tracking
- Implementation Status: Choice (Action Status) for implementation work tracking (kept as separate concern from stage)
