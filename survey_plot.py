"""
Survey Plot Generator

Creates PDF plots for the first 15 questions of the survey using vector graphics.
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
    'font.size': 20,
    'axes.titlesize': 18,
    'axes.labelsize': 20,
    'xtick.labelsize': 16,
    'ytick.labelsize': 20,
    'legend.fontsize': 18,
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
    
    # Local wrapping settings for this chart
    title_wrap_width = None  # No title wrapping
    label_wrap_width = None  # No label wrapping
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text

    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 6),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )

    
    pdf_path = os.path.join(output_dir, f"q1_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_years_experience(analyzer, plotter, output_dir):
    """Create plot for years of experience question."""
    question_key = 'years_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = None  # No title wrapping
    label_wrap_width = None  # No label wrapping
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 4.5),
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        colormap='Blues'
    )
    
    pdf_path = os.path.join(output_dir, f"q2_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_game_engines(analyzer, plotter, output_dir):
    """Create plot for game engines question."""
    question_key = 'game_engines'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = None  # No title wrapping
    label_wrap_width = 25   # Wrap long engine names
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    # Create role stacked chart showing cumulative professional role breakdown
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 5),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q3_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_procedural_tools_experience(analyzer, plotter, output_dir):
    """Create plot for procedural tools experience question."""
    question_key = 'procedural_tools_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = None   # Wrap titles for better readability
    label_wrap_width = 30   # Wrap tool names for matrix chart
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    # Use stacked bar chart for better readability of matrix data
    fig = plotter.create_matrix_stacked_bar_chart(
        question_key,
        title=wrapped_title,
        figsize=(12, 6),
        colormap='bwr',
        horizontal=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q4_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_procedural_tools_experience_comparison(analyzer, plotter, output_dir):
    """Create comparison plot for procedural tools experience between artist and designer/programmer roles."""
    question_key = 'procedural_tools_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating comparison plot for: {question_text}")
    
    # Define role groups for comparison
    artist_roles = ['Technical Artist', 'Environment Artist']
    designer_programmer_roles = ['Level Designer', 'Game Designer', 'Programmer/Technical Designer']
    
    # Create filter configurations for comparison
    filter_configs = [
        {'filters': [{'question': 'professional_role', 'value': artist_roles}]},
        {'filters': [{'question': 'professional_role', 'value': designer_programmer_roles}]}
    ]
    
    labels = ['Artist Roles', 'Designer/Programmer Roles']
    
    # Create comparison chart
    title = f"Procedural Tools Experience:\nArtist vs Designer/Programmer Roles"
    
    fig = plotter.create_comparison_chart(
        question_key,
        filter_configs,
        labels,
        title=title,
        figsize=(12, 10),
        show_percentages=True,
        label_wrap_width=30
    )
    
    pdf_path = os.path.join(output_dir, f"q4_comparison_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_current_pcg_usage(analyzer, plotter, output_dir):
    """Create plot for current PCG usage question."""
    question_key = 'current_pcg_usage'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap category labels
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 6),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q5_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_level_generation_frequency(analyzer, plotter, output_dir):
    """Create plot for level generation frequency question."""
    question_key = 'level_generation_frequency'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 4.5),
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"q6_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)

    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_level_generation_frequency_comparison(analyzer, plotter, output_dir):
    """Create comparison plot for level generation frequency between design and artist roles."""
    question_key = 'level_generation_frequency'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating comparison plot for: {question_text}")
    
    # Define role groups for comparison - design roles vs artist roles
    design_roles = ['Level Designer', 'Game Designer']
    artist_roles = ['Technical Artist', 'Environment Artist']
    
    # Create filter configurations for comparison
    filter_configs = [
        {'filters': [{'question': 'professional_role', 'value': design_roles}]},
        {'filters': [{'question': 'professional_role', 'value': artist_roles}]}
    ]
    
    labels = ['Design Roles', 'Artist Roles']
    
    # Create comparison chart
    title = f"Frequency of Procedural Level Generation Usage:\nDesign vs Artist Roles"
    
    fig = plotter.create_comparison_chart(
        question_key,
        filter_configs,
        labels,
        title=title,
        figsize=(12, 8),
        show_percentages=True,
        label_wrap_width=18
    )
    
    pdf_path = os.path.join(output_dir, f"q6_comparison_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_primary_concerns(analyzer, plotter, output_dir):
    """Create plot for primary concerns question."""
    question_key = 'primary_concerns'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap long labels for concerns
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 8),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q7_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_primary_concerns_comparison(analyzer, plotter, output_dir):
    """Create comparison plot for primary concerns between design and artist roles."""
    question_key = 'primary_concerns'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating comparison plot for: {question_text}")
    
    # Define role groups for comparison - design roles vs artist roles
    design_roles = ['Level Designer', 'Game Designer', 'Programmer/Technical Designer']
    artist_roles = ['Technical Artist', 'Environment Artist']
    
    # Create filter configurations for comparison
    filter_configs = [
        {'filters': [{'question': 'professional_role', 'value': design_roles}]},
        {'filters': [{'question': 'professional_role', 'value': artist_roles}]}
    ]
    
    labels = ['Design Roles', 'Artist Roles']
    
    # Create comparison chart
    title = f"Primary Concerns When Considering Procedural Level Generation:\nDesign vs Artist Roles"
    
    fig = plotter.create_comparison_chart(
        question_key,
        filter_configs,
        labels,
        title=title,
        figsize=(12, 8),
        show_percentages=True,
        label_wrap_width=30
    )
    
    pdf_path = os.path.join(output_dir, f"q7_comparison_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_tool_view(analyzer, plotter, output_dir):
    """Create plot for tool view question."""
    question_key = 'tool_view'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 35   # Wrap long labels for tool views
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 8),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q8_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_critical_factors(analyzer, plotter, output_dir):
    """Create plot for critical factors question."""
    question_key = 'critical_factors'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap labels for factors
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 8),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q9_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_node_tool_features(analyzer, plotter, output_dir):
    """Create plot for node tool features question using position distribution visualization."""
    question_key = 'node_tool_features'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 60   # Wrap long title
    label_wrap_width = 30   # Wrap long labels for features
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    # Use position distribution visualization to show ranking patterns
    fig = plotter.create_ranking_position_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 9),
        colormap='Set3',
        max_rank=3,  # Top 3 ranking as specified in the question
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q10_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_realtime_feedback_importance(analyzer, plotter, output_dir):
    """Create plot for realtime feedback importance question."""
    question_key = 'realtime_feedback_importance'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 4),
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"q11_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_preferred_approach(analyzer, plotter, output_dir):
    """Create plot for preferred approach question."""
    question_key = 'preferred_approach'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 40   # Wrap long labels for approaches
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 7),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q12_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_integration_preference(analyzer, plotter, output_dir):
    """Create plot for integration preference question."""
    question_key = 'integration_preference'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 35   # Wrap labels for integration options
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=(12, 5),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q13_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_genre_interest(analyzer, plotter, output_dir):
    """Create plot for genre interest question."""
    question_key = 'genre_interest'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 60   # Wrap long title
    label_wrap_width = 20   # Wrap genre labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    # Use matrix stacked bar chart for this matrix question
    fig = plotter.create_matrix_stacked_bar_chart(
        question_key,
        title=wrapped_title,
        figsize=(12, 6),
        colormap='RdYlGn',  # Green for interested, red for not interested
        horizontal=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q14_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_level_representation(analyzer, plotter, output_dir):
    """Create plot for level representation question."""
    question_key = 'level_representation'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 60   # Wrap long title
    label_wrap_width = 35   # Wrap representation method labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 7),
        colormap='Dark2',
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q15_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_most_useful_approach(analyzer, plotter, output_dir):
    """Create plot for most useful approach question."""
    question_key = 'most_useful_approach'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 50   # Wrap long title
    label_wrap_width = 40   # Wrap approach labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 6),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q16_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_ai_role_preference(analyzer, plotter, output_dir):
    """Create plot for AI role preference question."""
    question_key = 'ai_role_preference'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 60   # Wrap long title
    label_wrap_width = 42   # Wrap AI role labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 7),
        colormap='Dark2',
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q17_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_ai_importance_factors(analyzer, plotter, output_dir):
    """Create plot for AI importance factors question."""
    question_key = 'ai_importance_factors'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 60   # Wrap long title
    label_wrap_width = 30   # Wrap factor labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 6.5),
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q18_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_ai_concerns(analyzer, plotter, output_dir):
    """Create plot for AI concerns question."""
    question_key = 'ai_concerns'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 60   # Wrap long title
    label_wrap_width = 30   # Wrap concern labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 8),
        colormap='Dark2',
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q19_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_desired_solutions(analyzer, plotter, output_dir):
    """Create plot for desired solutions question."""
    question_key = 'desired_solutions'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    title_wrap_width = 50   # Wrap long title
    label_wrap_width = 35   # Wrap solution labels
    
    # Wrap the title text for better display if specified
    if title_wrap_width:
        wrapped_title = wrap_text(question_text, width=title_wrap_width)
    else:
        wrapped_title = question_text
    
    print(f"Creating plot for: {question_text}")
    
    fig = plotter.create_bar_chart(
        question_key,
        title=wrapped_title,
        horizontal=True,
        figsize=(12, 8),
        colormap='Dark2',
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q20_{question_key}.pdf")
    fig.savefig(pdf_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

def main():
    """Generate plots for all 20 survey questions."""
    
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
    
    # Create plots using individual functions with local wrapping settings
    # Questions 1
    #pdf_path = plot_professional_role(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 2
    pdf_path = plot_years_experience(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Question 3
    #pdf_path = plot_game_engines(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 4: Matrix chart with wrapping for better readability
    #pdf_path = plot_procedural_tools_experience(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 4 Comparison: Artist vs Designer/Programmer roles
    #pdf_path = plot_procedural_tools_experience_comparison(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 5: Role stacked chart
    #pdf_path = plot_current_pcg_usage(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)    
    
    # Question 6: Role stacked chart
    #pdf_path = plot_level_generation_frequency(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 6 Comparison: Level generation frequency across professional roles
    #pdf_path = plot_level_generation_frequency_comparison(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 7: Role stacked chart
    #pdf_path = plot_primary_concerns(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 7 Comparison: Primary concerns across professional roles
    #pdf_path = plot_primary_concerns_comparison(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 8: Role stacked chart
    pdf_path = plot_tool_view(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Question 9: Role stacked chart
    pdf_path = plot_critical_factors(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Questions 10: Ranking question with position distribution
    # pdf_path = plot_node_tool_features(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Question 11: Role stacked chart
    pdf_path = plot_realtime_feedback_importance(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Question 12: Role stacked chart
    pdf_path = plot_preferred_approach(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Question 13: Role stacked chart
    pdf_path = plot_integration_preference(analyzer, plotter, output_dir)
    created_files.append(pdf_path)
    
    # Questions 14
    #pdf_path = plot_genre_interest(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Questions 15
    #pdf_path = plot_level_representation(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Questions 16
    #pdf_path = plot_most_useful_approach(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Questions 17
    #pdf_path = plot_ai_role_preference(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Questions 18
    #pdf_path = plot_ai_importance_factors(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Questions 19
    #pdf_path = plot_ai_concerns(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
    # Questions 20
    #pdf_path = plot_desired_solutions(analyzer, plotter, output_dir)
    #created_files.append(pdf_path)
    
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