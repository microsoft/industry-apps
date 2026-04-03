# 📥 Request Tracker — Data Model Design

The **Request Tracker** module provides a lightweight, centralized way for teams or divisions to intake, triage, assign, and track cross-organizational or external requests from submission through completion. It serves as a flexible front door for handling items such as data pulls, access requests, policy questions, document reviews, partner inquiries, leadership taskings, service coordination requests, or general assistance requests. By standardizing Requests and Request Types, the module enables consistent routing, prioritization, ownership, and status tracking without the overhead of a full case management system. It is especially useful for smaller teams that need visibility, accountability, and basic reporting on workload and turnaround time, while retaining the ability to link requests to more specialized modules if the work expands in scope.

---

## Request Management

### Request
Represents a single submitted request for work, information, approval, or action. This is the primary tracking record from intake through completion and closure.

**Completed:**

**Planned:**
- Request Number: Text
- Request Type: Lookup (Request Type)
- Approval Status: Choice (Approval Status)
- Priority: Choice (Priority)
- Submitted By: Lookup (User)
- Submitted By (External): Lookup (Person)
- Submitting Account: Lookup (Account)
- Submitting Organization Unit: Lookup (Organization Unit)
- Contact Person: Lookup (Person)
- Contact Email: Text
- Contact Phone: Text
- Contact Preference: Choice (Method of Contact)
- Submission Date: Date
- Submission Date Time: Date Time
- Submission Method: Choice (Method of Contact)
- Received Date: Date
- Received By: Lookup (User)
- Request Description: Memo
- Attachments Description: Memo
- Due Date: Date
- Target Response Date: Date
- Target Completion Date: Date
- Assigned Organization Unit: Lookup (Organization Unit)
- Assignment Date: Date
- Assigned By: Lookup (User)
- Reviewer: Lookup (User)
- Review Date: Date
- Review Notes: Memo
- Requires Approval: Yes / No
- Approver: Lookup (User)
- Approval Status: Choice (Approval Status)
- Approval Date: Date
- Approval Notes: Memo
- Response Date: Date Time
- Response: Memo
- Resolution Date: Date Time
- Resolution: Memo
- Outcome: Choice (Overall Result)
- Completion Date: Date Time
- Completed By: Lookup (User)
- Effort Hours: Float
- Response Time (Hours): Float
- Time to Complete (Hours): Float
- Closure Date: Date
- Closed By: Lookup (User)
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

---

### Request Type
Defines the classification of a request and supports routing, prioritization, and reporting. Provides default routing rules, target timelines, and workflow configuration.

**Completed:**

**Planned:**
- Type Code: Text
- Parent Request Type: Lookup (Request Type)
- Request Type Category: Choice (Request Type Category)
- Description: Memo
- Purpose: Memo
- Examples: Memo
- Default Priority: Choice (Priority)
- Default Assigned Organization Unit: Lookup (Organization Unit)
- Default Assigned Person: Lookup (User)
- Default Reviewer: Lookup (User)
- Requires Approval: Yes / No
- Default Approver: Lookup (User)
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

## Choice Fields

**Planned:**

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
