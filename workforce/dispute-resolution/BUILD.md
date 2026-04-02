# ⚖️ Dispute Resolution — Data Model Design

## **Dispute**

Represents the primary case record for a formal internal dispute or complaint.
Tracks lifecycle status, case type, regulatory framework, assigned staff, key dates, and overall outcome.

**Completed:**

**Planned:**
- Case Number | Text
- Case Title | Text
- Dispute Type | Choice (Dispute Dispute Type)
- Stage | Choice (Dispute Stage)
- Decision Status | Choice (Item Decision Status)
- Priority | Choice (Priority)
- Severity Level | Choice (Severity Level)
- Filed Date | Date
- Close Date | Date
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Case Manager | Lookup *(to Person from Core)*
- Compliance Framework | Lookup *(to Compliance Framework from Core)*
- Legal Authority | Lookup *(to Legal Authority from Core)*
- Is Confidential | Yes / No
- Is Anonymous | Yes / No
- Overall Result | Choice (Overall Result)
- Description | Memo
- Details | Memo

---

## **Dispute Appeal**

Represents a formal challenge to a determination or decision.
Tracks appeal authority, filing date, appeal basis, review process, and final appellate outcome.

**Completed:**

**Planned:**
- Appeal Number | Text
- Appeal Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Determination | Lookup *(to Dispute Determination)*
- Appeal Basis | Choice (Dispute Appeal Basis)
- Stage | Choice (Dispute Appeal Stage)
- Decision Status | Choice (Item Decision Status)
- Appeal Date | Date
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

**Completed:**

**Planned:**
- Action Number | Text
- Action Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Determination | Lookup *(to Dispute Determination)*
- Corrective Action Type | Choice (Dispute Corrective Action Type)
- Completion Status | Choice (Item Completion Status)
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

**Completed:**

**Planned:**
- Determination Number | Text
- Determination Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Issue | Lookup *(to Dispute Issue)*
- Determination Type | Choice (Dispute Determination Type)
- Stage | Choice (Dispute Determination Stage)
- Determination Date | Date
- Effective Date | Date
- Deciding Official | Lookup *(to Person from Core)*
- Approval Status | Choice (Approval Status)
- Overall Result | Choice (Overall Result)
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Evidence**

Stores or references materials collected during investigation.
Examples include documents, communications, records, media files, and external reports.

**Completed:**

**Planned:**
- Evidence Number | Text
- Evidence Title | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Investigation | Lookup *(to Dispute Investigation)*
- Evidence Type | Choice (Dispute Evidence Type)
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

**Completed:**

**Planned:**
- Finding Number | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Issue | Lookup *(to Dispute Issue)*
- Dispute Investigation | Lookup *(to Dispute Investigation)*
- Finding Type | Choice (Finding Result)
- Finding Date | Date
- Inspector | Lookup *(to Person from Core)*
- Description | Memo
- Details | Memo

---

## **Dispute Intake**

Represents an initial inquiry, concern, or report prior to formal case creation.
Supports anonymous reporting, early resolution efforts, and triage decisions.

**Completed:**

**Planned:**
- Intake Number | Text
- Intake Title | Text
- Stage | Choice (Dispute Intake Stage)
- Disposition | Choice (Item Disposition)
- Submission Date Time | Date Time
- Method of Contact | Choice (Method of Contact)
- Method of Contact | Choice (Method of Contact)
- Submitted By | Lookup *(to Person from Core)*
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Intake Specialist | Lookup *(to Person from Core)*
- Priority | Choice (Priority)
- Is Anonymous | Yes / No
- Converted to Dispute | Lookup *(to Dispute)*
- Conversion Date | Date
- Description | Memo
- Details | Memo

---

## **Dispute Interview**

Tracks interviews conducted as part of an investigation.
Includes interviewee, role, date, summary, and related evidence.

**Completed:**

**Planned:**
- Interview Number | Text
- Dispute | Lookup *(to Dispute)*
- Dispute Investigation | Lookup *(to Dispute Investigation)*
- Interview Date Time | Date Time
- Interviewee | Lookup *(to Person from Core)*
- Interviewer | Lookup *(to Person from Core)*
- Interview Type | Choice (Dispute Interview Type)
- Location | Lookup *(to Location from Core)*
- Duration Minutes | Integer
- Was Recorded | Yes / No
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Notes | Memo

---

## **Dispute Investigation**

Represents the formal investigative process associated with a dispute.
Tracks investigator assignment, scope, timeline, methodology, and Action Status.

**Completed:**

**Planned:**
- Investigation Number | Text
- Investigation Title | Text
- Dispute | Lookup *(to Dispute)*
- Stage | Choice (Dispute Investigation Stage)
- Completion Status | Choice (Item Completion Status)
- Start Date | Date
- Target Completion Date | Date
- Actual Completion Date | Date
- Lead Investigator | Lookup *(to Person from Core)*
- Organization Unit | Lookup *(to Organization Unit from Core)*
- Investigation Type | Choice (Dispute Investigation Type)
- Methodology | Memo
- Scope | Memo
- Summary | Memo
- Details | Memo

---

## **Dispute Issue**

Defines the specific allegation, claim, or concern within a dispute case.
A single dispute may include multiple issues (e.g., discrimination, retaliation, harassment).

**Completed:**

**Planned:**
- Issue Number | Text
- Issue Title | Text
- Dispute | Lookup *(to Dispute)*
- Parent Dispute Issue | Lookup *(to Dispute Issue)*
- Issue Type | Choice (Dispute Issue Type)
- Severity Level | Choice (Severity Level)
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

