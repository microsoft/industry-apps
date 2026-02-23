# 🎮 Gamification — Data Model Design

The **Gamification** module provides a structured way to encourage, track, and recognize desired behaviors across programs, teams, and initiatives. It allows organizations to define Games (time-bound or ongoing initiatives), configure Activities that represent measurable actions, and establish Achievements that participants can earn based on participation or performance. Participants (individuals or teams) generate Activity records through their actions, and when criteria are met, Achievement records are granted and tracked. This module can be used to reinforce training completion, safety compliance, case resolution timeliness, volunteer engagement, productivity milestones, wellness initiatives, community participation, or internal innovation efforts—making it a flexible behavioral reinforcement layer that can operate alongside workforce, compliance, training, service delivery, or operational modules across public or commercial environments.

---

## Game Definition

### Game
Represents a structured gamification initiative or campaign. A Game defines the scope, timeframe, participation model, and overall purpose of the engagement effort (e.g., training challenge, performance drive, volunteer campaign).

**Completed:**

**Planned:**
- Name: Text
- Game Code: Text
- Game Type: Choice (Game Type)
- Description: Memo
- Objectives: Memo
- Game Status: Choice (Game Status)
- Visibility: Choice (Visibility)
- Start Date: Date
- End Date: Date
- Is Ongoing: Yes / No
- Participation Model: Choice (Participation Model)
- Open Enrollment: Yes / No
- Requires Approval: Yes / No
- Owner Organization Unit: Lookup (Organization Unit)
- Game Administrator: Lookup (Person)
- Organization Initiative: Lookup (Organization Initiative)
- Total Participants: Integer
- Active Participants: Integer
- Total Activities Logged: Integer
- Total Achievements Earned: Integer
- Scoring Enabled: Yes / No
- Leaderboard Enabled: Yes / No
- Team Based: Yes / No
- Logo URL: Text
- Banner URL: Text
- Rules: Memo
- Notes: Memo

---

### Game Activity
Defines the types of actions that are tracked within a Game. Activities represent measurable behaviors such as completing training, closing a case, attending an event, or submitting a task. These are definitional and not transactional.

**Completed:**

**Planned:**
- Name: Text
- Game: Lookup (Game)
- Parent Game Activity: Lookup (Game Activity)
- Activity Code: Text
- Activity Type: Choice (Activity Type)
- Description: Memo
- Activity Status: Choice (Operational Status)
- Points Value: Integer
- Can Repeat: Yes / No
- Maximum Occurrences: Integer
- Requires Verification: Yes / No
- Auto Award: Yes / No
- Verification Criteria: Memo
- Icon URL: Text

---

### Game Achievement
Defines the achievements that can be earned within a Game. These may represent badges, levels, milestones, point thresholds, or titles. This table stores the criteria and configuration for what participants can earn.

**Completed:**

**Planned:**
- Name: Text
- Game: Lookup (Game)
- Parent Game Achievement: Lookup (Game Achievement)
- Achievement Code: Text
- Achievement Type: Choice (Achievement Type)
- Description: Memo
- Achievement Status: Choice (Operational Status)
- Points Required: Integer
- Criteria: Memo
- Required Activities: Memo
- Prerequisite Achievements: Memo
- Award Criteria Type: Choice (Award Criteria Type)
- Can Be Revoked: Yes / No
- Is Public: Yes / No
- Tier Level: Integer
- Badge URL: Text
- Certificate Template: Lookup (Content Template)
- Reward Value: Currency
- Reward Description: Memo
- Total Earned: Integer
- Notes: Memo

---

## Participation & Tracking

### Game Participant
Represents an individual or team enrolled in a specific Game. This table tracks participation status, enrollment, and contextual role within the Game (participant, admin, etc.), separate from the core person or team record.

**Completed:**

