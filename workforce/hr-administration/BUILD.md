# 👥 HR Administration — Data Model Design

The **HR Administration module** manages the core employment structure, transactions, and workforce recordkeeping for an organization. It supports position and classification management (positions, job classifications, grades, and ranks), effective-dated employment actions (promotions, reassignments, pay changes, milestones), employee requests (time off, telework, overtime, workplace accommodations, declarations), and related compliance tracking through governing authorities and structured approvals. Typical use cases include maintaining authorized staffing structures, processing personnel actions, tracking leave and overtime activity, managing accommodation workflows, administering grade/rank frameworks in government or structured environments, and maintaining accurate historical employment records. The module serves as the operational system of record for the employee lifecycle while remaining distinct from recruiting, benefits, and performance management.

---

## Position & Classification Management

### HR Position
**Completed:**
- Name: Text
- Position Number: Text
- Full Time Equivalent: Float
- Authorized Date: Date
- Effective Start Date: Date
- Effective End Date: Date
- Bargaining Unit: Text
- Budget Code: Text
- Description: Memo
- HR Job Classification: Lookup (HR Job Classification)
- Location: Lookup (Location)
- Organization Unit: Lookup (Organization Unit)
- Job Series: Lookup (Job Series)
- Pay Grade: Lookup (Pay Grade)
- Grade Rank: Lookup (Grade-Rank)
- Personnel Type: Lookup (Personnel Type)
- Required Clearance Level: Lookup (Clearance Level)
- Reports To Position: Lookup (HR Position)
- HR Position Status: Choice (HR Position Status)
- Is Supervisory: Yes / No
- Is Management: Yes / No
- Requires Clearance: Yes / No

**Skipped:**
- Position Title: Text
- Notes: Memo
- Position Designation: Choice (Position Designation)
- Employment Type: Choice (Employment Type)

**Planned:**
---
### HR Position Assignment
Links an employee to a position for a defined period, including reporting structure and assignment details.

**Completed:**
- Person: Lookup (Person)
- HR Position: Lookup (HR Position)
- HR Assignment Type: Choice (HR Assignment Type)
- HR Assignment Status: Choice (HR Assignment Status)
- Start Date: Date
- End Date: Date
- Full Time Equivalent: Float
- Reports To Person: Lookup (Person)
- Reports To Position: Lookup (HR Position)
- Organization Unit: Lookup (Organization Unit)
- Location: Lookup (Location)
- Description: Memo
- Is Primary: Yes / No

**Planned:**

---

### HR Position Description
**Completed:**
- HR Position: Lookup (HR Position)
- Version Number: Text
- Effective Date: Date
- Purpose: Memo
- Primary Duties: Memo
- Key Responsibilities: Memo
- Required Qualifications: Memo
- Preferred Qualifications: Memo
- Physical Requirements: Memo
- Working Conditions: Memo
- Supervisory Responsibilities: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Supporting Document: Lookup (Document)
- Description: Memo
- Description Status: Choice (Publication Status)

**Planned:**
---
### HR Job Classification
Represents a defined job role or classification (title, exempt status, bargaining unit, etc.) used to categorize positions.

**Completed:**
- Classification Code: Text
- Job Series: Lookup (Job Series)
- Classification Level: Integer
- FLSA Status: Choice (Exemption Status)
- Standard Occupational Code: Text
- Default Pay Grade: Lookup (Pay Grade)
- Is Supervisory: Yes / No
- Is Management: Yes / No
- Requires Certification: Yes / No
- Bargaining Unit Eligible: Yes / No
- Default Bargaining Unit: Text
- Description: Memo

**Planned:**

---

## Employment Actions & Lifecycle

### HR Employment Action
**Completed:**

- Name: Text
- Action Number: Text
- HR Action Type: Lookup (HR Action Type)
- Person: Lookup (Person)
- Action Status: Choice (Action Status)
- Requested Date: Date
- Effective Date: Date
- Processed Date: Date
- Requested By: Lookup (Person)
- Processed By: Lookup (Person)
- From Position: Lookup (HR Position)
- To Position: Lookup (HR Position)
- From Organization Unit: Lookup (Organization Unit)
- To Organization Unit: Lookup (Organization Unit)
- From Pay Grade: Lookup (Pay Grade)
- To Pay Grade: Lookup (Pay Grade)
- From Grade Rank: Lookup (Grade-Rank)
- To Grade Rank: Lookup (Grade-Rank)
- From Location: Lookup (Location)
- To Location: Lookup (Location)
- From Salary: Currency
- To Salary: Currency
- From Employment Type: Choice (Employment Type)
- To Employment Type: Choice (Employment Type)
- From FTE: Float
- To FTE: Float
- Legal Authority: Lookup (Legal Authority)
- Justification: Memo
- Impact on Employee: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Notes: Memo

