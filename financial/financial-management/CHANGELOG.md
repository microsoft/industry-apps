# Financial Management Changelog

## Unreleased

## [1.1.0.0] - 2026-04-07

### Added
- **Financial Management Module**: 14 entities with 246+ fields supporting end-to-end procure-to-pay lifecycle from budget planning through payment execution
  - Budget & Control: Budget, Budget Line Item, Financial Funding Source, Financial Classification
  - Procurement: Purchase Request, Purchase Request Item, Procurement Package
  - Contract Management: Contract, Contract Amendment, Contract Line, Contract Deliverable, Contract Milestone
  - Financial Execution: Financial Commitment, Purchase Order, Purchase Order Line, Payment
- **Choice Sets**: 20 global option sets including funding source types, classification types, procurement methods, contract types and pricing structures, commitment types, and workflow stages for budget, procurement, contract, and payment processes
- **Baseline Forms and Views**: Initial configuration for all 14 entities

### Changed
- **Status Field Refactoring**: Replaced 7 legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Decision Status, Item Validation Status, Item Acceptance Status, Payment Status)

### Removed
- Legacy choice fields: Budget Status, Request Status (for Purchase Requests), Procurement Status, Agreement Status (for Contracts), Financial Commitment Status, Purchase Order Status, Contract Deliverable Status — replaced with Stage and Core status fields

---
