# 📥 Request Tracker — Data Model Design

The **Request Tracker** module provides a lightweight, centralized way for teams or divisions to intake, triage, assign, and track cross-organizational or external requests from submission through completion. It serves as a flexible front door for handling items such as data pulls, access requests, policy questions, document reviews, partner inquiries, leadership taskings, service coordination requests, or general assistance requests. By standardizing Requests and Request Types, the module enables consistent routing, prioritization, ownership, and status tracking without the overhead of a full case management system. It is especially useful for smaller teams that need visibility, accountability, and basic reporting on workload and turnaround time, while retaining the ability to link requests to more specialized modules if the work expands in scope.

---

## Request Management

### Request
Represents a single submitted request for work, information, approval, or action. This is the primary tracking record from intake through completion and closure.

**Completed:**

**Planned:**
- Name: Text
- Request Number: Text
- Request Type: Lookup (Request Type)
- Request Status: Choice (Request Status)
- Request Urgency: Choice (Request Urgency)
- Priority: Choice (Priority)
- Submitted By: Lookup (Person)
- Submitting Account: Lookup (Account)
- Submitting Organization Unit: Lookup (Organization Unit)
- Contact Person: Lookup (Person)
- Contact Email: Text
- Contact Phone: Text
- Contact Method: Choice (Method of Contact)
- Submission Date: Date
- Submission Date Time: Date Time
- Submission Method: Choice (Method of Receipt)
- Received Date: Date
- Received By: Lookup (Person)
- Request Description: Memo
- Request Details: Memo
- Attachments Description: Memo
- Due Date: Date
- Target Response Date: Date
- Target Completion Date: Date
- Assigned To: Lookup (Person)
- Assigned Organization Unit: Lookup (Organization Unit)
- Assignment Date: Date
- Assigned By: Lookup (Person)
- Reviewer: Lookup (Person)
- Review Date: Date
- Review Notes: Memo
- Requires Approval: Yes / No
- Approver: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Approval Date: Date
- Approval Notes: Memo
- Response Date: Date Time
- Response: Memo
- Resolution Date: Date Time
- Resolution: Memo
- Outcome: Choice (Overall Result)
- Completion Date: Date Time
- Completed By: Lookup (Person)
- Effort Hours: Float
- Response Time (Hours): Float
- Time to Complete (Hours): Float
- Closure Date: Date
- Closed By: Lookup (Person)
- Closure Notes: Memo
- Satisfaction Rating: Integer
- Feedback: Memo
- Related Action Item: Lookup (Action Item)
- Related Project Work Item: Lookup (Project Work Item)
- Related Discussion Item: Lookup (Discussion Item)
- Related Document: Lookup (Document)
- Supporting Document: Lookup (Document)
- Is External: Yes / No
- Is Confidential: Yes / No
- Security Classification: Choice (Security Classification)
- Visibility: Choice (Visibility)
- Tags: Text
- Notes: Memo

---

### Request Type
Defines the classification of a request and supports routing, prioritization, and reporting. Provides default routing rules, target timelines, and workflow configuration.

**Completed:**

**Planned:**
- Name: Text
- Type Code: Text
- Parent Request Type: Lookup (Request Type)
- Request Type Category: Choice (Request Type Category)
- Description: Memo
- Purpose: Memo
- Examples: Memo
- Default Priority: Choice (Priority)
- Default Urgency: Choice (Request Urgency)
- Default Assigned Organization Unit: Lookup (Organization Unit)
- Default Assigned Person: Lookup (Person)
- Default Reviewer: Lookup (Person)
- Requires Approval: Yes / No
- Default Approver: Lookup (Person)
- Target Response Time (Hours): Float
- Target Completion Time (Hours): Float
- Allows External Submission: Yes / No
- Requires Contact Information: Yes / No
- Instructions for Submitter: Memo
- Instructions for Handler: Memo
- Workflow Notes: Memo
- Icon: Text
- Color: Text

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Requestors, contacts, assigned handlers, reviewers, approvers.

### Account *(Core)*
Submitting organizations, external entities making requests.

### Organization Unit *(Core)*
Submitting units, assigned units, routing targets.

### Action Item *(Core)*
Related tasks spawned from requests.

### Discussion Item *(Core)*
Collaboration threads linked to requests.

### Document *(Core)*
Supporting documentation, attachments, response materials.

### Project Work Item *(Core)*
Work items created or linked as a result of requests.

---

## New Choice Fields

### Request Type Category
- Information Request
- Data Request
- Access Request
- Document Review
- Policy Question
- Technical Support
- Service Request
- Leadership Tasking
- Partner Inquiry
- General Assistance
- Coordination Request
- Research Request
- Report Request
- Approval Request

### Request Urgency
- Immediate
- Urgent
- Standard
- Low
