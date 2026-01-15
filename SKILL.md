---
name: garmin
description: Track Garmin fitness data with automated syncs and AI-powered insights. Pulls activity, sleep, heart rate, and health metrics from Garmin Connect.
homepage: https://github.com/berryk/clawdbot-skill-garmin
metadata: {"clawdbot":{"emoji":"⌚","requires":{"bins":["python3"],"packages":["garminconnect","pandas"]}}}
---

# Garmin Fitness Tracking

Integrate Garmin Connect data into Clawdbot for AI-powered fitness insights and trend analysis.

## Overview

This skill automatically syncs fitness data from Garmin Connect multiple times daily and stores it in CSV format for historical tracking and analysis.

**Data Tracked:**
- Steps, distance, calories, active minutes
- Sleep duration and quality scores
- Resting heart rate and HR zones
- Stress levels and Body Battery
- Workout details and performance metrics

## Setup

### 1. Install Dependencies

```bash
cd ~/.npm-global/lib/node_modules/clawdbot/skills/garmin
pip3 install -r requirements.txt
```

### 2. Configure Garmin Credentials

Create `config.json`:

```json
{
  "garmin": {
    "email": "your-email@example.com",
    "password": "your-garmin-password"
  },
  "data_dir": "~/clawd/fitness",
  "timezone": "Europe/London"
}
```

**Security:** Store credentials in environment variables or use a secrets manager in production.

### 3. Test Connection

```bash
python3 fetch_garmin.py --test
```

### 4. Set Up Scheduled Syncs

Add cron jobs via Clawdbot gateway:

```javascript
{
  "jobs": [
    {
      "id": "garmin-morning",
      "name": "Garmin Morning Sync",
      "schedule": "30 6 * * *",
      "action": {
        "type": "exec",
        "command": "python3",
        "args": [
          "~/.npm-global/lib/node_modules/clawdbot/skills/garmin/fetch_garmin.py"
        ]
      },
      "enabled": true
    },
    {
      "id": "garmin-noon",
      "name": "Garmin Noon Sync",
      "schedule": "0 12 * * *",
      "action": {
        "type": "exec",
        "command": "python3",
        "args": [
          "~/.npm-global/lib/node_modules/clawdbot/skills/garmin/fetch_garmin.py"
        ]
      },
      "enabled": true
    },
    {
      "id": "garmin-evening",
      "name": "Garmin Evening Sync",
      "schedule": "0 21 * * *",
      "action": {
        "type": "exec",
        "command": "python3",
        "args": [
          "~/.npm-global/lib/node_modules/clawdbot/skills/garmin/fetch_garmin.py"
        ]
      },
      "enabled": true
    }
  ]
}
```

**Schedule (UK Time):**
- 6:30 AM - Morning sync (overnight sleep + yesterday final)
- 12:00 PM - Midday check (morning activity)
- 9:00 PM - Evening sync (full day data)

## Usage

### Natural Language Queries

Ask questions about your fitness data:

**Daily Stats:**
```
"What were my fitness stats today?"
"How many steps did I take yesterday?"
"How did I sleep last night?"
```

**Trends & Analysis:**
```
"Show me my step trend over the last 30 days"
"How has my sleep quality changed this month?"
"What's my average resting heart rate this week?"
```

**Goal Tracking:**
```
"Am I hitting my 10,000 steps goal this week?"
"How many active minutes did I get this month?"
"Compare my activity this week vs last week"
```

**Correlations:**
```
"Does my stress level affect my sleep quality?"
"When do I have the most energy during the day?"
```

### Manual Commands

**Fetch latest data:**
```bash
exec python3 ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/fetch_garmin.py
```

**Analyze trends:**
```bash
exec python3 ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/garmin_analyzer.py --days 30
```

**View summary:**
```bash
read ~/clawd/fitness/garmin_summary.md
```

## Data Files

All data stored in `~/clawd/fitness/`:

**garmin_data.csv** - Historical data (append-only)
```csv
date,steps,distance_km,calories,active_minutes,resting_hr,sleep_hours,sleep_score,stress_avg,body_battery
2026-01-15,8500,6.2,2400,45,58,7.5,85,35,75
```

