# 🔧 Core — Data Model Design

The **Core module** provides foundational tables and choice fields used across multiple application modules. It includes organizational structure (organization units, locations, judicial districts), people and workforce management (personnel types, grades, competencies), governance and compliance (legal authorities, compliance frameworks), action tracking, risk management, and content management. These reusable components serve as the backbone for specialized modules like HR Administration, Financial Management, Compliance & Security, and Government operations.

---

## Organizational Structure

### Organization Unit
Represents departments, divisions, branches, offices, or other organizational subdivisions within an entity.

**Completed:**
- Name: Text
- Organization Unit Type: Lookup (Organization Unit Type)
- Parent Organization Unit: Lookup (Organization Unit)
- Organization: Lookup (Account)
- Abbreviation: Text
- Unit Code: Text
- Effective Start Date: Date
- Effective End Date: Date
- Manager: Lookup (Contact)
- Location: Lookup (Location)
- Description: Memo

**Planned:**

---

### Organization Unit Type
Categorizes organization units by hierarchical level or functional purpose (e.g., Department, Division, Branch, Office).

**Completed:**
- Name: Text
- Type Code: Text
- Hierarchical Level: Integer
- Description: Memo

**Planned:**

---

### Organization Initiative
**Completed:**
- Name: Text
- Initiative Code: Text
- General Category: Choice (General Category)
- Sponsoring Organization Unit: Lookup (Organization Unit)
- Program Manager: Lookup (Contact)
- Start Date: Date
- End Date: Date
- Operational Status: Choice (Operational Status)
- Priority: Choice (Priority)
- Budget Amount: Currency
- Description: Memo
- Expected Outcomes: Memo

**Added:**
- Parent Organization Initiative: Lookup (Organization Initiative)

**Planned:**

---

### Location
Represents physical locations, facilities, buildings, or sites where work occurs or services are delivered.

**Completed:**
- Name: Text
- General Category: Choice (General Category)
- Address Line 1: Text
- Address Line 2: Text
- City: Text
- State or Province: Lookup (State or Province)
- Postal Code: Text, Max Length: 20
- Country: Lookup (Country)
- Parent Location: Lookup (Location)
- Managing Organization Unit: Lookup (Organization Unit)
- Is Primary: Yes / No
- Capacity: Integer
- Description: Memo

**Planned:**

---

### Judicial District
**Completed:**
- Name: Text
- District Code: Text
- Jurisdiction Level: Choice (Jurisdiction Level)
- State or Province: Lookup (State or Province)
- Presiding Judge: Lookup (Contact)
- Court Location: Lookup (Location)
- Description: Memo

**Added:**
- Parent Judicial District: Lookup (Judicial District)

**Planned:**
---
## People & Workforce

### Personal Information
**Completed:**
- Name: Text
- Person: Lookup (Contact)
- Information Type: Lookup (Personal Information Type)
- Information Value: Text, Max Length: 500
- Effective Date: Date
- Expiration Date: Date
- Is Verified: Yes / No
- Verified Date: Date
- Verified By: Lookup (Contact)
- Security Classification: Choice (Security Classification)

**Planned:**
---
### Personal Information Type
**Completed:**
- Name: Text
- Type Code: Text
- General Category: Choice (General Category)
- Requires Verification: Yes / No
- Is Sensitive: Yes / No
- Description: Memo

**Planned:**
---

### Personnel Type
**Completed:**
- Name: Text
- Type Code: Text
- Employment Type: Choice (Employment Type)
- Description: Memo

**Planned:**
---
### Job Series
**Completed:**
- Name: Text
- Series Code: Text
- Occupational Category: Text
- Description: Memo

**Planned:**
---
### Grade-Rank
**Completed:**
- Name: Text
- Grade: Text
- Rank: Text
- Pay Grade: Lookup (Pay Grade)
- Abbreviation: Text
- Hierarchical Level: Integer
- Description: Memo

**Planned:**
---

### Pay Grade
**Completed:**
- Name: Text
- Grade Code: Text
- Min Salary: Currency
- Max Salary: Currency
- Midpoint Salary: Currency
- Effective Date: Date
- Expiration Date: Date
- Description: Memo

