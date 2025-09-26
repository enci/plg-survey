#!/usr/bin/env python3

def calculate_chart_size(num_options, base_height=0.0, height_per_option=1.08):    
    width = 12  # Fixed width as requested
    height = base_height + (num_options * height_per_option)
    return (width, height)

def calculate_role_stacked_chart_size(num_options):
    """
    Calculate chart size specifically for role stacked charts to ensure consistent bar heights.
    """
    width = 12
    consistent_bar_height = 1.2  # Consistent height per bar
    base_padding = 2.0  # Space for legend and padding
    height = base_padding + (num_options * consistent_bar_height)
    
    # Ensure minimum readable size
    height = max(height, 6.0)
    
    return (width, height)

print('COMPARISON: Original vs Role Stacked Chart Sizing')
print('=' * 55)
print('Bars | Original    | Role Stacked | Bar Height')
print('-' * 55)

for num_bars in [5, 9, 12, 15]:
    original = calculate_chart_size(num_bars)
    role_stacked = calculate_role_stacked_chart_size(num_bars)
    orig_bar_height = original[1] / num_bars if num_bars > 0 else 0
    role_bar_height = (role_stacked[1] - 2.0) / num_bars if num_bars > 0 else 0
    
    print(f'{num_bars:4d} | {original[1]:6.2f}      | {role_stacked[1]:7.2f}     | Orig: {orig_bar_height:.2f}, Role: {role_bar_height:.2f}')

print()
print('Q3 (game_engines): 5 options')
print('Q19 (ai_concerns): 9 options') 
print()
print('With role stacked sizing:')
q3_size = calculate_role_stacked_chart_size(5)
q19_size = calculate_role_stacked_chart_size(9)
print(f'Q3: {q3_size} -> {(q3_size[1]-2)/5:.2f} height per bar')
print(f'Q19: {q19_size} -> {(q19_size[1]-2)/9:.2f} height per bar')
print('Both should now have 1.20 height per bar!')