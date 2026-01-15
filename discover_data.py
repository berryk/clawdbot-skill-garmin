#!/usr/bin/env python3
"""
Garmin Data Discovery Script
Discovers all available data points from your Garmin device
"""

import json
import sys
from datetime import datetime, timedelta
from garminconnect import Garmin

def discover_garmin_data(email, password):
    """Connect to Garmin and discover all available data points."""
    
    print("🔐 Connecting to Garmin Connect...")
    try:
        client = Garmin(email, password)
        client.login()
        print("✅ Connected successfully!\n")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None
    
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
        ("get_max_metrics", "Max Metrics", lambda: client.get_max_metrics(yesterday.isoformat())),
        ("get_devices", "Devices", lambda: client.get_devices()),
        ("get_device_settings", "Device Settings", lambda: client.get_device_settings()),
        ("get_activities", "Recent Activities", lambda: client.get_activities(0, 5)),
    ]
    
    print("🔍 Discovering available data points...\n")
    
    for endpoint_name, description, func in endpoints:
        try:
            print(f"Testing: {description} ({endpoint_name})...", end=" ")
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
            print(f"❌ ({str(e)[:50]})")
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
    print("\n" + "="*70)
    print("📊 GARMIN DATA DISCOVERY SUMMARY")
    print("="*70)
    
    # Device info
    if results["device_info"]:
        print("\n🔹 Device Information:")
        device = results["device_info"]
        print(f"   Model: {device.get('productDisplayName', 'Unknown')}")
        print(f"   Device ID: {device.get('deviceId', 'Unknown')}")
        print(f"   Last Sync: {device.get('lastSyncTime', 'Unknown')}")
    
    # Available endpoints
    print("\n🔹 Available Data Points:")
    available = [e for e in results["available_endpoints"] if e["available"]]
    unavailable = [e for e in results["available_endpoints"] if not e["available"]]
    
    for endpoint in available:
        print(f"   ✅ {endpoint['description']}")
    
    if unavailable:
        print("\n🔹 Unavailable Data Points:")
        for endpoint in unavailable:
            print(f"   ❌ {endpoint['description']}")
    
    # Sample data structure
    print("\n🔹 Sample Data Structure:")
    for endpoint_name, data in results["sample_data"].items():
        if endpoint_name in ["get_stats", "get_heart_rates", "get_sleep_data", "get_stress_data"]:
            print(f"\n   {endpoint_name}:")
            print(f"   {json.dumps(data, indent=2)[:500]}...")
    
    print("\n" + "="*70)
    print(f"✅ Discovery complete! Found {len(available)} available data sources.")
    print("="*70)

def main():
    print("🏃‍♂️ Garmin Venu 4 Data Discovery\n")
    
    # Get credentials
    email = input("Garmin email: ").strip()
    password = input("Garmin password: ").strip()
    
    if not email or not password:
        print("❌ Email and password required")
        sys.exit(1)
    
    # Discover data
    results = discover_garmin_data(email, password)
    
    if results:
        print_summary(results)
        
        # Save full results
        output_file = "garmin_discovery_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Full results saved to: {output_file}")
        print("\nYou can review the complete data structure in that file.")
    else:
        print("❌ Discovery failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
