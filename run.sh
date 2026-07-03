#!/bin/bash
# Research Agent — auto-run wrapper
# Called by cron every 30 min. Processes pending topics from research_queue.csv.

DIR="$(cd "$(dirname "$0")" && pwd)"
LOG="$DIR/logs/cron_$(date +%Y-%m-%d).log"
mkdir -p "$DIR/logs"

echo "" >> "$LOG"
echo "========== $(date) ==========" >> "$LOG"

# Activate venv and load API key
source "$DIR/.venv/bin/activate"
source ~/.zshrc 2>/dev/null

# Run the batch processor
cd "$DIR"
python batch_runner.py >> "$LOG" 2>&1

echo "Exit code: $?" >> "$LOG"
