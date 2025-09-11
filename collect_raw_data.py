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
            timeout=60
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
    cmd = "gh auth status --hostname github.com 2>&1 | grep 'Logged in to github.com as sisuxi'"
    auth_check = run_command(cmd)
    if not auth_check:
        print("Warning: GitHub auth verification failed")
    
    # PRs created
    cmd = f'gh search prs --author=sisuxi --created=">={start_date}" --json number,title,state,createdAt,updatedAt,url,repository,labels,comments'
    result = run_command(cmd)
    if result:
        try:
            data['prs_created'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_created'] = []
    
    # PRs reviewed
    cmd = f'gh search prs --reviewed-by=sisuxi --updated=">={start_date}" --json number,title,author,url,reviews'
    result = run_command(cmd)
    if result:
        try:
            data['prs_reviewed'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_reviewed'] = []
    
    # PRs involved
    cmd = f'gh search prs --involves=sisuxi --updated=">={start_date}" --json number,title,repository,author'
    result = run_command(cmd)
    if result:
        try:
            data['prs_involved'] = json.loads(result)
        except json.JSONDecodeError:
            data['prs_involved'] = []
    
    # Commits
    cmd = f'gh search commits --author=sisuxi --repo=hebbia/mono --committer-date=">={start_date}..{end_date}" --json sha,commit'
    result = run_command(cmd)
    if result:
        try:
            data['commits'] = json.loads(result)
        except json.JSONDecodeError:
            data['commits'] = []
    
    # Team member PRs reviewed
    cmd = f'gh pr list --repo hebbia/mono --state all --limit 100 --json number,author,createdAt,reviews'
    result = run_command(cmd)
    if result:
        try:
            all_prs = json.loads(result)
            # Filter for PRs created after start_date with reviews by sisuxi
            team_prs = []
            for pr in all_prs:
                if pr.get('createdAt', '') >= start_date:
                    for review in pr.get('reviews', []):
                        if review.get('author', {}).get('login') == 'sisuxi':
                            team_prs.append(pr)
                            break
            data['team_prs_reviewed'] = team_prs
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
    cmd = f'.venv/bin/python tools/slack_explorer.py search "from:@sisu" --from "{start_date}" --to "{end_date}" --count 100'
    result = run_command(cmd, cwd=tools_dir)
    data['messages_from_me'] = result if result else ""
    
    # Engineering/architecture channels
    cmd = f'.venv/bin/python tools/slack_explorer.py search "from:@sisu in:#engineering OR in:#architecture OR in:#platform" --from "{start_date}" --to "{end_date}" --count 50'
    result = run_command(cmd, cwd=tools_dir)
    data['engineering_channels'] = result if result else ""
    
    # Activity summary
    cmd = f'.venv/bin/python tools/slack_explorer.py activity --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['activity_summary'] = result if result else ""
    
    # Incident responses
    cmd = f'.venv/bin/python tools/slack_explorer.py search "from:@sisu in:#incidents OR in:#alerts" --from "{start_date}" --to "{end_date}" --count 20'
    result = run_command(cmd, cwd=tools_dir)
    data['incident_responses'] = result if result else ""
    
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
    
    # Inbox statistics
    cmd = f'.venv/bin/python tools/gmail_explorer.py stats --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['stats'] = result if result else ""
    
    # Important emails
    cmd = f'.venv/bin/python tools/gmail_explorer.py important --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['important'] = result if result else ""
    
    # Sent emails
    cmd = f'.venv/bin/python tools/gmail_explorer.py sent --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['sent'] = result if result else ""
    
    # Detailed export
    cmd = f'.venv/bin/python tools/gmail_explorer.py export --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    if result:
        try:
            data['export'] = json.loads(result)
        except json.JSONDecodeError:
            data['export'] = result
    
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
    
    # Recent documents
    cmd = f'.venv/bin/python tools/drive_explorer.py recent --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['recent'] = result if result else ""
    
    # Shared documents
    cmd = f'.venv/bin/python tools/drive_explorer.py shared --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['shared'] = result if result else ""
    
    # Search for Hebbia documents
    cmd = f'.venv/bin/python tools/drive_explorer.py search "hebbia" --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['hebbia_docs'] = result if result else ""
    
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
    
    # All events
    cmd = f'.venv/bin/python tools/calendar_explorer.py events --from "{start_date}" --to "{end_date}" --json'
    result = run_command(cmd, cwd=tools_dir)
    if result:
        try:
            data['events'] = json.loads(result)
        except json.JSONDecodeError:
            data['events'] = result
    
    # Meeting analysis
    cmd = f'.venv/bin/python tools/calendar_explorer.py analyze --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['analysis'] = result if result else ""
    
    # 1:1 meetings
    cmd = f'.venv/bin/python tools/calendar_explorer.py search "1:1" --from "{start_date}" --to "{end_date}"'
    result = run_command(cmd, cwd=tools_dir)
    data['one_on_ones'] = result if result else ""
    
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
    
    # High-priority issues (P0/P1)
    query = '''query { issues(filter: { OR: [{assignee: { email: { eq: "sisu@hebbia.ai" } }}, {creator: { email: { eq: "sisu@hebbia.ai" } }}], priority: { in: [0, 1] } }, first: 50) { nodes { identifier title state { name } priority updatedAt team { name } } } }'''
    cmd = f'.venv/bin/python tools/linear_explorer.py --from "{start_date}" --to "{end_date}" --urls \'{query}\''
    result = run_command(cmd, cwd=tools_dir)
    data['high_priority'] = result if result else ""
    
    # Cross-team issues
    query = '''query { issues(filter: { OR: [{assignee: { email: { eq: "sisu@hebbia.ai" } }}, {subscribers: { email: { eq: "sisu@hebbia.ai" } }}] }, first: 50) { nodes { identifier title state { name } priority team { name } parent { identifier title } children { nodes { identifier title } } } } }'''
    cmd = f'.venv/bin/python tools/linear_explorer.py --from "{start_date}" --to "{end_date}" --urls \'{query}\''
    result = run_command(cmd, cwd=tools_dir)
    data['cross_team'] = result if result else ""
    
    # Technical debt and architecture
    query = '''query { issues(filter: { labels: { name: { in: ["tech-debt", "architecture", "performance"] } }, OR: [{assignee: { email: { eq: "sisu@hebbia.ai" } }}, {creator: { email: { eq: "sisu@hebbia.ai" } }}] }, first: 50) { nodes { identifier title state { name } labels { nodes { name } } team { name } } } }'''
    cmd = f'.venv/bin/python tools/linear_explorer.py --from "{start_date}" --to "{end_date}" --urls \'{query}\''
    result = run_command(cmd, cwd=tools_dir)
    data['tech_debt'] = result if result else ""
    
    # Completed issues
    query = '''query { issues(filter: { assignee: { email: { eq: "sisu@hebbia.ai" } }, state: { type: { eq: "completed" } } }, first: 50) { nodes { identifier title completedAt team { name } priority } } }'''
    cmd = f'.venv/bin/python tools/linear_explorer.py --from "{start_date}" --to "{end_date}" --urls \'{query}\''
    result = run_command(cmd, cwd=tools_dir)
    data['completed'] = result if result else ""
    
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
    
    # Audit log
    cmd = '.venv/bin/python tools/launchdarkly_explorer.py query "/auditlog" --params \'{"limit": 100}\''
    result = run_command(cmd, cwd=tools_dir)
    if result:
        try:
            audit_data = json.loads(result)
            # Filter by date
            start_ts = datetime.fromisoformat(start_date).timestamp() * 1000
            filtered = [item for item in audit_data.get('items', []) if item.get('date', 0) >= start_ts]
            data['audit_log'] = filtered
        except (json.JSONDecodeError, ValueError):
            data['audit_log'] = result
    
    # My changes
    cmd = '.venv/bin/python tools/launchdarkly_explorer.py query "/auditlog" --params \'{"limit": 100}\''
    result = run_command(cmd, cwd=tools_dir)
    if result:
        try:
            audit_data = json.loads(result)
            my_changes = [item for item in audit_data.get('items', []) 
                         if item.get('member', {}).get('email') == 'sisu@hebbia.ai']
            data['my_changes'] = my_changes
        except json.JSONDecodeError:
            data['my_changes'] = []
    
    # Production flags
    cmd = '.venv/bin/python tools/launchdarkly_explorer.py flags --env production --limit 100'
    result = run_command(cmd, cwd=tools_dir)
    if result:
        try:
            data['production_flags'] = json.loads(result)
        except json.JSONDecodeError:
            data['production_flags'] = result
    
    # Team-specific flags
    cmd = '.venv/bin/python tools/launchdarkly_explorer.py flags'
    result = run_command(cmd, cwd=tools_dir)
    if result:
        try:
            flags_data = json.loads(result)
            team_flags = []
            for flag in flags_data.get('items', []):
                tags = flag.get('tags', [])
                if 'matrix' in tags or 'epd' in tags:
                    team_flags.append(flag)
            data['team_flags'] = team_flags
        except json.JSONDecodeError:
            data['team_flags'] = []
    
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
    
    print(f"\n✅ All data collection completed!")
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