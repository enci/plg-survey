"""
Survey Plot Generator

Creates PDF plots for the first 5 questions of the survey using vector graphics.
Each plot is saved as a separate PDF file with the question text as the title.
"""

from survey_analyzer import SurveyAnalyzer, SurveyPlotter
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import os
import textwrap

def wrap_text(text, width=30):
    """
    Wrap text to specified width, breaking on word boundaries.
    
    Args:
        text: Text to wrap
        width: Maximum characters per line
        
    Returns:
        String with newlines inserted for wrapping
    """
    if len(text) <= width:
        return text
    
    # Use textwrap to break on word boundaries
    wrapped_lines = textwrap.wrap(text, width=width, break_long_words=False)
    return '\n'.join(wrapped_lines)

def wrap_labels(labels, width=25):
    """
    Wrap a list of labels for better display on axes.
    
    Args:
        labels: List of label strings
        width: Maximum characters per line
        
    Returns:
        List of wrapped label strings
    """
    return [wrap_text(label, width) for label in labels]

# Configure matplotlib for consistent styling across all plots
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif', 'serif'],
    'font.size': 16,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 18,
    'ytick.labelsize': 18,
    'legend.fontsize': 16,
    'figure.titlesize': 20,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.axisbelow': True,
    'axes.titlelocation': 'center',
    'axes.titlesize': 0,
    'font.weight': 'bold'  # Make heatmap labels bold
})

def plot_professional_role(analyzer, plotter, output_dir):
    """Create plot for professional role question."""
    question_key = 'professional_role'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Wrap the title text for better display
    wrapped_title = wrap_text(question_text, width=60)
        
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 6),  # Increased height for wrapped labels
        colormap='Dark2',
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_years_experience(analyzer, plotter, output_dir):
    """Create plot for years of experience question."""
    question_key = 'years_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Wrap the title text for better display
    wrapped_title = wrap_text(question_text, width=60)
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 8),
        colormap='plasma',
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_game_engines(analyzer, plotter, output_dir):
    """Create plot for game engines question."""
    question_key = 'game_engines'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Wrap the title text for better display
    wrapped_title = wrap_text(question_text, width=60)
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 8),
        colormap='tab10',
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_procedural_tools_experience(analyzer, plotter, output_dir):
    """Create plot for procedural tools experience question."""
    question_key = 'procedural_tools_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Wrap the title text for better display
    wrapped_title = wrap_text(question_text, width=60)
    
    print(f"Creating plot for: {question_text}")
    
    # Use stacked bar chart for better readability of matrix data
    fig = plotter.create_matrix_stacked_bar_chart(
        question_key,
        title=wrapped_title,
        figsize=(14, 10),
        colormap='RdYlBu_r',
        horizontal=True
    )
    
    pdf_path = os.path.join(output_dir, f"{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_current_pcg_usage(analyzer, plotter, output_dir):
    """Create plot for current PCG usage question."""
    question_key = 'current_pcg_usage'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Wrap the title text for better display
    wrapped_title = wrap_text(question_text, width=60)
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 8),
        colormap='Set2',
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def main():
    """Generate plots for the first 5 survey questions."""
    
    print("=== Survey Plot Generator ===\n")
    
    # Create output directory
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize analyzer and plotter
    analyzer = SurveyAnalyzer(
        'survey-questions-schema.json',
        'procedural-level-generation-survey.json'
    )
    plotter = SurveyPlotter(analyzer)
            
    created_files = []
    
    # Create plots using individual functions
    pdf_path = plot_professional_role(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    pdf_path = plot_years_experience(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    pdf_path = plot_game_engines(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    pdf_path = plot_procedural_tools_experience(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    pdf_path = plot_current_pcg_usage(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Summary
    print("=== Summary ===")
    print(f"Total plots created: {len(created_files)}")
    print(f"Output directory: {output_dir}/")
    print("Files created:")
    for file_path in created_files:
        filename = os.path.basename(file_path)
        print(f"  - {filename}")

if __name__ == "__main__":
    main()