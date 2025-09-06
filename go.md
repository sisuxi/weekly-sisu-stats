# Principal Engineer Weekly Snapshot Report Generator

Generate comprehensive weekly snapshot reports documenting strategic technical leadership, architectural decisions, and cross-team impact across GitHub, Slack, Gmail, Drive, Calendar, Linear, and LaunchDarkly.

## Purpose
Document principal-level engineering work including technical leadership, architectural guidance, mentorship, cross-functional collaboration, and strategic initiatives. Reports serve as weekly snapshots capturing high-impact contributions, technical decisions, and organizational influence as the company's highest-level IC.

## Usage

To generate last week's report (Sunday-Saturday):
```bash
# Run this prompt with Claude Code
# Automatically calculates last week's dates and generates the report
```

To generate a custom date range report:
```bash
# Specify custom dates: "2025-08-24 to 2025-08-30"
```

## Report Generation Process

### Step 1: Date Calculation
```bash
# Get current date
date +"%Y-%m-%d %A"

# Calculate last week's date range (Sunday to Saturday)
# If today is 2025-09-05 (Friday), last week would be:
# Sunday: 2025-08-24
# Saturday: 2025-08-30
```

### Step 2: Data Collection Commands

**IMPORTANT**: Claude should run these commands via parallel Task agents, NOT sequentially. Each command group below should be executed by a separate agent writing to its own output file.

#### GitHub Activity (Principal Engineer Focus)
```bash
# Verify account
gh auth switch --hostname github.com --user sisuxi
gh auth status --hostname github.com | grep "Logged in to github.com as sisuxi"

# Strategic PRs created (likely architectural or high-impact)
gh search prs --author=sisuxi --created=">=START_DATE" --json number,title,state,createdAt,updatedAt,url,repository,labels,comments

# Critical PR reviews given (focus on architecture and mentorship)
gh search prs --reviewed-by=sisuxi --updated=">=START_DATE" --json number,title,author,url,reviews | jq '.[] | select(.reviews[].body | length > 100)'

# Cross-team collaboration (PRs across multiple repos)
gh search prs --involves=sisuxi --updated=">=START_DATE" --json number,title,repository,author

# Commits with significant impact
gh search commits --author=sisuxi --repo=hebbia/mono --committer-date=">=START_DATE..END_DATE" --json sha,commit | jq '.[] | select(.commit.message | test("fix|critical|performance|security"; "i"))'

# Team member PRs (for mentorship tracking)
gh pr list --repo hebbia/mono --state all --limit 100 --json number,author,createdAt,reviews | jq --arg start "START_DATE" '.[] | select(.createdAt >= $start and (.reviews[]?.author.login == "sisuxi"))'
```

#### Slack Activity (Technical Leadership)
```bash
# Technical discussions and decisions
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/slack_explorer.py search "from:@sisu" --count 100

# Architecture and engineering channels
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/slack_explorer.py search "from:@sisu in:#engineering OR in:#architecture OR in:#platform" --count 50

# Mentorship and support (DMs and threads)
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/slack_explorer.py activity --days 7

# Critical incident responses
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/slack_explorer.py search "from:@sisu in:#incidents OR in:#alerts" --count 20
```

#### Gmail Activity
```bash
# Inbox statistics for the week
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/gmail_explorer.py stats --days 7

# Important emails
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/gmail_explorer.py important --days 7

# Sent emails
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/gmail_explorer.py sent --days 7

# Get detailed email data
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/gmail_explorer.py export --days 7 > week_emails.json
```

#### Google Drive Activity
```bash
# Documents modified during the week
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/drive_explorer.py recent --days 7

# Documents shared with me
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/drive_explorer.py shared --days 7

# Search for specific project documents
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/drive_explorer.py search "hebbia" --days 7
```

