#!/usr/bin/env python3
"""
Different ways to visualize the gap between artists and designers
"""

import matplotlib.pyplot as plt
import numpy as np

# Your actual data
artist_data = {
    "Always": 6, "Often": 10, "Sometimes": 5, "Rarely": 6, "Never": 3
}
designer_data = {
    "Always": 0, "Often": 4, "Sometimes": 7, "Rarely": 19, "Never": 4
}

artist_total = 30
designer_total = 34

# Convert to percentages
artist_pct = {k: v/artist_total*100 for k, v in artist_data.items()}
designer_pct = {k: v/designer_total*100 for k, v in designer_data.items()}

# Calculate weighted scores (using linear weights for example)
linear_weights = {"Always": 1.0, "Often": 0.75, "Sometimes": 0.5, "Rarely": 0.25, "Never": 0.0}

artist_score = sum(artist_pct[k] * linear_weights[k] / 100 for k in artist_data.keys()) * 100
designer_score = sum(designer_pct[k] * linear_weights[k] / 100 for k in designer_data.keys()) * 100

plt.style.use('default')
plt.rcParams['font.size'] = 10

# Create figure with multiple visualization options
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

categories = ["Always", "Often", "Sometimes", "Rarely", "Never"]
colors = ['#2E8B57', '#4682B4', '#DAA520', '#CD853F', '#DC143C']  # Green to red spectrum

# 1. STACKED BAR CHART (Most comprehensive)
ax1 = axes[0, 0]
x = np.arange(2)
width = 0.6

bottom_artist = 0
bottom_designer = 0

for i, cat in enumerate(categories):
    artist_val = artist_pct[cat]
    designer_val = designer_pct[cat]
    
    ax1.bar(0, artist_val, width, bottom=bottom_artist, 
           label=cat if i == 0 else "", color=colors[i], alpha=0.8)
    ax1.bar(1, designer_val, width, bottom=bottom_designer, 
           color=colors[i], alpha=0.8)
    
    # Add percentage labels if significant
    if artist_val > 5:
        ax1.text(0, bottom_artist + artist_val/2, f'{artist_val:.0f}%', 
                ha='center', va='center', fontweight='bold', color='white')
    if designer_val > 5:
        ax1.text(1, bottom_designer + designer_val/2, f'{designer_val:.0f}%', 
                ha='center', va='center', fontweight='bold', color='white')
    
    bottom_artist += artist_val
    bottom_designer += designer_val

ax1.set_xticks(x)
ax1.set_xticklabels(['Artists\n(n=30)', 'Designers\n(n=34)'])
ax1.set_ylabel('Percentage of Responses')
ax1.set_title('Distribution of Procedural Generation Usage\nby Professional Role')
ax1.legend(categories, loc='upper right', bbox_to_anchor=(1.15, 1))

# Add calculated scores as text
ax1.text(0, 105, f'Score: {artist_score:.1f}', ha='center', fontweight='bold', 
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
ax1.text(1, 105, f'Score: {designer_score:.1f}', ha='center', fontweight='bold',
         bbox=dict(boxstyle="round,pad=0.3", facecolor="lightcoral"))

# 2. GROUPED BAR CHART (Easy to compare)
ax2 = axes[0, 1]
x = np.arange(len(categories))
width = 0.35

bars1 = ax2.bar(x - width/2, [artist_pct[cat] for cat in categories], width, 
               label='Artists', color='skyblue', alpha=0.8)
bars2 = ax2.bar(x + width/2, [designer_pct[cat] for cat in categories], width,
               label='Designers', color='lightcoral', alpha=0.8)

ax2.set_xlabel('Usage Frequency')
ax2.set_ylabel('Percentage of Responses')
ax2.set_title('Usage Frequency Comparison\nArtists vs Designers')
ax2.set_xticks(x)
ax2.set_xticklabels(categories, rotation=45, ha='right')
ax2.legend()
ax2.grid(True, alpha=0.3, axis='y')

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 2:  # Only label bars with significant height
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.0f}%', ha='center', va='bottom', fontsize=8)

# 3. CUMULATIVE ADOPTION CURVE (Shows adoption patterns)
ax3 = axes[1, 0]
# Calculate cumulative percentages (from high to low adoption)
cumulative_categories = ["Always", "Always+Often", "Always+Often+Sometimes", 
                        "Always+Often+Sometimes+Rarely", "All"]

artist_cumulative = [
    artist_pct["Always"],
    artist_pct["Always"] + artist_pct["Often"],
    artist_pct["Always"] + artist_pct["Often"] + artist_pct["Sometimes"],
    artist_pct["Always"] + artist_pct["Often"] + artist_pct["Sometimes"] + artist_pct["Rarely"],
    100
]

designer_cumulative = [
    designer_pct["Always"],
    designer_pct["Always"] + designer_pct["Often"],
    designer_pct["Always"] + designer_pct["Often"] + designer_pct["Sometimes"],
    designer_pct["Always"] + designer_pct["Often"] + designer_pct["Sometimes"] + designer_pct["Rarely"],
    100
]

x_cum = np.arange(len(cumulative_categories))
ax3.plot(x_cum, artist_cumulative, marker='o', linewidth=2, label='Artists', color='blue')
ax3.plot(x_cum, designer_cumulative, marker='s', linewidth=2, label='Designers', color='red')

ax3.set_xlabel('Adoption Level')
ax3.set_ylabel('Cumulative Percentage')
ax3.set_title('Cumulative Adoption Patterns')
ax3.set_xticks(x_cum)
ax3.set_xticklabels(['Always\nOnly', 'Often+', 'Sometimes+', 'Rarely+', 'All'], rotation=45, ha='right')
ax3.legend()
ax3.grid(True, alpha=0.3)

