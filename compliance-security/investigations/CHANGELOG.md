# Investigations Changelog

## Unreleased

### Added

#### Core Case Management
- Investigation Intake: Created table to capture initial allegations and referrals with reporter details, screening workflow, disposition tracking, and conversion to formal investigations
- Investigation Allegation: Created table to document specific claims within cases including subjects, impacted parties, policy/regulation violations, monetary impact, and severity levels
- Investigation Issue: Created table to structure examination questions, policy elements, and control areas with analysis and conclusions
- Investigative Type: Created table to classify investigations by primary taxonomy (Fraud, Misconduct, Safety, Data Breach) with default priorities and review requirements
- Investigative Category: Created table for secondary classification supporting hierarchical categorization and reporting
- Investigation Related Cases: Created table to link cases together with relationship types (duplicate, predecessor, parallel, systemic)

#### Parties & Locations
- Investigation Party: Created table to manage persons and organizations involved in cases with roles, confidentiality levels, contact tracking, and protection status
- Investigative Party Role: Created table to define allowable party roles (subject, witness, etc.) with notification requirements
- Investigation Location: Created table to track physical and virtual locations relevant to cases with access details and relevance documentation

#### Planning & Work
- Investigation Plan: Created table to document scope, objectives, methodology, milestones, resource requirements, risk considerations, and approval workflow

#### Evidence Management
- Evidence Item: Created table to catalog collected materials with chain-of-custody verification, digital hash tracking, storage locations, and security classifications
- Evidence Type: Created table to classify evidence by category with special handling and retention requirements
- Evidence Link: Created table to associate evidence with allegations, issues, interviews, findings, and tasks
- Evidence Custody Record: Created table to maintain chain-of-custody audit trail documenting transfers, handling, condition changes, and seal integrity
- Evidence Access Log: Created table to track who viewed, downloaded, or accessed evidence items with IP addresses and audit details
- Evidence Storage Location: Created table to define physical and digital storage facilities with access controls, custodians, and security levels

#### Interviews
- Investigation Interview: Created table to manage interview sessions with scheduling, recording authorization, transcripts, key statements, and follow-up tracking
- Investigation Interview Participant: Created table to link participants to interviews with roles (interviewer, witness, observer, counsel) and attendance confirmation

#### Analysis & Results
- Investigation Finding: Created table to document formal conclusions regarding allegations/issues with substantiation status, evidence summary, monetary impact, and referral requirements
- Investigation Recommendation: Created table to propose corrective actions with management responses, implementation status, estimated costs, and priority tracking
- Investigation Corrective Action: Created table to assign and track remediation actions with owners, due dates, verification workflow, and progress documentation
- Investigation Outcome: Created table to capture overall case resolution with disposition summary, statistics on substantiated allegations, lessons learned, and approval workflow
- Investigation Recovery Record: Created table to track recovered funds, assets, restitution, and recoveries with payment references and disposition details

#### Reporting & External Coordination
- Investigation Report: Created table to manage formal written reports with version control, distribution tracking, approval workflow, and security classification
- Investigation Referral: Created table to record referrals to/from internal and external entities with response tracking and status management
- Investigative Referral Type: Created table to define referral categories (Legal, Law Enforcement, Regulator, HR) with standard response times

#### Choice Fields
- Investigation Status: Configured choice field (Intake, Screening, Open, Active Investigation, Analysis, Report Writing, Pending Review, Pending Closure, Closed, Suspended, Referred Out)
- Investigation Intake Status: Configured choice field (Received, Under Review, Screened, Assigned, Converted to Investigation, Declined, Referred, Duplicate)
- Investigation Screening Status: Configured choice field (Pending Screening, Under Review, Approved for Investigation, Declined, Referred)
- Investigation Intake Disposition: Configured choice field (Proceed with Investigation, Decline - Insufficient Evidence, Decline - Outside Scope, Refer to Other Entity, Duplicate Case, Already Resolved, Administrative Closure)
- Investigation Allegation Type: Configured choice field (Fraud, Theft, Misuse of Resources, Conflict of Interest, Ethics Violation, Safety Violation, Security Breach, Policy Violation, Misconduct, Discrimination, Harassment, Retaliation, Quality Defect, Environmental Violation)
- Investigation Allegation Status: Configured choice field (Pending Investigation, Under Investigation, Substantiated, Unsubstantiated, Inconclusive, Not Investigated, Withdrawn)
- Investigation Issue Type: Configured choice field (Policy Compliance, Control Effectiveness, Procedural Adherence, Documentation Adequacy, Authorization, Accountability, Transparency)
- Investigation Location Type: Configured choice field (Incident Site, Interview Location, Evidence Location, Subject Location, Facility, System Environment)
- Investigation Evidence Status: Configured choice field (Collected, In Custody, Under Analysis, Released, Archived, Destroyed)
- Investigation Evidence Category: Configured choice field (Documentary, Physical, Digital, Testimonial, Demonstrative)
- Investigation Evidence Link Type: Configured choice field (Supports Allegation, Contradicts Allegation, Relevant to Issue, Discussed in Interview, Basis for Finding, Referenced in Task)
- Investigation Custody Event Type: Configured choice field (Initial Collection, Transfer, Analysis, Viewing, Copying, Return, Release, Archival, Destruction)
- Investigation Interview Type: Configured choice field (Subject Interview, Witness Interview, Expert Interview, Follow Up Interview, Recorded Statement)
- Investigation Interview Participant Role: Configured choice field (Primary Interviewer, Co-Interviewer, Witness, Subject, Legal Counsel, Observer, Interpreter)
- Investigation Finding Type: Configured choice field (Allegation Finding, Policy Finding, Control Finding, Compliance Finding, Systemic Finding)
- Investigation Recommendation Type: Configured choice field (Disciplinary Action, Process Improvement, Policy Change, Control Enhancement, Training, System Modification, Management Action)
- Investigation Corrective Action Type: Configured choice field (Immediate Correction, Process Change, Policy Update, Training, Disciplinary Action, System Enhancement, Monitoring)
- Investigation Outcome Type: Configured choice field (Administrative Closure, Investigative Completion, Referral, Settled, Withdrawn)
- Investigation Overall Disposition: Configured choice field (Substantiated, Partially Substantiated, Unsubstantiated, Inconclusive, Unfounded, Referred, Administrative Closure)
- Investigation Recovery Type: Configured choice field (Monetary Recovery, Asset Recovery, Restitution, Fee or Penalty, Civil Settlement, Cost Savings)
- Investigation Recovery Status: Configured choice field (Identified, Pending Collection, Partial Recovery, Fully Recovered, Uncollectible, Written Off)
- Investigation Recovery Method: Configured choice field (Payment, Payroll Deduction, Asset Seizure, Legal Settlement, Insurance Claim, Voluntary Return)
- Investigation Referral Category: Configured choice field (Internal Department, Legal Counsel, Law Enforcement, Regulatory Agency, Inspector General, Human Resources, External Auditor)

### Changed
- 