**Planned:**
---
### Clearance Level
**Completed:**
- Name: Text
- Clearance Code: Text
- Security Level: Integer
- Description: Memo

**Planned:**
---
### Credential Type
**Completed:**

- Credential Code: Text
- Parent Credential Type: Lookup (Credential Type)
- General Category: Choice (General Category)
- Issuing Authority: Lookup (Account)
- Typical Validity Period (Months): Integer
- Requires Renewal: Yes / No
- Renewal Frequency (Months): Integer
- Description: Memo
- Requirements: Memo
- Related Competency: Lookup (Competency)

**Planned:**
- Name: Text
---
### Credential Assignment
**Completed:**

- Person: Lookup (Contact)
- Credential Type: Lookup (Credential Type)
- Credential Number: Text
- Issue Date: Date
- Expiration Date: Date
- Renewal Date: Date
- Certification Status: Choice (Simple Certification Status)
- Supporting Document: Lookup (Document)

**Planned:**
- Name: Text
---
### Competency
**Completed:**
- Name: Text
- Competency Code: Text
- General Category: Choice (General Category)
- Description: Memo

**Planned:**
---
## Action and Task Tracking

### Action Item
Represents tasks, action items, or follow-up items assigned to individuals or teams.

**Completed:**
- Name: Text

**Planned:**
- Action Number: Text
- Assigned By: Lookup (User)
- Assigned Date: Date
- Action Status: Choice (Action Status)
- Priority: Choice (Priority)
- Description: Memo
- Resolution Notes: Memo

---

## Governance & Decisions

### Agreement
**Completed:**
- Name: Text
- Agreement Number: Text
- Agreement Type: Choice (Agreement Type)
- Agreement Status: Choice (Agreement Status)
- Primary Organization: Lookup (Account)
- Primary Contact: Lookup (Contact)
- Counterparty Organization: Lookup (Account)
- Effective Date: Date
- Expiration Date: Date
- Total Value: Currency
- Organization Unit: Lookup (Organization Unit)
- Description: Memo
- Key Terms: Memo
- Document: Lookup (Document)

**Added:**
- Parent Agreement: Lookup (Agreeemnt)

**Planned:**
---
### Formal Decision
**Completed:**
- Name: Text
- Decision Number: Text
- Decision Date: Date
- Decision Maker: Lookup (Contact)
- Decision Body: Text
- General Category: Choice (General Category)
- Approval Status: Choice (Approval Status)
- Effective Date: Date
- Related Initiative: Lookup (Organization Initiative)
- Description: Memo
- Rationale: Memo
- Supporting Document: Lookup (Document)

**Planned:**
---
### Discussion Item
**Completed:**
- Name: Text
- Discussion Number: Text
- General Category: Choice (General Category)
- Raised By: Lookup (Contact)
- Raised Date: Date
- Priority: Choice (Priority)
- Action Status: Choice (Action Status)
- Related Decision: Lookup (Formal Decision)
- Description: Memo
- Discussion Notes: Memo
- Outcome: Memo

**Added:**
- Parent Discussion Item: Lookup (Discussion Item)

**Planned:**
---
### After Action Report
**Completed:**
- Name: Text
- Report Number: Text
- Report Date: Date
- Reporting Organization Unit: Lookup (Organization Unit)
- Report Author: Lookup (Contact)
- Event Date: Date
- General Category: Choice (General Category)
- Overall Assessment: Choice (Overall Result)
- Related Initiative: Lookup (Organization Initiative)
- Executive Summary: Memo
- What Went Well: Memo
- Areas for Improvement: Memo
- Recommendations: Memo
- Supporting Document: Lookup (Document)

**Planned:**
---
## Legal & Compliance

### Legal Authority
**Completed:**
- Name: Text
- Authority Type: Choice (Legal Authority Type)
- Authority Status: Choice (Legal Authority Status)
- Jurisdiction Level: Choice (Jurisdiction Level)
- Citation: Text, Max Length: 200
- Parent Legal Authority: Lookup (Legal Authority)
- Enactment Date: Date
- Effective Date: Date
- Expiration Date: Date
- Issuing Authority: Lookup (Account)
- Description: Memo
- Summary: Memo
- Document: Lookup (Document)

