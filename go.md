# Principal Engineer Weekly Snapshot Report Generator

**INSTRUCTIONS FOR CLAUDE**: Follow this workflow exactly. Do NOT manually calculate dates - use the existing Python scripts.

## Workflow Steps

### 1. Calculate date and clean folder

**ALWAYS** use the existing script:

```bash
FOLDER=$(python3 calculate_week.py)
echo "Working on week: $FOLDER"

# Clean slate: remove existing folder completely
rm -rf "$FOLDER"
echo "Cleaned folder: $FOLDER"
```

### 2. Collect raw data

**ALWAYS** use the existing script:

```bash
# Download all raw data for the calculated week
if ! python3 collect_raw_data.py; then
    echo "ERROR: Raw data collection failed. Exiting."
    exit 1
fi
echo "Raw data collection completed successfully"
```

### 3. Generate sections sequentially

Generate each section one at a time, reading the raw data files:

1. Read `raw_github.json` and create `section_github.md`
2. Read `raw_slack.json` and create `section_slack.md` 
3. Read `raw_gmail.json` and create `section_gmail.md`
4. Read `raw_calendar.json` and create `section_calendar.md`
5. Read `raw_drive.json` and create `section_drive.md`
6. Read `raw_linear.json` and create `section_linear.md`
7. Read `raw_launchdarkly.json` and create `section_launchdarkly.md`

### 4. Generate final report

After ALL sections complete:

- Read all `section_*.md` files
- Generate executive summary LAST (with full context)
- Combine into `weekly_report.md`

## Data Sources

**Raw Data** (collected by Python):

- `raw_github.json` - PRs, reviews, commits
- `raw_slack.json` - Messages, channels, DMs
- `raw_gmail.json` - Email statistics
- `raw_drive.json` - Document modifications
- `raw_calendar.json` - Meetings, time allocation
- `raw_linear.json` - Issues, priorities
- `raw_launchdarkly.json` - Feature flag changes

**Generated Files** (created by Claude):

- `section_*.md` - Individual activity sections
- `weekly_report.md` - Final combined report

## Report Template

```markdown
# Weekly Snapshot: [START_DATE] - [END_DATE]

## Executive Summary

- **PRs**: X total (X1 in repo1, X2 in repo2, ...)
- **Feature Flags**: X created/updated by me
- **Docs**: X created/updated (doc1, doc2, ... ranked by importance)
- **Meetings**: X meetings totaling Y hours

## GitHub Activity

### PRs Created
[Group by repo with high-level summary]
**Repo Name**: Brief summary of PRs in this repo
- #PR_NUMBER: Title - URL
- ...

### PRs Reviewed
[Group by repo with high-level summary]
**Repo Name**: Brief summary of reviews in this repo
- #PR_NUMBER: Title - URL
- ...

## Slack Activity
[If no activity, just say "No activity recorded"]

## Gmail Activity
- Received: X emails
- Sent: Y emails

Important sent emails:
- [List important sent emails]
[If no sent activity, just say "No sent emails"]

## Calendar Activity
X meetings totaling Y hours

**Area Name** (Z hours total):
- Meeting Name (duration) [doc link if available]
- ...

## Drive Activity
X docs created/updated/reviewed

**Area Name**: Brief summary
- Doc Name - URL
- ...

## Linear Activity
[If no activity, just say "No activity"]

## LaunchDarkly Activity
[Only show flags created/updated by me. If none, say "No flags created/updated"]
```

## Writing Guidelines

**Focus**: Concise, factual reporting
**Style**: Short, bullet-point driven
**Links**: Include all URLs to PRs, issues, documents
**Tone**: Objective reporting, no subjective assessments
**Length**: Keep report SHORT and to the point

## Critical Rules for Claude

- **NO MANUAL DATE CALCULATION**: Always use `python3 calculate_week.py`
- **NO MANUAL DATA COLLECTION**: Always use `python3 collect_raw_data.py`  
- **Sequential Execution**: Generate sections one at a time
- **Executive Summary**: Generated LAST with full context
- **Error Handling**: Exit immediately if ANY data download fails
- **Clean State**: Remove entire folder before regeneration (`rm -rf`)
- **Follow Scripts**: Use existing Python automation, don't reinvent
