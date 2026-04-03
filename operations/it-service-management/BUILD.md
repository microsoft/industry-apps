# 💻 IT Service Management — Data Model Design

The **IT Service Management (Lite) / IT System Catalog** module provides a structured framework for managing IT service offerings, access control, system inventory, technology standards, and compliance oversight in a unified model. It supports core operational use cases such as submitting and fulfilling service requests, processing access requests and entitlement assignments, publishing orderable IT catalog items, and tracking hosting environments. At the same time, it enables governance scenarios including documenting system components and technology stacks, managing compliance assessments and system accreditations, and tracking remediation activities through POAM items. The module is designed to balance day-to-day service delivery with architectural visibility and security oversight, making it suitable for both public sector and commercial organizations that need lightweight ITSM capabilities combined with structured system and technology governance.

---

## Service Request Management

### IT Service Request
Represents a general service transaction submitted by a user for IT support, provisioning, hardware, software, or other service needs. Parent record for request items.

**Completed:**

**Planned:**
- Request Number: Text
- Request Type: Choice (IT Request Type)
- Stage: Choice (IT Service Request Stage)
- Decision Status: Choice (Item Decision Status)
- Priority: Choice (Priority)
- Requested By: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Request Date: Date Time
- Required Date: Date
- Assigned Team: Lookup (Organization Unit)
- Assignment Date: Date
- Method of Contact: Choice (Method of Contact)
- Business Justification: Memo
- Total Estimated Cost: Currency
- Decision Date: Date
- Decided By: Lookup (Person)
- Fulfillment Start Date: Date
- Fulfillment Completion Date: Date
- Closed Date: Date
- Satisfaction Rating: Integer
- Feedback: Memo

---

### IT Service Request Item
A line-level record under an IT Service Request that references a specific IT Catalog Item or fulfillment action.

**Completed:**

**Planned:**
- IT Service Request: Lookup (IT Service Request)
- Line Number: Integer
- IT Catalog Item: Lookup (IT Catalog Item)
- Item Description: Memo
- Stage: Choice (IT Service Request Item Stage)
- Completion Status: Choice (Item Completion Status)
- Quantity: Integer
- Unit Cost: Currency
- Total Cost: Currency
- Delivery Date: Date
- Fulfillment Notes: Memo

---

## Access Management

### IT Access Request
Represents a request submitted to obtain, modify, or remove access to systems, applications, data, or other secured resources. Serves as the parent transaction record for access-related actions.

**Completed:**

**Planned:**
- Request Number: Text
- Access Request Type: Choice (IT Access Request Type)
- Stage: Choice (IT Access Request Stage)
- Decision Status: Choice (Item Decision Status)
- Completion Status: Choice (Item Completion Status)
- Priority: Choice (Priority)
- Requested For: Lookup (Person)
- Requested By: Lookup (Person)
- Request Date: Date Time
- Business Justification: Memo
- Access Start Date: Date
- Access End Date: Date
- Is Temporary: Yes / No
- Requires Manager Approval: Yes / No
- Manager: Lookup (Person)
- Manager Decision Status: Choice (Item Decision Status)
- Manager Decision Date: Date
- Requires Security Review: Yes / No
- Security Reviewer: Lookup (Person)
- Security Decision Status: Choice (Item Decision Status)
- Security Decision Date: Date
- Fulfilled By: Lookup (Person)
- Fulfillment Date: Date
- Closed Date: Date

---

### IT Access Request Item
A line-level record under an IT Access Request specifying the individual entitlement, system, or role being requested. Allows a single request to contain multiple access changes.

**Completed:**

**Planned:**
- IT Access Request: Lookup (IT Access Request)
- Line Number: Integer
- Access Action: Choice (IT Access Action)
- IT System: Lookup (IT System)
- IT Entitlement: Lookup (IT Entitlement)
- Current Access Level: Text
- Requested Access Level: Text
- Stage: Choice (IT Access Request Item Stage)
- Decision Status: Choice (Item Decision Status)
- Decision Date: Date
- Provisioned Date: Date
- Related Entitlement Assignment: Lookup (IT Entitlement Assignment)
- Description: Memo

---

### IT Entitlement
Defines a specific access right, permission set, license assignment, or role that can be granted to a user or system account.

**Completed:**