# Highlight key differences
for i, (a, d) in enumerate(zip(artist_cumulative, designer_cumulative)):
    if abs(a - d) > 10:  # Highlight significant differences
        ax3.annotate(f'Gap: {a-d:.0f}pp', xy=(i, max(a, d) + 2), ha='center', 
                    fontsize=8, color='red', fontweight='bold')

# 4. SCORE COMPARISON WITH CONFIDENCE INTERVALS (Most academic)
ax4 = axes[1, 1]

# For demonstration, let's show different weighting schemes
schemes = ['Linear', 'Domain-Specific', 'Exponential']
artist_scores = [58.3, 52.0, 59.0]  # From your earlier analysis
designer_scores = [33.1, 22.1, 30.9]
gaps = [a - d for a, d in zip(artist_scores, designer_scores)]

x_schemes = np.arange(len(schemes))
width = 0.35

bars1 = ax4.bar(x_schemes - width/2, artist_scores, width, label='Artists', 
               color='skyblue', alpha=0.8)
bars2 = ax4.bar(x_schemes + width/2, designer_scores, width, label='Designers', 
               color='lightcoral', alpha=0.8)

# Add gap annotations
for i, (a, d, gap) in enumerate(zip(artist_scores, designer_scores, gaps)):
    ax4.annotate('', xy=(i - width/2, a), xytext=(i + width/2, d),
                arrowprops=dict(arrowstyle='<->', color='red', lw=2))
    ax4.text(i, (a + d)/2, f'Gap:\n{gap:.1f}', ha='center', va='center',
            bbox=dict(boxstyle="round,pad=0.2", facecolor="yellow", alpha=0.7),
            fontweight='bold', fontsize=9)

ax4.set_xlabel('Weighting Scheme')
ax4.set_ylabel('Calculated Score (0-100)')
ax4.set_title('Scoring Methodology Comparison\nShowing Artist-Designer Gap')
ax4.set_xticks(x_schemes)
ax4.set_xticklabels(schemes)
ax4.legend()
ax4.grid(True, alpha=0.3, axis='y')

plt.tight_layout()
plt.savefig('gap_visualization_options.pdf', format='pdf', dpi=300, bbox_inches='tight')
plt.close()

print("Created gap visualization examples!")
print("\nVisualization Options:")
print("1. Stacked Bar Chart - Shows complete distribution with calculated scores")
print("2. Grouped Bar Chart - Easy category-by-category comparison")  
print("3. Cumulative Adoption Curve - Shows adoption thresholds clearly")
print("4. Score Comparison - Academic presentation of different methodologies")
print("\nSaved as: gap_visualization_options.png")

# Also create a single "best" visualization for your paper
fig, ax = plt.subplots(1, 1, figsize=(10, 6))

# RECOMMENDED: Combined stacked + score visualization
x = np.arange(2)
width = 0.6

bottom_artist = 0
bottom_designer = 0

# Create stacked bars with better styling
for i, cat in enumerate(categories):
    artist_val = artist_pct[cat]
    designer_val = designer_pct[cat]
    
    bar1 = ax.bar(0, artist_val, width, bottom=bottom_artist, 
                 color=colors[i], alpha=0.8, edgecolor='white', linewidth=1)
    bar2 = ax.bar(1, designer_val, width, bottom=bottom_designer, 
                 color=colors[i], alpha=0.8, edgecolor='white', linewidth=1)
    
    # Add percentage labels for significant segments
    if artist_val > 8:
        ax.text(0, bottom_artist + artist_val/2, f'{artist_val:.0f}%', 
               ha='center', va='center', fontweight='bold', color='white', fontsize=10)
    if designer_val > 8:
        ax.text(1, bottom_designer + designer_val/2, f'{designer_val:.0f}%', 
               ha='center', va='center', fontweight='bold', color='white', fontsize=10)
    
    bottom_artist += artist_val
    bottom_designer += designer_val

# Styling
ax.set_xticks(x)
ax.set_xticklabels(['Artists\n(n=30)', 'Designers\n(n=34)'], fontsize=12)
ax.set_ylabel('Percentage of Responses', fontsize=12)
ax.set_title('Procedural Generation Tool Usage Gap\nBetween Artists and Designers', 
             fontsize=14, fontweight='bold', pad=20)

# Add calculated scores with prominent display
ax.text(0, 108, f'Weighted Score: {artist_score:.1f}', ha='center', fontweight='bold', 
        fontsize=11, bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
ax.text(1, 108, f'Weighted Score: {designer_score:.1f}', ha='center', fontweight='bold',
        fontsize=11, bbox=dict(boxstyle="round,pad=0.5", facecolor="lightcoral", alpha=0.8))

# Add gap annotation
ax.annotate('', xy=(0, 102), xytext=(1, 102),
           arrowprops=dict(arrowstyle='<->', color='red', lw=3))
ax.text(0.5, 104, f'Gap: {artist_score - designer_score:.1f} points', 
       ha='center', va='center', fontweight='bold', fontsize=12,
       bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow", alpha=0.9))

# Legend
legend_elements = [plt.Rectangle((0,0),1,1, facecolor=colors[i], alpha=0.8) 
                  for i in range(len(categories))]
ax.legend(legend_elements, categories, loc='upper right', 
         bbox_to_anchor=(1.15, 1), title='Usage Frequency')

ax.set_ylim(0, 115)
plt.tight_layout()
plt.savefig('recommended_gap_visualization.pdf', format='pdf', bbox_inches='tight')
plt.close()

print("\nAlso created recommended visualization for your paper:")
print("- Shows both raw percentages AND calculated scores")
print("- Clear visual gap annotation")  
print("- Professional academic styling")
