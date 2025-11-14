#!/usr/bin/env python3
"""pcg_workshop_analysis.py

Simple analysis for PCG workshop papers: extract titles and abstracts from
`pcg_workshop_papers_filtered.json`, compute word frequencies and TF-IDF
scores, and save CSV summaries and plots to `plots/`.

This is intentionally lightweight: it uses scikit-learn's
TfidfVectorizer with english stopwords to produce ranked term lists.
"""

import json
import os
import re
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import survey_analyzer


PAPERS_PATH = 'pcg_workshop_papers_filtered.json'
OUT_DIR = os.path.join('plots', 'pcgw')
os.makedirs(OUT_DIR, exist_ok=True)

# -----------------------------
# Configuration (set these when running from source / VS Code)
# -----------------------------
# When True the script will only produce the final theme comparison PDF and
# skip generating the intermediate CSVs/plots. Set to False to run full pipeline.
ONLY_COMPARISON = False

# Output filename for the final comparison PDF (placed in top-level `plots/`)
FINAL_COMPARISON_PDF = 'c3_pcgw_theme_comparison.pdf'

# Module-level runtime switches. Instead of relying on command-line arguments,
# toggle these booleans in the file when running from an editor/IDE. This makes
# it easy to control which stages run without changing how the script is
# invoked by the debugger or VS Code "Run" button.
#
# - RUN_MAIN_PIPELINE: run the full paper analysis + thematic coding + theme comparison
# - RUN_SURVEY_BIGRAMS: compute and save TF-IDF bigrams for the survey open-texts
# - RUN_BIGRAM_TABLE: compute (if needed) and save the LaTeX bigram comparison table
RUN_MAIN_PIPELINE = True
RUN_SURVEY_BIGRAMS = True
RUN_BIGRAM_TABLE = True


def load_papers(path=PAPERS_PATH):
	with open(path, 'r', encoding='utf-8') as f:
		data = json.load(f)
	papers = data.get('papers', []) if isinstance(data, dict) else data
	print(f"✓ Loaded {len(papers)} papers from {path}")
	return papers


# ---------------------------------------------------------------------------
# THEME-BASED (THEMATIC) CODING - reuse approach from survey-text-question.py
# ---------------------------------------------------------------------------

# A compact version of the THEMES dictionary used for survey coding. You can
# extend or tweak these keywords as needed.
THEMES = {
	'Control & Flexibility': [
		'control', 'artistic control', 'creative control', 'flexibility', 'flexible',
		'customize', 'customization', 'adjust', 'tweak', 'manual', 'agency'
	],
	'Time & Efficiency': [
		'time', 'fast', 'efficient', 'iteration', 'quick', 'speed', 'time-consuming'
	],
	'Integration & Workflow': [
		'integration', 'workflow', 'pipeline', 'export', 'import', 'engine', 'work with'
	],
	'Technical Barriers': [
		'technical', 'complex', 'complicated', 'difficult', 'learning curve', 'programming', 'code'
	],
	'Designer Accessibility': [
		'designer', 'non-programmer', 'visual', 'user-friendly', 'accessible', 'intuitive'
	],
	'Debugging & Understanding': [
		'debug', 'debugging', 'understand', 'transparency', 'explain', 'unexpected', 'unpredictable'
	],
	'Quality & Consistency': [
		'quality', 'consistent', 'reliable', 'predictable', 'variation', 'diverse', 'boring'
	],
	'Content Mixing': [
		'mix', 'mixing', 'combine', 'handcrafted', 'hand-authored', 'blend'
	],
	'Documentation & Learning': [
		'documentation', 'tutorial', 'guide', 'examples', 'how to', 'help', 'support'
	]
}


def count_theme_occurrences(docs, themes=THEMES):
	"""Count occurrences of theme keywords across a list of documents.

	Returns:
	  - theme_counts: Counter-like dict theme -> total keyword matches
	  - total_words: total number of word tokens across all docs
	"""
	counts = Counter()
	total_words = 0
	for d in docs:
		text = (d or '').lower()
		tokens = simple_tokenize(text)
		total_words += len(tokens)

		# For each theme, count occurrences of any keyword/phrase
		for theme, keywords in themes.items():
			theme_count = 0
			for kw in keywords:
				kw = kw.lower()
				if ' ' in kw:
					# phrase: count substring occurrences (approximate)
					theme_count += text.count(kw)
				else:
					# single token: count in tokens
					theme_count += tokens.count(kw)
			if theme_count:
				counts[theme] += theme_count

	return counts, total_words


