# Core Choice Fields Analysis - New Additions from Personnel Security

## Analysis Date
February 28, 2026

## Newly Added Choice Fields (Planned Section)

The following 7 choice fields were added to Core from the Personnel Security module:

1. **Credential Status** - Active, Expired, Suspended, Revoked, Lost, Stolen, Damaged, Returned, Replaced
2. **Credential Category** - Permanent, Temporary, Contractor, Visitor, Emergency, Limited Access
3. **Event Status** - Reported, Under Review, Reviewed, No Action Required, Action Taken, Closed
4. **Resolution Status** - Pending, Under Investigation, Resolved, No Action Required, Mitigated, Unresolved
5. **Quality Review Status** - Passed, Passed with Notes, Failed, Pending Correction, Re Investigation Required
6. **Appeal Decision** - Appeal Granted, Appeal Denied, Appeal Partially Granted, Remanded for Review, Withdrawn
7. **Biometric Type** - Fingerprint, Facial Recognition, Iris Scan, Hand Geometry, Voice Recognition, Multiple Biometrics

---

## Comparison with Existing Core Choice Fields

### 1. Credential Status
**Comparison with Similar Fields:**
- **Simple Certification Status** (Certified, Not Certified, Pending, Expired, Revoked)
  - **Overlap**: Both include "Expired" and "Revoked"
  - **Distinction**: Credential Status includes physical state tracking (Lost, Stolen, Damaged, Returned, Replaced) which Certification Status lacks
  - **Recommendation**: ⚠️ **Consider consolidation** - These could be merged into a single comprehensive "Credential/Certification Status" field

**Analysis**: Credential Status is broader and more comprehensive. Simple Certification Status appears to be a simplified subset focused only on certification validity, while Credential Status handles both validity AND physical state management.

**Consolidation Opportunity**: HIGH

---

### 2. Credential Category
**Comparison with Similar Fields:**
- **Position Designation** (Career, Temporary, Term, Intern, Fellow, Appointed) - Different domain (HR positions vs credentials)
- **Employment Type** (Full Time, Part Time, Temporary, Seasonal, Contractor, Volunteer) - Different domain

**Analysis**: No overlap. This is unique to credential classification.

**Consolidation Opportunity**: NONE

---

### 3. Event Status
**Comparison with Similar Fields:**
- **Operational Status** (Draft, Pending, Active, Inactive, Suspended, Closed)
  - **Overlap**: Both include "Closed"
  - **Distinction**: Event Status is workflow-oriented (Reported → Under Review → Reviewed → Action), while Operational Status is state-oriented (lifecycle states)
  
- **Request Status** (Submitted, Under Review, Pending Information, Approved, Rejected, Withdrawn, Completed)
  - **Overlap**: Both include "Under Review" and both track workflow progression
  - **Distinction**: Request Status is approval-focused (approve/reject), Event Status is action-focused (review/action taken)

- **Issue Status** (Open, Under Review, Resolved, Closed)
  - **Overlap**: "Under Review" and general workflow concept
  - **Distinction**: Event Status adds granularity with "Reviewed", "No Action Required", "Action Taken"

**Analysis**: Event Status serves a distinct purpose for incident/event reporting workflows. While it shares some conceptual overlap with Request Status and Issue Status, the semantic focus is different.

**Consolidation Opportunity**: LOW - Different semantic purposes

---

### 4. Resolution Status
**Comparison with Similar Fields:**
- **Issue Status** (Open, Under Review, Resolved, Closed)
  - **Overlap**: ⚠️ **SIGNIFICANT** - Both include "Resolved" and both track investigation/resolution workflows
  - **Distinction**: Resolution Status is more granular (Pending, Under Investigation, Resolved, No Action Required, Mitigated, Unresolved) compared to Issue Status (Open, Under Review, Resolved, Closed)
  - **Recommendation**: ⚠️ **Strong consolidation candidate**

**Analysis**: These two fields serve nearly identical purposes. Resolution Status appears to be a more comprehensive version of Issue Status. Issue Status could potentially be deprecated in favor of Resolution Status.

**Mapping Proposal**:
- Issue Status "Open" → Resolution Status "Pending"
- Issue Status "Under Review" → Resolution Status "Under Investigation"
- Issue Status "Resolved" → Resolution Status "Resolved"
- Issue Status "Closed" → Resolution Status "Resolved" or "No Action Required"

**Consolidation Opportunity**: HIGH

---

