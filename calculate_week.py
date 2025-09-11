#!/usr/bin/env python3
"""
Calculate the previous week's date range (Sunday-Saturday) for weekly reports.
Returns the folder name in YYYYMMDD-YYYYMMDD format.
"""

from datetime import datetime, timedelta
import sys

def get_previous_week():
    """Calculate previous week's Sunday-Saturday range."""
    today = datetime.now()
    
    # Find days since last Sunday (0=Monday, 6=Sunday)
    days_since_sunday = (today.weekday() + 1) % 7
    if days_since_sunday == 0:  # If today is Sunday
        days_since_sunday = 7  # Go to previous Sunday
    
    # Get previous week's Sunday
    last_sunday = today - timedelta(days=days_since_sunday + 7)
    last_saturday = last_sunday + timedelta(days=6)
    
    return last_sunday, last_saturday

def main():
    last_sunday, last_saturday = get_previous_week()
    
    # Format as YYYYMMDD-YYYYMMDD
    folder_name = f"{last_sunday.strftime('%Y%m%d')}-{last_saturday.strftime('%Y%m%d')}"
    
    if len(sys.argv) > 1 and sys.argv[1] == "--verbose":
        print(f"Today: {datetime.now().strftime('%Y-%m-%d %A')}")
        print(f"Previous week: {last_sunday.strftime('%Y-%m-%d %A')} to {last_saturday.strftime('%Y-%m-%d %A')}")
        print(f"Folder: {folder_name}")
    else:
        print(folder_name)

if __name__ == "__main__":
    main()