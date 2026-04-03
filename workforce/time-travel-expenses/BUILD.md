# ⏱️ Time, Travel, and Expenses — Data Model Design

The **Time, Travel, and Expense** module provides a unified structure for capturing time worked, planning personnel availability, authorizing travel, and submitting reimbursable expenses within an organization. It enables individuals to record time against standardized **Time Codes**, plan future availability through **Time Commitments**, request and manage travel through **Travel Requests** and **Travel Segments**, and submit costs through **Expense Reports** and **Expense Items** categorized by defined **Expense Categories**. This module supports use cases such as operational time tracking (e.g., investigations, casework, internal initiatives), workforce planning and duty scheduling, travel authorization and itinerary management, reimbursement processing, and financial reporting alignment with organizational units or funding sources. It is designed to be reusable across public sector, nonprofit, and commercial environments, supporting both lightweight tracking needs and scalable financial governance.

---

## Time Tracking

### Time Period
Represents a defined reporting cycle such as a week, pay period, or month used to group Time Entries and optionally Expense Reports for administrative or financial purposes.

**Completed:**

**Planned:**
- Period Code: Text
- Period Type: Choice (Schedule Frequency)
- Period Start Date: Date
- Period End Date: Date
- Fiscal Year: Integer
- Fiscal Quarter: Integer
- Fiscal Month: Integer
- Stage: Choice (Time Period Stage)
- Due Date: Date
- Locked Date: Date
- Is Locked: Yes / No
- Locked By: Lookup (Person)

---

### Time Code
Represents a hierarchical classification structure used to categorize Time Entries. Supports parent/child relationships for organizing work types such as investigations, operations, initiatives, or administrative activities.

**Completed:**

**Planned:**
- Time Code: Text
- Parent Time Code: Lookup (Time Code)
- Time Code Category: Choice (Time Code Category)
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

---

### Time Entry
Represents the actual time worked by a person on a specific date, including hours and associated Time Code. Serves as the foundational operational record for time tracking and reporting.

**Completed:**

**Planned:**
- Entry Number: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Time Period: Lookup (Time Period)
- Entry Date: Date
- Time Code: Lookup (Time Code)
- Stage: Choice (Time Entry Stage)
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

---

### Time Commitment
Represents a planned availability or obligation for a person over a defined date and time range. Used for scheduling, duty assignments, leave tracking, or other forward-looking planning purposes.

**Completed:**

**Planned:**
- Commitment Number: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Commitment Type: Choice (Time Commitment Type)
- Stage: Choice (Time Commitment Stage)
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

---

## Travel Management

### Travel Purpose
Represents standardized reasons for travel such as training, site visits, inspections, or conferences. Used to categorize and report on Travel Requests.

**Completed:**

**Planned:**
- Purpose Code: Text
- Purpose Category: Choice (Travel Purpose Category)
- Description: Memo
- Requires Justification: Yes / No
- Requires Advance Approval: Yes / No
- Default Approver: Lookup (Person)

---

### Travel Request
Represents a planned or approved trip, including traveler details, purpose, dates, and estimated costs. Serves as the primary authorization and oversight record for organizational travel.

**Completed:**

**Planned:**
- Travel Request Number: Text
- Traveler: Lookup (Person)
- Traveler Organization Unit: Lookup (Organization Unit)
- Additional Travelers: Text
- Stage: Choice (Travel Request Stage)
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
- Transportation Method: Choice (Travel Transportation Method)
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

---

### Travel Segment
Represents an individual component of a trip, such as a flight, lodging stay, or rental car, under a Travel Request. Enables structured tracking of itinerary details and associated estimated costs.

**Completed:**

**Planned:**
- Segment Number: Text
- Travel Request: Lookup (Travel Request)
- Segment Type: Choice (Travel Segment Type)
- Stage: Choice (Travel Segment Stage)
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
- Transportation Method: Choice (Travel Transportation Method)
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

---

## Expense Management

### Expense Category
Represents standardized classifications for expenses such as lodging, meals, mileage, registration fees, and supplies. Used to categorize Expense Items for reporting, policy enforcement, and financial analysis.

**Completed:**

**Planned:**
- Category Code: Text
- Parent Category: Lookup (Expense Category)
- Expense Category Type: Choice (Expense Category Type)
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
- Expense Report Number: Text
- Person: Lookup (Person)
- Organization Unit: Lookup (Organization Unit)
- Stage: Choice (Expense Report Stage)
- Report Type: Choice (Expense Report Type)
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
- Payment Method: Choice (Payment Method)
- Payment Reference: Text
- Rejected Date: Date
- Rejection Reason: Memo
- Supporting Document: Lookup (Document)

---

### Expense Item
Represents an individual expense transaction recorded under an Expense Report. Captures details such as date, amount, category, and optional travel linkage for reimbursement and accounting purposes.

**Completed:**

**Planned:**
- Item Number: Text
- Expense Report: Lookup (Expense Report)
- Expense Category: Lookup (Expense Category)
- Stage: Choice (Expense Item Stage)
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
- Payment Method: Choice (Payment Method)
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

---

## Choice Fields

**Completed:**

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

### Time Period Stage
- Scheduled
- Open
- Closed for Entry
- Under Review
- Finalized

### Time Entry Stage
- Draft
- Submitted
- Under Review
- Processing
- Posted
- Archived

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

### Time Commitment Stage
- Planned
- Requested
- Confirmed
- Active
- Closed

### Travel Request Stage
- Planning
- Submitted
- Under Review
- Authorized
- Booking
- In Travel
- Post-Trip
- Closed

### Travel Segment Stage
- Planned
- Booking
- Reserved
- Confirmed
- In Progress
- Completed

### Expense Report Stage
- Draft
- Submitted
- Under Review
- Processing
- Payment Issued
- Closed

### Expense Item Stage
- Entered
- Pending Receipt
- Ready for Review
- Under Review
- Processing
- Paid

**Planned:**
