# 🔧 Core — Data Model Design

The **Core module** provides foundational tables and choice fields used across multiple application modules. It includes organizational structure (organization units, locations, judicial districts), people and workforce management (personnel types, grades, competencies), governance and compliance (legal authorities, compliance frameworks), action tracking, risk management, and content management. These reusable components serve as the backbone for specialized modules like HR Administration, Financial Management, Compliance & Security, and Government operations.

---

## Organizational Structure

### Organization Unit
Represents departments, divisions, branches, offices, or other organizational subdivisions within an entity.

**Completed:**
- Name: Text

**Planned:**
- Organization Unit Type: Choice (Organization Unit Type)
- Parent Organization Unit: Lookup (Organization Unit)
- Organization: Lookup (Account)
- Abbreviation: Text
- Unit Code: Text
- Effective Start Date: Date
- Effective End Date: Date
- Manager: Lookup (Contact)
- Location: Lookup (Location)
- Description: Memo
- Is Active: Yes / No

---

### Organization Unit Type
Categorizes organization units by hierarchical level or functional purpose (e.g., Department, Division, Branch, Office).

**Completed:**
- Name: Text

**Planned:**
- Type Code: Text
- Hierarchical Level: Integer
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Organization Initiative
Represents strategic initiatives, programs, or projects that span organizational boundaries.

**Completed:**
- Name: Text

**Planned:**
- Initiative Code: Text
- Initiative Type: Choice (General Category)
- Sponsoring Organization Unit: Lookup (Organization Unit)
- Program Manager: Lookup (Contact)
- Start Date: Date
- End Date: Date
- Status: Choice (Operational Status)
- Priority: Choice (Priority)
- Budget Amount: Currency
- Description: Memo
- Expected Outcomes: Memo
- Is Active: Yes / No

---

### Location
Represents physical locations, facilities, buildings, or sites where work occurs or services are delivered.

**Completed:**
- Name: Text

**Planned:**
- Location Type: Choice (General Category)
- Address Line 1: Text
- Address Line 2: Text
- City: Text
- State: Text, Max Length: 50
- Postal Code: Text, Max Length: 20
- Country: Text, Max Length: 50
- Parent Location: Lookup (Location)
- Managing Organization Unit: Lookup (Organization Unit)
- Is Primary: Yes / No
- Capacity: Integer
- Description: Memo
- Is Active: Yes / No

---

### Judicial District
Represents court jurisdictions or judicial districts for legal and government applications.

**Completed:**
- Name: Text

**Planned:**
- District Code: Text
- Jurisdiction Level: Choice (Jurisdiction Level)
- State: Text, Max Length: 50
- Presiding Judge: Lookup (Contact)
- Court Location: Lookup (Location)
- Description: Memo
- Is Active: Yes / No

---

## People & Workforce

### Personal Information
Stores additional demographic or personal details about individuals, linked to the Person (Contact) record.

**Completed:**
- Name: Text

**Planned:**
- Person: Lookup (Contact)
- Information Type: Lookup (Personal Information Type)
- Information Value: Text, Max Length: 500
- Effective Date: Date
- Expiration Date: Date
- Is Verified: Yes / No
- Verified Date: Date
- Verified By: Lookup (Contact)
- Security Classification: Choice (Security Classification)
- Description: Memo

---

### Personal Information Type
Defines categories of personal information (e.g., Emergency Contact, Citizenship, Language Proficiency).

**Completed:**
- Name: Text

**Planned:**
- Type Code: Text
- Category: Choice (General Category)
- Requires Verification: Yes / No
- Is Sensitive: Yes / No
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Personnel Type
Categorizes workforce members by employment category (e.g., Civilian, Uniformed, Contractor, Volunteer).

**Completed:**
- Name: Text

**Planned:**
- Type Code: Text
- Category: Choice (Employment Type)
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Job Series
Represents occupational groups or job families used to classify positions and roles.

**Completed:**
- Name: Text

**Planned:**
- Series Code: Text
- Occupational Category: Text
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Grade-Rank
Represents combined grade and rank structures for uniformed services or hierarchical organizations.

**Completed:**
- Name: Text

**Planned:**
- Grade: Text
- Rank: Text
- Pay Grade: Lookup (Pay Grade)
- Abbreviation: Text
- Hierarchical Level: Integer
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Pay Grade
Represents salary grades or pay scales used to structure compensation.

**Completed:**
- Name: Text

**Planned:**
- Grade Code: Text
- Min Salary: Currency
- Max Salary: Currency
- Midpoint Salary: Currency
- Effective Date: Date
- Expiration Date: Date
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Clearance Level
Defines security clearance levels required for sensitive positions or access to classified information.

