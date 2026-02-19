
## 1) Court Case

The primary record representing a legal matter before the court.
Tracks case number, type, jurisdiction, status, assigned judge, and overall lifecycle of the matter.

**Fields:**
- Case Number | Text
- Case Title | Text
- Case Type | Choice
- Court Case Status | Choice
- Priority | Choice *(reuse from Core)*
- Filing Date | Date
- Close Date | Date
- Judicial District | Lookup *(to Judicial District from Core)*
- Assigned Judge | Lookup *(to Person from Core)*
- Court Location | Lookup *(to Location from Core)*
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Description | Memo
- Details | Memo

---

## 2) Court Case Decision

Records a judicial ruling or determination made in a case.
Captures the decision type, date, deciding official, and links to related hearings or filings. May represent interim or final decisions.

**Fields:**
- Decision Number | Text
- Decision Title | Text
- Decision Type | Choice
- Decision Date Time | Date Time
- Court Case | Lookup *(to Court Case)*
- Deciding Official | Lookup *(to Person from Core)*
- Related Hearing | Lookup *(to Court Case Hearing)*
- Related Filing | Lookup *(to Court Case Filing)*
- Is Final Decision | Yes / No
- Overall Result | Choice *(reuse from Core)*
- Description | Memo
- Details | Memo

---

## 3) Court Case Docket Entry

The official chronological log entry for activity in a case.
Provides an audit-friendly record of filings, hearings, orders, and other significant case events.

**Fields:**
- Entry Number | Text
- Entry Date Time | Date Time
- Court Case | Lookup *(to Court Case)*
- Entry Type | Choice
- Filed By | Lookup *(to Person from Core)*
- Related Filing | Lookup *(to Court Case Filing)*
- Related Hearing | Lookup *(to Court Case Hearing)*
- Related Order | Lookup *(to Court Case Order)*
- Description | Memo

---

## 4) Court Case Filing

Represents a document or submission formally entered into the case record.
Includes motions and other filings submitted by parties or external entities, along with filing date and status.

**Fields:**
- Filing Number | Text
- Filing Title | Text
- Filing Type | Choice
- Filing Date Time | Date Time
- Court Case | Lookup *(to Court Case)*
- Filed By Party | Lookup *(to Court Case Party)*
- Filed By Person | Lookup *(to Person from Core)*
- Approval Status | Choice *(reuse from Core)*
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Details | Memo

---

## 5) Court Case Hearing

Represents a scheduled case appearance or proceeding.
May be associated with a Court Session and records hearing type, scheduling details, and results.

**Fields:**
- Hearing Number | Text
- Hearing Title | Text
- Hearing Type | Choice
- Scheduled Date Time | Date Time
- Actual Start Date Time | Date Time
- Actual End Date Time | Date Time
- Court Case | Lookup *(to Court Case)*
- Court Session | Lookup *(to Court Session)*
- Presiding Official | Lookup *(to Person from Core)*
- Location | Lookup *(to Location from Core)*
- Hearing Status | Choice
- Overall Result | Choice *(reuse from Core)*
- Description | Memo
- Details | Memo

---

## 6) Court Case Order

Represents a formal directive issued by the court.
Often generated from a decision, and may include effective dates, status (draft/issued), and compliance implications.

**Fields:**
- Order Number | Text
- Order Title | Text
- Order Type | Choice
- Issue Date | Date
- Effective Date | Date
- Court Case | Lookup *(to Court Case)*
- Court Case Decision | Lookup *(to Court Case Decision)*
- Issuing Official | Lookup *(to Person from Core)*
- Order Status | Choice
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Details | Memo

---

## 7) Court Case Party

Links a person or organization to a case in a defined role.
Used to track plaintiffs, defendants, petitioners, respondents, and other involved parties.

**Fields:**
- Party Role | Choice
- Party Type | Choice
- Court Case | Lookup *(to Court Case)*
- Person | Lookup *(to Person from Core)*
- Account | Lookup *(to Account from Core)*
- Start Date | Date
- End Date | Date
- Is Primary Party | Yes / No
- Description | Memo

---

## 8) Court Case Representation

Tracks representation relationships within a case.
Identifies which party is represented by which attorney, guardian, or agent, including effective dates.

**Fields:**
- Court Case | Lookup *(to Court Case)*
- Court Case Party | Lookup *(to Court Case Party)*
- Representative | Lookup *(to Person from Core)*
- Representation Type | Choice
- Start Date | Date
- End Date | Date
- Operational Status | Choice *(reuse from Core)*
- Description | Memo

---

## 9) Court Case Work Item

Represents internal court staff tasks related to advancing a case.
Includes assignments, due dates, status, and links to related filings, hearings, or orders.

**Fields:**
- Work Item Number | Text
- Work Item Title | Text
- Court Case | Lookup *(to Court Case)*
- Work Item Type | Choice
- Priority | Choice *(reuse from Core)*
- Action Status | Choice *(reuse from Core)*
- Assigned To | Lookup *(to Person from Core)*
- Due Date | Date
- Completion Date | Date
- Related Filing | Lookup *(to Court Case Filing)*
- Related Hearing | Lookup *(to Court Case Hearing)*
- Related Order | Lookup *(to Court Case Order)*
- Description | Memo
- Details | Memo

---

## 10) Court Session

Represents a scheduled sitting of the court.
Defines the date, location, presiding official, and status of a court calendar block during which one or more case hearings may occur.

**Fields:**
- Session Number | Text
- Session Title | Text
- Session Date | Date
- Start Time | Date Time
- End Time | Date Time
- Presiding Official | Lookup *(to Person from Core)*
- Location | Lookup *(to Location from Core)*
- Court | Lookup *(to Organization Unit from Core)*
- Operational Status | Choice *(reuse from Core)*
- Description | Memo

---

## ✅ New Choice Fields for Court Case Management

### Court Case Status
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

### Case Type
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

### Decision Type
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

### Entry Type
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

### Filing Type
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

### Hearing Type
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

### Hearing Status
Current state of a scheduled hearing:
- Scheduled
- Confirmed
- Postponed
- In Progress
- Completed
- Cancelled
- Continued
- Vacated

### Order Type
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

### Order Status
Current state of an order:
- Draft
- Issued
- Served
- In Effect
- Stayed
- Vacated
- Expired
- Superseded

### Party Role
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

### Party Type
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

### Representation Type
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

### Work Item Type
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

