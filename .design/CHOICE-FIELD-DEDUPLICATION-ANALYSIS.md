# Core Choice Field Deduplication Analysis

## 🔍 Analysis Summary

**Total Choice Components:** 61  
**Potential Consolidation Opportunities:** 8 groups identified

---

## ⚠️ HIGH-PRIORITY CONSOLIDATION CANDIDATES

### 1. **Method of Contact vs. Method of Receipt** 
**Overlap:** ~70% identical values

**Method of Contact:**
- Phone, Email, In Person, Mail, Web Form, Portal, Social Media

**Method of Receipt:**
- Web Portal, Phone, Email, In Person, Fax, Mail, Social Media

**Analysis:** These represent nearly the same concept (communication channel). Main differences:
- Method of Contact has "Web Form" and "Portal" (separate)
- Method of Receipt has "Fax" and "Web Portal" 
- Method of Receipt has "Automatic" and "Bulk Import"

**RECOMMENDATION: MERGE → "Communication Method" or keep "Method of Receipt" (more complete)**
- Add "Fax" to Method of Contact if keeping separate
- OR consolidate into one choice set with all values
- Suggested consolidated values: Web Portal, Phone, Email, In Person, Fax, Mail, Social Media, Web Form, Automatic, Bulk Import

---

### 2. **Severity Level vs. Priority**
**Overlap:** Conceptual - both are importance/impact ratings

**Severity Level:**
- Critical, High, Moderate, Low, Minimal (5 levels)

**Priority:**
- Critical, High, Medium, Low (4 levels)

**Analysis:** 
- Both serve similar purpose but have slightly different scales
- Severity = impact/seriousness of something that exists
- Priority = urgency/importance for action/attention
- These are semantically different concepts often used together

**RECOMMENDATION: KEEP SEPARATE**
- Severity Level: describes how bad something is (incident, risk, finding)
- Priority: describes how urgent addressing it is
- Use case: A "High Severity" issue might have "Low Priority" if it's not time-sensitive

---

### 3. **High Medium Low vs. Severity Level vs. Priority**
**Overlap:** All are rating scales

**High Medium Low:**
- High, Medium, Low (3 levels)

**Analysis:**
- Generic 3-point scale
- Severity Level is more specific (5 levels)
- Priority is more specific (4 levels)

**RECOMMENDATION: KEEP "High Medium Low" as generic option**
- Use for simple ratings where specific semantics aren't needed
- Use Severity Level for severity-specific contexts
- Use Priority for priority-specific contexts
- Example use: Risk likelihood, Effort level, Confidence level

---

### 4. **Overall Result vs. Objective Result vs. Finding Result**
**Overlap:** All measure outcomes/results

**Overall Result:**
- Successful, Partially Successful, Unsuccessful, Inconclusive

**Objective Result:**
- Met, Partially Met, Not Met, Exceeded

**Finding Result:**
- Substantiated, Partially Substantiated, Unsubstantiated, Inconclusive, No Finding, Unable to Determine

**Analysis:**
- Overall Result: Binary success/failure assessment
- Objective Result: Goal achievement assessment
- Finding Result: Investigation/audit conclusion (very specific)

**RECOMMENDATION: KEEP ALL THREE - Different semantic contexts**
- Overall Result: general activity/event outcome
- Objective Result: specific to goal/objective achievement
- Finding Result: specific to investigative/audit conclusions
- Not interchangeable due to different semantics

---

### 5. **Lifecycle Stage vs. Operational Status**
**Overlap:** Both track entity state through time

**Lifecycle Stage:**
- Planning, Initiation, Active, On Hold, Complete, Cancelled, Archived

**Operational Status:**
- Draft, Pending, Active, Inactive, Suspended, Closed

**Analysis:**
- Lifecycle Stage: Project/initiative phases (start to finish journey)
- Operational Status: Current operational state (on/off/paused)
- Some overlap (Active, Cancelled/Closed)

**RECOMMENDATION: KEEP SEPARATE - Different purposes**
- Lifecycle Stage: for projects, initiatives, programs (sequential phases)
- Operational Status: for ongoing operations, services, resources (state-based)
- Use together: A project in "Active" lifecycle stage might have "Inactive" operational status temporarily

---

## ⚙️ MEDIUM-PRIORITY REVIEW OPPORTUNITIES

### 6. **Similar Status Fields with Different Contexts**

Multiple status fields exist for different domains. These are BY DESIGN and should remain separate:

