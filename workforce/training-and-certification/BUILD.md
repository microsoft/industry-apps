# 🎓 Training and Certification — Data Model Design

The **Training and Certification** module provides a comprehensive framework for managing learning delivery, academic programs, credentialing, and eligibility requirements across higher education, workforce development, and regulated industries. It supports defining training courses and sessions (classes), organizing structured curricula through learning paths and academic programs, tracking enrollments, attendance, and completions, and awarding certificates with lifecycle management including renewals and expiration tracking. The module also enables configurable qualification requirements that can be applied to roles, access privileges, programs, or operational activities, ensuring individuals meet required training, credential, or competency standards. Common use cases include university course and degree management, corporate learning and development, professional certification programs, compliance-driven training environments, apprenticeship models, and readiness or eligibility enforcement across enterprise operations.

---

## Learning Delivery

### Training Course
Represents a catalog entry for a learning offering, including description, objectives, credit value, and prerequisites.

**Completed:**

**Planned:**
- Name: Text
- Course Code: Text
- Course Status: Choice (Operational Status)
- Course Type: Choice (Course Type)
- Course Category: Choice (Course Category)
- Course Level: Choice (Course Level)
- Description: Memo
- Course Objectives: Memo
- Learning Outcomes: Memo
- Target Audience: Memo
- Prerequisites: Memo
- Owning Organization Unit: Lookup (Organization Unit)
- Course Owner: Lookup (Person)
- Subject Area: Text
- Credit Hours: Float
- Continuing Education Units: Float
- Contact Hours: Float
- Duration (Hours): Float
- Duration (Days): Integer
- Delivery Method: Choice (Delivery Method)
- Is Online: Yes / No
- Is Instructor Led: Yes / No
- Is Self Paced: Yes / No
- Maximum Enrollment: Integer
- Standard Cost: Currency
- Materials Cost: Currency
- Materials List: Memo
- Course Materials: Lookup (Document)
- Course Syllabus: Lookup (Document)
- Website URL: Text
- Requires Certification: Yes / No
- Certification Authority: Text
- Is Published: Yes / No
- Publication Status: Choice (Publication Status)
- Effective Start Date: Date
- Effective End Date: Date
- Version: Text
- Display Order: Integer
- Notes: Memo

---

### Training Course Requirement
Represents prerequisite conditions required before enrolling in or completing a Training Course.

**Completed:**

**Planned:**
- Name: Text
- Training Course: Lookup (Training Course)
- Requirement Type: Choice (Training Requirement Type)
- Required Training Course: Lookup (Training Course)
- Required Learning Path: Lookup (Learning Path)
- Required Training Certificate: Lookup (Training Certificate)
- Required Credential: Lookup (Credential)
- Required Competency: Lookup (Competency)
- Minimum Score: Integer
- Is Prerequisite: Yes / No
- Is Corequisite: Yes / No
- Is Waivable: Yes / No
- Waiver Authority: Lookup (Person)
- Requirement Notes: Memo
- Display Order: Integer

---

### Training Objective
Represents a learning objective or outcome associated with a Training Course.

**Completed:**

**Planned:**
- Name: Text
- Objective Code: Text
- Training Course: Lookup (Training Course)
- Objective Type: Choice (Objective Type)
- Objective Category: Text
- Description: Memo
- Assessment Method: Memo
- Success Criteria: Memo
- Related Competency: Lookup (Competency)
- Bloom's Taxonomy Level: Choice (Blooms Level)
- Is Measurable: Yes / No
- Display Order: Integer

---

### Training Instructor
Represents an individual authorized to deliver Training Sessions.

**Completed:**

**Planned:**
- Name: Text
- Instructor Code: Text
- Person: Lookup (Person)
- Instructor Status: Choice (Instructor Status)
- Instructor Type: Choice (Instructor Type)
- Organization Unit: Lookup (Organization Unit)
- Subject Matter Expertise: Memo
- Authorized Courses: Memo
- Biography: Memo
- Qualifications: Memo
- Years of Experience: Integer
- Certification Number: Text
- Certification Expiration Date: Date
- Hourly Rate: Currency
- Is Active: Yes / No
- Effective Start Date: Date
- Effective End Date: Date
- Notes: Memo

