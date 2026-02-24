# 🏗️ Asset Management — Data Model Design

---

## Core Asset Records

### Asset
Individual, accountable item instance. Stores identifying details, current status/condition, links to Product, Asset Type, ownership, assignment, and lifecycle records.

**Completed:**
- Name: Text
- Asset Number: Text
- Serial Number: Text
- Asset Type: Lookup (Asset Type)
- Asset Category: Lookup (Asset Category)
- Related Product: Lookup (Product)
- Description: Memo
- Asset Status: Choice (Asset Status)
- Condition: Choice (Asset Condition)
- Acquired Date Time: Date Time
- In Service Date: Date
- Expected Useful Life (Years): Integer
- Parent Asset: Lookup (Asset)
- RF Tag: Text 
- Estimated Value: Currency
- Depreciation Method: Choice (Asset Depreciation Method)
- Barcode: Text
- Current Location: Lookup (Location)
- Current Assignment: Lookup (Asset Assignment)
- Current Owner: Lookup (Asset Owner)
- Notes: Memo
- Is Disposable: Yes / No
- Requires Inspection: Yes / No

**Planned:**

---

### Asset Type
Operational classification of assets (e.g., Laptop, Vehicle, Generator). Used for reporting, inspection requirements, and grouping.

**Completed:**
- Name: Text
- Asset Category: Lookup (Asset Category)
- Description: Memo
- Default Useful Life (Years): Integer
- Requires Tracking: Yes / No
- Requires Inspection: Yes / No

**Planned:**

---

### Asset Category
Higher-level grouping of Asset Types (e.g., IT Equipment, Fleet, Facilities Equipment). Useful for roll-up reporting and policy alignment.

**Completed:**
- Name: Text
- Parent Asset Category: Lookup (Asset Category)
- Description: Memo
- Capitalization Threshold: Currency

**Planned:**

---

## Acquisition & Financial Tracking

### Asset Acquisition
Represents the acquisition event for one or more assets (purchase, lease, donation, transfer-in). Captures supplier, acquisition type, funding, and financial context.

**Completed:**
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

**Planned:**

---

### Asset Cost Entry
Additional capital or operational costs associated with an asset (repairs, upgrades, improvements, reconditioning, etc.) for total cost tracking.

**Completed:**
- Name: Text
- Asset: Lookup (Asset)
- Cost Type: Choice (Asset Cost Type)
- Cost Date: Date
- Amount: Currency
- Vendor: Lookup (Account)
- Invoice Number: Text
- Description: Memo
- Notes: Memo
- Capitalizable: Yes / No

**Planned:**

---

## Ownership, Assignment & Custody

### Asset Owner
Tracks legal or financial ownership of the asset over time (e.g., owned, leased, externally owned). Supports ownership history with effective dates.

**Completed:**
- Name: Text
- Asset: Lookup (Asset)
- Ownership Type: Choice (Asset Ownership Type)
- Owner Account: Lookup (Account)
- Owner Organization Unit: Lookup (Organization Unit)
- Effective Start Date: Date
- Effective End Date: Date
- Notes: Memo
- Is Current: Yes / No

**Planned:**

---

### Asset Assignment
Tracks custody or responsibility for the asset over time (assigned to a person, organization unit, or team). Includes start and end dates.

**Completed:**
- Name: Text ok
- Asset: Lookup (Asset) ok
- Assigned To Person: Lookup (Person) ok
- Assigned To Organization Unit: Lookup (Organization Unit) ok
- Assignment Date: Date ok
- Expected Return Date: Date ok
- Actual Return Date: Date ok
- Assignment Purpose: Memo ok
- Assignment Status: Choice (Assignment Status)
- Notes: Memo
- Is Current: Yes / No

**Planned:**

---

### Asset Custody Event
Timeline-based record of significant custody or control changes (assign, return, move, transfer, retire, dispose). Provides an auditable history of asset movement and responsibility.

**Completed:**
- Name: Text
- Asset: Lookup (Asset)
- Event Type: Choice (Asset Custody Event Type)
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

**Planned:**

---

## Service & Operational History

### Asset Service Record
Lightweight maintenance/service log entry for an asset. Captures service date, service type, provider, cost, and notes.