#### Calendar Activity
```bash
# Get all meetings for the week
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/calendar_explorer.py events --from "START_DATE" --to "END_DATE" --json > week_calendar.json

# Analyze meeting time
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/calendar_explorer.py analyze --from "START_DATE" --to "END_DATE"

# Check for important meetings
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/calendar_explorer.py search "1:1" --from "START_DATE" --to "END_DATE"
```

#### Linear Activity (Strategic Focus)
```bash
# High-priority issues (P0/P1) assigned or created
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/linear_explorer.py "query { issues(filter: { OR: [{assignee: { email: { eq: \"sisu@hebbia.ai\" } }}, {creator: { email: { eq: \"sisu@hebbia.ai\" } }}], priority: { in: [0, 1] }, updatedAt: { gte: \"START_DATE\" } }, first: 50) { nodes { identifier title state { name } priority updatedAt url team { name } } } }"

# Cross-team issues and dependencies
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/linear_explorer.py "query { issues(filter: { OR: [{assignee: { email: { eq: \"sisu@hebbia.ai\" } }}, {subscribers: { email: { eq: \"sisu@hebbia.ai\" } }}], updatedAt: { gte: \"START_DATE\" } }, first: 50) { nodes { identifier title state { name } priority team { name } parent { identifier title } children { nodes { identifier title } } } } }"

# Technical debt and architecture issues
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/linear_explorer.py "query { issues(filter: { labels: { name: { in: [\"tech-debt\", \"architecture\", \"performance\"] } }, OR: [{assignee: { email: { eq: \"sisu@hebbia.ai\" } }}, {creator: { email: { eq: \"sisu@hebbia.ai\" } }}], updatedAt: { gte: \"START_DATE\" } }, first: 50) { nodes { identifier title state { name } labels { nodes { name } } team { name } } } }"

# Completed high-impact issues
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/linear_explorer.py "query { issues(filter: { assignee: { email: { eq: \"sisu@hebbia.ai\" } }, state: { type: { eq: \"completed\" } }, completedAt: { gte: \"START_DATE\" } }, first: 50) { nodes { identifier title completedAt url team { name } priority } } }"
```

#### LaunchDarkly Activity
```bash
# Check recent flag changes (audit log)
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/launchdarkly_explorer.py query "/auditlog" --params '{"limit": 100}' | jq --arg start "START_DATE" '.items[] | select(.date >= ($start | fromdateiso8601 * 1000))'

# Get flags modified by me (if applicable)
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/launchdarkly_explorer.py query "/auditlog" --params '{"limit": 100}' | jq --arg email "sisu@hebbia.ai" '.items[] | select(.member.email == $email)'

# Check production flags status
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/launchdarkly_explorer.py flags --env production --limit 100 | jq '.items[] | {key: .key, on: .on, tags: .tags}'

# Find team-specific flags
cd ~/Hebbia/sisu-tools && .venv/bin/python tools/launchdarkly_explorer.py flags | jq '.items[] | select(.tags | contains(["matrix"]) or contains(["epd"]))'
```

### Step 3: Report Generation

**IMPORTANT**: The Executive Summary MUST be generated AFTER all data collection is complete, as it needs full visibility into the week's activities to accurately identify highlights and lowlights.

Create the report in `reports/YYYYMMDD-YYYYMMDD.md` format with the following structure:

## Report Template (Principal Engineer Focus)

