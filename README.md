# Garmin Fitness Tracking Skill for Clawdbot

Track your Garmin fitness data with AI-powered insights and trend analysis via Clawdbot.

## Features

- 📊 **Automated Data Collection** - Pull data from Garmin Connect multiple times daily
- 📈 **Historical Tracking** - Store all data in CSV for long-term trend analysis
- 🤖 **AI Insights** - Natural language queries about your fitness data
- ⏰ **Scheduled Updates** - Automatic pulls at 6:30 AM, 12:00 PM, and 9:00 PM
- 📲 **On-Demand Sync** - Manual sync anytime via Clawdbot command

## Data Tracked

- **Activity:** Steps, distance, calories burned, active minutes
- **Sleep:** Duration, quality score, sleep stages
- **Heart Rate:** Resting HR, max HR, HR zones
- **Health:** Stress levels, Body Battery, VO2 Max
- **Workouts:** Exercise type, duration, calories

## Installation

### Prerequisites

- [Clawdbot](https://github.com/Anthropic/clawdbot) installed
- Garmin Connect account with a connected device
- Python 3.8+

### Quick Install

```bash
# Clone the skill
git clone https://github.com/berryk/clawdbot-skill-garmin.git
cd clawdbot-skill-garmin

# Run install script
./install.sh
```

### Manual Install

```bash
# Install Python dependencies
pip install -r requirements.txt

# Generate authentication tokens (handles MFA)
python3 generate_tokens.py

# This creates config.json with your tokens - no MFA needed after this!

# Install skill to Clawdbot
mkdir -p ~/.npm-global/lib/node_modules/clawdbot/skills/garmin
cp SKILL.md ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/
cp *.py ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/
cp config.json ~/.npm-global/lib/node_modules/clawdbot/skills/garmin/
```

## Configuration

### Token-Based Authentication (Recommended)

**✅ Handles MFA/2FA automatically** - No need to enter codes every time!

1. Run the token generator:
   ```bash
   python3 generate_tokens.py
   ```

2. Enter your Garmin email and password
3. If you have MFA enabled, enter the code from your email
4. Tokens are saved to `config.json` (valid for weeks/months)
5. No MFA needed for future data pulls!

**config.json structure:**
```json
{
  "garmin": {
    "email": "your-email@example.com",
    "tokens": "automatically-generated-token-string"
  },
  "data_dir": "~/clawd/fitness",
  "timezone": "Europe/London"
}
```

### Password Authentication (Alternative)

If you don't have MFA enabled, you can use direct password auth:

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

**Note:** Password auth will fail if you have MFA enabled. Use token-based auth instead.

**Security Note:** Your credentials and tokens are stored locally. The `config.json` file is excluded from git via `.gitignore`.

## Usage

### Via Clawdbot

Ask natural language questions:

```
"What were my fitness stats today?"
"How did I sleep last night?"
"Show me my step trend over the last 30 days"
"Am I hitting my fitness goals this week?"
```

### Manual Data Pull

```bash
python fetch_garmin.py
```

### Scheduled Syncs

The skill automatically syncs with Garmin Connect at:
- **6:30 AM** - Morning sync (overnight sleep data)
- **12:00 PM** - Midday check (morning activity)
- **9:00 PM** - Evening sync (full day data)

Configure via Clawdbot gateway cron jobs (see `SKILL.md`).

## Data Storage

All data is stored in CSV format for easy analysis:

```
~/clawd/fitness/
├── garmin_data.csv          # Historical data (append-only)
├── garmin_last_pull.json    # Latest sync cache
└── garmin_summary.md        # Auto-generated insights
```

### CSV Format

```csv
date,steps,distance_km,calories,active_minutes,resting_hr,sleep_hours,sleep_score,stress_avg,body_battery
2026-01-15,8500,6.2,2400,45,58,7.5,85,35,75
```

## Example Queries

**Daily Summary:**
> "Show me today's fitness stats"

**Trend Analysis:**
> "How has my sleep quality changed over the last month?"

**Goal Tracking:**
> "Am I on track to hit 10,000 steps daily this week?"

**Correlations:**
> "Does my stress level affect my sleep quality?"

## Development

### Project Structure

```
clawdbot-skill-garmin/
├── README.md                    # This file
├── SKILL.md                     # Clawdbot skill instructions
├── fetch_garmin.py              # Main data fetcher
├── garmin_analyzer.py           # Trend analysis tools
├── requirements.txt             # Python dependencies
├── config.example.json          # Template config
├── install.sh                   # Installation script
└── examples/
    └── daily_summary_example.md
```

### Running Tests

```bash
python -m pytest tests/
```

## Contributing

Contributions welcome! Please:

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Privacy & Security

- **Local Storage:** All data stored locally on your machine
- **No Cloud Sync:** Data never leaves your environment (except to Garmin Connect)
- **Credentials:** Store credentials securely (consider using env vars or secret manager)

## Troubleshooting

### Authentication Errors

If you get authentication errors:
1. Verify your Garmin credentials in `config.json`
2. Check if Garmin requires MFA (may need app password)
3. Try logging in to Garmin Connect web to verify account status

### Missing Data

If data is missing:
1. Ensure your Garmin device synced to Garmin Connect
2. Check Garmin Connect app/website for data availability
3. Run manual sync: `python fetch_garmin.py --verbose`

## License

MIT License - see LICENSE file for details

## Credits

- Built for [Clawdbot](https://github.com/Anthropic/clawdbot)
- Uses [garminconnect](https://github.com/cyberjunky/python-garminconnect) Python library
- Created by Keith Berry (@berryk)

## Roadmap

- [ ] Support for multiple Garmin accounts
- [ ] Export to Apple Health / Google Fit
- [ ] Custom goal tracking and alerts
- [ ] Integration with other fitness platforms
- [ ] Web dashboard for visualizations
- [ ] Workout plan recommendations via LLM

---

**Happy tracking! 🏃‍♂️📊**
