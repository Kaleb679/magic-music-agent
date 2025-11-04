#!/bin/zsh
# Run the on-device synth project

# Go to the project directory (where this script is)
cd "$(dirname "$0")"

# Activate virtual environment
source venv/bin/activate

# Run the synth entrypoint
python -m src.main