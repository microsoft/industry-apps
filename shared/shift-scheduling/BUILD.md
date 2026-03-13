# 🔧 Shift Scheduling — Data Model Design

The **Shift Scheduling module** provides tables for managing workforce scheduling across operational contexts. It supports creating schedules for locations, defining shifts and staffing requirements, assigning individuals and teams to shifts, tracking participant availability, and managing recurring shift patterns. This module is designed for use cases such as retail operations, healthcare facilities, field operations, security posts, and other environments requiring structured shift-based coverage.

---

## Schedule Management

### Shift Location
Represents a schedule created for a specific operational context (such as a field operation, retail outlet, clinical unit, or facility) and acts as the parent container for shifts, staffing requirements, and assignments.

**Completed:**
- Name: Text
- Schedule Type: Choice (Shift Schedule Type)
- Start Date: Date
- End Date: Date
- Owning Organization Unit: Lookup (Organization Unit)
- Physical Location: Lookup (Location)
- Manager: Lookup (Shift Worker)
- Schedule Status: Choice (Scheduled Event Status)
- Description: Memo

**Planned:**

---

### Shift Schedule
Defines a specific time block within a schedule that requires staffing coverage, such as a day shift, night shift, or operational coverage window.

**Completed:**
- Name: Text
- Shift Location: Lookup (Shift Location)
- Shift Type: Choice (Shift Type)
- Start Date Time: DateTime
- End Date Time: DateTime
- Shift Template: Lookup (Shift Template)
- Shift Status: Choice (Scheduled Event Status)
- Description: Memo

**Planned:**

---

## Staffing Requirements & Assignments

### Shift Staffing Requirement
Defines the number and type of personnel required to staff a specific shift, optionally tied to a role, team type, or operational location or post.

**Completed:**
- Name: Text
- Shift Location: Lookup (Shift Location)
- Scheduled Shift: Lookup (Shift Schedule)
- Required Role: Lookup (Shift Role)
- Quantity Required: Integer
- Priority: Choice (Priority)
- Fulfillment Status: Choice (Item Completion Status)
- Location or Post Reference: Text
- Description: Memo

**Planned:**

---

### Shift Assignment
Represents an individual assigned to fulfill a staffing requirement for a specific shift, including the role they will perform and the time window of the assignment.

**Completed:**
- Name: Text
- Shift Location: Lookup (Shift Location)
- Scheduled Shift: Lookup (Shift Schedule)
- Staffing Requirement: Lookup (Shift Staffing Requirement)
- Participant: Lookup (Shift Participant)
- Shift Worker: Lookup (Shift Worker)
- Assigned Role: Lookup (Shift Role)
- Assignment Start: DateTime
- Assignment End: DateTime
- Assignment Status: Choice (Item Assignment Status)
- Attendance Status: Choice (Attendance Status)
- Description: Memo

**Planned:**

---

### Shift Team Assignment
Represents a team assigned to a shift or staffing requirement, allowing groups of personnel to be scheduled together for operational coverage.

**Completed:**
- Name: Text
- Shift Location: Lookup (Shift Location)
- Scheduled Shift: Lookup (Shift Schedule)
- Staffing Requirement: Lookup (Shift Staffing Requirement)
- Team Reference: Text
- Assignment Start: DateTime
- Assignment End: DateTime
- Assignment Status: Choice (Item Assignment Status)
- Attendance Status: Choice (Attendance Status)
- Description: Memo

**Planned:**

---

## Worker Pool

### Shift Worker
Represents a person who can be scheduled for shifts. Can be a standalone worker record, linked to an existing Contact for reuse, and/or linked to a User if they have system access. Allows scheduling both internal employees and external workers (contractors, volunteers, casual staff) who may not have system accounts.

**Completed:**
- Name: Text
- First Name: Text
- Last Name: Text
- Email: Email
- Phone: Phone
- Contact: Lookup (Person)
- User: Lookup (User)
- Employee ID or Badge Number: Text
- Is Active: Yes / No
- Description: Memo

