import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import re

# Set up the plotting style for publication
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("husl")

# Configure matplotlib for high-quality output
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['savefig.bbox'] = 'tight'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9

def load_and_clean_data(filename):
    """Load and clean the survey data"""
    try:
        # Try different encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                df = pd.read_csv(filename, encoding=encoding)
                print(f"Successfully loaded with {encoding} encoding")
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError("Could not decode the file with any common encoding")
            
    except Exception as e:
        print(f"Error loading file: {e}")
        return None
    
    print(f"Dataset shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    
    # Clean column names
    df.columns = df.columns.str.strip()
    
    return df

def create_role_distribution_chart(df, save_path='role_distribution.png'):
    """Create professional role distribution chart"""
    role_col = 'How would you primarily describe your professional role?'
    
    if role_col not in df.columns:
        print(f"Column '{role_col}' not found")
        return
    
    # Count roles and clean data
    role_counts = df[role_col].dropna().value_counts()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(range(len(role_counts)), role_counts.values, 
                  color=sns.color_palette("husl", len(role_counts)))
    
    # Customize the chart
    ax.set_xlabel('Professional Role')
    ax.set_ylabel('Number of Respondents')
    ax.set_title('Distribution of Professional Roles Among Survey Respondents')
    ax.set_xticks(range(len(role_counts)))
    ax.set_xticklabels(role_counts.index, rotation=45, ha='right')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.savefig(save_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"Role distribution chart saved as {save_path}")
    plt.show()

def create_experience_chart(df, save_path='experience_distribution.png'):
    """Create experience level distribution chart"""
    exp_col = 'How many years of experience do you have in game development?'
    
    if exp_col not in df.columns:
        print(f"Column '{exp_col}' not found")
        return
    
    # Define the order of experience levels
    exp_order = ['0-2 years', '3-5 years', '6-10 years', '11-15 years', '15+ years']
    
    # Count experience levels
    exp_counts = df[exp_col].dropna().value_counts()
    
    # Reorder according to our defined order
    ordered_counts = []
    ordered_labels = []
    for exp in exp_order:
        if exp in exp_counts.index:
            ordered_counts.append(exp_counts[exp])
            ordered_labels.append(exp)
    
    # Add any missing categories
    for exp in exp_counts.index:
        if exp not in exp_order:
            ordered_counts.append(exp_counts[exp])
            ordered_labels.append(exp)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create bar chart
    bars = ax.bar(range(len(ordered_counts)), ordered_counts, 
                  color=sns.color_palette("Blues_r", len(ordered_counts)))
    
    # Customize the chart
    ax.set_xlabel('Years of Experience')
    ax.set_ylabel('Number of Respondents')
    ax.set_title('Game Development Experience Distribution')
    ax.set_xticks(range(len(ordered_counts)))
    ax.set_xticklabels(ordered_labels, rotation=0)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height)}',
                ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.savefig(save_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"Experience distribution chart saved as {save_path}")
    plt.show()

def create_tool_experience_heatmap(df, save_path='tool_experience_heatmap.png'):
    """Create heatmap of tool experience levels"""
    tool_columns = [
        'Houdini',
        'Unreal Engine PCG tools',
        'Blender Geometry Nodes',
        'Plugins/Tools that use Wave Function Collapse',
        'Custom code-based PCG solutions'
    ]
    
    # Check which columns exist
    available_tools = [col for col in tool_columns if col in df.columns]
    
    if not available_tools:
        print("No tool experience columns found")
        return
    
    # Define experience levels order
    exp_levels = ['No Experience', 'Limited Experience', 'Moderate Experience', 'Extensive Experience']
    
    # Create a matrix for the heatmap
    tool_data = []
    tool_labels = []
    
    for tool in available_tools:
        tool_counts = df[tool].dropna().value_counts()
        row = [tool_counts.get(level, 0) for level in exp_levels]
        tool_data.append(row)
        # Shorten tool names for better display
        short_name = tool.replace('Plugins/Tools that use ', '').replace(' PCG tools', '')
        tool_labels.append(short_name)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create heatmap
    im = ax.imshow(tool_data, cmap='YlOrRd', aspect='auto')
    
    # Set ticks and labels
    ax.set_xticks(range(len(exp_levels)))
    ax.set_yticks(range(len(tool_labels)))
    ax.set_xticklabels(exp_levels, rotation=45, ha='right')
    ax.set_yticklabels(tool_labels)
    
    # Add text annotations
    for i in range(len(tool_labels)):
        for j in range(len(exp_levels)):
            text = ax.text(j, i, tool_data[i][j],
                          ha="center", va="center", color="black" if tool_data[i][j] < np.max(tool_data)/2 else "white")
    
    # Add colorbar
    cbar = plt.colorbar(im)
    cbar.set_label('Number of Respondents', rotation=270, labelpad=15)
    
    ax.set_title('PCG Tool Experience Levels Across Survey Respondents')
    ax.set_xlabel('Experience Level')
    ax.set_ylabel('PCG Tools')
    
    plt.tight_layout()
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.savefig(save_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"Tool experience heatmap saved as {save_path}")
    plt.show()

