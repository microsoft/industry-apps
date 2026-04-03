# 🎊 Event Management — Data Model Design

---

## Core Event Records

### Event
The primary record representing a planned occurrence (conference, meeting, hearing, training, festival, etc.). Stores core details such as title, description, dates, location, status, and overall ownership.

**Completed:**

**Planned:**
- Name: Text
- Event Code: Text
- Event Type: Lookup (Event Type)
- Description: Memo
- Details: Memo
- Stage: Choice (Event Stage)
- Decision Status: Choice (Item Decision Status)
- Visibility: Choice (Visibility)
- Event Format: Choice (Participation Mode)
- Start Date Time: Date Time
- End Date Time: Date Time
- Registration Open Date: Date
- Registration Close Date: Date
- Time Zone: Text
- Primary Location: Lookup (Location)
- Virtual Meeting URL: Text
- Is Virtual: Yes / No
- Is Hybrid: Yes / No
- Host Organization Unit: Lookup (Organization Unit)
- Host Account: Lookup (Account)
- Event Owner: Lookup (Person)
- Maximum Capacity: Integer
- Expected Attendees: Integer
- Actual Attendees: Integer
- Requires Registration: Yes / No
- Registration Fee: Currency
- Is Public: Yes / No
- Website URL: Text
- Tags: Text
- Notes: Memo

---

### Event Type
A classification table defining categories of events (e.g., Conference, Training, Public Hearing, Webinar). Often used to drive default behaviors, templates, or required fields.

**Completed:**

**Planned:**
- Name: Text
- Description: Memo
- Default Duration (Hours): Float
- Requires Approval: Yes / No

---

### Event Track
Represents a thematic or organizational grouping within an event (e.g., "Technology," "Policy," "Community Outreach"). Sessions and/or entries may be associated with a track.

**Completed:**

**Planned:**
- Name: Text
- Event: Lookup (Event)
- Parent Event Track: Lookup (Event Track)
- Track Code: Text
- Description: Memo
- Track Lead: Lookup (Person)
- Color Code: Text

---

## Event Planning & Intake

### Event Request
Captures a proposed or requested event prior to formal approval or scheduling. Used for intake, evaluation, and approval workflows before an official Event record is created.

**Completed:**

**Planned:**
- Name: Text
- Stage: Choice (Event Request Stage)
- Decision Status: Choice (Item Decision Status)
- Requested By: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Request Date: Date
- Proposed Event Type: Lookup (Event Type)
- Proposed Title: Text
- Purpose: Memo
- Proposed Start Date: Date
- Proposed End Date: Date
- Proposed Location: Lookup (Location)
- Estimated Attendees: Integer
- Estimated Budget: Currency
- Approved By: Lookup (Person)
- Approval Date: Date
- Approved Event: Lookup (Event)
- Justification: Memo
- Decision Notes: Memo

---

## Participation & Registration

### Event Participant
Represents an individual or organization involved in the event. This can include attendees, speakers, staff, volunteers, exhibitors, VIPs, or panelists. Tracks participation status (invited, registered, confirmed, checked-in, etc.).

**Completed:**

**Planned:**
- Name: Text
- Event: Lookup (Event)
- Person: Lookup (Person)
- Account: Lookup (Account)
- Participant Type: Choice (Event Participant Type)
- Stage: Choice (Event Participation Stage)
- Registration Date Time: Date Time
- Registration Method: Choice (Method of Contact)
- Invitation Sent Date: Date
- Confirmation Date: Date
- Check In Date Time: Date Time
- Check Out Date Time: Date Time
- Attended: Yes / No
- Registration Fee Paid: Currency
- Payment Status: Choice (Payment Status)
- Dietary Restrictions: Text
- Accessibility Needs: Memo
- Emergency Contact Name: Text
- Emergency Contact Phone: Text
- Badge Printed: Yes / No
- Certificate Issued: Yes / No
- Notes: Memo

---

### Event Session Participant
Links participants to specific sessions. Used when attendance, roles, or responsibilities differ by session (e.g., a speaker in one session, attendee in another).

**Completed:**

**Planned:**
- Name: Text
- Event Session: Lookup (Event Session)
- Event Participant: Lookup (Event Participant)
- Person: Lookup (Person)
- Session Role: Choice (Event Session Role)
- Stage: Choice (Event Participation Stage)
- Check In Date Time: Date Time
- Attended: Yes / No
- Presentation Order: Integer
- Notes: Memo

---

## Sessions & Schedule

### Event Session
Represents a scheduled time block within an event (e.g., breakout session, hearing segment, workshop, keynote slot). Includes start/end time, location/room, capacity, and session-specific details.

**Completed:**

**Planned:**
- Name: Text
- Event: Lookup (Event)
- Parent Event Session: Lookup (Event Session)
- Event Track: Lookup (Event Track)
- Session Code: Text
- Session Type: Choice (Event Session Type)
- Description: Memo
- Stage: Choice (Event Session Stage)
- Start Date Time: Date Time
- End Date Time: Date Time
- Duration (Minutes): Integer
- Location: Lookup (Location)
- Room: Text
- Virtual Meeting URL: Text
- Is Virtual: Yes / No
- Maximum Capacity: Integer
- Expected Attendees: Integer
- Actual Attendees: Integer
- Requires Pre-Registration: Yes / No
- Session Lead: Lookup (Person)
- Recording URL: Text
- Materials URL: Text
- Notes: Memo

