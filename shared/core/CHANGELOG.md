# Core Module Changelog

All notable changes to the Core module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

#### Foundation Entities
- **Entity: General Category** - Created with 2 fields (Category Code, Description) for standardized categorization across all modules
- **Entity: State or Province** - Created with 4 fields (State Code, Country lookup, Abbreviation, Description) for geographic reference
- **Entity: Country** - Created with 4 fields (Country Code, ISO Code, Description, Currency) for international support
- **Entity: Location** - Created with 11 fields including address components, State or Province/Country lookups, GPS coordinates, and location type classification
- **Entity: Organization Unit** - Created with 10 fields including Unit Code, Parent Organization Unit hierarchy, Manager lookup, Location relationship, and organizational details
- **Entity: Tag** - Created with 4 fields (Tag Name, General Category, Color, Description) for flexible content tagging

#### Calendar & Time Management
- **Entity: Calendar** - Created with 7 fields including Calendar Type choice, Owner lookup, Location relationship, time zone, and validity periods
- **Entity: Calendar Entry** - Created with 11 fields including Calendar/Location lookups, Entry Type choice, start/end dates, recurrence, and attendee tracking
- **Entity: Holiday** - Created with 8 fields including Holiday Type/Observance Level choices, dates, Location relationship, and applicability scope

#### Communication & Notifications
- **Entity: Note** - Created with 7 fields including Regarding/Created By lookups, General Category, Note Date, Priority choice, and rich text content
- **Entity: Attachment** - Created with 9 fields including Regarding lookup, File Type choice, file metadata (name, size, MIME type, URL), and Security Classification
- **Entity: Communication** - Created with 13 fields including Sender/Recipient/Related To lookups, Communication Type/Method/Status choices, dates, subject, and message body
- **Entity: Communication Template** - Created with 7 fields including Template Type/Communication Method choices, template content, placeholders, and metadata
- **Entity: Notification** - Created with 11 fields including Recipient User/Related To lookups, Notification Type/Priority/Status choices, dates, and notification content
- **Entity: Notification Template** - Created with 6 fields including Template Type/Priority choices, template content with dynamic placeholders

#### Legal & Compliance Framework
- **Entity: Legal Authority** - Created with 10 fields including Authority Type/Jurisdiction Level choices, Issuing Organization lookup, identification codes, and effective dates
- **Entity: Legal Citation** - Created with 9 fields including Legal Authority/Cited Authority lookups, Citation Type choice, section references, and citation details
- **Entity: Legal Amendment** - Created with 10 fields including Original/Amended Legal Authority lookups, Amendment Type choice, tracking numbers, dates, and amendment summaries
- **Entity: Legal Cross-Reference** - Created with 5 fields including Primary/Related Legal Authority lookups, General Category/Impact choices, and relationship descriptions
- **Entity: Compliance Framework** - Created with 9 fields including Framework Category lookup, Issuing Organization relationship, version tracking, Publication Status choice, and framework scope
- **Entity: Compliance Framework Category** - Created with 2 fields (Category Code, Description) for organizing compliance frameworks
- **Entity: Compliance Requirement** - Created with 11 fields including Compliance Framework/Framework Category/Legal Authority/Responsible Organization Unit lookups, General Category/Priority/Compliance Status choices, and requirement documentation

#### Risk & Impact Management
- **Entity: Risk Item** - Created with 13 fields including Identified By Contact/User lookups, General Category/Likelihood/Severity/Risk Level/Action Status choices, dates, and risk documentation with mitigation strategies
- **Entity: Impact** - Created with 10 fields including Related Risk/Affected Organization Unit lookups, General Category/Severity/Direction/Polarity choices, Impact Date, Financial Impact with currency tracking, and mitigation actions

#### Document & Content Management
- **Entity: Document** - Created with 13 fields including Document Number, Version, General Category/Publication Status/Security Classification choices, Author (User) and External Author (Contact) lookups, Owning Organization Unit relationship, file metadata (name, size, URL), and descriptions
- **Entity: Content Template** - Created with 5 fields including General Category choice, template content, version tracking, effective date, and descriptions for reusable document templates

#### Privacy & Consent Management
- **Entity: Privacy Consent** - Created with 11 fields including Person (Contact) and User lookups, General Category choice, Consent Status (Yes/No), dates (consent, expiration, revoked), Revoked By lookup, Supporting Document relationship, and consent scope documentation

#### Product & Services
- **Entity: Product** - Created with 6 fields including Product Code, General Category/Unit of Issue choices, Unit Price with currency support, and detailed product descriptions and specifications

#### Supporting Infrastructure
- **Choice Set: Yes No** - Shared global option set (appbase_yesno) used for standardized Yes/No fields across all entities, referenced by Privacy Consent and other boolean-type fields

### Changed

### Fixed

### Removed

---

## Notes

- **Action Item entity intentionally skipped** per architectural decision - functionality will be provided through alternative implementation
- **Field naming conventions applied**: "General Category" standardized across all entities, "State or Province" for geographic references, "Description" for generic memo fields
- **Currency fields**: Automatically create companion _base fields for multi-currency support
- **Lookup relationships**: Follow ui-tools naming conventions for schema name generation
- **Yes/No fields**: Reference shared "Yes No" global option set rather than individual boolean fields