```markdown
# Principal Engineer Weekly Snapshot: [START_DATE] - [END_DATE]

*Generated: [CURRENT_DATE]*

## Executive Summary

### Strategic Impact
- [Major architectural decision with long-term implications]
- [Cross-team initiative delivered or advanced]
- [Technical debt reduction or system optimization]
- [Critical production issue resolved or prevented]

### Technical Leadership
- [Mentored engineers on complex problem]
- [Guided architectural review or design]
- [Unblocked teams with technical expertise]

### Organizational Influence  
- [Process improvement implemented]
- [Standard or best practice established]
- [Cross-functional alignment achieved]

### Metrics
- **Technical Reviews**: [X] architecture reviews, [Y] code reviews
- **Mentorship**: [X] engineers guided, [Y] technical discussions led
- **Cross-team**: [X] teams collaborated with
- **System Impact**: [Performance gains, reliability improvements]

## Technical Leadership

### Architecture & Design
**Reviews Led:**
- PR #[XXX]: [Architectural guidance provided, impact on system design]
- Design Review: [System/component reviewed with recommendations]

**Technical Decisions:**
- [Major technical decision]: [Rationale and expected impact]
- [Technology choice]: [Trade-offs considered, long-term implications]

### Code Contributions
**Strategic PRs:**
- PR #[XXX]: [System-level improvement or critical fix]
- PR #[XXX]: [Performance optimization with measurable impact]

**High-Impact Reviews:**
- PR #[XXX] by [Engineer]: [Critical feedback that prevented issue]
- PR #[XXX] by [Team]: [Architectural guidance provided]

## Cross-Team Collaboration

### Initiatives Led
- [Initiative]: Teams involved, current status, impact
- [Project]: Cross-functional alignment achieved

### Team Support
**Unblocked:**
- [Team]: [Technical blocker resolved]
- [Engineer]: [Complex problem solved]

**Mentorship:**
- [Engineer]: [Technical concept taught or skill developed]
- [Team]: [Best practice introduced or process improved]

### Feature Flags & Production
**Critical Changes:**
- `flag-name`: [Production rollout strategy and impact]
- System optimization: [Performance gain achieved]

## Strategic Work

### Linear Issues
**High-Priority Delivered:**
- [P0/P1 Issue]: [Business impact of resolution]
- [Cross-team Issue]: [Dependencies resolved]

**Technical Debt:**
- [Debt Item]: [Long-term benefit of addressing]

### Documentation & Standards
**Created/Updated:**
- [Architecture Doc]: [Future-proofing aspect]
- [Technical Standard]: [Teams affected, adoption plan]
- [Runbook/Guide]: [Operational improvement enabled]

## Organizational Impact

### Meetings & Decisions
**Strategic Meetings:**
- [Executive/Leadership]: [Technical input provided, decision influenced]
- [Architecture Review]: [System design guided]
- [Cross-team Sync]: [Alignment achieved]

### Communication
**Key Threads:**
- [Slack/Email]: [Technical decision communicated to org]
- [Discussion]: [Consensus built on approach]

### Process & Culture
- [Engineering Practice]: [Improvement introduced]
- [Tool/Process]: [Efficiency gain for teams]

## Next Week Focus

### Strategic Priorities
1. [Major Initiative]: [Why critical now, who's depending on it]
2. [Technical Investigation]: [What we'll learn, decisions it enables]
3. [Team Enablement]: [Who will be unblocked]

### Risk Mitigation
- [Technical Risk]: [Mitigation plan]
- [Dependency]: [Contingency approach]

## Principal Engineer Metrics

### Technical Leadership
- Architecture reviews: [X]
- Critical PRs reviewed: [Y] 
- Engineers mentored: [Z]
- Teams supported: [List]

### System Impact
- Performance improvements: [Metrics]
- Reliability gains: [Uptime/error rate changes]
- Technical debt reduced: [Estimated hours saved]
- Security issues prevented: [Count/severity]

### Organizational Influence
- Cross-team initiatives: [X]
- Standards established: [Y]
- Engineers influenced: [Estimated reach]
- Strategic decisions shaped: [Count]

---

*Report generated automatically using weekly-stats tools*
```

## Implementation Instructions

When executing this prompt with Claude:

### 1. **Calculate dates**: 
   - Default: Previous Sunday-Saturday
   - Custom: Parse provided range
   - Format: YYYYMMDD-YYYYMMDD (e.g., 20250824-20250830)