**Planned:**
---
### HR Action Type
**Completed:**

- Name: Text
- Action Category: Choice (Action Category)
- Description: Memo
- Requires Approval: Yes / No

**Planned:**
---
### HR Employment Milestone
**Completed:**

- Name: Text
- Person: Lookup (Person)
- Milestone Type: Choice (Milestone Type)
- Milestone Date: Date
- Milestone Status: Choice (Milestone Status)
- Years of Service: Integer
- Recorded Date: Date
- Recorded By: Lookup (Person)
- Notification Sent: Yes / No
- Notification Date: Date
- Recognition Provided: Yes / No
- Description: Memo
- Notes: Memo

**Planned:**
---
### HR Disciplinary Action
**Completed:**

- Person: Lookup (Person)
- Disciplinary Action Type: Choice (Disciplinary Action Type)
- Action Status: Choice (Action Status)
- Issue Date: Date
- Effective Date: Date
- Expiration Date: Date
- Issuing Authority: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Legal Authority: Lookup (Legal Authority)
- Incident Date: Date
- Incident Description: Memo
- Violation Type: Memo
- Action Taken: Memo
- Employee Response: Memo
- Appeal Filed: Yes / No
- Appeal Date: Date
- Appeal Outcome: Choice (Overall Result)
- Supporting Document: Lookup (Document)
- Security Classification: Choice (Security Classification)
- Visibility: Choice (Visibility)

**Planned:**
- Name: Text
- Notes: Memo
---
## Employee Requests

### HR Request
**Completed:**

- Request Number: Text
- Request Type: Choice (HR Request Type)
- Request Status: Choice (Request Status)
- Person: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Request Date: Date
- Requested Start Date: Date
- Requested End Date: Date
- Priority: Choice (Priority)
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Denial Reason: Memo
- Description: Memo

**Planned:**
- Name: Text
- Notes: Memo
---
### HR Time Off Request
Represents the header record for employee leave requests, including leave type, period, and approval status.

**Completed:**
- Name: Text
- HR Request: Lookup (HR Request)
- Person: Lookup (Person)
- Leave Type: Choice (HR Leave Type)
- Request Status: Choice (Request Status)
- Request Date: Date
- Start Date: Date
- End Date: Date
- Total Hours Requested: Float
- Total Hours Approved: Float
- Total Hours Taken: Float
- Return Date: Date
- Reason: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Denial Reason: Memo
- Contact During Leave: Text
- Emergency Contact: Text
- Supporting Document: Lookup (Document)

**Planned:**

---

### HR Time Off Entry
Stores individual leave date entries tied to a time off request (specific dates and hours).

**Completed:**
- Name: Text
- HR Time Off Request: Lookup (HR Time Off Request)
- Person: Lookup (Person)
- Entry Date: Date
- Hours: Float
- Approval Status: Choice (Approval Status)
- Leave Type: Choice (HR Leave Type)
- Notes: Memo

**Planned:**

---

### HR Overtime Entry
Captures individual overtime or compensatory time work entries, including date, hours, type, and rate.

