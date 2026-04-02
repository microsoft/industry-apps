# 🎁 Programs and Services — Data Model Design

The **Programs and Services** module provides a structured framework for defining what an organization offers, who is eligible, who is participating, and what officially occurred as a result of service delivery. It separates strategic structure (Program, Service, Service Offering), eligibility configuration (Service Eligibility Rule and related scoping), and operational execution (Service Participation, Service Activity, Service Result), allowing services to be consistently defined and delivered across contexts. This module supports public sector use cases such as benefits administration, grants management, community assistance programs, and workforce initiatives, as well as commercial scenarios such as customer onboarding, subscription services, vendor programs, and training offerings. By cleanly distinguishing between enrollment, operational activities, and auditable outcomes, the module enables reusable service design, lifecycle tracking, and integration with related domains like Claims Processing, Permits and Licensing, Case Management, and Financial Management.

---

## Program & Service Structure

### Program
Represents a high-level initiative or policy area under which services are offered. A Program groups related Services and provides strategic, organizational, or funding context.

**Completed:**

**Planned:**
- Name: Text
- Program Code: Text
- Lifecycle Stage: Choice (Lifecycle Stage)
- Program Type: Choice (Program Type)
- Parent Program: Lookup (Program)
- Administering Organization Unit: Lookup (Organization Unit)
- Program Manager: Lookup (Person)
- Organization Initiative: Lookup (Organization Initiative)
- Effective Start Date: Date
- Effective End Date: Date
- Description: Memo
- Purpose: Memo
- Target Population: Memo
- Strategic Goals: Memo
- Funding Source: Text
- Annual Budget: Currency
- Legal Authority: Lookup (Legal Authority)
- Policy Document: Lookup (Document)
- Website URL: Text
- Is Public: Yes / No
- Visibility: Choice (Visibility)
- Notes: Memo

---

### Service
Represents a defined type of service provided under a Program. A Service describes what is offered in general terms and may have one or more Service Offerings over time.

**Completed:**

**Planned:**
- Name: Text
- Service Code: Text
- Program: Lookup (Program)
- Service Category: Lookup (Service Category)
- Lifecycle Stage: Choice (Lifecycle Stage)
- Service Type: Choice (Service Type)
- Description: Memo
- Service Scope: Memo
- Service Owner: Lookup (Person)
- Owning Organization Unit: Lookup (Organization Unit)
- Service Delivery Method: Choice (Delivery Method)
- Service Level: Choice (Service Level)
- Requires Eligibility Check: Yes / No
- Requires Application: Yes / No
- Is Self Service: Yes / No
- Average Processing Time (Days): Integer
- Standard Cost: Currency
- Legal Authority: Lookup (Legal Authority)
- Policy Reference: Text
- Service Guide Document: Lookup (Document)
- Website URL: Text
- Is Published: Yes / No
- Publication Status: Choice (Publication Status)
- Notes: Memo

---

### Service Category
Represents a classification used to group Services for reporting, organization, or navigation purposes. Categories help structure the service catalog without affecting delivery logic.

**Completed:**

**Planned:**
- Name: Text
- Category Code: Text
- Parent Category: Lookup (Service Category)
- Description: Memo
- Icon URL: Text

---

### Service Offering
Represents a specific version or configuration of a Service, typically bounded by time, geography, or policy parameters. A Service Offering defines the concrete instance of a Service that participants may enroll in.

**Completed:**

**Planned:**
- Name: Text
- Offering Code: Text
- Service: Lookup (Service)
- Stage: Choice (Service Offering Stage)
- Completion Status: Choice (Item Completion Status)
- Offering Version: Text
- Effective Start Date: Date
- Effective End Date: Date
- Enrollment Start Date: Date
- Enrollment End Date: Date
- Is Open Enrollment: Yes / No
- Maximum Participants: Integer
- Current Participants: Integer
- Waitlist Capacity: Integer
- Waitlist Count: Integer
- Offering Owner: Lookup (Person)
- Provider Organization Unit: Lookup (Organization Unit)
- Provider Account: Lookup (Account)
- Primary Location: Lookup (Location)
- Service Delivery Method: Choice (Delivery Method)
- Service Level: Choice (Service Level)
- Cost to Participant: Currency
- Funding Source: Text
- Budget Allocation: Currency
- Requires Pre Approval: Yes / No
- Approver: Lookup (Person)
- Description: Memo
- Enrollment Instructions: Memo
- Terms and Conditions: Memo
- Legal Authority: Lookup (Legal Authority)
- Policy Document: Lookup (Document)
- Is Published: Yes / No
- Publication Status: Choice (Publication Status)
- Notes: Memo

