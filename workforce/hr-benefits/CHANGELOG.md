# HR Benefits Changelog

## Unreleased

## [1.2.0.0] - 2026-04-11

### Added
- Forms: Configured quick create forms for all HR Benefits entities including streamlined field layouts for rapid data entry
- Subgrids: Configured related subgrids for all applicable HR Benefits entities to enable comprehensive related record navigation and management

---

## [1.1.0.0] - 2026-04-07

### Added
- **HR Benefits Module**: 17 entities with 280+ fields supporting complete benefit lifecycle from plan design through enrollment, life events, and claims processing
  - Plan Configuration: HR Benefit Plan, HR Benefit Option, HR Benefit Coverage Level, HR Benefit Provider, HR Benefit Plan Document
  - Eligibility & Enrollment Periods: HR Benefit Eligibility Rule, HR Benefit Waiting Period, HR Benefit Enrollment Period
  - Enrollment & Elections: HR Benefit Enrollment, HR Benefit Election, HR Benefit Beneficiary
  - Life Events & Changes: HR Benefit Life Event, HR Benefit Life Event Change
  - Cost & Contribution Management: HR Benefit Contribution Rate, HR Benefit Cost Allocation, HR Benefit Deduction Code
  - Claims & Reimbursements: HR Benefit Claim
- **Choice Sets**: 25 global option sets including benefit categories, coverage types, provider types, eligibility rules, enrollment types, life event types, contribution types, claim types, and workflow stages for enrollments, life events, and claims
- **Baseline Forms and Views**: Initial configuration for all 17 entities

### Changed
- **Status Field Refactoring**: Replaced 6 legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Term Status, Item Decision Status, Item Validation Status, Item Disposition, Payment Status)

### Removed
- Legacy choice fields: Benefits Period Status, Benefits Enrollment Status, Benefits Event Status, Benefits Verification Status, Benefits Claim Status, Benefits Payment Status — replaced with Stage and Core status fields

---
