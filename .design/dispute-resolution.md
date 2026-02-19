
## **Dispute**

Represents the primary case record for a formal internal dispute or complaint.
Tracks lifecycle status, case type, regulatory framework, assigned staff, key dates, and overall outcome.

**Fields:**
- Case Number | Text
- Case Title | Text
- Dispute Type | Choice
- Dispute Status | Choice
- Priority | Choice *(reuse from Core)*
- Severity Level | Choice *(reuse from Core)*
- Filed Date | Date
- Close Date | Date
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Case Manager | Lookup *(to Person from Core)*
- Compliance Framework | Lookup *(to Compliance Framework from Core)*
- Legal Authority | Lookup *(to Legal Authority from Core)*
- Is Confidential | Yes / No
- Is Anonymous | Yes / No
- Overall Result | Choice *(reuse from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Appeal**

Represents a formal challenge to a determination or decision.
Tracks appeal authority, filing date, appeal basis, review process, and final appellate outcome.

**Fields:**
- Appeal Number | Text
- Appeal Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Determination | Lookup *(to Dispute Determination)*
- Appeal Basis | Choice
- Appeal Date | Date
- Appeal Status | Choice
- Appellant | Lookup *(to Person from Core)*
- Reviewing Authority | Lookup *(to Person from Core)*
- Decision Date | Date
- Decision Due Date | Date
- Overall Result | Choice *(reuse from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Corrective Action**

Tracks actions required as a result of a determination or settlement.
Examples include training requirements, disciplinary measures, policy updates, or monitoring plans.

**Fields:**
- Action Number | Text
- Action Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Determination | Lookup *(to Dispute Determination)*
- Corrective Action Type | Choice
- Corrective Action Status | Choice
- Assigned To | Lookup *(to Person from Core)*
- Responsible Organization | Lookup *(to Organization Unit from Core)*
- Due Date | Date
- Completion Date | Date
- Verification Date | Date
- Verified By | Lookup *(to Person from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Determination**

Represents the formal outcome or decision for a dispute or specific issue.
May include findings, remedies, dismissals, settlements, or final agency decisions.

**Fields:**
- Determination Number | Text
- Determination Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Issue | Lookup *(to Dispute Issue)*
- Determination Type | Choice
- Determination Date | Date
- Effective Date | Date
- Deciding Official | Lookup *(to Person from Core)*
- Approval Status | Choice *(reuse from Core)*
- Overall Result | Choice *(reuse from Core)*
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Evidence**

Stores or references materials collected during investigation.
Examples include documents, communications, records, media files, and external reports.

**Fields:**
- Evidence Number | Text
- Evidence Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Investigation | Lookup *(to Dispute Investigation)*
- Evidence Type | Choice
- Collection Date | Date
- Collected By | Lookup *(to Person from Core)*
- Submitted By | Lookup *(to Person from Core)*
- Document | Lookup *(to Document from Core)*
- Is Confidential | Yes / No
- Chain of Custody | Memo
- Description | Memo

---

## **Dispute Finding**

Captures the conclusion reached for a specific dispute issue after investigation.
Examples: Substantiated, Unsubstantiated, Inconclusive, Policy Violation Confirmed.

**Fields:**
- Finding Number | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Issue | Lookup *(to Dispute Issue)*
- Dispute Investigation | Lookup *(to Dispute Investigation)*
- Finding Type | Choice
- Finding Date | Date
- Inspector | Lookup *(to Person from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Intake**

Represents an initial inquiry, concern, or report prior to formal case creation.
Supports anonymous reporting, early resolution efforts, and triage decisions.

**Fields:**
- Intake Number | Text
- Intake Title | Text
- Intake Status | Choice
- Submission Date Time | Date Time
- Method of Contact | Choice *(reuse from Core)*
- Method of Receipt | Choice *(reuse from Core)*
- Submitted By | Lookup *(to Person from Core)*
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Intake Specialist | Lookup *(to Person from Core)*
- Priority | Choice *(reuse from Core)*
- Is Anonymous | Yes / No
- Converted to Dispute | Lookup *(to Dispute)*
- Conversion Date | Date
- Description | Memo
- Details | Memo

---

## **Dispute Interview**

Tracks interviews conducted as part of an investigation.
Includes interviewee, role, date, summary, and related evidence.

**Fields:**
- Interview Number | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Investigation | Lookup *(to Dispute Investigation)*
- Interview Date Time | Date Time
- Interviewee | Lookup *(to Person from Core)*
- Interviewer | Lookup *(to Person from Core)*
- Interview Type | Choice
- Location | Lookup *(to Location from Core)*
- Duration Minutes | Integer
- Was Recorded | Yes / No
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Notes | Memo

---

## **Dispute Investigation**

Represents the formal investigative process associated with a dispute.
Tracks investigator assignment, scope, timeline, methodology, and completion status.

**Fields:**
- Investigation Number | Text
- Investigation Title | Text
- Dispute | Lookup *(to Dispute)*
- Investigation Status | Choice
- Start Date | Date
- Target Completion Date | Date
- Actual Completion Date | Date
- Lead Investigator | Lookup *(to Person from Core)*
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Investigation Type | Choice
- Methodology | Memo
- Scope | Memo
- Summary | Memo
- Details | Memo

---

## **Dispute Issue**

Defines the specific allegation, claim, or concern within a dispute case.
A single dispute may include multiple issues (e.g., discrimination, retaliation, harassment).

**Fields:**
- Issue Number | Text
- Issue Title | Text
- Dispute | Lookup *(to Dispute)*
- Issue Type | Choice
- Severity Level | Choice *(reuse from Core)*
- Alleged Date | Date
- Alleged By | Lookup *(to Person from Core)*
- Alleged Against | Lookup *(to Person from Core)*
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Legal Authority | Lookup *(to Legal Authority from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Mediation**

Represents a structured mediation or alternative dispute resolution effort.
Tracks mediator, session dates, agreements reached, and mediation outcomes.

**Fields:**
- Mediation Number | Text
- Mediation Title | Text
- Dispute | Lookup *(to Dispute)*
- Mediation Status | Choice
- Scheduled Date Time | Date Time
- Actual Date Time | Date Time
- Mediator | Lookup *(to Person from Core)*
- Location | Lookup *(to Location from Core)*
- Is Voluntary | Yes / No
- Agreement Reached | Yes / No
- Mediation Outcome | Choice
- Agreement | Lookup *(to Agreement from Core)*
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Notes | Memo

---

## **Dispute Party**

Associates individuals or entities to a dispute with defined roles.
Roles may include complainant, respondent, witness, representative, investigator, or mediator.

**Fields:**
- Dispute | Lookup *(to Dispute)*
- Person | Lookup *(to Person from Core)*
- Account | Lookup *(to Account from Core)*
- Party Role | Choice
- Start Date | Date
- End Date | Date
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Is Primary | Yes / No
- Notified Date Time | Date Time
- Description | Memo

---

## **Dispute Referral**

Tracks referral of an intake or case to another office, authority, or support function.
Examples include HR, Legal, Security, Compliance, or external agencies.

**Fields:**
- Referral Number | Text
- Dispute Intake | Lookup *(to Dispute Intake)*
- Dispute | Lookup *(to Dispute)*
- Referral Date | Date
- Referred By | Lookup *(to Person from Core)*
- Referred To Organization | Lookup *(to Organization Unit from Core)*
- Referred To Person | Lookup *(to Person from Core)*
- Referral Status | Choice
- Referral Reason | Memo
- Response Date | Date
- Response Summary | Memo

---

## ✅ New Choice Fields for Dispute Resolution

### Dispute Status
Values representing the lifecycle of a dispute case:
- Intake
- Under Review
- Investigation
- Mediation
- Pending Determination
- Determined
- Under Appeal
- Closed
- Withdrawn
- Referred

### Dispute Type
Categories of disputes:
- Discrimination
- Harassment
- Retaliation
- Workplace Conflict
- Grievance
- Ethics Violation
- Policy Violation
- Employment Dispute
- Safety Concern
- Whistleblower Complaint
- Reasonable Accommodation
- Performance Issue

### Appeal Status
Current state of an appeal:
- Filed
- Under Review
- Hearing Scheduled
- Hearing Held
- Decision Pending
- Upheld
- Overturned
- Modified
- Remanded
- Withdrawn
- Dismissed

### Appeal Basis
Grounds for appeal:
- Procedural Error
- New Evidence
- Misapplication of Policy
- Excessive Remedy
- Bias or Conflict
- Insufficient Evidence
- Legal Error
- Timeliness Issue

### Corrective Action Type
Categories of required actions:
- Training Required
- Policy Revision
- Disciplinary Action
- Process Improvement
- Monitoring Plan
- Counseling
- Transfer or Reassignment
- Restitution
- System Enhancement
- Communication Plan

### Corrective Action Status
Progress on corrective actions:
- Planned
- In Progress
- Pending Verification
- Verified Complete
- Overdue
- Cancelled
- Deferred

### Determination Type
Types of formal outcomes:
- Finding
- Settlement
- Dismissal
- Summary Decision
- Final Decision
- Consent Order
- Default Decision
- Partial Decision

### Evidence Type
Categories of evidence:
- Document
- Email or Communication
- Witness Statement
- Audio Recording
- Video Recording
- Photograph
- Physical Item
- System Log
- Report
- Expert Opinion

### Finding Type
Conclusions from investigation:
- Substantiated
- Unsubstantiated
- Partially Substantiated
- Inconclusive
- Policy Violation Confirmed
- No Policy Violation
- Unable to Investigate
- Withdrawn
- Resolved Informally

### Intake Status
State of initial inquiry:
- New
- Under Review
- Information Requested
- Assigned
- Converted to Case
- Referred
- Resolved at Intake
- Closed - No Action
- Closed - Duplicate

### Investigation Status
Progress of investigation:
- Not Started
- Planning
- In Progress
- Evidence Collection
- Interviews Pending
- Analysis
- Report Drafting
- Completed
- On Hold
- Cancelled

### Interview Type
Categories of interviews:
- Initial Interview
- Follow-Up Interview
- Witness Interview
- Subject Interview
- Expert Consultation
- Informal Discussion
- Recorded Statement
- Virtual Interview

### Investigation Type
Nature of investigation:
- Formal Investigation
- Preliminary Inquiry
- Fact-Finding
- Compliance Review
- Safety Investigation
- Expedited Investigation
- External Investigation

### Issue Type
Specific categories of concerns:
- Discrimination - Age
- Discrimination - Disability
- Discrimination - Gender
- Discrimination - Race
- Discrimination - Religion
- Harassment - Sexual
- Harassment - Non-Sexual
- Retaliation
- Hostile Work Environment
- Wage and Hour
- Safety Violation
- Ethics Violation
- Conflict of Interest
- Misuse of Resources
- Misconduct

### Mediation Status
State of mediation process:
- Scheduled
- In Progress
- Continued
- Agreement Reached
- Impasse
- Completed
- Cancelled
- Declined

### Mediation Outcome
Result of mediation:
- Full Settlement
- Partial Settlement
- No Agreement
- Agreement Pending Approval
- Withdrawn
- Process Terminated

### Party Role
Role in dispute process:
- Complainant
- Respondent
- Witness
- Subject Matter Expert
- Representative
- Investigator
- Mediator
- Decision Maker
- Support Person
- Third Party

### Referral Status
State of referral:
- Pending
- Accepted
- Declined
- In Progress
- Completed
- Returned
- Closed