---

## Eligibility Management

### Service Eligibility Rule
Represents a reusable eligibility condition that may be applied to one or more Service Offerings. Eligibility Rules define qualification logic but are not scoped to a specific offering until linked.

**Completed:**

**Planned:**
- Name: Text
- Rule Code: Text
- Rule Type: Choice (Eligibility Rule Type)
- Rule Category: Choice (Eligibility Rule Category)
- Description: Memo
- Rule Logic: Memo
- Minimum Age: Integer
- Maximum Age: Integer
- Eligible Income Maximum: Currency
- Eligible Income Minimum: Currency
- Required Residency (Months): Integer
- Eligible Organization Units: Text
- Eligible Locations: Text
- Eligible Personnel Types: Text
- Required Credential: Lookup (Credential)
- Required Competency: Lookup (Competency)
- Required Clearance Level: Lookup (Clearance Level)
- Disqualifying Conditions: Memo
- Verification Method: Memo
- Priority: Choice (Priority)
- Notes: Memo

---

### Service Offering Eligibility Rule
Represents the association between a Service Offering and a Service Eligibility Rule. This table defines which eligibility rules apply to a specific offering and may control rule behavior (e.g., required, optional, effective dates).

**Completed:**

**Planned:**
- Name: Text
- Service Offering: Lookup (Service Offering)
- Service Eligibility Rule: Lookup (Service Eligibility Rule)
- Is Required: Yes / No
- Is Waivable: Yes / No
- Rule Priority: Integer
- Effective Start Date: Date
- Effective End Date: Date
- Waiver Authority: Lookup (Person)
- Notes: Memo

---

### Service Offering Geography
Represents geographic constraints or applicability for a Service Offering. This table defines where an offering is available or valid.

**Completed:**

**Planned:**
- Name: Text
- Service Offering: Lookup (Service Offering)
- Location: Lookup (Location)
- Judicial District: Lookup (Judicial District)
- Geographic Scope: Choice (Geographic Scope)
- Service Area Description: Memo
- Is Primary: Yes / No
- Effective Start Date: Date
- Effective End Date: Date
- Notes: Memo

---

## Service Delivery & Participation

### Service Participation
Represents a person's or organization's enrollment or engagement in a specific Service Offering. This table anchors the lifecycle of participation, including status, dates, and eligibility determination.

**Completed:**

**Planned:**
- Name: Text
- Participation Number: Text
- Service Offering: Lookup (Service Offering)
- Participant Person: Lookup (Person)
- Participant Account: Lookup (Account)
- On Behalf Of Person: Lookup (Person)
- Stage: Choice (Service Participation Stage)
- Cooperation Status: Choice (Cooperation Status)
- Enrollment Date: Date
- Enrollment Method: Choice (Method of Contact)
- Effective Start Date: Date
- Effective End Date: Date
- Scheduled Completion Date: Date
- Actual Completion Date: Date
- Termination Date: Date
- Termination Reason: Memo
- Eligibility Status: Choice (Eligibility Status)
- Eligibility Determination Date: Date
- Determined By: Lookup (Person)
- Eligibility Notes: Memo
- Assigned Case Manager: Lookup (Person)
- Assigned Organization Unit: Lookup (Organization Unit)
- Primary Service Location: Lookup (Location)
- Service Delivery Method: Choice (Delivery Method)
- Total Cost: Currency
- Amount Paid: Currency
- Funding Source: Text
- Priority: Choice (Priority)
- Participation Agreement: Lookup (Agreement)
- Privacy Consent: Lookup (Privacy Consent)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Service Activity
Represents an operational event or action performed during delivery of a Service to a specific Participation. Service Activities track the timeline of work or milestones related to service execution.

