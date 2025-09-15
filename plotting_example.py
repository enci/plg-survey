"""
Plotting example using SurveyAnalyzer

This script demonstrates how to create visualizations from filtered survey data.
"""

from survey_analyzer import SurveyAnalyzer, FilterLogic
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter

def create_bar_chart(data_dict, title, xlabel, ylabel, filename=None, top_n=None):
    """Create a horizontal bar chart from count data."""
    # Sort by count and optionally limit to top N
    sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
    if top_n:
        sorted_items = sorted_items[:top_n]
    
    labels, values = zip(*sorted_items) if sorted_items else ([], [])
    
    plt.figure(figsize=(10, max(6, len(labels) * 0.4)))
    bars = plt.barh(range(len(labels)), values)
    plt.yticks(range(len(labels)), labels)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.tight_layout()
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        plt.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                str(values[i]), ha='left', va='center')
    
    plt.gca().invert_yaxis()  # Top item at top
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Chart saved as {filename}")
    
    plt.show()

def create_comparison_chart(analyzer, question, filters_list, labels, title, filename=None):
    """Create a comparison chart for the same question across different filters."""
    data_sets = []
    
    for i, (filters, label) in enumerate(zip(filters_list, labels)):
        analyzer.clear_filters()
        
        # Apply filters for this dataset
        for filter_config in filters:
            analyzer.add_filter(
                filter_config['question'], 
                filter_config['value'], 
                filter_config.get('negate', False)
            )
        
        if len(filters) > 0:
            analyzer.set_filter_logic(filters[0].get('logic', FilterLogic.AND))
            analyzer.apply_filters()
        
        # Get counts for the question
        counts = analyzer.get_question_counts(question)
        data_sets.append((label, counts))
    
    # Find all unique options
    all_options = set()
    for _, counts in data_sets:
        all_options.update(counts.keys())
    all_options = sorted(all_options)
    
    # Prepare data for plotting
    x = np.arange(len(all_options))
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for i, (label, counts) in enumerate(data_sets):
        values = [counts.get(option, 0) for option in all_options]
        offset = width * (i - len(data_sets)/2 + 0.5)
        bars = ax.bar(x + offset, values, width, label=label, alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
    
    ax.set_xlabel('Options')
    ax.set_ylabel('Count')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(all_options, rotation=45, ha='right')
    ax.legend()
    
    plt.tight_layout()
    
    if filename:
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        print(f"Comparison chart saved as {filename}")
    
    plt.show()

def main():
    """Create example visualizations"""
    
    # Initialize analyzer
    analyzer = SurveyAnalyzer(
        schema_path='survey-questions-schema.json',
        data_path='procedural-level-generation-survey.json'
    )
    
    # Chart 1: Overall game engine usage
    print("=== Creating Chart 1: Game Engine Usage ===")
    analyzer.clear_filters()
    engine_counts = analyzer.get_question_counts('game_engines', filtered=False)
    create_bar_chart(
        engine_counts,
        'Game Engine Usage (All Respondents)',
        'Number of Users',
        'Game Engine',
        'plots/game_engines_overall.png'
    )
    
    # Chart 2: Primary concerns by experience level comparison
    print("\n=== Creating Chart 2: Primary Concerns by Experience ===")
    
    # Define the filter configurations for comparison
    filters_config = [
        [{'question': 'years_experience', 'value': ['0-2 years']}],  # Beginners
        [{'question': 'years_experience', 'value': ['10+ years']}],   # Experts
    ]
    labels = ['Beginners (0-2 years)', 'Experts (10+ years)']
    
    create_comparison_chart(
        analyzer,
        'primary_concerns',
        filters_config,
        labels,
        'Primary Concerns: Beginners vs Experts',
        'plots/concerns_comparison.png'
    )
    
    # Chart 3: Tool satisfaction among different roles
    print("\n=== Creating Chart 3: Tool Views by Professional Role ===")
    
    # Get unique professional roles first
    analyzer.clear_filters()
    all_roles = analyzer.get_question_values('professional_role', filtered=False)
    role_counts = Counter(all_roles)
    
    # Focus on roles with enough responses (>= 10)
    significant_roles = [role for role, count in role_counts.items() if count >= 10]
    
    filters_config = []
    labels = []
    for role in significant_roles:
        filters_config.append([{'question': 'professional_role', 'value': role}])
        labels.append(role)
    
    create_comparison_chart(
        analyzer,
        'tool_view',
        filters_config,
        labels,
        'Tool Satisfaction by Professional Role',
        'plots/tool_views_by_role.png'
    )
    
    # Chart 4: PCG Usage frequency among experienced Unity users
    print("\n=== Creating Chart 4: PCG Usage Frequency (Experienced Unity Users) ===")
    analyzer.clear_filters()
    analyzer.add_filter('game_engines', 'Unity')
    analyzer.add_filter('years_experience', ['6-10 years', '10+ years'])
    analyzer.apply_filters()
    
    usage_counts = analyzer.get_question_counts('level_generation_frequency')
    create_bar_chart(
        usage_counts,
        'PCG Usage Frequency\n(Experienced Unity Developers)',
        'Number of Respondents',
        'Usage Frequency',
        'plots/pcg_usage_unity_experienced.png'
    )
    
    # Chart 5: Critical factors for different experience levels
    print("\n=== Creating Chart 5: Critical Factors by Experience Level ===")
    
    filters_config = [
        [{'question': 'years_experience', 'value': ['0-2 years']}],
        [{'question': 'years_experience', 'value': ['3-5 years']}],
        [{'question': 'years_experience', 'value': ['6-10 years']}],
        [{'question': 'years_experience', 'value': ['10+ years']}],
    ]
    labels = ['0-2 years', '3-5 years', '6-10 years', '10+ years']
    
    create_comparison_chart(
        analyzer,
        'critical_factors',
        filters_config,
        labels,
        'Critical Factors by Experience Level',
        'plots/critical_factors_by_experience.png'
    )
    
    print("\n=== All charts created successfully! ===")
    print("Charts saved in the 'plots/' directory.")

if __name__ == "__main__":
    # Create plots directory if it doesn't exist
    import os
    os.makedirs('plots', exist_ok=True)
    
    main()
