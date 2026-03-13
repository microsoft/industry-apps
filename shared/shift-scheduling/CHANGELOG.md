# Changelog

All notable changes to the Shift Scheduling module will be documented in this file.

## Unreleased

### Added

#### Schedule Management
- **Shift Location**: Container for schedules created for specific operational contexts (retail outlets, clinical units, facilities). Links to Organization Unit and Physical Location, managed by Shift Worker. Tracks schedule type, date range, and status.
- **Shift Schedule**: Specific time blocks within a schedule requiring staffing coverage (day/night shifts, operational windows). Links to Shift Location and Template, tracks shift type and status.

#### Staffing Requirements & Assignments
- **Shift Staffing Requirement**: Defines personnel quantities and roles needed for shifts. Links to Shift Location, Scheduled Shift, and Required Role. Tracks quantity, priority, and fulfillment status.
- **Shift Assignment**: Individual worker assignments to fulfill staffing requirements. Links Shift Worker or Participant to Scheduled Shift and Staffing Requirement. Tracks assigned role, time window, assignment status, and attendance.
- **Shift Team Assignment**: Team-based scheduling for group assignments. Links teams to shifts and staffing requirements. Tracks time window, assignment status, and attendance.

#### Worker Pool
- **Shift Worker**: Person available for shift scheduling. Supports standalone records, optional links to Contact (for data reuse) and User (for system access). Enables scheduling of internal employees, contractors, volunteers, and external workers. Includes contact info, employee/badge ID, and active status.

#### Participants & Availability  
- **Shift Participant**: Roster entry representing worker availability within specific schedules or system-wide. Links to Shift Worker with optional Shift Location for roster-based or general pool availability. Tracks default role and date range.
- **Shift Availability**: Flexible availability/unavailability tracking with all lookups optional. Supports patterns: general ongoing availability, specific date ranges, location-specific, or shift-specific. Tracks availability type (Available, Unavailable, Preferred, Leave, etc.) and reason.

#### Configuration & Templates
- **Shift Role**: Standardized role definitions for staffing requirements (nurse, cashier, inspector, security officer). Links to Core Competency. Includes role code and active status.
- **Shift Template**: Reusable shift definitions for common coverage patterns. Defines shift type, default start/end times, and duration for quick schedule generation.
- **Shift Rotation Pattern**: Recurring shift rotation cycles for rotating crews, alternating shifts, and on-call coverage. Defines rotation type, cycle length, and frequency.

#### Choice Components (Global Option Sets)

**Module-Specific (4):**
- **Shift Schedule Type**: Fixed Schedule, Rotating Schedule, On-Call Schedule, Flexible Schedule, Seasonal Schedule
- **Shift Type**: Day Shift, Evening Shift, Night Shift, Split Shift, On-Call, Standby, Weekend, Holiday
- **Shift Availability Type**: Available, Unavailable, Preferred, Restricted, Leave, Training, Temporary Assignment
- **Shift Rotation Type**: Fixed Rotation, Rolling Rotation, Bidirectional Rotation

**Reused from Core (8):**
- Scheduled Event Status (Shift Location, Shift Schedule)
- Priority (Shift Staffing Requirement)
- Item Completion Status (Shift Staffing Requirement, Shift Participant, Shift Availability)
- Item Assignment Status (Shift Assignment, Shift Team Assignment)
- Attendance Status (Shift Assignment, Shift Team Assignment)
- Schedule Frequency (Shift Rotation Pattern)
- Organization Unit (via lookup)
- Location (via lookup)

#### Architectural Features
- Flexible worker linking: Shift Worker supports standalone records, optional Contact linking (data reuse), and optional User linking (system access)
- Multi-pattern availability: Shift Availability with all optional lookups enables general, date-specific, location-specific, and shift-specific availability tracking
- Dual assignment model: Individual assignments (Shift Assignment) and team assignments (Shift Team Assignment) for comprehensive scheduling
- Template-driven scheduling: Shift Templates for standardized shift creation
- Location-based organization: Shift Location as parent container for schedules, requirements, and assignments

### Changed

