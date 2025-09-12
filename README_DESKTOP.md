# Survey Analysis Desktop Application

A Python desktop application for analyzing Procedural Level Generation survey data using tkinter and matplotlib.

## Features

✨ **Complete Survey Analysis**
- Load and analyze JSON survey data
- Interactive question selection
- Multiple chart types (Bar, Horizontal Bar, Pie)
- Real-time demographic filtering
- Professional data visualization

📊 **Chart Types Supported**
- Single/Multiple choice questions → Bar/Pie charts
- Matrix questions → Stacked bar charts  
- Ranking questions → Average ranking charts
- Text questions → Word frequency analysis

🔍 **Advanced Filtering**
- Professional role filtering
- Years of experience filtering
- Real-time response count updates
- Filter summary and statistics

🎯 **User-Friendly Interface**
- Clean, intuitive GUI layout
- Matplotlib navigation tools (zoom, pan, save)
- Status updates and error handling
- Responsive design

## Installation

### Prerequisites

1. **Python 3.13+** with tkinter support
2. **Required system packages**:
   ```bash
   sudo apt update
   sudo apt install python3-tk
   ```

### Setup

1. **Clone or navigate to the project directory**:
   ```bash
   cd /path/to/plg-survey
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure data files are present**:
   - `procedural-level-generation-survey.json`
   - `survey-questions-schema.json`

## Usage

### Option 1: Direct Python execution
```bash
source .venv/bin/activate
python survey.py
```

### Option 2: Using the launcher script
```bash
./launch_survey.sh
```

### Application Interface

**Left Panel - Controls:**
- **Data Section**: Load survey data and view summary
- **Question Analysis**: Select questions to analyze
- **Chart Options**: Choose chart type (Bar/Pie/Horizontal)
- **Demographics Filters**: Filter by role and experience
- **Advanced Filters**: Additional filtering options (coming soon)

**Right Panel - Visualization:**
- **Main Chart Area**: Interactive matplotlib charts
- **Navigation Toolbar**: Zoom, pan, save charts
- **Real-time Updates**: Charts update automatically with filter changes

### Workflow

1. **Launch the application** - Data loads automatically on startup
2. **Select a question** from the dropdown menu
3. **Choose chart type** using radio buttons
4. **Apply filters** using demographic checkboxes
5. **Analyze results** in the interactive chart area
6. **Export charts** using the matplotlib toolbar

## Features Overview

### Supported Question Types

| Question Type | Visualization | Description |
|---------------|---------------|-------------|
| Single Choice | Bar/Pie Charts | Shows distribution of single responses |
| Multiple Choice | Bar/Pie Charts | Shows frequency of all selected options |
| Matrix | Stacked Bar Chart | Shows sub-question responses by scale |
| Ranking | Bar Chart | Shows average rankings (lower = better) |
| Text/Open | Word Frequency | Shows most common words (filtered) |

### Demographic Filtering

- **Professional Role**: Filter by respondent job roles
- **Years Experience**: Filter by experience levels  
- **Real-time Counts**: See response counts for each option
- **Visual Summary**: Track filtered vs total responses

### Chart Customization

- **Bar Chart**: Vertical bars with value labels
- **Horizontal Bar**: Sorted by value, good for long labels
- **Pie Chart**: Percentage distribution with color coding
- **Interactive**: Zoom, pan, and save using matplotlib tools

## Data Format

The application expects two JSON files:

### Survey Data (`procedural-level-generation-survey.json`)
```json
[
  {
    "id": "1",
    "professional_role": "Game Designer",
    "years_experience": "3-5 years",
    "question_id": "response_value",
    ...
  }
]
```

### Schema Data (`survey-questions-schema.json`)
```json
{
  "questions": {
    "question_id": {
      "question": "Question text",
      "type": "single_choice|multiple_choice|matrix|ranking|open_text",
      "options": ["Option 1", "Option 2", ...]
    }
  }
}
```

## Troubleshooting

### Common Issues

**"tkinter not available"**
```bash
sudo apt install python3-tk
```

**"Data files not found"**
- Ensure `procedural-level-generation-survey.json` and `survey-questions-schema.json` exist in the current directory

**"Virtual environment not found"**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Font Warnings
You may see warnings like:
```
UserWarning: Glyph 128202 (\N{BAR CHART}) missing from font(s) DejaVu Sans.
```
These are cosmetic and don't affect functionality. The emoji in the title will be replaced with a simple text character.

## Dependencies

- **pandas**: Data manipulation and analysis
- **matplotlib**: Plotting and visualization  
- **numpy**: Numerical computing
- **tkinter**: GUI framework (system package)
- **json**: JSON data parsing (built-in)
- **collections**: Data structures (built-in)
- **colorsys**: Color generation (built-in)

## Comparison with Web Version

| Feature | Web App | Desktop App |
|---------|---------|-------------|
| Technology | JavaScript/HTML/CSS | Python/tkinter/matplotlib |
| Installation | Browser only | Python + system packages |
| Performance | Browser dependent | Native performance |
| Offline Use | Limited | Full offline capability |
| Export Options | Browser save | Matplotlib export tools |
| Customization | Limited | Full Python ecosystem |
| Platform | Any with browser | Linux/Windows/macOS |

## Future Enhancements

- 🔧 Advanced filtering interface
- 📈 Additional chart types
- 💾 Export to CSV/Excel
- 🎨 Custom color schemes
- 📊 Statistical analysis tools
- 🔍 Search and filter questions
- 📱 Responsive layout improvements

## Contributing

This is a port of the original web-based survey analysis tool. The desktop version maintains feature parity while providing native performance and offline capabilities.

## License

Please refer to the `license.txt` file for licensing information.