### 2. **Setup**:
   
   **IMPORTANT**: Check if folder exists before proceeding:
   
   ```bash
   # Check if folder already exists
   if [ -d "YYYYMMDD-YYYYMMDD" ]; then
       # Claude should ask user:
       # "Folder YYYYMMDD-YYYYMMDD already exists. What would you like to do?
       #  1. Delete and regenerate everything (default - press Enter)
       #  2. Keep raw data, regenerate report only
       #  3. Cancel operation"
       
       # Default action (if user presses Enter or says "1" or "delete"):
       rm -rf YYYYMMDD-YYYYMMDD
       mkdir -p YYYYMMDD-YYYYMMDD
       
       # Option 2: Keep raw data files, only regenerate report
       # Skip data collection, go directly to section generation
       
       # Option 3: Exit without doing anything
   else
       # Create new folder
       mkdir -p YYYYMMDD-YYYYMMDD  # Example: 20250824-20250830
   fi
   ```

### 3. **Parallel Data Collection** (CRITICAL for speed):
   
   Claude should launch multiple Task agents in parallel to collect data simultaneously:
   
   ```
   # Launch all data collection agents AT ONCE (not sequentially)
   # All files saved to YYYYMMDD-YYYYMMDD/ folder
   Task 1: GitHub Activity Collection → YYYYMMDD-YYYYMMDD/github_raw.json
   Task 2: Slack Activity Collection → YYYYMMDD-YYYYMMDD/slack_raw.json  
   Task 3: Gmail Activity Collection → YYYYMMDD-YYYYMMDD/gmail_raw.json
   Task 4: Calendar Activity Collection → YYYYMMDD-YYYYMMDD/calendar_raw.json
   Task 5: Drive Activity Collection → YYYYMMDD-YYYYMMDD/drive_raw.json
   Task 6: Linear Activity Collection → YYYYMMDD-YYYYMMDD/linear_raw.json
   Task 7: LaunchDarkly Activity Collection → YYYYMMDD-YYYYMMDD/launchdarkly_raw.json
   ```
   
   Each agent should:
   - Run independently to avoid file locks
   - Save raw data to separate JSON files in the date folder
   - Return completion status

### 4. **Parallel Section Generation**:
   
   After data collection, launch parallel agents to generate report sections:
   
   ```
   # Launch section generation agents in parallel
   # All sections saved to same YYYYMMDD-YYYYMMDD/ folder
   Task A: Generate Technical Leadership section → YYYYMMDD-YYYYMMDD/section_technical.md
   Task B: Generate Cross-Team Collaboration section → YYYYMMDD-YYYYMMDD/section_collaboration.md
   Task C: Generate Strategic Work section → YYYYMMDD-YYYYMMDD/section_strategic.md
   Task D: Generate Metrics section → YYYYMMDD-YYYYMMDD/section_metrics.md
   ```

### 5. **Sequential Final Assembly**:
   
   After all parallel tasks complete:
   
   a. **Aggregate all data** from YYYYMMDD-YYYYMMDD/ folder
   
   b. **Generate Executive Summary** (MUST be done AFTER all data is collected):
      - Analyze all sections for highlights
      - Identify lowlights and blockers
      - Calculate overall metrics
      - Extract strategic impact
   
   c. **Merge sections** into final report:
      - Executive Summary (generated from full data)
      - Technical Leadership (from section_technical.md)
      - Cross-Team Collaboration (from section_collaboration.md)
      - Strategic Work (from section_strategic.md)
      - Metrics (from section_metrics.md)
   
   d. **Save final report**: `YYYYMMDD-YYYYMMDD/weekly_report.md`

### 6. **Output**: 
   - Report location: `YYYYMMDD-YYYYMMDD/weekly_report.md`
   - Summary statistics displayed to user
   - All raw data preserved in same folder for reference

## Parallel Execution Best Practices

