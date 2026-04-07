# Dispute Resolution Changelog

## Unreleased

## [1.1.0.0] - 2026-04-07

### Added
- **Dispute Resolution Module**: 13 entities with 148+ fields covering complete lifecycle from intake through investigation, mediation, determination, and appeals
  - Core entities: Dispute, Dispute Intake, Dispute Issue, Dispute Investigation, Dispute Finding
  - Process entities: Dispute Mediation, Dispute Appeal, Dispute Determination, Dispute Corrective Action
  - Supporting entities: Dispute Party, Dispute Evidence, Dispute Interview, Dispute Referral
- **Choice Sets**: 17 global option sets including workflow stages for each process (Intake, Investigation, Mediation, Appeal, Determination, Referral), dispute types, evidence categories, investigation types, party roles, and outcome types
- **Baseline Forms and Views**: Initial configuration for all 13 entities

### Changed
- **Status Field Refactoring**: Replaced 8 legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Decision Status, Item Completion Status, Item Disposition, Finding Result)

### Removed
- Legacy choice fields: Dispute Status, Dispute Appeal Status, Dispute Corrective Action Status, Dispute Intake Status, Dispute Investigation Status, Dispute Mediation Status, Dispute Referral Status, Dispute Finding Type — replaced with Stage and Core status fields

---
