#!/usr/bin/env python3
"""
Garmin Timezone Sync - Auto-update cron jobs when timezone changes
Checks Garmin API for current timezone and updates cron schedules accordingly
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from garminconnect import Garmin
except ImportError:
    print("Error: garminconnect not installed. Run: pip install garminconnect")
    sys.exit(1)


class TimezoneSyncer:
    def __init__(self, config_path="config.json"):
        """Initialize timezone syncer."""
        self.config_path = Path(__file__).parent / config_path
        self.config = self.load_config()
        self.client = None
    
    def load_config(self):
        """Load configuration from JSON file."""
        if not self.config_path.exists():
            print(f"Error: Config file not found: {self.config_path}")
            sys.exit(1)
        
        with open(self.config_path) as f:
            return json.load(f)
    
    def save_config(self):
        """Save updated configuration."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def connect(self):
        """Connect to Garmin Connect using tokens."""
        garmin_config = self.config.get("garmin", {})
        tokens = garmin_config.get("tokens")
        
        if not tokens:
            print("Error: No tokens in config.json")
            print("Run: python generate_tokens.py")
            return False
        
        try:
            self.client = Garmin()
            self.client.garth.loads(tokens)
            return True
        except Exception as e:
            print(f"Error connecting to Garmin: {e}")
            return False
    
    def get_garmin_timezone(self):
        """Get current timezone from Garmin API."""
        if not self.client:
            if not self.connect():
                return None
        
        try:
            settings = self.client.get_userprofile_settings()
            tz = settings.get('timeZone')
            print(f"📍 Garmin timezone: {tz}")
            return tz
        except Exception as e:
            print(f"Error getting timezone: {e}")
            return None
    
    def timezone_changed(self, new_tz):
        """Check if timezone has changed."""
        old_tz = self.config.get('timezone')
        
        if old_tz != new_tz:
            print(f"⚠️  Timezone changed: {old_tz} → {new_tz}")
            return True
        else:
            print(f"✅ Timezone unchanged: {new_tz}")
            return False
    
    def update_config_timezone(self, new_tz):
        """Update timezone in config."""
        self.config['timezone'] = new_tz
        self.save_config()
        print(f"✅ Updated config timezone: {new_tz}")
    
    def convert_time_to_timezone(self, hour, minute, from_tz, to_tz):
        """Convert time from one timezone to another, return cron hour/minute in UTC."""
        # Create a datetime in the target timezone
        now = datetime.now(ZoneInfo(to_tz))
        target_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Convert to UTC for cron (cron runs in UTC on most systems)
        utc_time = target_time.astimezone(ZoneInfo('UTC'))
        
        return utc_time.hour, utc_time.minute
    
    def update_cron_jobs(self, new_tz):
        """Update cron jobs to match new timezone."""
        print(f"\n🔄 Updating cron jobs for timezone: {new_tz}")
        
        # Define desired local times (in user's timezone)
        jobs = [
            {
                "id": "garmin-morning",
                "name": "Garmin Morning Sync",
                "local_hour": 6,
                "local_minute": 30,
                "description": "Morning sync (overnight sleep + yesterday final)"
            },
            {
                "id": "garmin-noon",
                "name": "Garmin Noon Sync",
                "local_hour": 12,
                "local_minute": 0,
                "description": "Midday check (morning activity)"
            },
            {
                "id": "garmin-evening",
                "name": "Garmin Evening Sync",
                "local_hour": 21,
                "local_minute": 0,
                "description": "Evening sync (full day data)"
            }
        ]
        
        # Convert to UTC and create cron expressions
        updated_jobs = []
        for job in jobs:
            utc_hour, utc_minute = self.convert_time_to_timezone(
                job['local_hour'], 
                job['local_minute'],
                'UTC',  # from timezone (not used in our convert function)
                new_tz   # to timezone
            )
            
            cron_schedule = f"{utc_minute} {utc_hour} * * *"
            
            updated_jobs.append({
                "id": job['id'],
                "name": job['name'],
                "schedule": cron_schedule,
                "action": {
                    "type": "exec",
                    "command": "python3",
                    "args": [
                        "~/.npm-global/lib/node_modules/clawdbot/skills/garmin/fetch_garmin.py"
                    ]
                },
                "enabled": True
            })
            
            print(f"  ✅ {job['name']}: {job['local_hour']:02d}:{job['local_minute']:02d} {new_tz} → {cron_schedule} UTC")
        
        # Output JSON for Clawdbot to apply
        output = {
            "timezone": new_tz,
            "updated_at": datetime.now().isoformat(),
            "jobs": updated_jobs
        }
        
        # Save to file for Clawdbot to read
        output_file = Path(__file__).parent / "cron_update.json"
        with open(output_file, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\n✅ Cron update saved to: {output_file}")
        print("\n⚠️  Note: Clawdbot will need to apply these changes using the gateway cron tool")
        
        return output
    
    def sync(self, force_update=False):
        """Main sync function - check timezone and update if needed."""
        print("🔍 Checking Garmin timezone...")
        
        # Get current timezone from Garmin API
        new_tz = self.get_garmin_timezone()
        if not new_tz:
            print("❌ Failed to get timezone from Garmin")
            return False
        
        # Check if timezone changed
        changed = self.timezone_changed(new_tz)
        
        if changed or force_update:
            # Update config
            self.update_config_timezone(new_tz)
            
            # Update cron jobs
            self.update_cron_jobs(new_tz)
            
            print("\n✅ Timezone sync complete!")
            return True
        else:
            print("\n✅ No changes needed")
            return False


def main():
    parser = argparse.ArgumentParser(description="Sync Garmin timezone and update cron jobs")
    parser.add_argument("--force", action="store_true", help="Force update even if timezone unchanged")
    parser.add_argument("--config", default="config.json", help="Config file path")
    
    args = parser.parse_args()
    
    syncer = TimezoneSyncer(config_path=args.config)
    syncer.sync(force_update=args.force)


if __name__ == "__main__":
    main()
