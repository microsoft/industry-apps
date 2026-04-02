# 💰 Financial Management — Data Model Design

Financial Management is an end-to-end module that supports the planning, acquisition, contractual oversight, and financial execution of goods and services. It enables organizations to define budgets and funding sources, validate availability of funds, manage procurement processes, formalize agreements through contracts and amendments, issue purchase orders, record financial commitments, and process payments. The module supports use cases such as departmental budget control, competitive sourcing and vendor selection, contract lifecycle management, project- or grant-funded spending, compliance-driven funds certification, and structured payment tracking. It provides traceability from initial request through contract award to final payment, ensuring financial accountability, operational transparency, and audit readiness across both public sector and commercial environments.

---

## Budget Planning & Control

### Budget
Represents an approved financial plan for a defined fiscal period and organizational scope. A Budget establishes the total planned spending authority and serves as the parent record for detailed allocations. It is used to monitor planned versus committed and expended amounts over time.

**Completed:**

**Planned:**
- Name: Text
- Budget Number: Text
- Fiscal Year: Text
- Budget Period Start Date: Date
- Budget Period End Date: Date
- Stage: Choice (Budget Stage)
- Decision Status: Choice (Item Decision Status)
- Organization Unit: Lookup (Organization Unit)
- Budget Owner: Lookup (Person)
- Total Planned Amount: Currency
- Total Allocated Amount: Currency
- Total Committed Amount: Currency
- Total Expended Amount: Currency
- Total Available Amount: Currency
- Approved By: Lookup (Person)
- Approval Date: Date
- Description: Memo
- Notes: Memo

---

### Budget Line Item
Detailed allocation within a Budget tied to a specific Financial Funding Source, Financial Classification, and Financial Period. Budget Line Items define how funds are distributed across categories and are used during funds checks and commitment creation to ensure spending stays within approved limits.

**Completed:**

**Planned:**
- Name: Text
- Budget: Lookup (Budget)
- Parent Budget Line Item: Lookup (Budget Line Item)
- Line Number: Text
- Financial Funding Source: Lookup (Financial Funding Source)
- Financial Classification: Lookup (Financial Classification)
- Organization Unit: Lookup (Organization Unit)
- Planned Amount: Currency
- Committed Amount: Currency
- Expended Amount: Currency
- Available Amount: Currency
- Period Start Date: Date
- Period End Date: Date
- Line Item Status: Choice (Budget Status)
- Description: Memo
- Notes: Memo

---

### Financial Funding Source
Identifies the origin of funds used to finance expenditures, such as a grant, appropriation, cost center, project, or internal budget. Funding Sources are referenced by budgets, commitments, and transactions to maintain traceability and compliance.

**Completed:**

**Planned:**
- Name: Text
- Funding Source Code: Text
- Funding Source Type: Choice (Financial Funding Source Type)
- Organization Unit: Lookup (Organization Unit)
- Funding Source Status: Choice (Operational Status)
- Total Authorized Amount: Currency
- Total Allocated Amount: Currency
- Total Available Amount: Currency
- Effective Start Date: Date
- Effective End Date: Date
- Sponsor Account: Lookup (Account)
- Grant Number: Text
- Appropriation Reference: Text
- Requires Compliance Reporting: Yes / No
- Description: Memo
- Restrictions: Memo
- Notes: Memo

---

### Financial Classification
A categorization structure used to classify financial transactions, such as expense type, revenue type, object class, or fee category. Financial Classifications support reporting, budget allocation, compliance, and accounting integration.

**Completed:**

**Planned:**
- Name: Text
- Classification Code: Text
- Classification Type: Choice (Financial Classification Type)
- Parent Classification: Lookup (Financial Classification)
- Account Code: Text
- Description: Memo

---

## Procurement & Sourcing

### Purchase Request
An internal request to procure goods or services, typically initiated by program or operational staff. Purchase Requests capture business justification, estimated cost, and required approvals prior to sourcing or issuing a purchase order.

**Completed:**

