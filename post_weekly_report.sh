#!/bin/bash
# Post Weekly Garmin Report to Telegram Fitness Chat
# Usage: ./post_weekly_report.sh

TELEGRAM_GROUP_ID="-5115882912"
SKILL_DIR="$HOME/.npm-global/lib/node_modules/clawdbot/skills/garmin"
FITNESS_DIR="$HOME/clawd/fitness"

# Generate weekly report
cd "$SKILL_DIR"
source venv/bin/activate
python weekly_report.py

# Check if report was generated
if [ ! -f "$FITNESS_DIR/weekly_report.md" ]; then
    echo "❌ Weekly report not found"
    exit 1
fi

# Read report content
REPORT=$(cat "$FITNESS_DIR/weekly_report.md")

# Post to Telegram via Clawdbot message tool
# Note: This will be called by Clawdbot, which has access to message tool

echo "✅ Weekly report generated"
echo "📱 Ready to post to Telegram group: $TELEGRAM_GROUP_ID"
echo ""
echo "Report content:"
echo "$REPORT"
