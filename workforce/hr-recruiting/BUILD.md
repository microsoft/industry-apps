# 🎯 HR Recruiting — Data Model Design

The **HR Recruiting module** manages the end-to-end hiring lifecycle from workforce request through candidate selection and offer. It supports structured requisition management, configurable posting and qualification requirements, candidate and application tracking, interviews, evaluator scoring, and formal selection decisions. The module is designed to work across public sector, commercial, and regulated environments, enabling use cases such as merit-based civil service hiring, corporate recruiting, campus hiring, internal mobility, and high-volume talent acquisition. It integrates with configurable question-and-answer capabilities for screening and leverages shared skills/competencies for defensible evaluation. The module concludes with offer management and pre-hire requirements, providing a clean handoff to HR Administration for onboarding and employment processing.

---

## Workforce Planning & Requisitions

### HR Workforce Request
Represents the initial request or justification to create or fill a position. Typically used in workforce planning and budgeting prior to requisition approval.

**Completed:**

**Planned:**
- Name: Text
- Request Number: Text
- Request Type: Choice (Workforce Request Type)
- Request Status: Choice (Request Status)
- Requested Date: Date
- Requested By: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Position Count: Integer
- Position Title: Text
- Job Series: Lookup (Job Series)
- Pay Grade: Lookup (Pay Grade)
- Employment Type: Choice (Employment Type)
- Is New Position: Yes / No
- Replaces Person: Lookup (Person)
- Business Justification: Memo
- Estimated Annual Cost: Currency
- Funding Source: Text
- Proposed Start Date: Date
- Priority: Choice (Priority)
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Related Requisition: Lookup (HR Requisition)
- Notes: Memo

---

### HR Requisition
Represents the authorized request to recruit for a position. Contains hiring details such as department, hiring manager, employment type, funding source, salary range, and approval status.

**Completed:**

**Planned:**
- Name: Text
- Requisition Number: Text
- Requisition Status: Choice (Requisition Status)
- Position Title: Text
- Number of Openings: Integer
- Job Series: Lookup (Job Series)
- Pay Grade: Lookup (Pay Grade)
- Salary Range Minimum: Currency
- Salary Range Maximum: Currency
- Employment Type: Choice (Employment Type)
- Position Designation: Choice (Position Designation)
- Hiring Organization Unit: Lookup (Organization Unit)
- Hiring Manager: Lookup (Person)
- Recruiter: Lookup (Person)
- Work Location: Lookup (Location)
- Is Remote Eligible: Yes / No
- Target Start Date: Date
- Required Security Clearance: Lookup (Clearance Level)
- Workforce Request: Lookup (HR Workforce Request)
- Opening Date: Date
- Closing Date: Date
- Is Open Until Filled: Yes / No
- Posting Required: Yes / No
- Internal Only: Yes / No
- Priority: Choice (Priority)
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Total Applications Received: Integer
- Total Qualified Applications: Integer
- Job Description: Memo
- Key Responsibilities: Memo
- Funding Source: Text
- Legal Authority: Lookup (Legal Authority)
- Notes: Memo

---

### HR Requisition Posting
Represents a specific publication or advertisement instance of a requisition. Tracks posting channel, posting dates, and versioned job description content.

**Completed:**

**Planned:**
- Name: Text
- HR Requisition: Lookup (HR Requisition)
- Posting Channel: Choice (Posting Channel)
- Posting Status: Choice (Publication Status)
- Posted Date: Date
- Posting Start Date: Date
- Posting End Date: Date
- External URL: Text
- Job Title: Text
- Job Summary: Memo
- Job Description: Memo
- Application Instructions: Memo
- Posted By: Lookup (Person)
- View Count: Integer
- Application Count: Integer
- Notes: Memo

---

### HR Requisition Requirement
Defines the required and preferred qualifications, competencies, or eligibility criteria associated with a requisition. May include weighting, proficiency levels, or minimum thresholds.

**Completed:**

**Planned:**
- Name: Text
- HR Requisition: Lookup (HR Requisition)
- Requirement Type: Choice (Requirement Type)
- Competency: Lookup (Competency)
- Credential: Lookup (Credential)
- Required Proficiency Level: Choice (Proficiency Level)
- Requirement Category: Choice (Requirement Category)
- Is Required: Yes / No
- Is Preferred: Yes / No
- Weight: Float
- Minimum Years Experience: Integer
- Description: Memo
- Evaluation Criteria: Memo
- Notes: Memo

---

## Candidate & Application Management

