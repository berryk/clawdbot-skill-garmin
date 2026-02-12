# Garmin Timezone Auto-Sync

## Overview

The Garmin skill now automatically syncs your timezone from the Garmin API and updates cron jobs to match your current location. This ensures:

1. ✅ Data is always fetched for the correct day based on your actual timezone
2. ✅ Sync times stay consistent in your local time (6:30 AM, 12:00 PM, 9:00 PM)
3. ✅ Automatic updates when you travel to different timezones

## How It Works

### 1. Timezone Detection

The `sync_timezone.py` script:
- Calls `client.get_userprofile_settings()` to get your current Garmin timezone
- Compares it to the stored timezone in `config.json`
- Updates the config if changed

### 2. Cron Job Updates

When timezone changes:
- Converts local sync times (6:30 AM, 12:00 PM, 9:00 PM) to UTC
- Generates updated cron schedules
- Saves to `cron_update.json`
- Clawdbot applies the new schedules

### 3. Data Fetching

The `fetch_garmin.py` script:
- Reads timezone from `config.json`
- Uses it to determine "today" in your timezone
- Fetches correct day's data

## Schedule

### Timezone Sync
- **Frequency:** Every 6 hours
- **Command:** `python3 sync_timezone.py`
- **Action:** Check Garmin API, update cron jobs if timezone changed

### Data Syncs (in your local time)
- **Morning (6:30 AM):** Overnight sleep + yesterday final stats
- **Noon (12:00 PM):** Midday activity check
- **Evening (9:00 PM):** Full day summary

## Current Configuration

```json
{
  "timezone": "Asia/Hong_Kong",
  "updated_at": "2026-02-12T00:44:13.670401"
}
```

### UTC Cron Schedules (for Hong Kong)
- Morning: `30 22 * * *` (6:30 AM HKT = 10:30 PM UTC)
- Noon: `0 4 * * *` (12:00 PM HKT = 4:00 AM UTC)
- Evening: `0 13 * * *` (9:00 PM HKT = 1:00 PM UTC)

## Manual Commands

### Force Timezone Sync
```bash
python3 ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/sync_timezone.py --force
```

### Check Current Timezone
```bash
python3 -c "
import json
with open('~/.npm-global/lib/node_modules/clawdbot/skills/garmin/config.json') as f:
    print(json.load(f)['timezone'])
"
```

### Test Fetch with Timezone
```bash
python3 ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/fetch_garmin.py
# Should show: "📍 Using timezone: Asia/Hong_Kong (today: 2026-02-12)"
```

## Travel Example

When you travel from London → Hong Kong:

1. **Before:**
   - Garmin timezone: `Europe/London`
   - Morning sync: `30 6 * * *` UTC (6:30 AM London = 6:30 AM UTC)

2. **After landing in HK:**
   - You update Garmin timezone on device/app to `Asia/Hong_Kong`
   - Within 6 hours, `sync_timezone.py` detects change
   - Morning sync updated: `30 22 * * *` UTC (6:30 AM HK = 10:30 PM UTC)
   - Clawdbot notifies you in Telegram Fitness Chat

3. **Result:**
   - Syncs still happen at 6:30 AM, 12:00 PM, 9:00 PM in your new timezone
   - Data fetches use Hong Kong date/time

## Troubleshooting

### Timezone Not Updating

1. Check Garmin Connect app/website - ensure timezone is correct there
2. Run manual sync: `python3 sync_timezone.py --force`
3. Check `config.json` for current timezone
4. Check `cron_update.json` for generated schedules

### Wrong Day Being Fetched

1. Verify timezone in config: `cat config.json | grep timezone`
2. Test fetch: `python3 fetch_garmin.py` (should show correct timezone/date)
3. If wrong, force sync: `python3 sync_timezone.py --force`

### Cron Jobs Not Running at Right Time

1. Check cron list: Use Clawdbot cron tool
2. Verify UTC conversion is correct
3. Remember: Cron runs in UTC, local times are converted

## Files

- **`sync_timezone.py`** - Main timezone sync script
- **`config.json`** - Stores current timezone
- **`cron_update.json`** - Generated cron schedules (for Clawdbot to apply)
- **`fetch_garmin.py`** - Updated to use timezone from config

## Benefits

✅ **No manual updates** - Timezone syncs automatically when you travel  
✅ **Consistent sync times** - Always 6:30 AM, noon, 9 PM in your local time  
✅ **Correct day data** - Fetches today in your timezone, not server timezone  
✅ **Travel-friendly** - Updates within 6 hours of timezone change  

## Version History

- **v1.0.0** (2026-02-12) - Initial timezone auto-sync implementation
