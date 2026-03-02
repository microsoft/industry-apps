# Personnel Security Choice Field Analysis

## 📊 Analysis Summary

**Total Choice Fields in Personnel Security:** 36  
**Already Exist in Core:** 1  
**Recommend Adding to Core:** 7  
**Keep in Personnel Security:** 28  

---

## ✅ ALREADY EXISTS IN CORE (1 field)

### 1. **Eligibility Status** → USE CORE
**Personnel Security Values:** Active, Expired, Suspended, Revoked, Denied, Pending Renewal, Inactive, Terminated

**Core Values:** Eligible, Ineligible, Conditionally Eligible, Under Review, Pending Verification

**Analysis:** Different semantic purposes!
- **Core Eligibility Status** = determination of eligibility (Yes/No/Conditional)
- **Personnel Security Eligibility Status** = ongoing status of granted eligibility (Active/Expired/Revoked)

**RECOMMENDATION: KEEP SEPARATE**
- Rename Personnel Security version to **"Security Eligibility Status"** or **"Clearance Status"**
- These serve different purposes in the workflow
- Core version = eligibility determination
- PS version = clearance/credential lifecycle status

**REVISED: Actually NOT A MATCH - Keep separate with better naming**

---

## 🌟 RECOMMEND ADDING TO CORE (7 fields)

### 1. **Credential Status** → ADD TO CORE
**Current Values:** Active, Expired, Suspended, Revoked, Lost, Stolen, Damaged, Returned, Replaced

**Rationale:** Generic credential/certificate lifecycle management useful across many modules  
**Potential Uses:** 
- Training certifications (certification status)
- Professional licenses (license status)
- Equipment credentials (equipment status)
- System access credentials (access status)
- Permits and authorizations
- Healthcare credentials
- Professional registrations

**Recommended Generic Name:** "Credential Status"

---

### 2. **Credential Category** → ADD TO CORE
**Current Values:** Permanent, Temporary, Contractor, Visitor, Emergency, Limited Access

**Rationale:** Generic classification for any credential, certificate, or authorization  
**Potential Uses:**
- Training certificates (permanent vs. temporary certifications)
- Employment classifications 
- Access authorizations
- Parking permits
- Facility access
- System access categories

**Recommended Generic Name:** "Credential Category"

---

### 3. **Event Status** → ADD TO CORE
**Current Values:** Reported, Under Review, Reviewed, No Action Required, Action Taken, Closed

**Rationale:** Generic event tracking lifecycle applicable to any reportable event, incident, or occurrence  
**Potential Uses:**
- Safety incidents
- Security incidents
- Quality events
- Compliance events
- Audit observations
- Complaints
- Service requests
- Hotline reports

**Recommended Generic Name:** "Event Status"

---

### 4. **Resolution Status** → ADD TO CORE
**Current Values:** Pending, Under Investigation, Resolved, No Action Required, Mitigated, Unresolved

**Rationale:** Generic resolution tracking for issues, findings, complaints, incidents  
**Potential Uses:**
- Issue resolution
- Complaint resolution
- Audit finding resolution
- Risk mitigation tracking
- Action item completion
- Customer service cases
- IT tickets

**Note:** Similar to "Issue Status" (Open, Under Review, Resolved, Closed) but with more nuanced states
**Recommended Generic Name:** "Resolution Status"

---

### 5. **Quality Review Status** → ADD TO CORE
**Current Values:** Passed, Passed with Notes, Failed, Pending Correction, Re Investigation Required

**Rationale:** Generic quality assurance review outcome applicable to any review/inspection process  
**Potential Uses:**
- Quality inspections
- Document reviews
- Compliance reviews
- Audit reviews
- Background investigations
- Procurement reviews
- Grant application reviews
- Building inspections

**Recommended Generic Name:** "Quality Review Status"

---

### 6. **Appeal Decision** → ADD TO CORE
**Current Values:** Appeal Granted, Appeal Denied, Appeal Partially Granted, Remanded for Review, Withdrawn

**Rationale:** Generic appeal process outcome useful across any contestable decision process  
**Potential Uses:**
- HR appeals (termination, discipline)
- Benefits appeals
- Permit appeals
- Licensing appeals
- Procurement protests
- Grade appeals (education)
- Parking violation appeals
- Zoning appeals
- Any administrative review process

**Recommended Generic Name:** "Appeal Decision"

---

### 7. **Biometric Type** → ADD TO CORE
**Current Values:** Fingerprint, Facial Recognition, Iris Scan, Hand Geometry, Voice Recognition, Multiple Biometrics

**Rationale:** Generic biometric classification useful for any system using biometric authentication  
**Potential Uses:**
- Physical access control
- Time and attendance
- Building security
- System authentication
- Border control
- Healthcare patient identification
- Law enforcement
- Visitor management

**Recommended Generic Name:** "Biometric Type"

---

## 🔐 KEEP IN PERSONNEL SECURITY MODULE (28 fields)

These are specific to personnel security, clearance, and vetting workflows:

### Security Review & Investigation Process (9 fields)
1. **Security Review Type** - Specific security review types (Initial, Reinvestigation, Upgrade, etc.)
2. **Security Review Status** - Security review workflow states
3. **Security Review Reason** - Reasons for security reviews
4. **Security Review Outcome** - Security adjudication outcomes
5. **Investigation Type** - Background investigation types (National Agency Check, etc.)
6. **Investigation Tier** - Tier 1-5 classification system
7. **Investigation Status** - Investigation workflow (similar to Core but security-specific)
8. **Investigation Scope** - Investigation scope levels
9. **Investigation Provider Type** - Government Agency, Contract Provider, etc.