def compare_themes_between_corpora(survey_docs, paper_docs, themes=THEMES, out_dir=OUT_DIR):
	survey_counts, survey_words = count_theme_occurrences(survey_docs, themes)
	paper_counts, paper_words = count_theme_occurrences(paper_docs, themes)

	# Build a DataFrame with normalized rates per 1000 words
	rows = []
	for theme in themes.keys():
		s_count = survey_counts.get(theme, 0)
		p_count = paper_counts.get(theme, 0)
		s_rate = (s_count / survey_words) * 1000 if survey_words > 0 else 0.0
		p_rate = (p_count / paper_words) * 1000 if paper_words > 0 else 0.0
		rows.append({
			'theme': theme,
			'survey_count': s_count,
			'survey_words': survey_words,
			'survey_per_1000_words': s_rate,
			'paper_count': p_count,
			'paper_words': paper_words,
			'paper_per_1000_words': p_rate
		})

	df = pd.DataFrame(rows).sort_values('survey_per_1000_words', ascending=False)
    
	# Plot side-by-side bars for each theme (survey vs papers)
	# Make the figure taller to accommodate long theme labels and improve readability
	fig, ax = plt.subplots(figsize=(12, max(6, len(rows) * 1.1)))
	ind = np.arange(len(df))
	width = 0.44
	# Draw bars and capture the bar containers so we can annotate them
	bars_survey = ax.barh(ind - width/2, df['survey_per_1000_words'][::-1], height=width, label='Survey Data')
	bars_papers = ax.barh(ind + width/2, df['paper_per_1000_words'][::-1], height=width, label='PCG Workshop')
	ax.set_yticks(ind)
	ax.set_yticklabels(df['theme'][::-1], fontsize=23)
	ax.set_xlabel('Occurrences per 1000 words', fontsize=23)
	ax.set_title('Thematic occurrence rates (normalized by words)')
	ax.legend(fontsize=23)

	# Determine offset for labels (2% of max value) and extend x-axis so labels
	# placed to the right of bars are visible.
	max_val = max(df['survey_per_1000_words'].max(), df['paper_per_1000_words'].max()) if len(df) > 0 else 0
	offset = max_val * 0.02 if max_val > 0 else 0.1
	# Add a small margin on the right for the numeric labels (12% of max_val)
	xmax = (max_val * 1.15) if max_val > 0 else (offset + 1.0)
	ax.set_xlim(0, xmax)

	# Annotate survey bars
	for rect, val in zip(bars_survey, df['survey_per_1000_words'][::-1]):
		x = rect.get_width()
		y = rect.get_y() + rect.get_height() / 2
		ax.text(x + offset, y, f"{val:.1f}", va='center', fontsize=20)

	# Annotate paper bars
	for rect, val in zip(bars_papers, df['paper_per_1000_words'][::-1]):
		x = rect.get_width()
		y = rect.get_y() + rect.get_height() / 2
		ax.text(x + offset, y, f"{val:.1f}", va='center', fontsize=20)

	plt.tight_layout()
	# Save as PDF (vector) for publication-quality output into top-level plots/
	plots_dir = 'plots'
	os.makedirs(plots_dir, exist_ok=True)
	out_plot = os.path.join(plots_dir, globals().get('FINAL_COMPARISON_PDF', 'c3_pcgw_theme_comparison.pdf'))
	fig.savefig(out_plot, bbox_inches='tight')
	plt.close(fig)
	print(f"✓ Theme comparison plot saved to: {out_plot}")


RE_WORD = re.compile(r"\b[a-zA-Z]{2,}\b")


def simple_tokenize(text):
	if not text:
		return []
	return RE_WORD.findall(text.lower())


