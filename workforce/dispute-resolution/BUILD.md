# ⚖️ Dispute Resolution — Data Model Design

### Dispute

Represents the primary case record for a formal internal dispute or complaint.
Tracks lifecycle status, case type, regulatory framework, assigned staff, key dates, and overall outcome.

**Completed:**

**Planned:**
- Case Title: Name
- Case Number: Text
- Dispute Type: Choice (Dispute Type)
- Stage: Choice (Dispute Stage)
- Decision Status: Choice (Item Decision Status)
- Priority: Choice (Priority)
- Severity Level: Choice (Severity Level)
- Filed Date: Date
- Close Date: Date
- Organization Unit: Lookup (Organization Unit)
- Compliance Framework: Lookup (Compliance Framework)
- Legal Authority: Lookup (Legal Authority)
- Is Confidential: Yes / No
- Is Anonymous: Yes / No
- Overall Result: Choice (Overall Result)
- Description: Memo

---

### Dispute Appeal

Represents a formal challenge to a determination or decision.
Tracks appeal authority, filing date, appeal basis, review process, and final appellate outcome.

**Completed:**

**Planned:**
- Appeal Title: Name
- Appeal Number: Text
- Dispute: Lookup (Dispute)
- Dispute Determination: Lookup (Dispute Determination)
- Appeal Basis: Choice (Dispute Appeal Basis)
- Stage: Choice (Dispute Appeal Stage)
- Decision Status: Choice (Item Decision Status)
- Appeal Date: Date
- Appellant: Lookup (Person)
- Reviewing Authority: Lookup (User)
- Decision Date: Date
- Decision Due Date: Date
- Overall Result: Choice (Overall Result)
- Description: Memo

---

### Dispute Corrective Action

Tracks actions required as a result of a determination or settlement.
Examples include training requirements, disciplinary measures, policy updates, or monitoring plans.

**Completed:**

**Planned:**
- Action Title: Name
- Action Number: Text
- Dispute: Lookup (Dispute)
- Dispute Determination: Lookup (Dispute Determination)
- Corrective Action Type: Choice (Dispute Corrective Action Type)
- Completion Status: Choice (Item Completion Status)
- Responsible Organization: Lookup (Organization Unit)
- Due Date: Date
- Completion Date: Date
- Verification Date: Date
- Verified By: Lookup (User)
- Description: Memo

---

### Dispute Determination

Represents the formal outcome or decision for a dispute or specific issue.
May include findings, remedies, dismissals, settlements, or final agency decisions.

**Completed:**

**Planned:**
- Determination Title: Name
- Determination Number: Text
- Dispute: Lookup (Dispute)
- Dispute Issue: Lookup (Dispute Issue)
- Determination Type: Choice (Dispute Determination Type)
- Stage: Choice (Dispute Determination Stage)
- Determination Date: Date
- Effective Date: Date
- Deciding Official: Lookup (User)
- Approval Status: Choice (Approval Status)
- Overall Result: Choice (Overall Result)
- Document: Lookup (Document)
- Description: Memo

---

### Dispute Evidence

Stores or references materials collected during investigation.
Examples include documents, communications, records, media files, and external reports.

**Completed:**

**Planned:**
- Evidence Title: Name
- Evidence Number: Text
- Dispute: Lookup (Dispute)
- Dispute Investigation: Lookup (Dispute Investigation)
- Evidence Type: Choice (Dispute Evidence Type)
- Collection Date: Date
- Collected By: Lookup (User)
- Submitted By: Lookup (Person)
- Document: Lookup (Document)
- Is Confidential: Yes / No
- Chain of Custody: Memo
- Description: Memo

---

### Dispute Finding

Captures the conclusion reached for a specific dispute issue after investigation.
Examples: Substantiated, Unsubstantiated, Inconclusive, Policy Violation Confirmed.

**Completed:**

**Planned:**
- Finding Title: Name
- Finding Number: Text
- Dispute: Lookup (Dispute)
- Dispute Issue: Lookup (Dispute Issue)
- Dispute Investigation: Lookup (Dispute Investigation)
- Finding Type: Choice (Finding Result)
- Finding Date: Date
- Description: Memo

---

### Dispute Intake

Represents an initial inquiry, concern, or report prior to formal case creation.
Supports anonymous reporting, early resolution efforts, and triage decisions.

**Completed:**

**Planned:**
- Intake Title: Name
- Intake Number: Text
- Stage: Choice (Dispute Intake Stage)
- Disposition: Choice (Item Disposition)
- Submission Date Time: Date Time
- Method of Contact: Choice (Method of Contact)
- Submitted By: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Priority: Choice (Priority)
- Is Anonymous: Yes / No
- Converted to Dispute: Lookup (Dispute)
- Conversion Date: Date
- Description: Memo

---

### Dispute Interview

Tracks interviews conducted as part of an investigation.
Includes interviewee, role, date, summary, and related evidence.