---

### Academic Term
Represents a defined academic period (e.g., Fall 2026, Spring 2027) used to organize and schedule Training Sessions.

**Completed:**

**Planned:**
- Name: Text
- Term Code: Text
- Term Type: Choice (Term Type)
- Academic Year: Integer
- Term Status: Choice (Term Status)
- Start Date: Date
- End Date: Date
- Registration Start Date: Date
- Registration End Date: Date
- Add Drop Deadline Date: Date
- Withdrawal Deadline Date: Date
- Final Exam Start Date: Date
- Final Exam End Date: Date
- Is Active: Yes / No
- Notes: Memo

---

### Training Session
Represents a scheduled offering of a Training Course within a specific Academic Term, often referred to as a "class" or "section."

**Completed:**

**Planned:**
- Name: Text
- Session Code: Text
- Training Course: Lookup (Training Course)
- Academic Term: Lookup (Academic Term)
- Session Status: Choice (Session Status)
- Session Type: Choice (Session Type)
- Section Number: Text
- Primary Instructor: Lookup (Training Instructor)
- Secondary Instructor: Lookup (Training Instructor)
- Delivery Method: Choice (Delivery Method)
- Location: Lookup (Location)
- Room Number: Text
- Virtual Meeting URL: Text
- Start Date: Date
- End Date: Date
- Start Time: Text
- End Time: Text
- Schedule Pattern: Text
- Number of Sessions: Integer
- Duration (Hours): Float
- Credit Hours: Float
- Minimum Enrollment: Integer
- Maximum Enrollment: Integer
- Current Enrollment: Integer
- Waitlist Capacity: Integer
- Waitlist Count: Integer
- Enrollment Fee: Currency
- Materials Fee: Currency
- Total Fee: Currency
- Registration Open Date: Date
- Registration Close Date: Date
- Is Published: Yes / No
- Is Cancelled: Yes / No
- Cancellation Date: Date
- Cancellation Reason: Memo
- Session Materials: Lookup (Document)
- Session Agenda: Lookup (Document)
- Notes: Memo

---

### Training Enrollment
Represents an individual's registration in a specific Training Session.

**Completed:**

**Planned:**
- Name: Text
- Enrollment Number: Text
- Training Session: Lookup (Training Session)
- Person: Lookup (Person)
- Enrollment Status: Choice (Enrollment Status)
- Enrollment Date: Date
- Enrollment Method: Choice (Method of Contact)
- Enrolled By: Lookup (Person)
- Approved Date: Date
- Approved By: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Waitlist Position: Integer
- Waitlist Date: Date
- Confirmed Date: Date
- Attendance Status: Choice (Attendance Status)
- Start Date: Date
- Completion Date: Date
- Withdrawal Date: Date
- Withdrawal Reason: Memo
- Drop Date: Date
- Drop Reason: Memo
- Grade: Text
- Score: Integer
- Pass Fail: Choice (Pass Fail)
- Credit Hours Earned: Float
- Completion Status: Choice (Simple Certification Status)
- Certificate Issued: Yes / No
- Certificate Issue Date: Date
- Tuition Amount: Currency
- Materials Amount: Currency
- Total Amount: Currency
- Amount Paid: Currency
- Payment Status: Choice (Payment Status)
- Funding Source: Text
- Requires Accommodation: Yes / No
- Accommodation Notes: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Training Session Attendance
Represents an individual's attendance status for a specific Training Session (and optionally per meeting occurrence).

**Completed:**

**Planned:**
- Name: Text
- Training Enrollment: Lookup (Training Enrollment)
- Attendance Date: Date
- Attendance Status: Choice (Attendance Status)
- Session Number: Integer
- Check In Time: Date Time
- Check Out Time: Date Time
- Duration (Minutes): Integer
- Attendance Method: Choice (Attendance Method)
- Location: Lookup (Location)
- Is Excused: Yes / No
- Excuse Reason: Memo
- Recorded By: Lookup (Person)
- Recorded Date: Date Time
- Notes: Memo

---

### Training Completion
Represents an individual's successful or attempted completion of a Training Course, including result, score, and completion date.

