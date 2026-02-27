# 🔍 Investigations — Data Model Design

The **Investigations module** supports the structured intake, management, analysis, and resolution of formal investigations across public sector and commercial environments. It enables organizations to document allegations, assign investigators, manage interviews and evidence with defensible chain-of-custody tracking, analyze issues against policies or standards, produce formal reports, and monitor corrective actions and recoveries through closure. The module supports use cases such as employee misconduct investigations, fraud inquiries, ethics hotline complaints, safety incidents, regulatory violations, data breach reviews, quality control investigations, inspector general cases, internal affairs reviews, and compliance examinations. It provides both operational case management and governance oversight, ensuring investigations are thorough, auditable, and aligned with organizational or statutory requirements.

---

## Core Case Management

### Investigation
Primary case record. Tracks lifecycle status, ownership, classification, key dates, confidentiality, and overall disposition.

**Completed:**

**Planned:**
- Name: Text
- Case Number: Text
- Parent Investigation: Lookup (Investigation)
- Investigative Type: Lookup (Investigative Type)
- Investigative Category: Lookup (Investigative Category)
- Case Status: Choice (Investigation Status)
- Priority: Choice (Priority)
- Severity Level: Choice (Severity Level)
- Security Classification: Choice (Security Classification)
- Visibility: Choice (Visibility)
- Is Confidential: Yes / No
- Intake Date: Date
- Investigation Start Date: Date
- Target Completion Date: Date
- Actual Completion Date: Date
- Closure Date: Date
- Lead Investigator: Lookup (Person)
- Investigation Team: Text
- Assigned Organization Unit: Lookup (Organization Unit)
- Reporting Organization Unit: Lookup (Organization Unit)
- Primary Location: Lookup (Location)
- Judicial District: Lookup (Judicial District)
- Related Investigation: Lookup (Investigation)
- Estimated Hours: Float
- Actual Hours: Float
- Investigation Budget: Currency
- Total Allegations: Integer
- Total Findings: Integer
- Legal Authority: Lookup (Legal Authority)
- Compliance Framework: Lookup (Compliance Framework)
- Subject Summary: Memo
- Background: Memo
- Overall Disposition: Choice (Investigation Overall Disposition)
- Closure Rationale: Memo
- Notes: Memo

---

### Investigation Intake
Initial allegation or referral submission before or at case creation. Captures source, channel, summary, and screening details.

**Completed:**
- Name: Text
- Intake Number: Text
- Intake Date Time: Date Time
- Intake Status: Choice (Investigation Intake Status)
- Method of Receipt: Choice (Method of Receipt)
- Received By: Lookup (Person)
- Reporter Person: Lookup (Person)
- Reporter Account: Lookup (Account)
- Reporter Name: Text
- Reporter Contact: Text
- Is Anonymous: Yes / No
- Reported Date: Date
- Incident Date: Date
- Incident Location: Lookup (Location)
- Allegation Summary: Memo
- Subject Person: Lookup (Person)
- Subject Account: Lookup (Account)
- Subject Organization Unit: Lookup (Organization Unit)
- Potential Investigative Type: Lookup (Investigative Type)
- Priority: Choice (Priority)
- Screening Status: Choice (Investigation Screening Status)
- Screened By: Lookup (Person)
- Screening Date: Date
- Screening Notes: Memo
- Disposition: Choice (Investigation Intake Disposition)
- Disposition Rationale: Memo
- Related Investigation: Lookup (Investigation)
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

### Investigation Allegation
Specific claim or accusation being evaluated within a case. A case may contain multiple allegations.

**Completed:**
- Name: Text
- Allegation Number: Text
- Investigation: Lookup (Investigation)
- Allegation Type: Choice (Investigation Allegation Type)
- Allegation Status: Choice (Investigation Allegation Status)
- Alleged Date: Date
- Description: Memo
- Subject Person: Lookup (Person)
- Subject Account: Lookup (Account)
- Subject Organization Unit: Lookup (Organization Unit)
- Impacted Person: Lookup (Person)
- Impacted Account: Lookup (Account)
- Policy Violated: Text
- Regulation Violated: Text
- Legal Authority: Lookup (Legal Authority)
- Estimated Monetary Impact: Currency
- Severity Level: Choice (Severity Level)
- Notes: Memo

**Planned:**

---

