# Programs and Services Changelog

## [1.1.0.0] - 2026-04-07

### Added
- **11 entities** with **197+ fields** supporting program and service delivery lifecycle:
  - Program and Service structure entities (Program, Service, Service Category, Service Offering) for strategic organization
  - Eligibility management entities (Service Eligibility Rule, Service Offering Eligibility Rule, Service Offering Geography) for qualification logic
  - Service delivery entities (Service Participation, Service Activity, Service Result, Service Result Type) for operational execution
- **12 choice sets** for program types, service types, eligibility rules, activity tracking, and result classification
- Stage-based workflow patterns for Service Offerings (6 stages: Planning → Ready → Enrollment → Closed Enrollment → Active → Finalized), Service Participation (5 stages: Application → Enrolled → Active → Completed → Terminated), and Service Results (4 stages: Pending → Determined → Issued → Final)

### Changed
- **Refactored status fields** to workflow Stage patterns with Core reusable statuses:
  - Service Offering Status → Service Offering Stage + Item Completion Status + Item Disposition + Publication Status
  - Service Result Status → Service Result Stage + Appeal Status + Item Disposition (with Service Result Category and Service Result Type distinguishing outcome types)
- **Promoted Delivery Method** to Core scope (formerly Service Delivery Method) for reuse across service delivery, training, support, and customer service contexts

## Unreleased

### Added
- 

### Changed
- 