**Planned:**
- Name: Text
- Request Number: Text
- Stage: Choice (Purchase Request Stage)
- Decision Status: Choice (Item Decision Status)
- Request Date: Date
- Requested By: Lookup (Person)
- Requesting Organization Unit: Lookup (Organization Unit)
- Purpose: Memo
- Justification: Memo
- Priority: Choice (Priority)
- Total Estimated Cost: Currency
- Delivery Required Date: Date
- Delivery Location: Lookup (Location)
- Approved By: Lookup (Person)
- Approval Date: Date
- Financial Funding Source: Lookup (Financial Funding Source)
- Budget Line Item: Lookup (Budget Line Item)
- Preferred Vendor: Lookup (Account)
- Procurement Method: Choice (Procurement Method)
- Related Procurement Package: Lookup (Procurement Package)
- Related Purchase Order: Lookup (Purchase Order)
- Notes: Memo

---

### Purchase Request Item
Line-level detail associated with a Purchase Request, specifying requested goods or services, quantities, and estimated pricing. These items support evaluation, sourcing, and budget validation activities.

**Completed:**

**Planned:**
- Name: Text
- Purchase Request: Lookup (Purchase Request)
- Line Number: Integer
- Item Type: Choice (Procurement Item Type)
- Product: Lookup (Product)
- Description: Memo
- Quantity: Float
- Unit of Issue: Choice (Unit of Issue)
- Estimated Unit Price: Currency
- Estimated Line Total: Currency
- Financial Classification: Lookup (Financial Classification)
- Delivery Required Date: Date
- Notes: Memo

---

### Procurement Package
A container for a sourcing process, such as a Request for Quote (RFQ), Request for Proposal (RFP), or sole-source procurement. The Procurement Package tracks vendor responses, evaluations, approvals, and award decisions prior to contract execution.

**Completed:**

**Planned:**
- Name: Text
- Package Number: Text
- Procurement Type: Choice (Procurement Type)
- Procurement Method: Choice (Procurement Method)
- Stage: Choice (Procurement Package Stage)
- Solicitation Issue Date: Date
- Response Due Date: Date
- Evaluation Completion Date: Date
- Award Date: Date
- Total Estimated Value: Currency
- Requesting Organization Unit: Lookup (Organization Unit)
- Contracting Officer: Lookup (Person)
- Technical Evaluator: Lookup (Person)
- Small Business Set Aside: Yes / No
- Competition Required: Yes / No
- Number of Responses Received: Integer
- Evaluation Criteria: Memo
- Award Justification: Memo
- Awarded Vendor: Lookup (Account)
- Awarded Contract: Lookup (Contract)
- Description: Memo
- Notes: Memo

---

## Contract Management

### Contract
A formal agreement with an external organization defining scope of work, pricing structure, performance period, terms and conditions, and total authorized value. Contracts serve as the governing instrument under which purchase orders, deliverables, and payments are executed.

**Completed:**

**Planned:**
- Name: Text
- Contract Number: Text
- Contract Type: Choice (Contract Type)
- Agreement Type: Choice (Agreement Type)
- Stage: Choice (Contract Stage)
- Decision Status: Choice (Item Decision Status)
- Contractor: Lookup (Account)
- Contractor Contact: Lookup (Person)
- Contracting Officer: Lookup (Person)
- Contracting Organization Unit: Lookup (Organization Unit)
- Contract Manager: Lookup (Person)
- Award Date: Date
- Effective Start Date: Date
- Effective End Date: Date
- Performance Period Start Date: Date
- Performance Period End Date: Date
- Base Period End Date: Date
- Total Contract Value: Currency
- Total Funded Amount: Currency
- Total Committed Amount: Currency
- Total Invoiced Amount: Currency
- Total Paid Amount: Currency
- Total Remaining Amount: Currency
- Pricing Structure: Choice (Contract Pricing Structure)
- Vehicle Contract: Lookup (Contract)
- Procurement Package: Lookup (Procurement Package)
- Related Agreement: Lookup (Agreement)
- Place of Performance: Lookup (Location)
- Includes Options: Yes / No
- Number of Option Periods: Integer
- Renewable: Yes / No
- Next Renewal Date: Date
- Description: Memo
- Scope of Work: Memo
- Terms and Conditions: Memo
- Notes: Memo

---

### Contract Amendment
A modification to an existing Contract that changes scope, funding amount, pricing, performance period, or contractual terms. Amendments maintain a structured history of changes and ensure traceability of contract evolution over time.

**Completed:**