### Investigation Issue
Structured question, policy element, or control area being examined. Often used to frame analysis and findings.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Investigation Allegation: Lookup (Investigation Allegation)
- Issue Type: Choice (Investigation Issue Type)
- Issue Category: Text
- Issue Status: Choice (Issue Status)
- Policy Reference: Text
- Control Reference: Text
- Question: Memo
- Analysis: Memo
- Conclusion: Memo
- Notes: Memo

**Planned:**

---

### Investigative Type
Primary investigation taxonomy (Fraud, Misconduct, Safety, Data Breach, Quality, etc.).

**Completed:**
- Name: Text
- Type Code: Text
- Description: Memo
- Default Priority: Choice (Priority)
- Requires Legal Review: Yes / No
- Requires External Reporting: Yes / No
- Standard Investigation Duration (Days): Integer

**Planned:**

---

### Investigative Category
Secondary classification used for reporting (program area, risk domain, business unit, etc.).

**Completed:**
- Name: Text
- Category Code: Text
- Description: Memo
- Parent Category: Lookup (Investigative Category)

**Planned:**

---

### Investigation Related Cases
Links cases together (duplicate, predecessor, parallel, systemic connection).

**Completed:**
- Name: Text
- Primary Investigation: Lookup (Investigation)
- Related Investigation: Lookup (Investigation)
- Relationship Type: Choice (Case Relationship Type)
- Relationship Description: Memo
- Notes: Memo

**Planned:**

---

## Parties & Locations

### Investigation Party
Person or organization involved in the case (subject, reporter, witness, impacted party, etc.).

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Person: Lookup (Person)
- Account: Lookup (Account)
- Investigative Party Role: Lookup (Investigative Party Role)
- Party Type: Choice (Party Type)
- Organization Unit: Lookup (Organization Unit)
- Contact Information: Text
- Participation Status: Choice (Participation Status)
- First Contact Date: Date
- Last Contact Date: Date
- Is Protected: Yes / No
- Confidentiality Level: Choice (Security Classification)
- Notes: Memo

**Planned:**

---

### Investigative Party Role
Defines allowable roles a party may have in a case.

**Completed:**
- Name: Text
- Role Code: Text
- Description: Memo
- Is Subject Role: Yes / No
- Is Witness Role: Yes / No
- Requires Notification: Yes / No

**Planned:**

---

### Investigation Location
Physical or virtual location relevant to the case (facility, site, region, system environment).

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Location: Lookup (Location)
- Location Type: Choice (Investigation Location Type)
- Is Primary: Yes / No
- Relevance: Memo
- Access Details: Memo
- Notes: Memo

**Planned:**

---

## Planning & Work

### Investigation Plan
Documents scope, objectives, methodology, milestones, and investigative strategy.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Plan Status: Choice (Plan Status)
- Plan Date: Date
- Prepared By: Lookup (Person)
- Scope: Memo
- Objectives: Memo
- Methodology: Memo
- Key Milestones: Memo
- Resource Requirements: Memo
- Risk Considerations: Memo
- Legal Considerations: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

## Evidence Management

### Evidence Item
Any collected material (document, image, device, log file, physical object).

**Completed:**
- Name: Text
- Evidence Number: Text
- Investigation: Lookup (Investigation)
- Evidence Type: Lookup (Evidence Type)
- Evidence Status: Choice (Investigation Evidence Status)
- Collection Date: Date
- Collected By: Lookup (Person)
- Source Person: Lookup (Person)
- Source Account: Lookup (Account)
- Source Location: Lookup (Location)
- Description: Memo
- Physical Description: Text
- Serial Number: Text
- Is Original: Yes / No
- Is Copy: Yes / No
- File Format: Text
- File Size (MB): Float
- Digital Hash: Text
- Current Custodian: Lookup (Person)
- Evidence Storage Location: Lookup (Evidence Storage Location)
- Chain of Custody Verified: Yes / No
- Relevance: Memo
- Potential Evidentiary Value: Choice (High Medium Low)
- Security Classification: Choice (Security Classification)
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

### Evidence Type
Classification of evidence (email, CCTV, financial record, system log, physical item, etc.).

**Completed:**
- Name: Text
- Type Code: Text
- Evidence Category: Choice (Investigation Evidence Category)
- Description: Memo
- Requires Special Handling: Yes / No
- Retention Requirements: Memo

**Planned:**