**Completed:**

**Planned:**
- Mediation Number | Text
- Mediation Title | Text
- Dispute | Lookup *(to Dispute)*
- Stage | Choice (Dispute Mediation Stage)
- Decision Status | Choice (Item Decision Status)
- Scheduled Date Time | Date Time
- Actual Date Time | Date Time
- Mediator | Lookup *(to Person from Core)*
- Location | Lookup *(to Location from Core)*
- Is Voluntary | Yes / No
- Agreement Reached | Yes / No
- Mediation Outcome | Choice (Dispute Mediation Outcome)
- Agreement | Lookup *(to Agreement from Core)*
- Document | Lookup *(to Document from Core)*
- Description | Memo
- Notes | Memo

---

## **Dispute Party**

Associates individuals or entities to a dispute with defined roles.
Roles may include complainant, respondent, witness, representative, investigator, or mediator.

**Completed:**

**Planned:**
- Dispute | Lookup *(to Dispute)*
- Person | Lookup *(to Person from Core)*
- Account | Lookup *(to Account from Core)*
- Party Role | Choice (Dispute Party Role)
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

**Completed:**

**Planned:**
- Referral Number | Text
- Dispute Intake | Lookup *(to Dispute Intake)*
- Dispute | Lookup *(to Dispute)*
- Stage | Choice (Dispute Referral Stage)
- Referral Date | Date
- Referred By | Lookup *(to Person from Core)*
- Referred To Organization | Lookup *(to Organization Unit from Core)*
- Referred To Person | Lookup *(to Person from Core)*
- Referral Status | Choice (Dispute Referral Status)
- Referral Reason | Memo
- Response Date | Date
- Response Summary | Memo

---

## ✅ New Choice Fields for Dispute Resolution - Semi-Reviewed

### Dispute Stage
Workflow progression for dispute cases:
- Intake
- Initial Review
- Investigation
- Mediation
- Determination Pending
- Determination Made
- Appeal
- Closed

### Dispute Appeal Stage
Workflow for appeals process:
- Filed
- Under Review
- Hearing Scheduled
- Hearing Conducted
- Decision Pending
- Closed

### Dispute Determination Stage
Workflow for formal determinations:
- Draft
- Under Review
- Approval Pending
- Issued
- Appealed
- Final

### Dispute Intake Stage
Workflow for intake records:
- Received
- Under Review
- Information Requested
- Assessment
- Routing Decision
- Closed

### Dispute Investigation Stage
Workflow for investigations:
- Planning
- Evidence Collection
- Interviews
- Analysis
- Report Drafting
- Review
- Completed

### Dispute Mediation Stage
Workflow for mediation process:
- Scheduled
- Preparation
- In Session
- Continued
- Outcome Pending
- Closed

### Dispute Referral Stage
Workflow for referrals:
- Draft
- Sent
- Acknowledged
- In Progress
- Completed
- Closed

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

### Dispute Corrective Action Type
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

### Dispute Evidence Type
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

### Dispute Investigation Type
Categories of interviews:
- Initial Interview
- Follow-Up Interview
- Witness Interview
- Subject Interview
- Expert Consultation
- Informal Discussion
- Recorded Statement
- Virtual Interview

### Dispute Investigation Type
Nature of investigation:
- Formal Investigation
- Preliminary Inquiry
- Fact-Finding
- Compliance Review
- Safety Investigation
- Expedited Investigation
- External Investigation

### Dispute Interview Type
Categories of interviews:
- Initial Interview
- Follow-Up Interview
- Witness Interview
- Subject Interview
- Expert Consultation
- Informal Discussion
- Recorded Statement
- Virtual Interview

### Dispute Issue Type
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

### Dispute Mediation Outcome
Result of mediation:
- Full Settlement
- Partial Settlement
- No Agreement
- Agreement Pending Approval
- Withdrawn
- Process Terminated

### Dispute Party Role
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

### Dispute Determination Type
Types of formal outcomes:
- Finding
- Settlement
- Dismissal
- Summary Decision
- Final Decision
- Consent Order
- Default Decision
- Partial Decision

### Dispute Appeal Basis
Grounds for appeal:
- Procedural Error
- New Evidence
- Misapplication of Policy
- Excessive Remedy
- Bias or Conflict
- Insufficient Evidence
- Legal Error
- Timeliness Issue

## Removed (Replaced with Stage or Core Item Status Fields)

### Dispute Status → Dispute Stage + Item Decision Status  
### Dispute Appeal Status → Dispute Appeal Stage + Item Decision Status  
### Dispute Corrective Action Status → Item Completion Status (Core)  
### Dispute Intake Status → Dispute Intake Stage + Item Disposition (Core)  
### Dispute Investigation Status → Dispute Investigation Stage + Item Completion Status (Core)  
### Dispute Mediation Status → Dispute Mediation Stage + Item Decision Status  
### Dispute Referral Status → Dispute Referral Stage (Note: field still present in table, requires manual removal)

## Removed (Replaced with Core Fields)

### Dispute Finding Type → Finding Result (Core)  
Replaced with Core Finding Result which covers essential investigation outcomes (Substantiated, Partially Substantiated, Unsubstantiated, Inconclusive, No Finding, Unable to Determine). Domain-specific nuances like "Policy Violation Confirmed/No Policy Violation" map to Substantiated/Unsubstantiated. Process outcomes like "Withdrawn" or "Resolved Informally" should use Item Disposition instead.
