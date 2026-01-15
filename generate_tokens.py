#!/usr/bin/env python3
"""
Garmin Token Generator for Clawdbot Skill
Run this once to generate authentication tokens (handles MFA)
Tokens are saved to config.json and can be used without MFA for weeks/months
"""

import json
import os
import sys
from pathlib import Path

try:
    from garminconnect import Garmin
except ImportError:
    print("Error: garminconnect not installed. Run: pip install garminconnect")
    sys.exit(1)


def prompt_for_mfa():
    """Prompt user for MFA code."""
    print("\n🔑 MFA Code Required!")
    print("Check your email for the Garmin verification code.")
    code = input("Enter MFA code: ").strip()
    return code


def generate_tokens(email, password):
    """Generate Garmin authentication tokens."""
    print("🔐 Connecting to Garmin Connect...")
    print("(If you have MFA enabled, check your email for a code)\n")
    
    try:
        # Create client with MFA prompt support
        client = Garmin(email, password, prompt_mfa=prompt_for_mfa)
        client.login()
        print("\n✅ Login successful!\n")
        
        # Get the session tokens as JSON string
        tokens = client.garth.dumps()
        
        # Get user info
        display_name = client.get_full_name()
        
        return tokens, display_name
        
    except Exception as e:
        print(f"❌ Login failed: {e}")
        print("\nTroubleshooting:")
        print("1. Check email/password are correct")
        print("2. If using MFA, make sure you entered the code correctly")
        print("3. MFA codes expire quickly - try again for a fresh code")
        print("4. Check https://connect.garmin.com to verify account status")
        return None, None


def save_tokens_to_config(tokens, email, config_path="config.json"):
    """Save tokens to config.json."""
    config_file = Path(__file__).parent / config_path
    
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
    
    return config_file


def main():
    print("🏃‍♂️ Garmin Token Generator for Clawdbot\n")
    print("This tool will:")
    print("  1. Connect to your Garmin account (handles MFA)")
    print("  2. Generate long-lived authentication tokens")
    print("  3. Save tokens to config.json")
    print("  4. Allow Clawdbot skill to access Garmin without MFA\n")
    
    # Check if config.json already exists
    config_file = Path(__file__).parent / "config.json"
    if config_file.exists():
        print(f"⚠️  config.json already exists at: {config_file}")
        overwrite = input("Overwrite existing config? (y/N): ").strip().lower()
        if overwrite != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    # Get credentials
    email = input("\nGarmin email: ").strip()
    password = input("Garmin password: ").strip()
    
    if not email or not password:
        print("❌ Email and password required")
        sys.exit(1)
    
    # Generate tokens
    tokens, display_name = generate_tokens(email, password)
    
    if tokens:
        # Save to config
        config_path = save_tokens_to_config(tokens, email)
        
        print("\n" + "="*70)
        print("✅ SUCCESS!")
        print("="*70)
        print(f"\nLogged in as: {display_name}")
        print(f"Tokens saved to: {config_path}")
        print("\n📋 Next Steps:")
        print("   1. Tokens are valid for weeks/months (no MFA needed)")
        print("   2. Test the skill: python fetch_garmin.py")
        print("   3. When tokens expire, run this script again")
        print("   4. Keep config.json secure (it's in .gitignore)")
        print("\n" + "="*70)
        
    else:
        print("\n❌ Token generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
