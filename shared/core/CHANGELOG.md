# Core Module Changelog

All notable changes to the Core module will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added

#### Organizational Structure
- **Entity: Organization Unit** - Created with 11 fields including Name, Organization Unit Type lookup, Parent Organization Unit hierarchy, Organization/Manager/Location relationships, Unit Code, Abbreviation, effective dates, and Description
- **Entity: Organization Unit Type** - Created with 4 fields (Name, Type Code, Hierarchical Level, Description) to categorize organization units by level or functional purpose
- **Entity: Organization Initiative** - Created with 12 fields including Initiative Code, General Category, Sponsoring Organization Unit, Program Manager, dates, Operational Status, Priority, Budget Amount, Description, Expected Outcomes, and Parent Organization Initiative lookup for hierarchy
- **Entity: Location** - Created with 13 fields including Name, General Category, full address components, State or Province/Country/Parent Location/Managing Organization Unit lookups, Is Primary flag, Capacity, and Description
- **Entity: Judicial District** - Created with 8 fields including District Code, Jurisdiction Level, State or Province, Presiding Judge, Court Location, Description, and Parent Judicial District lookup for hierarchy

#### People & Workforce Management
- **Entity: Personal Information** - Created with 10 fields including Person lookup, Information Type, Information Value (500 char), effective/expiration dates, verification tracking (Is Verified flag, Verified Date/By), and Security Classification
- **Entity: Personal Information Type** - Created with 6 fields including Type Code, General Category, Requires Verification flag, Is Sensitive flag, and Description for categorizing personal information
- **Entity: Personnel Type** - Created with 4 fields (Name, Type Code, Employment Type, Description) to classify employment categories for workforce management
- **Entity: Job Series** - Created with 4 fields including Series Code, Occupational Category, and Description for broader job family groupings
- **Entity: Grade-Rank** - Created with 7 fields including Grade, Rank, Pay Grade lookup, Abbreviation, Hierarchical Level, and Description for combined grade and rank structures
- **Entity: Pay Grade** - Created with 8 fields including Grade Code, salary ranges (Min/Max/Midpoint), effective/expiration dates, and Description for salary grade structures
- **Entity: Clearance Level** - Created with 4 fields (Name, Clearance Code, Security Level integer, Description) for security clearance requirements
- **Entity: Credential Type** - Created with 10 fields including Credential Code, Parent Credential Type hierarchy, General Category, Issuing Authority, validity periods, renewal requirements, Related Competency lookup, and detailed descriptions/requirements
- **Entity: Credential Assignment** - Created with 8 fields including Person, Credential Type, Credential Number, issue/expiration/renewal dates, Certification Status, and Supporting Document for tracking personnel credentials
- **Entity: Competency** - Created with 4 fields (Name, Competency Code, General Category, Description) for defining skills and capabilities

#### Calendar & Time Management
- **Entity: Calendar** - Created with 7 fields including Calendar Type choice, Owner lookup, Location relationship, time zone, and validity periods
- **Entity: Calendar Entry** - Created with 11 fields including Calendar/Location lookups, Entry Type choice, start/end dates, recurrence, and attendee tracking
- **Entity: Holiday** - Created with 8 fields including Holiday Type/Observance Level choices, dates, Location relationship, and applicability scope

#### Governance & Decisions
- **Entity: Agreement** - Created with 14 fields including Agreement Number, Agreement Type/Status choices, Primary/Counterparty Organization and Contact lookups, effective/expiration dates, Total Value, Organization Unit, Key Terms, Document reference, and Parent Agreement lookup for hierarchy
- **Entity: Formal Decision** - Created with 12 fields including Decision Number, Decision Date, Decision Maker/Body, General Category, Approval Status, Effective Date, Related Initiative, Rationale, and Supporting Document
- **Entity: Discussion Item** - Created with 11 fields including Discussion Number, General Category, Raised By/Date, Priority, Action Status, Related Decision, Discussion Notes, Outcome, and Parent Discussion Item lookup for threaded discussions
- **Entity: After Action Report** - Created with 14 fields including Report Number/Date, Reporting Organization Unit, Report Author, Event Date, General Category, Overall Assessment, Related Initiative, Executive Summary, What Went Well, Areas for Improvement, Recommendations, and Supporting Document

#### Communication & Notifications
- **Entity: Note** - Created with 7 fields including Regarding/Created By lookups, General Category, Note Date, Priority choice, and rich text content
- **Entity: Attachment** - Created with 9 fields including Regarding lookup, File Type choice, file metadata (name, size, MIME type, URL), and Security Classification
- **Entity: Communication** - Created with 13 fields including Sender/Recipient/Related To lookups, Communication Type/Method/Status choices, dates, subject, and message body
- **Entity: Communication Template** - Created with 7 fields including Template Type/Communication Method choices, template content, placeholders, and metadata
- **Entity: Notification** - Created with 11 fields including Recipient User/Related To lookups, Notification Type/Priority/Status choices, dates, and notification content
- **Entity: Notification Template** - Created with 6 fields including Template Type/Priority choices, template content with dynamic placeholders