**Planned:**
- Entitlement Code: Text
- Entitlement Type: Choice (IT Entitlement Type)
- IT System: Lookup (IT System)
- Entitlement Category: Choice (IT Entitlement Category)
- Description: Memo
- Access Level: Choice (IT Access Level)
- Requires Approval: Yes / No
- Approver: Lookup (Person)
- Requires Manager Approval: Yes / No
- Requires Security Review: Yes / No
- Maximum Assignment Duration (Days): Integer
- Risk Level: Choice (Severity Level)
- Compliance Requirement: Lookup (Compliance Requirement)

---

### IT Entitlement Assignment
Represents the assignment of an IT Entitlement to a person, account, or system. Tracks who has what access and its lifecycle status.

**Completed:**

**Planned:**
- Assignment Number: Text
- Person: Lookup (Person)
- IT Entitlement: Lookup (IT Entitlement)
- IT System: Lookup (IT System)
- Stage: Choice (IT Entitlement Assignment Stage)
- Validation Status: Choice (Item Validation Status)
- Assignment Type: Choice (IT Assignment Type)
- Start Date: Date
- End Date: Date
- Is Temporary: Yes / No
- IT Access Request: Lookup (IT Access Request)
- Granted By: Lookup (Person)
- Granted Date: Date
- Last Review Date: Date
- Next Review Date: Date
- Revocation Date: Date
- Revoked By: Lookup (Person)
- Revocation Reason: Memo
- Account Username: Text

---

## IT Service Catalog

### IT Catalog Item
Defines an orderable IT offering. Represents a published service, product package, provisioning action, or access offering that users can request.

**Completed:**

**Planned:**
- Item Code: Text
- Parent IT Catalog Item: Lookup (IT Catalog Item)
- Item Category: Choice (IT Catalog Item Category)
- Item Type: Choice (IT Catalog Item Type)
- Publication Status: Choice (Publication Status)
- Visibility: Choice (Visibility)
- Short Description: Text
- Description: Memo
- Fulfillment Instructions: Memo
- Estimated Delivery Time (Days): Integer
- Unit Cost: Currency
- Requires Approval: Yes / No
- Default Approver: Lookup (Person)
- Approving Organization Unit: Lookup (Organization Unit)
- Provider Organization Unit: Lookup (Organization Unit)
- Service Owner: Lookup (Person)
- Icon URL: Text
- Image URL: Text
- Documentation URL: Text
- Related IT System: Lookup (IT System)
- Is Orderable: Yes / No
- Tags: Text

---

### IT Catalog Item Technology
A junction table linking an IT Catalog Item to one or more IT Technologies. Identifies technologies that are required, delivered, approved, or restricted for that offering.

**Completed:**

**Planned:**
- IT Catalog Item: Lookup (IT Catalog Item)
- IT Technology: Lookup (IT Technology)
- Technology Relationship: Choice (IT Technology Relationship)
- Version: Text
- Is Required: Yes / No
- Description: Memo

---

## System & Component Management

### IT System
Represents a logical or operational information system. Serves as the primary record for tracking ownership, purpose, lifecycle status, and governance attributes.

**Completed:**

**Planned:**
- System Code: Text
- System Type: Choice (IT System Type)
- Lifecycle Stage: Choice (Lifecycle Stage)
- Security Classification: Choice (Security Classification)
- Description: Memo
- Purpose: Memo
- System Owner: Lookup (Person)
- Business Owner: Lookup (Person)
- Technical Owner: Lookup (Person)
- Owning Organization Unit: Lookup (Organization Unit)
- Primary Location: Lookup (Location)
- IT Hosting Location: Lookup (IT Hosting Location)
- Go Live Date: Date
- Retirement Date: Date
- Is Mission Critical: Yes / No
- Is Externally Accessible: Yes / No
- Contains PII: Yes / No
- Contains Sensitive Data: Yes / No
- User Count: Integer
- Annual Operating Cost: Currency
- Vendor: Lookup (Account)
- Support Contact: Lookup (Person)
- Documentation URL: Text
- System URL: Text
- Related Agreement: Lookup (Agreement)
- Compliance Framework: Lookup (Compliance Framework)
- Legal Authority: Lookup (Legal Authority)

---

### IT System Component
Represents a structural part of an IT System, such as an application module, service, database, infrastructure element, or interface.

**Completed:**

**Planned:**
- Component Code: Text
- Parent IT System Component: Lookup (IT System Component)
- IT System: Lookup (IT System)
- IT System Component Type: Lookup (IT System Component Type)
- Lifecycle Stage: Choice (Lifecycle Stage)
- Description: Memo
- Version: Text
- Primary Location: Lookup (Location)
- IT Hosting Location: Lookup (IT Hosting Location)
- Component Owner: Lookup (Person)
- Vendor: Lookup (Account)
- Is Critical: Yes / No
- Dependencies: Memo

