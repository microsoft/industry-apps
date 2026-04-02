Review the existing table definitions and propose Stage choice values only.

**Note:** Stage fields track **workflow progression**. Status fields track **semantic state and outcomes**. See [choice-status-fields.md](choice-status-fields.md) for Status field guidelines. Together, Stage and Status provide complete state management.

Stage rules:
- Stage choice fields are required on transactional records only, reference tables do not require them
- Stage describes where the record is in its domain workflow
- Stage must represent workflow steps, not outcomes or semantic state
- Use values that are intuitive to users and ordered in a natural progression
- Keep the set concise, domain-specific, and reusable

Do not use Stage for:
- Approved, Rejected, Cancelled, Deferred
- Blocked
- Completed as an outcome
- Validated or Failed
- Duplicate, Superseded, Withdrawn

Method:
1. Infer the operational workflow for the record
2. Identify the major process steps from creation to closure
3. Propose 5 to 10 clear Stage values
4. Briefly describe each value
5. End with:

<Table Name> Stage
- Value 1
- Value 2
- Value 3

6. Add Stage field to table's Planned section: Insert `- Stage: Choice (<Table Name> Stage)` early in field list, before workflow-related dates
7. Add any Status fields after Stage (see choice-status-fields.md for canonical Item Status fields)
8. Add Stage choice definition to Planned / Candidates section at the bottom of BUILD.md