**Planned:**
- Name: Text
- Amendment Number: Text
- Contract: Lookup (Contract)
- Amendment Type: Choice (Contract Amendment Type)
- Stage: Choice (Contract Amendment Stage)
- Decision Status: Choice (Item Decision Status)
- Amendment Date: Date
- Effective Date: Date
- Amended By: Lookup (Person)
- Amendment Value: Currency
- New Total Contract Value: Currency
- Scope Change: Yes / No
- Funding Change: Yes / No
- Period Change: Yes / No
- New End Date: Date
- Description: Memo
- Justification: Memo
- Approved By: Lookup (Person)
- Approval Date: Date
- Notes: Memo

---

### Contract Line
A structured pricing or scope element within a Contract, such as a labor category, fixed-price item, or cost-reimbursable component. Contract Lines allow financial tracking and purchase orders to align with defined contract elements.

**Completed:**

**Planned:**
- Name: Text
- Contract: Lookup (Contract)
- Line Number: Text
- Line Type: Choice (Contract Line Type)
- Product: Lookup (Product)
- Description: Memo
- Quantity: Float
- Unit of Issue: Choice (Unit of Issue)
- Unit Price: Currency
- Total Line Value: Currency
- Financial Classification: Lookup (Financial Classification)
- Period of Performance Start Date: Date
- Period of Performance End Date: Date
- Notes: Memo

---

### Contract Deliverable
A specific output, service, or product required under a Contract. Deliverables typically include due dates, acceptance criteria, and status tracking to monitor contractual performance and compliance.

**Completed:**

**Planned:**
- Name: Text
- Contract: Lookup (Contract)
- Deliverable Number: Text
- Deliverable Type: Choice (Contract Deliverable Type)
- Description: Memo
- Stage: Choice (Contract Deliverable Stage)
- Acceptance Status: Choice (Item Acceptance Status)
- Due Date: Date
- Submitted Date: Date
- Accepted Date: Date
- Rejected Date: Date
- Acceptance Criteria: Memo
- Reviewer: Lookup (Person)
- Review Comments: Memo
- Supporting Document: Lookup (Document)
- Is Critical: Yes / No
- Notes: Memo

---

### Contract Milestone
A significant contractual event or date, such as kickoff, phase completion, renewal decision, or option exercise. Milestones help monitor contract lifecycle progress and key decision points.

**Completed:**

**Planned:**
- Name: Text
- Contract: Lookup (Contract)
- Milestone Type: Choice (Contract Milestone Type)
- Description: Memo
- Target Date: Date
- Actual Date: Date
- Milestone Status: Choice (Milestone Status)
- Responsible Party: Lookup (Account)
- Responsible Person: Lookup (Person)
- Is Critical: Yes / No
- Payment Linked: Yes / No
- Completion Criteria: Memo
- Notes: Memo

---

## Financial Execution

### Financial Commitment
Represents funds that have been formally reserved or obligated for an approved financial action, such as issuing a purchase order. Commitments reduce available budget and provide forward visibility into planned spending prior to invoice and payment.

**Completed:**

**Planned:**
- Name: Text
- Commitment Number: Text
- Commitment Type: Choice (Financial Commitment Type)
- Stage: Choice (Financial Commitment Stage)
- Validation Status: Choice (Item Validation Status)
- Commitment Date: Date
- Committed Amount: Currency
- Expended Amount: Currency
- Remaining Amount: Currency
- Financial Funding Source: Lookup (Financial Funding Source)
- Budget Line Item: Lookup (Budget Line Item)
- Organization Unit: Lookup (Organization Unit)
- Financial Classification: Lookup (Financial Classification)
- Purchase Order: Lookup (Purchase Order)
- Contract: Lookup (Contract)
- Related Account: Lookup (Account)
- Fiscal Year: Text
- Period Start Date: Date
- Period End Date: Date
- Committed By: Lookup (Person)
- Certification Required: Yes / No
- Certified By: Lookup (Person)
- Certification Date: Date
- Description: Memo
- Notes: Memo

---

### Purchase Order
An authorized order issued to a supplier under a Contract or approved procurement action. A Purchase Order formally commits funds and defines the goods or services to be delivered, along with pricing and delivery terms.

**Completed:**

