# 💻 IT Service Management — Data Model Design

The **IT Service Management (Lite) / IT System Catalog** module provides a structured framework for managing IT service offerings, access control, system inventory, technology standards, and compliance oversight in a unified model. It supports core operational use cases such as submitting and fulfilling service requests, processing access requests and entitlement assignments, publishing orderable IT catalog items, and tracking hosting environments. At the same time, it enables governance scenarios including documenting system components and technology stacks, managing compliance assessments and system accreditations, and tracking remediation activities through POAM items. The module is designed to balance day-to-day service delivery with architectural visibility and security oversight, making it suitable for both public sector and commercial organizations that need lightweight ITSM capabilities combined with structured system and technology governance.

---

## Service Request Management

### IT Service Request
Represents a general service transaction submitted by a user for IT support, provisioning, hardware, software, or other service needs. Parent record for request items.

**Fields:**
- Name: Text
- Request Number: Text
- Request Type: Choice (IT Request Type)
- Request Status: Choice (Request Status)
- Priority: Choice (Priority)
- Requested By: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Request Date: Date Time
- Required Date: Date
- Assigned To: Lookup (Person)
- Assigned Team: Lookup (Organization Unit)
- Assignment Date: Date
- Method of Contact: Choice (Method of Contact)
- Business Justification: Memo
- Total Estimated Cost: Currency
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Fulfillment Start Date: Date
- Fulfillment Completion Date: Date
- Closed Date: Date
- Satisfaction Rating: Integer
- Feedback: Memo
- Notes: Memo

---

### IT Service Request Item
A line-level record under an IT Service Request that references a specific IT Catalog Item or fulfillment action.

**Fields:**
- Name: Text
- IT Service Request: Lookup (IT Service Request)
- Line Number: Integer
- IT Catalog Item: Lookup (IT Catalog Item)
- Item Description: Memo
- Quantity: Integer
- Unit Cost: Currency
- Total Cost: Currency
- Item Status: Choice (Request Item Status)
- Delivery Date: Date
- Assigned To: Lookup (Person)
- Fulfillment Notes: Memo
- Notes: Memo

---

## Access Management

### IT Access Request
Represents a request submitted to obtain, modify, or remove access to systems, applications, data, or other secured resources. Serves as the parent transaction record for access-related actions.

**Fields:**
- Name: Text
- Request Number: Text
- Access Request Type: Choice (Access Request Type)
- Request Status: Choice (Request Status)
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
- Manager Approval Status: Choice (Approval Status)
- Manager Approval Date: Date
- Requires Security Review: Yes / No
- Security Reviewer: Lookup (Person)
- Security Approval Status: Choice (Approval Status)
- Security Approval Date: Date
- Fulfillment Status: Choice (Fulfillment Status)
- Fulfilled By: Lookup (Person)
- Fulfillment Date: Date
- Closed Date: Date
- Notes: Memo

---

### IT Access Request Item
A line-level record under an IT Access Request specifying the individual entitlement, system, or role being requested. Allows a single request to contain multiple access changes.

**Fields:**
- Name: Text
- IT Access Request: Lookup (IT Access Request)
- Line Number: Integer
- Access Action: Choice (Access Action)
- IT System: Lookup (IT System)
- IT Entitlement: Lookup (IT Entitlement)
- Current Access Level: Text
- Requested Access Level: Text
- Item Status: Choice (Request Item Status)
- Approved: Yes / No
- Approval Date: Date
- Provisioned: Yes / No
- Provisioned Date: Date
- Related Entitlement Assignment: Lookup (IT Entitlement Assignment)
- Notes: Memo

---

### IT Entitlement
Defines a specific access right, permission set, license assignment, or role that can be granted to a user or system account.

**Fields:**
- Name: Text
- Entitlement Code: Text
- Entitlement Type: Choice (Entitlement Type)
- IT System: Lookup (IT System)
- Entitlement Category: Choice (Entitlement Category)
- Description: Memo
- Access Level: Choice (Access Level)
- Requires Approval: Yes / No
- Approver: Lookup (Person)
- Requires Manager Approval: Yes / No
- Requires Security Review: Yes / No
- Maximum Assignment Duration (Days): Integer
- Risk Level: Choice (Severity Level)
- Compliance Requirement: Lookup (Compliance Requirement)
- Is Active: Yes / No
- Notes: Memo

---

### IT Entitlement Assignment
Represents the assignment of an IT Entitlement to a person, account, or system. Tracks who has what access and its lifecycle status.

**Fields:**
- Name: Text
- Assignment Number: Text
- Person: Lookup (Person)
- IT Entitlement: Lookup (IT Entitlement)
- IT System: Lookup (IT System)
- Assignment Status: Choice (Assignment Status)
- Assignment Type: Choice (Assignment Type)
- Start Date: Date
- End Date: Date
- Is Temporary: Yes / No
- IT Access Request: Lookup (IT Access Request)
- Granted By: Lookup (Person)
- Granted Date: Date
- Last Review Date: Date
- Next Review Date: Date
- Review Status: Choice (Review Status)
- Revocation Date: Date
- Revoked By: Lookup (Person)
- Revocation Reason: Memo
- Account Username: Text
- Notes: Memo