### HR Candidate
Represents the persistent recruiting profile of an individual across applications. Stores contact details, high-level background information, and historical application activity independent of any single requisition.

**Completed:**

**Planned:**
- Name: Text
- Candidate Number: Text
- Person: Lookup (Person)
- First Name: Text
- Last Name: Text
- Email: Text
- Phone: Text
- Mobile Phone: Text
- Address: Text
- City: Text
- State or Province: Lookup (State or Province)
- Postal Code: Text
- Country: Lookup (Country)
- Candidate Source: Choice (Candidate Source)
- Referral Source: Text
- Referred By: Lookup (Person)
- Candidate Status: Choice (Candidate Status)
- Is Internal: Yes / No
- Current Employer: Text
- Current Job Title: Text
- Years of Experience: Integer
- Highest Education Level: Choice (Education Level)
- Veteran Status: Yes / No
- Requires Sponsorship: Yes / No
- Willing to Relocate: Yes / No
- Expected Salary: Currency
- Resume Document: Lookup (Document)
- LinkedIn Profile: Text
- Portfolio URL: Text
- Total Applications: Integer
- Privacy Consent: Lookup (Privacy Consent)
- Opt In Communications: Yes / No
- Notes: Memo

---

### HR Application
Represents a candidate's formal submission for a specific requisition or posting. Tracks the lifecycle status (submitted, under review, interviewed, selected, not selected, withdrawn) and serves as the central operational record for evaluating and processing applicants.

**Completed:**

**Planned:**
- Name: Text
- Application Number: Text
- HR Candidate: Lookup (HR Candidate)
- HR Requisition: Lookup (HR Requisition)
- HR Requisition Posting: Lookup (HR Requisition Posting)
- Application Status: Choice (Application Status)
- Application Date: Date Time
- Application Source: Choice (Application Source)
- Is Internal: Yes / No
- Current Stage: Choice (Application Stage)
- Stage Updated Date: Date
- Cover Letter: Memo
- Resume Document: Lookup (Document)
- Total Score: Float
- Minimum Qualifications Met: Yes / No
- Veteran Preference Claimed: Yes / No
- Eligibility Status: Choice (Eligibility Status)
- Disqualification Reason: Memo
- Assigned Recruiter: Lookup (Person)
- Assigned Date: Date
- Last Activity Date: Date
- Total Interviews: Integer
- Notes: Memo

---

### HR Application Skill Assessment
Stores detailed scoring or rating of how well an applicant meets specific skills, competencies, or requisition requirements. Supports structured, defensible evaluation using weighted criteria.

**Completed:**

**Planned:**
- Name: Text
- HR Application: Lookup (HR Application)
- HR Requisition Requirement: Lookup (HR Requisition Requirement)
- Competency: Lookup (Competency)
- Assessed By: Lookup (Person)
- Assessment Date: Date
- Proficiency Level: Choice (Proficiency Level)
- Score: Float
- Weight: Float
- Weighted Score: Float
- Evidence: Memo
- Comments: Memo
- Notes: Memo

---

### HR Application Evaluation
Provides the consolidated summary assessment of an application. Captures overall score, recommendation, decision rationale, and disposition outcome based on interviews, skill assessments, and reviewer input.

**Completed:**

**Planned:**
- Name: Text
- HR Application: Lookup (HR Application)
- Evaluation Type: Choice (Evaluation Type)
- Evaluation Date: Date
- Evaluated By: Lookup (Person)
- Overall Score: Float
- Overall Rating: Choice (Overall Rating)
- Recommendation: Choice (Recommendation)
- Strengths: Memo
- Concerns: Memo
- Decision Rationale: Memo
- Move to Next Stage: Yes / No
- Recommended Stage: Choice (Application Stage)
- Notes: Memo

---

## Interview & Evaluation

### HR Interview
Represents a scheduled interview event for an application. Tracks interview type (phone, panel, virtual, in-person), date/time, participants, and outcome notes.

**Completed:**

**Planned:**
- Name: Text
- HR Application: Lookup (HR Application)
- HR Requisition: Lookup (HR Requisition)
- Interview Type: Choice (Interview Type)
- Interview Status: Choice (Interview Status)
- Scheduled Date Time: Date Time
- Duration (Minutes): Integer
- Interview Location: Lookup (Location)
- Virtual Meeting URL: Text
- Primary Interviewer: Lookup (Person)
- Interview Panel: Text
- Interview Stage: Choice (Application Stage)
- Conducted Date Time: Date Time
- Attendance Status: Choice (Attendance Status)
- Overall Impression: Choice (Overall Rating)
- Recommend for Hire: Choice (Recommendation)
- Interview Notes: Memo
- Strengths Observed: Memo
- Concerns Raised: Memo
- Follow Up Required: Yes / No
- Follow Up Notes: Memo
- Notes: Memo

