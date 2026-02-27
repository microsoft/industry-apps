# Member Organizations Changelog

## Unreleased

### Added

#### Organization Management
- Organization: Created table to manage structured groups including boards, councils, committees, and clubs with hierarchical relationships, officer positions (Chair, Vice Chair, Secretary, Treasurer), meeting details, quorum settings, and governance documents
- Organization Type: Created table to classify organizations by category with default settings for quorum percentage, voting requirements, and term lengths
- Organization Term: Created table to track defined periods of service or operational cycles (board terms, fiscal years, seasons) with term-specific leadership and member counts

#### Membership Management
- Organization Member: Created table to record individual memberships with join/effective dates, voting status, appointment/nomination/election details, resignation/termination tracking, and emergency contacts
- Organization Member Type: Created table to define membership categories (e.g., Regular, Student, Associate) with voting eligibility, role permissions, approval requirements, and default fee structures
- Organization Member Role: Created table to assign specific roles to members within organizations or terms with appointment/election tracking and primary role designation
- Organization Role: Created table to define reusable role types (Chair, Secretary, Member, Advisor) with leadership/officer/voting flags and election/appointment requirements
- Organization Member Application: Created table to manage membership requests with applicant details, screening workflow, sponsor endorsements, interview tracking, and approval decisions
- Organization Member Fee: Created table to configure membership fees and dues with amounts, frequency, billing cycles, proration options, grace periods, and late fee handling

#### Governance & Decision Making
- Organization Motion: Created table to capture formal proposals with motion text, background, fiscal impact, vote thresholds, and links to discussions, votes, and resolutions
- Organization Vote: Created table to record voting events with method, quorum tracking, vote tallies (Yes/No/Abstain/Absent), percentages, results, and certification details
- Organization Vote Response: Created table to log individual member votes within voting events including proxy votes, vote method, timestamps, and comments
- Organization Resolution: Created table to document adopted decisions with resolution text, whereas/resolved clauses, voting summaries, implementation tracking, fiscal impact, legal authority, and publication status

#### Choice Fields
- Organization Term Type: Configured choice field (Board Term, Fiscal Year, Calendar Year, Season, Academic Year, Program Year, Election Cycle)
- Organization Member Status: Configured choice field (Prospective, Active, Inactive, Suspended, Resigned, Terminated, Expired, Honorary, Emeritus)
- Organization Role Status: Configured choice field (Active, Inactive, Completed, Resigned)
- Organization Role Category: Configured choice field (Executive, Officer, Committee Chair, Committee Member, General Member, Advisor, Ex Officio, Honorary)
- Organization Application Status: Configured choice field (Submitted, Under Review, Interview Scheduled, Recommended, Approved, Denied, Withdrawn, On Hold)
- Organization Fee Type: Configured choice field (Membership Dues, Initiation Fee, Annual Fee, Event Fee, Late Fee, Reinstatement Fee, Special Assessment)
- Organization Billing Cycle: Configured choice field (Upon Joining, Calendar Year, Fiscal Year, Term Start, Anniversary Date, Monthly)
- Organization Fee Frequency: Configured choice field (One Time, Annual, Semi-Annual, Quarterly, Monthly, Per Event)
- Organization Motion Type: Configured choice field (Resolution, Policy Change, Budget Approval, Appointment, Amendment, Procedural Motion, Recommendation, Endorsement)
- Organization Motion Status: Configured choice field (Draft, Introduced, Under Discussion, Tabled, Scheduled for Vote, Voted, Adopted, Failed, Withdrawn)
- Organization Vote Type: Configured choice field (Motion Vote, Election, Ratification, Approval, Procedural Vote)
- Organization Vote Status: Configured choice field (Scheduled, In Progress, Completed, Cancelled, Postponed)
- Organization Vote Method: Configured choice field (Voice Vote, Roll Call, Show of Hands, Secret Ballot, Electronic Vote, Written Ballot, Proxy Vote)
- Organization Vote Response: Configured choice field (Yes, No, Abstain, Present Not Voting, Absent)
- Organization Vote Result: Configured choice field (Passed, Failed, Tied, No Quorum, Postponed)
- Organization Resolution Type: Configured choice field (Standard Resolution, Policy Resolution, Budget Resolution, Commemorative Resolution, Emergency Resolution, Procedural Resolution)
- Organization Resolution Status: Configured choice field (Draft, Adopted, Implemented, Repealed, Amended, Expired)

### Changed
- 
