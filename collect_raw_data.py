#!/usr/bin/env python3
"""
Raw Data Collector for Weekly Snapshot Reports
Collects data from GitHub, Slack, Gmail, Drive, Calendar, Linear, and LaunchDarkly
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
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
    
    # PRs created in Hebbia org
    cmd = f'gh search prs --author=sisuxi --created=">={start_date}" "org:hebbia" --json number,title,state,createdAt,updatedAt,url,repository,labels'
    result = run_command(cmd)
    if result:
        try:
            data['prs_created'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_created'] = []
    
    # PRs reviewed in Hebbia org
    cmd = f'gh search prs --reviewed-by=sisuxi --updated=">={start_date}" "org:hebbia" --json number,title,author,url,repository'
    result = run_command(cmd)
    if result:
        try:
            data['prs_reviewed'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_reviewed'] = []
    
    # PRs involved in Hebbia org
    cmd = f'gh search prs --involves=sisuxi --updated=">={start_date}" "org:hebbia" --json number,title,repository,author'
    result = run_command(cmd)
    if result:
        try:
            data['prs_involved'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_involved'] = []
    
    # Commits in all Hebbia repos (recent, will filter by date later)
    cmd = f'gh search commits --author=sisuxi "org:hebbia" --limit 100 --json sha,commit,repository'
    result = run_command(cmd)
    if result:
        try:
            commits_data = json.loads(result)
            # Filter commits by date
            filtered_commits = []
            for commit_item in commits_data:
                commit_date = commit_item.get('commit', {}).get('author', {}).get('date', '')
                if commit_date and commit_date >= start_date:
                    filtered_commits.append(commit_item)
            data['commits'] = filtered_commits
        except json.JSONDecodeError:
            data['commits'] = []
    
    # Team PRs reviewed across all Hebbia repos (using search to get all)
    cmd = f'gh search prs --reviewed-by=sisuxi --created=">={start_date}" "org:hebbia" --limit 100 --json number,title,author,repository,createdAt,state'
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


def collect_slack_data(start_date, end_date, output_dir):
    """Collect Slack activity data"""
    print("Collecting Slack data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    # Messages from me
    cmd = f'.venv/bin/python tools/slack_explorer.py search "from:@sisu" --from "{start_date}" --to "{end_date}" --count 50'
    result = run_command(cmd, cwd=tools_dir)
    if result is None:
        raise Exception("Failed to collect Slack messages")
    data['messages_from_me'] = result
    
    # Activity summary
    cmd = f'.venv/bin/python tools/slack_explorer.py activity --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    if result is None:
        raise Exception("Failed to collect Slack activity summary")
    data['activity_summary'] = result
    
    output_path = Path(output_dir) / "raw_slack.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Slack data saved to {output_path}")
    return data


def collect_gmail_data(start_date, end_date, output_dir):
    """Collect Gmail activity data"""
    print("Collecting Gmail data...")
    data = {}
    tools_dir = Path.home() / "Hebbia" / "sisu-tools"
    
    try:
        # Inbox statistics (using days parameter)
        days = (datetime.fromisoformat(end_date) - datetime.fromisoformat(start_date)).days + 1
        cmd = f'.venv/bin/python tools/gmail_explorer.py stats --days {days}'
        result = run_command(cmd, cwd=tools_dir)
        data['stats'] = result if result else ""
        
        # Sent emails
        cmd = f'.venv/bin/python tools/gmail_explorer.py sent --days {days}'
        result = run_command(cmd, cwd=tools_dir)
        data['sent'] = result if result else ""
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
        # Recent documents
        cmd = '.venv/bin/python tools/drive_explorer.py recent'
        result = run_command(cmd, cwd=tools_dir)
        data['recent'] = result if result else ""
        
        # Shared documents
        cmd = '.venv/bin/python tools/drive_explorer.py shared'
        result = run_command(cmd, cwd=tools_dir)
        data['shared'] = result if result else ""
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
        # All events
        cmd = '.venv/bin/python tools/calendar_explorer.py events'
        result = run_command(cmd, cwd=tools_dir)
        data['events'] = result if result else ""
        
        # Meeting analysis
        cmd = '.venv/bin/python tools/calendar_explorer.py analyze'
        result = run_command(cmd, cwd=tools_dir)
        data['analysis'] = result if result else ""
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
        # My assigned issues
        query = '{ issues(filter: { assignee: { email: { eq: "sisu@hebbia.ai" } } }, first: 100) { nodes { identifier title state { name } priority createdAt updatedAt team { name } } } }'
        cmd = f".venv/bin/python tools/linear_explorer.py '{query}' --from '{start_date}' --to '{end_date}' --urls"
        result = run_command(cmd, cwd=tools_dir)
        data['my_issues'] = result if result else ""
        
        # High priority issues
        query = '{ issues(filter: { assignee: { email: { eq: "sisu@hebbia.ai" } }, priority: { in: [0, 1] } }, first: 50) { nodes { identifier title state { name } priority team { name } } } }'
        cmd = f".venv/bin/python tools/linear_explorer.py '{query}' --from '{start_date}' --to '{end_date}'"
        result = run_command(cmd, cwd=tools_dir)
        data['high_priority'] = result if result else ""
        
        # Issues I created
        query = '{ issues(filter: { creator: { email: { eq: "sisu@hebbia.ai" } } }, first: 50) { nodes { identifier title state { name } createdAt team { name } } } }'
        cmd = f".venv/bin/python tools/linear_explorer.py '{query}' --from '{start_date}' --to '{end_date}'"
        result = run_command(cmd, cwd=tools_dir)
        data['created'] = result if result else ""
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
        # Get flags list
        cmd = '.venv/bin/python tools/launchdarkly_explorer.py flags'
        result = run_command(cmd, cwd=tools_dir)
        data['flags'] = result if result else ""
        
        # Get environments
        cmd = '.venv/bin/python tools/launchdarkly_explorer.py environments'
        result = run_command(cmd, cwd=tools_dir)
        data['environments'] = result if result else ""
        
        # Get projects
        cmd = '.venv/bin/python tools/launchdarkly_explorer.py projects'
        result = run_command(cmd, cwd=tools_dir)
        data['projects'] = result if result else ""
    except Exception as e:
        print(f"Warning: Some LaunchDarkly data collection failed: {e}")
        data['error'] = str(e)
    
    output_path = Path(output_dir) / "raw_launchdarkly.json"
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"LaunchDarkly data saved to {output_path}")
    return data


def calculate_week_dates(date_str=None):
    """Calculate Sunday-Saturday date range for the previous week or custom date"""
    if date_str:
        # Parse custom date
        target_date = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        # Use today's date
        target_date = datetime.now()
    
    # Calculate last Sunday
    days_since_sunday = (target_date.weekday() + 1) % 7
    last_sunday = target_date - timedelta(days=days_since_sunday + 7)
    last_saturday = last_sunday + timedelta(days=6)
    
    return last_sunday.strftime("%Y-%m-%d"), last_saturday.strftime("%Y-%m-%d")


def main():
    parser = argparse.ArgumentParser(description='Collect raw data for weekly snapshot report')
    parser.add_argument('--start', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end', help='End date (YYYY-MM-DD)')
    parser.add_argument('--date', help='Calculate week containing this date (YYYY-MM-DD)')
    parser.add_argument('--output', help='Output directory (default: YYYYMMDD-YYYYMMDD)')
    args = parser.parse_args()
    
    # Determine date range
    if args.start and args.end:
        start_date = args.start
        end_date = args.end
    elif args.date:
        start_date, end_date = calculate_week_dates(args.date)
    else:
        # Default to previous week
        start_date, end_date = calculate_week_dates()
    
    print(f"Collecting data for {start_date} to {end_date}")
    
    # Create output directory
    if args.output:
        output_dir = args.output
    else:
        start_fmt = start_date.replace('-', '')
        end_fmt = end_date.replace('-', '')
        output_dir = f"{start_fmt}-{end_fmt}"
    
    # Check if directory exists
    if os.path.exists(output_dir):
        response = input(f"\nFolder {output_dir} already exists. What would you like to do?\n"
                        "1. Delete and regenerate everything (default - press Enter)\n"
                        "2. Keep existing data and exit\n"
                        "3. Cancel operation\n"
                        "Choice [1]: ")
        
        if response == "" or response == "1":
            import shutil
            shutil.rmtree(output_dir)
            os.makedirs(output_dir)
            print(f"Deleted and recreated {output_dir}")
        elif response == "2":
            print(f"Keeping existing data in {output_dir}")
            return
        else:
            print("Operation cancelled")
            sys.exit(0)
    else:
        os.makedirs(output_dir)
        print(f"Created directory {output_dir}")
    
    # Collect data in parallel
    collectors = [
        ('GitHub', collect_github_data),
        ('Slack', collect_slack_data),
        ('Gmail', collect_gmail_data),
        ('Drive', collect_drive_data),
        ('Calendar', collect_calendar_data),
        ('Linear', collect_linear_data),
        ('LaunchDarkly', collect_launchdarkly_data),
    ]
    
    print("\nStarting parallel data collection...")
    failed_collectors = []
    
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {}
        for name, collector_func in collectors:
            future = executor.submit(collector_func, start_date, end_date, output_dir)
            futures[future] = name
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                print(f"✅ {name} collection completed")
            except Exception as e:
                print(f"❌ {name} collection failed: {e}")
                failed_collectors.append(name)
    
    # Check if any collectors failed
    if failed_collectors:
        print(f"\n❌ Data collection failed for: {', '.join(failed_collectors)}")
        print(f"Exiting with error code 1")
        sys.exit(1)
    
    print(f"\n✅ All data collection completed successfully!")
    print(f"📁 Raw data saved in: {output_dir}/")
    print(f"   - raw_github.json")
    print(f"   - raw_slack.json")
    print(f"   - raw_gmail.json")
    print(f"   - raw_drive.json")
    print(f"   - raw_calendar.json")
    print(f"   - raw_linear.json")
    print(f"   - raw_launchdarkly.json")
    print(f"\nYou can now run the report generation process to create the final report.")


if __name__ == "__main__":
    main()