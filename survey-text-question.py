"""
Thematic Co-occurrence Network Analysis for Survey Open-Ended Responses
Using NetworkX built-in drawing functions with consistent plot styling
"""

import json
import matplotlib
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
from itertools import combinations
import os

# ============================================================================
# CONFIGURE MATPLOTLIB - CONSISTENT WITH OTHER PLOTS
# ============================================================================

font_size = 15  # Adjust this to match your other plots

plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['DejaVu Serif'],
    'font.sans-serif': ['DejaVu Sans'],
    'font.monospace': ['DejaVu Sans Mono'],
    'font.size': font_size,
    'axes.titlesize': 18,
    'axes.labelsize': font_size,
    'xtick.labelsize': font_size - 5,
    'ytick.labelsize': font_size,
    'legend.fontsize': font_size,
    'figure.titlesize': 0,
    'figure.dpi': 300,
    'axes.grid': True,
    'grid.alpha': 0.4,
    'axes.axisbelow': True,
    'axes.titlelocation': 'center',
    'axes.titlesize': 0,
    'savefig.dpi': 300,
    'savefig.format': 'pdf',
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.0,
    'pdf.fonttype': 42,
    'pdf.use14corefonts': False,
    'mathtext.fontset': 'stix',
})

os.makedirs('plots', exist_ok=True)

# ============================================================================
# TWEAKABLE VISUALIZATION PARAMETERS
# ============================================================================

VIZ_PARAMS = {
    # Layout parameters
    'scale': 1.0,         # Scale factor for layout (lower = more compact, try: 0.5-2.0)
    'center': (0.5, 0.5), # Center point for layout
    
    # Figure size
    'figsize': (8, 8),   # Canvas size in inches
    
    # Node styling
    'node_size_scale': 400,    # Multiplier for node sizes (try: 150-400)
    'node_cmap': 'tab10',     # Color map (try: 'Blues', 'Greens', 'YlOrRd', 'viridis')
    
    # Edge styling  
    'edge_width_scale': 5.0,   # Multiplier for edge thickness (try: 0.5-2.0)
    'edge_color': 'lightgray',      # Edge color
    
    # Label styling
    'label_font_size': font_size,      # Node label font size
    'edge_label_font_size': font_size - 3,  # Edge label font size
    'font_weight': 'normal',           # 'normal' or 'bold'
    
    # Which edge labels to show
    'min_edge_label': 0,       # Only show edge weights >= this value (reduces clutter)
    
    # Alternative layouts
    'layout_algorithm': 'circular',  # 'spring', 'kamada_kawai', 'circular', or 'shell'
}

# ============================================================================
# Theme Dictionary
# ============================================================================

THEMES = {
    'Control & \n Flexibility': [
        'control', 'artistic control', 'creative control', 'flexibility', 'flexible',
        'customize', 'customization', 'adjust', 'tweak', 'fine-tune', 'precision',
        'manual', 'agency', 'freedom', 'autonomy', 'direct manipulation'
    ],
    'Time & \n Efficiency': [
        'time', 'fast', 'faster', 'quick', 'speed', 'efficient', 'efficiency',
        'iteration', 'rapid', 'productivity', 'workflow speed', 'save time',
        'time-consuming', 'slow', 'lengthy', 'productivity'
    ],
    'Integration & \n Workflow': [
        'integration', 'integrate', 'workflow', 'pipeline', 'existing tools',
        'compatible', 'compatibility', 'seamless', 'export', 'import', 'engine',
        'work with', 'fit into', 'alongside', 'existing workflow', 'blend'
    ],
    'Technical \n Barriers': [
        'technical', 'complexity', 'complex', 'complicated', 'difficult',
        'steep learning curve', 'learning curve', 'barrier', 'entry barrier',
        'technical knowledge', 'programming', 'code', 'coding', 'requires coding'
    ],
    'Designer \n Accessibility': [
        'designer', 'non-programmer', 'non-technical', 'without code',
        'no programming', 'visual', 'user-friendly', 'accessible',
        'easy to use', 'intuitive', 'for designers', 'designer-friendly'
    ],
    'Debugging & \n Understanding': [
        'debug', 'debugging', 'understand', 'understanding', 'transparent',
        'transparency', 'black box', 'explain', 'explainable', 'why',
        'trace', 'unexpected', 'unpredictable', 'hard to understand',
        'interpretable', 'readable'
    ],
    'Quality & \n Consistency': [
        'quality', 'consistent', 'consistency', 'reliable', 'reliability',
        'predictable', 'stable', 'variation', 'variety', 'diverse',
        'repetitive', 'same', 'boring', 'generic', 'game balance'
    ],
    'Content \n Mixing': [
        'mix', 'mixing', 'combine', 'hybrid', 'procedural and manual',
        'procedural and hand-crafted', 'handcrafted', 'hand-authored',
        'blend', 'merge', 'together with'
    ],
    'Documentation & \n Learning': [
        'documentation', 'tutorial', 'tutorials', 'guide', 'examples',
        'learning resources', 'how to', 'instructions', 'help',
        'support', 'community', 'learn'
    ]
}