#### Legal & Compliance Framework
- **Entity: Legal Authority** - Created with 12 fields including Authority Type/Status/Jurisdiction Level choices, Citation, Parent Legal Authority hierarchy, Issuing Authority, dates (enactment/effective/expiration), Description, Summary, and Document reference
- **Entity: Legal Citation** - Created with 9 fields including Legal Authority/Cited Authority lookups, Citation Type choice, section references, and citation details
- **Entity: Legal Amendment** - Created with 10 fields including Original Authority lookup, Amendment Number/Date, Effective Date, Legal Authority Impact choice, Changes Summary, and Document reference for tracking legal authority amendments
- **Entity: Legal Cross-Reference** - Created with 5 fields including Primary/Related Legal Authority lookups, General Category/Impact choices, and relationship descriptions
- **Entity: Compliance Framework** - Created with 10 fields including Framework Code, Framework Category, Issuing Organization, Version, effective dates, Publication Status, Scope, Supporting Document, and Parent Compliance Framework lookup for hierarchy
- **Entity: Compliance Framework Category** - Created with 4 fields (Name, Category Code, Description, Parent Category) for organizing compliance frameworks hierarchically
- **Entity: Compliance Requirement** - Created with 12 fields including Requirement Number, Compliance Framework/Category/Legal Authority lookups, General Category, Priority, Compliance Status, Responsible Organization Unit, Control Objective, Supporting Document, and Parent Compliance Requirement lookup for requirement hierarchies

#### Risk & Impact Management
- **Entity: Analysis** - Created with 10 fields including Analysis Number, General Category/Action Status choices, Analysis Date, Conducted By (User) lookup, Owning Organization Unit relationship, Supporting Document lookup, and detailed findings and recommendations memos. Serves as a parent container for Risk Items and Impacts
- **Entity: Risk Item** - Created with 13 fields including Identified By Contact/User lookups, General Category/Likelihood/Severity/Risk Level/Action Status choices, dates, and risk documentation with mitigation strategies
- **Entity: Impact** - Created with 10 fields including Related Risk/Affected Organization Unit lookups, General Category/Severity/Direction/Polarity choices, Impact Date, Financial Impact with currency tracking, and mitigation actions
- **Relationship: Analysis to Risk Items** - Added Analysis lookup field to Risk Item entity enabling parent-child relationship for organizing risks under analyses
- **Relationship: Analysis to Impacts** - Added Analysis lookup field to Impact entity enabling parent-child relationship for organizing impacts under analyses

#### Document & Content Management
- **Entity: Document** - Created with 13 fields including Document Number, Version, General Category/Publication Status/Security Classification choices, Author (User) and External Author (Contact) lookups, Owning Organization Unit relationship, file metadata (name, size, URL), and descriptions
- **Entity: Content Template** - Created with 5 fields including General Category choice, template content, version tracking, effective date, and descriptions for reusable document templates

#### Privacy & Consent Management
- **Entity: Privacy Consent** - Created with 11 fields including Person (Contact) and User lookups, General Category choice, Consent Status (Yes/No), dates (consent, expiration, revoked), Revoked By lookup, Supporting Document relationship, and consent scope documentation

#### Product & Services
- **Entity: Product** - Created with 6 fields including Product Code, General Category/Unit of Issue choices, Unit Price with currency support, and detailed product descriptions and specifications

#### Supporting Infrastructure
- **Choice Set: Yes No** - Shared global option set (appbase_yesno) used for standardized Yes/No fields across all entities, referenced by Privacy Consent and other boolean-type fields

#### Comprehensive Choice Sets (50+ Global Option Sets)
Created comprehensive choice field library covering all common domains:

**Workflow & Status Management:**
- Action Status (8 values: New, In Progress, Submitted for Review, Review In Progress, Returned, Complete, Cancelled, Deferred)
- Approval Status (6 values: Pending, Approved, Rejected, Cancelled, Returned, Recalled)
- Request Status (7 values: Submitted, Under Review, Pending Information, Approved, Rejected, Withdrawn, Completed)
- Operational Status (6 values: Draft, Pending, Active, Inactive, Suspended, Closed)
- Publication Status (6 values: Draft, In Review, Approved, Published, Archived, Withdrawn)
- Assignment Status (5 values: Active, Pending Return, Returned, Overdue, Cancelled)
- Payment Status (5 values: Pending, Partial, Paid, Disputed, Refunded)
- Verification Status (5 values: Verified, Not Found, Discrepancy Found, Pending Investigation, Resolved)

**Priority & Severity:**
- Priority (4 values: Low, Medium, High, Critical)
- Severity Level (5 values: Critical, High, Moderate, Low, Minimal)
- High Medium Low (3 values: simple rating scale)

**Lifecycle & Progress:**
- Lifecycle Stage (7 values: Planning, Initiation, Active, On Hold, Complete, Cancelled, Archived)
- Period Status (5 values: Future, Open, Closed, Locked, Adjusted)
- Commitment Status (7 values: Planned, Committed, In Progress, Fulfilled, Partially Fulfilled, Unfulfilled, Cancelled)

