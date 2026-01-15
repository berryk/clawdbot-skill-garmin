#!/usr/bin/env python3
"""
Add Manual Waist Measurement to Garmin Data
Allows adding waist measurements for specific dates
"""

import csv
import sys
from datetime import datetime
from pathlib import Path

def update_waist_measurement(csv_file, date, waist_inches):
    """Update waist measurement for a specific date."""
    
    # Convert to cm as well
    waist_cm = round(waist_inches * 2.54, 1)
    
    # Read all data
    rows = []
    headers = []
    updated = False
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        
        # Add waist columns if they don't exist
        if 'waist_inches' not in headers:
            headers = list(headers)
            # Insert waist measurements after body composition data
            insert_index = headers.index('weight_date') + 1 if 'weight_date' in headers else len(headers) - 2
            headers.insert(insert_index, 'waist_inches')
            headers.insert(insert_index + 1, 'waist_cm')
            headers.insert(insert_index + 2, 'waist_date')
        
        for row in reader:
            # Initialize waist columns if they don't exist
            if 'waist_inches' not in row:
                row['waist_inches'] = ''
                row['waist_cm'] = ''
                row['waist_date'] = ''
            
            # Update the matching date
            if row['date'] == date:
                row['waist_inches'] = waist_inches
                row['waist_cm'] = waist_cm
                row['waist_date'] = date
                updated = True
                print(f"✅ Updated {date}: {waist_inches} inches ({waist_cm} cm)")
            
            rows.append(row)
    
    if not updated:
        print(f"⚠️  Date {date} not found in CSV. Available dates:")
        for row in rows[-7:]:  # Show last 7 days
            print(f"   - {row['date']}")
        return False
    
    # Write back to CSV
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ CSV updated: {csv_file}")
    return True

def main():
    if len(sys.argv) < 3:
        print("Usage: python add_waist_measurement.py <date> <waist_inches>")
        print("")
        print("Examples:")
        print("  python add_waist_measurement.py 2026-01-15 34.5")
        print("  python add_waist_measurement.py today 34.5")
        print("")
        print("Or run interactively:")
        print("  python add_waist_measurement.py")
        print("")
        
        # Interactive mode
        date_input = input("Date (YYYY-MM-DD or 'today'): ").strip()
        waist_input = input("Waist measurement (inches): ").strip()
        
        if not date_input or not waist_input:
            print("❌ Date and waist measurement required")
            sys.exit(1)
    else:
        date_input = sys.argv[1]
        waist_input = sys.argv[2]
    
    # Parse date
    if date_input.lower() == 'today':
        date = datetime.now().date().isoformat()
    else:
        try:
            date = datetime.strptime(date_input, "%Y-%m-%d").date().isoformat()
        except ValueError:
            print(f"❌ Invalid date format: {date_input}")
            print("Use YYYY-MM-DD or 'today'")
            sys.exit(1)
    
    # Parse waist measurement
    try:
        waist_inches = float(waist_input)
        if waist_inches < 20 or waist_inches > 60:
            print(f"⚠️  Unusual waist measurement: {waist_inches} inches")
            confirm = input("Continue? (y/N): ").strip().lower()
            if confirm != 'y':
                sys.exit(0)
    except ValueError:
        print(f"❌ Invalid waist measurement: {waist_input}")
        sys.exit(1)
    
    # Update CSV
    csv_file = Path.home() / "clawd" / "fitness" / "garmin_data.csv"
    
    if not csv_file.exists():
        print(f"❌ CSV file not found: {csv_file}")
        print("Run fetch_garmin.py first to create the CSV")
        sys.exit(1)
    
    success = update_waist_measurement(csv_file, date, waist_inches)
    
    if success:
        print("")
        print("💡 Tip: For Clawdbot, you can just tell me:")
        print(f'   "My waist is {waist_inches} inches today"')
        print("   and I\'ll add it automatically!")

if __name__ == "__main__":
    main()
