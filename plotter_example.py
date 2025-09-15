"""
Simple example showing SurveyAnalyzer and SurveyPlotter usage together
"""

from survey_analyzer import SurveyAnalyzer, SurveyPlotter, FilterLogic
import os

def main():
    """Example of using SurveyAnalyzer with SurveyPlotter"""
    
    # Create plots directory
    os.makedirs('plots', exist_ok=True)
    
    # Initialize analyzer
    analyzer = SurveyAnalyzer(
        'survey-questions-schema.json',
        'procedural-level-generation-survey.json'
    )
    
    # Initialize plotter
    plotter = SurveyPlotter(analyzer)
    
    print("=== Creating Charts with SurveyPlotter ===\n")
    
    # Chart 1: Professional roles distribution
    print("1. Creating professional roles bar chart...")
    plotter.create_bar_chart(
        'professional_role',
        title='Professional Roles in Survey',
        save_path='plots/professional_roles.png'
    )
    
    # Chart 2: Game engines pie chart (filtered for experienced users)
    print("2. Creating game engines pie chart for experienced users...")
    analyzer.add_filter('years_experience', ['6-10 years', '10+ years'])
    analyzer.apply_filters()
    
    plotter.create_pie_chart(
        'game_engines',
        title='Game Engines Used by Experienced Developers',
        top_n=6,
        save_path='plots/game_engines_experienced.png'
    )
    
    # Chart 3: Comparison of concerns between beginners and experts
    print("3. Creating comparison chart of concerns...")
    filter_configs = [
        {'filters': [{'question': 'years_experience', 'value': '0-2 years'}]},
        {'filters': [{'question': 'years_experience', 'value': '10+ years'}]}
    ]
    labels = ['Beginners (0-2 years)', 'Experts (10+ years)']
    
    plotter.create_comparison_chart(
        'primary_concerns',
        filter_configs,
        labels,
        title='Primary Concerns: Beginners vs Experts',
        save_path='plots/concerns_comparison.png'
    )
    
    # Chart 4: PCG tool experience heatmap
    print("4. Creating PCG tool experience heatmap...")
    analyzer.clear_filters()  # Use all data
    plotter.create_matrix_heatmap(
        'procedural_tools_experience',
        title='PCG Tool Experience Levels',
        save_path='plots/pcg_tools_heatmap.png'
    )
    
    # Chart 5: Stacked bar chart of tool views by role
    print("5. Creating stacked bar chart...")
    analyzer.clear_filters()
    # Filter for roles with sufficient data
    analyzer.add_filter('professional_role', [
        'Programmer/Technical Designer', 
        'Technical Artist', 
        'Game Designer',
        'Level Designer'
    ])
    analyzer.apply_filters()
    
    plotter.create_stacked_bar_chart(
        'tool_view',
        'professional_role',
        title='Tool Satisfaction by Professional Role',
        save_path='plots/tool_views_by_role.png'
    )
    
    print("\n=== All charts created successfully! ===")
    print("Charts saved in the 'plots/' directory.")
    
    # Show some basic statistics
    summary = analyzer.get_summary()
    print(f"\nSummary:")
    print(f"- Total responses analyzed: {summary['total_responses']}")
    print(f"- Charts created: 5")
    print(f"- Available questions: {summary['available_questions']}")


if __name__ == "__main__":
    main()