---

## IT Service Catalog

### IT Catalog Item
Defines an orderable IT offering. Represents a published service, product package, provisioning action, or access offering that users can request.

**Fields:**
- Name: Text
- Item Code: Text
- Item Category: Choice (Catalog Item Category)
- Item Type: Choice (Catalog Item Type)
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
- Display Order: Integer
- Icon URL: Text
- Image URL: Text
- Documentation URL: Text
- Related IT System: Lookup (IT System)
- Is Orderable: Yes / No
- Is Active: Yes / No
- Tags: Text
- Notes: Memo

---

### IT Catalog Item Technology
A junction table linking an IT Catalog Item to one or more IT Technologies. Identifies technologies that are required, delivered, approved, or restricted for that offering.

**Fields:**
- Name: Text
- IT Catalog Item: Lookup (IT Catalog Item)
- IT Technology: Lookup (IT Technology)
- Technology Relationship: Choice (Technology Relationship)
- Version: Text
- Is Required: Yes / No
- Notes: Memo

---

## System & Component Management

### IT System
Represents a logical or operational information system. Serves as the primary record for tracking ownership, purpose, lifecycle status, and governance attributes.

**Fields:**
- Name: Text
- System Code: Text
- System Type: Choice (System Type)
- Operational Status: Choice (Operational Status)
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
- Notes: Memo

---

### IT System Component
Represents a structural part of an IT System, such as an application module, service, database, infrastructure element, or interface.

**Fields:**
- Name: Text
- Component Code: Text
- IT System: Lookup (IT System)
- IT System Component Type: Lookup (IT System Component Type)
- Component Status: Choice (Operational Status)
- Description: Memo
- Version: Text
- Primary Location: Lookup (Location)
- IT Hosting Location: Lookup (IT Hosting Location)
- Component Owner: Lookup (Person)
- Vendor: Lookup (Account)
- Is Critical: Yes / No
- Dependencies: Memo
- Notes: Memo

---

### IT System Component Type
Defines categories or classifications of system components (e.g., Application, Database, API, Infrastructure, Interface).

**Fields:**
- Name: Text
- Type Code: Text
- Component Category: Choice (Component Category)
- Description: Memo
- Is Active: Yes / No

---

### IT System Technology
A junction table linking an IT System (or optionally a specific System Component) to the IT Technologies it uses. Tracks technology usage and version information.

**Fields:**
- Name: Text
- IT System: Lookup (IT System)
- IT System Component: Lookup (IT System Component)
- IT Technology: Lookup (IT Technology)
- Technology Role: Choice (Technology Role)
- Version: Text
- Usage Context: Memo
- Is Production: Yes / No
- Installation Date: Date
- End of Support Date: Date
- Notes: Memo

---

## Technology Management

### IT Technology
Represents a technology concept, platform, framework, protocol, runtime, standard, or tool used within IT systems.

**Fields:**
- Name: Text
- Technology Code: Text
- IT Technology Type: Lookup (IT Technology Type)
- Technology Status: Choice (Technology Status)
- Description: Memo
- Vendor: Lookup (Account)
- Current Stable Version: Text
- Recommended Version: Text
- End of Life Date: Date
- End of Support Date: Date
- License Type: Choice (License Type)
- License Cost: Currency
- Is Approved: Yes / No
- Approval Date: Date
- Approved By: Lookup (Person)
- Is Restricted: Yes / No
- Restriction Reason: Memo
- Documentation URL: Text
- Vendor URL: Text
- Notes: Memo

---

### IT Technology Type
Defines classification categories for IT Technologies (e.g., Operating System, Database Engine, Framework, Protocol, Security Standard).

**Fields:**
- Name: Text
- Type Code: Text
- Description: Memo
- Parent Type: Lookup (IT Technology Type)
- Is Active: Yes / No

---

## Hosting & Infrastructure

### IT Hosting Location
Represents the physical or logical hosting environment for a system or component, such as a data center, cloud region, or managed hosting facility.

**Fields:**
- Name: Text
- Location Code: Text
- Hosting Type: Choice (Hosting Type)
- Physical Location: Lookup (Location)
- Cloud Region: Text
- Cloud Provider: Lookup (Account)
- Hosting Provider: Lookup (Account)
- Environment Type: Choice (Environment Type)
- Operational Status: Choice (Operational Status)
- Security Classification: Choice (Security Classification)
- Network Address Range: Text
- Primary Contact: Lookup (Person)
- Technical Contact: Lookup (Person)
- Service Agreement: Lookup (Agreement)
- Capacity: Text
- Utilization: Text
- Description: Memo
- Notes: Memo

---

## Compliance & Accreditation

### IT System Accreditation
Represents the formal authorization or approval status of an IT System to operate within defined security and compliance parameters.

**Fields:**
- Name: Text
- Accreditation Number: Text
- IT System: Lookup (IT System)
- Accreditation Type: Choice (Accreditation Type)
- Accreditation Status: Choice (Accreditation Status)
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
- Notes: Memo

---

