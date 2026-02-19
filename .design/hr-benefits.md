# 💼 HR Benefits — Data Model Design

The **HR Benefits module** manages the full lifecycle of employee benefit offerings, from plan design and eligibility configuration to enrollment, life event changes, and cost administration. It allows organizations to define benefit plans, options, coverage levels, providers, and contribution structures, while enforcing eligibility rules and waiting periods. HR staff can manage open enrollment cycles, process new hire enrollments, handle qualifying life events (such as marriage or birth), maintain beneficiary records, and track benefit-related claims or reimbursements. The module also supports payroll integration through deduction codes and contribution rates, and enables financial oversight through cost allocation tracking. It is designed to support both public sector and commercial organizations with effective dating, auditability, and structured benefit governance.

---

## Plan Configuration

### HR Benefit Plan
Defines a specific benefit offering provided by the organization (e.g., Medical Plan A, Pension Plan, Basic Life Insurance), including plan year and provider.

**Fields:**
- Name: Text
- Plan Code: Text
- Benefit Category: Choice (Benefit Category)
- HR Benefit Provider: Lookup (HR Benefit Provider)
- Plan Year: Text
- Plan Status: Choice (Operational Status)
- Effective Start Date: Date
- Effective End Date: Date
- Enrollment Allowed: Yes / No
- Requires Beneficiary: Yes / No
- Allows Dependent Coverage: Yes / No
- Allows Multiple Enrollments: Yes / No
- Is Mandatory: Yes / No
- Plan Administrator: Lookup (Person)
- Administrator Organization Unit: Lookup (Organization Unit)
- Plan Summary: Memo
- Coverage Details: Memo
- Legal Authority: Lookup (Legal Authority)
- Compliance Framework: Lookup (Compliance Framework)
- Notes: Memo

---

### HR Benefit Option
Defines selectable options within a benefit plan (e.g., PPO vs. HDHP, Basic vs. Premium coverage).

**Fields:**
- Name: Text
- Option Code: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Description: Memo
- Option Status: Choice (Operational Status)
- Effective Start Date: Date
- Effective End Date: Date
- Is Default: Yes / No
- Display Order: Integer
- Premium Amount: Currency
- Coverage Summary: Memo
- Notes: Memo

---

### HR Benefit Coverage Level
Defines coverage tiers available under benefit plans (e.g., Employee Only, Employee + Spouse, Family). Used to determine pricing and eligibility.

**Fields:**
- Name: Text
- Coverage Code: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Coverage Type: Choice (Coverage Type)
- Description: Memo
- Allows Dependents: Yes / No
- Maximum Dependents: Integer
- Display Order: Integer
- Is Active: Yes / No

---

### HR Benefit Provider
Stores information about the external or internal organization administering the benefit plan (e.g., insurance carrier, retirement board, third-party administrator).

**Fields:**
- Name: Text
- Provider Code: Text
- Provider Account: Lookup (Account)
- Provider Type: Choice (Provider Type)
- Provider Status: Choice (Operational Status)
- Primary Contact: Lookup (Person)
- Contact Phone: Text
- Contact Email: Text
- Website URL: Text
- Portal URL: Text
- Service Agreement: Lookup (Agreement)
- Agreement Start Date: Date
- Agreement End Date: Date
- Policy Number: Text
- Group Number: Text
- Tax ID: Text
- Description: Memo
- Notes: Memo

---

### HR Benefit Plan Document
Stores plan-related documentation such as summary plan descriptions, policy documents, regulatory filings, or internal guidelines.

**Fields:**
- Name: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Document Type: Choice (Benefit Document Type)
- Document: Lookup (Document)
- Document Status: Choice (Publication Status)
- Effective Date: Date
- Expiration Date: Date
- Version Number: Text
- Description: Memo
- Notes: Memo

---

## Eligibility & Enrollment Periods

### HR Benefit Eligibility Rule
Defines reusable eligibility conditions for benefit participation, such as employment type, grade/rank, bargaining unit, service duration, or location.

**Fields:**
- Name: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Rule Type: Choice (Eligibility Rule Type)
- Description: Memo
- Eligible Employment Types: Text
- Eligible Personnel Types: Text
- Minimum Service Days: Integer
- Minimum FTE: Float
- Eligible Organization Units: Text
- Eligible Locations: Text
- Eligible Pay Grades: Text
- Bargaining Unit Restriction: Text
- Age Minimum: Integer
- Age Maximum: Integer
- Rule Priority: Integer
- Is Active: Yes / No
- Notes: Memo