**Security & Access:**
- Security Classification (5 values: Unclassified, Sensitive, Confidential, Secret, Top Secret)
- Visibility (4 values: Public, Internal, Restricted, Confidential)

**Assessment & Results:**
- Overall Result (4 values: Successful, Partially Successful, Unsuccessful, Inconclusive)
- Objective Result (4 values: Met, Partially Met, Not Met, Exceeded)
- Simple Certification Status (5 values: Certified, Not Certified, Pending, Expired, Revoked)
- Eligibility Status (5 values: Eligible, Ineligible, Conditionally Eligible, Under Review, Pending Verification)
- Compliance Status (6 values: Compliant, Partially Compliant, Non-Compliant, Not Assessed, In Progress, Not Applicable)

**Direction & Impact:**
- Direction (3 values: Increase, Decrease, No Change)
- Polarity (3 values: Positive, Neutral, Negative)
- Impact (5 values: Direct, Indirect, Minimal, None, Unknown)

**Workforce & Personnel:**
- Employment Type (6 values: Full Time, Part Time, Temporary, Seasonal, Contractor, Volunteer)
- Engagement Mode (5 values: On Site, Remote, Hybrid, Field, Travel)
- Personnel Availability (5 values: Available, Assigned, Deployed, On Leave, Unavailable)
- Position Designation (6 values: Career, Temporary, Term, Intern, Fellow, Appointed)

**Legal & Governance:**
- Jurisdiction Level (6 values: Federal, State, County, Municipal, Tribal, International)
- Legal Authority Type (7 values: Statute, Regulation, Executive Order, Policy, Directive, Guideline, Case Law)
- Legal Authority Status (6 values: Proposed, Enacted, In Effect, Amended, Repealed, Expired)
- Legal Authority Impact (5 values: Major, Moderate, Minor, Technical, Clarification)
- Decision Category (12 values: Scope Change, Timeline Extension, Budget Reallocation, Accountability Reassignment, etc.)

**Agreements & Contracts:**
- Agreement Type (7 values: Contract, Memorandum of Understanding, Service Level Agreement, Grant, Cooperative Agreement, Lease, License)
- Agreement Status (7 values: Draft, Under Negotiation, Pending Approval, Active, Expired, Terminated, Renewed)

**Communication & Contact:**
- Method of Receipt (7 values: Web Portal, Phone, Email, In Person, Fax, Mail, Social Media)
- Method of Contact (7 values: Phone, Email, In Person, Mail, Web Form, Portal, Social Media)
- Submission Type (5 values: Self Submitted, Agency Submitted, Third Party, Automatic, Bulk Import)

**Financial & Inventory:**
- Unit of Issue (8 values: Each, Box, Case, Pallet, Pound, Gallon, Hour, Day)
- Period Type (7 values: Month, Quarter, Half Year, Fiscal Year, Calendar Year, Biennial, Custom Period)

**Cross-Domain Classification:**
- General Category (20 domain values: Access Control & Identity Management, Asset & Logistics Management, Compliance & Regulatory, Cybersecurity, Data Privacy & Protection, Environmental Compliance, Ethics & Governance, Financial Management, Foreign Interests, Health & Safety, Human Resources & Workforce, Incident & Disaster Response, Information Management & Records, National Security, Operational Resilience, Procurement & Contract Management, Public Relations & Communication, Risk Management, Technology & Innovation, Training & Development)

**Task & Dependency Management:**
- Task Dependency Type (6 values: Finish to Start, Finish to Finish, Start to Start, Start to Finish, Informational, Resource Dependency)
- Task Dependency Status (5 values: Active, Satisfied, Blocked, At Risk, Cancelled)

### Changed

### Fixed

### Removed

---

## Notes

- **Module Status**: Core module field and choice set creation complete - all 40+ entities and 50+ choice sets fully implemented
- **Entity Count**: 40+ foundational entities covering organizational structure, people & workforce, calendar & time, governance & decisions, communication & notifications, legal & compliance, risk & impact, content & documentation, privacy, and product management
- **Choice Set Count**: 50+ global option sets providing standardized values for workflow management, security, assessment, workforce, legal governance, agreements, communication, financial periods, and cross-domain classification
- **Hierarchical Relationships**: Multiple entities support parent-child hierarchies including Organization Unit, Organization Initiative, Judicial District, Credential Type, Compliance Framework, Compliance Framework Category, Compliance Requirement, Discussion Item, Agreement, Risk Item, and Impact
- **Action Item entity intentionally skipped** per architectural decision - functionality will be provided through alternative implementation
- **Analysis entity pattern**: General-purpose table for storing various types of analyses, serving as a parent container for Risk Items and Impacts to enable organized tracking of analytical work
- **Field naming conventions applied**: "General Category" standardized across all entities, "State or Province" for geographic references, "Description" for generic memo fields
- **Currency fields**: Automatically create companion _base fields for multi-currency support
- **Lookup relationships**: Follow ui-tools naming conventions for schema name generation
- **Yes/No fields**: Reference shared "Yes No" global option set rather than individual boolean fields
- **Reusability**: Core entities and choice sets designed for reference across all specialized modules (HR, Financial, Compliance, Asset Management, etc.)