**Completed:**

**Planned:**
- Name: Text
- Activity Number: Text
- Service Participation: Lookup (Service Participation)
- Service Activity Type: Choice (Service Activity Type)
- Action Status: Choice (Action Status)
- Activity Date: Date
- Activity Date Time: Date Time
- Performed By: Lookup (Person)
- Performing Organization Unit: Lookup (Organization Unit)
- Activity Location: Lookup (Location)
- Activity Description: Memo
- Duration (Minutes): Integer
- Quantity: Float
- Unit of Issue: Choice (Unit of Issue)
- Activity Cost: Currency
- Outcome: Memo
- Next Steps: Memo
- Follow Up Date: Date
- Related Action Item: Lookup (Action Item)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Service Result
Represents an official, factual outcome that occurred for a specific Service Participation. Examples include approval, denial, issuance, adjustment, or completion. Service Results are auditable and historical.

**Completed:**

**Planned:**
- Name: Text
- Result Number: Text
- Service Participation: Lookup (Service Participation)
- Service Result Type: Lookup (Service Result Type)
- Stage: Choice (Service Result Stage)
- Appeal Status: Choice (Appeal Status)
- Result Date: Date
- Effective Date: Date
- Expiration Date: Date
- Result Description: Memo
- Result Value: Text
- Numeric Value: Float
- Currency Value: Currency
- Decision Rationale: Memo
- Approved Amount: Currency
- Benefit Period Start Date: Date
- Benefit Period End Date: Date
- Determined By: Lookup (Person)
- Determination Date: Date
- Approved By: Lookup (Person)
- Approval Date: Date
- Notification Sent: Yes / No
- Notification Date: Date
- Is Final: Yes / No
- Appeal Deadline Date: Date
- Appealed: Yes / No
- Appeal Date: Date
- Legal Authority: Lookup (Legal Authority)
- Formal Decision: Lookup (Formal Decision)
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Service Result Type
Represents the predefined set of allowable result classifications that may be applied to Service Results. This table defines the controlled vocabulary of possible outcomes.

**Completed:**

**Planned:**
- Name: Text
- Result Type Code: Text
- Service Result Category: Choice (Service Result Category)
- Description: Memo
- Is Approval: Yes / No
- Is Denial: Yes / No
- Is Adjustment: Yes / No
- Requires Notification: Yes / No
- Allows Appeal: Yes / No
- Appeal Window (Days): Integer

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Represents participants, program managers, service owners, case managers, decision makers.

### Account *(Core)*
Represents participant organizations, service providers.

### Organization Unit *(Core)*
Administering units, owning units, provider units.

### Organization Initiative *(Core)*
Strategic initiatives that programs support.

### Location *(Core)*
Service delivery locations, geographic areas.

### Judicial District *(Core)*
Service area definitions for geographic scope.

### Action Item *(Core)*
Tasks linked to service activities and follow-ups.

### Agreement *(Core)*
Participation agreements, service agreements.

### Legal Authority *(Core)*
Regulatory basis for programs, services, and eligibility.

### Formal Decision *(Core)*
Official decisions linked to service results.

### Document *(Core)*
Policy documents, guides, supporting documentation, result documents.

### Privacy Consent *(Core)*
Participant consent tracking.

### Credential, Competency, Clearance Level *(Core)*
Used in eligibility rules.

---

## New Choice Fields - Reviewed

**Completed:**

**Completed Last Round:**

### Program Type
- Benefits Program
- Grant Program
- Assistance Program
- Workforce Program
- Community Program
- Training Program
- Support Services
- Customer Program
- Vendor Program
- Subscription Program

### Service Type
- Direct Service
- Support Service
- Benefit Service
- Information Service
- Referral Service
- Assessment Service
- Training Service
- Consultation Service

### Service Level
- Standard
- Priority
- Expedited
- Emergency
- Premium