**Completed:**

**Planned:**
- Interview Title: Name
- Interview Number: Text
- Dispute: Lookup (Dispute)
- Dispute Investigation: Lookup (Dispute Investigation)
- Interview Date Time: Date Time
- Interviewee: Lookup (Person)
- Interview Type: Choice (Dispute Interview Type)
- Location: Lookup (Location)
- Duration Minutes: Integer
- Was Recorded: Yes / No
- Document: Lookup (Document)
- Description: Memo

---

### Dispute Investigation

Represents the formal investigative process associated with a dispute.
Tracks investigator assignment, scope, timeline, methodology, and Action Status.

**Completed:**

**Planned:**
- Investigation Title: Name
- Investigation Number: Text
- Dispute: Lookup (Dispute)
- Stage: Choice (Dispute Investigation Stage)
- Completion Status: Choice (Item Completion Status)
- Start Date: Date
- Target Completion Date: Date
- Actual Completion Date: Date
- Organization Unit: Lookup (Organization Unit)
- Investigation Type: Choice (Dispute Investigation Type)
- Methodology: Memo
- Scope: Memo
- Summary: Memo
- Description: Memo

---

### Dispute Issue

Defines the specific allegation, claim, or concern within a dispute case.
A single dispute may include multiple issues (e.g., discrimination, retaliation, harassment).

**Completed:**

**Planned:**
- Issue Title: Name
- Issue Number: Text
- Dispute: Lookup (Dispute)
- Parent Dispute Issue: Lookup (Dispute Issue)
- Issue Type: Choice (Dispute Issue Type)
- Severity Level: Choice (Severity Level)
- Alleged Date: Date
- Alleged By: Lookup (Person)
- Alleged Against: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Legal Authority: Lookup (Legal Authority)
- Description: Memo

---

### Dispute Mediation

Represents a structured mediation or alternative dispute resolution effort.
Tracks mediator, session dates, agreements reached, and mediation outcomes.

**Completed:**

**Planned:**
- Mediation Title: Name
- Mediation Number: Text
- Dispute: Lookup (Dispute)
- Stage: Choice (Dispute Mediation Stage)
- Decision Status: Choice (Item Decision Status)
- Scheduled Date Time: Date Time
- Actual Date Time: Date Time
- Location: Lookup (Location)
- Is Voluntary: Yes / No
- Agreement Reached: Yes / No
- Mediation Outcome: Choice (Dispute Mediation Outcome)
- Agreement: Lookup (Agreement)
- Document: Lookup (Document)
- Description: Memo

---

### Dispute Party

Associates individuals or entities to a dispute with defined roles.
Roles may include complainant, respondent, witness, representative, investigator, or mediator.

**Completed:**

**Planned:**
- Name: Text
- Dispute: Lookup (Dispute)
- Person: Lookup (Person)
- Account: Lookup (Account)
- Party Role: Choice (Dispute Party Role)
- Start Date: Date
- End Date: Date
- Organization Unit: Lookup (Organization Unit)
- Is Primary: Yes / No
- Notified Date Time: Date Time
- Description: Memo

---

### Dispute Referral

Tracks referral of an intake or case to another office, authority, or support function.
Examples include HR, Legal, Security, Compliance, or external agencies.

**Completed:**

**Planned:**
- Referral Title: Name
- Referral Number: Text
- Dispute Intake: Lookup (Dispute Intake)
- Dispute: Lookup (Dispute)
- Stage: Choice (Dispute Referral Stage)
- Referral Date: Date
- Referred By: Lookup (User)
- Referred To Organization: Lookup (Organization Unit)
- Referred To Person: Lookup (Person)
- Referral Reason: Memo
- Description: Memo
- Response Date: Date
- Response Summary: Memo

---

## ✅ Choice Fields

**Completed Last Round:**

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

**Refactoring:**

## Removed (Replaced with Stage or Core Item Status Fields)
### Dispute Status → Dispute Stage + Item Decision Status  
### Dispute Appeal Status → Dispute Appeal Stage + Item Decision Status  
### Dispute Corrective Action Status → Item Completion Status (Core)  
### Dispute Intake Status → Dispute Intake Stage + Item Disposition (Core)  
### Dispute Investigation Status → Dispute Investigation Stage + Item Completion Status (Core)  
### Dispute Mediation Status → Dispute Mediation Stage + Item Decision Status  
### Dispute Referral Status → Dispute Referral Stage (Note: field still present in table, requires manual removal)
### Dispute Finding Type → Finding Result (Core)  
Replaced with Core Finding Result which covers essential investigation outcomes (Substantiated, Partially Substantiated, Unsubstantiated, Inconclusive, No Finding, Unable to Determine). Domain-specific nuances like "Policy Violation Confirmed/No Policy Violation" map to Substantiated/Unsubstantiated. Process outcomes like "Withdrawn" or "Resolved Informally" should use Item Disposition instead.