**Planned:**
---
### Legal Amendment
**Completed:**
- Name: Text
- Original Authority: Lookup (Legal Authority)
- Amendment Number: Text
- Amendment Date: Date
- Effective Date: Date
- Legal Authority Impact: Choice (Legal Authority Impact)
- Description: Memo
- Changes Summary: Memo
- Document: Lookup (Document)

**Planned:**
---
### Legal Cross-Reference
**Completed:**
- Name: Text
- Primary Authority: Lookup (Legal Authority)
- Related Authority: Lookup (Legal Authority)
- General Category: Choice (General Category)
- Impact: Choice (Impact)
- Description: Memo

**Planned:**
---
### Compliance Framework
**Completed:**
- Name: Text
- Framework Code: Text
- Framework Category: Lookup (Compliance Framework Category)
- Issuing Organization: Lookup (Account)
- Version: Text
- Effective Date: Date
- Publication Status: Choice (Publication Status)
- Description: Memo
- Scope: Memo
- Supporting Document: Lookup (Document)

**Added:**
- Parent Compliance Framework: Lookup (Compliance Framework)

**Planned:**
---
### Compliance Framework Category
**Completed:**
- Name: Text
- Category Code: Text
- Description: Memo

**Added:**
- Parent Compliance Framework Category: Lookup (Compliance Framework Category)

**Planned:**

---

### Compliance Requirement
**Completed:**
- Name: Text
- Requirement Number: Text
- Compliance Framework: Lookup (Compliance Framework)
- Compliance Framework Category: Lookup (Compliance Framework Category)
- Legal Authority: Lookup (Legal Authority)
- General Category: Choice (General Category)
- Priority: Choice (Priority)
- Compliance Status: Choice (Compliance Status)
- Responsible Organization Unit: Lookup (Organization Unit)
- Description: Memo
- Control Objective: Memo
- Supporting Document: Lookup (Document)

**Added:**
- Parent Compliance Requirement: Lookup (Compliance Requirement)

**Planned:**
---
## Risk & Impact

### Analysis
**Completed:**
- Name: Text
- Analysis Number: Text
- General Category: Choice (General Category)
- Analysis Date: Date
- Conducted By: Lookup (User)
- Owning Organization Unit: Lookup (Organization Unit)
- Action Status: Choice (Action Status)
- Description: Memo
- Findings: Memo
- Recommendations: Memo
- Supporting Document: Lookup (Document)

**Planned:**

---
### Risk Item
**Completed:**
- Name: Text
- Risk Number: Text
- General Category: Choice (General Category)
- Identified Date: Date
- Identified By: Lookup (Contact)
- Identified By User: Lookup (User)
- Owning Organization Unit: Lookup (Organization Unit)
- Likelihood: Choice (High Medium Low)
- Severity: Choice (Severity Level)
- Overall Risk Level: Choice (High Medium Low)
- Action Status: Choice (Action Status)
- Description: Memo
- Impact Description: Memo
- Mitigation Strategy: Memo

**Added:**
- Parent Risk Item: Lookup (Risk Item)
- Analysis: Lookup (Analysis)

**Planned:**

---
### Impact
**Completed:**
- Name: Text
- General Category: Choice (General Category)
- Impact Date: Date
- Affected Organization Unit: Lookup (Organization Unit)
- Severity: Choice (Severity Level)
- Direction: Choice (Direction)
- Polarity: Choice (Polarity)
- Related Risk: Lookup (Risk Item)
- Description: Memo
- Financial Impact: Currency
- Mitigation Actions: Memo

**Added:**
- Parent Impact: Lookup (Impact)
- Analysis: Lookup (Analysis)

**Planned:**

---

## Content & Documentation

### Document
**Completed:**
- Name: Text
- Document Number: Text
- General Category: Choice (General Category)
- Version: Text
- Publication Date: Date
- Publication Status: Choice (Publication Status)
- Author: Lookup (User)
- External Author: Lookup (Contact)
- Owning Organization Unit: Lookup (Organization Unit)
- Security Classification: Choice (Security Classification)
- Description: Memo
- File Name: Text
- File URL: URL
- File Size: Integer

