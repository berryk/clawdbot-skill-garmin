#!/bin/bash
# Installation script for Garmin Clawdbot skill

set -e

echo "🚀 Installing Garmin Skill for Clawdbot..."
echo ""

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not found. Please install pip3"
    exit 1
fi

echo "✅ pip3 found"

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Create Clawdbot skill directory
SKILL_DIR="$HOME/.npm-global/lib/node_modules/clawdbot/skills/garmin"
echo ""
echo "📁 Creating skill directory: $SKILL_DIR"
mkdir -p "$SKILL_DIR"

# Copy files
echo "📋 Copying skill files..."
cp SKILL.md "$SKILL_DIR/"
cp fetch_garmin.py "$SKILL_DIR/"
chmod +x "$SKILL_DIR/fetch_garmin.py"

# Copy config template if config doesn't exist
if [ ! -f "$SKILL_DIR/config.json" ]; then
    echo "📝 Creating config template..."
    cp config.example.json "$SKILL_DIR/config.json"
    echo ""
    echo "⚠️  IMPORTANT: Edit your Garmin credentials:"
    echo "   nano $SKILL_DIR/config.json"
else
    echo "✅ Config already exists (not overwriting)"
fi

# Create data directory
DATA_DIR="$HOME/clawd/fitness"
echo ""
echo "📂 Creating data directory: $DATA_DIR"
mkdir -p "$DATA_DIR"

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit config with your Garmin credentials:"
echo "      nano $SKILL_DIR/config.json"
echo ""
echo "   2. Test connection:"
echo "      python3 $SKILL_DIR/fetch_garmin.py --test"
echo ""
echo "   3. Fetch data:"
echo "      python3 $SKILL_DIR/fetch_garmin.py"
echo ""
echo "   4. Set up cron jobs (see SKILL.md for details)"
echo ""
echo "🎉 Happy tracking!"
