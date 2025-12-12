#!/bin/bash
# Launcher script for Thematic Coding Application

cd "$(dirname "$0")"

# Check if answers_input.json exists
if [ ! -f "answers_input.json" ]; then
    echo "❌ Error: answers_input.json not found"
    echo ""
    echo "Please run the survey analysis script first:"
    echo "  cd .."
    echo "  python survey-text-question.py"
    exit 1
fi

echo "🚀 Starting Thematic Coding Application..."
echo ""
python app.py