**Completed:**
- Name: Text

**Planned:**
- Clearance Code: Text
- Security Level: Integer
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Credential
Represents professional licenses, certifications, or credentials held by individuals.

**Completed:**
- Name: Text

**Planned:**
- Person: Lookup (Contact)
- Credential Type: Choice (General Category)
- Issuing Authority: Text
- Credential Number: Text
- Issue Date: Date
- Expiration Date: Date
- Renewal Date: Date
- Status: Choice (Simple Certification Status)
- Supporting Document: Lookup (Document)
- Is Active: Yes / No

---

### Competency
Defines skills, knowledge areas, or competencies used for workforce development and assessment.

**Completed:**
- Name: Text

**Planned:**
- Competency Code: Text
- Competency Category: Choice (General Category)
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

## Action and Task Tracking

### Action Item
Represents tasks, action items, or follow-up items assigned to individuals or teams.

**Completed:**
- Name: Text

**Planned:**
- Action Number: Text
- Assigned To: Lookup (Contact)
- Assigned By: Lookup (Contact)
- Assigned Date: Date
- Due Date: Date
- Completed Date: Date
- Status: Choice (Action Status)
- Priority: Choice (Priority)
- Related To: Text
- Description: Memo
- Resolution Notes: Memo
- Is Overdue: Yes / No

---

## Governance & Decisions

### Agreement
Represents contracts, memoranda of understanding, or formal agreements between parties.

**Completed:**
- Name: Text

**Planned:**
- Agreement Number: Text
- Agreement Type: Choice (Agreement Type)
- Agreement Status: Choice (Agreement Status)
- Primary Organization: Lookup (Account)
- Primary Contact: Lookup (Contact)
- Counterparty Organization: Text
- Effective Date: Date
- Expiration Date: Date
- Total Value: Currency
- Owning Organization Unit: Lookup (Organization Unit)
- Description: Memo
- Key Terms: Memo
- Document: Lookup (Document)

---

### Formal Decision
Records official decisions made by governing bodies, committees, or authorized decision-makers.

**Completed:**
- Name: Text

**Planned:**
- Decision Number: Text
- Decision Date: Date
- Decision Maker: Lookup (Contact)
- Decision Body: Text
- Decision Type: Choice (General Category)
- Status: Choice (Approval Status)
- Effective Date: Date
- Related Initiative: Lookup (Organization Initiative)
- Description: Memo
- Rationale: Memo
- Supporting Document: Lookup (Document)

---

### Discussion Item
Represents topics, agenda items, or issues for discussion in meetings or deliberative processes.

**Completed:**
- Name: Text

**Planned:**
- Discussion Number: Text
- Topic Type: Choice (General Category)
- Raised By: Lookup (Contact)
- Raised Date: Date
- Priority: Choice (Priority)
- Status: Choice (Action Status)
- Related Decision: Lookup (Formal Decision)
- Description: Memo
- Discussion Notes: Memo
- Outcome: Memo

---

### After Action Report
Documents lessons learned and outcomes from completed initiatives, projects, or events.

**Completed:**
- Name: Text

**Planned:**
- Report Number: Text
- Report Date: Date
- Reporting Organization Unit: Lookup (Organization Unit)
- Report Author: Lookup (Contact)
- Event Date: Date
- Event Type: Choice (General Category)
- Overall Assessment: Choice (Overall Result)
- Related Initiative: Lookup (Organization Initiative)
- Executive Summary: Memo
- What Went Well: Memo
- Areas for Improvement: Memo
- Recommendations: Memo
- Supporting Document: Lookup (Document)

---

## Legal & Compliance

### Legal Authority
Represents laws, regulations, statutes, executive orders, or other legal authorities governing operations.

**Completed:**
- Name: Text

**Planned:**
- Authority Type: Choice (Legal Authority Type)
- Authority Status: Choice (Legal Authority Status)
- Jurisdiction Level: Choice (Jurisdiction Level)
- Citation: Text, Max Length: 200
- Enactment Date: Date
- Effective Date: Date
- Expiration Date: Date
- Issuing Authority: Text
- Description: Memo
- Summary: Memo
- Document: Lookup (Document)
- Is Active: Yes / No

---

### Legal Amendment
Records amendments, modifications, or revisions to existing legal authorities.

**Completed:**
- Name: Text

**Planned:**
- Original Authority: Lookup (Legal Authority)
- Amendment Number: Text
- Amendment Date: Date
- Effective Date: Date
- Impact: Choice (Legal Authority Impact)
- Description: Memo
- Changes Summary: Memo
- Document: Lookup (Document)