---

### HR Benefit Waiting Period
Defines waiting period rules before an employee becomes eligible for enrollment (e.g., 30 days after hire, first of month following eligibility).

**Fields:**
- Name: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Waiting Period Type: Choice (Waiting Period Type)
- Waiting Days: Integer
- Calculation Method: Choice (Calculation Method)
- Effective Date Rule: Memo
- Description: Memo
- Is Active: Yes / No

---

### HR Benefit Enrollment Period
Defines enrollment windows such as Open Enrollment, New Hire Enrollment, or Special Enrollment periods, including start and end dates.

**Fields:**
- Name: Text
- Period Type: Choice (Enrollment Period Type)
- Period Status: Choice (Period Status)
- Start Date: Date
- End Date: Date
- Plan Year: Text
- Applies To Plans: Memo
- Applies To Personnel Types: Text
- Default Effective Date: Date
- Grace Period Days: Integer
- Requires Life Event: Yes / No
- Administrator: Lookup (Person)
- Communication Sent: Yes / No
- Communication Date: Date
- Description: Memo
- Notes: Memo

---

## Enrollment & Elections

### HR Benefit Enrollment
Represents an individual's enrollment in a specific benefit plan, including selected option, coverage level, effective dates, and enrollment status.

**Fields:**
- Name: Text
- Enrollment Number: Text
- Person: Lookup (Person)
- HR Benefit Plan: Lookup (HR Benefit Plan)
- HR Benefit Option: Lookup (HR Benefit Option)
- HR Benefit Coverage Level: Lookup (HR Benefit Coverage Level)
- HR Benefit Enrollment Period: Lookup (HR Benefit Enrollment Period)
- Enrollment Status: Choice (Enrollment Status)
- Enrollment Type: Choice (Enrollment Type)
- Enrollment Date: Date
- Effective Start Date: Date
- Effective End Date: Date
- Coverage End Date: Date
- Submitted By: Lookup (Person)
- Submitted Date: Date
- Enrollment Source: Choice (Enrollment Source)
- Related Life Event: Lookup (HR Benefit Life Event)
- Employee Premium: Currency
- Employer Premium: Currency
- Total Premium: Currency
- Deduction Frequency: Choice (Deduction Frequency)
- HR Benefit Deduction Code: Lookup (HR Benefit Deduction Code)
- Requires Beneficiary: Yes / No
- Beneficiary Designated: Yes / No
- Confirmation Sent: Yes / No
- Confirmation Date: Date
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### HR Benefit Election
Captures detailed selections made under a benefit enrollment, such as optional riders, add-ons, or sub-options within a plan.

**Fields:**
- Name: Text
- HR Benefit Enrollment: Lookup (HR Benefit Enrollment)
- Election Type: Choice (Election Type)
- Election Value: Text
- Election Amount: Currency
- Description: Memo
- Notes: Memo

---

### HR Benefit Beneficiary
Stores beneficiary designations for benefit plans that require them (e.g., life insurance, retirement). Includes allocation percentage, relationship, effective dates, and priority sequencing.

**Fields:**
- Name: Text
- HR Benefit Enrollment: Lookup (HR Benefit Enrollment)
- Person: Lookup (Person)
- Beneficiary Type: Choice (Beneficiary Type)
- Beneficiary Person: Lookup (Person)
- Beneficiary Name: Text
- Relationship: Choice (Relationship Type)
- Allocation Percentage: Float
- Designation Priority: Integer
- Date of Birth: Date
- Social Security Number: Text
- Address: Text
- Phone: Text
- Email: Text
- Effective Start Date: Date
- Effective End Date: Date
- Is Active: Yes / No
- Notes: Memo

---

## Life Events & Changes

### HR Benefit Life Event
Records a reported qualifying life event for an individual (e.g., marriage, birth, divorce) that may trigger enrollment changes. Includes documentation and approval status.