---

### HR Evaluation
Captures an individual reviewer's structured assessment of a candidate, typically tied to an interview or evaluation stage. May include rubric-based scoring, comments, and competency ratings.

**Completed:**

**Planned:**
- Name: Text
- HR Application: Lookup (HR Application)
- HR Interview: Lookup (HR Interview)
- Evaluator: Lookup (Person)
- Evaluation Date: Date
- Evaluation Category: Choice (Evaluation Category)
- Competency: Lookup (Competency)
- Score: Float
- Rating: Choice (Overall Rating)
- Comments: Memo
- Supporting Evidence: Memo
- Notes: Memo

---

## Selection & Offer

### HR Selection Decision
Documents the formal hiring decision for a requisition. Identifies the selected candidate, ranking (if applicable), approvals, and justification supporting the final selection.

**Completed:**

**Planned:**
- Name: Text
- Decision Number: Text
- HR Requisition: Lookup (HR Requisition)
- Selected Application: Lookup (HR Application)
- Selected Candidate: Lookup (HR Candidate)
- Decision Date: Date
- Decision Status: Choice (Decision Status)
- Selection Ranking: Integer
- Selection Rationale: Memo
- Hiring Manager: Lookup (Person)
- Hiring Manager Approval: Choice (Approval Status)
- Hiring Manager Approval Date: Date
- HR Approval: Choice (Approval Status)
- HR Approver: Lookup (Person)
- HR Approval Date: Date
- Executive Approval Required: Yes / No
- Executive Approval: Choice (Approval Status)
- Executive Approver: Lookup (Person)
- Executive Approval Date: Date
- Legal Authority: Lookup (Legal Authority)
- Formal Decision: Lookup (Formal Decision)
- Offer Extended: Yes / No
- Offer Date: Date
- Related Offer: Lookup (HR Offer)
- Notes: Memo

---

### HR Offer
Documents the formal employment offer extended to a selected candidate. Captures compensation details, employment terms, start date, expiration, negotiation status, and final acceptance or decline.

**Completed:**

**Planned:**
- Name: Text
- Offer Number: Text
- HR Application: Lookup (HR Application)
- HR Selection Decision: Lookup (HR Selection Decision)
- HR Candidate: Lookup (HR Candidate)
- Offer Status: Choice (Offer Status)
- Offer Date: Date
- Offer Expiration Date: Date
- Extended By: Lookup (Person)
- Position Title: Text
- Employment Type: Choice (Employment Type)
- Organization Unit: Lookup (Organization Unit)
- Work Location: Lookup (Location)
- Proposed Start Date: Date
- Pay Grade: Lookup (Pay Grade)
- Offered Salary: Currency
- Salary Frequency: Choice (Salary Frequency)
- Sign On Bonus: Currency
- Relocation Allowance: Currency
- Other Compensation: Memo
- Benefits Summary: Memo
- Employment Terms: Memo
- Contingencies: Memo
- Offer Document: Lookup (Document)
- Offer Sent Date: Date
- Response Received Date: Date
- Candidate Response: Choice (Offer Response)
- Negotiation Requested: Yes / No
- Negotiation Notes: Memo
- Final Acceptance Date: Date
- Decline Reason: Memo
- Actual Start Date: Date
- Notes: Memo

---

### HR Pre-Hire Requirement
Tracks conditional requirements that must be completed prior to employment start. Examples include background checks, credential verification, medical screening, or security clearance initiation.

**Completed:**

**Planned:**
- Name: Text
- HR Offer: Lookup (HR Offer)
- HR Candidate: Lookup (HR Candidate)
- Requirement Type: Choice (Pre-Hire Requirement Type)
- Requirement Status: Choice (Requirement Status)
- Required By Date: Date
- Initiated Date: Date
- Completed Date: Date
- Result: Choice (Requirement Result)
- Result Details: Memo
- Vendor: Lookup (Account)
- Cost: Currency
- Assigned To: Lookup (Person)
- Supporting Document: Lookup (Document)
- Is Blocking: Yes / No
- Notes: Memo

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Represents candidates (internally), hiring managers, recruiters, interviewers, evaluators, and approvers.

### Organization Unit *(Core)*
Hiring departments, divisions, and organizational structure for requisitions and offers.

### Location *(Core)*
Work locations for positions, interview locations, and office assignments.

### Job Series *(Core)*
Job family classifications for requisitions and workforce requests.

