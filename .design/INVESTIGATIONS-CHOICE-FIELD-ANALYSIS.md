# Investigations Choice Field Analysis

## ✅ REUSE FROM CORE (9 fields)

These fields already exist in Core and should be referenced directly:

| Field Name | Status | Notes |
|------------|--------|-------|
| **Priority** | ✅ Use Core | Low, Medium, High, Critical |
| **Severity Level** | ✅ Use Core | Critical, High, Moderate, Low, Minimal |
| **Security Classification** | ✅ Use Core | Unclassified, Sensitive, Confidential, Secret, Top Secret |
| **Visibility** | ✅ Use Core | Public, Internal, Restricted, Confidential |
| **Method of Receipt** | ✅ Use Core | Web Portal, Phone, Email, In Person, Fax, Mail, Social Media |
| **Approval Status** | ✅ Use Core | Pending, Approved, Rejected, Cancelled, Returned, Recalled |
| **Action Status** | ✅ Use Core | New, In Progress, Submitted for Review, Review In Progress, Returned, Complete, Cancelled, Deferred |
| **Publication Status** | ✅ Use Core | Draft, In Review, Approved, Published, Archived, Withdrawn |
| **High Medium Low** | ✅ Use Core | High, Medium, Low (used for Potential Evidentiary Value) |

---

## 🌟 RECOMMEND ADDING TO CORE (12 fields)

These are generic enough to be useful across multiple modules:

### 1. **Party Type** → ADD TO CORE
**Current Values:** Individual, Organization, Department, External Entity  
**Rationale:** Many modules need to distinguish between individual and organizational participants (events, contracts, grants, legal matters, external engagement, training, etc.)  
**Potential Uses:** Event participants, contract parties, grant applicants, legal case parties, service recipients

### 2. **Participation Status** → ADD TO CORE
**Current Values:** Identified, Contacted, Cooperative, Uncooperative, Unavailable, Declined to Participate  
**Rationale:** Generic workflow for tracking engagement with any party across events, meetings, trainings, surveys, etc.  
**Potential Uses:** Event attendance, training enrollment, meeting participation, survey responses, committee membership

### 3. **Plan Status** → ADD TO CORE
**Current Values:** Draft, Under Review, Approved, Active, Revised, Completed  
**Rationale:** Generic planning lifecycle applicable to strategic plans, project plans, operational plans, training plans, etc.  
**Potential Uses:** Project plans, strategic plans, training plans, emergency response plans, budget plans

### 4. **Issue Status** → ADD TO CORE
**Current Values:** Open, Under Review, Resolved, Closed  
**Rationale:** Simple issue tracking lifecycle useful for help desk, quality issues, risks, audit observations, etc.  
**Potential Uses:** IT tickets, quality control issues, audit observations, safety concerns, citizen complaints

### 5. **Finding Status** → ADD TO CORE
**Current Values:** Draft, Under Review, Finalized, Appealed, Upheld, Overturned  
**Rationale:** Generic for any assessment process - audits, inspections, reviews, evaluations  
**Potential Uses:** Audit findings, inspection results, compliance assessments, quality reviews, performance evaluations

### 6. **Finding Result** → ADD TO CORE
**Current Values:** Substantiated, Partially Substantiated, Unsubstantiated, Inconclusive, No Finding, Unable to Determine  
**Rationale:** Generic assessment outcome useful across audits, investigations, inspections, compliance reviews  
**Potential Uses:** Audit conclusions, inspection results, allegation determinations, complaint resolutions

### 7. **Recommendation Status** → ADD TO CORE
**Current Values:** Proposed, Under Review, Accepted, Rejected, Modified, Implemented, Closed  
**Rationale:** Generic recommendation lifecycle for audits, reviews, strategic planning, process improvement  
**Potential Uses:** Audit recommendations, inspection recommendations, strategic initiatives, process improvements, policy proposals

### 8. **Report Type** → ADD TO CORE
**Current Values:** Investigation Report, Interim Report, Summary Report, Statistical Report, Public Report  
**Rationale:** Generic report categorization (though specific values may vary by module)  
**Suggested Generic Values:** Final Report, Interim Report, Summary Report, Statistical Report, Public Report, Internal Report, Executive Report  
**Potential Uses:** Audit reports, financial reports, performance reports, program reports

### 9. **Report Status** → ADD TO CORE
**Current Values:** Draft, Under Review, Final, Published, Archived  
**Rationale:** Generic report lifecycle across all reporting activities  
**Potential Uses:** Audit reports, financial reports, performance reports, compliance reports, program reports

### 10. **Referral Direction** → ADD TO CORE
**Current Values:** Outgoing, Incoming  
**Rationale:** Simple, generic concept applicable anywhere referrals are tracked  
**Potential Uses:** Service referrals, legal referrals, healthcare referrals, program referrals, client referrals

### 11. **Access Type** → ADD TO CORE
**Current Values:** View, Download, Copy, Analysis, Administrative  
**Rationale:** Generic access tracking for documents, systems, facilities, data  
**Potential Uses:** Document access, system access, facility access, data access, records management