### Eligibility Rule Type
- Age Based
- Income Based
- Residency Based
- Employment Based
- Credential Based
- Risk Based
- Need Based
- Asset Based

### Eligibility Rule Category
- Minimum Requirement
- Preferred Qualification
- Disqualifying Condition
- Priority Factor
- Scoring Criteria

### Service Activity Type
- Enrollment
- Assessment
- Consultation
- Service Delivery
- Follow Up
- Review
- Monitoring
- Evaluation
- Communication
- Documentation
- Referral

### Service Result Category
- Approval
- Denial
- Certification
- Issuance
- Adjustment
- Renewal
- Termination
- Completion
- Referral

**Planned:**

**New Stage Fields:**

### Service Offering Stage
Tracks service offering workflow from planning through delivery to finalization.
- Planning
- Ready
- Enrollment
- Closed Enrollment
- Active
- Finalized

### Service Participation Stage
Tracks individual participation from enrollment through service delivery to completion.
- Application
- Enrolled
- Active
- Completed
- Terminated

### Service Result Stage
Tracks official service result workflow from pending determination through final outcome.
- Pending
- Determined
- Issued
- Final

**Removed (Replaced with Stage and Core Status Fields):**

### Service Offering Status → Replaced with Service Offering Stage + Completion Status
Service Offering Status mixed workflow states (Planning, Open for Enrollment, Enrollment Closed, Active) with outcomes (Completed, Cancelled) and work impediments (Suspended). Separated into:
- Service Offering Stage for workflow (Planning → Ready → Enrollment → Closed Enrollment → Active → Finalized)
- Item Completion Status (Core) for work tracking: Blocked (replaces Suspended)
- Item Disposition (Core) for final outcomes: Completed, Canceled
- Keep Publication Status (Core) for content publishing status

Value mapping:
- Planning → Stage: Planning
- Open for Enrollment → Stage: Enrollment
- Enrollment Closed → Stage: Closed Enrollment
- Active → Stage: Active
- Completed → Stage: Finalized + Disposition: Completed
- Cancelled → Disposition: Canceled
- Suspended → Completion Status: Blocked

### Service Result Status → Replaced with Service Result Stage + Appeal Status
Service Result Status mixed workflow states (Pending) with decision outcomes (Approved, Denied), modifications (Adjusted), appeal states (Appealed, Reversed), lifecycle (Expired), and disposition (Cancelled). The specific outcome type (approval, denial, certification, issuance, etc.) is now determined by the Service Result Type lookup. Separated into:
- Service Result Stage for workflow (Pending → Determined → Issued → Final)
- Appeal Status (Core) for appeal tracking (Submitted for Appeal, Appeal Granted, Appeal Denied, etc.)
- Item Disposition (Core) for final outcomes (Completed, Superseded, Canceled)
- Service Result Category (kept) distinguishes outcome types (Approval, Denial, Certification, Issuance, Adjustment, etc.)

Value mapping:
- Pending → Stage: Pending
- Approved → Stage: Determined + Result Category: Approval
- Denied → Stage: Determined + Result Category: Denial
- Adjusted → Stage: Determined + Result Category: Adjustment
- Appealed → Stage: Under Appeal + Appeal Status: Submitted for Appeal
- Reversed → Stage: Final + Appeal Status: Appeal Granted + Disposition: Superseded
- Expired → Stage: Final + Disposition: Completed (with Expiration Date tracking)
- Cancelled → Disposition: Canceled

**Note:** Service Result Type (lookup table) determines the nature of the result (approval, certification, issuance, etc.), while Service Result Category provides high-level classification. The Stage tracks the workflow, not the outcome type.

**Promoted to Core:**

### Service Delivery Method → Promoted to Core as "Delivery Method"
Service Delivery Method has been promoted to Core as "Delivery Method" for broader reuse across service delivery, training, support, and customer service contexts. The field is now available at Core scope with the same values (In Person, Virtual, Hybrid, Self Service, Phone, Mail, Mobile, Home Visit) and can be used across modules including Programs and Services, Training & Certification, IT Service Management, HR Benefits, Customer Service, and Events.