### IT Compliance Assessment
Represents a formal evaluation of a system, component, or technology against defined standards, policies, or regulatory requirements. May generate findings or POAM items.

**Fields:**
- Name: Text
- Assessment Number: Text
- Assessment Type: Choice (Assessment Type)
- Assessment Status: Choice (Assessment Status)
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
- Notes: Memo

---

### IT POAM Item
Plan of Action and Milestones (POAM) record used to track remediation of identified compliance findings, vulnerabilities, or control gaps.

**Fields:**
- Name: Text
- POAM Number: Text
- IT System: Lookup (IT System)
- IT System Component: Lookup (IT System Component)
- IT Compliance Assessment: Lookup (IT Compliance Assessment)
- POAM Status: Choice (Action Status)
- Priority: Choice (Priority)
- Severity Level: Choice (Severity Level)
- Finding Type: Choice (Finding Type)
- Control Reference: Text
- Compliance Framework: Lookup (Compliance Framework)
- Weakness Description: Memo
- Risk Statement: Memo
- Proposed Solution: Memo
- Milestones: Memo
- Assigned To: Lookup (Person)
- Responsible Organization Unit: Lookup (Organization Unit)
- Identified Date: Date
- Target Completion Date: Date
- Actual Completion Date: Date
- Estimated Cost: Currency
- Actual Cost: Currency
- Mitigation Status: Choice (Mitigation Status)
- Completion Evidence: Memo
- Verification Date: Date
- Verified By: Lookup (Person)
- Related Risk Item: Lookup (Risk Item)
- Related Action Item: Lookup (Action Item)
- Supporting Document: Lookup (Document)
- Notes: Memo

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

## New Choice Fields

### IT Request Type
- Service Request
- Hardware Request
- Software Request
- Access Request
- Support Request
- Change Request
- Provisioning Request

### Request Item Status
- Pending
- In Progress
- Fulfilled
- Cancelled
- On Hold
- Blocked

### Access Request Type
- New Access
- Modify Access
- Remove Access
- Temporary Access
- Emergency Access
- Transfer Access

### Access Action
- Grant
- Modify
- Revoke
- Extend
- Transfer

### Entitlement Type
- System Access
- Application Role
- Data Access
- Administrative Rights
- License
- Group Membership
- API Access

### Entitlement Category
- User Access
- Administrative Access
- Service Account
- Privileged Access
- Read Only
- Read Write
- Full Control

### Access Level
- None
- Read
- Write
- Modify
- Delete
- Administrator
- Full Control

### Assignment Status
- Active
- Pending Activation
- Suspended
- Expired
- Revoked
- Under Review

### Assignment Type
- Permanent
- Temporary
- Emergency
- Project Based
- Role Based

### Review Status
- Current
- Review Required
- Under Review
- Approved
- Revoked

### Fulfillment Status
- Not Started
- In Progress
- Partially Fulfilled
- Fulfilled
- Cancelled

### Catalog Item Category
- Hardware
- Software
- Access
- Licenses
- Services
- Infrastructure
- Cloud Resources
- Support

### Catalog Item Type
- Orderable Item
- Service Offering
- Access Entitlement
- Provisioning Package
- Consultation Service

### Technology Relationship
- Required Technology
- Delivered Technology
- Approved Technology
- Restricted Technology
- Alternative Technology

### System Type
- Business Application
- Infrastructure System
- Platform Service
- Data System
- Security System
- Communications System
- Development Tool
- Enterprise System

### Component Category
- Application
- Database
- API
- Interface
- Middleware
- Infrastructure
- Network
- Storage

### Technology Role
- Operating System
- Database Platform
- Application Framework
- Development Tool
- Runtime Environment
- Integration Tool
- Security Tool
- Monitoring Tool

### Technology Status
- Approved
- Evaluation
- Deprecated
- Restricted
- End of Life
- Not Approved

### License Type
- Commercial
- Open Source
- Proprietary
- Subscription
- Perpetual
- Freeware
- Government License

### Hosting Type
- On Premises
- Co-Location
- Public Cloud
- Private Cloud
- Hybrid Cloud
- Managed Hosting
- Software as a Service

### Environment Type
- Production
- Development
- Test
- Staging
- Quality Assurance
- Training
- Sandbox
- Disaster Recovery

### Accreditation Type
- Authority to Operate (ATO)
- Interim Authority to Operate
- Interim Authority to Test
- Provisional Authorization
- Certification
- Self Assessment

### Accreditation Status
- Not Started
- In Progress
- Accredited
- Conditionally Accredited
- Denied
- Expired
- Under Review

### Assessment Type
- Security Assessment
- Compliance Audit
- Vulnerability Assessment
- Penetration Test
- Architecture Review
- Code Review
- Configuration Review
- Annual Review

### Assessment Status
- Planned
- In Progress
- Completed
- Under Review
- Approved
- Remediation Required

### Finding Type
- Security Control Gap
- Policy Violation
- Configuration Issue
- Vulnerability
- Process Deficiency
- Documentation Gap
- Architecture Issue

### Mitigation Status
- Not Started
- In Progress
- Risk Accepted
- Completed
- Verified
- Cancelled