**Completed:**

**Planned:**
- Name: Text
- Completion Number: Text
- Training Course: Lookup (Training Course)
- Training Enrollment: Lookup (Training Enrollment)
- Person: Lookup (Person)
- Completion Status: Choice (Simple Certification Status)
- Completion Date: Date
- Completion Method: Choice (Completion Method)
- Result: Choice (Overall Result)
- Grade: Text
- Score: Integer
- Percentage: Integer
- Pass Fail: Choice (Pass Fail)
- Credit Hours Earned: Float
- Continuing Education Units Earned: Float
- Attempts: Integer
- Duration (Hours): Float
- Instructor: Lookup (Training Instructor)
- Organization Unit: Lookup (Organization Unit)
- Academic Term: Lookup (Academic Term)
- Certificate Issued: Yes / No
- Certificate Issue Date: Date
- Certificate Number: Text
- Certificate Expiration Date: Date
- Verification Code: Text
- Verified By: Lookup (Person)
- Verification Date: Date
- Transcript Entry: Yes / No
- External Course: Yes / No
- External Provider: Text
- Transfer Credits: Yes / No
- Supporting Document: Lookup (Document)
- Notes: Memo

---

## Learning Paths

### Learning Path
Represents an ordered or curated sequence of Training Courses intended to guide learners toward a specific outcome or skill set.

**Completed:**

**Planned:**
- Name: Text
- Path Code: Text
- Learning Path Status: Choice (Operational Status)
- Path Type: Choice (Learning Path Type)
- Path Category: Text
- Description: Memo
- Learning Objectives: Memo
- Target Audience: Memo
- Owning Organization Unit: Lookup (Organization Unit)
- Path Owner: Lookup (Person)
- Total Credit Hours: Float
- Total Duration (Hours): Float
- Estimated Completion Time (Weeks): Integer
- Difficulty Level: Choice (Difficulty Level)
- Prerequisites: Memo
- Is Published: Yes / No
- Publication Status: Choice (Publication Status)
- Effective Start Date: Date
- Effective End Date: Date
- Display Order: Integer
- Icon URL: Text
- Notes: Memo

---

### Learning Path Course
Represents the association between a Learning Path and its component Training Courses, including sequence order and requirement status.

**Completed:**

**Planned:**
- Name: Text
- Learning Path: Lookup (Learning Path)
- Training Course: Lookup (Training Course)
- Is Required: Yes / No
- Is Elective: Yes / No
- Sequence Order: Integer
- Credit Hours: Float
- Prerequisite Courses: Text
- Course Notes: Memo

---

## Certificates & Credentials

### Training Certificate
Represents a credential that may be awarded upon meeting defined requirements. Includes issuing authority, validity period, and renewal rules.

**Completed:**

**Planned:**
- Name: Text
- Certificate Code: Text
- Certificate Status: Choice (Operational Status)
- Certificate Type: Choice (Certificate Type)
- Certificate Category: Text
- Description: Memo
- Purpose: Memo
- Issuing Authority: Text
- Issuing Organization Unit: Lookup (Organization Unit)
- Accrediting Body: Text
- Accreditation Number: Text
- Credential: Lookup (Credential)
- Validity Period (Months): Integer
- Validity Period (Years): Integer
- Is Renewable: Yes / No
- Renewal Period (Months): Integer
- Requires Continuing Education: Yes / No
- Continuing Education Hours Required: Float
- Renewal Requirements: Memo
- Is Transferable: Yes / No
- Recognition Level: Choice (Recognition Level)
- Compliance Framework: Lookup (Compliance Framework)
- Legal Authority: Lookup (Legal Authority)
- Certificate Template: Lookup (Document)
- Standard Cost: Currency
- Is Published: Yes / No
- Publication Status: Choice (Publication Status)
- Effective Start Date: Date
- Effective End Date: Date
- Website URL: Text
- Notes: Memo

---

### Training Certificate Requirement
Represents the criteria required to earn a Training Certificate, such as completion of specific courses or paths.

**Completed:**

