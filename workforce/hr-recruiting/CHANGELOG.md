# HR Recruiting Changelog

## Unreleased

## [1.1.0.0] - 2026-04-07

### Added
- **HR Recruiting Module**: 14 entities with 290+ fields supporting end-to-end hiring lifecycle from workforce planning through offer acceptance
  - Workforce Planning & Requisitions: HR Workforce Request, HR Requisition, HR Requisition Posting, HR Requisition Requirement
  - Candidate & Application Management: HR Candidate, HR Application, HR Application Skill Assessment, HR Application Evaluation
  - Interview & Evaluation: HR Interview, HR Evaluation
  - Selection & Offer: HR Selection Decision, HR Offer, HR Pre-Hire Requirement
- **Choice Sets**: 25 global option sets including request types, posting channels, requirement types, candidate sources, interview types, hiring recommendations, evaluation categories, offer responses, pre-hire requirement types, and workflow stages for requisitions, applications, interviews, and offers
- **Baseline Forms and Views**: Initial configuration for all 14 entities

### Changed
- **Status Field Refactoring**: Replaced 7 legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Decision Status, Item Completion Status)
- **Core Field Promotion**: Promoted 4 recruiting-specific choice fields to Core for broader reuse (Proficiency Level, Education Level, Overall Rating, Attendance Status)

### Removed
- Legacy choice fields: Recruiting Candidate Status, Recruiting Application Status, Recruiting Interview Status, Recruiting Decision Status, Recruiting Offer Status, Recruiting Requirement Status, Recruiting Requisition Status — replaced with Stage and Core status fields

---
