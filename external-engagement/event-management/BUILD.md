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
- Event Status: Choice (Event Status)
- Visibility: Choice (Visibility)
- Event Format: Choice (Event Format)
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
- Is Active: Yes / No

---

### Event Track
Represents a thematic or organizational grouping within an event (e.g., "Technology," "Policy," "Community Outreach"). Sessions and/or entries may be associated with a track.

**Completed:**

**Planned:**
- Name: Text
- Event: Lookup (Event)
- Track Code: Text
- Description: Memo
- Track Lead: Lookup (Person)
- Display Order: Integer
- Color Code: Text

---

## Event Planning & Intake

### Event Request
Captures a proposed or requested event prior to formal approval or scheduling. Used for intake, evaluation, and approval workflows before an official Event record is created.

**Completed:**

**Planned:**
- Name: Text
- Request Status: Choice (Request Status)
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
- Approval Status: Choice (Approval Status)
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
- Participant Type: Choice (Participant Type)
- Participation Status: Choice (Participation Status)
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
- Session Role: Choice (Session Role)
- Participation Status: Choice (Participation Status)
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
- Event Track: Lookup (Event Track)
- Session Code: Text
- Session Type: Choice (Session Type)
- Description: Memo
- Start Date Time: Date Time
- End Date Time: Date Time
- Duration (Minutes): Integer
- Location: Lookup (Location)
- Room: Text
- Virtual Meeting URL: Text
- Is Virtual: Yes / No
- Session Status: Choice (Session Status)
- Maximum Capacity: Integer
- Expected Attendees: Integer
- Actual Attendees: Integer
- Requires Pre-Registration: Yes / No
- Session Lead: Lookup (Person)
- Display Order: Integer
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
- Entry Type: Choice (Entry Type)
- Submission Type: Choice (Submission Type)
- Submission Date Time: Date Time
- Submitted By: Lookup (Person)
- Submitting Account: Lookup (Account)
- Title: Text
- Abstract: Memo
- Description: Memo
- Review Status: Choice (Approval Status)
- Reviewer: Lookup (Person)
- Review Date: Date
- Review Comments: Memo
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Entry Status: Choice (Entry Status)
- Display Order: Integer
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
- Sponsorship Level: Choice (Sponsorship Level)
- Sponsorship Type: Choice (Sponsorship Type)
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
- Display Order: Integer
- Notes: Memo

---

## New Choice Fields

### Event Status
- Draft
- Planning
- Open for Registration
- Registration Closed
- In Progress
- Completed
- Cancelled
- Postponed

### Event Format
- In Person
- Virtual
- Hybrid

### Participant Type
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

### Participation Status
- Invited
- Tentative
- Registered
- Confirmed
- Waitlisted
- Checked In
- Attended
- No Show
- Cancelled
- Declined

### Payment Status
- Not Required
- Pending
- Partial
- Paid
- Refunded
- Waived
- Complimentary

### Session Role
- Presenter
- Co-Presenter
- Moderator
- Panelist
- Attendee
- Facilitator
- Note Taker

### Session Type
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

### Session Status
- Scheduled
- In Progress
- Completed
- Cancelled
- Rescheduled

### Entry Type
- Presentation
- Poster
- Exhibition Booth
- Demonstration
- Workshop
- Lightning Talk
- Video Submission
- Abstract Only

### Entry Status
- Submitted
- Under Review
- Accepted
- Rejected
- Waitlisted
- Withdrawn
- Confirmed

### Sponsorship Level
- Title Sponsor
- Platinum
- Gold
- Silver
- Bronze
- Supporting
- In Kind

### Sponsorship Type
- Financial
- In Kind
- Media Partner
- Venue Partner
- Technology Partner
- Community Partner
