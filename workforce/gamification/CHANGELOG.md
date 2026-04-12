# Gamification Changelog

## Unreleased

## [1.2.0.0] - 2026-04-11

### Added
- Forms: Configured quick create forms for all Gamification entities including streamlined field layouts for rapid data entry
- Subgrids: Configured related subgrids for all applicable Gamification entities to enable comprehensive related record navigation and management

---

## [1.1.0.0] - 2026-04-07

### Added
- **Gamification Module**: 6 entities with 99+ fields supporting behavioral reinforcement through games, activities, and achievements
  - Game Definition: Game, Game Activity, Game Achievement
  - Participation & Tracking: Game Participant, Game Participant Activity, Game Participant Achievement
- **Choice Sets**: 11 global option sets including game types, participation models, activity types, achievement types, award criteria types, participant types, recognition status, and workflow stages
- **Baseline Forms and Views**: Initial configuration for all 6 entities

### Changed
- **Status Field Refactoring**: Replaced 5 legacy status-specific choice fields with standardized Stage workflow patterns and Core reusable statuses (Item Validation Status, Item Decision Status, Item Disposition)

### Removed
- Legacy choice fields: Gamification Game Status, Gamification Participation Status, Gamification Activity Record Status, Gamification Verification Status, Gamification Achievement Record Status — replaced with Stage and Core status fields

---
