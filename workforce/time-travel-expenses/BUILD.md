# ⏱️ Time, Travel, and Expenses — Data Model Design

The **Time, Travel, and Expense** module provides a unified structure for capturing time worked, planning personnel availability, authorizing travel, and submitting reimbursable expenses within an organization. It enables individuals to record time against standardized **Time Codes**, plan future availability through **Time Commitments**, request and manage travel through **Travel Requests** and **Travel Segments**, and submit costs through **Expense Reports** and **Expense Items** categorized by defined **Expense Categories**. This module supports use cases such as operational time tracking (e.g., investigations, casework, internal initiatives), workforce planning and duty scheduling, travel authorization and itinerary management, reimbursement processing, and financial reporting alignment with organizational units or funding sources. It is designed to be reusable across public sector, nonprofit, and commercial environments, supporting both lightweight tracking needs and scalable financial governance.

---

## Time Tracking

### Time Period
Represents a defined reporting cycle such as a week, pay period, or month used to group Time Entries and optionally Expense Reports for administrative or financial purposes.

**Completed:**

**Planned:**
- Name: Text
- Period Code: Text
- Period Type: Choice (Time Time Period Type)
- Period Start Date: Date
- Period End Date: Date
- Fiscal Year: Integer
- Fiscal Quarter: Integer
- Fiscal Month: Integer
- Period Status: Choice (Time Period Status)
- Due Date: Date
- Locked Date: Date
- Is Locked: Yes / No
- Locked By: Lookup (Person)
- Notes: Memo

---

### Time Code
Represents a hierarchical classification structure used to categorize Time Entries. Supports parent/child relationships for organizing work types such as investigations, operations, initiatives, or administrative activities.

**Completed:**

**Planned:**
- Name: Text
- Time Code: Text
- Parent Time Code: Lookup (Time Code)
- Time Code Category: Choice (Time Time Code Category)
- Description: Memo
- Organization Unit: Lookup (Organization Unit)
- Organization Initiative: Lookup (Organization Initiative)
- Project: Lookup (Project)
- Cost Center: Text
- Funding Source: Text
- Is Billable: Yes / No
- Is Overtime Eligible: Yes / No
- Requires Approval: Yes / No
- Default Approver: Lookup (Person)
- Effective Start Date: Date
- Effective End Date: Date
- Notes: Memo

---

### Time Entry
Represents the actual time worked by a person on a specific date, including hours and associated Time Code. Serves as the foundational operational record for time tracking and reporting.

**Completed:**

**Planned:**
- Name: Text
- Entry Number: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Time Period: Lookup (Time Period)
- Entry Date: Date
- Time Code: Lookup (Time Code)
- Entry Status: Choice (Time Entry Status)
- Hours: Float
- Overtime Hours: Float
- Is Billable: Yes / No
- Billing Rate: Currency
- Cost Rate: Currency
- Total Cost: Currency
- Total Billing: Currency
- Work Description: Memo
- Location: Lookup (Location)
- Related Project: Lookup (Project)
- Related Project Work Item: Lookup (Project Work Item)
- Related Action Item: Lookup (Action Item)
- Related Travel Request: Lookup (Travel Request)
- Submitted Date: Date
- Submitted By: Lookup (Person)
- Reviewed Date: Date
- Reviewed By: Lookup (Person)
- Review Notes: Memo
- Approved Date: Date
- Approved By: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Approval Notes: Memo
- Rejected Date: Date
- Rejection Reason: Memo
- Is Locked: Yes / No
- Notes: Memo

---

### Time Commitment
Represents a planned availability or obligation for a person over a defined date and time range. Used for scheduling, duty assignments, leave tracking, or other forward-looking planning purposes.

**Completed:**

**Planned:**
- Name: Text
- Commitment Number: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Commitment Type: Choice (Time Commitment Type)
- Commitment Status: Choice (Time Commitment Status)
- Start Date: Date
- End Date: Date
- Start Date Time: Date Time
- End Date Time: Date Time
- All Day: Yes / No
- Total Hours: Float
- Availability: Choice (Personnel Availability)
- Time Code: Lookup (Time Code)
- Location: Lookup (Location)
- Description: Memo
- Related Action Item: Lookup (Action Item)
- Related Project: Lookup (Project)
- Related Travel Request: Lookup (Travel Request)
- Requires Approval: Yes / No
- Requested Date: Date
- Approved Date: Date
- Approved By: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Approval Notes: Memo
- Is Recurring: Yes / No
- Recurrence Pattern: Text
- Notes: Memo

---

## Travel Management

### Travel Purpose
Represents standardized reasons for travel such as training, site visits, inspections, or conferences. Used to categorize and report on Travel Requests.

**Completed:**

**Planned:**
- Name: Text
- Purpose Code: Text
- Purpose Category: Choice (Time Travel Purpose Category)
- Description: Memo
- Requires Justification: Yes / No
- Requires Advance Approval: Yes / No
- Default Approver: Lookup (Person)

---

### Travel Request
Represents a planned or approved trip, including traveler details, purpose, dates, and estimated costs. Serves as the primary authorization and oversight record for organizational travel.

