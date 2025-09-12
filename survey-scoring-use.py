#!/usr/bin/env python3
"""
Complete Survey Scoring Analysis Tool - Fixed Version
Extracts data from survey files and tests different scoring methodologies
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Hardcoded survey file path
SURVEY_FILE = "procedural-level-generation-survey.json"

def load_survey_data():
    """
    Load survey data from the hardcoded JSON file
    
    Returns:
        list of survey responses
    """
    file_path = Path(SURVEY_FILE)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Survey file not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_frequency_data(survey_data, role_mapping=None):
    """
    Extract frequency response counts from survey data
    
    Args:
        survey_data: list of survey responses
        role_mapping: optional dict to customize role categorization
        
    Returns:
        dict with frequency counts by role category
    """
    
    # Default role categorization
    if role_mapping is None:
        role_mapping = {
            'artists': ['Environment Artist', 'Technical Artist', 'Character / General Artist'],
            'designers': ['Level Designer', 'Game Designer'],
            'programmers': ['Programmer/Technical Designer'],
            'researchers': ['Academic/Researcher']
        }
    
    # Initialize counters for each category
    frequency_data = {}
    for category in role_mapping.keys():
        frequency_data[category] = {}
    
    # Define expected frequency categories
    frequency_categories = [
        "Always (essential part of workflow)",
        "Often (most projects)", 
        "Sometimes (about half of projects)",
        "Rarely (a few projects)",
        "Never"
    ]
    
    # Process each response
    valid_responses = 0
    for response in survey_data:
        # Skip if missing required fields
        if 'level_generation_frequency' not in response or 'professional_role' not in response:
            continue
            
        if not response['level_generation_frequency'] or not response['professional_role']:
            continue
            
        role = response['professional_role']
        frequency = response['level_generation_frequency']
        valid_responses += 1
        
        # Find which category this role belongs to
        for category, roles in role_mapping.items():
            if role in roles:
                frequency_data[category][frequency] = frequency_data[category].get(frequency, 0) + 1
                break
    
    # Ensure all frequency categories are represented with 0 if no responses
    for category in frequency_data.keys():
        for freq in frequency_categories:
            if freq not in frequency_data[category]:
                frequency_data[category][freq] = 0
    
    # Calculate totals
    totals = {}
    for category in frequency_data.keys():
        totals[category] = sum(frequency_data[category].values())
    
    print(f"Processed {valid_responses} valid survey responses")
    return frequency_data, totals

def calculate_weighted_score(responses, weights, total_responses):
    """
    Calculate weighted score for a set of responses
    
    Args:
        responses: dict with frequency labels as keys and counts as values
        weights: dict with frequency labels as keys and weight values (0-1) as values
        total_responses: total number of responses for percentage calculation
    
    Returns:
        weighted_score: score between 0-100
    """
    if total_responses == 0:
        return 0
        
    weighted_sum = 0
    for freq_label, count in responses.items():
        if freq_label in weights:
            percentage = count / total_responses
            weighted_sum += weights[freq_label] * percentage
    
    return weighted_sum * 100  # Convert to 0-100 scale

def analyze_scoring_methodologies(frequency_data, totals, categories_to_compare=['artists', 'designers']):
    """
    Test different weighting schemes and compare results
    
    Args:
        frequency_data: dict with frequency counts by role category
        totals: dict with total responses by role category
        categories_to_compare: list of categories to compare
        
    Returns:
        DataFrame with results
    """
    
    # Define different weighting schemes
    weighting_schemes = {
        "Original Linear": {
            "Always (essential part of workflow)": 1.0,
            "Often (most projects)": 0.75,
            "Sometimes (about half of projects)": 0.5,
            "Rarely (a few projects)": 0.25,
            "Never": 0.0
        },
        
        "Exponential Scale": {
            "Always (essential part of workflow)": 1.0,
            "Often (most projects)": 0.8,
            "Sometimes (about half of projects)": 0.5,
            "Rarely (a few projects)": 0.2,
            "Never": 0.0
        },
        
        "Adoption-Stage Based": {
            "Always (essential part of workflow)": 1.0,
            "Often (most projects)": 0.85,
            "Sometimes (about half of projects)": 0.45,
            "Rarely (a few projects)": 0.15,
            "Never": 0.0
        },
        
        "Domain-Specific": {
            "Always (essential part of workflow)": 1.0,
            "Often (most projects)": 0.7,
            "Sometimes (about half of projects)": 0.4,
            "Rarely (a few projects)": 0.1,
            "Never": 0.0
        },
        
        "Logarithmic": {
            "Always (essential part of workflow)": 1.0,
            "Often (most projects)": 0.69,
            "Sometimes (about half of projects)": 0.41,
            "Rarely (a few projects)": 0.18,
            "Never": 0.0
        }
    }
    
    # Calculate scores for each methodology
    results = []
    for scheme_name, weights in weighting_schemes.items():
        row = {'Scheme': scheme_name}
        
        # Calculate scores for each category
        for category in categories_to_compare:
            if category in frequency_data and totals[category] > 0:
                score = calculate_weighted_score(
                    frequency_data[category], 
                    weights, 
                    totals[category]
                )
                row[f'{category.title()} Score'] = round(score, 1)
            else:
                row[f'{category.title()} Score'] = 0
        
        # Calculate gap if comparing two categories
        if len(categories_to_compare) == 2:
            score1 = row[f'{categories_to_compare[0].title()} Score']
            score2 = row[f'{categories_to_compare[1].title()} Score']
            gap = score1 - score2
            row['Gap'] = round(gap, 1)
            if score1 > 0:
                row['Gap %'] = round((gap / score1) * 100, 1)
            else:
                row['Gap %'] = 0
        
        results.append(row)
    
    return pd.DataFrame(results), weighting_schemes

def create_visualizations(df_results, frequency_data, totals, weighting_schemes, categories):
    """Create comprehensive visualizations with proper matplotlib handling"""
    
    # Configure matplotlib for non-interactive environments
    plt.ioff()  # Turn off interactive mode
    plt.style.use('default')  # Use default style to avoid issues
    
    fig = plt.figure(figsize=(18, 12))
    
    # 1. Score comparison
    ax1 = plt.subplot(2, 3, 1)
    schemes = df_results['Scheme'].values
    
    x = np.arange(len(schemes))
    width = 0.35
    
    colors = ['skyblue', 'lightcoral', 'lightgreen', 'orange']
    for i, category in enumerate(categories):
        if f'{category.title()} Score' in df_results.columns:
            scores = df_results[f'{category.title()} Score'].values
            ax1.bar(x + i*width - width/2, scores, width, 
                   label=category.title(), alpha=0.8, color=colors[i])
    
    ax1.set_xlabel('Scoring Methodology')
    ax1.set_ylabel('Score (0-100)')
    ax1.set_title('Scores by Methodology')
    ax1.set_xticks(x)
    ax1.set_xticklabels(schemes, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Gap comparison (if applicable) - FIXED
    if 'Gap' in df_results.columns:
        ax2 = plt.subplot(2, 3, 2)
        gaps = df_results['Gap'].values
        x_gap = np.arange(len(schemes))
        ax2.bar(x_gap, gaps, alpha=0.8, color='orange')
        ax2.set_xlabel('Scoring Methodology')
        ax2.set_ylabel('Score Gap')
        ax2.set_title(f'{categories[0].title()}-{categories[1].title()} Score Gaps')
        ax2.set_xticks(x_gap)  # FIXED: Set ticks first
        ax2.set_xticklabels(schemes, rotation=45, ha='right')
        ax2.grid(True, alpha=0.3)
    
    # 3. Weight distributions
    ax3 = plt.subplot(2, 3, 3)
    freq_categories = ["Always", "Often", "Sometimes", "Rarely", "Never"]
    full_categories = [
        "Always (essential part of workflow)",
        "Often (most projects)", 
        "Sometimes (about half of projects)",
        "Rarely (a few projects)",
        "Never"
    ]
    
    for i, (scheme_name, weights) in enumerate(list(weighting_schemes.items())[:3]):
        weight_values = [weights[cat] for cat in full_categories]
        ax3.plot(freq_categories, weight_values, marker='o', 
                label=scheme_name, linewidth=2)
    
    ax3.set_xlabel('Frequency Category')
    ax3.set_ylabel('Weight Value')
    ax3.set_title('Weight Distribution Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    ax3.set_ylim(0, 1.05)
    
    # 4. Response distributions - FIXED
    for i, category in enumerate(categories[:2]):  # Show first 2 categories
        ax = plt.subplot(2, 3, 4 + i)
        
        if category in frequency_data and totals[category] > 0:
            responses = frequency_data[category]
            counts = [responses[cat] for cat in full_categories]
            percentages = [count/totals[category]*100 for count in counts]
            
            x_bars = np.arange(len(freq_categories))  # FIXED: Use numeric positions
            bars = ax.bar(x_bars, percentages, alpha=0.8, color=colors[i])
            ax.set_xlabel('Frequency Category')
            ax.set_ylabel('Percentage of Responses')
            ax.set_title(f'{category.title()} Response Distribution (n={totals[category]})')
            ax.set_xticks(x_bars)  # FIXED: Set ticks first
            ax.set_xticklabels(freq_categories, rotation=45, ha='right')
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, pct in zip(bars, percentages):
                height = bar.get_height()
                if height > 0:  # Only add label if there's a bar
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                           f'{pct:.1f}%', ha='center', va='bottom', fontsize=8)
    
    # 6. Sensitivity analysis
    ax6 = plt.subplot(2, 3, 6)
    if len(categories) == 2 and all(cat in frequency_data for cat in categories):
        # Show how gap changes with different "Sometimes" weights
        sometimes_weights = np.linspace(0.2, 0.8, 20)
        gaps = []
        
        base_weights = weighting_schemes["Domain-Specific"].copy()
        
        for weight in sometimes_weights:
            test_weights = base_weights.copy()
            test_weights["Sometimes (about half of projects)"] = weight
            
            score1 = calculate_weighted_score(
                frequency_data[categories[0]], test_weights, totals[categories[0]]
            )
            score2 = calculate_weighted_score(
                frequency_data[categories[1]], test_weights, totals[categories[1]]
            )
            gaps.append(score1 - score2)
        
        ax6.plot(sometimes_weights, gaps, marker='o', linewidth=2, color='red')
        ax6.set_xlabel('"Sometimes" Weight')
        ax6.set_ylabel('Score Gap')
        ax6.set_title('Sensitivity: Gap vs "Sometimes" Weight')
        ax6.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # Save the figure and handle properly
    output_file = 'survey_scoring_analysis.pdf'
    try:
        plt.savefig(output_file, format='pdf', bbox_inches='tight')
        print(f"\nVisualization saved as: {output_file}")
    except Exception as e:
        print(f"Warning: Could not save visualization: {e}")
    finally:
        plt.close(fig)  # Always close the figure to prevent warnings

def print_detailed_analysis(df_results, frequency_data, totals):
    """Print detailed analysis and recommendations"""
    
    print("\n" + "="*60)
    print("DETAILED ANALYSIS")
    print("="*60)
    
    # Print response distributions
    for category, data in frequency_data.items():
        if totals[category] > 0:
            print(f"\n{category.upper()} RESPONSES (n={totals[category]}):")
            for freq, count in data.items():
                percentage = (count / totals[category]) * 100
                print(f"  {freq}: {count} ({percentage:.1f}%)")
    
    print("\n" + "="*60)
    print("SCORING METHODOLOGY COMPARISON")
    print("="*60)
    print(df_results.to_string(index=False))
    
    print("\n" + "="*60)
    print("RECOMMENDATIONS")
    print("="*60)
    
    print("1. ISSUES WITH LINEAR DISTRIBUTION:")
    print("   - Assumes equal psychological distance between categories")
    print("   - May not reflect actual adoption behavior patterns")
    print("   - Could overweight middle categories ('Sometimes')")
    
    print("\n2. ALTERNATIVE APPROACHES:")
    print("   - Domain-Specific: Better reflects adoption thresholds")
    print("   - Exponential: Accounts for non-linear usage patterns")  
    print("   - Adoption-Stage: Emphasizes commitment levels")
    
    if 'Gap' in df_results.columns:
        # Find scheme with most reasonable gap
        median_gap = df_results['Gap'].median()
        best_scheme = df_results.loc[df_results['Gap'].sub(median_gap).abs().idxmin()]
        print(f"\n3. RECOMMENDED SCHEME:")
        print(f"   - Consider '{best_scheme['Scheme']}' methodology")
        print(f"   - Produces gap of {best_scheme['Gap']:.1f} points")
        print(f"   - This represents {best_scheme['Gap %']:.1f}% relative difference")
    
    print("\n4. NEXT STEPS:")
    print("   - Validate chosen methodology with domain experts")
    print("   - Test sensitivity with different weight adjustments")
    print("   - Consider context of your research questions")

def test_custom_weights(frequency_data, totals, categories):
    """Allow testing of custom weight schemes"""
    print("\n=== CUSTOM WEIGHT TESTER ===")
    print("Define your own weights (0.0 to 1.0) for each category:")
    
    frequency_categories = [
        "Always (essential part of workflow)",
        "Often (most projects)", 
        "Sometimes (about half of projects)",
        "Rarely (a few projects)",
        "Never"
    ]
    
    custom_weights = {}
    for category in frequency_categories:
        while True:
            try:
                weight = float(input(f"{category}: "))
                if 0.0 <= weight <= 1.0:
                    custom_weights[category] = weight
                    break
                else:
                    print("Please enter a value between 0.0 and 1.0")
            except ValueError:
                print("Please enter a valid number")
    
    print(f"\nYour custom weights:")
    for cat, weight in custom_weights.items():
        print(f"  {cat}: {weight}")
    
    print(f"\nResults with your custom weights:")
    for category in categories:
        if category in frequency_data and totals[category] > 0:
            score = calculate_weighted_score(
                frequency_data[category], custom_weights, totals[category]
            )
            print(f"  {category.title()}: {score:.1f}")
    
    if len(categories) == 2:
        score1 = calculate_weighted_score(
            frequency_data[categories[0]], custom_weights, totals[categories[0]]
        )
        score2 = calculate_weighted_score(
            frequency_data[categories[1]], custom_weights, totals[categories[1]]
        )
        gap = score1 - score2
        gap_pct = (gap / score1 * 100) if score1 > 0 else 0
        print(f"  Gap: {gap:.1f} ({gap_pct:.1f}%)")

def main():
    """Main function to run the complete analysis"""
    
    print("=== SURVEY SCORING METHODOLOGY ANALYZER ===\n")
    
    try:
        # Load and process survey data
        print(f"Loading survey data from: {SURVEY_FILE}")
        survey_data = load_survey_data()
        frequency_data, totals = extract_frequency_data(survey_data)
        print("Survey data processed successfully!")
        
    except Exception as e:
        print(f"Error loading survey data: {e}")
        print("Please ensure the file 'procedural-level-generation-survey.json' exists in the current directory.")
        return
    
    # Choose categories to compare
    available_categories = [cat for cat, total in totals.items() if total > 0]
    print(f"\nAvailable categories: {available_categories}")
    
    if len(available_categories) >= 2:
        categories_to_compare = available_categories[:2]  # Use first two
    else:
        categories_to_compare = available_categories
        
    print(f"Comparing: {categories_to_compare}")
    
    # Run analysis
    df_results, weighting_schemes = analyze_scoring_methodologies(
        frequency_data, totals, categories_to_compare
    )
    
    # Print results
    print_detailed_analysis(df_results, frequency_data, totals)
    
    # Create visualizations
    print("\nGenerating visualizations...")
    create_visualizations(
        df_results, frequency_data, totals, 
        weighting_schemes, categories_to_compare
    )
    
    # Option to test custom weights
    while True:
        try:
            test_custom = input("\nWould you like to test custom weights? (y/n): ").lower()
            if test_custom == 'y':
                test_custom_weights(frequency_data, totals, categories_to_compare)
            else:
                break
        except KeyboardInterrupt:
            print("\nExiting...")
            break
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main()