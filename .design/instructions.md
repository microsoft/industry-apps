# 🎯 Data Model Design Instructions

When designing a data model:

1. Do not recreate Core tables (from Core.md)
2. Reuse existing choice fields where logically appropriate (from Core.md).
3. Only introduce new tables if they represent new domain concepts.
4. Suggest generic naming that works in both Public Sector and Commercial contexts.
5. Focus on business process, domain modeling, and data relationships — not Power Platform implementation details.
6. Identify relationships back to Core explicitly.
7. Keep the model reusable and composable with other modules.

# Field Design Rules

When designing fields:

1. Place fields after each table definition in the appropriate markdown file. Include friendly name and type only. For example: - My Field: Text
2. For field types, use Text, Memo, Integer, Float, Currency, Date, Date Time, Yes / No, Lookup, or Choice.
3. Date fields - End the field name with "Date" or "Date Time" depending if only a date or if tracking the time is important.