**Work/Task Status:**
- **Action Status**: focuses on task workflow (New, In Progress, Submitted for Review, etc.)
- **Schedule Status**: focuses on scheduled activities (Scheduled, In Progress, Completed, Overdue)
- **Milestone Status**: focuses on milestones (Upcoming, Current, Completed, Acknowledged)

**Assessment Status:**
- **Issue Status**: simple issue lifecycle (Open, Under Review, Resolved, Closed)
- **Finding Status**: assessment findings (Draft, Under Review, Finalized, Appealed, Upheld, Overturned)
- **Recommendation Status**: recommendation lifecycle (Proposed, Under Review, Accepted, Rejected, Modified, Implemented, Closed)

**Document/Content Status:**
- **Publication Status**: publishing workflow (Draft, In Review, Approved, Published, Archived, Withdrawn)
- **Plan Status**: planning documents (Draft, Under Review, Approved, Active, Revised, Completed)

**Agreement/Commitment Status:**
- **Agreement Status**: contract lifecycle (Draft, Under Negotiation, Pending Approval, Active, Expired, Terminated, Renewed)
- **Commitment Status**: obligation tracking (Planned, Committed, In Progress, Fulfilled, Partially Fulfilled, Unfulfilled, Cancelled)

**Specialized Status:**
- **Request Status**: application/request processing
- **Referral Status**: referral tracking
- **Interview Status**: interview scheduling
- **Assignment Status**: asset/resource assignment
- **Payment Status**: financial transactions
- **Verification Status**: verification activities
- **Participation Status**: party engagement
- **Compliance Status**: compliance assessment
- **Eligibility Status**: eligibility determination
- **Legal Authority Status**: legal document lifecycle
- **Period Status**: fiscal period states

**RECOMMENDATION: KEEP ALL - Domain-specific semantics matter**
- Each serves a specific business context
- Values are optimized for their domain
- Consolidating would lose semantic meaning and business clarity

---

### 7. **Impact vs. Legal Authority Impact**
**Overlap:** Both measure impact levels

**Impact:**
- Direct, Indirect, Minimal, None, Unknown

**Legal Authority Impact:**
- Major, Moderate, Minor, Technical, Clarification

**Analysis:**
- Impact: describes nature/scope of impact (qualitative type)
- Legal Authority Impact: describes magnitude of legal change (quantitative scale)
- Different purposes, different value sets

**RECOMMENDATION: KEEP SEPARATE**
- Impact: general impact classification (cause-effect relationship)
- Legal Authority Impact: specific to legal/regulatory changes
- Could use Impact more broadly, but Legal Authority Impact has domain-specific values

---

### 8. **Direction vs. Polarity**
**Overlap:** Both indicate positive/negative direction

**Direction:**
- Increase, Decrease, No Change

**Polarity:**
- Positive, Neutral, Negative

**Analysis:**
- Direction: quantitative change direction (more/less)
- Polarity: qualitative valence (good/bad/neutral)
- Different semantic purposes

**RECOMMENDATION: KEEP SEPARATE**
- Direction: for metrics, quantities, trends (objective)
- Polarity: for sentiment, assessment, evaluation (subjective)
- Example: Revenue "Increase" (direction) with "Negative" polarity (due to fraud)

---

## ✅ FINAL RECOMMENDATIONS

### Consolidate (1 opportunity):
1. **Method of Contact + Method of Receipt** → **Communication Method** or enhance "Method of Receipt"
   - Merge values: Web Portal, Phone, Email, In Person, Fax, Mail, Social Media, Web Form, Automatic, Bulk Import

### Keep Separate (all others):
- All status fields are domain-specific by design
- Rating scales serve different semantic purposes (Severity vs Priority vs High/Medium/Low)
- Result fields have different contexts (Overall, Objective, Finding)
- Impact types serve different purposes
- Direction vs Polarity are conceptually different

### Action Items:
1. **MERGE**: Method of Contact + Method of Receipt → single "Communication Method" choice field
   - Update all table references in BUILD.md
   - Create consolidated XML file
   - Deprecate one of the two fields
   
2. **DOCUMENT**: Add usage guidance to BUILD.md for:
   - When to use Severity Level vs Priority vs High Medium Low
   - When to use Overall Result vs Objective Result vs Finding Result
   - When to use Lifecycle Stage vs Operational Status

---

## 📊 Revised Count After Consolidation

| Before | After | Change |
|--------|-------|--------|
| 61 choice fields | 60 choice fields | -1 (merged methods) |

**Estimated Consolidation Impact:**
- 1 choice field eliminated
- ~10-20 table field references to update across modules
- Clearer semantic separation for remaining fields