**Planned:**

---

## Participants & Availability

### Shift Participant
Represents a person available to be scheduled, either within a specific schedule (roster-based) or in the general worker pool. Optional location allows for both location-specific rosters and system-wide availability.

**Completed:**
- Name: Text
- Shift Worker: Lookup (Shift Worker)
- Shift Location: Lookup (Shift Location)
- Default Role: Lookup (Shift Role)
- Availability Start: Date
- Availability End: Date
- Participant Status: Choice (Item Completion Status)
- Description: Memo

**Planned:**

---

### Shift Availability
Tracks participant availability or unavailability for scheduling purposes. Supports multiple patterns: general ongoing availability (no dates), specific date ranges, location-specific availability, or availability for specific shifts. All lookups and dates are optional to enable flexible scheduling scenarios.

**Completed:**
- Name: Text
- Shift Worker: Lookup (Shift Worker)
- Participant: Lookup (Shift Participant)
- Shift Location: Lookup (Shift Location)
- Shift Schedule: Lookup (Shift Schedule)
- Availability Type: Choice (Shift Availability Type)
- Start Date Time: DateTime
- End Date Time: DateTime
- Reason: Text
- Status: Choice (Item Completion Status)
- Description: Memo

**Planned:**

---

## Configuration & Templates

### Shift Role
Defines roles that may be required for staffing shifts, providing a standardized way to describe responsibilities such as nurse, cashier, inspector, or security officer.

**Completed:**
- Name: Text
- Role Code: Text
- Core Competency: Lookup (Competency)
- Is Active: Yes / No
- Description: Memo

**Planned:**

---

### Shift Template
Defines reusable shift definitions that can be applied to schedules to quickly generate common coverage patterns such as standard day shifts or recurring shift blocks.

**Completed:**
- Name: Text
- Template Code: Text
- Shift Type: Choice (Shift Type)
- Default Start Time: Text
- Default End Time: Text
- Duration Hours: Decimal
- Is Active: Yes / No
- Description: Memo

**Planned:**

---

### Shift Rotation Pattern
Defines repeating shift rotation cycles used for recurring staffing patterns such as rotating crews, alternating shifts, or scheduled on-call coverage.

**Completed:**
- Name: Text
- Pattern Code: Text
- Rotation Type: Choice (Shift Rotation Type)
- Cycle Length Days: Integer
- Rotation Frequency: Choice (Schedule Frequency)
- Is Active: Yes / No
- Description: Memo

**Planned:**

---

## ✅ Module-Specific Choice Fields

**Completed:**

### Shift Schedule Type
Type of shift schedule being managed.
- Fixed Schedule
- Rotating Schedule
- On-Call Schedule
- Flexible Schedule
- Seasonal Schedule

### Shift Type
Classification of shift timing and pattern.
- Day Shift
- Evening Shift
- Night Shift
- Split Shift
- On-Call
- Standby
- Weekend
- Holiday

### Shift Availability Type
Indicates whether the entry represents availability or unavailability.
- Available
- Unavailable
- Preferred
- Restricted
- Leave
- Training
- Temporary Assignment

### Shift Rotation Type
Pattern used for rotating shift assignments.
- Fixed Rotation
- Rolling Rotation
- Bidirectional Rotation
- Custom Pattern

**Planned:**

---

## 🔗 Reused Components from Core

The following tables and choice fields are referenced from the **Core** module:

### Tables
- Contact (for linking to existing person records)
- User (for system account references)
- Organization Unit (for owning units)
- Location (for physical locations)
- Competency (for role requirements)

### Choice Fields
- Priority
- Scheduled Event Status (used for schedule and shift status)
- Item Completion Status (used for requirements, participants, and availability)
- Item Assignment Status (used for assignment workflow)
- Attendance Status (used for tracking attendance at shifts)
- Schedule Frequency
- General Category
- Yes No

---