### Pay Grade *(Core)*
Salary grade structures for requisitions and offers.

### Clearance Level *(Core)*
Security clearance requirements for positions.

### Competency *(Core)*
Skills and competencies for requisition requirements and candidate assessments.

### Credential *(Core)*
Required certifications, licenses, and credentials for positions.

### Personnel Type *(Core)*
Employment categories for requisitions.

### Document *(Core)*
Resumes, cover letters, offer letters, background check results.

### Legal Authority *(Core)*
Regulatory basis for hiring decisions (merit systems, civil service rules, EEO regulations).

### Formal Decision *(Core)*
Links selection decisions to formal decision records when required.

### Privacy Consent *(Core)*
Candidate data privacy consent and opt-in tracking.

---

## New Choice Fields

### Workforce Request Type
- New Position
- Replacement
- Temporary Backfill
- Seasonal
- Project Based
- Expansion

### Requisition Status
- Draft
- Pending Approval
- Approved
- Open
- On Hold
- Filled
- Cancelled
- Closed

### Posting Channel
- Company Website
- Job Board
- LinkedIn
- Indeed
- Government Jobs Portal
- Professional Association
- Internal Portal
- Campus Recruiting
- Agency
- Employee Referral

### Requirement Type
- Education
- Experience
- Competency
- Credential
- License
- Certification
- Language
- Technical Skill
- Physical Requirement
- Clearance

### Requirement Category
- Minimum Qualification
- Preferred Qualification
- Screening Criteria
- Evaluation Criteria

### Proficiency Level
- Beginner
- Intermediate
- Advanced
- Expert
- Subject Matter Expert

### Candidate Source
- Direct Application
- Employee Referral
- Agency
- LinkedIn
- Job Board
- Campus Recruiting
- Career Fair
- Social Media
- Internal Transfer
- Rehire

### Candidate Status
- Active
- Under Consideration
- Interviewing
- Selected
- Offered
- Hired
- Not Selected
- Withdrawn
- Inactive

### Education Level
- High School
- Associate Degree
- Bachelor Degree
- Master Degree
- Doctoral Degree
- Professional Degree
- Some College
- Trade Certification

### Application Status
- Submitted
- Under Review
- Screening
- Qualified
- Interviewing
- Finalist
- Selected
- Not Selected
- Withdrawn
- On Hold

### Application Stage
- Application Review
- Initial Screening
- Phone Screen
- First Interview
- Second Interview
- Panel Interview
- Final Interview
- Reference Check
- Offer Stage
- Pre-Hire

### Application Source
- Direct Application
- Employee Referral
- Agency Submission
- Internal Application
- Campus Recruiting
- Sourced by Recruiter

### Evaluation Type
- Initial Screening
- Phone Screen Evaluation
- Technical Assessment
- Behavioral Interview
- Panel Interview
- Final Assessment

### Overall Rating
- Excellent
- Above Average
- Average
- Below Average
- Poor
- Not Assessed

### Recommendation
- Strong Hire
- Hire
- Maybe
- Do Not Hire
- Advance to Next Stage
- Decline

### Interview Type
- Phone Screen
- Video Interview
- In Person
- Panel Interview
- Technical Interview
- Behavioral Interview
- Case Interview
- Presentation

### Interview Status
- Scheduled
- Confirmed
- Rescheduled
- Completed
- No Show
- Cancelled

### Attendance Status
- Attended
- No Show
- Cancelled by Candidate
- Cancelled by Employer
- Rescheduled

### Evaluation Category
- Technical Skills
- Communication
- Leadership
- Problem Solving
- Cultural Fit
- Experience
- Education
- Motivation

### Decision Status
- Pending
- Recommended
- Approved
- Declined
- On Hold

### Offer Status
- Draft
- Pending Approval
- Approved
- Extended
- Under Negotiation
- Accepted
- Declined
- Expired
- Withdrawn

### Salary Frequency
- Hourly
- Annual
- Bi-Weekly
- Monthly

### Offer Response
- Pending
- Accepted
- Declined
- Negotiating
- Expired

### Pre-Hire Requirement Type
- Background Check
- Drug Screening
- Medical Examination
- Reference Check
- Credential Verification
- Education Verification
- Employment Verification
- Security Clearance
- I-9 Verification
- Fingerprinting

### Requirement Status
- Not Started
- In Progress
- Completed
- Pending Review
- On Hold
- Cancelled
- Failed

### Requirement Result
- Cleared
- Cleared with Conditions
- Failed
- Incomplete
- Cancelled
- Pending

