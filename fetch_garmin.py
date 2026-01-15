#!/usr/bin/env python3
"""
Garmin Connect Data Fetcher for Clawdbot - V2
Fetches comprehensive fitness data from Garmin Connect and stores in CSV format

Includes:
- Daily Activity (steps, calories, floors, etc.)
- Sleep Quality (duration, stages, scores)
- Heart Rate (resting, min, max)
- Stress & Recovery
- Body Battery
- Weight & Body Composition
- Respiration, SpO2
- Performance Metrics (VO2 Max, fitness age)
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
            print("Run: python generate_tokens.py")
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
        """Fetch comprehensive stats for a specific date."""
        if date is None:
            date = datetime.now().date()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d").date()
        
        date_str = date.isoformat()
        print(f"📊 Fetching data for {date}...")
        
        stats = {
            "date": date_str,
            "fetched_at": datetime.now().isoformat()
        }
        
        try:
            # 1. Get daily summary stats
            print("  - Daily activity stats...", end=" ", flush=True)
            summary = self.client.get_stats(date_str)
            
            # Activity metrics
            stats["steps"] = summary.get("totalSteps", 0)
            stats["distance_km"] = round(summary.get("totalDistanceMeters", 0) / 1000, 2)
            stats["distance_miles"] = round(summary.get("totalDistanceMeters", 0) / 1609.34, 2)
            stats["calories_total"] = summary.get("totalKilocalories", 0)
            stats["calories_active"] = summary.get("activeKilocalories", 0)
            stats["calories_bmr"] = summary.get("bmrKilocalories", 0)
            stats["floors_up"] = summary.get("floorsAscended", 0)
            stats["floors_down"] = summary.get("floorsDescended", 0)
            stats["active_minutes_moderate"] = summary.get("moderateIntensityMinutes", 0)
            stats["active_minutes_vigorous"] = summary.get("vigorousIntensityMinutes", 0)
            stats["sedentary_hours"] = round(summary.get("sedentarySeconds", 0) / 3600, 2)
            
            # Heart Rate from summary
            stats["resting_hr"] = summary.get("restingHeartRate")
            stats["min_hr"] = summary.get("minHeartRate")
            stats["max_hr"] = summary.get("maxHeartRate")
            stats["avg_hr_7day"] = summary.get("lastSevenDaysAvgRestingHeartRate")
            
            # Stress from summary
            stats["stress_avg"] = summary.get("averageStressLevel")
            stats["stress_max"] = summary.get("maxStressLevel")
            stats["stress_rest_min"] = round(summary.get("restStressDuration", 0) / 60, 1)
            stats["stress_low_min"] = round(summary.get("lowStressDuration", 0) / 60, 1)
            stats["stress_med_min"] = round(summary.get("mediumStressDuration", 0) / 60, 1)
            stats["stress_high_min"] = round(summary.get("highStressDuration", 0) / 60, 1)
            
            # Body Battery from summary
            stats["bb_charged"] = summary.get("bodyBatteryChargedValue")
            stats["bb_drained"] = summary.get("bodyBatteryDrainedValue")
            stats["bb_high"] = summary.get("bodyBatteryHighestValue")
            stats["bb_low"] = summary.get("bodyBatteryLowestValue")
            
            # Respiration from summary
            stats["respiration_avg"] = summary.get("avgWakingRespirationValue")
            stats["respiration_min"] = summary.get("lowestRespirationValue")
            stats["respiration_max"] = summary.get("highestRespirationValue")
            
            # SpO2 from summary
            stats["spo2_latest"] = summary.get("latestSpo2")
            stats["spo2_avg"] = summary.get("averageSpo2")
            stats["spo2_min"] = summary.get("lowestSpo2")
            
            print("✅")
            
        except Exception as e:
            print(f"❌ ({str(e)[:50]})")
        
        try:
            # 2. Get detailed sleep data
            print("  - Sleep data...", end=" ", flush=True)
            sleep_data = self.client.get_sleep_data(date_str)
            
            if sleep_data and 'dailySleepDTO' in sleep_data:
                sleep = sleep_data['dailySleepDTO']
                
                stats["sleep_hours"] = round(sleep.get("sleepTimeSeconds", 0) / 3600, 2)
                stats["sleep_deep_min"] = round(sleep.get("deepSleepSeconds", 0) / 60, 1)
                stats["sleep_light_min"] = round(sleep.get("lightSleepSeconds", 0) / 60, 1)
                stats["sleep_rem_min"] = round(sleep.get("remSleepSeconds", 0) / 60, 1)
                stats["sleep_awake_min"] = round(sleep.get("awakeSleepSeconds", 0) / 60, 1)
                
                # Sleep scores
                scores = sleep.get("sleepScores", {})
                stats["sleep_score"] = scores.get("overall", {}).get("value")
                stats["sleep_quality_score"] = scores.get("quality", {}).get("value")
                stats["sleep_recovery_score"] = scores.get("recovery", {}).get("value")
                
                # Sleep times
                if sleep.get("sleepStartTimestampLocal"):
                    stats["sleep_start"] = sleep.get("sleepStartTimestampLocal")
                if sleep.get("sleepEndTimestampLocal"):
                    stats["sleep_end"] = sleep.get("sleepEndTimestampLocal")
                
                stats["sleep_stress_avg"] = sleep.get("avgSleepStress")
                
            print("✅")
            
        except Exception as e:
            print(f"❌ ({str(e)[:50]})")
        
        try:
            # 3. Get VO2 Max and performance metrics
            print("  - Performance metrics...", end=" ", flush=True)
            max_metrics = self.client.get_max_metrics(date_str)
            
            if max_metrics and len(max_metrics) > 0:
                metrics = max_metrics[0]
                if 'generic' in metrics:
                    stats["vo2_max"] = metrics['generic'].get('vo2MaxValue')
                    stats["fitness_age"] = metrics['generic'].get('fitnessAge')
            
            print("✅")
            
        except Exception as e:
            print(f"❌ ({str(e)[:50]})")
        
        try:
            # 4. Get weight and body composition
            print("  - Body composition...", end=" ", flush=True)
            # Get data from last 7 days to ensure we catch latest measurement
            start_date = (date - timedelta(days=7)).isoformat()
            end_date = date.isoformat()
            
            body_comp = self.client.get_body_composition(start_date, end_date)
            
            if body_comp and 'dateWeightList' in body_comp:
                weight_list = body_comp['dateWeightList']
                if weight_list and len(weight_list) > 0:
                    # Get most recent measurement
                    latest_weight = weight_list[-1]
                    
                    # Convert weight from grams to kg/lbs
                    weight_grams = latest_weight.get('weight', 0)
                    stats["weight_kg"] = round(weight_grams / 1000, 2) if weight_grams else None
                    stats["weight_lbs"] = round(weight_grams / 453.592, 2) if weight_grams else None
                    stats["bmi"] = round(latest_weight.get('bmi', 0), 2) if latest_weight.get('bmi') else None
                    stats["body_fat_pct"] = latest_weight.get('bodyFat')
                    stats["body_water_pct"] = latest_weight.get('bodyWater')
                    
                    # Convert muscle/bone mass from grams to kg
                    muscle_grams = latest_weight.get('muscleMass', 0)
                    bone_grams = latest_weight.get('boneMass', 0)
                    stats["muscle_mass_kg"] = round(muscle_grams / 1000, 2) if muscle_grams else None
                    stats["bone_mass_kg"] = round(bone_grams / 1000, 2) if bone_grams else None
                    
                    stats["visceral_fat"] = latest_weight.get('visceralFat')
                    stats["metabolic_age"] = latest_weight.get('metabolicAge')
                    stats["weight_date"] = latest_weight.get('calendarDate')
                    
            print("✅")
            
        except Exception as e:
            print(f"❌ ({str(e)[:50]})")
        
        return stats
    
    def save_to_csv(self, stats):
        """Save stats to CSV file (append mode)."""
        if not stats:
            return False
        
        # Define CSV columns (comprehensive list)
        columns = [
            # Metadata
            "date", "fetched_at",
            # Activity
            "steps", "distance_km", "distance_miles",
            "calories_total", "calories_active", "calories_bmr",
            "floors_up", "floors_down",
            "active_minutes_moderate", "active_minutes_vigorous", "sedentary_hours",
            # Sleep
            "sleep_hours", "sleep_deep_min", "sleep_light_min", "sleep_rem_min", "sleep_awake_min",
            "sleep_score", "sleep_quality_score", "sleep_recovery_score",
            "sleep_start", "sleep_end", "sleep_stress_avg",
            # Heart Rate
            "resting_hr", "min_hr", "max_hr", "avg_hr_7day",
            # Stress
            "stress_avg", "stress_max",
            "stress_rest_min", "stress_low_min", "stress_med_min", "stress_high_min",
            # Body Battery
            "bb_charged", "bb_drained", "bb_high", "bb_low",
            # Weight & Body Composition
            "weight_kg", "weight_lbs", "bmi",
            "body_fat_pct", "body_water_pct",
            "muscle_mass_kg", "bone_mass_kg",
            "visceral_fat", "metabolic_age", "weight_date",
            # Manual Measurements
            "waist_inches", "waist_cm", "waist_date",
            # Health
            "respiration_avg", "respiration_min", "respiration_max",
            "spo2_latest", "spo2_avg", "spo2_min",
            # Performance
            "vo2_max", "fitness_age"
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

### Activity 🏃‍♂️
- 🚶 **Steps:** {stats.get('steps', 0):,}
- 📏 **Distance:** {stats.get('distance_km', 0)} km ({stats.get('distance_miles', 0)} miles)
- 🔥 **Calories:** {stats.get('calories_total', 0):,} (Active: {stats.get('calories_active', 0):,})
- ⚡ **Active Minutes:** Moderate: {stats.get('active_minutes_moderate', 0)}, Vigorous: {stats.get('active_minutes_vigorous', 0)}
- 🪜 **Floors:** Up: {stats.get('floors_up', 0)}, Down: {stats.get('floors_down', 0)}
- 💺 **Sedentary:** {stats.get('sedentary_hours', 0)} hours

### Sleep 💤
- 💤 **Total Sleep:** {stats.get('sleep_hours', 0)} hours
- ⭐ **Sleep Score:** {stats.get('sleep_score', 'N/A')}/100
- 🌊 **Deep Sleep:** {stats.get('sleep_deep_min', 0)} min
- 🌙 **Light Sleep:** {stats.get('sleep_light_min', 0)} min
- 🧠 **REM Sleep:** {stats.get('sleep_rem_min', 0)} min
- 🔔 **Awake:** {stats.get('sleep_awake_min', 0)} min
- 📅 **Bedtime:** {stats.get('sleep_start', 'N/A')}
- ⏰ **Wake Time:** {stats.get('sleep_end', 'N/A')}

### Heart Rate ❤️
- ❤️ **Resting HR:** {stats.get('resting_hr', 'N/A')} bpm
- 📈 **Max HR:** {stats.get('max_hr', 'N/A')} bpm
- 📊 **Min HR:** {stats.get('min_hr', 'N/A')} bpm

### Stress & Recovery 🧘
- 🧘 **Stress (avg):** {stats.get('stress_avg', 'N/A')}
- 🔋 **Body Battery:** High: {stats.get('bb_high', 'N/A')}, Low: {stats.get('bb_low', 'N/A')}
- ⚡ **Charged:** {stats.get('bb_charged', 'N/A')} | **Drained:** {stats.get('bb_drained', 'N/A')}

### Weight & Body Composition ⚖️
- ⚖️ **Weight:** {stats.get('weight_kg', 'N/A')} kg ({stats.get('weight_lbs', 'N/A')} lbs)
- 📊 **BMI:** {stats.get('bmi', 'N/A')}
- 💪 **Body Fat:** {stats.get('body_fat_pct', 'N/A')}%
- 🏋️ **Muscle Mass:** {stats.get('muscle_mass_kg', 'N/A')} kg
- 💧 **Body Water:** {stats.get('body_water_pct', 'N/A')}%

### Health Metrics 🏥
- 🫁 **Respiration:** {stats.get('respiration_avg', 'N/A')} brpm
- 🩸 **SpO2:** {stats.get('spo2_latest', 'N/A')}%

### Performance 🏆
- 🏃 **VO2 Max:** {stats.get('vo2_max', 'N/A')}
- 🎂 **Fitness Age:** {stats.get('fitness_age', 'N/A')}

---
*Last updated: {stats.get('fetched_at', 'N/A')}*
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