def load_survey_texts(path='procedural-level-generation-survey.json'):
	"""Load survey JSON and return a list of open-text responses.

	Uses the same 'most_important_problem' field as the survey analysis script.
	"""
	if not os.path.exists(path):
		print(f"⚠ Survey file not found: {path}")
		return []
	with open(path, 'r', encoding='utf-8') as f:
		data = json.load(f)

	texts = []
	for entry in data:
		resp = entry.get('most_important_problem')
		if resp and resp.strip():
			texts.append(resp.strip())
	print(f"✓ Loaded {len(texts)} survey open-text responses from {path}")
	return texts


def corpus_from_papers(papers):
	docs = []
	rows = []
	for p in papers:
		title = p.get('title') or ''
		abstract = p.get('abstract') or ''
		doc = (title + '. ' + abstract).strip()
		docs.append(doc)
		rows.append({'title': title, 'abstract': abstract})
	return docs, pd.DataFrame(rows)


def top_term_frequencies(docs, top_n=40):
	c = Counter()
	for d in docs:
		c.update(simple_tokenize(d))
	df = pd.DataFrame(c.most_common(), columns=['term', 'count'])
	df['rank'] = range(1, len(df) + 1)
	return df.head(top_n)


def compute_tfidf(docs, top_n=40, ngram_range=(1, 1)):
	vect = TfidfVectorizer(stop_words='english', ngram_range=ngram_range, max_features=5000)
	X = vect.fit_transform(docs)
	# average tf-idf across documents
	mean_tfidf = np.asarray(X.mean(axis=0)).ravel()
	terms = vect.get_feature_names_out()
	df = pd.DataFrame({'term': terms, 'tfidf': mean_tfidf})
	df = df.sort_values('tfidf', ascending=False).reset_index(drop=True)
	df['rank'] = df.index + 1
	return df.head(top_n)


def compute_and_save_survey_bigrams(survey_path='procedural-level-generation-survey.json', out_dir=OUT_DIR, top_n=200):
	"""Compute TF-IDF for survey open-text bigrams and save CSV to out_dir.

	This replicates the ad-hoc script used interactively; exposing it here
	makes it reproducible when running the analysis script.
	"""
	texts = load_survey_texts(survey_path)
	if not texts:
		print(f"⚠ No survey texts found at: {survey_path}")
		return None
	df_bigrams = compute_tfidf(texts, top_n=top_n, ngram_range=(2, 2))
	os.makedirs(out_dir, exist_ok=True)
	out_csv = os.path.join(out_dir, 'survey_tfidf_bigrams.csv')
	df_bigrams.to_csv(out_csv, index=False)
	print(f"✓ Saved survey bigrams TF-IDF to: {out_csv}")
	return out_csv


