"""
Survey Plot Generator
"""

from survey_analyzer import SurveyAnalyzer, SurveyPlotter, wrap_label_smart
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import matplotlib.figure as mpl_figure
import os
from typing import List, Tuple, Optional, Union

# Calculate chart size to ensure consistent bar heights. 
def calculate_chart_size(num_options: int) -> Tuple[float, float]:
    width = 12
    consistent_bar_height = 0.8  # Consistent height per bar
    base_padding = 1.0  # Space for legend and padding
    height = base_padding + (num_options * consistent_bar_height)
    return (width, height)

# Get the number of unique response options for a question.
def get_question_options_count(analyzer: SurveyAnalyzer, question_key: str) -> int:
    try:
        # Get question info to check type
        question_info = analyzer.get_question_info(question_key)
        question_type = question_info.get('type', 'single_choice')
        
        # For matrix questions, return the number of items (rows)
        if question_type == 'matrix':
            items = question_info.get('items', [])
            return len(items)
        
        # First try to get predefined options from schema
        options = analyzer.get_question_options(question_key)

        # check which options are actually used in responses
        responses = analyzer.get_question_values(question_key, filtered=False)
        if not responses:
            return len(options)  # No responses, return total options
        
        # Handle multi-select questions (lists in responses) - already handled by get_question_values
        unique_options = set(responses)
        return len(unique_options)

    except Exception as e:
        print(f"Warning: Could not get options count for {question_key}: {e}")
        return 5  # Default fallback if there's any error
    