---

### Evidence Link
Associates evidence to specific allegations, issues, interviews, findings, or tasks.

**Completed:**
- Name: Text
- Evidence Item: Lookup (Evidence Item)
- Investigation: Lookup (Investigation)
- Investigation Allegation: Lookup (Investigation Allegation)
- Investigative Issue: Lookup (Investigative Issue)
- Investigation Interview: Lookup (Investigation Interview)
- Investigation Finding: Lookup (Investigation Finding)
- Link Type: Choice (Investigation Evidence Link Type)
- Relevance: Memo
- Notes: Memo

**Planned:**

---

### Evidence Custody Record
Chain-of-custody entries documenting transfer, handling, and condition changes.

**Completed:**
- Name: Text
- Evidence Item: Lookup (Evidence Item)
- Custody Event Type: Choice (Investigation Custody Event Type)
- Event Date Time: Date Time
- From Custodian: Lookup (Person)
- To Custodian: Lookup (Person)
- From Location: Lookup (Evidence Storage Location)
- To Location: Lookup (Evidence Storage Location)
- Purpose: Memo
- Condition Before: Memo
- Condition After: Memo
- Seal Intact: Yes / No
- Seal Number: Text
- Witness: Lookup (Person)
- Recorded By: Lookup (User)
- Notes: Memo

**Planned:**

---

### Evidence Access Log
Audit log of who viewed, downloaded, or accessed an evidence item.

**Completed:**
- Name: Text
- Evidence Item: Lookup (Evidence Item)
- Access Date Time: Date Time
- Accessed By: Lookup (Person)
- Access Type: Choice (Access Type)
- Access Purpose: Memo
- Document Downloaded: Yes / No
- Download Count: Integer
- IP Address: Text
- System User: Text
- Notes: Memo

**Planned:**

---

### Evidence Storage Location
Physical or digital storage location (locker, vault, secure repository, external archive).

**Completed:**
- Name: Text
- Location Code: Text
- Storage Type: Choice (Storage Type)
- Physical Location: Lookup (Location)
- Storage Facility: Text
- Access Control: Memo
- Climate Control Required: Yes / No
- Custodian: Lookup (Person)
- Capacity: Text
- Security Level: Choice (Security Classification)
- Notes: Memo

**Planned:**

---

## Interviews

### Investigation Interview
Scheduled or completed interview session related to the case.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Interview Number: Text
- Interview Type: Choice (Investigation Interview Type)
- Interview Status: Choice (Interview Status)
- Scheduled Date Time: Date Time
- Actual Date Time: Date Time
- Duration (Minutes): Integer
- Interview Location: Lookup (Location)
- Virtual Meeting URL: URL
- Primary Interviewer: Lookup (Person)
- Interview Subject: Lookup (Person)
- Subject Representation: Text
- Recording Authorized: Yes / No
- Recording Location: Text
- Transcript Available: Yes / No
- Transcript Document: Lookup (Document)
- Interview Summary: Memo
- Key Statements: Memo
- Follow Up Required: Yes / No
- Follow Up Notes: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

### Investigation Interview Participant
Links participants to interviews and defines their role (interviewer, witness, observer, counsel).

**Completed:**
- Name: Text
- Investigation Interview: Lookup (Investigation Interview)
- Person: Lookup (Person)
- Participant Role: Choice (Investigation Interview Participant Role)
- Participation Status: Choice (Participation Status)
- Attendance Confirmed: Yes / No
- Notes: Memo

**Planned:**

---

## Analysis & Results

### Investigation Finding
Formal conclusion regarding an allegation or issue (substantiated, unsubstantiated, inconclusive, etc.).

**Completed:**
- Name: Text
- Finding Number: Text
- Investigation: Lookup (Investigation)
- Investigation Allegation: Lookup (Investigation Allegation)
- Investigative Issue: Lookup (Investigative Issue)
- Finding Type: Choice (Investigation Finding Type)
- Finding Status: Choice (Finding Status)
- Finding Date: Date
- Finding Result: Choice (Finding Result)
- Basis: Memo
- Analysis: Memo
- Evidence Summary: Memo
- Legal Standard Applied: Text
- Policy Reference: Text
- Determined By: Lookup (Person)
- Monetary Impact: Currency
- Severity Level: Choice (Severity Level)
- Requires Corrective Action: Yes / No
- Requires Referral: Yes / No
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

