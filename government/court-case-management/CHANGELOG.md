# Court Case Management Changelog

## Unreleased

## [1.2.0.0] - 2026-03-11

### Added

#### Case Management
- Court Case: Created table to track legal matters with case number/title, case type/stage, priority, filing/close dates, judicial district, assigned judge, court location, related cases, security classification, settlement tracking, jury trial flags, and case relationships
- Court Case Decision: Created table to record judicial rulings with decision number/title, decision type/date, deciding official, related hearing/filing, final decision flag, overall result, appeal status, publication status, legal authority, supporting documents, and legal reasoning
- Court Case Docket Entry: Created table for chronological case activity log with entry number, entry date/time, entry type, filed by party/organization, related filing/hearing/order/decision, security classification, public record flag, supporting documents, and descriptions

#### Documents & Filings
- Court Case Filing: Created table to manage document submissions with filing number/title, filing type, filing date/time, filed by party/person, approval status, priority, response tracking, filing fees, payment status, document reference, page count, electronic filing flag, organization unit, and descriptions

#### Hearings & Proceedings
- Court Case Hearing: Created table for scheduled appearances with hearing number/title, hearing type, scheduled/actual dates, duration, court case/session, presiding official, court reporter, location, participation mode, hearing stage, overall result, attendance status, priority, sealed hearing flag, recording/transcript availability, and notes
- Court Session: Created table for court calendar blocks with session number/title, session type/date, start/end times, presiding official, court reporter, bailiff, location, courtroom number, court organizational unit, operational status, participation mode, capacity, public/emergency session flags, and session notes

#### Orders & Compliance
- Court Case Order: Created table for formal court directives with order number/title, order type, issue/effective/expiration dates, court case, related decision, issuing official, order stage, priority, responsible party, compliance due date/status, compliance requirement, supporting document, temporary order flag, appeal status, and compliance notes

#### Parties & Representation
- Court Case Party: Created table to link persons/organizations to cases with party role/type, person/account references, start/end dates, primary party flag, party status, representation requirements, pro se flag, contact methods, notification details, service address, and descriptions
- Court Case Representation: Created table for attorney-client relationships with court case/party, representative person/organization, representation type, start/end dates, operational status, lead counsel flag, bar number/state, admission date, pro hac vice flag, contact information, and descriptions

#### Internal Work Management
- Court Case Work Item: Created table for staff task tracking with work item number/title, court case, work item type, general category, priority, action status, assignment details, due/completion dates, organization unit, estimated/actual hours, related filing/hearing/order/decision, supporting documents, and resolution notes

#### Choice Fields
- Court Case Stage: Configured choice field (Filed, Active, In Hearing, Under Review, Pending Decision, Decided, Appealed, Closed, Dismissed, Settled)
- Court Case Type: Configured choice field (Civil, Criminal, Family, Probate, Juvenile, Traffic, Small Claims, Administrative, Bankruptcy, Appeals)
- Court Decision Type: Configured choice field (Preliminary Ruling, Interlocutory Order, Summary Judgment, Final Judgment, Verdict, Sentencing, Dismissal, Default Judgment, Consent Decree)
- Court Docket Entry Type: Configured choice field (Filing Received, Hearing Scheduled, Hearing Held, Order Issued, Decision Rendered, Party Added, Motion Filed, Evidence Submitted, Continuance Granted, Status Update)
- Court Filing Type: Configured choice field (Complaint, Answer, Motion, Brief, Affidavit, Exhibit, Notice, Stipulation, Petition, Response, Reply, Memorandum)
- Court Hearing Type: Configured choice field (Initial Appearance, Arraignment, Pre-Trial Conference, Motion Hearing, Trial, Sentencing, Status Conference, Settlement Conference, Evidentiary Hearing, Appeals Hearing)
- Court Hearing Stage: Configured choice field (Scheduled, Preparation, Called to Order, In Session, Recessed, Continued, Under Deliberation, Decision Issued, Recorded, Closed)
- Court Order Type: Configured choice field (Temporary Order, Permanent Order, Protective Order, Restraining Order, Consent Order, Default Order, Enforcement Order, Modification Order, Show Cause Order, Dismissal Order)
- Court Order Stage: Configured choice field (Drafting, Under Review, Ready for Issuance, Issued, Entered on Record, Served / Notified, Effective, Monitoring Compliance, Satisfied, Closed)
- Court Party Role: Configured choice field (Plaintiff, Defendant, Petitioner, Respondent, Claimant, Appellant, Appellee, Intervener, Amicus Curiae, Third Party)
- Court Party Type: Configured choice field (Individual, Corporation, Partnership, Government Entity, Non-Profit Organization, Trust, Estate, Minor, Guardian, Conservator)
- Court Representation Type: Configured choice field (Retained Counsel, Court Appointed Counsel, Public Defender, Guardian Ad Litem, Legal Guardian, Conservator, Power of Attorney, Pro Bono Counsel, Special Counsel)
- Court Work Item Type: Configured choice field (Document Review, Filing Processing, Hearing Preparation, Order Preparation, Correspondence, Research, Scheduling, Notification, Compliance Check, Case Closure)
- Court Session Type: Configured choice field (Regular Session, Special Session, Emergency Session, Settlement Conference, Status Conference, Calendar Call, Motion Docket, Trial Docket)

#### Sample Data
- Created sample data for all 11 tables demonstrating typical court case workflows, party relationships, hearing schedules, filing processes, and compliance tracking

### Changed
- 