**Completed:**
- Name: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Work Date: Date
- Hours Worked: Float
- Overtime Type: Choice (Overtime Type)
- Overtime Rate: Float
- Total Pay: Currency
- Justification: Memo
- Entry Status: Choice (Entry Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Pay Period: Text
- Project Code: Text
- Notes: Memo

**Planned:**

---

### HR Telework Request
Captures employee requests for telework or remote work arrangements, including schedule and approval details.

**Completed:**
- Name: Text
- HR Request: Lookup (HR Request)
- Person: Lookup (Person)
- Telework Type: Choice (Telework Type)
- Request Status: Choice (Request Status)
- Request Date: Date
- Start Date: Date
- End Date: Date
- Frequency: Choice (Telework Frequency)
- Primary Telework Location: Lookup (Location)
- Telework Address: Text
- Schedule Description: Memo
- Business Justification: Memo
- Equipment Needs: Memo
- Internet Speed Available: Text
- Supervisor: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Agreement Date: Date
- Notes: Memo
- Agreement Signed: Yes / No
- Safety Checklist Completed: Yes / No

**Planned:**

---

### HR Workplace Accommodation
Tracks requests and fulfillment of workplace accommodations, including approval workflow and implementation details.

**Completed:**
- Name: Text
- HR Request: Lookup (HR Request)
- Person: Lookup (Person)
- Accommodation Type: Choice (Accommodation Type)
- Request Status: Choice (Request Status)
- Request Date: Date
- Need Description: Memo
- Requested Accommodation: Memo
- Documentation Date: Date
- Interactive Process Date: Date
- Approved Accommodation: Memo
- Implementation Date: Date
- Implementation Cost: Currency
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Denial Reason: Memo
- Review Date: Date
- End Date: Date
- Effectiveness Evaluation: Memo
- Privacy Consent: Lookup (Privacy Consent)
- Security Classification: Choice (Security Classification)
- Supporting Document: Lookup (Document)
- Notes: Memo
- Interactive Process Started: Yes / No
- Medical Documentation Provided: Yes / No
- Is Temporary: Yes / No

**Planned:**

---

### HR Employee Declaration
Captures employee-submitted attestations or disclosures (e.g., conflict of interest, outside employment, ethics certifications).

**Completed:**
- Name: Text
- Person: Lookup (Person)
- Declaration Type: Choice (Declaration Type)
- Declaration Status: Choice (Simple Certification Status)
- Submission Date: Date
- Effective Date: Date
- Expiration Date: Date
- Declaration Content: Memo
- Reviewed By: Lookup (Person)
- Review Date: Date
- Review Comments: Memo
- Attestation Date: Date
- Legal Authority: Lookup (Legal Authority)
- Compliance Framework: Lookup (Compliance Framework)
- Supporting Document: Lookup (Document)
- Security Classification: Choice (Security Classification)
- Notes: Memo
- Requires Review: Yes / No
- Attestation: Yes / No

**Planned:**

---

### HR Leave Donation
Records voluntary transfer or donation of leave hours from one employee to another, including approval and balance impact.

**Completed:**
- Name: Text
- Donor: Lookup (Person)
- Recipient: Lookup (Person)
- Donation Date: Date
- Leave Type Donated: Choice (Leave Type)
- Leave Type Received: Choice (Leave Type)
- Hours Donated: Float
- Hours Received: Float
- Conversion Rate: Float
- Justification: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Processing Status: Choice (Entry Status)
- Processed Date: Date
- Donor Balance Before: Float
- Donor Balance After: Float
- Recipient Balance Before: Float
- Recipient Balance After: Float
- Notes: Memo

**Planned:**

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Represents employees throughout the module for assignments, actions, requests, and history.

### Organization Unit *(Core)*
Departmental and divisional structure for position placement and reporting hierarchy.

### Location *(Core)*
Work locations for positions, assignments, and telework arrangements.

### Pay Grade *(Core)*
Salary grade structures referenced by positions, classifications, and employment actions.

### Grade-Rank *(Core)*
Combined grade and rank structures for uniformed or hierarchical organizations.

### Job Series *(Core)*
Broader job family groupings for classifications and positions.

### Personnel Type *(Core)*
Classification of employment categories (civilian, uniformed, contractor, etc.).

### Clearance Level *(Core)*
Security clearance requirements for positions.

### Legal Authority *(Core)*
Used as HR Governing Authority for employment actions, disciplinary actions, and declarations.

### Compliance Framework *(Core)*
Referenced for regulatory compliance in declarations and accommodations.

### Privacy Consent *(Core)*
Required for sensitive accommodation requests and medical information.

### Document *(Core)*
Supporting documentation for requests, descriptions, actions, and declarations.

### Content Template *(Core)*
Templates for position descriptions, offers, and standardized documents.

---

## New Choice Fields

**Completed:**

- HR Position Status
- HR Assignment Type
- HR Assignment Status
- Exemption Status
- HR Action Category
- HR Milestone Type
- Milestone Status
- HR Request Type
- Approval Status
- HR Disciplinary Action Type
- HR Leave Type
- HR Overtime Type
- HR Telework Type
- Schedule Frequency
- HR Declaration Type
- HR Accommodation Type

**Planned:**