### Investigation Recommendation
Proposed corrective, preventive, or control improvement action arising from findings.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Investigation Finding: Lookup (Investigation Finding)
- Recommendation Type: Choice (Investigation Recommendation Type)
- Recommendation Status: Choice (Recommendation Status)
- Recommendation Date: Date
- Recommended To: Lookup (Organization Unit)
- Recommended Action: Memo
- Rationale: Memo
- Priority: Choice (Priority)
- Expected Benefit: Memo
- Estimated Cost: Currency
- Recommended By: Lookup (Person)
- Response Required By Date: Date
- Management Response: Memo
- Response Date: Date
- Response By: Lookup (Person)
- Implementation Status: Choice (Action Status)
- Related Corrective Action: Lookup (Investigation Corrective Action)
- Notes: Memo

**Planned:**

---

### Investigation Corrective Action
Action assigned to remediate findings, with owner, due date, and status tracking.

**Completed:**
- Name: Text
- Action Number: Text
- Investigation: Lookup (Investigation)
- Investigation Finding: Lookup (Investigation Finding)
- Investigation Recommendation: Lookup (Investigation Recommendation)
- Action Status: Choice (Action Status)
- Action Type: Choice (Investigation Corrective Action Type)
- Description: Memo
- Assigned To: Lookup (Person)
- Assigned Organization Unit: Lookup (Organization Unit)
- Due Date: Date
- Completion Date: Date
- Priority: Choice (Priority)
- Implementation Plan: Memo
- Progress Notes: Memo
- Verification Required: Yes / No
- Verified By: Lookup (Person)
- Verification Date: Date
- Verification Notes: Memo
- Notes: Memo

**Planned:**

---

### Investigation Outcome
Overall case resolution summary and closure rationale.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Outcome Type: Choice (Investigation Outcome Type)
- Outcome Date: Date
- Overall Disposition: Choice (Investigation Overall Disposition)
- Summary: Memo
- Allegations Substantiated: Integer
- Allegations Unsubstantiated: Integer
- Allegations Inconclusive: Integer
- Total Findings: Integer
- Total Recommendations: Integer
- Total Corrective Actions: Integer
- Monetary Recovery: Currency
- Lessons Learned: Memo
- Preventive Measures: Memo
- Prepared By: Lookup (User)
- Approved By: Lookup (User)
- Approval Date: Date
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

### Investigation Recovery Record
Tracks recovered funds, assets, restitution, or other tangible recoveries resulting from the case.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Investigation Finding: Lookup (Investigation Finding)
- Recovery Type: Choice (Investigation Recovery Type)
- Recovery Status: Choice (Investigation Recovery Status)
- Recovery Amount: Currency
- Recovery Date: Date
- Recovery Method: Choice (Investigation Recovery Method)
- Recovered From Person: Lookup (Person)
- Recovered From Account: Lookup (Account)
- Payment Reference: Text
- Asset Description: Memo
- Current Value: Currency
- Disposition: Memo
- Recorded By: Lookup (User)
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

## Reporting & External Coordination

### Investigation Report
Formal written report record (draft/final versions, approvals, publication metadata).

**Completed:**
- Name: Text
- Report Number: Text
- Investigation: Lookup (Investigation)
- Report Type: Choice (Report Type)
- Report Status: Choice (Publication Status)
- Version Number: Text
- Prepared Date: Date
- Prepared By: Lookup (User)
- Report Summary: Memo
- Report Document: Lookup (Document)
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (User)
- Approval Date: Date
- Distribution Date: Date
- Distribution List: Memo
- Security Classification: Choice (Security Classification)
- Is Public: Yes / No
- External Release Authorized: Yes / No
- Notes: Memo

**Planned:**

---

### Investigation Referral
Records referrals made to or received from internal or external entities.

**Completed:**
- Name: Text
- Investigation: Lookup (Investigation)
- Investigative Referral Type: Lookup (Investigative Referral Type)
- Referral Direction: Choice (Referral Direction)
- Referral Date: Date
- Referred To Account: Lookup (Account)
- Referred To Organization Unit: Lookup (Organization Unit)
- Referred To Contact: Lookup (Person)
- Referred By: Lookup (Person)
- Referral Status: Choice (Referral Status)
- Referral Summary: Memo
- Justification: Memo
- Response Required: Yes / No
- Response Due Date: Date
- Response Received Date: Date
- Response Summary: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

