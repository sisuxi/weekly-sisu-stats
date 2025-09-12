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

- **Automated Data Collection**: Python scripts handle all API calls and data gathering
- **Principal Engineer Focus**: Emphasizes strategic impact over tactical tasks
- **Self-Contained Reports**: Each week stored in `YYYYMMDD-YYYYMMDD/` folder
- **Data Preservation**: Raw data kept alongside generated reports
- **Writing Guidelines Compliance**: Concise, objective, action-oriented style
- **Flexible Date Ranges**: Support for custom date ranges and automatic week calculation
- **Rate Limiting Protection**: Built-in Slack rate limiting with configurable delays
- **Error Recovery**: Robust error handling with detailed status reporting

## Usage

### Quick Start
Run with Claude Code:
```bash
@go.md
```

### Manual Execution
```bash
# Calculate previous week and collect all data
python3 calculate_week.py --verbose  # See date calculation
python3 collect_raw_data.py          # Collect all data sources
```

### Custom Date Range
```bash
# Collect data for specific dates
python3 collect_raw_data.py --start 2025-08-24 --end 2025-08-30 --force
```

### Slack Rate Limiting
```bash
# For environments with strict rate limits
python3 collect_raw_data.py --single-channel --channel-delay 2

# Check specific channels only
python3 collect_raw_data.py --channels eng ask-eng-leads matrix-team
```

## Report Structure

```
YYYYMMDD-YYYYMMDD/
├── raw_github.json          # GitHub activity data
├── raw_slack.json           # Slack communications
├── raw_gmail.json           # Email activity
├── raw_calendar.json        # Meeting data
├── raw_drive.json           # Document activity
├── raw_linear.json          # Issue tracking
├── raw_launchdarkly.json    # Feature flags
├── section_github.md        # GitHub activity section
├── section_slack.md         # Slack activity section
├── section_gmail.md         # Email activity section
├── section_calendar.md      # Calendar activity section
├── section_drive.md         # Drive activity section
├── section_linear.md        # Linear activity section
├── section_launchdarkly.md  # LaunchDarkly activity section
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

## Workflow

1. **Date Calculation**: `calculate_week.py` determines previous week's Sunday-Saturday range
2. **Data Collection**: `collect_raw_data.py` gathers data from all 7 sources using authenticated APIs
3. **Report Generation**: Claude Code processes raw data files into structured sections
4. **Final Assembly**: All sections combined into comprehensive weekly report

## Command Line Options

### collect_raw_data.py Options
- `--start YYYY-MM-DD --end YYYY-MM-DD`: Custom date range
- `--force`: Overwrite existing data without prompting
- `--channels channel1 channel2`: Specific Slack channels to check
- `--single-channel`: Process Slack channels one at a time (rate limiting)
- `--channel-delay N`: Seconds between Slack channels (default: 1)

### calculate_week.py Options
- `--verbose`: Show detailed date calculation information

## Configuration

All tool configurations are in `~/Hebbia/sisu-tools/`:
- `.venv/`: Python virtual environment with required packages
- `tools/`: Individual API exploration tools
- `config.py`: API keys and tokens
- `google.json`: OAuth credentials
- Various `*_token.json`: Authentication tokens

## Slack Data Collection Improvements

The Slack data collection has been significantly enhanced:
- **Full Message History**: Uses `history` command instead of limited search results
- **User-Specific Filtering**: Filters messages by user identity across all channels
- **Multi-Channel Support**: Checks 12+ relevant engineering channels automatically
- **Rate Limiting**: Built-in protection with configurable delays between channels
- **Channel Selection**: Option to target specific channels for faster collection

## Error Handling

Robust error handling throughout the data collection process:
- Individual source failures don't stop the entire collection
- Detailed error reporting for troubleshooting
- Graceful degradation with partial data collection
- Timeout protection for API calls (30s per command)
- Authentication verification before data collection

## Author

Sisu Xi - Principal Software Engineer at Hebbia