# ============================================================================
# Data Loading and Processing
# ============================================================================

def load_survey_data(filepath='procedural-level-generation-survey.json'):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    responses = []
    for entry in data:
        response = entry.get('most_important_problem')
        if response and response.strip():
            responses.append({
                'id': entry.get('id'),
                'response': response.strip(),
                'role': entry.get('professional_role'),
                'experience': entry.get('years_experience')
            })
    
    print(f"✓ Loaded {len(responses)} open-ended responses from {len(data)} total entries")
    return responses

def code_response(response_text, themes=THEMES):
    response_lower = response_text.lower()
    found_themes = []
    
    for theme, keywords in themes.items():
        for keyword in keywords:
            if keyword in response_lower:
                found_themes.append(theme)
                break
    
    return found_themes

def perform_thematic_coding(responses, themes=THEMES):
    coded_data = []
    for resp in responses:
        themes_found = code_response(resp['response'], themes)
        coded_data.append({
            **resp,
            'themes': themes_found,
            'num_themes': len(themes_found)
        })
    return coded_data

def calculate_theme_stats(coded_data):
    all_themes = []
    for entry in coded_data:
        all_themes.extend(entry['themes'])
    
    theme_counts = Counter(all_themes)
    total_responses = len([e for e in coded_data if e['themes']])
    
    stats = []
    for theme, count in theme_counts.most_common():
        stats.append({
            'theme': theme,
            'count': count,
            'percentage': (count / total_responses) * 100
        })
    
    return pd.DataFrame(stats)

def calculate_cooccurrence_matrix(coded_data):
    cooccurrence = defaultdict(lambda: defaultdict(int))
    
    for entry in coded_data:
        themes = entry['themes']
        if len(themes) > 1:
            for theme1, theme2 in combinations(sorted(themes), 2):
                cooccurrence[theme1][theme2] += 1
                cooccurrence[theme2][theme1] += 1
    
    all_themes = sorted(set(theme for entry in coded_data for theme in entry['themes']))
    matrix = pd.DataFrame(0, index=all_themes, columns=all_themes)
    
    for theme1 in cooccurrence:
        for theme2 in cooccurrence[theme1]:
            matrix.loc[theme1, theme2] = cooccurrence[theme1][theme2]
    
    return matrix

def create_network_graph(theme_stats, cooccurrence_matrix, min_cooccurrence=1):
    G = nx.Graph()

    # Shuffle the order to avoid clustering by size
    theme_stats_shuffled = theme_stats.sample(frac=1, random_state=42)
    
    for _, row in theme_stats_shuffled.iterrows():
        G.add_node(row['theme'], 
                   count=row['count'],
                   percentage=row['percentage'])
    
    for theme1 in cooccurrence_matrix.index:
        for theme2 in cooccurrence_matrix.columns:
            if theme1 < theme2:
                weight = cooccurrence_matrix.loc[theme1, theme2]
                if weight >= 1:
                    G.add_edge(theme1, theme2, weight=weight)
    
    return G

# ============================================================================
# Visualization Using NetworkX Built-in Functions
# ============================================================================