### 5. Quality Review Status
**Comparison with Similar Fields:**
- **Verification Status** (Verified, Not Found, Discrepancy Found, Pending Investigation, Resolved)
  - **Overlap**: Both relate to review/verification processes
  - **Distinction**: Quality Review Status focuses on pass/fail assessments with correction workflow; Verification Status focuses on data validation/investigation

- **Overall Result** (Successful, Partially Successful, Unsuccessful, Inconclusive)
  - **Overlap**: Both express outcomes
  - **Distinction**: Quality Review Status includes workflow states (Pending Correction, Re Investigation Required); Overall Result is purely outcome-focused

**Analysis**: Quality Review Status serves a specific QA/inspection purpose that existing fields don't fully address.

**Consolidation Opportunity**: NONE

---

### 6. Appeal Decision
**Comparison with Similar Fields:**
- **Finding Status** (Draft, Under Review, Finalized, Appealed, Upheld, Overturned)
  - **Overlap**: Finding Status includes "Appealed", "Upheld", "Overturned" which relate to appeal outcomes
  - **Distinction**: Appeal Decision captures the specific decision outcome, while Finding Status tracks the overall finding lifecycle

**Analysis**: Appeal Decision is complementary to Finding Status. Finding Status tracks that something was "Appealed", while Appeal Decision captures what the appeal decision was. These serve different purposes.

**Consolidation Opportunity**: NONE - Complementary fields

---

### 7. Biometric Type
**Comparison with Similar Fields:**
- No similar fields exist in Core

**Analysis**: Domain-specific enumeration of biometric methods. No overlap.

**Consolidation Opportunity**: NONE

---

## Summary of Recommendations

### High Priority Consolidations

#### 1. ⚠️ **Issue Status vs Resolution Status**
**Current State**:
- Issue Status: Open, Under Review, Resolved, Closed
- Resolution Status: Pending, Under Investigation, Resolved, No Action Required, Mitigated, Unresolved

**Recommendation**: Consolidate into **Resolution Status** (the more comprehensive option)

**Impact**: 
- Issue Status is used in 1 existing location (added in "Completed Last Round" section)
- Would need to update any references to Issue Status

**Proposed Mapping**:
```
Issue Status → Resolution Status
-----------------------------------
Open → Pending
Under Review → Under Investigation
Resolved → Resolved
Closed → Resolved (or No Action Required depending on context)
```

#### 2. ⚠️ **Simple Certification Status vs Credential Status**
**Current State**:
- Simple Certification Status: Certified, Not Certified, Pending, Expired, Revoked
- Credential Status: Active, Expired, Suspended, Revoked, Lost, Stolen, Damaged, Returned, Replaced

**Recommendation**: Options:
- **Option A**: Consolidate into **Credential Status** and add "Certified/Not Certified" values
- **Option B**: Keep separate - Certification Status for simple cert tracking, Credential Status for physical credential management
- **Option C**: Rename to clarify - "Certification Validity Status" vs "Physical Credential Status"

**Impact**:
- Simple Certification Status appears to be an existing completed field
- Need to understand current usage before consolidating

**Analysis**: These serve related but potentially distinct purposes:
- Simple Certification Status = Digital/logical state (is someone certified?)
- Credential Status = Physical/comprehensive state (what's the state of their badge/card?)

---

## Recommended Actions

### Immediate Actions
1. **Consolidate Issue Status into Resolution Status**
   - Remove Issue Status from "Completed Last Round" section
   - Update Core BUILD.md to show Resolution Status in appropriate section
   - Search for any table fields using "Issue Status" and update to "Resolution Status"
   - Update Personnel Security and Investigations modules if they reference Issue Status

### Recommended for Review
2. **Review Simple Certification Status vs Credential Status usage**
   - Determine if these serve distinct use cases or should be consolidated
   - If consolidating, decide on comprehensive option set
   - If keeping separate, consider renaming for clarity

### No Action Required
3. **Keep as-is**: Credential Category, Event Status, Quality Review Status, Appeal Decision, Biometric Type
   - These fields serve unique purposes with no significant overlap

---

## Additional Notes

**Event Status Consideration**: While Event Status shares some workflow concepts with Request Status and Issue Status, the semantic purpose is distinct (event/incident reporting vs requests vs issues). Recommend keeping separate unless a truly generic "Workflow Status" field is desired (which may be too abstract to be useful).

**Finding Status and Appeal Decision**: These are complementary - Finding Status tracks lifecycle including appeals, Appeal Decision captures specific appeal outcomes. Both are needed.
