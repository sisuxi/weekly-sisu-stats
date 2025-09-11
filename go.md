# Principal Engineer Weekly Snapshot Report Generator

Generate comprehensive weekly snapshot reports documenting strategic technical leadership, architectural decisions, and cross-team impact.

## Purpose
Generate concise, data-focused weekly activity snapshots with links to sources. Reports provide factual summaries of work completed across GitHub, Slack, Gmail, Drive, Calendar, Linear, and LaunchDarkly.

## Quick Start

### Step 1: Collect Raw Data
```bash
# Collect last week's data (Sunday-Saturday)
python3 collect_raw_data.py

# Or specify custom dates
python3 collect_raw_data.py --start 2025-08-24 --end 2025-08-30

# Or specify a week containing a specific date
python3 collect_raw_data.py --date 2025-08-27
```

This will:
- Calculate the date range (default: previous Sunday-Saturday)
- Create a folder named `YYYYMMDD-YYYYMMDD`
- Collect all raw data in parallel
- Save as `raw_*.json` files

### Step 2: Generate Report
After data collection, run this prompt with Claude Code to generate the final report.

## Report Generation Process (Claude Code)

When you run `@go.md` after data collection, Claude will:

1. **Check for existing data folder**
   - Look for the most recent `YYYYMMDD-YYYYMMDD` folder
   - Verify all `raw_*.json` files exist

2. **Launch parallel section generators**
   - Read each `raw_*.json` file
   - Generate markdown sections for each data source
   - Save as `section_*.md` files

3. **Create final report**
   - Aggregate all sections
   - Generate executive summary (MUST be last)
   - Save as `weekly_report.md`

## Data Files

### Raw Data (collected by Python script)
- `raw_github.json` - GitHub PRs, reviews, commits
- `raw_slack.json` - Slack messages, channels, DMs
- `raw_gmail.json` - Email statistics and important messages
- `raw_drive.json` - Document modifications and shares
- `raw_calendar.json` - Meetings and time allocation
- `raw_linear.json` - Issues, priorities, cross-team work
- `raw_launchdarkly.json` - Feature flag changes

### Generated Files (created by Claude)
- `section_github.md` - GitHub activity section
- `section_slack.md` - Slack activity section
- `section_gmail.md` - Gmail activity section
- `section_drive.md` - Drive activity section
- `section_calendar.md` - Calendar activity section
- `section_linear.md` - Linear activity section
- `section_launchdarkly.md` - LaunchDarkly activity section
- `weekly_report.md` - Final combined report

## Report Template

```markdown
# Weekly Snapshot: [START_DATE] - [END_DATE]

*Generated: [CURRENT_DATE]*

## Executive Summary
- **PRs**: [X] created, [Y] reviewed
- **Teams**: [List teams collaborated with]
- **P0/P1 Issues**: [Count and identifiers]
- **Key Decisions**: [1-2 major technical decisions]

## GitHub Activity

### PRs Created
- #[XXX]: [Title] - [URL]

### PRs Reviewed
- #[XXX] by @[author]: [Title] - [URL]

### Commits
- [SHA]: [Message] - [Impact if significant]

## Slack Activity

### Key Messages
- **#[channel]**: [Topic/decision] - [Outcome]
- **DM @[person]**: [Support provided]

### Stats
- Messages sent: [X]
- Channels active: [List]
- DMs/support: [Count]

## Gmail Activity

### Important Emails
- **To**: [Recipients] | **Subject**: [Title] | **Action**: [Decision/outcome]

### Stats
- Emails sent: [X]
- Emails received: [Y]

## Calendar Activity

### Key Meetings
- **[Meeting Name]**: [Duration] | [Attendees] | [Outcome/decision]

### Time Allocation
- Meeting hours: [X]
- Strategic sessions: [Y]
- 1:1s: [Z]

## Google Drive Activity

### Documents Modified
- **[Doc Name]**: [Type] | [Purpose] | [Link if shareable]

### Documents Created
- **[Doc Name]**: [Purpose] | [Audience]

## Linear Activity

### High Priority Issues
- **[ID]**: [Title] - [Status] - [Team]

### Completed This Week
- **[ID]**: [Title] - [Impact]

### Cross-Team Issues
- **[ID]**: [Title] - Teams: [List]

## LaunchDarkly Activity

### Flag Changes
- **[flag-name]**: [Action: created/modified/toggled] - [Environment]

### Production Changes
- [Description of significant production changes]

## Next Week
- [Top priority item with Linear ID]
- [Blocked items needing attention]
- [Scheduled strategic work]

---

*Report generated: [timestamp]*
```

## Claude Code Instructions

When executing this prompt:

### 1. Find the data folder
```python
# Look for most recent YYYYMMDD-YYYYMMDD folder
# Verify all raw_*.json files exist
```

### 2. Launch parallel section generators

**IMPORTANT**: Use Task tool to run these in parallel:

```python
# Launch ALL section generators simultaneously
Task("Generate GitHub section", 
     prompt="Read raw_github.json and create a markdown section with PRs created, reviewed, and commits",
     subagent_type="documentation-specialist")

Task("Generate Slack section",
     prompt="Read raw_slack.json and create a markdown section with key messages and statistics", 
     subagent_type="documentation-specialist")

Task("Generate Gmail section",
     prompt="Read raw_gmail.json and create a markdown section with important emails and stats",
     subagent_type="documentation-specialist")

Task("Generate Calendar section",
     prompt="Read raw_calendar.json and create a markdown section with key meetings and time allocation",
     subagent_type="documentation-specialist")

Task("Generate Drive section",
     prompt="Read raw_drive.json and create a markdown section with documents modified and created",
     subagent_type="documentation-specialist")

Task("Generate Linear section",
     prompt="Read raw_linear.json and create a markdown section with issues and priorities",
     subagent_type="documentation-specialist")

Task("Generate LaunchDarkly section",
     prompt="Read raw_launchdarkly.json and create a markdown section with flag changes",
     subagent_type="documentation-specialist")
```

### 3. Generate final report

After all sections complete:

```python
# Read all section_*.md files
# Generate executive summary based on ALL data
# Combine into final weekly_report.md
```

## Important Notes

- **Executive Summary**: MUST be generated LAST with full context
- **Parallel Execution**: All section generators run simultaneously
- **Data Preservation**: Raw data files are never modified
- **Neutral Tone**: Factual reporting, no subjective assessments
- **Links**: Include all URLs to PRs, issues, documents
- **Folder Structure**: Everything in `YYYYMMDD-YYYYMMDD/`

## Writing Guidelines

- **Concise**: Remove unnecessary words
- **Clear**: Avoid jargon
- **Objective**: Focus on outcomes
- **Action-oriented**: Use active voice
- **Data-focused**: Just facts with links
- **Scannable**: Use bullet points

## Principal Engineer Focus

When generating sections, prioritize:
- **Strategic Impact**: Architectural decisions, system improvements
- **Technical Leadership**: Mentorship, code reviews, unblocking
- **Cross-Team Work**: Breaking silos, aligning teams
- **Organizational Influence**: Process improvements, standards

## Success Metrics

A good weekly snapshot:
- Highlights strategic impact over tactical work
- Quantifies influence (teams affected, engineers helped)
- Documents major technical decisions
- Shows cross-functional leadership
- Demonstrates system-wide thinking
- Captures mentorship and enablement