**garmin_last_pull.json** - Latest sync cache
```json
{
  "timestamp": "2026-01-15T09:00:00Z",
  "date": "2026-01-15",
  "steps": 8500,
  "distance_km": 6.2,
  ...
}
```

**garmin_summary.md** - Auto-generated insights

## Examples

### Example: Daily Summary

User asks: *"What were my fitness stats today?"*

Assistant reads `garmin_last_pull.json` and responds:

```
📊 Fitness Stats for Wednesday, January 15, 2026:

🚶 Steps: 8,500 (85% of 10,000 goal)
📏 Distance: 6.2 km
🔥 Calories: 2,400
⚡ Active Minutes: 45

💤 Sleep: 7.5 hours (score: 85/100)
❤️ Resting HR: 58 bpm
🧘 Stress: 35 (low)
🔋 Body Battery: 75

Great job on sleep quality! Try to get a few more steps to hit your goal.
```

### Example: Trend Analysis

User asks: *"How has my sleep changed over the last month?"*

Assistant runs `garmin_analyzer.py` on CSV data:

```
📈 Sleep Trend Analysis (Last 30 Days):

Average: 7.4 hours/night
Best: 8.5 hours (Jan 10)
Worst: 6.0 hours (Jan 3)

Quality Score: 82/100 (↑ 5 points from last month)

Insights:
- Sleep improving week-over-week
- Best sleep on weekends (avg 8.2 hrs)
- Weekday average: 7.0 hrs

Recommendation: Try to maintain 8+ hours on weekdays for optimal recovery.
```

## Troubleshooting

### Authentication Issues

If Garmin authentication fails:
1. Verify credentials in `config.json`
2. Check if Garmin requires MFA (may need app-specific password)
3. Test login at https://connect.garmin.com

### Missing Data

If recent data is missing:
1. Ensure Garmin device synced to Garmin Connect app
2. Check Garmin Connect website for data availability
3. Run manual sync with verbose logging:
   ```bash
   python3 fetch_garmin.py --verbose
   ```

### CSV Corruption

If CSV data appears corrupted:
1. Backup existing file: `cp garmin_data.csv garmin_data.csv.bak`
2. Re-fetch last 90 days: `python3 fetch_garmin.py --backfill 90`

## Advanced Usage

### Backfill Historical Data

Fetch last 90 days of data:
```bash
python3 fetch_garmin.py --backfill 90
```

### Custom Analysis

Use pandas to analyze the CSV:
```python
import pandas as pd

df = pd.read_csv('~/clawd/fitness/garmin_data.csv')
df['date'] = pd.to_datetime(df['date'])

# Weekly averages
weekly = df.groupby(df['date'].dt.isocalendar().week).mean()
print(weekly[['steps', 'sleep_hours', 'resting_hr']])
```

## Integration with Memory

The skill can store fitness insights in your Clawdbot memory:

```bash
# Add to memory/fitness.md
echo "## Fitness Goals 2026\n- Target: 10,000 steps daily\n- Current avg: 8,500" >> ~/clawd/memory/fitness.md
```

Then recall with memory_search:
```
memory_search("fitness goals")
```

## Privacy & Security

- **Local Storage:** All data stored locally in `~/clawd/fitness/`
- **No Cloud Sync:** Data never sent to external services (except Garmin Connect API)
- **Secure Credentials:** Use environment variables or secret manager for production
- **Data Retention:** You control all data; delete anytime

## Maintenance

### Update Skill

```bash
cd ~/Github/clawdbot-skill-garmin
git pull origin main
pip3 install -r requirements.txt --upgrade
```

### Clear Cache

```bash
rm ~/clawd/fitness/garmin_last_pull.json
```

### Reset Data

**⚠️ Warning:** This deletes all historical data.

```bash
rm ~/clawd/fitness/garmin_data.csv
```

## Support

- GitHub: https://github.com/berryk/clawdbot-skill-garmin
- Issues: https://github.com/berryk/clawdbot-skill-garmin/issues

---

**Skill Version:** 1.0.0  
**Author:** Keith Berry (@berryk)  
**License:** MIT