---

### Legal Cross-Reference
Links related legal authorities to establish relationships and dependencies.

**Completed:**
- Name: Text

**Planned:**
- Primary Authority: Lookup (Legal Authority)
- Related Authority: Lookup (Legal Authority)
- Relationship Type: Choice (General Category)
- Description: Memo

---

### Compliance Framework
Represents regulatory frameworks, standards, or compliance programs (e.g., FISMA, HIPAA, ISO).

**Completed:**
- Name: Text

**Planned:**
- Framework Code: Text
- Framework Category: Lookup (Compliance Framework Category)
- Issuing Organization: Text
- Version: Text
- Effective Date: Date
- Status: Choice (Publication Status)
- Description: Memo
- Scope: Memo
- Supporting Document: Lookup (Document)
- Is Active: Yes / No

---

### Compliance Framework Category
Categorizes compliance frameworks by domain or regulatory area.

**Completed:**
- Name: Text

**Planned:**
- Category Code: Text
- Description: Memo
- Sort Order: Integer
- Is Active: Yes / No

---

### Compliance Requirement
Represents specific compliance requirements derived from frameworks or legal authorities.

**Completed:**
- Name: Text

**Planned:**
- Requirement Number: Text
- Compliance Framework: Lookup (Compliance Framework)
- Legal Authority: Lookup (Legal Authority)
- Requirement Category: Choice (General Category)
- Priority: Choice (Priority)
- Status: Choice (Compliance Status)
- Responsible Organization Unit: Lookup (Organization Unit)
- Description: Memo
- Control Objective: Memo
- Supporting Document: Lookup (Document)

---

## Risk & Impact

### Risk Item
Represents identified risks, threats, or vulnerabilities requiring monitoring or mitigation.

**Completed:**
- Name: Text

**Planned:**
- Risk Number: Text
- Risk Category: Choice (General Category)
- Identified Date: Date
- Identified By: Lookup (Contact)
- Owning Organization Unit: Lookup (Organization Unit)
- Likelihood: Choice (High Medium Low)
- Severity: Choice (Severity Level)
- Overall Risk Level: Choice (High Medium Low)
- Status: Choice (Action Status)
- Description: Memo
- Impact Description: Memo
- Mitigation Strategy: Memo
- Is Active: Yes / No

---

### Impact
Records actual or potential impacts resulting from events, decisions, or risk items.

**Completed:**
- Name: Text

**Planned:**
- Impact Type: Choice (General Category)
- Impact Date: Date
- Affected Organization Unit: Lookup (Organization Unit)
- Severity: Choice (Severity Level)
- Direction: Choice (Direction)
- Polarity: Choice (Polarity)
- Related Risk: Lookup (Risk Item)
- Description: Memo
- Financial Impact: Currency
- Mitigation Actions: Memo

---

## Content & Documentation

### Document
Represents stored documents, files, or attachments linked to records across the system.

**Completed:**
- Name: Text

**Planned:**
- Document Number: Text
- Document Type: Choice (General Category)
- Version: Text
- Publication Date: Date
- Status: Choice (Publication Status)
- Author: Lookup (Contact)
- Owning Organization Unit: Lookup (Organization Unit)
- Security Classification: Choice (Security Classification)
- Description: Memo
- File Name: Text
- File Size: Integer
- Is Active: Yes / No

---

### Content Template
Stores reusable document templates for consistent formatting across modules.

**Completed:**
- Name: Text

**Planned:**
- Template Type: Choice (General Category)
- Template Content: Memo
- Description: Memo
- Version: Text
- Effective Date: Date
- Is Active: Yes / No

---

## Privacy

### Privacy Consent
Records consent for data collection, processing, or sharing, supporting privacy compliance.

**Completed:**
- Name: Text

**Planned:**
- Person: Lookup (Contact)
- Consent Type: Choice (General Category)
- Consent Date: Date
- Consent Status: Choice (Simple Certification Status)
- Expiration Date: Date
- Revoked Date: Date
- Revoked By: Lookup (Contact)
- Purpose: Memo
- Scope: Memo
- Supporting Document: Lookup (Document)

---

## Product

### Product
Represents goods, services, or products tracked for inventory, procurement, or service delivery.

**Completed:**
- Name: Text

**Planned:**
- Product Code: Text
- Product Category: Choice (General Category)
- Unit of Issue: Choice (Unit of Issue)
- Unit Price: Currency
- Description: Memo
- Specifications: Memo
- Is Active: Yes / No

---

## ✅ Global / Reusable Choice Fields