---

### IT System Component Type
Defines categories or classifications of system components (e.g., Application, Database, API, Infrastructure, Interface).

**Completed:**

**Planned:**
- Type Code: Text
- Component Category: Choice (IT Component Category)
- Description: Memo

---

### IT System Technology
A junction table linking an IT System (or optionally a specific System Component) to the IT Technologies it uses. Tracks technology usage and version information.

**Completed:**

**Planned:**
- IT System: Lookup (IT System)
- IT System Component: Lookup (IT System Component)
- IT Technology: Lookup (IT Technology)
- Technology Role: Choice (IT Technology Role)
- Version: Text
- Usage Context: Memo
- Is Production: Yes / No
- Installation Date: Date
- End of Support Date: Date

---

## Technology Management

### IT Technology
Represents a technology concept, platform, framework, protocol, runtime, standard, or tool used within IT systems.

**Completed:**

**Planned:**
- Technology Code: Text
- IT Technology Type: Lookup (IT Technology Type)
- Technology Status: Choice (IT Technology Status)
- Description: Memo
- Vendor: Lookup (Account)
- Current Stable Version: Text
- Recommended Version: Text
- End of Life Date: Date
- End of Support Date: Date
- License Type: Choice (IT License Type)
- License Cost: Currency
- Is Approved: Yes / No
- Approval Date: Date
- Approved By: Lookup (Person)
- Is Restricted: Yes / No
- Restriction Reason: Memo
- Documentation URL: Text
- Vendor URL: Text

---

### IT Technology Type
Defines classification categories for IT Technologies (e.g., Operating System, Database Engine, Framework, Protocol, Security Standard).

**Completed:**

**Planned:**
- Type Code: Text
- Description: Memo
- Parent Type: Lookup (IT Technology Type)

---

## Hosting & Infrastructure

### IT Hosting Location
Represents the physical or logical hosting environment for a system or component, such as a data center, cloud region, or managed hosting facility.

**Completed:**

**Planned:**
- Location Code: Text
- Hosting Type: Choice (IT Hosting Type)
- Physical Location: Lookup (Location)
- Cloud Region: Text
- Cloud Provider: Lookup (Account)
- Hosting Provider: Lookup (Account)
- Environment Type: Choice (IT Environment Type)
- Lifecycle Stage: Choice (Lifecycle Stage)
- Security Classification: Choice (Security Classification)
- Network Address Range: Text
- Primary Contact: Lookup (Person)
- Technical Contact: Lookup (Person)
- Service Agreement: Lookup (Agreement)
- Capacity: Text
- Utilization: Text
- Description: Memo

---

## Compliance & Accreditation

### IT System Accreditation
Represents the formal authorization or approval status of an IT System to operate within defined security and compliance parameters.

**Completed:**

**Planned:**
- Accreditation Number: Text
- IT System: Lookup (IT System)
- Accreditation Type: Choice (IT Accreditation Type)
- Stage: Choice (IT System Accreditation Stage)
- Decision Status: Choice (Item Decision Status)
- Compliance Framework: Lookup (Compliance Framework)
- Authorization Date: Date
- Expiration Date: Date
- Authorizing Official: Lookup (Person)
- Authorizing Organization Unit: Lookup (Organization Unit)
- Security Level: Choice (Security Classification)
- Accreditation Scope: Memo
- Conditions: Memo
- Risk Statement: Memo
- Last Assessment Date: Date
- Next Assessment Date: Date
- Supporting Document: Lookup (Document)

---

### IT Compliance Assessment
Represents a formal evaluation of a system, component, or technology against defined standards, policies, or regulatory requirements. May generate findings or POAM items.

**Completed:**

**Planned:**
- Assessment Number: Text
- Assessment Type: Choice (IT Assessment Type)
- Stage: Choice (IT Compliance Assessment Stage)
- IT System: Lookup (IT System)
- IT System Component: Lookup (IT System Component)
- IT Technology: Lookup (IT Technology)
- Compliance Framework: Lookup (Compliance Framework)
- Assessment Start Date: Date
- Assessment Completion Date: Date
- Assessor: Lookup (Person)
- Assessment Team: Text
- Assessment Scope: Memo
- Assessment Method: Memo
- Overall Result: Choice (Overall Result)
- Compliance Status: Choice (Compliance Status)
- Total Findings: Integer
- Critical Findings: Integer
- High Findings: Integer
- Medium Findings: Integer
- Low Findings: Integer
- Total POAM Items: Integer
- Executive Summary: Memo
- Recommendations: Memo
- Next Assessment Date: Date
- Supporting Document: Lookup (Document)

