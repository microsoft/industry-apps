# Asset Management Changelog

## Unreleased

## [1.1.0.0] - 2026-02-26

### Added
- Choice Sets: Created 13 global option sets for Asset Management module:
  - **Asset Lifecycle**: Asset Status (10 values), Asset Condition (7 values), Asset Depreciation Method (5 values)
  - **Acquisition & Financial**: Asset Acquisition Type (6 values), Asset Cost Type (7 values)
  - **Ownership & Custody**: Asset Ownership Type (6 values), Asset Custody Event Type (8 values)
  - **Audit & Compliance**: Schedule Status (6 values), Asset Audit Type (6 values), Asset Discrepancy Type (6 values), Verification Status
  - **Disposition**: Asset Disposition Type (8 values), Asset Disposition Reason (8 values)

- Entity Fields: Completed field creation for all 14 Asset Management entities (180+ fields total):
  - **Core Asset Records:**
    - **Asset**: 28 fields for individual asset tracking including asset number, serial number, asset type/category, product reference, status/condition, acquisition dates, useful life, parent asset, RF tag/barcode, estimated value, depreciation method, disposal flags, inspection requirements, current location/assignment/owner, and notes
    - **Asset Type**: 6 fields for operational asset classification including asset category, description, default useful life, tracking requirements, and inspection flags
    - **Asset Category**: 4 fields for high-level asset grouping including parent category hierarchy, description, and capitalization thresholds
  - **Acquisition & Financial Tracking:**
    - **Asset Acquisition**: 13 fields for acquisition events including acquisition type, date, supplier, purchase order, total cost, funding source, payment status, receiving details (date/person), invoice tracking, warranty expiration, and notes
    - **Asset Cost Entry**: 7 fields for additional capital/operational costs including asset, cost type, date, amount, vendor, invoice number, description, capitalization flag, and notes
  - **Ownership, Assignment & Custody:**
    - **Asset Owner**: 8 fields for ownership tracking including asset, ownership type, owner account/organization unit, effective dates (start/end), current flag, and notes
    - **Asset Assignment**: 11 fields for custody/responsibility tracking including asset, assigned person/organization unit, assignment date, expected/actual return dates, purpose, assignment status, current flag, and notes
    - **Asset Custody Event**: 13 fields for auditable custody history including asset, event type, event date time, from/to person, from/to organization unit, from/to location, recorded by, verification method, and notes
  - **Service & Operational History:**
    - **Asset Service Record**: 12 fields for maintenance/service logs including asset, service type, service date, provider (account/contact), cost, meter reading, service status, next service due date, description, and notes
    - **Asset Service Type**: 2 fields for service event reference list (name, description)
  - **Audit & Compliance:**
    - **Asset Audit**: 13 fields for audit cycles including audit type, start/end dates, schedule status, auditor, scope (organization unit/location), totals (expected/verified assets, discrepancies), description, and notes
    - **Asset Audit Item**: 17 fields for asset-level audit results including asset audit, asset, expected vs observed data (location/assignee/condition), verification status, verification date time/person, discrepancy type, findings, resolution details, and resolution date
    - **Asset Inspection Requirement**: 7 fields for recurring inspection rules including asset type, specific asset, inspection frequency (choice/days), regulatory authority, compliance framework, and description
  - **Retirement & Disposition:**
    - **Asset Disposition**: 16 fields for retirement/disposal including asset, disposition type/reason, disposition date, approval workflow (approved by/date), recipient (account/person), sale price, disposal cost, certificate of destruction, environmental/data sanitization compliance flags, description, and notes
- Forms: Configured baseline forms for all 14 Asset Management entities including main form layouts, field sections, tab organization, and business rules for Core Asset Records (Asset, Asset Type, Asset Category), Acquisition & Financial (Asset Acquisition, Asset Cost Entry), Ownership & Custody (Asset Owner, Asset Assignment, Asset Custody Event), Service & Operational History (Asset Service Record, Asset Service Type), Audit & Compliance (Asset Audit, Asset Audit Item, Asset Inspection Requirement), and Retirement & Disposition (Asset Disposition)
- Views: Configured baseline views for all 14 Asset Management entities including active views, lookup views, associated views, and advanced find views with appropriate columns, filters, and sorting
- Model-Driven App: Configured Asset Management model-driven app with navigation structure, entity forms/views integration, dashboards, and user interface customizations

### Changed
- 
