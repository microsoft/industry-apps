# ⚖️ Court Case Management — Data Model Design

## Court Case

The primary record representing a legal matter before the court.
Tracks case number, type, jurisdiction, status, assigned judge, and overall lifecycle of the matter.

**Completed:**
- Case Number: Text
- Case Title: Text
- Case Type: Choice (Court Case Type)
- Court Case Stage: Choice (Court Case Stage)
- Priority: Choice (Priority)
- Filing Date: Date
- Close Date: Date
- Last Action Date: Date
- Next Hearing Date: Date
- Judicial District: Lookup (Judicial District)
- Assigned Judge: Lookup (Person)
- Court Location: Lookup (Location)
- Organization Unit: Lookup (Organization Unit)
- Related Case: Lookup (Court Case)
- Case Relationship Type: Choice (Case Relationship Type)
- Security Classification: Choice (Security Classification)
- Visibility: Choice (Visibility)
- Is Sealed: Yes / No
- Jury Trial Requested: Yes / No
- Settlement Amount: Currency
- Description: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Decision

Records a judicial ruling or determination made in a case.
Captures the decision type, date, deciding official, and links to related hearings or filings. May represent interim or final decisions.

**Completed:**
- Decision Number: Text
- Decision Title: Text
- Decision Type: Choice (Court Decision Type)
- Decision Date Time: Date Time
- Court Case: Lookup (Court Case)
- Deciding Official: Lookup (Person)
- Related Hearing: Lookup (Court Case Hearing)
- Related Filing: Lookup (Court Case Filing)
- Is Final Decision: Yes / No
- Overall Result: Choice (Overall Result)
- Appeal Status: Choice (Appeal Status)
- Appealed Date: Date
- Publication Status: Choice (Publication Status)
- Supporting Document: Lookup (Document)
- Legal Authority: Lookup (Legal Authority)
- Description: Memo
- Legal Reasoning: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Docket Entry

The official chronological log entry for activity in a case.
Provides an audit-friendly record of filings, hearings, orders, and other significant case events.

**Completed:**
- Entry Number: Text
- Entry Date Time: Date Time
- Court Case: Lookup (Court Case)
- Entry Type: Choice (Court Docket Entry Type)
- Filed By: Lookup (Person)
- Filed By Organization: Lookup (Account)
- Related Filing: Lookup (Court Case Filing)
- Related Hearing: Lookup (Court Case Hearing)
- Related Order: Lookup (Court Case Order)
- Related Decision: Lookup (Court Case Decision)
- Security Classification: Choice (Security Classification)
- Supporting Document: Lookup (Document)
- Is Public Record: Yes / No
- Description: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Filing

Represents a document or submission formally entered into the case record.
Includes motions and other filings submitted by parties or external entities, along with filing date and status.

**Completed:**
- Filing Number: Text
- Filing Title: Text
- Filing Type: Choice (Court Filing Type)
- Filing Date Time: Date Time
- Court Case: Lookup (Court Case)
- Filed By Party: Lookup (Court Case Party)
- Filed By Person: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Priority: Choice (Priority)
- Response Due Date: Date
- Response Received Date: Date
- Filing Fee Amount: Currency
- Payment Status: Choice (Payment Status)
- Document: Lookup (Document)
- Page Count: Integer
- Is Electronic Filing: Yes / No
- Organization Unit: Lookup (Organization Unit)
- Description: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Hearing

Represents a scheduled case appearance or proceeding. May be associated with a Court Session and records hearing type, scheduling details, and results.

**Completed:**
- Hearing Number: Text
- Hearing Title: Text
- Hearing Type: Choice (Court Hearing Type)
- Scheduled Date Time: Date Time
- Actual Start Date Time: Date Time
- Actual End Date Time: Date Time
- Duration Minutes: Integer
- Court Case: Lookup (Court Case)
- Court Session: Lookup (Court Session)
- Presiding Official: Lookup (Person)
- Court Reporter: Lookup (Person)
- Location: Lookup (Location)
- Participation Mode: Choice (Participation Mode)
- Hearing Stage: Choice (Court Hearing Stage)
- Overall Result: Choice (Overall Result)
- Attendance Status: Choice (Attendance Status)
- Priority: Choice (Priority)
- Is Sealed Hearing: Yes / No
- Recording Available: Yes / No
- Transcript Available: Yes / No
- Description: Memo
- Hearing Notes: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Order