**Planned:**

---

### Investigative Referral Type
Defines referral categories (Internal, Legal, Law Enforcement, Regulator, HR, etc.).

**Completed:**
- Type Code: Text
- Referral Category: Choice (Investigation Referral Category)
- Description: Memo
- Default Organization Unit: Lookup (Organization Unit)
- Requires Formal Notification: Yes / No
- Standard Response Time (Days): Integer
- Name: Text

**Planned:**

---

## Investigation Module Choice Fields

The following choice fields are specific to the Investigations module:

**Completed:**

### Investigation Status
- Intake
- Screening
- Open
- Active Investigation
- Analysis
- Report Writing
- Pending Review
- Pending Closure
- Closed
- Suspended
- Referred Out

### Investigation Intake Status
- Received
- Under Review
- Screened
- Assigned
- Converted to Investigation
- Declined
- Referred
- Duplicate

### Investigation Screening Status
- Pending Screening
- Under Review
- Approved for Investigation
- Declined
- Referred

### Investigation Intake Disposition
- Proceed with Investigation
- Decline - Insufficient Evidence
- Decline - Outside Scope
- Refer to Other Entity
- Duplicate Case
- Already Resolved
- Administrative Closure

### Investigation Allegation Type
- Fraud
- Theft
- Misuse of Resources
- Conflict of Interest
- Ethics Violation
- Safety Violation
- Security Breach
- Policy Violation
- Misconduct
- Discrimination
- Harassment
- Retaliation
- Quality Defect
- Environmental Violation

### Investigation Allegation Status
- Pending Investigation
- Under Investigation
- Substantiated
- Unsubstantiated
- Inconclusive
- Not Investigated
- Withdrawn

### Investigation Issue Type
- Policy Compliance
- Control Effectiveness
- Procedural Adherence
- Documentation Adequacy
- Authorization
- Accountability
- Transparency

### Investigation Location Type
- Incident Site
- Interview Location
- Evidence Location
- Subject Location
- Facility
- System Environment

### Investigation Evidence Status
- Collected
- In Custody
- Under Analysis
- Released
- Archived
- Destroyed

### Investigation Evidence Category
- Documentary
- Physical
- Digital
- Testimonial
- Demonstrative

### Investigation Evidence Link Type
- Supports Allegation
- Contradicts Allegation
- Relevant to Issue
- Discussed in Interview
- Basis for Finding
- Referenced in Task

### Investigation Custody Event Type
- Initial Collection
- Transfer
- Analysis
- Viewing
- Copying
- Return
- Release
- Archival
- Destruction

### Investigation Interview Type
- Subject Interview
- Witness Interview
- Expert Interview
- Follow Up Interview
- Recorded Statement

### Investigation Interview Participant Role
- Primary Interviewer
- Co-Interviewer
- Witness
- Subject
- Legal Counsel
- Observer
- Interpreter

### Investigation Finding Type
- Allegation Finding
- Policy Finding
- Control Finding
- Compliance Finding
- Systemic Finding

### Investigation Recommendation Type
- Disciplinary Action
- Process Improvement
- Policy Change
- Control Enhancement
- Training
- System Modification
- Management Action

### Investigation Corrective Action Type
- Immediate Correction
- Process Change
- Policy Update
- Training
- Disciplinary Action
- System Enhancement
- Monitoring

### Investigation Outcome Type
- Administrative Closure
- Investigative Completion
- Referral
- Settled
- Withdrawn

### Investigation Overall Disposition
- Substantiated
- Partially Substantiated
- Unsubstantiated
- Inconclusive
- Unfounded
- Referred
- Administrative Closure

### Investigation Recovery Type
- Monetary Recovery
- Asset Recovery
- Restitution
- Fee or Penalty
- Civil Settlement
- Cost Savings

### Investigation Recovery Status
- Identified
- Pending Collection
- Partial Recovery
- Fully Recovered
- Uncollectible
- Written Off

### Investigation Recovery Method
- Payment
- Payroll Deduction
- Asset Seizure
- Legal Settlement
- Insurance Claim
- Voluntary Return

### Investigation Referral Category
- Internal Department
- Legal Counsel
- Law Enforcement
- Regulatory Agency
- Inspector General
- Human Resources
- External Auditor