def visualize_network(G, params=VIZ_PARAMS, output_path='plots/q21_problem_theme_network.pdf'):
    """
    NetworkX visualization with consistent styling and proper font control
    """
    fig, ax = plt.subplots(figsize=params['figsize'], facecolor='white')

    # Draw background circle
    circle = plt.Circle((0, 0), params['scale'] * 1.4, 
                   color='lightgray', 
                   fill=False, 
                   linewidth=3, 
                   zorder=0)
    # ax.add_patch(circle)
        
    pos = nx.circular_layout(G)     

    # Extract node attributes
    node_sizes = [G.nodes[node]['count'] * params['node_size_scale'] for node in G.nodes()]
    node_colors = list(range(len(G.nodes())))
    
    # Extract edge attributes
    edge_widths = [G[u][v]['weight'] * params['edge_width_scale'] for u, v in G.edges()]
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, 
                          node_size=node_sizes,
                          node_color=node_colors,
                          cmap=plt.cm.get_cmap(params['node_cmap']),
                          edgecolors='black',
                          linewidths=0,
                          ax=ax)
        
    # Sort edges by weight
    edges_sorted = sorted(G.edges(), key=lambda e: G[e[0]][e[1]]['weight'])
    edge_widths_sorted = [G[u][v]['weight'] * params['edge_width_scale'] for u, v in edges_sorted]
    edge_colors_sorted = [G[u][v]['weight'] for u, v in edges_sorted]

    # Normalize edge colors to use only darker half of colormap
    norm = matplotlib.colors.Normalize(vmin=min(edge_colors_sorted), 
                            vmax=max(edge_colors_sorted))
    norm_colors = [0.65 + 0.35 * norm(c) for c in edge_colors_sorted]

    nx.draw_networkx_edges(G, pos,
                        edgelist=edges_sorted,
                        width=edge_widths_sorted,
                        edge_color=norm_colors,
                        edge_cmap=plt.cm.Blues,
                        edge_vmin=0.5, edge_vmax=1.0,  # Use only darker half
                        ax=ax)

    # Spread the labels slightly by adding an offset based on the 
    # size for that now (from node_sizes)
    #label_pos = {}
    #for node, (x, y) in pos.items():
    #    size = G.nodes[node]['count']
    #    offset = (size ** 0.4) / 5.0  # Adjust divisor to change spacing
    #    label_pos[node] = (x * (1 + offset), y * (1 + offset))

    # use constant offset instead
    label_pos = {}
    offset = 0.4  # constant offset
    for node, (x, y) in pos.items():
        label_pos[node] = (x * (1 + offset), y * (1 + offset))

    # Draw node labels - EXPLICITLY SET FONT PROPERTIES
    nx.draw_networkx_labels(G, label_pos,
                           font_size=params['label_font_size'],
                           font_family='serif',  # Match your rcParams
                           font_weight=params['font_weight'],
                           bbox=dict(boxstyle='round,pad=0.3',
                                facecolor='white',
                                edgecolor='lightgray',
                                linewidth=1),
                           ax=ax)
                
    # Set fixed axis limits so scale parameter has effect
    lim = 1.8
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)

    # Turn off axis and grid (network graphs shouldn't have grids)
    ax.axis('off')
    ax.grid(False)
    
    plt.tight_layout()
    
    # Save as PDF (uses matplotlib settings for DPI, format, etc.)
    plt.savefig(output_path)
    
    print(f"✓ Network visualization saved to: {output_path}")
    print(f"  Fonts: DejaVu Serif, size={params['label_font_size']}")
    
    plt.close()

# ============================================================================
# Analysis Report
# ============================================================================

def generate_report(coded_data, theme_stats, cooccurrence_matrix, G):
    print("\n" + "="*80)
    print("THEMATIC ANALYSIS REPORT")
    print("="*80)
    
    total_responses = len(coded_data)
    coded_responses = len([e for e in coded_data if e['themes']])
    
    print(f"\n1. RESPONSE STATISTICS")
    print(f"   Total responses: {total_responses}")
    print(f"   Coded responses: {coded_responses} ({coded_responses/total_responses*100:.1f}%)")
    print(f"   Average themes per response: {sum(e['num_themes'] for e in coded_data)/coded_responses:.1f}")
    
    print(f"\n2. THEME FREQUENCIES")
    print(theme_stats.to_string(index=False))
    
    print(f"\n3. NETWORK STATISTICS")
    print(f"   Nodes: {G.number_of_nodes()}")
    print(f"   Edges: {G.number_of_edges()}")
    
    if G.number_of_edges() > 0:
        edge_weights = [(u, v, G[u][v]['weight']) for u, v in G.edges()]
        edge_weights.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n   Top co-occurring theme pairs:")
        for u, v, w in edge_weights[:5]:
            print(f"   • {u} ↔ {v}: {w} times")
        
        if G.number_of_nodes() > 0:
            degree_cent = nx.degree_centrality(G)
            most_central = max(degree_cent, key=degree_cent.get)
            print(f"\n   Most central theme: {most_central}")
            print(f"   (Connected to {G.degree(most_central)} other themes)")
    
    print("\n" + "="*80)

# ============================================================================
# Main Pipeline
# ============================================================================

def main():
    print("\nThematic Network Analysis")
    print("-" * 80)
    
    print("\n[1/5] Loading survey data...")
    responses = load_survey_data('procedural-level-generation-survey.json')
    
    print("[2/5] Performing thematic coding...")
    coded_data = perform_thematic_coding(responses)
    
    print("[3/5] Calculating statistics...")
    theme_stats = calculate_theme_stats(coded_data)
    cooccurrence_matrix = calculate_cooccurrence_matrix(coded_data)
    
    print("[4/5] Creating network graph...")
    G = create_network_graph(theme_stats, cooccurrence_matrix, min_cooccurrence=2)
    
    print("[5/5] Generating network visualization...")
    visualize_network(G)
    
    generate_report(coded_data, theme_stats, cooccurrence_matrix, G)
    
    print("\n✅ COMPLETE! Network PDF saved to plots/theme_network.pdf")
    print("\n💡 TIP: Adjust 'label_font_size' in VIZ_PARAMS to change text size")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()