**Planned:**
- Name: Text
- Purchase Order Number: Text
- Purchase Order Type: Choice (Purchase Order Type)
- Stage: Choice (Purchase Order Stage)
- Decision Status: Choice (Item Decision Status)
- Order Date: Date
- Vendor: Lookup (Account)
- Vendor Contact: Lookup (Person)
- Contract: Lookup (Contract)
- Procurement Package: Lookup (Procurement Package)
- Purchase Request: Lookup (Purchase Request)
- Buyer: Lookup (Person)
- Buying Organization Unit: Lookup (Organization Unit)
- Requestor: Lookup (Person)
- Requestor Organization Unit: Lookup (Organization Unit)
- Total Order Amount: Currency
- Total Invoiced Amount: Currency
- Total Paid Amount: Currency
- Delivery Required Date: Date
- Delivery Location: Lookup (Location)
- Ship To Location: Lookup (Location)
- Bill To Location: Lookup (Location)
- Payment Terms: Text
- Shipping Terms: Text
- Financial Commitment: Lookup (Financial Commitment)
- Approved By: Lookup (Person)
- Approval Date: Date
- Special Instructions: Memo
- Notes: Memo

---

### Purchase Order Line
Line-level detail within a Purchase Order specifying item or service description, quantity, unit price, and funding allocation. Purchase Order Lines enable detailed receiving, invoice matching, and financial tracking.

**Completed:**

**Planned:**
- Name: Text
- Purchase Order: Lookup (Purchase Order)
- Line Number: Integer
- Item Type: Choice (Procurement Item Type)
- Product: Lookup (Product)
- Contract Line: Lookup (Contract Line)
- Description: Memo
- Quantity Ordered: Float
- Quantity Received: Float
- Quantity Invoiced: Float
- Unit of Issue: Choice (Unit of Issue)
- Unit Price: Currency
- Line Total: Currency
- Financial Funding Source: Lookup (Financial Funding Source)
- Budget Line Item: Lookup (Budget Line Item)
- Financial Classification: Lookup (Financial Classification)
- Delivery Required Date: Date
- Stage: Choice (Purchase Order Line Stage)
- Notes: Memo

---

### Payment
Represents the disbursement of funds to a supplier or payee in satisfaction of an approved financial obligation. Payments may reference invoices, purchase orders, contracts, and funding sources, and support audit and reconciliation processes.

**Completed:**

**Planned:**
- Name: Text
- Payment Number: Text
- Stage: Choice (Payment Stage)
- Payment Status: Choice (Payment Status)
- Payment Method: Choice (Payment Method)
- Payment Date: Date
- Payment Amount: Currency
- Payee: Lookup (Account)
- Purchase Order: Lookup (Purchase Order)
- Contract: Lookup (Contract)
- Financial Commitment: Lookup (Financial Commitment)
- Financial Funding Source: Lookup (Financial Funding Source)
- Invoice Number: Text
- Invoice Date: Date
- Invoice Amount: Currency
- Payment Approved By: Lookup (Person)
- Payment Approval Date: Date
- Reference Number: Text
- Check Number: Text
- Transaction ID: Text
- Fiscal Year: Text
- Payment Period: Text
- Description: Memo
- Notes: Memo

---

## Choiced Fields

**Completed:**

**Completed Last Round:**

### Financial Funding Source Type
- Appropriation
- Grant
- Contract Revenue
- Fee Revenue
- Cost Center
- Project Funding
- Capital Fund
- Operating Fund
- Reserve Fund

### Financial Classification Type
- Expense Category
- Revenue Category
- Object Class
- Cost Element
- Account Code
- Program Code
- Function Code

### Procurement Method
- Competitive Bid
- Request for Proposal
- Request for Quote
- Sole Source
- Emergency Procurement
- Blanket Purchase Agreement
- Simplified Acquisition
- GSA Schedule
- Cooperative Agreement

### Procurement Item Type
- Goods
- Services
- Software
- Equipment
- Supplies
- Professional Services
- Construction

### Procurement Type
- Request for Proposal (RFP)
- Request for Quote (RFQ)
- Invitation for Bid (IFB)
- Sole Source
- Small Purchase
- Emergency

### Contract Type
- Fixed Price
- Cost Reimbursable
- Time and Materials
- Indefinite Delivery Indefinite Quantity (IDIQ)
- Blanket Purchase Agreement (BPA)
- Task Order
- Delivery Order