def compute_and_save_bigram_comparison_table(paper_bigrams_csv=None, survey_bigrams_csv=None, out_dir=OUT_DIR, top_n=15, decimals=3):
	"""Create a LaTeX table comparing the top N bigrams from papers and survey.

	If the CSVs are not present, the function will compute the bigrams first.
	The resulting .tex file is saved to out_dir/bigram_comparison_table.tex.
	"""
	# ensure bigram CSVs exist (compute if necessary)
	if paper_bigrams_csv is None:
		paper_bigrams_csv = os.path.join(out_dir, 'pcg_papers_tfidf_bigrams.csv')
	if survey_bigrams_csv is None:
		survey_bigrams_csv = os.path.join(out_dir, 'survey_tfidf_bigrams.csv')

	# compute paper bigrams if missing
	if not os.path.exists(paper_bigrams_csv):
		# need papers
		papers = load_papers()
		docs, _ = corpus_from_papers(papers)
		df_p = compute_tfidf(docs, top_n=200, ngram_range=(2, 2))
		os.makedirs(out_dir, exist_ok=True)
		df_p.to_csv(paper_bigrams_csv, index=False)
	else:
		df_p = pd.read_csv(paper_bigrams_csv)

	# compute survey bigrams if missing
	if not os.path.exists(survey_bigrams_csv):
		compute_and_save_survey_bigrams(out_dir=out_dir)
		df_s = pd.read_csv(survey_bigrams_csv)
	else:
		df_s = pd.read_csv(survey_bigrams_csv)

	df_p_top = df_p.head(top_n).reset_index(drop=True)
	df_s_top = df_s.head(top_n).reset_index(drop=True)

	def latex_escape(s: str) -> str:
		if not isinstance(s, str):
			return s
		replacements = {
			'&':'\\&', '%':'\\%', '$':'\\$', '#':'\\#', '_':'\\_', '{':'\\{',
			'}':'\\}', '~':'\\textasciitilde{}', '^':'\\textasciicircum{}', '\\':'\\textbackslash{}'
		}
		for k,v in replacements.items():
			s = s.replace(k,v)
		return ' '.join(s.split())

	out_tex = os.path.join(out_dir, 'bigram_comparison_table.tex')
	header = rf"""\begin{{table}}[h]
\centering
\caption{{Top {top_n} TF--IDF bigrams from PCG workshop papers (left) and survey responses (right).}}
\label{{tab:bigram-comparison}}
\begin{{tabular}}{{p{{0.46\columnwidth}} p{{0.46\columnwidth}}}}
\hline
	extbf{{PCG papers (bigram (tf-idf))}} & \textbf{{Survey (bigram (tf-idf))}} \\\
\hline
"""

	rows = []
	for i in range(top_n):
		p_term = latex_escape(str(df_p_top.iloc[i]['term'])) if i < len(df_p_top) else ''
		p_tfidf = df_p_top.iloc[i]['tfidf'] if i < len(df_p_top) else 0.0
		s_term = latex_escape(str(df_s_top.iloc[i]['term'])) if i < len(df_s_top) else ''
		s_tfidf = df_s_top.iloc[i]['tfidf'] if i < len(df_s_top) else 0.0
		left = f"{p_term} ({p_tfidf:.{decimals}f})"
		right = f"{s_term} ({s_tfidf:.{decimals}f})"
		rows.append(f"{left} & {right} \\\\")

	footer = r"""\hline
\end{tabular}
\end{table}
"""

	content = header + '\n'.join(rows) + '\n' + footer
	os.makedirs(out_dir, exist_ok=True)
	with open(out_tex, 'w', encoding='utf-8') as f:
		f.write(content)

	print(f"✓ Saved LaTeX bigram comparison table to: {out_tex}")
	return out_tex


# ---------------------------------------------------------------------------
# Thematic coding (adapted from survey-text-question.py)
# ---------------------------------------------------------------------------
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
		'work with', 'fit into', 'alongside', 'existing workflow', 'blend', 'tool'
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
	'Algorithms & \n Models': [
		'model', 'models', 'algorithm', 'algorithms', 'wfc',
		'wave function collapse', 'ml', 'machine learning', 'neural', 'network', 'automated',
		'spatial', 'evolutionary', 'search-based', 'constraint-based', 'evolution', 'wfc',
		'learning', 'constraint', 'semantic'
	],		
	'Tooling & \n Methods' : [
		'method', 'methods', 'approach', 'approaches', 'technique', 'techniques',
		'tool', 'tools', 'framework', 'implementation', 'generator', 'generators',
		'generative', 'procedurally', 'pcg', 'framework', 'language', 'levels', 'mixed'
	],
	'Documentation & \n Learning': [
		'documentation', 'tutorial', 'tutorials', 'guide', 'examples',
		'learning resources', 'how to', 'instructions', 'help',
		'support', 'community', 'learn'
	]
}


def code_response(text, themes=THEMES):
	text_l = (text or '').lower()
	found = []
	for theme, keywords in themes.items():
		for kw in keywords:
			if kw in text_l:
				found.append(theme)
				break
	return found


def perform_thematic_coding_from_df(df, text_field='text'):
	coded = []
	for _, row in df.iterrows():
		txt = row.get(text_field, '')
		themes_found = code_response(txt)
		coded.append({'title': row.get('title', ''),
					  'themes': themes_found,
					  'num_themes': len(themes_found)})
	return pd.DataFrame(coded)


def calculate_theme_stats_df(coded_df):
	all_themes = []
	for themes in coded_df['themes']:
		all_themes.extend(themes)
	counts = Counter(all_themes)
	total = len(coded_df)
	rows = [{'theme': t, 'count': c, 'percentage': (c / total) * 100} for t, c in counts.items()]
	return pd.DataFrame(sorted(rows, key=lambda r: r['count'], reverse=True))


