# 🏗️ Asset Management — Data Model Design

---

## Core Asset Records

### Asset
Individual, accountable item instance. Stores identifying details, current status/condition, links to Product, Asset Type, ownership, assignment, and lifecycle records.

**Fields:**
- Name: Text
- Asset Tag: Text
- Serial Number: Text
- Asset Type: Lookup (Asset Type)
- Asset Category: Lookup (Asset Category)
- Product: Lookup (Product)
- Description: Memo
- Asset Status: Choice (Asset Status)
- Condition: Choice (Asset Condition)
- Acquisition Date: Date
- In Service Date: Date
- Expected Useful Life (Years): Integer
- Estimated Value: Currency
- Depreciation Method: Choice (Depreciation Method)
- Barcode: Text
- RFID Tag: Text
- Is Disposable: Yes / No
- Requires Inspection: Yes / No
- Current Location: Lookup (Location)
- Current Assignment: Lookup (Asset Assignment)
- Current Owner: Lookup (Asset Owner)
- Notes: Memo

---

### Asset Type
Operational classification of assets (e.g., Laptop, Vehicle, Generator). Used for reporting, inspection requirements, and grouping.

**Fields:**
- Name: Text
- Asset Category: Lookup (Asset Category)
- Description: Memo
- Default Useful Life (Years): Integer
- Requires Tracking: Yes / No
- Requires Inspection: Yes / No
- Is Active: Yes / No

---

### Asset Category
Higher-level grouping of Asset Types (e.g., IT Equipment, Fleet, Facilities Equipment). Useful for roll-up reporting and policy alignment.

**Fields:**
- Name: Text
- Description: Memo
- Capitalization Threshold: Currency
- Is Active: Yes / No

---

## Acquisition & Financial Tracking

### Asset Acquisition
Represents the acquisition event for one or more assets (purchase, lease, donation, transfer-in). Captures supplier, acquisition type, funding, and financial context.

**Fields:**
- Name: Text
- Acquisition Type: Choice (Acquisition Type)
- Acquisition Date: Date
- Supplier: Lookup (Account)
- Purchase Order Number: Text
- Total Cost: Currency
- Funding Source: Text
- Payment Status: Choice (Payment Status)
- Received Date: Date
- Received By: Lookup (Person)
- Invoice Number: Text
- Invoice Date: Date
- Warranty Expiration Date: Date
- Notes: Memo

---

### Asset Cost Entry
Additional capital or operational costs associated with an asset (repairs, upgrades, improvements, reconditioning, etc.) for total cost tracking.

**Fields:**
- Name: Text
- Asset: Lookup (Asset)
- Cost Type: Choice (Asset Cost Type)
- Cost Date: Date
- Amount: Currency
- Vendor: Lookup (Account)
- Invoice Number: Text
- Description: Memo
- Capitalizable: Yes / No
- Notes: Memo

---

## Ownership, Assignment & Custody

### Asset Owner
Tracks legal or financial ownership of the asset over time (e.g., owned, leased, externally owned). Supports ownership history with effective dates.

**Fields:**
- Name: Text
- Asset: Lookup (Asset)
- Ownership Type: Choice (Ownership Type)
- Owner Account: Lookup (Account)
- Owner Organization Unit: Lookup (Organization Unit)
- Effective Start Date: Date
- Effective End Date: Date
- Is Current: Yes / No
- Notes: Memo

---

### Asset Assignment
Tracks custody or responsibility for the asset over time (assigned to a person, organization unit, or team). Includes start and end dates.

**Fields:**
- Name: Text
- Asset: Lookup (Asset)
- Assigned To Person: Lookup (Person)
- Assigned To Organization Unit: Lookup (Organization Unit)
- Assignment Date: Date
- Expected Return Date: Date
- Actual Return Date: Date
- Assignment Status: Choice (Assignment Status)
- Assignment Purpose: Memo
- Is Current: Yes / No
- Notes: Memo

---

### Asset Custody Event
Timeline-based record of significant custody or control changes (assign, return, move, transfer, retire, dispose). Provides an auditable history of asset movement and responsibility.

**Fields:**
- Name: Text
- Asset: Lookup (Asset)
- Event Type: Choice (Custody Event Type)
- Event Date Time: Date Time
- From Person: Lookup (Person)
- To Person: Lookup (Person)
- From Organization Unit: Lookup (Organization Unit)
- To Organization Unit: Lookup (Organization Unit)
- From Location: Lookup (Location)
- To Location: Lookup (Location)
- Recorded By: Lookup (Person)
- Verification Method: Text
- Notes: Memo

---

## Service & Operational History

### Asset Service Record
Lightweight maintenance/service log entry for an asset. Captures service date, service type, provider, cost, and notes.

**Fields:**
- Name: Text
- Asset: Lookup (Asset)
- Service Type: Lookup (Asset Service Type)
- Service Date: Date
- Service Provider: Lookup (Account)
- Service Provider Contact: Lookup (Person)
- Service Cost: Currency
- Meter Reading: Integer
- Service Status: Choice (Service Status)
- Next Service Due Date: Date
- Description: Memo
- Notes: Memo

