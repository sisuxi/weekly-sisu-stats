# Principal Engineer Weekly Snapshot Report Generator

Generate comprehensive weekly reports documenting strategic technical leadership, architectural decisions, and cross-team impact.

## Usage

```bash
@go.md
```

## Claude Code Instructions

When executing `@go.md`:

### 1. Calculate date and clean folder
```bash
FOLDER=$(python3 calculate_week.py)
echo "Working on week: $FOLDER"

# Clean slate: remove existing folder completely
rm -rf "$FOLDER"
echo "Cleaned folder: $FOLDER"
```

### 2. Collect raw data
```bash
# Download all raw data for the calculated week
if ! python3 collect_raw_data.py; then
    echo "ERROR: Raw data collection failed. Exiting."
    exit 1
fi
echo "Raw data collection completed successfully"
```

### 3. Launch parallel section generators

**CRITICAL**: Use Task tool to run ALL simultaneously:

```python
Task("Generate GitHub section", 
     prompt="Read raw_github.json and create GitHub activity section",
     subagent_type="documentation-specialist")

Task("Generate Slack section",
     prompt="Read raw_slack.json and create Slack activity section", 
     subagent_type="documentation-specialist")

Task("Generate Gmail section",
     prompt="Read raw_gmail.json and create Gmail activity section",
     subagent_type="documentation-specialist")

Task("Generate Calendar section",
     prompt="Read raw_calendar.json and create Calendar activity section",
     subagent_type="documentation-specialist")

Task("Generate Drive section",
     prompt="Read raw_drive.json and create Drive activity section",
     subagent_type="documentation-specialist")

Task("Generate Linear section",
     prompt="Read raw_linear.json and create Linear activity section",
     subagent_type="documentation-specialist")

Task("Generate LaunchDarkly section",
     prompt="Read raw_launchdarkly.json and create LaunchDarkly activity section",
     subagent_type="documentation-specialist")
```

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
- **PRs**: [X] created, [Y] reviewed  
- **Teams**: [List teams collaborated with]
- **P0/P1 Issues**: [Count and identifiers]
- **Key Decisions**: [Major technical decisions]

## [Data Source] Activity
[Generated from raw_*.json files]
```

## Writing Guidelines

**Focus**: Strategic impact > tactical work
**Style**: Factual, concise, scannable
**Links**: Include all URLs to PRs, issues, documents
**Tone**: Objective reporting, no subjective assessments

## Critical Rules

- **Parallel Execution**: ALL section generators run simultaneously
- **Executive Summary**: Generated LAST with full context  
- **Error Handling**: Exit immediately if ANY data download fails
- **Clean State**: Remove entire folder before regeneration (`rm -rf`)