**Why Keep Separate:** These are specific to government/defense security clearance processes with specific terminology, regulations, and workflows

---

### Adjudication & Decision (2 fields)
10. **Adjudication Status** - Adjudication workflow states
11. **Adjudication Type** - Types of security adjudications
12. **Adjudication Decision** - Security clearance decisions

**Why Keep Separate:** Specific to formal security adjudication processes per federal guidelines (e.g., SEAD-4)

---

### Eligibility & Clearance (2 fields - after renaming)
13. **Security Eligibility Status** (rename from Eligibility Status) - Clearance lifecycle status
14. **Eligibility Type** - Security Clearance, Position of Trust, Special Access, etc.
15. **Eligibility Category** - Confidential, Secret, Top Secret classifications

**Why Keep Separate:** Specific to security clearance levels and access authorization types

---

### Continuous Evaluation (4 fields)
16. **Continuous Evaluation Status** - CE program enrollment status
17. **Continuous Evaluation Type** - Types of ongoing monitoring
18. **Enrollment Reason** - Why enrolled in CE
19. **Evaluation Frequency** - How often evaluations occur
20. **Automated Check Frequency** - Frequency of automated checks

**Why Keep Separate:** Specific to continuous evaluation/vetting programs (NBIB Trusted Workforce)

---

### Reportable Events (8 fields)
21. **Reportable Event Type** - Foreign Travel, Foreign Contact, Legal Incident, etc.
22. **Reportable Event Category** - Foreign Influence, Criminal Conduct, etc.
23. **Foreign Contact Type** - Types of foreign contacts
24. **Financial Issue Type** - Types of financial concerns
25. **Legal Incident Type** - Types of legal issues
26. **Adverse Action Type** - Employment-related adverse actions
27. **Security Concern Level** - Low, Moderate, High, Critical concern levels
28. **Eligibility Action** - Actions taken on eligibility (Suspension, Revocation, etc.)

**Why Keep Separate:** Specific to security clearance adjudicative guidelines and reportable incident tracking per SF-86, SEAD-3, and federal vetting requirements

---

### Access Credentials (1 field - after moving 2 to Core)
29. **Access Credential Type** - Badge, Smart Card, Proximity Card, etc.

**Why Keep Separate:** While credential status/category go to Core, the specific types are security/access control focused

**Note:** Could potentially be generalized, but the values are specific to physical/logical security access systems

---

### Impact Assessment (1 field)
30. **Impact Level** - No Impact, Minor, Moderate, Significant, Critical Impact

**Analysis:** Similar to Core "Impact" and "Severity Level" but with different scale
- Core "Impact" = Direct, Indirect, Minimal, None, Unknown (nature of impact)
- Core "Severity Level" = Critical, High, Moderate, Low, Minimal (severity)
- PS "Impact Level" = Five-level impact scale

**Recommendation:** Could potentially use **Core "Severity Level"** instead, or keep as domain-specific if the five-level scale is important for personnel security risk assessment

---

## 📋 SUMMARY TABLE

| Category | Count | Action |
|----------|-------|--------|
| **Already in Core** | 0 | N/A (Eligibility Status is different) |
| **Add to Core** | 7 | Move to Core module for reusability |
| **Rename in PS Module** | 1 | Rename "Eligibility Status" to avoid confusion |
| **Keep in PS Module** | 28 | Domain-specific to personnel security |
| **Review for Consolidation** | 1 | Consider using Core Severity Level for Impact Level |
| **Total Choice Fields** | 36 | |

---

## 🎯 RECOMMENDED ACTIONS

### Phase 1: Core Enhancement
Add these 7 generic choice fields to Core:
1. Credential Status
2. Credential Category  
3. Event Status
4. Resolution Status
5. Quality Review Status
6. Appeal Decision
7. Biometric Type

### Phase 2: Personnel Security Cleanup
1. **Rename** "Eligibility Status" to "Security Eligibility Status" or "Clearance Status" to avoid confusion with Core's Eligibility Status
2. **Consider** using Core "Severity Level" instead of custom "Impact Level" (or keep if five-level scale is required)
3. Keep all 28 domain-specific fields

### Phase 3: Implementation
1. Update Core BUILD.md with 7 new planned choice fields
2. Create XML files for new Core choice components
3. Update Personnel Security BUILD.md to:
   - Reference Core choice fields where applicable
   - Rename Eligibility Status to Security Eligibility Status
   - Document 28 module-specific fields

---

## ⚠️ SPECIAL CONSIDERATIONS

### Eligibility Status Naming Conflict
**Core has:** Eligibility Status (determination: Eligible/Ineligible/Conditional)  
**PS needs:** Clearance lifecycle status (Active/Expired/Revoked/Suspended)

**Solution:** Rename PS version to "Security Eligibility Status" or "Clearance Status" to clearly differentiate:
- Core: "Eligibility Status" = determination outcome
- PS: "Security Eligibility Status" = ongoing clearance status

### Investigation Status
Both Core (from Investigations module) and Personnel Security have "Investigation Status" but they may have different values and contexts:
- **Investigations module:** Focus on investigative case management
- **Personnel Security:** Focus on background investigation for clearances

**Recommendation:** Keep separate with "Personnel" or "Background" prefix if needed, or ensure values align if truly the same concept

### Impact Level vs Severity Level
Consider whether PS really needs a separate five-level "Impact Level" or if Core's "Severity Level" (Critical, High, Moderate, Low, Minimal) would suffice. If the scale is mandated by regulation (e.g., NIST 800-53), keep it separate.
