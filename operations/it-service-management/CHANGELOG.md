# IT Service Management Changelog

## Unreleased

## [1.2.0.0] - 2026-04-11

### Added
- Forms: Configured quick create forms for all IT Service Management entities including streamlined field layouts for rapid data entry
- Subgrids: Configured related subgrids for all applicable IT Service Management entities to enable comprehensive related record navigation and management

---

## [1.1.0.0] - 2026-04-07

### Added
- **IT Service Management Module**: 18 entities with 340+ fields supporting service delivery, access management, system inventory, technology governance, and compliance oversight
  - Service Request Management: IT Service Request, IT Service Request Item
  - Access Management: IT Access Request, IT Access Request Item, IT Entitlement, IT Entitlement Assignment
  - IT Service Catalog: IT Catalog Item, IT Catalog Item Technology
  - System & Component Management: IT System, IT System Component, IT System Component Type, IT System Technology
  - Technology Management: IT Technology, IT Technology Type
  - Hosting & Infrastructure: IT Hosting Location
  - Compliance & Accreditation: IT System Accreditation, IT Compliance Assessment, IT POAM Item
- **Choice Sets**: 35 global option sets including request types, access actions, entitlement types, catalog categories, system types, technology status, hosting types, assessment types, finding types, and workflow stages for requests, access, accreditation, assessments, and POAM items
- **Baseline Forms and Views**: Initial configuration for all 18 entities

### Changed
- **Status Field Refactoring**: Replaced legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Decision Status, Item Completion Status, Item Validation Status, Action Status, Compliance Status)

### Removed
- Legacy choice fields replaced with Stage and Core status fields

---
