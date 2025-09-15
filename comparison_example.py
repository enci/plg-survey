"""
Comparison Example: Counts vs Percentages

This script demonstrates when to use counts vs percentages in survey visualization.
"""

from survey_analyzer import SurveyAnalyzer, SurveyPlotter
import matplotlib.pyplot as plt
import os

# Configure matplotlib for consistent styling
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

def create_comparison_plots():
    """Create side-by-side comparison of counts vs percentages."""
    
    print("=== Survey Visualization: Counts vs Percentages ===\n")
    
    # Initialize analyzer
    analyzer = SurveyAnalyzer('survey-questions-schema.json', 'procedural-level-generation-survey.json')
    plotter = SurveyPlotter(analyzer)
    
    # Create output directory
    output_dir = "plots/comparison"
    os.makedirs(output_dir, exist_ok=True)
    
    question = 'professional_role'
    question_info = analyzer.get_question_info(question)
    base_title = question_info.get('question', question)
    
    print(f"Analyzing: {base_title}")
    
    # Get total responses safely
    summary = analyzer.get_summary()
    total_responses = summary['total_responses']
    print(f"Total responses: {total_responses}\n")
    
    # Show raw data
    counts = analyzer.get_question_counts(question)
    total = sum(counts.values())
    
    print("Data breakdown:")
    print("-" * 60)
    print(f"{'Category':<30} | {'Count':<5} | {'Percentage'}")
    print("-" * 60)
    for category, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total) * 100
        print(f"{category:<30} | {count:<5} | {percentage:>6.1f}%")
    print("-" * 60)
    print(f"{'TOTAL':<30} | {total:<5} | {100.0:>6.1f}%")
    
    # Create counts chart
    print(f"\n📊 Creating counts chart...")
    fig_counts = plotter.create_bar_chart(
        question,
        title=f"{base_title}\n(Absolute Counts - n={total_responses})",
        show_percentages=False,
        colormap='viridis',
        figsize=(12, 8)
    )
    
    counts_path = os.path.join(output_dir, f"{question}_counts.pdf")
    fig_counts.savefig(counts_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig_counts)
    print(f"   Saved: {counts_path}")
    
    # Create percentages chart
    print(f"📊 Creating percentages chart...")
    fig_percentages = plotter.create_bar_chart(
        question,
        title=f"{base_title}\n(Percentages - n={total_responses})",
        show_percentages=True,
        colormap='viridis',
        figsize=(12, 8)
    )
    
    percentages_path = os.path.join(output_dir, f"{question}_percentages.pdf")
    fig_percentages.savefig(percentages_path, format='pdf', bbox_inches='tight', dpi=300)
    plt.close(fig_percentages)
    print(f"   Saved: {percentages_path}")
    
    # Analysis and recommendations
    print(f"\n=== Analysis & Recommendations ===")
    
    print(f"\n🔢 COUNTS are better when:")
    print(f"   • You want to emphasize sample size (n={total_responses})")
    print(f"   • Absolute numbers matter for decision-making")
    print(f"   • Comparing with other surveys of different sizes")
    print(f"   • Academic/research contexts requiring sample size transparency")
    
    print(f"\n📊 PERCENTAGES are better when:")
    print(f"   • You want to show relative proportions clearly")
    print(f"   • Comparing subgroups of different sizes")
    print(f"   • Creating executive summaries or presentations")
    print(f"   • Sample size is less relevant than distribution")
    
    # Demonstrate filtered comparison
    print(f"\n=== Filtered Data Comparison ===")
    
    # Filter for experienced developers
    analyzer.clear_filters()
    analyzer.add_filter('years_experience', ['6-10 years', '10+ years'])
    analyzer.apply_filters()
    
    filtered_counts = analyzer.get_question_counts(question, filtered=True)
    filtered_total = sum(filtered_counts.values())
    
    print(f"\nFiltered data (6+ years experience): {filtered_total} responses")
    print("-" * 50)
    for category, count in sorted(filtered_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / filtered_total) * 100 if filtered_total > 0 else 0
        print(f"{category:<30} | {count:>3} | {percentage:>6.1f}%")
    
    print(f"\n💡 Notice: Percentages help compare the filtered subset to the full dataset!")
    print(f"   Full dataset: Programmer/Technical Designer = {(counts.get('Programmer/Technical Designer', 0)/total*100):.1f}%")
    print(f"   Experienced: Programmer/Technical Designer = {(filtered_counts.get('Programmer/Technical Designer', 0)/filtered_total*100):.1f}%")
    
    print(f"\n✅ Both visualization types created in: {output_dir}/")
    return output_dir

if __name__ == "__main__":
    create_comparison_plots()