**Planned:**
- Name: Text
- Game: Lookup (Game)
- Person: Lookup (Person)
- Participant Organization Unit: Lookup (Organization Unit)
- Team Name: Text
- Participant Type: Choice (Participant Type)
- Participation Status: Choice (Participation Status)
- Enrollment Date: Date
- Start Date: Date
- Completion Date: Date
- Last Activity Date: Date
- Total Points: Integer
- Total Activities Logged: Integer
- Total Achievements Earned: Integer
- Leaderboard Rank: Integer
- Percent Complete: Integer
- Opted In: Yes / No
- Notifications Enabled: Yes / No
- Is Team Lead: Yes / No
- Eligibility Status: Choice (Eligibility Status)
- Notes: Memo

---

### Game Participant Activity
Logs instances of Participants performing defined Game Activities. This table captures the behavioral history used to evaluate achievement criteria and calculate performance metrics.

**Completed:**

**Planned:**
- Name: Text
- Game Participant: Lookup (Game Participant)
- Game: Lookup (Game)
- Game Activity: Lookup (Game Activity)
- Person: Lookup (Person)
- Activity Date Time: Date Time
- Activity Status: Choice (Activity Record Status)
- Points Earned: Integer
- Verification Status: Choice (Verification Status)
- Verified By: Lookup (Person)
- Verification Date: Date
- Verification Notes: Memo
- Source Record Type: Text
- Source Record ID: Text
- Location: Lookup (Location)
- Duration (Minutes): Integer
- Quantity: Float
- Description: Memo
- Evidence URL: Text
- Supporting Document: Lookup (Document)
- Auto Recorded: Yes / No
- Notes: Memo

---

### Game Participant Achievement
Records when a Participant earns a specific Game Achievement. This is the transactional recognition record, including when it was granted, its status, and any related activity or approval.

**Completed:**

**Planned:**
- Name: Text
- Game Participant: Lookup (Game Participant)
- Game: Lookup (Game)
- Game Achievement: Lookup (Game Achievement)
- Person: Lookup (Person)
- Achievement Status: Choice (Achievement Record Status)
- Earned Date: Date
- Awarded Date: Date
- Awarded By: Lookup (Person)
- Revoked Date: Date
- Revoked By: Lookup (Person)
- Revoke Reason: Memo
- Points Earned: Integer
- Recognition Status: Choice (Recognition Status)
- Certificate Issued: Yes / No
- Certificate Issued Date: Date
- Certificate Document: Lookup (Document)
- Reward Delivered: Yes / No
- Reward Delivery Date: Date
- Approval Required: Yes / No
- Approval Status: Choice (Approval Status)
- Approved By: Lookup (Person)
- Approval Date: Date
- Is Visible: Yes / No
- Display on Profile: Yes / No
- Achievement Notes: Memo
- Notes: Memo

---

## New Choice Fields

### Game Type
- Training Challenge
- Performance Drive
- Compliance Campaign
- Wellness Initiative
- Safety Program
- Volunteer Campaign
- Innovation Challenge
- Service Excellence
- Onboarding Program
- Community Engagement

### Game Status
- Planning
- Open for Enrollment
- Active
- Paused
- Completed
- Archived
- Cancelled

### Participation Model
- Individual
- Team
- Department
- Organization Wide
- Invitation Only
- Tiered

### Activity Type
- Training Completion
- Task Completion
- Event Attendance
- Case Resolution
- Time Logged
- Certification Earned
- Feedback Submitted
- Survey Completion
- Mentor Session
- Safety Report
- Innovation Submission
- Volunteer Hours

### Achievement Type
- Badge
- Level
- Tier
- Milestone
- Certificate
- Title
- Rank
- Recognition
- Reward

### Award Criteria Type
- Points Threshold
- Activity Count
- Activity Streak
- Time Based
- Performance Based
- Combination

### Participant Type
- Individual Participant
- Team Member
- Team Lead
- Game Administrator
- Observer

### Participation Status
- Invited
- Enrolled
- Active
- Inactive
- Completed
- Withdrawn
- Disqualified

### Activity Record Status
- Pending
- Verified
- Rejected
- Expired
- Voided

### Verification Status
- Not Required
- Pending Verification
- Verified
- Rejected
- Needs Information

### Achievement Record Status
- Earned
- Awarded
- Pending Approval
- Revoked
- Expired

### Recognition Status
- Not Recognized
- Pending
- Recognized
- Public
- Private