---

### IT POAM Item
Plan of Action and Milestones (POAM) record used to track remediation of identified compliance findings, vulnerabilities, or control gaps.

**Completed:**

**Planned:**
- POAM Number: Text
- IT System: Lookup (IT System)
- IT System Component: Lookup (IT System Component)
- IT Compliance Assessment: Lookup (IT Compliance Assessment)
- Stage: Choice (IT POAM Item Stage)
- Action Status: Choice (Action Status)
- Completion Status: Choice (Item Completion Status)
- Validation Status: Choice (Item Validation Status)
- Priority: Choice (Priority)
- Severity Level: Choice (Severity Level)
- Finding Type: Choice (IT Finding Type)
- Control Reference: Text
- Compliance Framework: Lookup (Compliance Framework)
- Weakness Description: Memo
- Risk Statement: Memo
- Proposed Solution: Memo
- Milestones: Memo
- Responsible Organization Unit: Lookup (Organization Unit)
- Identified Date: Date
- Target Completion Date: Date
- Actual Completion Date: Date
- Estimated Cost: Currency
- Actual Cost: Currency
- Completion Evidence: Memo
- Verification Date: Date
- Verified By: Lookup (Person)
- Related Risk Item: Lookup (Risk Item)
- Related Action Item: Lookup (Action Item)
- Supporting Document: Lookup (Document)

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Represents requesters, approvers, system owners, technical contacts, assessors.

### Account *(Core)*
Represents vendors, cloud providers, hosting providers.

### Organization Unit *(Core)*
Departments requesting services, owning systems, providing support.

### Location *(Core)*
Physical locations for systems, hosting facilities, data centers.

### Action Item *(Core)*
Operational tasks linked to service requests, access provisioning, POAM remediation.

### Agreement *(Core)*
Service level agreements, hosting agreements, vendor contracts.

### Compliance Framework *(Core)*
NIST, FedRAMP, ISO 27001, HIPAA, PCI-DSS frameworks.

### Compliance Requirement *(Core)*
Specific control requirements for systems and entitlements.

### Legal Authority *(Core)*
Regulatory basis for system operations and compliance.

### Risk Item *(Core)*
Risks identified during assessments linked to POAM items.

### Document *(Core)*
System documentation, assessment reports, accreditation packages.

---

## Choice Fields

**Planned:**

### IT Request Type
- Service Request
- Hardware Request
- Software Request
- Access Request
- Support Request
- Change Request
- Provisioning Request

### IT Access Request Type
- New Access
- Modify Access
- Remove Access
- Temporary Access
- Emergency Access
- Transfer Access

### IT Access Action
- Grant
- Modify
- Revoke
- Extend
- Transfer

### IT Entitlement Type
- System Access
- Application Role
- Data Access
- Administrative Rights
- License
- Group Membership
- API Access

### IT Entitlement Category
- User Access
- Administrative Access
- Service Account
- Privileged Access
- Read Only
- Read Write
- Full Control

### IT Access Level
- None
- Read
- Write
- Modify
- Delete
- Administrator
- Full Control

### IT Assignment Type
- Permanent
- Temporary
- Emergency
- Project Based
- Role Based

### IT Catalog Item Category
- Hardware
- Software
- Access
- Licenses
- Services
- Infrastructure
- Cloud Resources
- Support

### IT Catalog Item Type
- Orderable Item
- Service Offering
- Access Entitlement
- Provisioning Package
- Consultation Service

### IT Technology Relationship
- Required Technology
- Delivered Technology
- Approved Technology
- Restricted Technology
- Alternative Technology

### IT System Type
- Business Application
- Infrastructure System
- Platform Service
- Data System
- Security System
- Communications System
- Development Tool
- Enterprise System

### IT Component Category
- Application
- Database
- API
- Interface
- Middleware
- Infrastructure
- Network
- Storage

### IT Technology Role
- Operating System
- Database Platform
- Application Framework
- Development Tool
- Runtime Environment
- Integration Tool
- Security Tool
- Monitoring Tool

### IT Technology Status
- Approved
- Evaluation
- Deprecated
- Restricted
- End of Life
- Not Approved

### IT License Type
- Commercial
- Open Source
- Proprietary
- Subscription
- Perpetual
- Freeware
- Government License

### IT Hosting Type
- On Premises
- Co-Location
- Public Cloud
- Private Cloud
- Hybrid Cloud
- Managed Hosting
- Software as a Service

