# Project Tracking Changelog

## [1.2.0.0] - 2026-04-11

### Added
- Forms: Configured quick create forms for all Project Tracking entities including streamlined field layouts for rapid data entry
- Subgrids: Configured related subgrids for all applicable Project Tracking entities to enable comprehensive related record navigation and management

---

## [1.1.0.0] - 2026-04-07

### Added
- **10 entities** with **260+ fields** supporting project lifecycle from intake through execution:
  - Intake and planning entities (Project Request, Project, Project Role, Project Resource Assignment) for governance and staffing
  - Work planning entities (Project Backlog, Project Iteration, Project Work Item Type, Project Work Item) for iterative delivery
  - Timeline and control entities (Project Milestone, Project Change Request) for progress tracking and governance
- **16 choice sets** for project types, work item categories, milestone types, role categories, change request types, and resolutions
- Stage-based workflow patterns for all major entities including Project Request (5 stages), Project (5 stages), Project Work Item (6 stages), Project Change Request (6 stages), and others

### Changed
- **Refactored status fields** to workflow Stage patterns with Core reusable statuses:
  - Project Status → Project Stage + Item Completion Status + Project Health + Item Disposition
  - Project Work Item Status → Project Work Item Stage + Item Completion Status + Item Disposition
  - Project Resource Assignment Status → Project Resource Assignment Stage + Item Assignment Status + Duty Status + Item Disposition
  - Project Request Approval Status → Project Request Stage + Item Decision Status
  - Project Change Request Action Status → Project Change Request Stage + Item Decision Status + Implementation Status
  - Plus similar refactors for Backlog, Iteration, and Milestone status fields

## Unreleased

### Added
- 

### Changed
- 