def create_concerns_chart(df, save_path='concerns_chart.png'):
    """Create chart of primary concerns with PCG"""
    concerns_col = 'What are your primary concerns when considering procedural level generation? (Select up to 3)'
    
    if concerns_col not in df.columns:
        print(f"Column '{concerns_col}' not found")
        return
    
    # Parse multiple selections (assuming semicolon-separated)
    all_concerns = []
    for response in df[concerns_col].dropna():
        if pd.isna(response) or response == '':
            continue
        concerns = [c.strip() for c in str(response).split(';') if c.strip()]
        all_concerns.extend(concerns)
    
    # Count concerns
    concern_counts = Counter(all_concerns)
    
    # Get top 10 concerns
    top_concerns = concern_counts.most_common(10)
    
    if not top_concerns:
        print("No concerns data found")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Create horizontal bar chart
    concerns, counts = zip(*top_concerns)
    y_pos = np.arange(len(concerns))
    
    bars = ax.barh(y_pos, counts, color=sns.color_palette("Reds_r", len(concerns)))
    
    # Customize the chart
    ax.set_yticks(y_pos)
    ax.set_yticklabels([c[:50] + '...' if len(c) > 50 else c for c in concerns])
    ax.invert_yaxis()  # Top concern at the top
    ax.set_xlabel('Number of Respondents')
    ax.set_title('Primary Concerns with Procedural Level Generation')
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.5, bar.get_y() + bar.get_height()/2,
                f'{int(width)}',
                ha='left', va='center')
    
    plt.tight_layout()
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.savefig(save_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"Concerns chart saved as {save_path}")
    plt.show()

def create_pcg_frequency_chart(df, save_path='pcg_frequency.png'):
    """Create chart showing frequency of PCG usage"""
    freq_col = 'How frequently do you incorporate procedural level generation (not just world building) in your design workflow?'
    
    if freq_col not in df.columns:
        print(f"Column '{freq_col}' not found")
        return
    
    # Count frequencies
    freq_counts = df[freq_col].dropna().value_counts()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create pie chart
    colors = sns.color_palette("Set3", len(freq_counts))
    wedges, texts, autotexts = ax.pie(freq_counts.values, labels=freq_counts.index, 
                                      autopct='%1.1f%%', colors=colors, startangle=90)
    
    # Customize the chart
    ax.set_title('Frequency of Procedural Level Generation Usage')
    
    # Make percentage text more readable
    for autotext in autotexts:
        autotext.set_color('black')
        autotext.set_fontweight('bold')
    
    plt.tight_layout()
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.savefig(save_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"PCG frequency chart saved as {save_path}")
    plt.show()

def create_game_genre_interest_chart(df, save_path='genre_interest.png'):
    """Create chart showing interest levels across game genres"""
    genre_columns = [
        'Action/Adventure', 'First-person Shooters', 'Platformers', 
        'Racing games', 'Puzzle games', 'RPGs', 'Strategy games', 
        'Roguelikes / Roguelites'
    ]
    
    # Check which columns exist
    available_genres = [col for col in genre_columns if col in df.columns]
    
    if not available_genres:
        print("No genre interest columns found")
        return
    
    # Count interest levels for each genre
    interest_levels = ['Very Interested', 'Somewhat Interested', 'Not Interested']
    genre_data = []
    
    for genre in available_genres:
        counts = df[genre].dropna().value_counts()
        row = [counts.get(level, 0) for level in interest_levels]
        genre_data.append(row)
    
    # Create stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Set up the data for stacked bars
    x = np.arange(len(available_genres))
    width = 0.8
    
    colors = ['#2E8B57', '#FFA500', '#DC143C']  # Green, Orange, Red
    
    bottoms = np.zeros(len(available_genres))
    for i, level in enumerate(interest_levels):
        values = [row[i] for row in genre_data]
        ax.bar(x, values, width, bottom=bottoms, label=level, color=colors[i])
        bottoms += values
    
    # Customize the chart
    ax.set_xlabel('Game Genres')
    ax.set_ylabel('Number of Respondents')
    ax.set_title('Interest Levels Across Game Genres for PCG')
    ax.set_xticks(x)
    ax.set_xticklabels(available_genres, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(save_path, format='png', bbox_inches='tight')
    plt.savefig(save_path.replace('.png', '.pdf'), format='pdf', bbox_inches='tight')
    print(f"Genre interest chart saved as {save_path}")
    plt.show()

def generate_summary_statistics(df):
    """Generate and print summary statistics"""
    print("\n" + "="*50)
    print("SURVEY SUMMARY STATISTICS")
    print("="*50)
    
    print(f"Total Responses: {len(df)}")
    
    # Response completion rate (assuming non-null Email indicates completion)
    if 'Email' in df.columns:
        completed = df['Email'].notna().sum()
        completion_rate = (completed / len(df)) * 100
        print(f"Completion Rate: {completion_rate:.1f}%")
    
    # Role distribution
    role_col = 'How would you primarily describe your professional role?'
    if role_col in df.columns:
        print(f"\nProfessional Role Distribution:")
        for role, count in df[role_col].value_counts().head().items():
            print(f"  {role}: {count} ({count/len(df)*100:.1f}%)")
    
    # Experience distribution
    exp_col = 'How many years of experience do you have in game development?'
    if exp_col in df.columns:
        print(f"\nExperience Distribution:")
        for exp, count in df[exp_col].value_counts().items():
            print(f"  {exp}: {count} ({count/len(df)*100:.1f}%)")

def main():
    """Main function to generate all charts"""
    # Load data
    filename = 'plg_survey.csv'  # Update this path as needed
    df = load_and_clean_data(filename)
    
    if df is None:
        print("Failed to load data. Please check the file path and format.")
        return
    
    # Generate summary statistics
    generate_summary_statistics(df)
    
    # Create all charts
    print("\nGenerating charts...")
    
    create_role_distribution_chart(df)
    create_experience_chart(df)
    create_tool_experience_heatmap(df)
    create_concerns_chart(df)
    create_pcg_frequency_chart(df)
    create_game_genre_interest_chart(df)
    
    print("\nAll charts generated successfully!")
    print("Charts saved in both PNG and PDF formats for LaTeX compatibility.")

if __name__ == "__main__":
    main()