# Create plot for professional role question.
def plot_professional_role(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'professional_role'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 0
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    # chart_size = (chart_size[0], chart_size[1] + 0.5)

    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width
    )
    
    pdf_path = os.path.join(output_dir, f"q1_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for years of experience question.
def plot_years_experience(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'years_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = None
        
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=chart_size,
        color='grey',
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        colormap='tab20b'
    )
    
    pdf_path = os.path.join(output_dir, f"q2_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for game engines question.
def plot_game_engines(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'game_engines'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)

    # Local wrapping settings for this chart
    label_wrap_width = 25   # Wrap long engine names
    
    print(f"Creating plot for: {question_text}")
    
    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    # Create role stacked chart showing cumulative professional role breakdown
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        xlim_padding=12,
        legend_ncol=2
    )
    
    pdf_path = os.path.join(output_dir, f"q3_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for procedural tools experience question.
def plot_procedural_tools_experience(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'procedural_tools_experience'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)        
    print(f"Creating plot for: {question_text}")
    
    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    # Make the chart taller for matrix data
    chart_size = (chart_size[0], chart_size[1] * 1.2)
    
    
    # Use stacked bar chart for better readability of matrix data
    fig = plotter.create_matrix_stacked_bar_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        colormap='plasma', 
        label_wrap_width=25,
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"q4_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create comparison plot for procedural tools experience between artist and designer/programmer roles.
def plot_procedural_tools_experience_comparison(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
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
    
    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)  # Comparison charts need more height
    
    fig = plotter.create_comparison_chart(
        question_key,
        filter_configs,
        labels,
        title=title,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=30
    )
    
    pdf_path = os.path.join(output_dir, f"q4_comparison_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for current PCG usage question.
def plot_current_pcg_usage(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'current_pcg_usage'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    analyzer.clear_filters()

    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap category labels
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        legend_fontsize=21,
        xlim_padding=12,
    )
    
    pdf_path = os.path.join(output_dir, f"q5_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path


# Create plot for current PCG usage question.
def plot_current_pcg_usage_artist(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'current_pcg_usage'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    analyzer.clear_filters()

    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap category labels
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    analyzer.add_filter('professional_role', ['Technical Artist', 'Environment Artist'])
    fig = plotter.create_bar_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=chart_size,
        color='green',  # Use green for artist PCG usage chart
        show_percentages=True,
        filtered=True,
        label_wrap_width=label_wrap_width)
    
    pdf_path = os.path.join(output_dir, f"q5_{question_key}_artist.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for level generation frequency question.
def plot_level_generation_frequency(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'level_generation_frequency'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")
    analyzer.clear_filters()    

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=18,
        legend_loc = 'upper right',
        legend_fontsize=19,
        legend_ncol=2,
        label_fontsize_offset=-2,
        xlim_padding=8
    )
    
    pdf_path = os.path.join(output_dir, f"q6_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)

    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create comparison plot for level generation frequency between design and artist roles.
def plot_level_generation_frequency_comparison(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
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
        figsize=(12, 10),
        show_percentages=True,
        label_wrap_width=18,
        colors=['#9E2DB5', '#50A326']
    )
    
    pdf_path = os.path.join(output_dir, f"q6_comparison_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for primary concerns question.
def plot_primary_concerns(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'primary_concerns'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap long labels for concerns
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    analyzer.clear_filters()
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        label_fontsize_offset=-3,
        legend_ncol=2,
        legend_fontsize=18,
        xlim_padding=10
    )
    
    pdf_path = os.path.join(output_dir, f"q7_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create comparison plot for primary concerns between design and artist roles.
def plot_primary_concerns_comparison(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'primary_concerns'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating comparison plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
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
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=30
    )
    
    pdf_path = os.path.join(output_dir, f"q7_comparison_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for tool view question.
def plot_tool_view(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'tool_view'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 35   # Wrap long labels for tool views
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    analyzer.clear_filters()    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        legend_fontsize=21,
        legend_loc='upper right',
        xlim_padding=7
    )
    
    pdf_path = os.path.join(output_dir, f"q8_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for critical factors question.
def plot_critical_factors(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'critical_factors'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap labels for factors
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        legend_ncol=3,
        xlim_padding=13
    )
    
    pdf_path = os.path.join(output_dir, f"q9_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for node tool features question using position distribution visualization.
def plot_node_tool_features(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'node_tool_features'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)    
        
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = 8  # Fixed number of options for this question
    chart_size = calculate_chart_size(num_options)
    
    # Use position distribution visualization to show ranking patterns
    fig = plotter.create_ranking_position_chart(
        question_key,
        title=question_text,
        horizontal=True,
        figsize=chart_size,
        colormap='plasma',
        max_rank=3,  # Top 3 ranking as specified in the question
        label_wrap_width=30,
        label_fontsize_offset=-5,
        legend_fontsize=19,
        xlabel_fontsize=18
    )
    
    pdf_path = os.path.join(output_dir, f"q10_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for realtime feedback importance question.
def plot_realtime_feedback_importance(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'realtime_feedback_importance'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        legend_fontsize=20,
        legend_ncol=1,
        xlim_padding=22
    )
    
    pdf_path = os.path.join(output_dir, f"q11_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for preferred approach question.
def plot_preferred_approach(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'preferred_approach'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)    
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=45,
        legend_fontsize=21,
        xlim_padding=10,
        legend_ncol=2
    )
    
    pdf_path = os.path.join(output_dir, f"q12_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for integration preference question.
def plot_integration_preference(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'integration_preference'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")
    
    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=35,
        label_fontsize_offset=-2,
        legend_ncol=3,
        legend_fontsize=19,
        xlim_padding=8

    )
    
    pdf_path = os.path.join(output_dir, f"q13_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for genre interest question.
def plot_genre_interest(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'genre_interest'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 40   # Wrap genre labels
        
    print(f"Creating plot for: {question_text}")

     # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    # Use matrix stacked bar chart for this matrix question
    fig = plotter.create_matrix_stacked_bar_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        colormap='plasma',
        label_wrap_width=label_wrap_width,
        show_percentages=True
    )
    
    pdf_path = os.path.join(output_dir, f"q14_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for level representation question.
def plot_level_representation(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'level_representation'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
        
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=50,
        xlim_padding=12
    )
    
    pdf_path = os.path.join(output_dir, f"q15_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for most useful approach question.
def plot_most_useful_approach(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'most_useful_approach'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
        
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=35,
        xlim_padding=15,
        legend_loc='upper right',
    )
    
    pdf_path = os.path.join(output_dir, f"q16_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for AI role preference question.
def plot_ai_role_preference(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'ai_role_preference'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
        
    print(f"Creating plot for: {question_text}")
    
    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=35,
        legend_ncol=3,
        legend_fontsize=18,
        xlim_padding=10
    )
    
    pdf_path = os.path.join(output_dir, f"q17_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for AI importance factors question.
def plot_ai_importance_factors(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'ai_importance_factors'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap factor labels
    
    print(f"Creating plot for: {question_text}")

     # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)

    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        xlim_padding=20
        )
    
    pdf_path = os.path.join(output_dir, f"q18_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for AI concerns question.
def plot_ai_concerns(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'ai_concerns'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    # Local wrapping settings for this chart
    label_wrap_width = 30   # Wrap concern labels
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)  # Use consistent sizing for role stacked charts

    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=label_wrap_width,
        label_fontsize_offset=-4,
        xlim_padding=25
    )
    
    pdf_path = os.path.join(output_dir, f"q19_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create plot for desired solutions question.
def plot_desired_solutions(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    question_key = 'desired_solutions'
    question_info = analyzer.get_question_info(question_key)
    question_text = question_info.get('question', question_key)
    
    print(f"Creating plot for: {question_text}")

    # Calculate dynamic chart size based on number of response options
    num_options = get_question_options_count(analyzer, question_key)
    chart_size = calculate_chart_size(num_options)
    
    fig = plotter.create_role_stacked_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        show_percentages=True,
        label_wrap_width=30,
        xlim_padding=18
    )
    
    pdf_path = os.path.join(output_dir, f"q20_{question_key}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Generate plots for all 20 survey questions.
def main() -> None:
    
    print("=== Survey Plot Generator ===\n")
    
    # Specify which questions to plot (1-20). Use None or empty list to plot all.
    # questions_to_plot = [15, 16, 17, 18 , 19, 20]
    questions_to_plot = list(range(1, 21))  # Plot all questions by default
    
    # Create output directory
    output_dir = "plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize analyzer and plotter
    analyzer = SurveyAnalyzer(
        'survey-questions-schema.json',
        'procedural-level-generation-survey.json',
        'survey-options-mapping.json'  # Load option mappings for shortened text
    )
    plotter = SurveyPlotter(analyzer)
            
    created_files = []
    
    # Define plot functions for each question
    plot_functions = {
        1: [plot_professional_role],
        2: [plot_years_experience],
        3: [plot_game_engines],
        4: [plot_procedural_tools_experience],
        5: [plot_current_pcg_usage],
        6: [plot_level_generation_frequency, plot_level_generation_frequency_comparison],
        7: [plot_primary_concerns],
        8: [plot_tool_view],
        9: [plot_critical_factors],
        10: [plot_node_tool_features],
        11: [plot_realtime_feedback_importance],
        12: [plot_preferred_approach],
        13: [plot_integration_preference],
        14: [plot_genre_interest],
        15: [plot_level_representation],
        16: [plot_most_useful_approach],
        17: [plot_ai_role_preference],
        18: [plot_ai_importance_factors],
        19: [plot_ai_concerns],
        20: [plot_desired_solutions]
    }
    
    # Generate plots for selected questions
    for question in sorted(set(questions_to_plot)):  # Use set to remove duplicates
        if question in plot_functions:
            for plot_func in plot_functions[question]:
                pdf_path = plot_func(analyzer, plotter, output_dir)
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