- **Use Task tool aggressively**: Launch multiple agents for independent operations
- **Avoid sequential operations**: Never run data collection commands one after another
- **File isolation**: Each agent writes to its own file to prevent locks
- **Status tracking**: Monitor completion of all parallel tasks before proceeding
- **Error handling**: If any agent fails, retry that specific task
- **Performance gain**: Parallel execution should reduce total time by 60-80%

### Example Claude Execution Pattern

```python
# CORRECT: Parallel execution (what Claude should do)
# Launch ALL these tasks in a single message with multiple tool calls
# Example: For week 20250824-20250830
Task("GitHub data collection", collect_github_data, writes_to="20250824-20250830/github_raw.json")
Task("Slack data collection", collect_slack_data, writes_to="20250824-20250830/slack_raw.json")
Task("Gmail data collection", collect_gmail_data, writes_to="20250824-20250830/gmail_raw.json")
Task("Calendar data collection", collect_calendar_data, writes_to="20250824-20250830/calendar_raw.json")
Task("Linear data collection", collect_linear_data, writes_to="20250824-20250830/linear_raw.json")
Task("Drive data collection", collect_drive_data, writes_to="20250824-20250830/drive_raw.json")
Task("LaunchDarkly data collection", collect_ld_data, writes_to="20250824-20250830/launchdarkly_raw.json")

# Wait for all to complete...

# Then launch section generation in parallel
Task("Generate technical section", analyze_technical_data, reads=["20250824-20250830/github_raw.json", "20250824-20250830/launchdarkly_raw.json"])
Task("Generate collaboration section", analyze_collab_data, reads=["20250824-20250830/slack_raw.json", "20250824-20250830/gmail_raw.json"])
Task("Generate strategic section", analyze_strategic_data, reads=["20250824-20250830/linear_raw.json", "20250824-20250830/calendar_raw.json"])

# Wait for all sections...

# Finally, generate executive summary with full context
Task("Generate executive summary and final report", create_final_report, reads=all_files_in_folder, writes_to="20250824-20250830/weekly_report.md")
```

```python
# WRONG: Sequential execution (avoid this)
collect_github_data()
wait_for_completion()
collect_slack_data()  # Wastes time waiting
wait_for_completion()
collect_gmail_data()  # Could have run in parallel
# etc...
```

## Important Notes

- **Executive Summary MUST be generated LAST**: It needs all data to accurately summarize
- **Highlights/Lowlights require full context**: Don't generate these until all sections are complete
- **Use separate files**: Prevents file lock conflicts during parallel writes
- **Claude's parallel capability**: Leverage Claude's ability to run multiple tools simultaneously
- **Folder structure**: Everything for a week stays in one folder (YYYYMMDD-YYYYMMDD/)
  - Raw data files: `*_raw.json`
  - Section files: `section_*.md`
  - Final report: `weekly_report.md`
- **Data preservation**: All raw data is kept for future reference or reprocessing

## Guidelines

- **Writing Style**: Follow `/Users/sisu/.claude/commands/writing_guideline.md`
  - Concise: Remove unnecessary words
  - Clear: Avoid jargon, explain technical terms
  - Objective: Focus on facts and outcomes
  - Action-oriented: Use active voice

- **Principal Engineer Focus**:
  - Strategic impact over tactical tasks
  - System-wide improvements over local fixes
  - Mentorship and team enablement
  - Cross-functional collaboration
  - Technical decision-making and architecture
  - Long-term technical vision

- **Content Priorities**:
  - Architectural decisions and their rationale
  - Cross-team initiatives and alignment
  - Technical debt reduction with measurable impact
  - Mentorship and knowledge transfer
  - Production stability and performance gains
  - Standards and best practices established

- **Technical Details**:
  - Pacific Time (PT) for all timestamps
  - Include PR/issue links
  - Verify metrics from raw data
  - Highlight P0/P1 items
  - Quantify impact (users affected, performance gains, etc.)