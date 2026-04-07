# Event Management Changelog

## Unreleased

## [1.1.0.0] - 2026-04-07

### Added
- **Event Management Module**: 10 entities with 127+ fields supporting complete event lifecycle from planning through execution
  - Core entities: Event, Event Type, Event Track
  - Planning: Event Request (planned for future implementation)
  - Participation: Event Participant, Event Session Participant
  - Schedule: Event Session
  - Content: Event Entry (presentations, posters, submissions)
  - Support: Event Sponsor
- **Choice Sets**: 6 global option sets including participant types, session roles, session types, sponsorship levels, and sponsorship types
- **Baseline Forms and Views**: Initial configuration for 8 implemented entities

### Changed
- **Status Field Refactoring**: Replaced Event Status with Event Stage workflow pattern for improved lifecycle tracking

### Removed
- Legacy choice field: Event Status — replaced with Event Stage

---
