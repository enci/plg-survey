import numpy as np
from scipy import stats

# Artists data (n=30)
artists = (
    [1.00] * 6 +   # Always
    [0.75] * 10 +  # Often
    [0.50] * 5 +   # Sometimes
    [0.25] * 6 +   # Rarely
    [0.00] * 3     # Never
)

# Designers data (n=34)
designers = (
    [1.00] * 0 +   # Always
    [0.75] * 4 +   # Often
    [0.50] * 7 +   # Sometimes
    [0.25] * 19 +  # Rarely
    [0.00] * 4     # Never
)

# Perform Mann-Whitney U test
statistic, p_value = stats.mannwhitneyu(artists, designers, alternative='two-sided')

print(f"Mann-Whitney U statistic: {statistic}")
print(f"P-value: {p_value}")
print(f"P-value (scientific notation): {p_value:.2e}")

# Also calculate means for reference
print(f"\nArtists mean: {np.mean(artists):.3f}")
print(f"Designers mean: {np.mean(designers):.3f}")
print(f"Difference: {np.mean(artists) - np.mean(designers):.3f}")