---

### Asset Service Type
Reference list defining types of service events (Preventive, Repair, Inspection, Upgrade, Calibration, etc.).

**Fields:**
- Name: Text
- Description: Memo
- Is Active: Yes / No

---

## Audit & Compliance

### Asset Audit
Represents an audit cycle or inventory verification event (e.g., Annual Inventory Count). Defines scope, dates, and status.

**Fields:**
- Name: Text
- Audit Type: Choice (Audit Type)
- Audit Start Date: Date
- Audit End Date: Date
- Audit Status: Choice (Audit Status)
- Auditor: Lookup (Person)
- Scope Organization Unit: Lookup (Organization Unit)
- Scope Location: Lookup (Location)
- Total Assets Expected: Integer
- Total Assets Verified: Integer
- Total Discrepancies: Integer
- Description: Memo
- Notes: Memo

---

### Asset Audit Item
Asset-level audit result within an Asset Audit. Records expected vs observed data, verification status, and findings.

**Fields:**
- Name: Text
- Asset Audit: Lookup (Asset Audit)
- Asset: Lookup (Asset)
- Expected Location: Lookup (Location)
- Observed Location: Lookup (Location)
- Expected Assignee: Lookup (Person)
- Observed Assignee: Lookup (Person)
- Expected Condition: Choice (Asset Condition)
- Observed Condition: Choice (Asset Condition)
- Verification Status: Choice (Verification Status)
- Verification Date Time: Date Time
- Verified By: Lookup (Person)
- Discrepancy Type: Choice (Discrepancy Type)
- Finding: Memo
- Resolution: Memo
- Resolution Date: Date

---

### Asset Inspection Requirement
Defines recurring inspection rules that apply to an Asset Type or specific Asset. Includes frequency and regulatory reference.

**Fields:**
- Name: Text
- Asset Type: Lookup (Asset Type)
- Specific Asset: Lookup (Asset)
- Inspection Frequency (Days): Integer
- Regulatory Authority: Lookup (Legal Authority)
- Compliance Framework: Lookup (Compliance Framework)
- Is Active: Yes / No
- Description: Memo

---

## Retirement & Disposition

### Asset Disposition
Captures retirement and disposal details for an asset, including retirement reason, disposal method, dates, approvals, and recipient (if applicable).

**Fields:**
- Name: Text
- Asset: Lookup (Asset)
- Disposition Type: Choice (Disposition Type)
- Disposition Reason: Choice (Disposition Reason)
- Disposition Date: Date
- Approved By: Lookup (Person)
- Approval Date: Date
- Recipient Account: Lookup (Account)
- Recipient Person: Lookup (Person)
- Sale Price: Currency
- Disposal Cost: Currency
- Certificate of Destruction: Text
- Environmental Compliance Verified: Yes / No
- Data Sanitization Verified: Yes / No
- Description: Memo
- Notes: Memo

---

## New Choice Fields

### Asset Status
- Available
- In Use
- In Storage
- In Maintenance
- In Transit
- Reserved
- Retired
- Disposed
- Lost
- Stolen

### Asset Condition
- Excellent
- Good
- Fair
- Poor
- Non-Functional
- Needs Repair
- Under Evaluation

### Depreciation Method
- Straight Line
- Declining Balance
- Units of Production
- Sum of Years Digits
- Not Depreciated

### Acquisition Type
- Purchase
- Lease
- Donation
- Transfer In
- Fabricated
- Found Property

### Payment Status
- Pending
- Partial
- Paid
- Disputed
- Refunded

### Asset Cost Type
- Repair
- Upgrade
- Improvement
- Maintenance
- Recondition
- Installation
- Decommission

### Ownership Type
- Owned
- Leased
- Rented
- Borrowed
- On Loan
- Consignment

### Assignment Status
- Active
- Pending Return
- Returned
- Overdue
- Cancelled

### Custody Event Type
- Assigned
- Returned
- Transferred
- Moved
- Lost
- Found
- Retired
- Disposed

### Service Status
- Scheduled
- In Progress
- Completed
- Cancelled
- Overdue

### Audit Type
- Scheduled Inventory
- Spot Check
- Random Sample
- Annual Audit
- Regulatory Audit
- Investigation

### Audit Status
- Planned
- In Progress
- Completed
- On Hold
- Cancelled

### Verification Status
- Verified
- Not Found
- Discrepancy Found
- Pending Investigation
- Resolved

### Discrepancy Type
- Missing
- Wrong Location
- Wrong Assignee
- Wrong Condition
- Unrecorded Asset
- Duplicate Entry

### Disposition Type
- Sale
- Donation
- Transfer Out
- Trash
- Recycle
- Destruction
- Return to Vendor
- Salvage

### Disposition Reason
- End of Life
- Obsolete
- Damaged Beyond Repair
- Cost to Maintain Excessive
- Surplus
- Replaced
- Policy Requirement
- Lost or Stolen

