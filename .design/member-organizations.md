# 👥 Member Organizations — Data Model Design

The **Member Organizations** module manages structured groups of people formed for a defined purpose, such as boards, councils, committees, panels, clubs, associations, and teams. It supports defining the organization itself, classifying its type, managing members and their roles, handling membership applications and fees, and organizing service terms. For governance-focused groups, it also enables formal decision-making through motions, votes, vote responses, and resolutions, providing a clear record of proposals and adopted outcomes. This module can be used for scenarios such as a board of directors approving resolutions, a city council recording votes, a professional association managing dues-paying members, a university committee tracking terms and roles, or a club reviewing membership applications and documenting decisions.

---

## Organization Management

### Organization
Represents a structured group of people formed for a defined purpose, such as a board, council, committee, club, association, or team. Supports hierarchical relationships to model parent and subordinate organizations.

**Fields:**
- Name: Text
- Organization Code: Text
- Organization Type: Lookup (Organization Type)
- Organization Status: Choice (Operational Status)
- Parent Organization: Lookup (Organization)
- Affiliated Organization Unit: Lookup (Organization Unit)
- Affiliated Account: Lookup (Account)
- Established Date: Date
- Dissolution Date: Date
- Operational Status: Choice (Operational Status)
- Visibility: Choice (Visibility)
- Is Public: Yes / No
- Purpose: Memo
- Mission Statement: Memo
- Bylaws: Memo
- Chair: Lookup (Person)
- Vice Chair: Lookup (Person)
- Secretary: Lookup (Person)
- Primary Contact: Lookup (Person)
- Contact Email: Text
- Contact Phone: Text
- Meeting Location: Lookup (Location)
- Meeting Schedule: Text
- Website URL: Text
- Total Members: Integer
- Active Members: Integer
- Quorum Required: Integer
- Quorum Percentage: Float
- Requires Membership Approval: Yes / No
- Allows Self Registration: Yes / No
- Legal Authority: Lookup (Legal Authority)
- Governing Document: Lookup (Document)
- Notes: Memo

---

### Organization Type
Classifies organizations by their structural or functional category (e.g., Board, Council, Committee, Club, Team).

**Fields:**
- Name: Text
- Type Code: Text
- Description: Memo
- Default Quorum Percentage: Float
- Requires Voting: Yes / No
- Requires Terms: Yes / No
- Default Term Length (Months): Integer
- Is Active: Yes / No

---

### Organization Term
Defines a defined period of service or operational cycle for an organization (e.g., board term, fiscal year, season), used to structure membership tenure and governance activities.

**Fields:**
- Name: Text
- Organization: Lookup (Organization)
- Term Type: Choice (Term Type)
- Term Number: Integer
- Start Date: Date
- End Date: Date
- Term Status: Choice (Term Status)
- Description: Memo
- Chair: Lookup (Person)
- Vice Chair: Lookup (Person)
- Total Members: Integer
- Notes: Memo

---

## Membership Management

### Organization Member
Represents an individual's membership in an organization, including status and participation details. Serves as the central record linking a person to a specific organization.

**Fields:**
- Name: Text
- Member Number: Text
- Organization: Lookup (Organization)
- Person: Lookup (Person)
- Organization Member Type: Lookup (Organization Member Type)
- Membership Status: Choice (Membership Status)
- Join Date: Date
- Effective Start Date: Date
- Effective End Date: Date
- Organization Term: Lookup (Organization Term)
- Primary Role: Lookup (Organization Role)
- Is Voting Member: Yes / No
- Is Active: Yes / No
- Appointed By: Lookup (Person)
- Appointment Date: Date
- Nominated By: Lookup (Person)
- Nomination Date: Date
- Election Date: Date
- Resignation Date: Date
- Resignation Reason: Memo
- Termination Date: Date
- Termination Reason: Memo
- Emergency Contact Name: Text
- Emergency Contact Phone: Text
- Preferred Communication Method: Choice (Method of Contact)
- Email: Text
- Phone: Text
- Organization Member Application: Lookup (Organization Member Application)
- Notes: Memo

---

### Organization Member Type
Defines categories of membership within an organization (e.g., Regular, Student, Associate, Sponsor, Coach), used to classify members and determine eligibility or fee structures.

**Fields:**
- Name: Text
- Type Code: Text
- Organization: Lookup (Organization)
- Description: Memo
- Is Voting Type: Yes / No
- Allows Multiple Roles: Yes / No
- Requires Approval: Yes / No
- Default Fee: Currency
- Display Order: Integer
- Is Active: Yes / No

---

### Organization Member Role
Associates a member with a specific role within the organization (e.g., Chair, Treasurer, Captain), including effective dates when applicable.

