# Principal Engineer Weekly Snapshot Report Generator

Generate comprehensive weekly snapshot reports documenting strategic technical leadership, architectural decisions, and cross-team impact across GitHub, Slack, Gmail, Drive, Calendar, Linear, and LaunchDarkly.

## Purpose
Generate concise, data-focused weekly activity snapshots with links to sources. Reports provide factual summaries of work completed across GitHub, Slack, Gmail, Drive, Calendar, Linear, and LaunchDarkly.

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

**IMPORTANT**: The Executive Summary MUST be generated AFTER all data collection is complete. Keep it to 4-5 bullet points with just high-level metrics.

Create the report in `reports/YYYYMMDD-YYYYMMDD.md` format with the following structure:

## Report Template (Data-Focused Format)

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
- #[XXX]: [Title] - [URL]

### PRs Reviewed
- #[XXX] by @[author]: [Title] - [URL]
- #[XXX] by @[author]: [Title] - [URL]

### Commits
- [SHA]: [Message] - [Impact if significant]

## Slack Activity

### Key Messages
- **#[channel]**: [Topic/decision] - [Outcome]
- **DM @[person]**: [Support provided]
- **Thread**: [Technical discussion] - [Resolution]

### Stats
- Messages sent: [X]
- Channels active: [List]
- DMs/support: [Count]

## Gmail Activity

### Important Emails
- **To**: [Recipients] | **Subject**: [Title] | **Action**: [Decision/outcome]
- **From**: [Sender] | **Subject**: [Title] | **Response**: [Action taken]

### Stats
- Emails sent: [X]
- Emails received: [Y]
- Response rate: [%]

## Calendar Activity

### Key Meetings
- **[Meeting Name]**: [Duration] | [Attendees] | [Outcome/decision]
- **[Meeting Name]**: [Duration] | [Type: 1:1/team/strategic]

### Time Allocation
- Meeting hours: [X]
- Strategic sessions: [Y]
- 1:1s: [Z]

## Google Drive Activity

### Documents Modified
- **[Doc Name]**: [Type] | [Purpose] | [Link if shareable]
- **[Doc Name]**: [Collaborators] | [Status]

### Documents Created
- **[Doc Name]**: [Purpose] | [Audience]

## Linear Activity

### High Priority Issues
- **[ID]**: [Title] - [Status] - [Team] - [URL]
- **[ID]**: [Title] - P[0/1] - [Status]

### Completed This Week
- **[ID]**: [Title] - [Impact]

### Cross-Team Issues
- **[ID]**: [Title] - Teams: [List] - [Dependencies]

## LaunchDarkly Activity

### Flag Changes
- **[flag-name]**: [Action: created/modified/toggled] - [Environment]
- **[flag-name]**: [Rollout %] - [Impact]

### Production Changes
- [Description of significant production changes]

## Next Week
- [Top priority item with Linear ID]
- [Blocked items needing attention]
- [Scheduled strategic work]

---

*Report generated: [timestamp]*
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
   Task A: Generate GitHub section → YYYYMMDD-YYYYMMDD/section_github.md
   Task B: Generate Slack section → YYYYMMDD-YYYYMMDD/section_slack.md
   Task C: Generate Gmail section → YYYYMMDD-YYYYMMDD/section_gmail.md
   Task D: Generate Calendar section → YYYYMMDD-YYYYMMDD/section_calendar.md
   Task E: Generate Drive section → YYYYMMDD-YYYYMMDD/section_drive.md
   Task F: Generate Linear section → YYYYMMDD-YYYYMMDD/section_linear.md
   Task G: Generate LaunchDarkly section → YYYYMMDD-YYYYMMDD/section_launchdarkly.md
   ```

### 5. **Sequential Final Assembly**:
   
   After all parallel tasks complete:
   
   a. **Aggregate all data** from YYYYMMDD-YYYYMMDD/ folder
   
   b. **Generate Executive Summary** (MUST be done AFTER all data is collected):
      - Count total PRs created and reviewed
      - List teams collaborated with
      - Note P0/P1 issues
      - Extract 1-2 key technical decisions (if any)
   
   c. **Merge sections** into final report:
      - Executive Summary (4-5 bullet points only)
      - GitHub Activity (from section_github.md)
      - Slack Activity (from section_slack.md)
      - Gmail Activity (from section_gmail.md)
      - Calendar Activity (from section_calendar.md)
      - Google Drive Activity (from section_drive.md)
      - Linear Activity (from section_linear.md)
      - LaunchDarkly Activity (from section_launchdarkly.md)
      - Next Week (brief list)
   
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

# Then launch section generation in parallel (7 separate sections)
Task("Generate GitHub section", analyze_github_data, reads=["20250824-20250830/github_raw.json"])
Task("Generate Slack section", analyze_slack_data, reads=["20250824-20250830/slack_raw.json"])
Task("Generate Gmail section", analyze_gmail_data, reads=["20250824-20250830/gmail_raw.json"])
Task("Generate Calendar section", analyze_calendar_data, reads=["20250824-20250830/calendar_raw.json"])
Task("Generate Drive section", analyze_drive_data, reads=["20250824-20250830/drive_raw.json"])
Task("Generate Linear section", analyze_linear_data, reads=["20250824-20250830/linear_raw.json"])
Task("Generate LaunchDarkly section", analyze_ld_data, reads=["20250824-20250830/launchdarkly_raw.json"])

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

- **Executive Summary MUST be generated LAST**: Keep to 4-5 high-level bullet points only
- **Neutral tone throughout**: No subjective assessments, just facts with links
- **Data-focused sections**: Each data source gets its own section (GitHub, Slack, etc.)
- **Include all URLs**: Every PR, issue, document should have a clickable link
- **Use separate files**: Prevents file lock conflicts during parallel writes
- **Claude's parallel capability**: Leverage Claude's ability to run multiple tools simultaneously
- **Folder structure**: Everything for a week stays in one folder (YYYYMMDD-YYYYMMDD/)
  - Raw data files: `*_raw.json`
  - Section files: `section_*.md`
  - Final report: `weekly_report.md`
- **Data preservation**: All raw data is kept for future reference or reprocessing

## Guidelines

- **Writing Style**:
  - **Neutral tone**: Factual, no superlatives or subjective assessments
  - **Bullet points**: Data in scannable format
  - **Links included**: Direct URLs to PRs, issues, documents
  - **Concise**: Just the facts, no narrative
  - **Raw data**: Focus on what happened, not interpretation

- **Content Format**:
  - One section per data source (GitHub, Slack, etc.)
  - Chronological or priority order within sections
  - Include identifiers (PR#, issue ID, etc.)
  - Add URLs for easy access
  - Keep descriptions to essential information only

- **Technical Details**:
  - Pacific Time (PT) for all timestamps
  - Include all PR/issue/document links
  - Use exact titles from sources
  - Preserve original formatting (PR titles, issue names)
  - No editorializing or analysis