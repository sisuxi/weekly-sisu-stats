# Claude Code Context for Weekly Snapshot Reports

## Project Overview
This repository generates comprehensive weekly snapshot reports for Sisu Xi, Principal Software Engineer at Hebbia (highest-level IC in the company). The reports document strategic technical leadership, cross-team impact, and organizational influence.

## Critical Context

### User Role
- **Name**: Sisu Xi
- **Position**: Principal Software Engineer at Hebbia
- **Level**: Highest-level Individual Contributor (IC) in the company
- **GitHub**: `sisuxi` (Hebbia work account)
- **Email**: `sisu@hebbia.ai`
- **Start Date**: August 18, 2025

### Report Purpose
Weekly snapshots serve multiple purposes:
1. Performance documentation for reviews
2. Team visibility into principal-level work
3. Historical record of technical decisions
4. Personal tracking of impact and contributions

## Execution Requirements

### CRITICAL: Parallel Execution
**ALWAYS** run data collection tasks in parallel using the Task tool:
- Launch all 7 data collection agents simultaneously
- Launch all 4 section generation agents simultaneously
- Only the final assembly should be sequential

### Folder Structure
Each week gets its own folder: `YYYYMMDD-YYYYMMDD/`
- Raw data files: `*_raw.json`
- Section files: `section_*.md`
- Final report: `weekly_report.md`

### Existing Folder Handling
If folder exists, ask user:
1. Delete and regenerate (default)
2. Keep raw data, regenerate report only
3. Cancel operation

## Report Focus Areas

### Principal Engineer Priorities
- **Strategic Impact**: Architectural decisions, system-wide improvements
- **Technical Leadership**: Mentorship, code reviews, unblocking teams
- **Cross-Team Collaboration**: Breaking silos, aligning teams
- **Organizational Influence**: Process improvements, standards establishment

### Metrics That Matter
- Architecture reviews conducted
- Engineers mentored/unblocked
- Cross-team initiatives led
- System performance improvements
- Technical debt reduced

## Data Sources

All configured in `~/Hebbia/sisu-tools/`:

1. **GitHub**: PRs, reviews, commits (focus on architectural impact)
   - Uses date ranges for precise filtering
   - Tracks created, reviewed, and involved PRs separately
   
2. **Slack**: Technical discussions, mentorship, incident response
   - **NEW**: Uses `history` command for ALL messages (not limited to 50)
   - **NEW**: Checks multiple channels for user's activity
   - **NEW**: Rate limiting protection with `--single-channel` mode
   - Filters messages by user (Sisu Xi)
   
3. **Gmail**: Strategic communications, decisions
   - Filters by date range for sent/received emails
   
4. **Calendar**: Meeting time, strategic sessions
   - Events within specified date range
   
5. **Drive**: Documentation, technical designs
   - Modified documents within date range
   
6. **Linear**: P0/P1 issues, technical debt, cross-team work
   - Issues assigned/created/completed within date range
   
7. **LaunchDarkly**: Production changes, feature rollouts
   - Feature flag status (limited history support)

## Writing Style

Follow `/Users/sisu/.claude/commands/writing_guideline.md`:
- **Concise**: Remove unnecessary words
- **Clear**: Avoid jargon
- **Objective**: Focus on outcomes
- **Action-oriented**: Use active voice

## Common Gotchas

1. **Date Calculation**: Always verify current date from environment
2. **Executive Summary**: MUST be generated AFTER all data collection
3. **Parallel Execution**: Never run data collection sequentially
4. **File Locks**: Each agent writes to separate file
5. **Raw Data**: Always preserve for future reference
6. **Slack Rate Limiting**: Use `--single-channel --channel-delay 2` if hitting rate limits
7. **Date Range Filtering**: All data sources now properly filter by date range

## Usage Pattern

```bash
@go.md
```

This will:
1. Calculate previous week's dates (Sunday-Saturday)
2. Check if folder exists (prompt if yes)
3. Run parallel data collection
4. Generate sections in parallel
5. Create final report with executive summary
6. Output location: `YYYYMMDD-YYYYMMDD/weekly_report.md`

## Key Commands

### Date Calculation
```bash
date +"%Y-%m-%d %A"  # Get current date
# Calculate Sunday-Saturday of previous week
```

### Folder Setup
```bash
mkdir -p YYYYMMDD-YYYYMMDD  # Create week folder (e.g., 20250824-20250830)
```

### Parallel Task Launch Example
```python
# Launch ALL at once (correct)
Task("GitHub collection", ..., writes_to="20250824-20250830/github_raw.json")
Task("Slack collection", ..., writes_to="20250824-20250830/slack_raw.json")
Task("Gmail collection", ..., writes_to="20250824-20250830/gmail_raw.json")
# ... all 7 tasks in one message
```

## Report Sections

1. **Executive Summary** (generated last with full context)
   - Strategic impact
   - Technical leadership
   - Organizational influence

2. **Technical Leadership**
   - Architecture reviews
   - Code contributions
   - Technical decisions

3. **Cross-Team Collaboration**
   - Initiatives led
   - Teams supported
   - Dependencies resolved

4. **Strategic Work**
   - High-priority issues
   - Technical debt
   - Documentation

5. **Metrics**
   - Efficiency metrics
   - Impact measurements
   - Collaboration patterns

## Success Criteria

A good weekly snapshot:
- Highlights strategic impact over tactical work
- Quantifies influence (teams affected, engineers helped)
- Documents major technical decisions
- Shows cross-functional leadership
- Demonstrates system-wide thinking
- Captures mentorship and enablement