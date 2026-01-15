#!/usr/bin/env python3
"""
Garmin Connect Data Fetcher for Clawdbot
Fetches fitness data from Garmin Connect and stores in CSV format
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import csv

try:
    from garminconnect import Garmin, GarminConnectConnectionError, GarminConnectAuthenticationError
except ImportError:
    print("Error: garminconnect not installed. Run: pip install garminconnect")
    sys.exit(1)


class GarminDataFetcher:
    def __init__(self, config_path="config.json"):
        """Initialize Garmin data fetcher."""
        self.config = self.load_config(config_path)
        self.data_dir = Path(os.path.expanduser(self.config.get("data_dir", "~/clawd/fitness")))
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.csv_file = self.data_dir / "garmin_data.csv"
        self.cache_file = self.data_dir / "garmin_last_pull.json"
        self.summary_file = self.data_dir / "garmin_summary.md"
        
        self.client = None
    
    def load_config(self, config_path):
        """Load configuration from JSON file."""
        config_file = Path(__file__).parent / config_path
        
        if not config_file.exists():
            print(f"Error: Config file not found: {config_file}")
            print("Create config.json with your Garmin credentials.")
            sys.exit(1)
        
        with open(config_file) as f:
            return json.load(f)
    
    def connect(self):
        """Connect to Garmin Connect using tokens or credentials."""
        garmin_config = self.config.get("garmin", {})
        email = garmin_config.get("email")
        password = garmin_config.get("password")
        tokens = garmin_config.get("tokens")
        
        # Try token-based auth first (no MFA needed!)
        if tokens:
            try:
                print("🔐 Connecting to Garmin Connect (using saved tokens)...")
                self.client = Garmin()
                self.client.garth.loads(tokens)
                self.client.display_name = self.client.garth.profile.get("displayName", "User")
                print(f"✅ Connected as: {self.client.display_name}")
                return True
            except Exception as e:
                print(f"⚠️  Saved tokens failed: {e}")
                print("Falling back to password authentication...")
        
        # Fallback to password auth (may require MFA)
        if not email or not password:
            print("❌ Error: No valid tokens and no credentials in config.json")
            print("Run: python generate_tokens.py")
            sys.exit(1)
        
        try:
            print("🔐 Connecting to Garmin Connect (using credentials)...")
            print("⚠️  Note: If you have MFA enabled, this may fail.")
            print("    Run 'python generate_tokens.py' instead to handle MFA.")
            self.client = Garmin(email, password)
            self.client.login()
            print("✅ Connected successfully!")
            return True
        except GarminConnectAuthenticationError as e:
            print(f"❌ Authentication failed: {e}")
            print("\n💡 Tip: Run 'python generate_tokens.py' to handle MFA and save tokens")
            return False
        except GarminConnectConnectionError as e:
            print(f"❌ Connection error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False
    
    def fetch_daily_stats(self, date=None):
        """Fetch stats for a specific date."""
        if date is None:
            date = datetime.now().date()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        
        print(f"📊 Fetching data for {date}...")
        
        try:
            # Get daily summary
            summary = self.client.get_stats(date.isoformat())
            
            # Get sleep data
            sleep_data = self.client.get_sleep_data(date.isoformat())
            
            # Get heart rate data
            hr_data = self.client.get_heart_rates(date.isoformat())
            
            # Get stress data
            stress_data = self.client.get_stress_data(date.isoformat())
            
            # Compile daily stats
            stats = {
                "date": date.isoformat(),
                "steps": summary.get("totalSteps", 0),
                "distance_km": round(summary.get("totalDistanceMeters", 0) / 1000, 2),
                "calories": summary.get("activeKilocalories", 0) + summary.get("bmrKilocalories", 0),
                "active_minutes": summary.get("activeTime", 0) // 60 if summary.get("activeTime") else 0,
                "floors": summary.get("floorsAscended", 0),
                
                # Heart rate
                "resting_hr": hr_data.get("restingHeartRate", None) if hr_data else None,
                "max_hr": hr_data.get("maxHeartRate", None) if hr_data else None,
                "avg_hr": hr_data.get("averageHeartRate", None) if hr_data else None,
                
                # Sleep
                "sleep_hours": round(sleep_data.get("dailySleepDTO", {}).get("sleepTimeSeconds", 0) / 3600, 1) if sleep_data else None,
                "sleep_score": sleep_data.get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value", None) if sleep_data else None,
                "deep_sleep_minutes": sleep_data.get("dailySleepDTO", {}).get("deepSleepSeconds", 0) // 60 if sleep_data else None,
                "light_sleep_minutes": sleep_data.get("dailySleepDTO", {}).get("lightSleepSeconds", 0) // 60 if sleep_data else None,
                "rem_sleep_minutes": sleep_data.get("dailySleepDTO", {}).get("remSleepSeconds", 0) // 60 if sleep_data else None,
                
                # Stress
                "stress_avg": stress_data.get("averageStressLevel", None) if stress_data else None,
                "stress_max": stress_data.get("maxStressLevel", None) if stress_data else None,
                
                # Body battery (if available)
                "body_battery": summary.get("bodyBatteryHighestValue", None),
                
                # Timestamp
                "fetched_at": datetime.now().isoformat()
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error fetching data for {date}: {e}")
            return None
    
    def save_to_csv(self, stats):
        """Save stats to CSV file (append mode)."""
        if not stats:
            return False
        
        # Define CSV columns
        columns = [
            "date", "steps", "distance_km", "calories", "active_minutes", "floors",
            "resting_hr", "max_hr", "avg_hr",
            "sleep_hours", "sleep_score", "deep_sleep_minutes", "light_sleep_minutes", "rem_sleep_minutes",
            "stress_avg", "stress_max", "body_battery", "fetched_at"
        ]
        
        # Check if file exists
        file_exists = self.csv_file.exists()
        
        # Write to CSV
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            
            # Write header if new file
            if not file_exists:
                writer.writeheader()
            
            # Write data row
            writer.writerow(stats)
        
        print(f"✅ Saved to CSV: {self.csv_file}")
        return True
    
    def save_cache(self, stats):
        """Save latest stats to cache file."""
        if not stats:
            return False
        
        with open(self.cache_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"✅ Updated cache: {self.cache_file}")
        return True
    
    def generate_summary(self, stats):
        """Generate markdown summary."""
        if not stats:
            return
        
        date_str = datetime.fromisoformat(stats['date']).strftime("%A, %B %d, %Y")
        
        summary = f"""# Garmin Fitness Summary