**Planned:**
- Name: Text
- Training Certificate: Lookup (Training Certificate)
- Requirement Type: Choice (Training Requirement Type)
- Required Training Course: Lookup (Training Course)
- Required Learning Path: Lookup (Learning Path)
- Required Credential: Lookup (Credential)
- Required Competency: Lookup (Competency)
- Minimum Credit Hours: Float
- Minimum Score: Integer
- Minimum Experience (Months): Integer
- Is Required: Yes / No
- Is Waivable: Yes / No
- Waiver Authority: Lookup (Person)
- Requirement Notes: Memo
- Display Order: Integer

---

### Training Certificate Achievement
Represents a specific instance of a Training Certificate awarded to an individual, including issue date, expiration date, and current status.

**Completed:**

**Planned:**
- Name: Text
- Certificate Number: Text
- Training Certificate: Lookup (Training Certificate)
- Person: Lookup (Person)
- Achievement Status: Choice (Achievement Status)
- Issue Date: Date
- Expiration Date: Date
- Effective Date: Date
- Revocation Date: Date
- Revocation Reason: Memo
- Issued By: Lookup (Person)
- Issuing Organization Unit: Lookup (Organization Unit)
- Verification Code: Text
- Is Active: Yes / No
- Is Expired: Yes / No
- Days Until Expiration: Integer
- Renewal Required Date: Date
- Continuing Education Hours Completed: Float
- Related Training Completion: Lookup (Training Completion)
- Certificate Document: Lookup (Document)
- Digital Badge URL: Text
- Verification URL: Text
- Notes: Memo

---

### Training Certificate Renewal
Represents a renewal event for a Training Certificate Achievement, including renewal date and updated expiration details.

**Completed:**

**Planned:**
- Name: Text
- Renewal Number: Text
- Training Certificate Achievement: Lookup (Training Certificate Achievement)
- Renewal Status: Choice (Renewal Status)
- Prior Expiration Date: Date
- Renewal Date: Date
- New Expiration Date: Date
- Renewal Method: Choice (Renewal Method)
- Continuing Education Hours Submitted: Float
- Continuing Education Hours Approved: Float
- Requirements Met: Yes / No
- Requirements Notes: Memo
- Renewal Fee: Currency
- Fee Paid: Yes / No
- Payment Date: Date
- Processed By: Lookup (Person)
- Processed Date: Date
- Approved By: Lookup (Person)
- Approval Date: Date
- Approval Status: Choice (Approval Status)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

## Academic Programs

### Academic Program
Represents a structured curriculum such as a degree, diploma, or formal certificate program. Contains overall program metadata, credit requirements, and governance information.

**Completed:**

**Planned:**
- Name: Text
- Program Code: Text
- Academic Program Status: Choice (Operational Status)
- Program Type: Choice (Academic Program Type)
- Program Level: Choice (Academic Program Level)
- Academic Department: Text
- Description: Memo
- Program Objectives: Memo
- Learning Outcomes: Memo
- Admission Requirements: Memo
- Owning Organization Unit: Lookup (Organization Unit)
- Program Director: Lookup (Person)
- Accreditation Body: Text
- Accreditation Status: Text
- Accreditation Date: Date
- Accreditation Expiration Date: Date
- Total Credit Hours Required: Float
- Required Core Credits: Float
- Required Elective Credits: Float
- Minimum GPA: Float
- Maximum Time to Complete (Years): Integer
- Standard Duration (Years): Integer
- Degree Awarded: Text
- Is Published: Yes / No
- Publication Status: Choice (Publication Status)
- Enrollment Capacity: Integer
- Current Enrollment: Integer
- Tuition Amount: Currency
- Website URL: Text
- Program Catalog: Lookup (Document)
- Effective Start Date: Date
- Effective End Date: Date
- Notes: Memo

---

### Academic Program Requirement
Represents the specific course, path, credit, or rule requirements that must be met to complete an Academic Program.

**Completed:**

**Planned:**
- Name: Text
- Academic Program: Lookup (Academic Program)
- Requirement Type: Choice (Program Requirement Type)
- Requirement Category: Text
- Description: Memo
- Required Training Course: Lookup (Training Course)
- Required Learning Path: Lookup (Learning Path)
- Required Credit Hours: Float
- Minimum Grade: Text
- Is Required: Yes / No
- Is Elective: Yes / No
- Sequence Order: Integer
- Recommended Term: Text
- Requirement Notes: Memo