---

## Presentations & Submissions

### Event Entry
Represents an exhibition, presentation, booth, poster, demonstration, or other showcased submission within an event. Typically includes submission details, review/approval status, assigned session or track, and associated presenters.

**Completed:**

**Planned:**
- Name: Text
- Entry Code: Text
- Event: Lookup (Event)
- Event Track: Lookup (Event Track)
- Assigned Session: Lookup (Event Session)
- Entry Type: Choice (Event Entry Type)
- Submission Type: Choice (Submission Type)
- Stage: Choice (Event Entry Stage)
- Decision Status: Choice (Item Decision Status)
- Submission Date Time: Date Time
- Submitted By: Lookup (Person)
- Submitting Account: Lookup (Account)
- Title: Text
- Abstract: Memo
- Description: Memo
- Reviewer: Lookup (Person)
- Review Date: Date
- Review Comments: Memo
- Approved By: Lookup (Person)
- Approval Date: Date
- Booth Number: Text
- Equipment Needs: Memo
- Space Requirements: Memo
- Supporting Document: Lookup (Document)
- Presentation URL: Text
- Notes: Memo

---

## Sponsorship & Support

### Event Sponsor
Represents an organization or entity providing financial or in-kind support for the event. May track sponsorship level, benefits, commitments, and related agreements.

**Completed:**

**Planned:**
- Name: Text
- Event: Lookup (Event)
- Sponsor Account: Lookup (Account)
- Sponsorship Level: Choice (Event Sponsorship Level)
- Sponsorship Type: Choice (Event Sponsorship Type)
- Stage: Choice (Event Sponsor Stage)
- Contact Person: Lookup (Person)
- Commitment Amount: Currency
- In Kind Value: Currency
- Total Value: Currency
- Agreement: Lookup (Agreement)
- Commitment Status: Choice (Commitment Status)
- Commitment Date: Date
- Received Date: Date
- Recognition Requirements: Memo
- Benefits Provided: Memo
- Logo URL: Text
- Website URL: Text
- Notes: Memo

---

## Choice Fields

**Completed:**

**Completed Last Round:**


### Event Participant Type
- Attendee
- Speaker
- Presenter
- Panelist
- Moderator
- Staff
- Volunteer
- Exhibitor
- Sponsor Representative
- VIP
- Media

### Event Session Role
- Presenter
- Co-Presenter
- Moderator
- Panelist
- Attendee
- Facilitator
- Note Taker

### Event Session Type
- Keynote
- Breakout Session
- Workshop
- Panel Discussion
- Roundtable
- Poster Session
- Networking
- Reception
- General Session
- Training

### Event Sponsorship Level
- Title Sponsor
- Platinum
- Gold
- Silver
- Bronze
- Supporting
- In Kind

### Event Sponsorship Type
- Financial
- In Kind
- Media Partner
- Venue Partner
- Technology Partner
- Community Partner

**Deferred:**

### Event Entry Type
- Presentation
- Poster
- Exhibition Booth
- Demonstration
- Workshop
- Lightning Talk
- Video Submission
- Abstract Only

**Planned:**

### Event Stage
Tracks the event through planning, registration, execution, and completion.
- Draft
- Planning
- Open for Registration
- Registration Closed
- Ready to Start
- In Progress
- Completed
- Cancelled

### Event Request Stage
Tracks event requests from submission through approval and scheduling.
- Draft
- Submitted
- Under Review
- Scheduling
- Published
- Closed

### Event Participation Stage
Tracks participant journey from invitation through attendance. Used by both Event Participant and Event Session Participant tables.
- Invited
- Registered
- Confirmed
- Checked In
- Attended

### Event Session Stage
Tracks session preparation and delivery.
- Draft
- Scheduled
- Ready
- In Progress
- Completed
- Cancelled

### Event Entry Stage
Tracks submissions (presentations, posters, booths) from submission through presentation.
- Draft
- Submitted
- Under Review
- Accepted
- Scheduled
- Presented

### Event Sponsor Stage
Tracks sponsor relationships from prospecting through fulfillment.
- Prospective
- Committed
- Agreement Signed
- Active
- Fulfilled

**Removed (Replaced with Stage Fields):**

### Event Status → Event Stage
Event Status tracked workflow progression, so it has been renamed to Event Stage and updated to reflect pure workflow steps. "Postponed" removed as it represents a disposition/outcome.

### Event Participation Status → Event Participation Stage
Event Participation Status tracked registration and attendance workflow, so it has been replaced with Event Participation Stage. Status outcomes (Tentative, Waitlisted, No Show, Cancelled, Declined) can be tracked using:
- Item Decision Status (Declined)
- Item Disposition (Cancelled, Withdrawn)
- Attended field (Yes/No) for attendance outcome
- Custom status fields if needed for Tentative/Waitlisted states

### Session Status (Scheduled Event Status) → Event Session Stage
Replaced with Event Session Stage which tracks session preparation and delivery workflow.

---