## {date_str}

### Activity
- 🚶 **Steps:** {stats['steps']:,}
- 📏 **Distance:** {stats['distance_km']} km
- 🔥 **Calories:** {stats['calories']:,}
- ⚡ **Active Minutes:** {stats['active_minutes']}
- 🪜 **Floors:** {stats['floors']}

### Heart Rate
- ❤️ **Resting HR:** {stats['resting_hr']} bpm
- 📈 **Max HR:** {stats['max_hr']} bpm
- 📊 **Average HR:** {stats['avg_hr']} bpm

### Sleep
- 💤 **Total Sleep:** {stats['sleep_hours']} hours
- ⭐ **Sleep Score:** {stats['sleep_score']}/100
- 🌊 **Deep Sleep:** {stats['deep_sleep_minutes']} min
- 🌙 **Light Sleep:** {stats['light_sleep_minutes']} min
- 🧠 **REM Sleep:** {stats['rem_sleep_minutes']} min

### Health
- 🧘 **Stress (avg):** {stats['stress_avg']}
- 🔋 **Body Battery:** {stats['body_battery']}

---
*Last updated: {stats['fetched_at']}*
"""
        
        with open(self.summary_file, 'w') as f:
            f.write(summary)
        
        print(f"✅ Generated summary: {self.summary_file}")
    
    def fetch_and_save(self, date=None):
        """Fetch data and save to CSV and cache."""
        if not self.connect():
            return False
        
        stats = self.fetch_daily_stats(date)
        
        if stats:
            self.save_to_csv(stats)
            self.save_cache(stats)
            self.generate_summary(stats)
            print("✅ Data fetch complete!")
            return True
        else:
            print("❌ Failed to fetch data")
            return False
    
    def backfill(self, days=30):
        """Backfill historical data."""
        if not self.connect():
            return False
        
        print(f"📅 Backfilling last {days} days...")
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        current_date = start_date
        success_count = 0
        
        while current_date <= end_date:
            stats = self.fetch_daily_stats(current_date)
            if stats:
                self.save_to_csv(stats)
                success_count += 1
            
            current_date += timedelta(days=1)
        
        print(f"✅ Backfilled {success_count}/{days} days")
        return True


def main():
    parser = argparse.ArgumentParser(description="Fetch Garmin Connect fitness data")
    parser.add_argument("--date", help="Fetch specific date (YYYY-MM-DD)")
    parser.add_argument("--backfill", type=int, metavar="DAYS", help="Backfill last N days")
    parser.add_argument("--test", action="store_true", help="Test connection only")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--config", default="config.json", help="Config file path")
    
    args = parser.parse_args()
    
    fetcher = GarminDataFetcher(config_path=args.config)
    
    if args.test:
        # Test connection only
        if fetcher.connect():
            print("✅ Connection test successful!")
            sys.exit(0)
        else:
            print("❌ Connection test failed")
            sys.exit(1)
    
    elif args.backfill:
        # Backfill historical data
        fetcher.backfill(days=args.backfill)
    
    elif args.date:
        # Fetch specific date
        fetcher.fetch_and_save(date=args.date)
    
    else:
        # Fetch today's data
        fetcher.fetch_and_save()


if __name__ == "__main__":
    main()