**Completed:**

**Planned:**
- Name: Text
- Travel Request Number: Text
- Traveler: Lookup (Person)
- Traveler Organization Unit: Lookup (Organization Unit)
- Additional Travelers: Text
- Travel Request Status: Choice (Time Travel Request Status)
- Travel Purpose: Lookup (Travel Purpose)
- Trip Description: Memo
- Business Justification: Memo
- Departure Date: Date
- Return Date: Date
- Total Days: Integer
- Origin Location: Lookup (Location)
- Origin City: Text
- Origin State or Province: Lookup (State or Province)
- Origin Country: Lookup (Country)
- Destination Location: Lookup (Location)
- Destination City: Text
- Destination State or Province: Lookup (State or Province)
- Destination Country: Lookup (Country)
- Is International: Yes / No
- Is Overnight: Yes / No
- Transportation Method: Choice (Time Transportation Method)
- Lodging Required: Yes / No
- Rental Car Required: Yes / No
- Estimated Total Cost: Currency
- Estimated Transportation Cost: Currency
- Estimated Lodging Cost: Currency
- Estimated Meal Cost: Currency
- Estimated Other Cost: Currency
- Actual Total Cost: Currency
- Funding Source: Text
- Cost Center: Text
- Organization Initiative: Lookup (Organization Initiative)
- Project: Lookup (Project)
- Related Event: Lookup (Event)
- Requested Date: Date
- Requested By: Lookup (Person)
- Submitted Date: Date
- Reviewed Date: Date
- Reviewed By: Lookup (Person)
- Review Notes: Memo
- Approved Date: Date
- Approved By: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Approval Notes: Memo
- Authorization Number: Text
- Cancelled Date: Date
- Cancellation Reason: Memo
- Completed Date: Date
- Trip Report: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Travel Segment
Represents an individual component of a trip, such as a flight, lodging stay, or rental car, under a Travel Request. Enables structured tracking of itinerary details and associated estimated costs.

**Completed:**

**Planned:**
- Name: Text
- Segment Number: Text
- Travel Request: Lookup (Travel Request)
- Segment Type: Choice (Time Travel Segment Type)
- Segment Status: Choice (Time Segment Status)
- Sequence Order: Integer
- Segment Date: Date
- Start Date Time: Date Time
- End Date Time: Date Time
- Origin City: Text
- Origin State or Province: Lookup (State or Province)
- Origin Country: Lookup (Country)
- Origin Location: Lookup (Location)
- Destination City: Text
- Destination State or Province: Lookup (State or Province)
- Destination Country: Lookup (Country)
- Destination Location: Lookup (Location)
- Transportation Method: Choice (Time Transportation Method)
- Carrier: Text
- Flight Number: Text
- Confirmation Number: Text
- Booking Reference: Text
- Booked By: Lookup (Person)
- Booking Date: Date
- Check In Date: Date
- Check Out Date: Date
- Nights: Integer
- Hotel Name: Text
- Hotel Address: Text
- Rental Company: Text
- Vehicle Type: Text
- Estimated Cost: Currency
- Actual Cost: Currency
- Segment Notes: Memo
- Notes: Memo

---

## Expense Management

### Expense Category
Represents standardized classifications for expenses such as lodging, meals, mileage, registration fees, and supplies. Used to categorize Expense Items for reporting, policy enforcement, and financial analysis.

**Completed:**

**Planned:**
- Name: Text
- Category Code: Text
- Parent Category: Lookup (Expense Category)
- Expense Category Type: Choice (Time Expense Category Type)
- Description: Memo
- Is Reimbursable: Yes / No
- Requires Receipt: Yes / No
- Receipt Threshold Amount: Currency
- Requires Justification: Yes / No
- Requires Approval: Yes / No
- Default Approver: Lookup (Person)
- Maximum Amount Per Day: Currency
- Maximum Amount Per Trip: Currency
- Is Mileage Based: Yes / No
- Mileage Rate: Currency
- GL Account: Text

---

### Expense Report
Represents a grouped submission of multiple Expense Items for review, approval, and reimbursement. Serves as the primary expense workflow record for an individual reporting period or trip.

**Completed:**

**Planned:**
- Name: Text
- Expense Report Number: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Report Status: Choice (Time Report Status)
- Report Type: Choice (Time Expense Report Type)
- Time Period: Lookup (Time Period)
- Related Travel Request: Lookup (Travel Request)
- Report Start Date: Date
- Report End Date: Date
- Purpose: Memo
- Business Justification: Memo
- Total Amount: Currency
- Total Reimbursable Amount: Currency
- Total Non Reimbursable Amount: Currency
- Total Approved Amount: Currency
- Total Paid Amount: Currency
- Currency Code: Text
- Advance Amount Received: Currency
- Amount Due to Person: Currency
- Amount Due from Person: Currency
- Funding Source: Text
- Cost Center: Text
- Project: Lookup (Project)
- Submitted Date: Date
- Submitted By: Lookup (Person)
- Reviewed Date: Date
- Reviewed By: Lookup (Person)
- Review Notes: Memo
- Approved Date: Date
- Approved By: Lookup (Person)
- Approval Status: Choice (Approval Status)
- Approval Notes: Memo
- Payment Date: Date
- Payment Method: Choice (Time Payment Method)
- Payment Reference: Text
- Rejected Date: Date
- Rejection Reason: Memo
- Supporting Document: Lookup (Document)
- Notes: Memo

