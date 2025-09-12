#!/usr/bin/env python3
"""
Raw Data Collector for Weekly Snapshot Reports
Collects data from GitHub, Slack, Gmail, Drive, Calendar, Linear, and LaunchDarkly
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
import argparse


def run_command(cmd, cwd=None):
    """Execute a shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Error running command: {cmd}")
            print(f"Error: {result.stderr}")
            return None
        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"Command timed out: {cmd}")
        return None
    except Exception as e:
        print(f"Exception running command: {cmd}")
        print(f"Error: {e}")
        return None


def collect_github_data(start_date, end_date, output_dir):
    """Collect GitHub activity data"""
    print("Collecting GitHub data...")
    data = {}
    
    # Verify account
    cmd = "gh auth status 2>&1"
    auth_check = run_command(cmd)
    if not auth_check or 'sisuxi' not in auth_check:
        raise Exception("GitHub auth verification failed - not authenticated as sisuxi")
    
    # PRs created in Hebbia org within date range
    cmd = f'gh search prs --author=sisuxi --created="{start_date}..{end_date}" "org:hebbia" --json number,title,state,createdAt,updatedAt,url,repository,labels'
    result = run_command(cmd)
    if result:
        try:
            data['prs_created'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_created'] = []
    
    # PRs reviewed in Hebbia org within date range
    cmd = f'gh search prs --reviewed-by=sisuxi --updated="{start_date}..{end_date}" "org:hebbia" --json number,title,author,url,repository'
    result = run_command(cmd)
    if result:
        try:
            prs = json.loads(result)
            # Filter to only include reviews actually done in the date range
            filtered_prs = []
            for pr in prs:
                # Keep PRs that were likely reviewed during this period
                if pr.get('updatedAt', '') >= start_date:
                    filtered_prs.append(pr)
            data['prs_reviewed'] = filtered_prs
        except json.JSONDecodeError:
            data['prs_reviewed'] = []
    
    # PRs involved in Hebbia org within date range
    cmd = f'gh search prs --involves=sisuxi --updated="{start_date}..{end_date}" "org:hebbia" --json number,title,repository,author'
    result = run_command(cmd)
    if result:
        try:
            data['prs_involved'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_involved'] = []
    
    # Commits in all Hebbia repos within date range
    cmd = f'gh search commits --author=sisuxi --author-date="{start_date}..{end_date}" "org:hebbia" --limit 100 --json sha,commit,repository'
    result = run_command(cmd)
    if result:
        try:
            data['commits'] = json.loads(result)
        except json.JSONDecodeError:
            data['commits'] = []
    
    # Team PRs reviewed across all Hebbia repos within date range
    cmd = f'gh search prs --reviewed-by=sisuxi --created="{start_date}..{end_date}" "org:hebbia" --limit 100 --json number,title,author,repository,createdAt,state'
    result = run_command(cmd)
    if result:
        try:
            data['team_prs_reviewed'] = json.loads(result)
        except json.JSONDecodeError:
            data['team_prs_reviewed'] = []
    
    output_path = Path(output_dir) / "raw_github.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"GitHub data saved to {output_path}")
    return data


def collect_slack_data(start_date, end_date, output_dir, channels=None, single_channel_mode=False, channel_delay=1):
    """Collect Slack activity data - focused on user's messages"""
    print("Collecting Slack data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    # Default channels to check for user's activity
    if channels is None:
        channels = ['eng', 'ask-eng-leads', 'eng-postmortems', 'oncall', 'alerts', 
                   'bugs-and-support', 'product-change-log', 'feedback-eng', 
                   'matrix-team', 'doc-team', 'agents-team', 'infra-team']
    
    print(f"Checking {len(channels)} channels for your messages...")
    if single_channel_mode:
        print(f"  Single-channel mode enabled with {channel_delay}s delay between channels")
    
    channel_data = {}
    
    for i, channel in enumerate(channels):
        print(f"  [{i+1}/{len(channels)}] Checking #{channel} for your messages...")
        try:
            # Use history command with full pagination support
            # First get all messages in the channel for the date range
            cmd = f'.venv/bin/python tools/slack_explorer.py history {channel} --from {start_date} --to {end_date} --json'
            result = run_command(cmd, cwd=tools_dir)
            
            if result:
                try:
                    channel_messages = json.loads(result)
                    # Filter for messages from the user
                    user_messages = []
                    if 'messages' in channel_messages:
                        for msg in channel_messages['messages']:
                            # Check if message is from user (by name or user ID)
                            if (msg.get('user_profile', {}).get('real_name', '').lower() == 'sisu xi' or
                                msg.get('user_profile', {}).get('display_name', '').lower() == 'sisu.xi' or
                                'sisu' in msg.get('user_profile', {}).get('real_name', '').lower()):
                                user_messages.append(msg)
                    
                    if user_messages:
                        channel_data[channel] = {
                            'message_count': len(user_messages),
                            'messages': user_messages
                        }
                        print(f"    Found {len(user_messages)} messages from you in #{channel}")
                    else:
                        print(f"    No messages from you in #{channel}")
                except json.JSONDecodeError:
                    print(f"    Warning: Could not parse JSON for #{channel}")
            else:
                print(f"    Warning: No data retrieved for #{channel}")
                
        except Exception as e:
            print(f"    Warning: Failed to collect #{channel} data: {e}")
        
        # Add delay between channels if in single-channel mode
        if single_channel_mode and i < len(channels) - 1:
            print(f"    Waiting {channel_delay}s before next channel...")
            time.sleep(channel_delay)
    
    # Also get direct search for user's messages (as backup/validation)
    print("\n  Running direct search for your messages...")
    cmd = f'.venv/bin/python tools/slack_explorer.py search "from:@sisu.xi" --from "{start_date}" --to "{end_date}" --count 100'
    result = run_command(cmd, cwd=tools_dir)
    if result:
        data['direct_search'] = result
    
    # Get activity summary
    print("  Getting activity summary...")
    cmd = f'.venv/bin/python tools/slack_explorer.py activity --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    if result:
        data['activity_summary'] = result
    
    # Store channel data
    data['channels_with_messages'] = channel_data
    data['total_messages'] = sum(ch['message_count'] for ch in channel_data.values())
    data['active_channels'] = list(channel_data.keys())
    
    output_path = Path(output_dir) / "raw_slack.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"\nSlack data saved to {output_path}")
    print(f"Total messages found: {data['total_messages']} across {len(data['active_channels'])} channels")
    return data


def collect_gmail_data(start_date, end_date, output_dir):
    """Collect Gmail activity data"""
    print("Collecting Gmail data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    try:
        # Calculate days for stats
        days = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days + 1
        
        # Inbox statistics
        cmd = f'.venv/bin/python tools/gmail_explorer.py stats --days {days}'
        result = run_command(cmd, cwd=tools_dir)
        data['stats'] = result if result else ""
        
        # Search for sent emails in date range
        cmd = f'.venv/bin/python tools/gmail_explorer.py search "from:sisu@hebbia.ai after:{start_date} before:{end_date}" --max 50'
        result = run_command(cmd, cwd=tools_dir)
        data['sent_emails'] = result if result else ""
        
        # Search for received emails in date range
        cmd = f'.venv/bin/python tools/gmail_explorer.py search "to:sisu@hebbia.ai after:{start_date} before:{end_date}" --max 100'
        result = run_command(cmd, cwd=tools_dir)
        data['received_emails'] = result if result else ""
        
    except Exception as e:
        print(f"Warning: Some Gmail data collection failed: {e}")
        data['error'] = str(e)
    
    output_path = Path(output_dir) / "raw_gmail.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Gmail data saved to {output_path}")
    return data


def collect_drive_data(start_date, end_date, output_dir):
    """Collect Google Drive activity data"""
    print("Collecting Drive data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    try:
        # Documents I modified in date range
        cmd = f'.venv/bin/python tools/drive_explorer.py recent --from "{start_date}" --to "{end_date}" --max 50'
        result = run_command(cmd, cwd=tools_dir)
        data['modified_docs'] = result if result else ""
        
        # Recent activity
        cmd = f'.venv/bin/python tools/drive_explorer.py activities --from "{start_date}" --to "{end_date}" --max 50'
        result = run_command(cmd, cwd=tools_dir)
        if result:
            data['activity'] = result
        
    except Exception as e:
        print(f"Warning: Some Drive data collection failed: {e}")
        data['error'] = str(e)
    
    output_path = Path(output_dir) / "raw_drive.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Drive data saved to {output_path}")
    return data


def collect_calendar_data(start_date, end_date, output_dir):
    """Collect Calendar activity data"""
    print("Collecting Calendar data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    try:
        # Events in date range
        cmd = f'.venv/bin/python tools/calendar_explorer.py events --from "{start_date}" --to "{end_date}"'
        result = run_command(cmd, cwd=tools_dir)
        data['events'] = result if result else ""
        
        # Summary for the period
        cmd = f'.venv/bin/python tools/calendar_explorer.py summary --from "{start_date}" --to "{end_date}"'
        result = run_command(cmd, cwd=tools_dir)
        data['summary'] = result if result else ""
        
    except Exception as e:
        print(f"Warning: Some Calendar data collection failed: {e}")
        data['error'] = str(e)
    
    output_path = Path(output_dir) / "raw_calendar.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Calendar data saved to {output_path}")
    return data


def collect_linear_data(start_date, end_date, output_dir):
    """Collect Linear activity data"""
    print("Collecting Linear data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    try:
        # Issues assigned to me or created by me in date range
        query = f'{{ issues(filter: {{ OR: [{{ assignee: {{ email: {{ eq: "sisu@hebbia.ai" }} }} }}, {{ creator: {{ email: {{ eq: "sisu@hebbia.ai" }} }} }}], updatedAt: {{ gte: "{start_date}" }} }}, first: 50) {{ nodes {{ identifier title state {{ name }} priority createdAt updatedAt completedAt assignee {{ name }} creator {{ name }} team {{ name }} labels {{ nodes {{ name }} }} }} }} }}'
        cmd = f".venv/bin/python tools/linear_explorer.py '{query}' --urls"
        result = run_command(cmd, cwd=tools_dir)
        data['my_issues'] = result if result else ""
        
        # Issues I completed in date range
        query = f'{{ issues(filter: {{ assignee: {{ email: {{ eq: "sisu@hebbia.ai" }} }}, completedAt: {{ gte: "{start_date}", lte: "{end_date}" }} }}, first: 50) {{ nodes {{ identifier title state {{ name }} priority completedAt team {{ name }} }} }} }}'
        cmd = f".venv/bin/python tools/linear_explorer.py '{query}' --urls"
        result = run_command(cmd, cwd=tools_dir)
        data['completed_issues'] = result if result else ""
        
        # High priority issues I'm involved with
        query = f'{{ issues(filter: {{ OR: [{{ assignee: {{ email: {{ eq: "sisu@hebbia.ai" }} }} }}, {{ creator: {{ email: {{ eq: "sisu@hebbia.ai" }} }} }}], priority: {{ in: [0, 1, 2] }}, state: {{ type: {{ nin: ["completed", "canceled"] }} }} }}, first: 20) {{ nodes {{ identifier title state {{ name }} priority team {{ name }} }} }} }}'
        cmd = f".venv/bin/python tools/linear_explorer.py '{query}' --urls"
        result = run_command(cmd, cwd=tools_dir)
        data['high_priority_issues'] = result if result else ""
        
    except Exception as e:
        print(f"Warning: Some Linear data collection failed: {e}")
        data['error'] = str(e)
    
    output_path = Path(output_dir) / "raw_linear.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Linear data saved to {output_path}")
    return data


def collect_launchdarkly_data(start_date, end_date, output_dir):
    """Collect LaunchDarkly activity data"""
    print("Collecting LaunchDarkly data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    try:
        # Get all flags (we'll filter by date later if possible)
        cmd = '.venv/bin/python tools/launchdarkly_explorer.py flags'
        result = run_command(cmd, cwd=tools_dir)
        data['flags'] = result if result else ""
        
        # Get environments
        cmd = '.venv/bin/python tools/launchdarkly_explorer.py environments'
        result = run_command(cmd, cwd=tools_dir)
        data['environments'] = result if result else ""
        
        # Note: The tool may not support detailed history, so we get what we can
        
    except Exception as e:
        print(f"Warning: Some LaunchDarkly data collection failed: {e}")
        data['error'] = str(e)
    
    output_path = Path(output_dir) / "raw_launchdarkly.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"LaunchDarkly data saved to {output_path}")
    return data


def main():
    """Main execution function with command line argument support"""
    parser = argparse.ArgumentParser(description='Collect raw data for weekly snapshot reports')
    parser.add_argument('--start', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date (YYYY-MM-DD)')
    parser.add_argument('--force', action='store_true', help='Overwrite existing data without prompting')
    parser.add_argument('--channels', nargs='+', help='Specific Slack channels to check')
    parser.add_argument('--single-channel', action='store_true', help='Process Slack channels one at a time to avoid rate limiting')
    parser.add_argument('--channel-delay', type=int, default=1, help='Seconds to wait between Slack channels (default: 1)')
    
    args = parser.parse_args()
    
    # Calculate dates if not provided
    if args.start and args.end:
        start_date = args.start
        end_date = args.end
        # Create folder name from dates
        folder_name = f"{start_date.replace('-', '')}-{end_date.replace('-', '')}"
    else:
        # Use calculate_week.py to get the folder and dates
        result = subprocess.run(['python3', 'calculate_week.py'], capture_output=True, text=True)
        if result.returncode != 0:
            print("Error: Failed to calculate week")
            sys.exit(1)
        folder_name = result.stdout.strip()
        
        # Parse dates from folder name (YYYYMMDD-YYYYMMDD)
        parts = folder_name.split('-')
        start_date = f"{parts[0][:4]}-{parts[0][4:6]}-{parts[0][6:8]}"
        end_date = f"{parts[1][:4]}-{parts[1][4:6]}-{parts[1][6:8]}"
    
    print(f"Collecting data for: {start_date} to {end_date}")
    print(f"Output folder: {folder_name}")
    
    # Check if folder exists
    output_dir = Path(folder_name)
    if output_dir.exists() and not args.force:
        response = input(f"Folder {folder_name} already exists. Overwrite? (y/n): ")
        if response.lower() != 'y':
            print("Aborted")
            sys.exit(0)
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Track collection status
    success = True
    
    # Collect data from all sources
    try:
        collect_github_data(start_date, end_date, output_dir)
    except Exception as e:
        print(f"ERROR: GitHub collection failed: {e}")
        success = False
    
    try:
        collect_slack_data(start_date, end_date, output_dir, 
                          channels=args.channels,
                          single_channel_mode=args.single_channel,
                          channel_delay=args.channel_delay)
    except Exception as e:
        print(f"ERROR: Slack collection failed: {e}")
        success = False
    
    try:
        collect_gmail_data(start_date, end_date, output_dir)
    except Exception as e:
        print(f"ERROR: Gmail collection failed: {e}")
        success = False
    
    try:
        collect_drive_data(start_date, end_date, output_dir)
    except Exception as e:
        print(f"ERROR: Drive collection failed: {e}")
        success = False
    
    try:
        collect_calendar_data(start_date, end_date, output_dir)
    except Exception as e:
        print(f"ERROR: Calendar collection failed: {e}")
        success = False
    
    try:
        collect_linear_data(start_date, end_date, output_dir)
    except Exception as e:
        print(f"ERROR: Linear collection failed: {e}")
        success = False
    
    try:
        collect_launchdarkly_data(start_date, end_date, output_dir)
    except Exception as e:
        print(f"ERROR: LaunchDarkly collection failed: {e}")
        success = False
    
    if success:
        print(f"\n✅ All data collection completed successfully!")
        print(f"📁 Data saved in: {output_dir}")
    else:
        print(f"\n⚠️  Some data collection failed. Check the errors above.")
        print(f"📁 Partial data saved in: {output_dir}")
        sys.exit(1)


if __name__ == "__main__":
    main()