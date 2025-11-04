#!/bin/zsh
# Minimal runner for your on-device synth project

# Go to the project directory (where this script is)
cd "$(dirname "$0")"

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
  echo "🐍 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
  echo "📦 Installing dependencies..."
  pip install -r requirements.txt > /dev/null
fi

# Run the synth
echo "🎵 Running synth..."
python -m src.main