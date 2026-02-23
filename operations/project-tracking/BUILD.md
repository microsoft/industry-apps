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
- Request Status: Choice (Request Status)
- Request Type: Choice (Project Type)
- Request Priority: Choice (Request Priority)
- Submission Date: Date
- Submission Method: Choice (Method of Receipt)
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
- Decision: Choice (Approval Status)
- Decision Rationale: Memo
- Approved By: Lookup (Person)
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
- Project Status: Choice (Project Status)
- Project Type: Choice (Project Type)
- Project Health: Choice (Project Health)
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
- Role Category: Choice (Role Category)
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
- Assignment Status: Choice (Resource Assignment Status)
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
- Backlog Status: Choice (Backlog Status)
- Backlog Type: Choice (Backlog Type)
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
- Iteration Status: Choice (Iteration Status)
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
- Type Category: Choice (Work Item Category)
- Description: Memo
- Icon: Text
- Color: Text
- Default Priority: Choice (Work Item Priority)
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
- Work Item Status: Choice (Work Item Status)
- Work Item Priority: Choice (Work Item Priority)
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
- Resolution: Choice (Work Item Resolution)
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
- Milestone Status: Choice (Milestone Status)
- Milestone Type: Choice (Milestone Type)
- Milestone Category: Choice (Milestone Category)
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
- Change Request Status: Choice (Action Status)
- Change Request Type: Choice (Change Request Type)
- Change Impact Level: Choice (Change Impact Level)
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

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Project managers, sponsors, business owners, technical leads, resource assignments, work item assignees.

### Organization Unit *(Core)*
Owning units, delivery units, requesting units.

### Organization Initiative *(Core)*
Strategic alignment for projects and requests.

### Account *(Core)*
Customer accounts, vendor accounts, partner organizations.

### Action Item *(Core)*
Tasks related to projects, milestones, and work items.

### Risk Item *(Core)*
Project risks linked to work items and change requests.

### Agreement *(Core)*
Master agreements, contracts, SOWs for projects.

### Legal Authority *(Core)*
Regulatory requirements for projects.

### Document *(Core)*
Project charters, plans, deliverables, supporting documentation.

---

## New Choice Fields

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

### Project Status
- Proposed
- Approved
- Planning
- In Progress
- On Hold
- At Risk
- Completed
- Cancelled
- Closed

### Project Health
- Healthy
- At Risk
- Off Track
- Critical
- On Hold
- Unknown

### Request Priority
- Critical
- High
- Medium
- Low
- Future Consideration

### Backlog Status
- Planning
- Ready
- Active
- Archived
- Closed

### Backlog Type
- Product Backlog
- Sprint Backlog
- Release Backlog
- Feature Backlog
- Maintenance Backlog

### Iteration Status
- Planned
- Active
- Completed
- Cancelled

### Work Item Category
- Epic
- Feature
- User Story
- Task
- Defect
- Spike
- Technical Debt
- Documentation

### Work Item Status
- New
- Proposed
- Approved
- In Progress
- In Review
- In Testing
- Blocked
- Completed
- Cancelled
- Deferred

### Work Item Priority
- Critical
- High
- Medium
- Low

### Work Item Resolution
- Completed
- Fixed
- Verified
- Duplicate
- Won't Fix
- Cannot Reproduce
- By Design
- Deferred

### Milestone Status
- Planned
- On Track
- At Risk
- Achieved
- Missed
- Cancelled

### Milestone Type
- Project Start
- Project End
- Phase Gate
- Delivery
- Review
- Approval
- Go Live
- Customer Acceptance

### Milestone Category
- Schedule
- Deliverable
- Decision Point
- Funding
- Regulatory
- Contractual

### Resource Assignment Status
- Proposed
- Confirmed
- Active
- On Leave
- Completed
- Withdrawn
- Cancelled

### Role Category
- Management
- Leadership
- Technical
- Business
- Support
- Quality
- Subject Matter Expert

### Change Request Type
- Scope Change
- Schedule Change
- Budget Change
- Resource Change
- Quality Change
- Risk Response
- Requirement Change
- Technical Change
- Process Change

### Change Impact Level
- Minor
- Moderate
- Significant
- Major
- Critical