### IT Environment Type
- Production
- Development
- Test
- Staging
- Quality Assurance
- Training
- Sandbox
- Disaster Recovery

### IT Accreditation Type
- Authority to Operate (ATO)
- Interim Authority to Operate
- Interim Authority to Test
- Provisional Authorization
- Certification
- Self Assessment

### IT Accreditation Status
- Not Started
- In Progress
- Accredited
- Conditionally Accredited
- Denied
- Expired
- Under Review

### IT Assessment Type
- Security Assessment
- Compliance Audit
- Vulnerability Assessment
- Penetration Test
- Architecture Review
- Code Review
- Configuration Review
- Annual Review

### IT Finding Type
- Security Control Gap
- Policy Violation
- Configuration Issue
- Vulnerability
- Process Deficiency
- Documentation Gap
- Architecture Issue

### IT Compliance Assessment Stage
Tracks compliance assessment workflow from scheduling through finalization.
- Scheduled
- Fieldwork
- Analysis
- Report Drafting
- Report Review
- Finalized

### IT Service Request Stage
Tracks service request workflow from submission through closure.
- Draft
- Submitted
- Under Review
- Approved
- In Progress
- Fulfilled
- Closed

### IT Service Request Item Stage
Tracks individual request item fulfillment.
- Pending
- Assigned
- In Progress
- Delivered

### IT Access Request Stage
Tracks access request workflow through approval and provisioning.
- Draft
- Submitted
- Manager Review
- Security Review
- Approved
- Provisioning
- Completed
- Closed

### IT Access Request Item Stage
Tracks individual access item provisioning.
- Pending
- In Progress
- Provisioned

### IT Entitlement Assignment Stage
Tracks entitlement assignment lifecycle from activation through revocation.
- Pending Activation
- Active
- Under Review
- Suspended
- Revoked
- Expired

### IT System Accreditation Stage
Tracks system accreditation workflow from assessment through authorization.
- Not Started
- Assessment
- Documentation
- Review
- Authorized
- Monitoring
- Renewal

### IT POAM Item Stage
Tracks remediation workflow from identification through verification.
- Identified
- Planning
- In Progress
- Verification
- Closed

**Removed (Replaced with Stage and Core Status Fields):**

### IT Assessment Status → Replaced with IT Compliance Assessment Stage
Assessment Status mixed workflow (Planned, In Progress) with outcomes (Completed, Approved, Remediation Required). Separated into:
- IT Compliance Assessment Stage for workflow
- Overall Result (Core) for assessment outcome
- Compliance Status (Core) for compliance determination

### IT Request Item Status → Replaced with IT Service Request Item Stage + Completion Status
Request Item Status mixed workflow (Pending, In Progress, Fulfilled) with work states (On Hold, Blocked, Cancelled). Separated into:
- IT Service Request Item Stage for workflow
- Item Completion Status (Core) for work tracking (Blocked, On Hold)
- Item Disposition (Core) for final outcomes (Completed, Cancelled)

### IT Assignment Status → Replaced with IT Entitlement Assignment Stage
Assignment Status mixed workflow (Pending Activation, Active, Under Review) with final states (Suspended, Expired, Revoked). Now tracked as Stage values representing assignment lifecycle phases.

### IT Review Status → Replaced with Item Validation Status (Core)
Review Status tracked access review outcomes. Replaced with Core Item Validation Status:
- Current → Validated
- Review Required → Pending Validation
- Under Review → Pending Validation
- Approved → Validated
- Revoked → Failed Validation

### IT Fulfillment Status → Replaced with Item Completion Status (Core)
Fulfillment Status tracked work progress. Replaced with Core Item Completion Status which provides standard work state tracking (Not Started, Planned, In Progress, Blocked, Completed).

### IT Accreditation Status → Replaced with IT System Accreditation Stage + Decision Status
Accreditation Status mixed workflow (Not Started, In Progress, Under Review) with authorization outcomes (Accredited, Conditionally Accredited, Denied, Expired). Separated into:
- IT System Accreditation Stage for workflow
- Item Decision Status (Core) for authorization outcome
- Item Disposition (Core) for final states (Expired, Superseded)

### IT Mitigation Status → Replaced with Item Completion Status + Validation Status (Core)
Mitigation Status tracked POAM remediation progress. Separated into:
- IT POAM Item Stage for workflow
- Item Completion Status (Core) for work tracking (Not Started, In Progress, Blocked, Completed)
- Item Validation Status (Core) for verification (Validated, Failed Validation)
- Keep Action Status (Core) for overall action state tracking


