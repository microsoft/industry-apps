# HR Administration Changelog

## Unreleased

### Added
- Choice Sets: Created 16 global option sets for HR Administration module:
  - **Position Management**: HR Position Status, HR Assignment Type, HR Assignment Status
  - **Employment Actions**: HR Action Category, Exemption Status
  - **Milestones**: HR Milestone Type, Milestone Status
  - **Requests & Approvals**: HR Request Type, Approval Status
  - **Employee Relations**: HR Disciplinary Action Type
  - **Time & Attendance**: HR Leave Type, HR Overtime Type, Schedule Frequency
  - **Workplace Management**: HR Telework Type, HR Accommodation Type, HR Declaration Type
- Entity Fields: Completed field creation for all 16 HR Administration entities (240+ fields total):
  - **Position & Classification Management:**
    - **HR Position**: 26 fields for authorized position structure including job classification, location, organization unit, pay grade, FTE, reporting relationships, and position status
    - **HR Position Assignment**: 13 fields linking employees to positions with assignment type, dates, FTE, reporting structure, and location details
    - **HR Position Description**: 17 fields for version-controlled position descriptions with duties, qualifications, requirements, approval workflow, and supporting documents
    - **HR Job Classification**: 13 fields for job role definitions including classification code, job series, FLSA status, supervisory flags, and bargaining unit eligibility
  - **Employment Actions & Lifecycle:**
    - **HR Employment Action**: 32 fields for personnel actions including action type, person, From/To tracking for position/org/pay grade/rank/location/employment type/FTE/salary, legal authority, approval workflow, and impact documentation
    - **HR Action Type**: 4 fields defining action categories, descriptions, and approval requirements
    - **HR Employment Milestone**: 11 fields for career milestones including milestone type, years of service, recognition tracking, notifications, and status
    - **HR Disciplinary Action**: 21 fields for incident management including disciplinary action type, dates, issuing authority, incident details, actions taken, appeal process, legal references, supporting documents, and security classification
  - **Employee Requests:**
    - **HR Request**: 14 fields for generic request header including request type, person, organization unit, dates, priority, approval workflow, and denial tracking
    - **HR Time Off Request**: 18 fields for leave requests including leave type, person, dates, hours (requested/approved/taken), return date, reason, approval workflow, contact information, and supporting documents
    - **HR Time Off Entry**: 7 fields for individual leave date entries tied to time off requests with date, hours, status, and leave type
    - **HR Overtime Entry**: 15 fields for overtime tracking including person, work date, hours, overtime type/rate, total pay, justification, approval workflow, pay period, and project code
    - **HR Telework Request**: 23 fields for telework arrangements including telework type, dates, frequency, location details, schedule, business justification, equipment needs, supervisor approval, agreement tracking, and safety checklist
    - **HR Workplace Accommodation**: 28 fields for accommodation requests including accommodation type, need description, medical documentation, interactive process tracking, approved accommodation, implementation details, cost, approval workflow, effectiveness evaluation, privacy consent, and security classification
    - **HR Employee Declaration**: 18 fields for employee attestations including declaration type, submission dates, content, review workflow, attestation tracking, legal authority, compliance framework, supporting documents, and security classification
    - **HR Leave Donation**: 20 fields for leave transfers including donor/recipient, donation date, leave types (donated/received), hours, conversion rate, approval workflow, processing status, and balance tracking (before/after for both parties)

### Changed
- 