def calculate_cooccurrence_matrix_from_coded(coded_df):
	from collections import defaultdict
	from itertools import combinations
	co = defaultdict(lambda: defaultdict(int))
	for themes in coded_df['themes']:
		if len(themes) > 1:
			for a, b in combinations(sorted(themes), 2):
				co[a][b] += 1
				co[b][a] += 1
	all_themes = sorted({t for themes in coded_df['themes'] for t in themes})
	mat = pd.DataFrame(0, index=all_themes, columns=all_themes)
	for a in co:
		for b in co[a]:
			mat.loc[a, b] = co[a][b]
	return mat


def create_and_save_theme_network(theme_stats_df, cooccurrence_matrix, out_path):
	import networkx as nx
	G = nx.Graph()
	for _, row in theme_stats_df.iterrows():
		G.add_node(row['theme'], count=row['count'])
	for i in cooccurrence_matrix.index:
		for j in cooccurrence_matrix.columns:
			if i < j and cooccurrence_matrix.loc[i, j] > 0:
				G.add_edge(i, j, weight=int(cooccurrence_matrix.loc[i, j]))

	# simple plotting
	plt.figure(figsize=(9, 9))
	pos = nx.spring_layout(G, seed=42)
	sizes = [G.nodes[n].get('count', 1) * 200 for n in G.nodes()]
	nx.draw_networkx_nodes(G, pos, node_size=sizes, node_color='tab:blue')
	edges = G.edges()
	weights = [G[u][v]['weight'] for u, v in edges]
	if weights:
		nx.draw_networkx_edges(G, pos, width=[w for w in weights], edge_color='gray')
	nx.draw_networkx_labels(G, pos, font_size=10)
	plt.axis('off')
	plt.title('Theme co-occurrence network (PCG papers)')
	plt.tight_layout()
	plt.savefig(out_path)
	plt.close()
	return G


def save_barplot(df, value_col, title, out_path, top_n=25):
	# Use the project's survey plotting style (font family/size) by relying on
	# `survey_analyzer` which already configures matplotlib rcParams.
	df_plot = df.head(top_n).iloc[::-1]
	# Figure width chosen to match survey plotting defaults
	fig_w = 12.0
	fig_h = max(4, top_n * 0.18)
	fig, ax = plt.subplots(figsize=(fig_w, fig_h))
	ax.barh(df_plot['term'], df_plot[value_col], color='steelblue')
	# Use survey font sizes where appropriate
	base_font = getattr(survey_analyzer, 'font_size', 24)
	ax.set_xlabel(value_col, fontsize=max(10, base_font - 6))
	ax.set_title(title, fontsize=max(12, base_font - 6))
	ax.tick_params(labelsize=max(8, base_font - 8))
	plt.tight_layout()
	fig.savefig(out_path)
	plt.close(fig)
	print(f"✓ Saved plot: {out_path}")