### 12. **Storage Type** → ADD TO CORE
**Current Values:** Physical Locker, Evidence Vault, Secure Repository, Cloud Storage, External Archive, Sealed Container  
**Rationale:** Generic storage categorization useful for assets, records, inventory, equipment  
**Suggested Generic Values:** Physical Storage, Secure Vault, Digital Repository, Cloud Storage, External Archive, On-Site, Off-Site  
**Potential Uses:** Asset storage, records management, inventory management, equipment storage, document management

### 13. **Case Relationship Type** → ADD TO CORE
**Current Values:** Duplicate, Related, Predecessor, Successor, Parallel Investigation, Systemic Issue, Similar Pattern  
**Rationale:** Generic relationship tracking useful for any case management (legal, projects, incidents, complaints)  
**Suggested Generic Values:** Duplicate, Related, Predecessor, Successor, Parallel, Systemic Issue, Similar Pattern  
**Potential Uses:** Legal case relationships, project dependencies, incident tracking, complaint management, audit linkages

### 14. **Interview Status** → ADD TO CORE
**Current Values:** Scheduled, Conducted, Cancelled, Rescheduled, Declined  
**Rationale:** Generic interview/meeting lifecycle applicable to HR, investigations, research, media relations  
**Potential Uses:** HR interviews, candidate interviews, research interviews, witness statements, stakeholder meetings

### 15. **Referral Status** → ADD TO CORE
**Current Values:** Pending, Submitted, Acknowledged, Under Review, Completed, Declined  
**Rationale:** Generic referral tracking workflow for any inter-agency or inter-department referrals  
**Potential Uses:** Service referrals, legal referrals, healthcare referrals, program referrals, client referrals, case transfers

**Note:** Report Status was consolidated into Publication Status (already in Core).

---

## 🔍 KEEP IN INVESTIGATIONS MODULE (24 fields)

These are specific to investigation workflows and should remain module-specific:

### Investigation Core Workflow
- **Investigation Status** - 11 investigation-specific states
- **Intake Status** - Intake-specific workflow
- **Screening Status** - Screening-specific process
- **Intake Disposition** - Investigation intake decisions

### Investigation Content
- **Allegation Type** - Investigation-specific (Fraud, Theft, Misconduct, etc.)
- **Allegation Status** - Allegation lifecycle specific to investigations
- **Issue Type** - Investigation analysis framework (Policy Compliance, Control Effectiveness, etc.)

### Location & Parties
- **Investigation Location Type** - Investigation-specific location purposes
- **Interview Participant Role** - Interview-specific roles

### Evidence Management (5 fields)
- **Evidence Status** - Evidence lifecycle
- **Evidence Category** - Documentary, Physical, Digital, Testimonial, Demonstrative
- **Evidence Link Type** - Evidence-to-case relationship types
- **Custody Event Type** - Chain of custody events
- **Interview Type** - Investigation interview types

### Findings & Actions (5 fields)
- **Finding Type** - Investigation-specific finding categories
- **Recommendation Type** - Investigation-specific recommendations (Disciplinary, Process Improvement, etc.)
- **Corrective Action Type** - Investigation-specific corrective actions
- **Outcome Type** - Investigation closure types
- **Overall Disposition** - Investigation final determination

### Recovery & Financial (3 fields)
- **Recovery Type** - Financial recovery categories
- **Recovery Status** - Recovery collection workflow
- **Recovery Method** - Recovery collection methods

### External Coordination (1 field)
- **Referral Category** - Investigation-specific referral targets (Law Enforcement, Regulatory Agency, IG, etc.)

---

## 📋 SUMMARY

| Category | Count | Action |
|----------|-------|--------|
| **Reuse from Core** | 9 | Reference existing core choice fields |
| **Add to Core** | 14 | Move to core module for reusability |
| **Keep in Investigations** | 23 | Create as investigation-specific fields |
| **Total Choice Fields** | 46 | |

**Note:** Count updated after consolidating Report Status into Publication Status and moving Case Relationship Type, Interview Status, and Referral Status to Core.

---

## 🎯 RECOMMENDED ACTIONS

### Phase 1: Immediate Updates
1. Update Investigation BUILD.md to reference the 9 existing Core choice fields
2. Document the 12 candidates for Core addition

### Phase 2: Core Enhancement
1. Add the 12 recommended generic choice fields to Core
2. Update Core BUILD.md documentation
3. Create the Core choice component XML files
4. Deploy Core updates to Dataverse

### Phase 3: Investigation Implementation
1. Create the 27 investigation-specific choice fields
2. Reference Core choice fields where applicable
3. Build Investigation solution with proper dependencies

---

## ⚠️ CONSIDERATIONS

### Generic vs. Specific Values
Some fields like **Report Type** and **Storage Type** have investigation-specific values that should be generalized when moving to Core:
- Report Type: Remove "Investigation Report", keep generic types
- Storage Type: Generalize from "Evidence Vault" to "Secure Vault"

### Dependencies
When fields move to Core, Investigation module will need to:
- Reference Core solution as a dependency
- Import Core choice fields during development
- Maintain consistency with Core definitions

### Future Reusability
Fields marked for Core will be available for:
- Audit & Compliance modules
- HR misconduct/grievance tracking
- Quality assurance
- Risk management
- Customer service & complaints
- Any module tracking findings, recommendations, or referrals
