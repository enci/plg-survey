#!/bin/bash
# Survey Analysis Desktop Application Launcher

echo "🚀 Starting Survey Analysis Desktop Application..."
echo "=================================================="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run:"
    echo "   python3 -m venv .venv"
    echo "   source .venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Check if data files exist
if [ ! -f "procedural-level-generation-survey.json" ] || [ ! -f "survey-questions-schema.json" ]; then
    echo "❌ Required data files not found:"
    echo "   • procedural-level-generation-survey.json"
    echo "   • survey-questions-schema.json"
    echo ""
    echo "Please ensure these files are in the current directory."
    exit 1
fi

# Check if tkinter is available
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "❌ tkinter not available. Please install with:"
    echo "   sudo apt install python3-tk"
    exit 1
fi

echo "✅ All dependencies satisfied"
echo "🔧 Launching application..."
echo ""

# Run the application
.venv/bin/python survey.py

echo ""
echo "👋 Application closed. Thank you for using Survey Analysis Tool!"
