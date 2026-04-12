# Personnel Security Changelog

## Unreleased

## [1.2.0.0] - 2026-04-11

### Added
- Forms: Configured quick create forms for all Personnel Security entities including streamlined field layouts for rapid data entry
- Subgrids: Configured related subgrids for all applicable Personnel Security entities to enable comprehensive related record navigation and management

---

## [1.1.0.0] - 2026-04-07

### Added
- **Personnel Security Module**: 7 entities with 350+ fields supporting comprehensive security vetting from initial review through eligibility management, continuous monitoring, and access credential tracking
  - Security Review & Investigation: Personnel Security Review, Personnel Background Investigation, Personnel Adjudication
  - Eligibility & Monitoring: Personnel Security Eligibility, Personnel Continuous Evaluation, Personnel Reportable Event
  - Access Credentials: Personnel Access Credential
- **Choice Sets**: 33 global option sets including review types, investigation types and tiers, adjudication types and decisions, eligibility types and statuses, reportable event types and categories, credential types and statuses, foreign contact types, financial and legal incident types, biometric types, evaluation frequencies, and workflow stages for reviews, investigations, adjudications, and reportable events
- **Baseline Forms and Views**: Initial configuration for all 7 entities

### Changed
- **Status Field Refactoring**: Replaced 3 legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Completion Status, Item Validation Status, Item Disposition, Issue Resolution Status)
- **Field Clarification**: Personnel Reportable Event "Event Status" renamed to "Stage" to clarify workflow progression vs. resolution outcome

### Removed
- Legacy choice fields: Security Review Status, Security Investigation Status, Security Adjudication Status — replaced with Stage and Core status fields

---