**Completed:**

**Planned:**

### Lifecycle Stage
Defines stages in a typical lifecycle (e.g., Planning, Active, Complete, Archived).
- Planning
- Initiation
- Active
- On Hold
- Complete
- Cancelled
- Archived

### Operational Status
General operational status applicable across entities (e.g., Draft, Pending, Active, Inactive).
- Draft
- Pending
- Active
- Inactive
- Suspended
- Closed

### Publication Status
Status of published content or documents.
- Draft
- In Review
- Approved
- Published
- Archived
- Withdrawn

### Approval Status
Tracks approval workflow status.
- Pending
- Approved
- Rejected
- Cancelled
- Recalled

### Visibility
Controls who can view records (e.g., Public, Internal, Restricted).
- Public
- Internal
- Restricted
- Confidential

### Yes No
Standard Yes/No choice set (already created in Core).
- Yes
- No

### Priority
Standard priority levels.
- Critical
- High
- Medium
- Low

### Severity Level
Severity classification for risks, incidents, or impacts.
- Critical
- High
- Moderate
- Low
- Minimal

### High Medium Low
Simple three-level rating scale.
- High
- Medium
- Low

### Security Classification
Data security classification levels.
- Unclassified
- Sensitive
- Confidential
- Secret
- Top Secret

### Employment Type
Types of employment relationships.
- Full Time
- Part Time
- Temporary
- Seasonal
- Contractor
- Volunteer

### Engagement Mode
How personnel engage with work.
- On Site
- Remote
- Hybrid
- Field
- Travel

### Personnel Availability
Availability status for workforce planning.
- Available
- Assigned
- Deployed
- On Leave
- Unavailable

### Position Designation
Designation or classification of positions.
- Career
- Temporary
- Term
- Intern
- Fellow
- Appointed

### Jurisdiction Level
Level of legal or governmental jurisdiction.
- Federal
- State
- County
- Municipal
- Tribal
- International

### Legal Authority Type
Categories of legal authorities.
- Statute
- Regulation
- Executive Order
- Policy
- Directive
- Guideline
- Case Law

### Legal Authority Status
Current status of legal authority.
- Proposed
- Enacted
- In Effect
- Amended
- Repealed
- Expired

### Legal Authority Impact
Impact level of legal authority or amendment.
- Major
- Moderate
- Minor
- Technical
- Clarification

### Compliance Status
Status of compliance activities or requirements.
- Compliant
- Partially Compliant
- Non-Compliant
- Not Assessed
- In Progress
- Not Applicable

### Method of Contact
How contact was initiated.
- Phone
- Email
- In Person
- Mail
- Web Form
- Portal
- Social Media

### Method of Receipt
How items or requests were received.
- Electronic
- Mail
- In Person
- Fax
- Portal
- Email

### Submission Type
Type or source of submission.
- Self Submitted
- Agency Submitted
- Third Party
- Automatic
- Bulk Import

### Request Status
Status of requests or applications.
- Submitted
- Under Review
- Pending Information
- Approved
- Rejected
- Withdrawn
- Completed

### Action Status
Status of action items or tasks.
- Not Started
- In Progress
- On Hold
- Completed
- Cancelled
- Deferred

### Eligibility Status
Eligibility determination status.
- Eligible
- Ineligible
- Conditionally Eligible
- Under Review
- Pending Verification

### Simple Certification Status
Basic certification or attestation status.
- Certified
- Not Certified
- Pending
- Expired
- Revoked

### Direction
Direction of change or movement.
- Increase
- Decrease
- No Change

### Polarity
Positive or negative valence.
- Positive
- Neutral
- Negative

### Overall Result
Outcome assessment for activities or events.
- Successful
- Partially Successful
- Unsuccessful
- Inconclusive

### Objective Result
Achievement of stated objectives.
- Met
- Partially Met
- Not Met
- Exceeded

### Unit of Issue
Standard units for products or resources.
- Each
- Box
- Case
- Pallet
- Pound
- Gallon
- Hour
- Day

### General Category
Generic categorization field for flexible classification.
- Type A
- Type B
- Type C
- Other

### Agreement Type
Types of agreements or contracts.
- Contract
- Memorandum of Understanding
- Service Level Agreement
- Grant
- Cooperative Agreement
- Lease
- License

### Agreement Status
Current status of agreements.
- Draft
- Under Negotiation
- Pending Approval
- Active
- Expired
- Terminated
- Renewed

### Commitment Status
Status of commitments or obligations.
- Planned
- Committed
- In Progress
- Fulfilled
- Partially Fulfilled
- Unfulfilled
- Cancelled