---

### Academic Program Completion
Represents an individual's completion status for an Academic Program, including completion date, final standing, and honors if applicable.

**Completed:**

**Planned:**
- Name: Text
- Completion Number: Text
- Academic Program: Lookup (Academic Program)
- Person: Lookup (Person)
- Completion Status: Choice (Program Completion Status)
- Enrollment Date: Date
- Expected Completion Date: Date
- Actual Completion Date: Date
- Total Credits Earned: Float
- Final GPA: Float
- Class Rank: Integer
- Class Size: Integer
- Academic Standing: Choice (Academic Standing)
- Honors: Choice (Academic Honors)
- Distinction: Text
- Degree Awarded: Text
- Degree Award Date: Date
- Diploma Number: Text
- Diploma Issue Date: Date
- Commencement Date: Date
- Graduation Ceremony: Lookup (Event)
- Conferral Status: Choice (Conferral Status)
- Academic Advisor: Lookup (Person)
- Program Director: Lookup (Person)
- Transcript Issued: Yes / No
- Transcript Issue Date: Date
- Verification Code: Text
- Diploma Document: Lookup (Document)
- Official Transcript: Lookup (Document)
- Notes: Memo

---

## Qualification & Eligibility

### Qualification Requirement
Represents a reusable eligibility rule set that specifies what an individual must possess (courses, certificates, competencies) to perform a role, access a resource, or participate in an activity.

**Completed:**

**Planned:**
- Name: Text
- Requirement Code: Text
- Requirement Status: Choice (Operational Status)
- Requirement Type: Choice (Qualification Requirement Type)
- Requirement Category: Text
- Description: Memo
- Purpose: Memo
- Evaluation Logic: Memo
- Owning Organization Unit: Lookup (Organization Unit)
- Requirement Owner: Lookup (Person)
- Is Active: Yes / No
- Effective Start Date: Date
- Effective End Date: Date
- Validation Frequency: Choice (Validation Frequency)
- Grace Period (Days): Integer
- Enforcement Level: Choice (Enforcement Level)
- Legal Authority: Lookup (Legal Authority)
- Compliance Framework: Lookup (Compliance Framework)
- Notes: Memo

---

### Qualification Requirement Item
Represents an individual requirement within a Qualification Requirement, such as a required course, certificate, or competency level.

**Completed:**

**Planned:**
- Name: Text
- Qualification Requirement: Lookup (Qualification Requirement)
- Item Type: Choice (Qualification Item Type)
- Required Training Course: Lookup (Training Course)
- Required Learning Path: Lookup (Learning Path)
- Required Training Certificate: Lookup (Training Certificate)
- Required Credential: Lookup (Credential)
- Required Competency: Lookup (Competency)
- Required Clearance Level: Lookup (Clearance Level)
- Minimum Score: Integer
- Minimum Proficiency Level: Integer
- Is Required: Yes / No
- Is Alternative: Yes / No
- Alternative Group: Text
- Validity Period (Months): Integer
- Requirement Notes: Memo
- Display Order: Integer

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Learners, instructors, course owners, program directors, advisors.

### Organization Unit *(Core)*
Departments, training divisions, program ownership.

### Credential *(Core)*
Professional credentials required or linked to certificates.

### Competency *(Core)*
Skills and competencies linked to courses, certificates, and qualifications.

### Clearance Level *(Core)*
Security clearances required in qualification requirements.

### Compliance Framework *(Core)*
Regulatory frameworks for training and certification requirements.

### Legal Authority *(Core)*
Regulatory basis for training, certification, and qualification requirements.

### Event *(Core)*
Commencement ceremonies, graduation events.

### Document *(Core)*
Course materials, syllabi, certificates, transcripts, diplomas, supporting documentation.

---

## New Choice Fields

### Course Type
- Instructor Led
- Online
- Hybrid
- Self Paced
- Workshop
- Seminar
- Lab
- Practicum
- Capstone

### Course Category
- Technical
- Professional Development
- Leadership
- Compliance
- Safety
- Operational
- Administrative
- Elective
- Core

