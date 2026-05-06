# Operational Excellence Changelog

## Unreleased

## [1.2.1.0] - 2026-05-06

### Added
- Icons: Assigned custom table icons for all Operational Excellence entities

---

## [1.2.0.0] - 2026-04-11

### Added
- Forms: Configured quick create forms for all Operational Excellence entities including streamlined field layouts for rapid data entry
- Subgrids: Configured related subgrids for all applicable Operational Excellence entities to enable comprehensive related record navigation and management

---

## [1.1.0.0] - 2026-04-07

### Added
- **Operational Excellence Module**: 12 entities with 290+ fields supporting incident management, inspections, exercises, readiness assessments, findings, recommendations, and operational impact reporting
  - Incident Management: Operational Incident
  - Inspection Management: Operational Item, Operational Inspection
  - Operational Events & Exercises: Operational Event, Operational Event Objective, Operational Event Outcome, Operational Event Participant
  - Readiness Assessment: Operational Readiness Assessment
  - Findings & Recommendations: Operational Finding, Operational Recommendation
  - Operational Impact Reporting: Operational Impact
- **Choice Sets**: 22 global option sets including incident types, inspection types, event types, readiness assessment types, finding types, recommendation types, impact types, improvement areas, innovation categories, participant roles, and workflow stages for incidents, inspections, events, assessments, findings, recommendations, and impacts
- **Baseline Forms and Views**: Initial configuration for all 12 entities

### Changed
- **Status Field Refactoring**: Replaced legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Decision Status, Item Acceptance Status, Action Status, Compliance Status, Overall Result, Item Readiness Status, Item Performance Rating, Objective Result)
- **Field Refinement**: Operational Impact Review Status replaced with Item Decision Status for consistency with Core decision-tracking patterns

### Removed
- Legacy choice fields: Operational Impact Review Status — replaced with Item Decision Status

---