**Completed:**
- Name: Text
- Asset: Lookup (Asset)
- Service Type: Lookup (Asset Service Type)
- Service Date: Date
- Service Provider: Lookup (Account)
- Service Provider Contact: Lookup (Person)
- Service Cost: Currency
- Meter Reading: Integer
- Service Status: Choice (Asset Status)
- Next Service Due Date: Date
- Description: Memo
- Notes: Memo

**Planned:**

---

### Asset Service Type
Reference list defining types of service events (Preventive, Repair, Inspection, Upgrade, Calibration, etc.).

**Completed:**
- Name: Text
- Description: Memo

**Planned:**

---

## Audit & Compliance

### Asset Audit
Represents an audit cycle or inventory verification event (e.g., Annual Inventory Count). Defines scope, dates, and status.

**Completed:**
- Name: Text
- Audit Type: Choice (Asset Audit Type)
- Audit Start Date: Date
- Audit End Date: Date
- Schedule Status: Choice (Schedule Status)
- Auditor: Lookup (Person)
- Scope Organization Unit: Lookup (Organization Unit)
- Scope Location: Lookup (Location)
- Total Assets Expected: Integer
- Total Assets Verified: Integer
- Total Discrepancies: Integer
- Description: Memo
- Notes: Memo

**Planned:**

---

### Asset Audit Item
Asset-level audit result within an Asset Audit. Records expected vs observed data, verification status, and findings.

**Completed:**
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
- Discrepancy Type: Choice (Asset Discrepancy Type)
- Finding: Memo
- Resolution: Memo
- Resolution Date: Date

**Planned:**

---

### Asset Inspection Requirement
Defines recurring inspection rules that apply to an Asset Type or specific Asset. Includes frequency and regulatory reference.

**Completed:**
- Name: Text
- Asset Type: Lookup (Asset Type)
- Specific Asset: Lookup (Asset)
- Inspection Frequency: Choice (Schedule Frequency)
- Inspection Frequency (Days): Integer
- Regulatory Authority: Lookup (Legal Authority)
- Compliance Framework: Lookup (Compliance Framework)
- Description: Memo

**Planned:**

---

## Retirement & Disposition

### Asset Disposition
Captures retirement and disposal details for an asset, including retirement reason, disposal method, dates, approvals, and recipient (if applicable).

**Completed:**
- Name: Text
- Asset: Lookup (Asset)
- Disposition Type: Choice (Asset Disposition Type)
- Disposition Reason: Choice (Asset Disposition Reason)
- Disposition Date: Date
- Approved By: Lookup (Person)
- Approval Date: Date
- Recipient Account: Lookup (Account)
- Recipient Person: Lookup (Person)
- Sale Price: Currency
- Disposal Cost: Currency
- Certificate of Destruction: Text
- Description: Memo
- Notes: Memo
- Environmental Compliance Verified: Yes / No
- Data Sanitization Verified: Yes / No

**Planned:**

---

## Choice Fields

**Completed:**

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

### Asset Depreciation Method
- Straight Line
- Declining Balance
- Units of Production
- Sum of Years Digits
- Not Depreciated

### Asset Acquisition Type
- Purchase
- Lease
- Donation
- Transfer In
- Fabricated
- Found Property

### Asset Cost Type
- Repair
- Upgrade
- Improvement
- Maintenance
- Recondition
- Installation
- Decommission

### Asset Ownership Type
- Owned
- Leased
- Rented
- Borrowed
- On Loan
- Consignment

### Asset Custody Event Type
- Assigned
- Returned
- Transferred
- Moved
- Lost
- Found
- Retired
- Disposed

### Schedule Status
- Scheduled
- In Progress
- Completed
- Cancelled
- On Hold
- Overdue

### Asset Audit Type
- Scheduled Inventory
- Spot Check
- Random Sample
- Annual Audit
- Regulatory Audit
- Investigation

### Audit Status - Use Schedule Statue
- Planned
- In Progress
- Completed
- On Hold
- Cancelled

### Asset Discrepancy Type
- Missing
- Wrong Location
- Wrong Assignee
- Wrong Condition
- Unrecorded Asset
- Duplicate Entry

### Asset Disposition Type
- Sale
- Donation
- Transfer Out
- Trash
- Recycle
- Destruction
- Return to Vendor
- Salvage

### Asset Disposition Reason
- End of Life
- Obsolete
- Damaged Beyond Repair
- Cost to Maintain Excessive
- Surplus
- Replaced
- Policy Requirement
- Lost or Stolen

**Planned:**