---

### Expense Item
Represents an individual expense transaction recorded under an Expense Report. Captures details such as date, amount, category, and optional travel linkage for reimbursement and accounting purposes.

**Completed:**

**Planned:**
- Name: Text
- Item Number: Text
- Expense Report: Lookup (Expense Report)
- Expense Category: Lookup (Expense Category)
- Item Status: Choice (Time Item Status)
- Expense Date: Date
- Description: Memo
- Merchant Name: Text
- Merchant Location: Text
- Location: Lookup (Location)
- City: Text
- State or Province: Lookup (State or Province)
- Country: Lookup (Country)
- Related Travel Segment: Lookup (Travel Segment)
- Quantity: Float
- Unit Cost: Currency
- Total Amount: Currency
- Currency Code: Text
- Exchange Rate: Float
- Amount in Local Currency: Currency
- Is Reimbursable: Yes / No
- Reimbursable Amount: Currency
- Is Billable: Yes / No
- Billable Amount: Currency
- Payment Method: Choice (Time Payment Method)
- Is Personal Card: Yes / No
- Receipt Attached: Yes / No
- Receipt Required: Yes / No
- Receipt Number: Text
- Mileage: Float
- Mileage Rate: Currency
- Start Odometer: Float
- End Odometer: Float
- Trip Purpose: Text
- Attendees: Text
- Number of Attendees: Integer
- Cost Per Person: Currency
- Approved Amount: Currency
- Approval Notes: Memo
- Rejected: Yes / No
- Rejection Reason: Memo
- GL Account: Text
- Cost Center: Text
- Supporting Document: Lookup (Document)
- Notes: Memo

---

## Reused Core Tables

The following Core tables are used directly by this module:

### Person *(Core)*
Travelers, time entry submitters, approvers, reviewers.

### Organization Unit *(Core)*
Cost centers, organizational ownership of time codes and expenses.

### Organization Initiative *(Core)*
Strategic initiatives linked to time entries and travel requests.

### Location *(Core)*
Work locations, travel origins, destinations, segment locations.

### Project *(Core)*
Projects linked to time entries, time codes, commitments, and travel.

### Project Work Item *(Core)*
Work items linked to time entries.

### Action Item *(Core)*
Tasks linked to time entries and commitments.

### Event *(Core)*
Events linked to travel requests (conferences, trainings).

### Document *(Core)*
Supporting documentation, receipts, trip reports, authorizations.

---

## New Choice Fields

### Time Period Type
- Weekly
- Biweekly
- Semimonthly
- Monthly
- Quarterly
- Annual
- Custom

### Time Period Status
- Future
- Open
- Pending Approval
- Approved
- Locked
- Closed

### Time Code Category
- Operational
- Project
- Initiative
- Administrative
- Leave
- Training
- Travel
- Investigative
- Direct Work
- Indirect Work

### Time Entry Status
- Draft
- Submitted
- Under Review
- Approved
- Rejected
- Locked

### Time Commitment Type
- Work Assignment
- Duty Schedule
- Leave
- Training
- Travel
- Meeting
- On Call
- Unavailable
- Other

### Time Commitment Status
- Planned
- Requested
- Approved
- Active
- Completed
- Cancelled

### Travel Purpose Category
- Training
- Conference
- Site Visit
- Inspection
- Audit
- Investigation
- Meeting
- Consultation
- Operational Support
- Emergency Response
- Customer Visit
- Vendor Visit

### Travel Request Status
- Draft
- Submitted
- Under Review
- Approved
- Authorized
- In Progress
- Completed
- Cancelled
- Rejected

### Travel Transportation Method
- Air
- Rail
- Personal Vehicle
- Rental Car
- Government Vehicle
- Taxi / Rideshare
- Public Transit
- Walking
- Other

### Travel Segment Type
- Flight
- Ground Transportation
- Lodging
- Rental Car
- Rail
- Other

### Travel Segment Status
- Planned
- Booked
- Confirmed
- In Progress
- Completed
- Cancelled

### Expense Category Type
- Lodging
- Meals
- Transportation
- Mileage
- Airfare
- Ground Transportation
- Registration
- Supplies
- Equipment
- Communication
- Parking
- Tolls
- Per Diem
- Other

### Expense Report Type
- Travel Expense
- Operational Expense
- Training Expense
- Project Expense
- Reimbursement
- Blanket Expense

### Expense Report Status
- Draft
- Submitted
- Under Review
- Approved
- Payment Pending
- Paid
- Rejected
- Cancelled

### Export Report Item Status
- Entered
- Submitted
- Approved
- Rejected
- Paid

### Expense Payment Method
- Personal Card
- Corporate Card
- Cash
- Check
- Direct Deposit
- Wire Transfer
- Reimbursement