Represents a formal directive issued by the court. Often generated from a decision, and may include effective dates, status (draft/issued), and compliance implications.

**Completed:**
- Order Number: Text
- Order Title: Text
- Order Type: Choice (Court Order Type)
- Issue Date: Date
- Effective Date: Date
- Expiration Date: Date
- Court Case: Lookup (Court Case)
- Court Case Decision: Lookup (Court Case Decision)
- Issuing Official: Lookup (Person)
- Order Stage: Choice (Court Order Stage)
- Priority: Choice (Priority)
- Responsible Party: Lookup (Court Case Party)
- Compliance Due Date: Date
- Compliance Status: Choice (Compliance Status)
- Compliance Requirement: Lookup (Compliance Requirement)
- Document: Lookup (Document)
- Is Temporary: Yes / No
- Appeal Status: Choice (Appeal Status)
- Description: Memo
- Compliance Notes: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Party

Links a person or organization to a case in a defined role.
Used to track plaintiffs, defendants, petitioners, respondents, and other involved parties.

**Completed:**
- Party Role: Choice (Court Party Role)
- Party Type: Choice (Court Party Type)
- Court Case: Lookup (Court Case)
- Person: Lookup (Person)
- Account: Lookup (Account)
- Start Date: Date
- End Date: Date
- Is Primary Party: Yes / No
- Party Status: Choice (Lifecycle Stage)
- Representation Required: Yes / No
- Is Pro Se: Yes / No
- Contact Method: Choice (Method of Contact)
- Notification Email: Text
- Notification Phone: Text
- Service Address Line 1: Text
- Service Address City: Text
- Service Address State: Lookup (State or Province)
- Service Address Postal Code: Text
- Description: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Representation

Tracks representation relationships within a case.
Identifies which party is represented by which attorney, guardian, or agent, including effective dates.

**Completed:**
- Court Case: Lookup (Court Case)
- Court Case Party: Lookup (Court Case Party)
- Representative: Lookup (Person)
- Representative Organization: Lookup (Account)
- Representation Type: Choice (Court Representation Type)
- Start Date: Date
- End Date: Date
- Operational Status: Choice (Lifecycle Stage)
- Is Lead Counsel: Yes / No
- Bar Number: Text
- Bar State: Lookup (State or Province)
- Admission Date: Date
- Pro Hac Vice: Yes / No
- Contact Email: Text
- Contact Phone: Text
- Description: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Case Work Item

Represents internal court staff tasks related to advancing a case.
Includes assignments, due dates, status, and links to related filings, hearings, or orders.

**Completed:**
- Work Item Number: Text
- Work Item Title: Text
- Court Case: Lookup (Court Case)
- Work Item Type: Choice (Court Work Item Type)
- General Category: Choice (General Category)
- Priority: Choice (Priority)
- Action Status: Choice (Action Status)
- Assigned To: Lookup (Person)
- Assigned By: Lookup (User)
- Assigned Date: Date
- Due Date: Date
- Completion Date: Date
- Organization Unit: Lookup (Organization Unit)
- Estimated Hours: Decimal
- Actual Hours: Decimal
- Related Filing: Lookup (Court Case Filing)
- Related Hearing: Lookup (Court Case Hearing)
- Related Order: Lookup (Court Case Order)
- Related Decision: Lookup (Court Case Decision)
- Supporting Document: Lookup (Document)
- Description: Memo
- Resolution Notes: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## Court Session

Represents a scheduled sitting of the court.
Defines the date, location, presiding official, and status of a court calendar block during which one or more case hearings may occur.

