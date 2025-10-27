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

OFFSETS = {
    'Control & \n Flexibility': [ -0.15, 0.1 ],
    'Time & \n Efficiency': [ -0.0, 0.17 ],
    'Integration & \n Workflow': [ 0.0, 0.0 ],
    'Technical \n Barriers': [ 0.0, -0.1 ],
    'Designer \n Accessibility': [ 0.2, 0.2 ],
    'Debugging & \n Understanding': [ 0.0, 0.1 ],
    'Quality & \n Consistency': [ 0.15, 0.11 ],
    'Content \n Mixing': [ 0.0, 0.0 ],
    'Documentation & \n Learning': [ 0.1, 0.07 ]
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
    
    edge_count_by_weight = {}
    for theme1 in cooccurrence_matrix.index:
        for theme2 in cooccurrence_matrix.columns:
            if theme1 < theme2:
                weight = cooccurrence_matrix.loc[theme1, theme2]
                if weight >= min_cooccurrence:
                    G.add_edge(theme1, theme2, weight=weight)
                    edge_count_by_weight[weight] = edge_count_by_weight.get(weight, 0) + 1
    
    print(f"  Edge distribution: {dict(sorted(edge_count_by_weight.items()))}")
    return G

# ============================================================================
# Visualization Using NetworkX Built-in Functions
# ============================================================================

def visualize_network(
    G, 
    params=VIZ_PARAMS, 
    output_path='plots/q21_problem_theme_network.pdf',
    crop='tight',      # 'none' | 'tight' | 'axes'
    pad_inches=0.01
):
    """
    NetworkX visualization with consistent styling and proper font control
    
    Cropping options (applied at save time):
    - crop='none':  no additional cropping
    - crop='tight': Matplotlib tight layout cropping (bbox_inches='tight')
    - crop='axes':  Crop to the axes' tight bounding box (content-only)
    
    pad_inches controls extra border around the cropped box.
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
                          cmap=plt.get_cmap(params['node_cmap']),
                          edgecolors='black',
                          linewidths=0,
                          ax=ax)
        
    # Sort edges by weight
    edges_sorted = sorted(G.edges(), key=lambda e: G[e[0]][e[1]]['weight'])
    edge_widths_sorted = [G[u][v]['weight'] * params['edge_width_scale'] for u, v in edges_sorted]
    edge_colors_sorted = [G[u][v]['weight'] for u, v in edges_sorted]

    # Store min/max for legend and create truncated colormap (darker half only)
    edge_vmin = min(edge_colors_sorted)
    edge_vmax = max(edge_colors_sorted)
    
    # Create a colormap using only the darker half of Blues (0.5 to 1.0)
    import numpy as np
    from matplotlib.colors import LinearSegmentedColormap
    blues_dark = plt.cm.Blues(np.linspace(0.5, 1.0, 256))
    blues_dark_cmap = LinearSegmentedColormap.from_list('blues_dark', blues_dark)

    nx.draw_networkx_edges(G, pos,
                        edgelist=edges_sorted,
                        width=edge_widths_sorted,
                        edge_color=edge_colors_sorted,  # Just pass raw weights
                        edge_cmap=blues_dark_cmap,  # Use truncated colormap
                        edge_vmin=edge_vmin,
                        edge_vmax=edge_vmax,
                        ax=ax)

    # Spread the labels slightly by adding an offset based on the 
    # size for that now (from node_sizes)
    #label_pos = {}
    #for node, (x, y) in pos.items():
    #    size = G.nodes[node]['count']
    #    offset = (size ** 0.4) / 5.0  # Adjust divisor to change spacing
    #    label_pos[node] = (x * (1 + offset), y * (1 + offset))

    # Use constant offset with manual adjustments from OFFSETS dictionary
    label_pos = {}
    offset = 0.4  # constant offset
    for node, (x, y) in pos.items():
        # Get manual offset for this node (default to [0, 0] if not defined)
        manual_offset = OFFSETS.get(node, [0.0, 0.0])
        label_pos[node] = (x * (1 + offset) + manual_offset[0], 
                          y * (1 + offset) + manual_offset[1])

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
    
    # Save with optional cropping
    if crop == 'axes':
        # Crop to axes content
        fig.canvas.draw()  # ensure renderer exists
        bbox = ax.get_tightbbox(fig.canvas.get_renderer()).transformed(
            fig.dpi_scale_trans.inverted()
        )
        plt.savefig(output_path, bbox_inches=bbox, pad_inches=pad_inches)
    elif crop == 'tight':
        plt.savefig(output_path, bbox_inches='tight', pad_inches=pad_inches)
    else:
        plt.savefig(output_path)
    
    print(f"✓ Network visualization saved to: {output_path}")
    print(f"  Fonts: DejaVu Serif, size={params['label_font_size']}")
    
    plt.close()

def save_edge_legend(
    G,
    params=VIZ_PARAMS,
    output_path='plots/q21_problem_theme_legend.pdf',
    samples=None,  # None = show all unique weights
    title='Edge legend: co-occurrence count'
):
    """Save a separate legend figure showing sample edge widths and colors.

    - Shows unique positive weights from the graph (or samples if specified)
    - Uses the EXACT same width and color mapping as the main plot
    - Saves a compact, wide legend you can place below the figure in LaTeX
    """
    import numpy as np
    
    # Collect positive weights only
    weights = [G[u][v]['weight'] for u, v in G.edges() if G[u][v]['weight'] > 0]
    if not weights:
        # Nothing to show
        return None

    weights = sorted(set(weights))
    
    # Use all weights by default, or sample if requested
    if samples is None or len(weights) <= samples:
        reps = weights
    else:
        # Smart sampling: ensure we get min, max, and evenly distributed middle values
        idxs = np.round(np.linspace(0, len(weights) - 1, samples)).astype(int)
        idxs = np.unique(idxs)
        reps = [weights[i] for i in idxs]

    # Use EXACT same normalization as the main graph
    vmin, vmax = min(weights), max(weights)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    
    # Use only darker half of Blues colormap (0.5 to 1.0), matching the graph
    def color_for(w):
        t = norm(w)  # Normalize weight to [0, 1]
        # Map to darker half: 0 -> 0.5, 1 -> 1.0 in Blues colormap
        blues_value = 0.5 + 0.5 * t
        return plt.cm.Blues(blues_value)

    def width_for(w):
        return w * params['edge_width_scale']

    # Build legend figure
    fig_w, fig_h = params.get('figsize', (8, 8))
    legend_height = max(1.1, fig_h * 0.16)  # compact strip
    fig, ax = plt.subplots(figsize=(fig_w, legend_height), facecolor='white')

    ax.axis('off')
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    # Title
    ax.text(0.5, 0.88, title, ha='center', va='center', fontsize=params['label_font_size'], zorder=10)

    # Draw sample lines evenly spaced
    n = len(reps)
    xs = np.linspace(0.12, 0.88, n)
    y_line = 0.55
    y_text = 0.10
    line_len = 0.12

    for x, w in zip(xs, reps):
        lw = width_for(w)
        color = color_for(w)
        ax.hlines(y_line, x - line_len/2, x + line_len/2, colors=color, linewidth=lw, zorder=10)
        ax.text(x, y_text, f"{w}", ha='center', va='center', zorder=10)

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0.0)  # Increased padding to include border
    plt.close(fig)
    return output_path

def merge_pdfs(graph_pdf, legend_pdf, output_pdf='plots/q21_problem_theme_network_with_legend.pdf'):
    """Merge the graph and legend PDFs into a single page with vertical stacking.
    
    Uses pure vector PDF operations - no rasterization, preserves quality.
    Crops both PDFs and combines them on one page with the graph on top
    and the legend below.
    
    Args:
        graph_pdf: Path to the main graph PDF
        legend_pdf: Path to the legend PDF
        output_pdf: Path for the merged output
    
    Returns:
        Path to the merged PDF
    """
    try:
        from pypdf import PdfReader, PdfWriter, Transformation, PageObject
        #from pypdf.generic import RectangleObject
        import fitz  # PyMuPDF for getting tight crop boxes
        
        # Get tight bounding boxes using PyMuPDF
        graph_doc = fitz.open(graph_pdf)
        legend_doc = fitz.open(legend_pdf)
        
        graph_page = graph_doc[0]
        legend_page = legend_doc[0]
        
        # Get actual content bounds
        graph_rect = graph_page.bound()
        legend_rect = legend_page.bound()
        
        graph_doc.close()
        legend_doc.close()
        
        # Use pypdf for the actual merging (vector operations)
        graph_reader = PdfReader(graph_pdf)
        legend_reader = PdfReader(legend_pdf)
        
        graph_pg = graph_reader.pages[0]
        legend_pg = legend_reader.pages[0]
        
        # Use the tight bounds from fitz
        g_width = graph_rect.width
        g_height = graph_rect.height
        l_width = legend_rect.width
        l_height = legend_rect.height

        top_crop = 40
        bottom_crop = 40
        
        # Apply crop factor to graph height (reduce to remove whitespace from bottom)
        #graph_height_crop = 1.0  # Adjust this value (0.0-1.0) to crop more or less
        #g_height = g_height_original * graph_height_crop
        #crop_amount = g_height_original - g_height  # How much we're removing from bottom
        
        # Adjust the graph's crop box to remove content from the bottom
        graph_pg.cropbox.lower_left = (graph_rect.x0, graph_rect.y0)
        graph_pg.cropbox.upper_right = (graph_rect.x1, graph_rect.y1)
        
        # Add some padding
        spacer = 20
        
        # Calculate new page size
        new_width = max(g_width, l_width)
        new_height = g_width - top_crop - bottom_crop + l_height + spacer
        
        # Create new page
        writer = PdfWriter()
        
        # Create a blank page with the combined size
        new_page = PageObject.create_blank_page(width=new_width, height=new_height)
        
        # Calculate positions (centered horizontally)
        graph_x = (new_width - g_width) / 2
        graph_y = new_height - g_height  # Top
        
        legend_x = (new_width - l_width) / 2  
        legend_y = 0  # Bottom
        
        
        # Merge graph at top (now with adjusted crop box)
        new_page.merge_transformed_page(
            graph_pg,
            Transformation().translate(tx=graph_x - graph_rect.x0,
                                       ty=graph_y - graph_rect.y0 + top_crop)
        )
                
        # Merge legend at bottom
        new_page.merge_transformed_page(
            legend_pg,
            Transformation().translate(tx=legend_x - legend_rect.x0,
                                       ty=legend_y - legend_rect.y0)
        )
        
        writer.add_page(new_page)
        
        # Write output
        with open(output_pdf, 'wb') as f:
            writer.write(f)
        
        return output_pdf
        
    except ImportError as e:
        print(f"⚠ PDF merging requires PyMuPDF (fitz) and pypdf. Install with: pip install PyMuPDF pypdf")
        print(f"  Error: {e}")
        return None
    except Exception as e:
        print(f"⚠ Could not merge PDFs: {e}")
        import traceback
        traceback.print_exc()
        return None

# ============================================================================
# Analysis Report
# ============================================================================

def generate_report(coded_data, theme_stats, cooccurrence_matrix, G, output_latex='plots/q21_theme_statistics.tex'):
    """Generate report and save statistics as LaTeX tables"""
    
    print("\n" + "="*80)
    print("THEMATIC ANALYSIS REPORT")
    print("="*80)
    
    total_responses = len(coded_data)
    coded_responses = len([e for e in coded_data if e['themes']])
    avg_themes = sum(e['num_themes'] for e in coded_data)/coded_responses
    
    print(f"\n1. RESPONSE STATISTICS")
    print(f"   Total responses: {total_responses}")
    print(f"   Coded responses: {coded_responses} ({coded_responses/total_responses*100:.1f}%)")
    print(f"   Average themes per response: {avg_themes:.1f}")
    
    print(f"\n2. THEME FREQUENCIES")
    print(theme_stats.to_string(index=False))
    
    print(f"\n3. NETWORK STATISTICS")
    print(f"   Nodes: {G.number_of_nodes()}")
    print(f"   Edges: {G.number_of_edges()}")
    
    # Collect network statistics
    edge_weights = []
    most_central = None
    central_connections = 0
    
    if G.number_of_edges() > 0:
        edge_weights = [(u, v, G[u][v]['weight']) for u, v in G.edges()]
        edge_weights.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\n   Top co-occurring theme pairs:")
        for u, v, w in edge_weights[:5]:
            print(f"   • {u} ↔ {v}: {w} times")
        
        if G.number_of_nodes() > 0:
            degree_cent = nx.degree_centrality(G)
            most_central = max(degree_cent, key=degree_cent.get)
            central_connections = G.degree(most_central)
            print(f"\n   Most central theme: {most_central}")
            print(f"   (Connected to {central_connections} other themes)")
    
    print("\n" + "="*80)
    
    # ========================================================================
    # Generate LaTeX output
    # ========================================================================
    
    latex_output = []
    latex_output.append("% Theme Frequencies Table")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Theme Frequencies in Open-Ended Responses}")
    latex_output.append("\\label{tab:theme_frequencies}")
    
    # Create theme frequencies table
    theme_stats_latex = theme_stats.copy()
    theme_stats_latex['theme'] = theme_stats_latex['theme'].str.replace(' \n ', ' & ')
    theme_stats_latex['theme'] = theme_stats_latex['theme'].str.replace('&', '\\&')
    theme_stats_latex['percentage'] = theme_stats_latex['percentage'].apply(lambda x: f"{x:.1f}\\%")
    
    latex_table = theme_stats_latex.to_latex(
        index=False,
        column_format='lcc',
        escape=False,
        header=['Theme', 'Count', 'Percentage']
    )
    latex_output.append(latex_table)
    latex_output.append("\\end{table}")
    latex_output.append("")
    
    # Top co-occurring pairs table
    if edge_weights:
        latex_output.append("% Top Co-occurring Theme Pairs")
        latex_output.append("\\begin{table}[htbp]")
        latex_output.append("\\centering")
        latex_output.append("\\caption{Top Co-occurring Theme Pairs}")
        latex_output.append("\\label{tab:cooccurrence}")
        latex_output.append("\\begin{tabular}{llc}")
        latex_output.append("\\toprule")
        latex_output.append("Theme 1 & Theme 2 & Co-occurrence Count \\\\")
        latex_output.append("\\midrule")
        
        for u, v, w in edge_weights[:10]:  # Top 10 pairs
            u_clean = u.replace(' \n ', ' ').replace('&', '\\&')
            v_clean = v.replace(' \n ', ' ').replace('&', '\\&')
            latex_output.append(f"{u_clean} & {v_clean} & {w} \\\\")
        
        latex_output.append("\\bottomrule")
        latex_output.append("\\end{tabular}")
        latex_output.append("\\end{table}")
        latex_output.append("")
    
    # Summary statistics table
    latex_output.append("% Summary Statistics")
    latex_output.append("\\begin{table}[htbp]")
    latex_output.append("\\centering")
    latex_output.append("\\caption{Survey Response Summary Statistics}")
    latex_output.append("\\label{tab:summary_stats}")
    latex_output.append("\\begin{tabular}{lr}")
    latex_output.append("\\toprule")
    latex_output.append("Statistic & Value \\\\")
    latex_output.append("\\midrule")
    latex_output.append(f"Total responses & {total_responses} \\\\")
    latex_output.append(f"Coded responses & {coded_responses} ({coded_responses/total_responses*100:.1f}\\%) \\\\")
    latex_output.append(f"Average themes per response & {avg_themes:.1f} \\\\")
    latex_output.append(f"Number of themes & {G.number_of_nodes()} \\\\")
    latex_output.append(f"Number of co-occurrence edges & {G.number_of_edges()} \\\\")
    if most_central:
        most_central_clean = most_central.replace(' \n ', ' ').replace('&', '\\&')
        latex_output.append(f"Most central theme & {most_central_clean} \\\\")
        latex_output.append(f"Connections of most central & {central_connections} \\\\")
    latex_output.append("\\bottomrule")
    latex_output.append("\\end{tabular}")
    latex_output.append("\\end{table}")
    
    # Write to file
    latex_content = '\n'.join(latex_output)
    with open(output_latex, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    
    print(f"\n✓ LaTeX tables saved to: {output_latex}")
    print(f"  Include in your LaTeX document with: \\input{{{output_latex}}}")
    
    return latex_content

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
    G = create_network_graph(theme_stats, cooccurrence_matrix, min_cooccurrence=1)
    
    print("[5/5] Generating network visualization...")
    visualize_network(G, crop='none')  # Don't crop - let merge handle it
    # Also emit a separate legend PDF for edge sizes/colors
    legend_path = save_edge_legend(G)
    if legend_path:
        print(f"✓ Edge legend saved to: {legend_path}")
        
        # Merge the graph and legend into one PDF (single page, cropped)
        merged_path = merge_pdfs('plots/q21_problem_theme_network.pdf', legend_path)
        if merged_path:
            print(f"✓ Merged graph+legend saved to: {merged_path} (single page, cropped)")
        print("  Tip: Use individual PDFs separately or the merged version in LaTeX.")
    
    generate_report(coded_data, theme_stats, cooccurrence_matrix, G)
    
    print("\n✅ COMPLETE! Network PDF saved to plots/theme_network.pdf")
    print("\n💡 TIP: Adjust 'label_font_size' in VIZ_PARAMS to change text size")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()