### Contract Pricing Structure
- Firm Fixed Price
- Fixed Price with Economic Adjustment
- Cost Plus Fixed Fee
- Cost Plus Award Fee
- Cost Plus Incentive Fee
- Time and Materials
- Labor Hour

### Contract Amendment Type
- Funding Increase
- Funding Decrease
- Period Extension
- Scope Change
- Administrative Correction
- Termination
- Option Exercise

### Contract Line Type
- Fixed Price Item
- Labor Category
- Material
- Travel
- Other Direct Cost
- Subcontract

### Contract Deliverable Type
- Report
- Software
- Data Set
- Training Material
- Documentation
- Presentation
- Physical Product
- Service Completion

### Contract Milestone Type
- Contract Award
- Kickoff
- Phase Start
- Phase Completion
- Deliverable Due
- Renewal Decision
- Option Exercise
- Contract Closeout

### Financial Commitment Type
- Purchase Order
- Contract Obligation
- Grant Award
- Reserved Funds
- Encumbrance

### Purchase Order Type
- Standard
- Blanket
- Standing
- Emergency
- Contract Release

**Planned:**

### Purchase Order Line Stage
- Open
- Partially Received
- Fully Received
- Invoiced
- Closed
- Cancelled

### Budget Stage
Tracks budget through preparation, approval, execution, and closeout.
- Draft
- Submitted
- Under Review
- Approved
- Active
- Amended
- Closed

### Purchase Request Stage
Tracks internal requisition from creation through sourcing and ordering.
- Draft
- Submitted
- Under Review
- Approved
- Sourcing
- Ordered
- Closed

### Procurement Package Stage
Tracks solicitation and award process for competitive procurement.
- Planning
- Solicitation Issued
- Responses Due
- Under Evaluation
- Awarded
- Closed

### Contract Stage
Tracks contract from negotiation through execution and closeout.
- Draft
- Under Negotiation
- Pending Approval
- Approved
- Active
- Close Out
- Closed

### Contract Amendment Stage
Tracks contract modifications from drafting through execution.
- Draft
- Submitted
- Under Review
- Approved
- Executed

### Contract Deliverable Stage
Tracks deliverable submission and acceptance workflow.
- Not Started
- In Progress
- Submitted
- Under Review
- Accepted

### Financial Commitment Stage
Tracks funds reservation through certification and expenditure.
- Draft
- Pending Certification
- Certified
- Active
- Fully Expended
- Closed

### Purchase Order Stage
Tracks purchase order from creation through fulfillment.
- Draft
- Pending Approval
- Approved
- Issued
- Receiving
- Closed

### Payment Stage
Tracks payment processing from initiation through disbursement.
- Draft
- Pending Approval
- Approved
- Scheduled
- Processed

**Removed (Replaced with Stage Fields):**

### Budget Status → Budget Stage
Budget Status tracked workflow progression. Replaced with Budget Stage. Decision outcomes (Approved/Rejected) now tracked via Item Decision Status.

### Request Status → Purchase Request Stage  
Request Status merged into Approval Status in Core, but for Purchase Requests we use Purchase Request Stage for workflow + Item Decision Status for approval outcomes.

### Procurement Status → Procurement Package Stage
Procurement Status already tracked workflow steps. Renamed to Procurement Package Stage for consistency.

### Agreement Status → Contract Stage
For Contracts specifically, Agreement Status values tracked workflow. Replaced with Contract Stage. Note: Core Agreement Status remains for general agreements.

### Financial Commitment Status → Financial Commitment Stage + Validation Status
Financial Commitment Status mixed workflow (Draft, Pending Certification, Active) with state (Partially/Fully Expended). Replaced with Stage for workflow and Validation Status for certification tracking. Expenditure amounts tracked in currency fields.

### Purchase Order Status → Purchase Order Stage
Purchase Order Status tracked workflow and receiving state. Replaced with Purchase Order Stage. Receiving quantities tracked in Purchase Order Line fields.

### Contract Deliverable Status → Contract Deliverable Stage + Acceptance Status
Contract Deliverable Status mixed workflow (In Progress, Submitted) with outcomes (Accepted, Rejected). Separated into Stage for workflow and Item Acceptance Status for acceptance decisions.

**Deferred:**

