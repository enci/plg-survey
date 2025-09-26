#!/usr/bin/env python3
"""
Debug Question 3 vs Question 19 bar sizes
"""

# Let's manually inspect what get_question_options_count returns for these two questions
print("DEBUGGING Q3 vs Q19 BAR SIZES")
print("=" * 50)

def calculate_chart_size(num_options, base_height=0.0, height_per_option=1.08):    
    width = 12  # Fixed width as requested
    height = base_height + (num_options * height_per_option)
    return (width, height)

print("Current sizing formula:")
print("  height = base_height + (num_options * height_per_option)")
print("  Default: height = 0.0 + (num_options * 1.08)")
print()

# Let's test different scenarios
print("If Q3 has few options and Q19 has many options:")
q3_options = 5  # Example: few game engines
q19_options = 15  # Example: many AI concerns

q3_size = calculate_chart_size(q3_options)
q19_size = calculate_chart_size(q19_options)

print(f"Q3 (game_engines): {q3_options} options -> {q3_size}")
print(f"Q19 (ai_concerns): {q19_options} options -> {q19_size}")

print(f"\nBar height per option:")
print(f"Q3: {q3_size[1] / q3_options:.2f} height per bar")
print(f"Q19: {q19_size[1] / q19_options:.2f} height per bar")

print(f"\nSo the bars should be the same size ({1.08} units each),")
print(f"but Q19 has {q19_options - q3_options} more bars in the chart.")

print("\nThis means:")
print("- Q19 should be a much TALLER chart (more bars)")
print("- But each individual bar should be the SAME SIZE")
print()
print("If Q19 bars look 'comically large', it might be because:")
print("1. Q19 actually has fewer response options than expected")
print("2. The chart height is being interpreted differently")
print("3. There's an issue with the chart rendering/scaling")

print("\n" + "=" * 50)
print("TO DIAGNOSE:")
print("1. Check how many unique responses each question actually has")
print("2. Look at the actual PDF dimensions")
print("3. Check if the data structure differs between the questions")