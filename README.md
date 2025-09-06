# Weekly Snapshot Report Generator

Comprehensive weekly activity reporting system for Principal Engineer role at Hebbia.

## Overview

Generates detailed weekly snapshot reports documenting technical leadership, architectural decisions, and cross-team impact by aggregating data from multiple sources:

- **GitHub**: PRs, reviews, commits, cross-team collaboration
- **Slack**: Technical discussions, mentorship, incident response
- **Gmail**: Important communications, decisions, threads
- **Google Calendar**: Meetings, time allocation, strategic sessions
- **Google Drive**: Documentation, technical designs, knowledge sharing
- **Linear**: High-priority issues, technical debt, cross-team dependencies
- **LaunchDarkly**: Feature flag changes, production rollouts

## Features

- **Parallel Data Collection**: 60-80% faster through simultaneous API calls
- **Principal Engineer Focus**: Emphasizes strategic impact over tactical tasks
- **Self-Contained Reports**: Each week stored in `YYYYMMDD-YYYYMMDD/` folder
- **Data Preservation**: Raw data kept alongside generated reports
- **Writing Guidelines Compliance**: Concise, objective, action-oriented style

## Usage

Run with Claude Code:
```bash
@go.md
```

This will:
1. Calculate date range (default: previous Monday-Sunday)
2. Create folder `YYYYMMDD-YYYYMMDD/`
3. Collect data from all sources in parallel
4. Generate report sections
5. Create final report at `YYYYMMDD-YYYYMMDD/weekly_report.md`

### Custom Date Range

Specify custom dates when prompted:
```
"Generate report for 2025-08-26 to 2025-09-01"
```

## Report Structure

```
YYYYMMDD-YYYYMMDD/
├── github_raw.json          # GitHub activity data
├── slack_raw.json           # Slack communications
├── gmail_raw.json           # Email activity
├── calendar_raw.json        # Meeting data
├── drive_raw.json           # Document activity
├── linear_raw.json          # Issue tracking
├── launchdarkly_raw.json    # Feature flags
├── section_technical.md     # Technical leadership
├── section_collaboration.md # Cross-team work
├── section_strategic.md     # Strategic initiatives
├── section_metrics.md       # Performance metrics
└── weekly_report.md         # Final consolidated report
```

## Report Contents

The weekly snapshot includes:

### Executive Summary
- Strategic impact and architectural decisions
- Technical leadership and mentorship
- Organizational influence and process improvements

### Detailed Sections
- **Technical Leadership**: Architecture reviews, code contributions, technical decisions
- **Cross-Team Collaboration**: Initiatives led, teams supported, dependencies resolved
- **Strategic Work**: High-priority issues, technical debt, documentation
- **Organizational Impact**: Strategic meetings, key communications, process improvements
- **Metrics**: Review velocity, mentorship reach, system impact

## Prerequisites

Requires access to:
- Hebbia GitHub organization (`sisuxi` account)
- Hebbia Slack workspace
- Gmail with OAuth authentication
- Google Calendar and Drive
- Linear workspace
- LaunchDarkly dashboard

Tools are configured in `~/Hebbia/sisu-tools/`

## Configuration

All tool configurations are in `~/Hebbia/sisu-tools/tools/`:
- `config.py`: API keys and tokens
- `google.json`: OAuth credentials
- Various `*_token.json`: Authentication tokens

## Author

Sisu Xi - Principal Software Engineer at Hebbia