**Fields:**
- Name: Text
- Event Number: Text
- Person: Lookup (Person)
- Life Event Type: Choice (Life Event Type)
- Event Date: Date
- Reported Date: Date
- Reported By: Lookup (Person)
- Event Status: Choice (Event Status)
- Enrollment Change Deadline: Date
- Supporting Documentation Required: Yes / No
- Documentation Received: Yes / No
- Documentation Date: Date
- Verification Status: Choice (Verification Status)
- Verified By: Lookup (Person)
- Verification Date: Date
- Description: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### HR Benefit Life Event Change
Tracks specific benefit enrollment changes resulting from a life event, including affected plans, requested modifications, approval status, and effective dates.

**Fields:**
- Name: Text
- HR Benefit Life Event: Lookup (HR Benefit Life Event)
- HR Benefit Enrollment: Lookup (HR Benefit Enrollment)
- Change Type: Choice (Enrollment Change Type)
- Change Status: Choice (Request Status)
- Requested Date: Date
- Effective Date: Date
- Previous Option: Lookup (HR Benefit Option)
- New Option: Lookup (HR Benefit Option)
- Previous Coverage Level: Lookup (HR Benefit Coverage Level)
- New Coverage Level: Lookup (HR Benefit Coverage Level)
- Previous Premium: Currency
- New Premium: Currency
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Processed Date: Date
- Description: Memo
- Notes: Memo

---

## Cost & Contribution Management

### HR Benefit Contribution Rate
Defines employer and employee contribution structures for a benefit plan, option, and/or coverage level. Supports percentage-based or fixed-amount contributions with effective dating.

**Fields:**
- Name: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- HR Benefit Option: Lookup (HR Benefit Option)
- HR Benefit Coverage Level: Lookup (HR Benefit Coverage Level)
- Rate Type: Choice (Rate Type)
- Effective Start Date: Date
- Effective End Date: Date
- Employee Contribution Type: Choice (Contribution Type)
- Employee Contribution Amount: Currency
- Employee Contribution Percentage: Float
- Employer Contribution Type: Choice (Contribution Type)
- Employer Contribution Amount: Currency
- Employer Contribution Percentage: Float
- Total Premium Amount: Currency
- Applies To Personnel Types: Text
- Applies To Pay Grades: Text
- Is Active: Yes / No
- Notes: Memo

---

### HR Benefit Cost Allocation
Defines how employer benefit costs are allocated across funds, cost centers, grants, or departments. Supports split allocations and effective dating.

**Fields:**
- Name: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Organization Unit: Lookup (Organization Unit)
- Funding Source: Text
- Cost Center: Text
- Account Code: Text
- Allocation Percentage: Float
- Allocation Amount: Currency
- Effective Start Date: Date
- Effective End Date: Date
- Is Active: Yes / No
- Notes: Memo

---

### HR Benefit Deduction Code
Maps benefit enrollments to payroll deduction identifiers. Supports integration with payroll systems and deduction tracking.

**Fields:**
- Name: Text
- Deduction Code: Text
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Deduction Type: Choice (Deduction Type)
- Deduction Category: Choice (Benefit Category)
- Is Pre-Tax: Yes / No
- Is Post-Tax: Yes / No
- Payroll System Code: Text
- Description: Memo
- Is Active: Yes / No

---

## Claims & Reimbursements

### HR Benefit Claim
Tracks internal benefit-related claims or reimbursement requests (e.g., tuition reimbursement, wellness reimbursement). Includes submission details, approval status, payment status, and associated enrollment.

**Fields:**
- Name: Text
- Claim Number: Text
- Person: Lookup (Person)
- HR Benefit Enrollment: Lookup (HR Benefit Enrollment)
- HR Benefit Plan: Lookup (HR Benefit Plan)
- Claim Type: Choice (Claim Type)
- Claim Status: Choice (Claim Status)
- Submission Date: Date
- Service Date: Date
- Claim Amount: Currency
- Approved Amount: Currency
- Paid Amount: Currency
- Denial Reason: Memo
- Payment Status: Choice (Payment Status)
- Payment Date: Date
- Payment Method: Text
- Submitted By: Lookup (Person)
- Reviewed By: Lookup (Person)
- Review Date: Date
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Description: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Represents employees and beneficiaries throughout the benefit lifecycle.

### Organization Unit *(Core)*
Used for plan administration, eligibility rules, and cost allocation.

### Account *(Core)*
Represents benefit providers and carriers.

### Agreement *(Core)*
Service agreements with benefit providers.

### Legal Authority *(Core)*
Regulatory basis for benefit plans (ERISA, ACA, etc.).

