"""
Survey Plot Generator
"""

from survey_analyzer import SurveyAnalyzer, SurveyPlotter, wrap_label_smart, font_size
import matplotlib.pyplot as plt
import matplotlib.backends.backend_pdf as pdf_backend
import matplotlib.figure as mpl_figure
import os
from typing import List, Tuple, Optional, Union

# Calculate chart size to ensure consistent bar heights. 
def calculate_chart_size(num_options: int) -> Tuple[float, float]:
    width = 12.0
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
        show_percentages=True,
        legend_xoffset=-0.18
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

# Show role breakdown per designer-focused usage with selectable normalization
def plot_role_per_usage(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str, normalize_by: str = 'role') -> str:
    """Plot stacked bars per designer task showing role contributions.

        Normalization modes:
        - normalize_by='task': each bar (task) sums to 100% across roles.
        - normalize_by='role' (default): each segment reflects the percentage of respondents within that role
            who selected the task (bars do not necessarily sum to 100%).

        Designer tasks considered:
        - Level layout/structure generation
        - Enemy/NPC placement
        - Mission/quest generation
        - Puzzle generation
        """
    question_key = 'current_pcg_usage'
    # Original option strings from schema (we'll map them to display/keys used by counts)
    designer_tasks = [
        'Level layout/structure generation',
        'Enemy/NPC placement',
        'Mission/quest generation',
        'Puzzle generation'
    ]

    # Map task labels using analyzer's mapping so keys match get_question_counts
    mapped_tasks = [analyzer._get_mapped_option(opt) for opt in designer_tasks]

    # Use fixed role order, but include only roles present in data; append any unexpected roles at the end
    desired_role_order = [
        'Level Designer',
        'Game Designer',
        'Technical Artist',
        'Environment Artist',
        'Programmer/Technical Designer',
        'Academic/Researcher',
        'Other'
    ]
    present_roles = set(analyzer.get_question_values('professional_role', filtered=False))
    roles = [r for r in desired_role_order if r in present_roles]
    extra_roles = sorted([r for r in present_roles if r not in desired_role_order])
    roles.extend(extra_roles)
    # Remove 'Other' role from plotting/legend if present
    roles = [r for r in roles if r != 'Other']

    # Helper to shorten role labels for legend
    def shorten_role(role: str) -> str:
        shortcuts = {
            'Level Designer': 'LD',
            'Game Designer': 'GD',
            'Technical Artist': 'TA',
            'Environment Artist': 'EA',
            'Programmer/Technical Designer': 'PTD',
            'Academic/Researcher': 'AR',
            'Other': 'O'
        }
        return shortcuts.get(role, role[:3])

    shortened_roles = [shorten_role(role) for role in roles]

    # Build role-by-task counts
    role_task_counts = {role: [0] * len(mapped_tasks) for role in roles}

    for role in roles:
        analyzer.clear_filters()
        analyzer.add_filter('professional_role', role)
        analyzer.apply_filters()
        counts = analyzer.get_question_counts(question_key, filtered=True)
        for j, task in enumerate(mapped_tasks):
            role_task_counts[role][j] = counts.get(task, 0)

    # Reset filters
    analyzer.clear_filters()

    # Compute percentages based on requested normalization
    if normalize_by == 'task':
        # Each task (bar) sums to 100% across roles
        totals_per_task = [0] * len(mapped_tasks)
        for j in range(len(mapped_tasks)):
            totals_per_task[j] = sum(role_task_counts[role][j] for role in roles)

        role_task_percent = {
            role: [
                (role_task_counts[role][j] / totals_per_task[j] * 100) if totals_per_task[j] > 0 else 0
                for j in range(len(mapped_tasks))
            ]
            for role in roles
        }
    else:
        # Default: normalize by role population size
        # Percentage of respondents within each role who selected the task
        role_totals = analyzer.get_question_counts('professional_role', filtered=False)
        role_task_percent = {
            role: [
                (role_task_counts[role][j] / max(role_totals.get(role, 0), 1) * 100)
                for j in range(len(mapped_tasks))
            ]
            for role in roles
        }

    # Figure sizing and wrapping
    label_wrap_width = 30
    wrapped_tasks = [wrap_label_smart(t, label_wrap_width) for t in mapped_tasks]
    chart_size = calculate_chart_size(len(mapped_tasks))
    # Expand width to make room for external legend
    chart_size = (12.0, chart_size[1])

    # Plot stacked horizontal bars
    fig, ax = plt.subplots(figsize=chart_size)
    # Increase axis tick label sizes slightly (+2pt)
    ax.tick_params(axis='y', labelsize=font_size)
    ax.tick_params(axis='x', labelsize=(font_size - 5))
    left = [0] * len(mapped_tasks)
    colors = plotter.role_colors

    for i, role in enumerate(roles):
        values = role_task_percent[role]
        ax.barh(wrapped_tasks, values, left=left, label=shortened_roles[i], color=colors[i])
        left = [left[k] + values[k] for k in range(len(values))]

    # X-axis limits and label
    if normalize_by == 'task':
        # Percentage scale to 100 when normalizing per task
        ax.set_xlim(0, 100)
        ax.set_xlabel('% of task responses by role', fontsize=font_size)
    else:
        # Auto-scale based on stacked totals (may exceed 100)
        stacked_totals = [sum(role_task_percent[role][j] for role in roles) for j in range(len(mapped_tasks))]
        max_total = max(stacked_totals) if stacked_totals else 0
        ax.set_xlim(0, max_total * 1.08 if max_total > 0 else 100)
        ax.set_xlabel('Accumulated percentages per role', fontsize=font_size - 1)
    ax.invert_yaxis()  # Top category at top
    # Place legend inside bottom-right where there's room
    ax.legend(loc='lower right', fontsize=20, ncol=2)

    plt.tight_layout()

    pdf_path = os.path.join(output_dir, f"q5_role_per_usage.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)

    print(f"  Saved as: {pdf_path}")
    return pdf_path

def plot_role_vs_usage_counts(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    return plot_role_vs_usage(analyzer, plotter, output_dir, use_percentages=False)

# Create side-by-side comparison of role groups for designer-focused PCG usage
def plot_role_vs_usage(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str, use_percentages: bool = True) -> str:
    """Side-by-side comparison of designer-focused PCG usage for two groups.

    Groups:
    - Design Roles: Level Designer, Game Designer
    - Technical/Art Roles: Programmer/Technical Designer, Technical Artist, Environment Artist
    
    Args:
        analyzer: SurveyAnalyzer instance
        plotter: SurveyPlotter instance
        output_dir: Directory to save the plot
        use_percentages: If True, display percentages; if False, display raw counts
    
    Note: Academic/Researcher and Other responses are excluded from this comparison.
    """
    question_key = 'current_pcg_usage'
    
    mode_str = "percentages" if use_percentages else "counts"
    print(f"Creating role vs usage comparison plot ({mode_str})")
    
    # Designer tasks to compare
    designer_tasks = [
        'Level layout/structure generation',
        'Enemy/NPC placement',
        'Mission/quest generation',
        'Puzzle generation'
    ]
    
    # Map task labels to match analyzer's mapping
    mapped_tasks = [analyzer._get_mapped_option(opt) for opt in designer_tasks]
    
    # Define role groups for comparison: Design vs Technical/Art
    design_roles = ['Level Designer', 'Game Designer']
    technical_art_roles = ['Programmer/Technical Designer', 'Technical Artist', 'Environment Artist']

    role_groups = [design_roles, technical_art_roles]
    group_labels = ['Design Roles', 'Technical/Art Roles']
    
    # Collect data for each role group
    data_sets = []
    for roles in role_groups:
        analyzer.clear_filters()
        analyzer.add_filter('professional_role', roles)
        analyzer.apply_filters()
        
        counts = analyzer.get_question_counts(question_key, filtered=True)
        
        # Count total respondents in this role group
        role_counts = analyzer.get_question_counts('professional_role', filtered=False)
        total_in_group = sum(role_counts.get(role, 0) for role in roles)
        
        # Calculate values (percentages or raw counts)
        task_values = {}
        for task in mapped_tasks:
            count = counts.get(task, 0)
            if use_percentages:
                value = (count / total_in_group * 100) if total_in_group > 0 else 0
            else:
                value = count
            task_values[task] = value
        
        data_sets.append(task_values)
    
    # Reset filters
    analyzer.clear_filters()
    
    # Prepare visualization
    label_wrap_width = 30
    wrapped_tasks = [wrap_label_smart(t, label_wrap_width) for t in mapped_tasks]
    
    # Calculate chart size
    num_options = len(mapped_tasks)
    chart_size = calculate_chart_size(num_options)
    chart_size = (chart_size[0], chart_size[1] * 1.6)  # Add extra height for comparison
    
    # Create figure
    fig, ax = plt.subplots(figsize=chart_size)
    
    # Plot settings
    y = list(range(len(mapped_tasks)))
    height = 0.8 / len(group_labels)  # Bar height for each group
    colors = ['#2E86AB', '#E67E22']  # Blue for Design, orange for Other
    
    # Plot bars for each role group
    for i, (task_values, label, color) in enumerate(zip(data_sets, group_labels, colors)):
        values = [task_values[task] for task in mapped_tasks]
        offset = height * (i - len(group_labels)/2 + 0.5)
        bars = ax.barh([pos + offset for pos in y], values, height, label=label, color=color)
        
        # Add labels on bars
        for bar in bars:
            width_val = bar.get_width()
            if width_val > 0:
                if use_percentages:
                    label_text = f'{width_val:.1f}%'
                else:
                    label_text = f'{int(width_val)}'
                ax.text(width_val + 1, bar.get_y() + bar.get_height()/2.,
                       label_text, ha='left', va='center', fontsize=font_size)
    
    # Find max value for axis scaling
    max_value = max(max(d.values()) for d in data_sets) if data_sets else 0
    
    # Styling
    ax.set_xlim(0, max_value * 1.25)
    ax.set_yticks(y)
    ax.set_yticklabels(wrapped_tasks, fontsize=font_size)
    if use_percentages:
        ax.set_xlabel('% of respondents in role group', fontsize=font_size)
    else:
        ax.set_xlabel('Number of respondents', fontsize=font_size)
    ax.invert_yaxis()  # Top task at top
    ax.tick_params(axis='x', labelsize=font_size-2)
    
    # Legend
    ax.legend(fontsize=font_size-2, loc='lower right')
    
    # Customize spines
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
    
    plt.tight_layout()
    
    # Generate filename with mode suffix
    suffix = "" if use_percentages else "_counts"
    pdf_path = os.path.join(output_dir, f"q5_role_vs_usage{suffix}.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)
    
    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Create three-way comparison of role groups for designer-focused PCG usage
def plot_role_vs_usage_3(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    """Three-way comparison of designer-focused PCG usage.

    Groups:
    - Design Roles: Level Designer, Game Designer
    - Technical Roles: Programmer/Technical Designer
    - Art Roles: Technical Artist, Environment Artist
    
    Note: Academic/Researcher and Other responses are excluded from this comparison.
    """
    question_key = 'current_pcg_usage'
    
    print(f"Creating 3-way role vs usage comparison plot")
    
    # Designer tasks to compare
    designer_tasks = [
        'Level layout/structure generation',
        'Enemy/NPC placement',
        'Mission/quest generation',
        'Puzzle generation'
    ]
    
    # Map task labels to match analyzer's mapping
    mapped_tasks = [analyzer._get_mapped_option(opt) for opt in designer_tasks]
    
    # Define role groups for comparison: Design, Technical, Art
    design_roles = ['Level Designer', 'Game Designer']
    technical_roles = ['Programmer/Technical Designer']
    art_roles = ['Technical Artist', 'Environment Artist']

    role_groups = [design_roles, technical_roles, art_roles]
    group_labels = ['Design Roles', 'Technical Roles', 'Art Roles']
    
    # Collect data for each role group
    data_sets = []
    for roles in role_groups:
        analyzer.clear_filters()
        analyzer.add_filter('professional_role', roles)
        analyzer.apply_filters()
        
        counts = analyzer.get_question_counts(question_key, filtered=True)
        
        # Filter to only designer tasks and calculate percentages
        # Count total respondents in this role group
        role_counts = analyzer.get_question_counts('professional_role', filtered=False)
        total_in_group = sum(role_counts.get(role, 0) for role in roles)
        
        # Calculate percentage of respondents in this group who selected each task
        task_percentages = {}
        for task in mapped_tasks:
            count = counts.get(task, 0)
            percentage = (count / total_in_group * 100) if total_in_group > 0 else 0
            task_percentages[task] = percentage
        
        data_sets.append(task_percentages)
    
    # Reset filters
    analyzer.clear_filters()
    
    # Prepare visualization
    label_wrap_width = 30
    wrapped_tasks = [wrap_label_smart(t, label_wrap_width) for t in mapped_tasks]
    
    # Calculate chart size
    num_options = len(mapped_tasks)
    chart_size = calculate_chart_size(num_options)
    chart_size = (chart_size[0], chart_size[1] * 1.6)  # Add extra height for comparison
    
    # Create figure
    fig, ax = plt.subplots(figsize=chart_size)
    
    # Plot settings
    y = list(range(len(mapped_tasks)))
    height = 0.8 / len(group_labels)  # Bar height for each group
    colors = ['#2E86AB', '#E67E22', '#27AE60']  # Blue for Designer, orange for Tech, green for Other
    
    # Plot bars for each role group
    for i, (percentages, label, color) in enumerate(zip(data_sets, group_labels, colors)):
        values = [percentages[task] for task in mapped_tasks]
        offset = height * (i - len(group_labels)/2 + 0.5)
        bars = ax.barh([pos + offset for pos in y], values, height, label=label, color=color)
        
        # Add percentage labels on bars
        for bar in bars:
            width_val = bar.get_width()
            if width_val > 0:
                label_text = f'{width_val:.1f}%'
                ax.text(width_val + 1, bar.get_y() + bar.get_height()/2.,
                       label_text, ha='left', va='center', fontsize=font_size)
    
    # Find max value for axis scaling
    max_value = max(max(d.values()) for d in data_sets) if data_sets else 0
    
    # Styling
    ax.set_xlim(0, max_value * 1.25)
    ax.set_yticks(y)
    ax.set_yticklabels(wrapped_tasks, fontsize=font_size)
    ax.set_xlabel('% of respondents in role group', fontsize=font_size)
    ax.invert_yaxis()  # Top task at top
    ax.tick_params(axis='x', labelsize=font_size-2)
    
    # Legend
    ax.legend(fontsize=font_size-2, loc='lower right')
    
    # Customize spines
    for spine in ax.spines.values():
        spine.set_linewidth(0.5)
    
    plt.tight_layout()
    
    pdf_path = os.path.join(output_dir, f"q5_role_vs_usage_3.pdf")
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
        colors=['#2E86AB', '#E67E22']
    )
    
    # Add secondary y-axis on the right showing normalized values (0-1)
    # aligned with the response option ticks on the left
    ax = fig.axes[0]
    ax2 = ax.twinx()
    
    # Get the tick positions from the left y-axis (where response options are)
    left_ticks = ax.get_yticks()
    
    # Set the same limits and tick positions for the secondary axis
    ax2.set_ylim(ax.get_ylim())
    ax2.set_yticks(left_ticks)
    
    # Assign normalized values (0.0, 0.25, 0.5, 0.75, 1.0) to the response options
    # Assuming response options go from best to worst (top to bottom)
    num_ticks = len(left_ticks)
    if num_ticks == 5:
        # Perfect case: 5 response options map to 5 values
        norm_labels = ['1.0', '0.75', '0.5', '0.25', '0.0']
    elif num_ticks > 1:
        # General case: distribute values evenly
        norm_labels = [f'{1.0 - i/(num_ticks-1):.2f}' for i in range(num_ticks)]
    else:
        norm_labels = ['0.5']  # Single option case
    
    ax2.set_yticklabels(norm_labels, fontsize=font_size-2)
    ax2.set_ylabel('Assigned Value (0-1)', fontsize=font_size-2)
    
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
    chart_size = calculate_chart_size(num_options) # Make the chart taller for matrix data  
    chart_size = (chart_size[0], chart_size[1] * 1.2)

    # Use matrix stacked bar chart for this matrix question
    fig = plotter.create_matrix_stacked_bar_chart(
        question_key,
        title=question_text,
        figsize=chart_size,
        colormap='plasma',
        label_wrap_width=label_wrap_width,
        show_percentages=True,
        legend_xoffset=-0.18
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

# Create grouped bar chart summarizing control vs automation themes across AI-related questions
def plot_ai_conclusions(analyzer: SurveyAnalyzer, plotter: SurveyPlotter, output_dir: str) -> str:
    """Synthesize control vs automation theme across Q10, Q17, Q18, Q19.

    X-axis contexts:
    - AI Role (Q17)
    - AI Priorities (Q18)
    - AI Concerns (Q19)

    Two bars per context:
    - Control/Transparency
    - Automation/Convenience
    """
    import numpy as np

    print("Creating plot for: AI Conclusions (Control vs Automation)")

    # Helper to map option text using analyzer's mappings
    map_opt = analyzer._get_mapped_option

    # Define themed option sets using mapped labels (short forms where available)
    # Q17 (ai_role_preference - multiple choice up to 2)
    q17_control = {"Assistant-based", "Tool-based"}
    q17_automation = {"Full automation", "Learning-based"}

    # Q18 (ai_importance_factors - multiple choice up to 2)
    q18_control = {"Creative control", "Understanding AI decisions"}
    q18_automation = {"Speed", "Novelty"}

    # Q19 (ai_concerns - multiple choice up to 2)
    # Control-oriented concerns (evidence of desire for control/transparency)
    q19_control = {"Unpredictable results", "Loss of agency", "Black box nature"}
    # Non-control concerns used to provide a contrasting bar (engineering/ops/legal)
    q19_automation = {"Performance requirements", "Integration difficulty", "Lack of specialized tools", "Copyright/IP issues", "IP/ownership"}

    # Calculation helper: percentage of respondents for a question that selected any item in target set
    def percent_selecting_any(question_key: str, target_set: set) -> float:
        df = analyzer.get_filtered_dataframe()
        if question_key not in df.columns:
            return 0.0
        series = df[question_key].dropna()
        if series.empty:
            return 0.0
        total = len(series)

        hit = 0
        for val in series:
            # Normalize to iterable of strings
            if isinstance(val, list):
                items = [map_opt(v) for v in val]
            elif isinstance(val, str):
                items = [map_opt(val)]
            else:
                # Unexpected type (e.g., dict for matrix) – treat as no hit
                items = []
            if any(item in target_set for item in items):
                hit += 1
        return (hit / total) * 100.0 if total > 0 else 0.0

    p17_ctrl = percent_selecting_any('ai_role_preference', q17_control)
    p17_auto = percent_selecting_any('ai_role_preference', q17_automation)

    p18_ctrl = percent_selecting_any('ai_importance_factors', q18_control)
    p18_auto = percent_selecting_any('ai_importance_factors', q18_automation)

    p19_ctrl = percent_selecting_any('ai_concerns', q19_control)
    p19_auto = percent_selecting_any('ai_concerns', q19_automation)

    contexts = [
        "AI Role",
        "AI Priorities",
        "AI Concerns"
    ]

    control_vals = [p17_ctrl, p18_ctrl, p19_ctrl]
    automation_vals = [p17_auto, p18_auto, p19_auto]

    # Figure sizing and style consistent with other figures (wider to fit legend)
    fig, ax = plt.subplots(figsize=(12, 6.8))

    y = np.arange(len(contexts))
    height = 0.36

    # Colors: blue for control, orange for automation
    control_color = '#2E86AB'
    automation_color = '#E67E22'

    bars1 = ax.barh(y - height/2, control_vals, height, label='Control/Transparency', color=control_color)
    bars2 = ax.barh(y + height/2, automation_vals, height, label='Automation/Convenience', color=automation_color)

    # Styling
    # Provide a little room to the right beyond 100% for labels
    right_margin = 10  # percentage points of extra space
    ax.set_xlim(0, 100 + right_margin)
    ax.set_xlabel('% of respondents', fontsize=font_size)
    wrapped_ctx = [wrap_label_smart(c, 20) for c in contexts]
    ax.set_yticks(y)
    ax.set_yticklabels(wrapped_ctx, fontsize=font_size)
    ax.invert_yaxis()  # Top context at top

    # Reference line at 50%
    ax.axvline(50, color='#888888', linewidth=1, linestyle='--', alpha=0.7)

    # Add bar labels to the right end of bars
    def add_labels_h(bars):
        for b in bars:
            width_val = b.get_width()
            if width_val > 0:
                ax.text(width_val + 1, b.get_y() + b.get_height()/2,
                        f"{width_val:.1f}%", ha='left', va='center', fontsize=font_size)

    add_labels_h(bars1)
    add_labels_h(bars2)

    # Legend and spines consistent with plotter style
    # Place legend centered below the chart
    ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.17), ncol=2, fontsize=font_size-2, frameon=True)
    for spine in ax.spines.values():
        spine.set_linewidth(plotter.chart_style['spine_linewidth'])
        spine.set_color(plotter.chart_style['spine_color'])

    plt.tight_layout()

    pdf_path = os.path.join(output_dir, f"c2_ai_conclusions.pdf")
    fig.savefig(pdf_path)
    plt.close(fig)

    print(f"  Saved as: {pdf_path}")
    return pdf_path

# Generate plots for all 20 survey questions.
def main() -> None:
    
    print("=== Survey Plot Generator ===\n")
    
    # Specify which questions to plot (1-20). Use None or empty list to plot all.
    questions_to_plot = [6]
    # questions_to_plot = list(range(1, 22))  # Plot all questions by default
    
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
        5: [plot_current_pcg_usage, plot_role_vs_usage, plot_role_vs_usage_counts],
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
        20: [plot_desired_solutions],
        21: [plot_ai_conclusions]
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