**Completed:**
- Session Number: Text
- Session Title: Text
- Session Type: Choice (Court Session Type)
- Session Date: Date
- Start Time: Date Time
- End Time: Date Time
- Presiding Official: Lookup (Person)
- Court Reporter: Lookup (Person)
- Bailiff: Lookup (Person)
- Location: Lookup (Location)
- Courtroom Number: Text
- Court: Lookup (Organization Unit)
- Operational Status: Choice (Lifecycle Stage)
- Participation Mode: Choice (Participation Mode)
- Capacity: Integer
- Is Public Session: Yes / No
- Is Emergency Session: Yes / No
- Description: Memo
- Session Notes: Memo

**Completed Last Round:**
- Configure Main form (Information)
- Configure Active view

**Planned:**

---

## ✅ New Choice Fields for Court Case Management - Reviewed

**Completed:**

### Court Case Stage
Values representing the lifecycle stage of a case:
- Filed
- Active
- In Hearing
- Under Review
- Pending Decision
- Decided
- Appealed
- Closed
- Dismissed
- Settled

### Court Case Type
Categories of legal matters:
- Civil
- Criminal
- Family
- Probate
- Juvenile
- Traffic
- Small Claims
- Administrative
- Bankruptcy
- Appeals

### Court Decision Type
Categories of judicial determinations:
- Preliminary Ruling
- Interlocutory Order
- Summary Judgment
- Final Judgment
- Verdict
- Sentencing
- Dismissal
- Default Judgment
- Consent Decree

### Court Docket Entry Type
Categories of docket entries:
- Filing Received
- Hearing Scheduled
- Hearing Held
- Order Issued
- Decision Rendered
- Party Added
- Motion Filed
- Evidence Submitted
- Continuance Granted
- Status Update

### Court Filing Type
Categories of document submissions:
- Complaint
- Answer
- Motion
- Brief
- Affidavit
- Exhibit
- Notice
- Stipulation
- Petition
- Response
- Reply
- Memorandum

### Court Hearing Type
Categories of court proceedings:
- Initial Appearance
- Arraignment
- Pre-Trial Conference
- Motion Hearing
- Trial
- Sentencing
- Status Conference
- Settlement Conference
- Evidentiary Hearing
- Appeals Hearing

### Court Hearing Stage
- Scheduled
- Preparation
- Called to Order
- In Session
- Recessed
- Continued
- Under Deliberation
- Decision Issued
- Recorded
- Closed

### Court Order Type
Categories of court directives:
- Temporary Order
- Permanent Order
- Protective Order
- Restraining Order
- Consent Order
- Default Order
- Enforcement Order
- Modification Order
- Show Cause Order
- Dismissal Order

### Court Order Stage
- Drafting
- Under Review
- Ready for Issuance
- Issued
- Entered on Record
- Served / Notified
- Effective
- Monitoring Compliance
- Satisfied
- Closed

### Court Party Role
Role of a party in the case:
- Plaintiff
- Defendant
- Petitioner
- Respondent
- Claimant
- Appellant
- Appellee
- Intervener
- Amicus Curiae
- Third Party

### Court Party Type
Classification of party entity:
- Individual
- Corporation
- Partnership
- Government Entity
- Non-Profit Organization
- Trust
- Estate
- Minor
- Guardian
- Conservator

### Court Representation Type
Nature of the representation relationship:
- Retained Counsel
- Court Appointed Counsel
- Public Defender
- Guardian Ad Litem
- Legal Guardian
- Conservator
- Power of Attorney
- Pro Bono Counsel
- Special Counsel

### Court Work Item Type
Categories of internal tasks:
- Document Review
- Filing Processing
- Hearing Preparation
- Order Preparation
- Correspondence
- Research
- Scheduling
- Notification
- Compliance Check
- Case Closure

### Court Session Type
Categories of court sessions:
- Regular Session
- Special Session
- Emergency Session
- Settlement Conference
- Status Conference
- Calendar Call
- Motion Docket
- Trial Docket

**Completed Last Round:**

**Planned:**