**Planned:**
---
### Content Template
**Completed:**
- Name: Text
- General Category: Choice (General Category)
- Template Content: Memo
- Description: Memo
- Version: Text
- Effective Date: Date

**Planned:**
---
## Privacy

### Privacy Consent
**Completed:**
- Name: Text
- Person: Lookup (Contact)
- User: Lookup (User)
- General Category: Choice (General Category)
- Consent Date: Date
- Consent Status: Yes / No
- Expiration Date: Date
- Revoked Date: Date
- Revoked By: Lookup (Contact)
- Purpose: Memo
- Scope: Memo
- Supporting Document: Lookup (Document)

**Planned:**
---
## Product

### Product
**Completed:**
- Name: Text
- Product Code: Text
- General Category: Choice (General Category)
- Unit of Issue: Choice (Unit of Issue)
- Unit Price: Currency
- Description: Memo
- Specifications: Memo

**Planned:**
---
## Financial Periods

### Fiscal Period
Represents time periods used for financial reporting, budgeting, and accounting cycles. Supports hierarchical structures (e.g., Fiscal Year containing Quarters containing Months) for flexible period-based reporting and controls.

**Completed:**

**Planned:**
- Name: Text
- Period Code: Text
- Parent Fiscal Period: Lookup (Fiscal Period)
- Fiscal Year: Text
- Period Type: Choice (Period Type)
- Start Date: Date
- End Date: Date
- Period Status: Choice (Period Status)
- Sequence Number: Integer
- Description: Memo

---
## ✅ Global / Reusable Choice Fields

**Completed:**

### Action Status
Status of action items or tasks.
- New (Not Started)
- In Progress
- Submitted for Review
- Review In Progress
- Returned
- Complete
- Cancelled
- Deferred (On Hold)

### Approval Status
Tracks approval workflow status.
- Pending
- Approved
- Rejected
- Cancelled
- Returned
- Recalled

### Method of Receipt
How items or requests were received.
- Web Portal
- Phone
- Email
- In Person
- Fax
- Mail
- Social Media

### Priority
Standard priority levels.
- Low
- Medium
- High
- Critical

### Yes No
Standard Yes/No choice set (already created in Core).
- No
- Yes

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

### Visibility
Controls who can view records (e.g., Public, Internal, Restricted).
- Public
- Internal
- Restricted
- Confidential

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
Generic categorization field for flexible classification across multiple domains.
- Access Control & Identity Management
- Asset & Logistics Management
- Compliance & Regulatory
- Cybersecurity
- Data Privacy & Protection
- Environmental Compliance
- Ethics & Governance
- Financial Management
- Foreign Interests
- Health & Safety
- Human Resources & Workforce
- Incident & Disaster Response
- Information Management & Records
- National Security
- Operational Resilience
- Procurement & Contract Management
- Public Relations & Communication
- Risk Management
- Technology & Innovation
- Training & Development

### Impact
Classifies the nature and scope of impact.
- Direct
- Indirect
- Minimal
- None
- Unknown

### Period Type
Defines the type of fiscal or reporting period.
- Month
- Quarter
- Half Year
- Fiscal Year
- Calendar Year
- Biennial
- Custom Period

### Period Status
Status of a financial or reporting period.
- Future
- Open
- Closed
- Locked
- Adjusted

### Task Dependency Type
- Finish to Start
- Finish to Finish
- Start to Start
- Start to Finish
- Informational
- Resource Dependency

### Task Dependency Status
- Active
- Satisfied
- Blocked
- At Risk
- Cancelled

### Assignment Status
- Active
- Pending Return
- Returned
- Overdue
- Cancelled

### Payment Status
- Pending
- Partial
- Paid
- Disputed
- Refunded

### Decision Category
- Scope Change
- Timeline Extension
- Budget Reallocation
- Accountability Reassignment
- Approach Modification
- Priority Adjustment
- Resource Addition
- Dependency Change
- Requirement Clarification
- Risk Mitigation
- Termination
- Hold

### Verification Status
- Verified
- Not Found
- Discrepancy Found
- Pending Investigation
- Resolved

**Completed Last Round:**
 
 - Added Extended to Schedule Status

**Planned:**



