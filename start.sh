#!/usr/bin/env bash
# PitchPulse AI Startup Script
PORT="${1:-8085}"
cd "$(dirname "$0")"
echo "Starting PitchPulse AI on http://127.0.0.1:$PORT ..."
python3 server.py "$PORT"