### Course Level
- Introductory
- Intermediate
- Advanced
- Expert
- Refresher

### Delivery Method
- In Person
- Virtual
- Hybrid
- Self Paced
- Blended
- Asynchronous
- Synchronous

### Training Requirement Type
- Course Completion
- Certificate Held
- Credential Held
- Competency Level
- Experience
- Assessment
- Approval

### Objective Type
- Knowledge
- Skill
- Ability
- Behavior
- Performance

### Blooms Level
- Remember
- Understand
- Apply
- Analyze
- Evaluate
- Create

### Instructor Status
- Active
- Inactive
- Pending Approval
- Suspended
- Retired

### Instructor Type
- Full Time
- Adjunct
- Guest
- Subject Matter Expert
- Contractor
- Volunteer

### Term Type
- Fall
- Spring
- Summer
- Winter
- Quarter 1
- Quarter 2
- Quarter 3
- Quarter 4
- Intersession

### Term Status
- Planning
- Active
- Completed
- Archived

### Session Status
- Scheduled
- Open for Registration
- Registration Closed
- In Progress
- Completed
- Cancelled
- Postponed

### Session Type
- Regular
- Accelerated
- Intensive
- Weekend
- Evening
- Online
- Hybrid

### Enrollment Status
- Registered
- Confirmed
- Waitlisted
- Enrolled
- In Progress
- Completed
- Withdrawn
- Dropped
- No Show
- Cancelled

### Attendance Status
- Present
- Absent
- Tardy
- Excused
- Partial
- Remote

### Attendance Method
- In Person
- Virtual
- Remote
- Self Reported

### Pass Fail
- Pass
- Fail
- Incomplete
- Withdrawn

### Payment Status
- Not Required
- Pending
- Partial
- Paid
- Overdue
- Waived
- Refunded

### Completion Method
- In Person
- Online
- Hybrid
- Challenge Exam
- Transfer Credit
- Prior Learning Assessment

### Learning Path Type
- Career Path
- Skill Development
- Compliance Path
- Onboarding
- Professional Development
- Certification Prep

### Difficulty Level
- Beginner
- Intermediate
- Advanced
- Expert

### Certificate Type
- Professional Certification
- Compliance Certification
- License
- Credential
- Badge
- Award
- Recognition

### Recognition Level
- Internal
- Industry
- Regional
- National
- International

### Achievement Status
- Active
- Expired
- Suspended
- Revoked
- Pending Renewal
- Renewed

### Renewal Status
- Not Required
- Upcoming
- Submitted
- Under Review
- Approved
- Denied
- Completed
- Expired

### Renewal Method
- Continuing Education
- Re Examination
- Professional Development
- Work Experience
- Combination

### Academic Program Type
- Degree Program
- Certificate Program
- Diploma Program
- Credential Program
- Professional Program

### Academic Program Level
- Associate
- Bachelor
- Master
- Doctoral
- Post Doctoral
- Professional
- Certificate
- Diploma

### Program Requirement Type
- Core Course
- Elective Course
- Concentration Course
- Capstone
- Thesis
- Dissertation
- Practicum
- Internship
- Credit Hours

### Program Completion Status
- Prospective
- Admitted
- Enrolled
- Active
- On Leave
- Completed
- Graduated
- Withdrawn
- Dismissed

### Academic Standing
- Good Standing
- Academic Probation
- Academic Warning
- Dean's List
- Honor Roll
- Dismissed

### Academic Honors
- Summa Cum Laude
- Magna Cum Laude
- Cum Laude
- With Distinction
- With High Distinction
- With Highest Distinction

### Conferral Status
- Pending
- Conferred
- Deferred
- Withheld

### Qualification Requirement Type
- Role Qualification
- Access Qualification
- Operational Qualification
- Certification Requirement
- Licensing Requirement
- Safety Requirement

### Qualification Item Type
- Course Completion
- Learning Path Completion
- Certificate
- Credential
- Competency
- Clearance
- Assessment
- Experience

### Validation Frequency
- One Time
- Annual
- Biennial
- Triennial
- Quarterly
- On Demand
- Event Driven

### Enforcement Level
- Required
- Recommended
- Optional
- Advisory

