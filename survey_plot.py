"""
Survey Plot Generator

Creates PDF plots for the first 5 questions of the survey using vector graphics.
Each plot is saved as a separate PDF file with the question text as the title.
"""

from survey_analyzer import SurveyAnalyzer, SurveyPlotter
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import os

# Configure matplotlib for consistent styling across all plots
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif', 'serif'],
    'font.size': 14,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'figure.titlesize': 20,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.axisbelow': True
})

def plot_professional_role(analyzer, plotter, output_dir):
    """Create plot for professional role question."""
    question_key = 'professional_role'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 8),
        colormap='viridis',
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
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
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
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
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
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_matrix_heatmap(
        question_key,
        title=question_text,
        figsize=(14, 10),
        colormap='RdYlBu_r'
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
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
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
    
    # Get all questions from schema
    all_questions = analyzer.get_available_questions()
    
    print(f"Found {len(all_questions)} total questions in survey")
    print(f"Plotting first 5 questions...\n")
    
    created_files = []
    
    # Create plots using individual functions
    print("1. Professional Role")
    pdf_path = plot_professional_role(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    print()
    
    print("2. Years of Experience")
    pdf_path = plot_years_experience(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    print()
    
    print("3. Game Engines")
    pdf_path = plot_game_engines(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    print()
    
    print("4. Procedural Tools Experience")
    pdf_path = plot_procedural_tools_experience(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    print()
    
    print("5. Current PCG Usage")
    pdf_path = plot_current_pcg_usage(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    print()
    
    # Summary
    print("=== Summary ===")
    print(f"Total plots created: {len(created_files)}")
    print(f"Output directory: {output_dir}/")
    print("Files created:")
    for file_path in created_files:
        filename = os.path.basename(file_path)
        print(f"  - {filename}")
    
    print(f"\nAll plots saved as vector PDFs in '{output_dir}/' directory.")
    
    # Show basic survey statistics
    summary = analyzer.get_summary()
    print(f"\nSurvey statistics:")
    print(f"  - Total responses: {summary['total_responses']}")
    print(f"  - Total questions: {summary['available_questions']}")
    
    # Show data for first question as example
    example_question = 'professional_role'
    counts = analyzer.get_question_counts(example_question, filtered=False)
    print(f"\nExample data for '{example_question}':")
    for value, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {value}: {count} responses")

if __name__ == "__main__":
    main()
