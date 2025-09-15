"""
Example usage script for SurveyAnalyzer

This script demonstrates how to use the SurveyAnalyzer to filter survey data
and extract values for analysis and plotting.
"""

from survey_analyzer import SurveyAnalyzer, FilterLogic
import matplotlib.pyplot as plt
import pandas as pd

def main():
    """Example analysis workflow"""
    
    # Initialize the analyzer
    print("=== Initializing Survey Analyzer ===")
    analyzer = SurveyAnalyzer(
        schema_path='survey-questions-schema.json',
        data_path='procedural-level-generation-survey.json'
    )
    
    # Example 1: Analyze all responses for a specific question
    print("\n=== Example 1: Game Engine Usage (All Responses) ===")
    engine_counts = analyzer.get_question_counts('game_engines', filtered=False)
    print("Game engine usage across all responses:")
    for engine, count in sorted(engine_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {engine}: {count}")
    
    # Example 2: Filter by professional role and analyze
    print("\n=== Example 2: Level Designers' Primary Concerns ===")
    analyzer.clear_filters()
    analyzer.add_filter('professional_role', 'Level Designer')
    analyzer.apply_filters()
    
    concerns_counts = analyzer.get_question_counts('primary_concerns')
    print("Primary concerns of Level Designers:")
    for concern, count in sorted(concerns_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {concern}: {count}")
    
    # Example 3: Multiple filters with OR logic
    print("\n=== Example 3: Concerns of Beginners OR Experts (OR Logic) ===")
    analyzer.clear_filters()
    analyzer.add_filter('years_experience', '0-2 years')
    analyzer.add_filter('years_experience', '10+ years')
    analyzer.set_filter_logic(FilterLogic.OR)
    analyzer.apply_filters()
    
    concerns_or = analyzer.get_question_counts('primary_concerns')
    print("Primary concerns of beginners OR experts:")
    for concern, count in sorted(concerns_or.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {concern}: {count}")
    
    # Example 4: Complex filtering with negation
    print("\n=== Example 4: Non-Academics with Unity Experience ===")
    analyzer.clear_filters()
    analyzer.add_filter('professional_role', 'Academic/Researcher', negate=True)  # NOT Academic
    analyzer.add_filter('game_engines', 'Unity')  # Uses Unity
    analyzer.set_filter_logic(FilterLogic.AND)
    analyzer.apply_filters()
    
    tool_view = analyzer.get_question_counts('tool_view')
    print("Tool satisfaction among non-academic Unity users:")
    for view, count in tool_view.items():
        print(f"  {view}: {count}")
    
    # Example 5: Get raw data for plotting
    print("\n=== Example 5: Preparing Data for Plotting ===")
    analyzer.clear_filters()
    analyzer.add_filter('years_experience', ['6-10 years', '10+ years'])  # Experienced users
    analyzer.apply_filters()
    
    # Get the filtered DataFrame for custom analysis
    filtered_df = analyzer.get_filtered_dataframe()
    print(f"Filtered DataFrame shape: {filtered_df.shape}")
    print(f"Columns available: {list(filtered_df.columns)}")
    
    # Example of extracting specific data for plotting
    # Get PCG tool experience ratings for experienced users
    if 'procedural_tools_experience' in filtered_df.columns:
        print("\nPCG Tool Experience Distribution (Experienced Users):")
        # This is a matrix question - we'll need to handle it differently
        pcg_data = filtered_df['procedural_tools_experience'].dropna()
        
        # Count experience levels for each tool
        experience_summary = {}
        for response in pcg_data:
            if isinstance(response, dict):
                for tool, experience in response.items():
                    if tool not in experience_summary:
                        experience_summary[tool] = {}
                    if experience not in experience_summary[tool]:
                        experience_summary[tool][experience] = 0
                    experience_summary[tool][experience] += 1
        
        # Show summary for one tool as example
        if 'Unity' in experience_summary or 'Unreal Engine PCG tools' in experience_summary:
            tool_name = 'Unreal Engine PCG tools' if 'Unreal Engine PCG tools' in experience_summary else 'Unity'
            print(f"\n{tool_name} experience levels among experienced developers:")
            for exp_level, count in experience_summary.get(tool_name, {}).items():
                print(f"  {exp_level}: {count}")
    
    # Example 6: Export filtered data
    print("\n=== Example 6: Exporting Filtered Data ===")
    analyzer.export_filtered_data('experienced_users.json', 'json')
    analyzer.export_filtered_data('experienced_users.csv', 'csv')
    print("Exported filtered data for further analysis.")
    
    # Show final summary
    analyzer.print_summary()
    
    # Example 7: Available questions and their types
    print("\n=== Example 7: Question Information ===")
    questions = analyzer.get_available_questions()
    print(f"Total questions available: {len(questions)}")
    
    # Show info for a few key questions
    key_questions = ['professional_role', 'years_experience', 'primary_concerns', 'game_engines']
    for q in key_questions:
        if q in questions:
            q_info = analyzer.get_question_info(q)
            q_type = analyzer.get_question_type(q)
            print(f"\nQuestion: {q}")
            print(f"  Type: {q_type}")
            print(f"  Text: {q_info.get('question', 'N/A')}")
            if 'options' in q_info:
                print(f"  Options: {len(q_info['options'])} choices")


if __name__ == "__main__":
    main()