### Compliance Framework *(Core)*
Compliance requirements for benefit administration.

### Document *(Core)*
Plan documents, SPDs, enrollment forms, claim documentation.

### Personnel Type *(Core)*
Used in eligibility rules and contribution rate structures.

### Pay Grade *(Core)*
Used in eligibility rules and tiered contribution structures.

---

## New Choice Fields

### Benefit Category
- Medical
- Dental
- Vision
- Life Insurance
- Disability
- Retirement
- Health Savings Account
- Flexible Spending Account
- Wellness
- Tuition Assistance
- Employee Assistance Program
- Commuter Benefits
- Legal Services
- Pet Insurance

### Coverage Type
- Employee Only
- Employee Plus Spouse
- Employee Plus Dependents
- Employee Plus Family
- Retiree
- Continuation Coverage

### Provider Type
- Insurance Carrier
- Third Party Administrator
- Retirement Board
- Health Maintenance Organization
- Preferred Provider Organization
- Self-Insured
- Government Agency

### Benefit Document Type
- Summary Plan Description
- Policy Document
- Enrollment Form
- Evidence of Coverage
- Certificate of Insurance
- Regulatory Filing
- Plan Amendment
- Summary of Benefits and Coverage

### Eligibility Rule Type
- Employment Type
- Personnel Type
- Service Duration
- Full Time Equivalent
- Organization Unit
- Location
- Pay Grade
- Age Based
- Bargaining Unit
- Combination

### Waiting Period Type
- Days from Hire
- First of Month Following
- First Day of Month After Days
- Immediate
- Plan Year Start
- Custom

### Calculation Method
- Calendar Days
- Business Days
- From Start Date
- From Eligibility Date

### Enrollment Period Type
- Open Enrollment
- New Hire Enrollment
- Special Enrollment
- Life Event Enrollment
- Annual Enrollment
- Qualifying Event

### Period Status
- Upcoming
- Active
- Closed
- Cancelled

### Enrollment Status
- Active
- Pending
- Pending Approval
- Approved
- Declined
- Terminated
- Waived
- Cancelled
- Suspended

### Enrollment Type
- New Enrollment
- Re-Enrollment
- Change
- Termination
- Waiver

### Enrollment Source
- Open Enrollment
- New Hire
- Life Event
- Administrative
- Reinstatement

### Deduction Frequency
- Per Pay Period
- Monthly
- Quarterly
- Annually
- Semi-Monthly
- Bi-Weekly
- Weekly

### Election Type
- Optional Rider
- Supplemental Coverage
- Buy-Up Option
- Beneficiary Election
- Contribution Amount
- Coverage Amount

### Beneficiary Type
- Primary
- Contingent
- Secondary
- Estate

### Relationship Type
- Spouse
- Domestic Partner
- Child
- Parent
- Sibling
- Other Relative
- Estate
- Trust
- Other

### Life Event Type
- Marriage
- Domestic Partnership
- Birth
- Adoption
- Legal Guardianship
- Divorce
- Legal Separation
- Death of Dependent
- Loss of Other Coverage
- Gain of Other Coverage
- Change in Employment
- Change in Residence
- Medicare Eligibility
- Court Order

### Event Status
- Reported
- Pending Documentation
- Verified
- Processed
- Expired
- Cancelled

### Enrollment Change Type
- Add Coverage
- Drop Coverage
- Change Option
- Change Coverage Level
- Add Dependent
- Remove Dependent
- Change Contribution
- Terminate

### Rate Type
- Standard
- Tiered by Age
- Tiered by Salary
- Tiered by Service
- Composite

### Contribution Type
- Fixed Amount
- Percentage of Premium
- Percentage of Salary
- Tiered

### Deduction Type
- Pre-Tax
- Post-Tax
- Employer Paid
- Shared

### Claim Type
- Medical Claim
- Dental Claim
- Vision Claim
- Tuition Reimbursement
- Wellness Reimbursement
- Dependent Care
- Flexible Spending Account
- Health Savings Account
- Other Reimbursement

### Claim Status
- Submitted
- Under Review
- Approved
- Partially Approved
- Denied
- Paid
- Closed

### Payment Status
- Pending
- Approved
- Processed
- Paid
- Cancelled
- On Hold

### Verification Status
- Not Required
- Pending Verification
- Verified
- Rejected
- Needs Information