**Fields:**
- Name: Text
- Organization Member: Lookup (Organization Member)
- Organization: Lookup (Organization)
- Person: Lookup (Person)
- Organization Role: Lookup (Organization Role)
- Organization Term: Lookup (Organization Term)
- Role Status: Choice (Role Status)
- Start Date: Date
- End Date: Date
- Is Primary: Yes / No
- Appointed By: Lookup (Person)
- Appointment Date: Date
- Election Date: Date
- Notes: Memo

---

### Organization Role
Defines reusable role types within organizations (e.g., Chair, Secretary, Member, Advisor), which can be assigned to organization members.

**Fields:**
- Name: Text
- Role Code: Text
- Role Category: Choice (Role Category)
- Description: Memo
- Is Leadership Role: Yes / No
- Is Officer Role: Yes / No
- Is Voting Role: Yes / No
- Requires Election: Yes / No
- Requires Appointment: Yes / No
- Display Order: Integer
- Is Active: Yes / No

---

### Organization Member Application
Captures requests to join an organization, including applicant details, review status, approval decisions, and onboarding information.

**Fields:**
- Name: Text
- Application Number: Text
- Organization: Lookup (Organization)
- Applicant: Lookup (Person)
- Organization Member Type: Lookup (Organization Member Type)
- Application Status: Choice (Application Status)
- Application Date: Date
- Requested Membership Type: Lookup (Organization Member Type)
- Requested Role: Lookup (Organization Role)
- Application Method: Choice (Method of Receipt)
- Motivation: Memo
- Qualifications: Memo
- Sponsor: Lookup (Person)
- Sponsor Endorsement: Memo
- Screening Status: Choice (Screening Status)
- Screened By: Lookup (Person)
- Screening Date: Date
- Screening Notes: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Denial Reason: Memo
- Interview Required: Yes / No
- Interview Date: Date
- Interview Notes: Memo
- Membership Effective Date: Date
- Related Membership: Lookup (Organization Member)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Organization Member Fee
Defines membership fees or dues associated with an organization or membership type, including amounts, frequency, and applicability rules.

**Fields:**
- Name: Text
- Organization: Lookup (Organization)
- Organization Member Type: Lookup (Organization Member Type)
- Fee Type: Choice (Fee Type)
- Fee Amount: Currency
- Fee Frequency: Choice (Fee Frequency)
- Billing Cycle: Choice (Billing Cycle)
- Effective Start Date: Date
- Effective End Date: Date
- Is Mandatory: Yes / No
- Is Prorated: Yes / No
- Grace Period (Days): Integer
- Late Fee Amount: Currency
- Payment Instructions: Memo
- Is Active: Yes / No
- Notes: Memo

---

## Governance & Decision Making

### Organization Motion
Represents a formal proposal submitted for consideration within an organization's governance process. Motions may proceed to vote and result in resolutions.

**Fields:**
- Name: Text
- Motion Number: Text
- Organization: Lookup (Organization)
- Organization Term: Lookup (Organization Term)
- Motion Type: Choice (Motion Type)
- Motion Status: Choice (Motion Status)
- Introduced Date: Date
- Introduced By: Lookup (Person)
- Seconded By: Lookup (Person)
- Motion Title: Text
- Motion Text: Memo
- Background: Memo
- Rationale: Memo
- Fiscal Impact: Currency
- Requires Supermajority: Yes / No
- Required Vote Threshold: Float
- Scheduled Vote Date: Date
- Discussion Item: Lookup (Discussion Item)
- Related Resolution: Lookup (Organization Resolution)
- Related Vote: Lookup (Organization Vote)
- Priority: Choice (Priority)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Organization Vote
Represents a formal voting event associated with a motion or decision, including voting method, quorum information, and outcome summary.

**Fields:**
- Name: Text
- Vote Number: Text
- Organization: Lookup (Organization)
- Organization Motion: Lookup (Organization Motion)
- Organization Term: Lookup (Organization Term)
- Vote Type: Choice (Vote Type)
- Vote Status: Choice (Vote Status)
- Vote Method: Choice (Vote Method)
- Vote Date: Date Time
- Vote Description: Memo
- Total Eligible Voters: Integer
- Quorum Required: Integer
- Total Votes Cast: Integer
- Quorum Met: Yes / No
- Yes Votes: Integer
- No Votes: Integer
- Abstain Votes: Integer
- Present Not Voting: Integer
- Absent Votes: Integer
- Vote Result: Choice (Vote Result)
- Percentage Yes: Float
- Percentage No: Float
- Percentage Abstain: Float
- Vote Passed: Yes / No
- Certification Date: Date
- Certified By: Lookup (Person)
- Related Resolution: Lookup (Organization Resolution)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Organization Vote Response
Captures an individual member's vote within a specific voting event (e.g., Yes, No, Abstain), providing detailed accountability and audit history.