def main(only_comparison=False):
	papers = load_papers()
	docs, df_meta = corpus_from_papers(papers)

	# Fast path: when only the final theme-comparison is needed, skip all
	# intermediate CSVs/plots and produce only the comparison CSV + PDF.
	if only_comparison:
		survey_docs = load_survey_texts('procedural-level-generation-survey.json')
		compare_themes_between_corpora(survey_docs, docs, themes=THEMES, out_dir=OUT_DIR)
		print('\nDone (only comparison).')
		return

	# Quick sanity
	num_with_abstract = sum(1 for a in df_meta['abstract'] if a and a.strip())
	print(f"{num_with_abstract}/{len(df_meta)} papers contain abstracts")

	# Term frequency (unigram)
	tf_df = top_term_frequencies(docs, top_n=200)
	tf_csv = os.path.join(OUT_DIR, 'pcg_papers_term_frequencies.csv')
	tf_df.to_csv(tf_csv, index=False)
	print(f"✓ Term frequency CSV saved to: {tf_csv}")
	save_barplot(tf_df, 'count', 'Top terms (frequency)', os.path.join(OUT_DIR, 'pcg_papers_top_terms_freq.png'), top_n=30)

	# TF-IDF unigrams
	tfidf_unigram = compute_tfidf(docs, top_n=200, ngram_range=(1, 1))
	tfidf_csv = os.path.join(OUT_DIR, 'pcg_papers_tfidf_unigrams.csv')
	tfidf_unigram.to_csv(tfidf_csv, index=False)
	print(f"✓ TF-IDF (unigrams) CSV saved to: {tfidf_csv}")
	save_barplot(tfidf_unigram, 'tfidf', 'Top terms (TF-IDF)', os.path.join(OUT_DIR, 'pcg_papers_top_terms_tfidf.png'), top_n=30)

	# TF-IDF bigrams (useful for multi-word phrases)
	tfidf_bigrams = compute_tfidf(docs, top_n=200, ngram_range=(2, 2))
	bigram_csv = os.path.join(OUT_DIR, 'pcg_papers_tfidf_bigrams.csv')
	tfidf_bigrams.to_csv(bigram_csv, index=False)
	print(f"✓ TF-IDF (bigrams) CSV saved to: {bigram_csv}")
	save_barplot(tfidf_bigrams, 'tfidf', 'Top bigrams (TF-IDF)', os.path.join(OUT_DIR, 'pcg_papers_top_bigrams_tfidf.png'), top_n=30)

	# Save a small sample of the metadata for reference
	meta_csv = os.path.join(OUT_DIR, 'pcg_papers_metadata_sample.csv')
	df_meta.head(200).to_csv(meta_csv, index=False)
	print(f"✓ Metadata sample saved to: {meta_csv}")

	print('\nSummary:')
	print(f"  Papers: {len(df_meta)}")
	print(f"  Unique terms (freq list): {len(tf_df)} (top shown)")
	print('Done.')

	# -------------------------
	# Thematic coding on titles+abstracts
	# -------------------------
	# create a combined text field
	df_meta['text'] = df_meta['title'].fillna('') + '. ' + df_meta['abstract'].fillna('')

	coded_df = perform_thematic_coding_from_df(df_meta, text_field='text')
	coded_csv = os.path.join(OUT_DIR, 'pcg_papers_thematic_coding.csv')
	coded_df.to_csv(coded_csv, index=False)
	print(f"✓ Thematic coding CSV saved to: {coded_csv}")

	theme_stats_df = calculate_theme_stats_df(coded_df)
	theme_stats_csv = os.path.join(OUT_DIR, 'pcg_papers_theme_stats.csv')
	theme_stats_df.to_csv(theme_stats_csv, index=False)
	print(f"✓ Theme stats CSV saved to: {theme_stats_csv}")

	cooc = calculate_cooccurrence_matrix_from_coded(coded_df)
	cooc_csv = os.path.join(OUT_DIR, 'pcg_papers_theme_cooccurrence.csv')
	cooc.to_csv(cooc_csv)
	print(f"✓ Co-occurrence matrix CSV saved to: {cooc_csv}")

	net_png = os.path.join(OUT_DIR, 'pcg_papers_theme_network.png')
	G = create_and_save_theme_network(theme_stats_df, cooc, net_png)
	print(f"✓ Theme network image saved to: {net_png}")

	# -------------------------
	# Compare themes normalized by total words between survey responses and papers
	# -------------------------
	# Load survey open-ended responses (field: most_important_problem)
	survey_docs = load_survey_texts('procedural-level-generation-survey.json')
	# compare and save CSV/plot
	compare_themes_between_corpora(survey_docs, docs, themes=THEMES, out_dir=OUT_DIR)


if __name__ == '__main__':
	# Module-level control: toggle the booleans at the top of this file to
	# decide which stages run. This is convenient when running from an IDE
	# or the debugger and avoids dealing with CLI argument parsing.
	print("pcg_workshop_analysis starting with configuration:")
	print(f"  RUN_MAIN_PIPELINE={RUN_MAIN_PIPELINE}")
	print(f"  RUN_SURVEY_BIGRAMS={RUN_SURVEY_BIGRAMS}")
	print(f"  RUN_BIGRAM_TABLE={RUN_BIGRAM_TABLE}")
	print(f"  ONLY_COMPARISON={ONLY_COMPARISON}")

	if RUN_SURVEY_BIGRAMS:
		compute_and_save_survey_bigrams(survey_path='procedural-level-generation-survey.json', out_dir=OUT_DIR, top_n=200)

	if RUN_BIGRAM_TABLE:
		compute_and_save_bigram_comparison_table(out_dir=OUT_DIR, top_n=15, decimals=3)

	if RUN_MAIN_PIPELINE:
		main(only_comparison=ONLY_COMPARISON)

