#!/usr/bin/env python3
"""
Garmin Data Discovery Script with Token/MFA Support
Discovers all available data points from your Garmin device

Uses token-based auth if available (no MFA needed), falls back to password+MFA
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from garminconnect import Garmin

def load_config(config_path="config.json"):
    """Load config file if it exists."""
    config_file = Path(__file__).parent / config_path
    
    if config_file.exists():
        with open(config_file) as f:
            return json.load(f)
    return None

def prompt_for_mfa():
    """Prompt user for MFA code."""
    print("\n🔑 MFA Code Required!")
    print("Check your email for the Garmin verification code.")
    code = input("Enter MFA code: ").strip()
    return code

def connect_to_garmin():
    """Connect to Garmin using tokens or credentials."""
    
    # Try loading config first
    config = load_config()
    
    # Method 1: Try token-based auth (no MFA needed!)
    if config and config.get("garmin", {}).get("tokens"):
        try:
            print("🔐 Connecting with saved tokens...")
            client = Garmin()
            client.garth.loads(config["garmin"]["tokens"])
            client.display_name = client.garth.profile.get("displayName", "User")
            print(f"✅ Connected as: {client.display_name} (using tokens)\n")
            return client
        except Exception as e:
            print(f"⚠️  Saved tokens failed: {e}")
            print("Falling back to credential login...\n")
    
    # Method 2: Password auth with MFA support
    email = None
    password = None
    
    # Try to get credentials from config
    if config and config.get("garmin", {}).get("email"):
        email = config["garmin"]["email"]
        password = config["garmin"].get("password")
        print(f"📧 Using email from config: {email}")
        if not password:
            password = input("Garmin password: ").strip()
    else:
        # Prompt for credentials
        email = input("Garmin email: ").strip()
        password = input("Garmin password: ").strip()
    
    if not email or not password:
        print("❌ Email and password required")
        return None
    
    print("\n🔐 Connecting to Garmin Connect...")
    print("(If you have MFA enabled, check your email for a code)\n")
    
    try:
        # Create client with MFA prompt support
        client = Garmin(email, password, prompt_mfa=prompt_for_mfa)
        client.login()
        print("\n✅ Connected successfully!\n")
        
        # Save tokens for future use
        save_option = input("💾 Save tokens to config.json for future use? (Y/n): ").strip().lower()
        if save_option != 'n':
            save_tokens(client.garth.dumps(), email)
            print("✅ Tokens saved! Future runs won't need MFA.\n")
        
        return client
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check email/password are correct")
        print("2. If using MFA, make sure you entered the code correctly")
        print("3. MFA codes expire quickly - try again for a fresh code")
        print("4. Check https://connect.garmin.com to verify account status")
        return None

def save_tokens(tokens, email):
    """Save tokens to config.json."""
    config_file = Path(__file__).parent / "config.json"
    
    # Load existing config or create new one
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    else:
        config = {
            "garmin": {},
            "data_dir": "~/clawd/fitness",
            "timezone": "Europe/London"
        }
    
    # Update with tokens
    config["garmin"]["email"] = email
    config["garmin"]["tokens"] = tokens
    
    # Save to file
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)

def discover_garmin_data(client):
    """Discover all available data points from connected Garmin client."""
    
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    
    results = {
        "device_info": {},
        "available_endpoints": [],
        "sample_data": {}
    }
    
    # Test all available endpoints
    endpoints = [
        ("get_stats", "Daily Summary Stats", lambda: client.get_stats(yesterday.isoformat())),
        ("get_heart_rates", "Heart Rate Data", lambda: client.get_heart_rates(yesterday.isoformat())),
        ("get_sleep_data", "Sleep Data", lambda: client.get_sleep_data(yesterday.isoformat())),
        ("get_stress_data", "Stress Data", lambda: client.get_stress_data(yesterday.isoformat())),
        ("get_body_battery", "Body Battery", lambda: client.get_body_battery(yesterday.isoformat())),
        ("get_steps_data", "Steps Data", lambda: client.get_steps_data(yesterday.isoformat())),
        ("get_hydration_data", "Hydration", lambda: client.get_hydration_data(yesterday.isoformat())),
        ("get_respiration_data", "Respiration", lambda: client.get_respiration_data(yesterday.isoformat())),
        ("get_spo2_data", "SpO2 (Blood Oxygen)", lambda: client.get_spo2_data(yesterday.isoformat())),
        ("get_max_metrics", "Max Metrics (VO2 Max, etc)", lambda: client.get_max_metrics(yesterday.isoformat())),
        ("get_devices", "Devices", lambda: client.get_devices()),
        ("get_device_settings", "Device Settings", lambda: client.get_device_settings()),
        ("get_activities", "Recent Activities", lambda: client.get_activities(0, 5)),
        ("get_user_settings", "User Settings", lambda: client.get_user_settings()),
        ("get_full_name", "User Name", lambda: client.get_full_name()),
    ]
    
    print("🔍 Discovering available data points from your Garmin device...\n")
    
    for endpoint_name, description, func in endpoints:
        try:
            print(f"Testing: {description:<30} ", end="", flush=True)
            data = func()
            
            if data:
                results["available_endpoints"].append({
                    "endpoint": endpoint_name,
                    "description": description,
                    "available": True
                })
                results["sample_data"][endpoint_name] = data
                print("✅")
            else:
                print("⚠️  (no data)")
                results["available_endpoints"].append({
                    "endpoint": endpoint_name,
                    "description": description,
                    "available": False
                })
        except Exception as e:
            error_msg = str(e)[:50]
            print(f"❌ ({error_msg})")
            results["available_endpoints"].append({
                "endpoint": endpoint_name,
                "description": description,
                "available": False,
                "error": str(e)
            })
    
    # Get device info
    try:
        devices = client.get_devices()
        if devices:
            results["device_info"] = devices[0] if isinstance(devices, list) else devices
    except:
        pass
    
    return results

def print_summary(results):
    """Print a summary of discovered data."""
    print("\n" + "="*80)
    print("📊 GARMIN DATA DISCOVERY SUMMARY")
    print("="*80)
    
    # Device info
    if results["device_info"]:
        print("\n🔹 Device Information:")
        device = results["device_info"]
        print(f"   Model: {device.get('productDisplayName', 'Unknown')}")
        print(f"   Device ID: {device.get('deviceId', 'Unknown')}")
        print(f"   Last Sync: {device.get('lastSyncTime', 'Unknown')}")
        print(f"   Firmware: {device.get('softwareVersion', 'Unknown')}")
    
    # Available endpoints
    print("\n🔹 Available Data Points for Clawdbot Skill:")
    available = [e for e in results["available_endpoints"] if e["available"]]
    unavailable = [e for e in results["available_endpoints"] if not e["available"]]
    
    for endpoint in available:
        print(f"   ✅ {endpoint['description']}")
    
    if unavailable:
        print("\n🔹 Unavailable/Not Supported:")
        for endpoint in unavailable:
            print(f"   ❌ {endpoint['description']}")
    
    # Data summary
    if "get_stats" in results["sample_data"]:
        stats = results["sample_data"]["get_stats"]
        print("\n🔹 Sample Data from Yesterday:")
        print(f"   Steps: {stats.get('totalSteps', 'N/A'):,}")
        print(f"   Calories: {stats.get('activeKilocalories', 0) + stats.get('bmrKilocalories', 0):,}")
        print(f"   Floors: {stats.get('floorsAscended', 'N/A')}")
    
    print("\n" + "="*80)
    print(f"✅ Discovery complete! Found {len(available)}/{len(results['available_endpoints'])} available data sources.")
    print("="*80)

def main():
    print("🏃‍♂️ Garmin Data Discovery Tool\n")
    print("This tool will:")
    print("  1. Connect to your Garmin Connect account")
    print("  2. Test all available API endpoints")
    print("  3. Show what data your device provides")
    print("  4. Save results for the Clawdbot skill\n")
    
    # Connect to Garmin (tries tokens first, then password+MFA)
    client = connect_to_garmin()
    
    if not client:
        print("❌ Failed to connect to Garmin")
        sys.exit(1)
    
    # Discover data
    results = discover_garmin_data(client)
    
    if results:
        print_summary(results)
        
        # Save full results
        output_file = "garmin_discovery_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Full results saved to: {output_file}")
        print("\n📋 Next Steps:")
        print("   1. Review the full results in garmin_discovery_results.json")
        print("   2. We'll use this to update fetch_garmin.py with all available data")
        print("   3. The skill will track all available metrics automatically")
    else:
        print("❌ Discovery failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