**Fields:**
- Name: Text
- Organization Vote: Lookup (Organization Vote)
- Organization Member: Lookup (Organization Member)
- Person: Lookup (Person)
- Vote Response: Choice (Vote Response)
- Vote Date Time: Date Time
- Vote Method: Choice (Vote Method)
- Is Proxy Vote: Yes / No
- Proxy Holder: Lookup (Person)
- Comment: Memo
- Recorded By: Lookup (Person)
- Notes: Memo

---

### Organization Resolution
Represents an adopted decision or formal outcome of a motion or governance action. Serves as the official record of an organization's approved actions.

**Fields:**
- Name: Text
- Resolution Number: Text
- Organization: Lookup (Organization)
- Organization Term: Lookup (Organization Term)
- Organization Motion: Lookup (Organization Motion)
- Organization Vote: Lookup (Organization Vote)
- Resolution Type: Choice (Resolution Type)
- Resolution Status: Choice (Resolution Status)
- Adoption Date: Date
- Effective Date: Date
- Expiration Date: Date
- Resolution Title: Text
- Whereas Clauses: Memo
- Resolved Clauses: Memo
- Resolution Text: Memo
- Sponsored By: Lookup (Person)
- Voting Result Summary: Memo
- Implementation Status: Choice (Action Status)
- Implementation Notes: Memo
- Fiscal Impact: Currency
- Legal Authority: Lookup (Legal Authority)
- Formal Decision: Lookup (Formal Decision)
- Publication Status: Choice (Publication Status)
- Published Date: Date
- Visibility: Choice (Visibility)
- Resolution Document: Lookup (Document)
- Notes: Memo

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Represents organization members, officers, applicants, voters, motion sponsors.

### Organization Unit *(Core)*
Can be affiliated with organizations for departmental boards or committees.

### Account *(Core)*
Can be affiliated with organizations representing external associations or partner entities.

### Location *(Core)*
Meeting locations for organizations.

### Legal Authority *(Core)*
Regulatory basis for organization establishment and resolutions.

### Discussion Item *(Core)*
Can be linked to motions for pre-vote deliberation tracking.

### Formal Decision *(Core)*
Can be linked to resolutions for official governance decisions.

### Document *(Core)*
Governing documents, bylaws, supporting materials, resolution documents.

---

## New Choice Fields

### Term Type
- Board Term
- Fiscal Year
- Calendar Year
- Season
- Academic Year
- Program Year
- Election Cycle

### Term Status
- Scheduled
- Active
- Completed
- Extended
- Cancelled

### Membership Status
- Prospective
- Active
- Inactive
- Suspended
- Resigned
- Terminated
- Expired
- Honorary
- Emeritus

### Role Status
- Active
- Inactive
- Completed
- Resigned

### Role Category
- Executive
- Officer
- Committee Chair
- Committee Member
- General Member
- Advisor
- Ex Officio
- Honorary

### Application Status
- Submitted
- Under Review
- Interview Scheduled
- Recommended
- Approved
- Denied
- Withdrawn
- On Hold

### Screening Status
- Pending Screening
- Under Review
- Passed Screening
- Failed Screening
- Requires Interview

### Fee Type
- Membership Dues
- Initiation Fee
- Annual Fee
- Event Fee
- Late Fee
- Reinstatement Fee
- Special Assessment

### Fee Frequency
- One Time
- Annual
- Semi-Annual
- Quarterly
- Monthly
- Per Event

### Billing Cycle
- Upon Joining
- Calendar Year
- Fiscal Year
- Term Start
- Anniversary Date
- Monthly

### Motion Type
- Resolution
- Policy Change
- Budget Approval
- Appointment
- Amendment
- Procedural Motion
- Recommendation
- Endorsement

### Motion Status
- Draft
- Introduced
- Under Discussion
- Tabled
- Scheduled for Vote
- Voted
- Adopted
- Failed
- Withdrawn

### Vote Type
- Motion Vote
- Election
- Ratification
- Approval
- Procedural Vote

### Vote Status
- Scheduled
- In Progress
- Completed
- Cancelled
- Postponed

### Vote Method
- Voice Vote
- Roll Call
- Show of Hands
- Secret Ballot
- Electronic Vote
- Written Ballot
- Proxy Vote

### Vote Response
- Yes
- No
- Abstain
- Present Not Voting
- Absent

### Vote Result
- Passed
- Failed
- Tied
- No Quorum
- Postponed

### Resolution Type
- Standard Resolution
- Policy Resolution
- Budget Resolution
- Commemorative Resolution
- Emergency Resolution
- Procedural Resolution

### Resolution Status
- Draft
- Adopted
- Implemented
- Repealed
- Amended
- Expired
