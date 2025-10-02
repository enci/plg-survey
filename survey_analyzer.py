"""
SurveyAnalyzer - A Python tool for analyzing survey data with flexible filtering

This script loads survey questions from a schema (JSON) and answers (JSON),
and allows for filtering based on question responses with AND/OR logic.
Results can be used for plotting and analysis.

Author: Survey Analysis Tool
Version: 1.0
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.figure as mpl_figure
import numpy as np
import textwrap
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from dataclasses import dataclass
from enum import Enum
from collections import Counter

# Helper function for smart label wrapping
def wrap_label_smart(label, width):
    """Wrap labels based on width setting: None=no wrapping, 0=wrap at slashes, >0=wrap at width"""
    if width is None:
        return label
    elif width == 0:
        # Special case: wrap at slashes only
        return label.replace('/', '/\n')
    else:
        # Normal width-based wrapping
        return textwrap.fill(label, width=width, break_long_words=False)

# Enum for filter logic operations
class FilterLogic(Enum):
    AND = "AND"
    OR = "OR"

# Represents a single filter condition
@dataclass
class Filter:
    question: str
    value: Union[str, List[str]]
    negate: bool = False
    
    def __str__(self):
        negation = "NOT " if self.negate else ""
        return f"{negation}{self.question} = {self.value}"

# A comprehensive survey analysis tool that supports flexible filtering
# and data extraction from survey responses.
class SurveyAnalyzer:    
    # Initialize the SurveyAnalyzer with schema and data files.
    def __init__(self, schema_path: str, data_path: str):
        self.schema_path = schema_path
        self.data_path = data_path
        self.schema: Optional[Dict[str, Any]] = None
        self.responses: Optional[List[Dict[str, Any]]] = None
        self.df: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.filters: List[Filter] = []
        self.filter_logic = FilterLogic.AND
        
        self._load_data()
    
    # Load schema and survey response data from JSON files. Non-standard answers are stored as 'Other'.
    def _load_data(self):
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)

            with open(self.data_path, 'r', encoding='utf-8') as f:
                raw_responses = json.load(f)

            # Clean responses: replace non-standard answers with 'Other'
            cleaned_responses = []
            if self.schema is not None:
                for response in raw_responses:
                    cleaned = response.copy()
                    for q_key, q_info in self.schema['questions'].items():
                        options = q_info.get('options', [])
                        q_type = q_info.get('type', '')
                        if q_key in cleaned:
                            val = cleaned[q_key]
                            if options:
                                if q_type == 'multiple_choice' and isinstance(val, list):
                                    cleaned[q_key] = [v if v in options else 'Other' for v in val]
                                elif q_type == 'single_choice' and isinstance(val, str):
                                    if val not in options:
                                        cleaned[q_key] = 'Other'
                                # For other types, leave as is
                    cleaned_responses.append(cleaned)
            else:
                cleaned_responses = raw_responses

            self.responses = cleaned_responses
            self.df = pd.DataFrame(self.responses)
            self.filtered_data = self.df.copy()

            if self.responses and self.schema:
                print(f"Loaded {len(self.responses)} survey responses")
                print(f"Available questions: {list(self.schema['questions'].keys())}")

        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not find file: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    # Ensure data is loaded, raise error if not
    def _ensure_loaded(self):
        if self.schema is None or self.responses is None or self.df is None:
            raise RuntimeError("Data not loaded. Check file paths and try again.")
    
    # Get information about a specific question from the schema
    def get_question_info(self, question_key: str) -> Dict[str, Any]:
        self._ensure_loaded()
        assert self.schema is not None  # for type checker
        
        if question_key not in self.schema['questions']:
            raise ValueError(f"Question '{question_key}' not found in schema")
        
        return self.schema['questions'][question_key]
    
    # Get list of all available question keys
    def get_available_questions(self) -> List[str]:
        self._ensure_loaded()
        assert self.schema is not None  # for type checker
        return list(self.schema['questions'].keys())
    
    # Get available options for a question
    def get_question_options(self, question_key: str) -> List[str]:
        question_info = self.get_question_info(question_key)
        return question_info.get('options', [])
    
    # Get the type of a question
    def get_question_type(self, question_key: str) -> str:
        question_info = self.get_question_info(question_key)
        return question_info.get('type', 'unknown')
    
    # Add a filter condition
    def add_filter(self, question: str, value: Union[str, List[str]], negate: bool = False):
        self._ensure_loaded()
        assert self.schema is not None  # for type checker
        
        if question not in self.schema['questions']:
            raise ValueError(f"Question '{question}' not found in schema")
        
        filter_obj = Filter(question=question, value=value, negate=negate)
        self.filters.append(filter_obj)
        print(f"Added filter: {filter_obj}")
    
    # Remove a filter by index
    def remove_filter(self, index: int):
        if 0 <= index < len(self.filters):
            removed_filter = self.filters.pop(index)
            print(f"Removed filter: {removed_filter}")
        else:
            raise IndexError(f"Filter index {index} out of range")
    
    # Remove all filters
    def clear_filters(self):
        self._ensure_loaded()
        assert self.df is not None  # for type checker
        
        self.filters.clear()
        self.filtered_data = self.df.copy()
        print("All filters cleared")
    
    # Set the logic for combining multiple filters
    def set_filter_logic(self, logic: Union[FilterLogic, str]):
        if isinstance(logic, str):
            logic = FilterLogic(logic.upper())
        
        self.filter_logic = logic
        print(f"Filter logic set to: {logic.value}")
    
    # Apply all current filters to the data and return filtered DataFrame
    def apply_filters(self) -> pd.DataFrame:
        self._ensure_loaded()
        assert self.df is not None  # for type checker
        
        if not self.filters:
            self.filtered_data = self.df.copy()
            return self.filtered_data
        
        def check_filter(row: pd.Series, filter_obj: Filter) -> bool:
            """Check if a row matches a single filter."""
            response_value = row[filter_obj.question]
            
            # Handle multiple choice questions (arrays)
            if isinstance(response_value, list):
                if isinstance(filter_obj.value, list):
                    # Check if any of the filter values are in the response
                    match = any(val in response_value for val in filter_obj.value)
                else:
                    # Check if the single filter value is in the response array
                    match = filter_obj.value in response_value
            else:
                # Handle single value responses
                if isinstance(filter_obj.value, list):
                    # Check if response value is in the filter value list
                    match = response_value in filter_obj.value
                else:
                    # Direct comparison
                    match = response_value == filter_obj.value
            
            # Apply negation if specified
            return not match if filter_obj.negate else match
        
        if self.filter_logic == FilterLogic.AND:
            # All filters must match
            mask = self.df.apply(
                lambda row: all(check_filter(row, f) for f in self.filters), 
                axis=1
            )
        else:  # OR logic
            # At least one filter must match
            mask = self.df.apply(
                lambda row: any(check_filter(row, f) for f in self.filters), 
                axis=1
            )
        
        self.filtered_data = self.df[mask]
        
        print(f"Applied {len(self.filters)} filter(s) with {self.filter_logic.value} logic")
        print(f"Filtered data: {len(self.filtered_data)} responses (from {len(self.df)} total)")
        
        return self.filtered_data
    
    # Get all values for a specific question from the (optionally filtered) data
    def get_question_values(self, question: str, filtered: bool = True) -> List[Any]:
        self._ensure_loaded()
        assert self.schema is not None and self.df is not None and self.filtered_data is not None

        if question not in self.schema['questions']:
            raise ValueError(f"Question '{question}' not found in schema")

        # Always apply filters if filtered=True to ensure up-to-date filtered_data
        if filtered:
            self.apply_filters()
            data = self.filtered_data
        else:
            data = self.df

        if question not in data.columns:
            print(f"Warning: Question '{question}' not found in response data")
            return []

        # Handle missing values
        values = data[question].dropna().tolist()

        # Flatten if this is a multiple choice question with arrays
        question_type = self.get_question_type(question)
        if question_type == 'multiple_choice':
            flattened_values = []
            for value in values:
                if isinstance(value, list):
                    flattened_values.extend(value)
                else:
                    flattened_values.append(value)
            values = flattened_values

        return values
    
    # Get count distribution for a specific question
    def get_question_counts(self, question: str, filtered: bool = True, group_other: bool = False) -> Dict[str, int]:
        values = self.get_question_values(question, filtered)
        
        # Handle matrix-type questions separately
        question_type = self.get_question_type(question)
        if question_type == 'matrix':
            # For matrix questions, flatten the dictionary responses
            flattened_values = []
            for value in values:
                if isinstance(value, dict):
                    # Extract all the individual responses from the matrix
                    for item, rating in value.items():
                        if rating is not None:
                            flattened_values.append(f"{item}: {rating}")
                else:
                    flattened_values.append(str(value))
            values = flattened_values
        
        # Count occurrences while preserving schema order
        # First get the expected order from schema
        question_info = self.get_question_info(question)
        schema_options = question_info.get('options', [])
        
        # Count all occurrences
        raw_counts = {}
        for value in values:
            value_str = str(value) if not isinstance(value, str) else value
            raw_counts[value_str] = raw_counts.get(value_str, 0) + 1
        
        # Build ordered counts dictionary preserving schema order
        counts = {}
        
        # First add schema options in their original order (if they have counts)
        for option in schema_options:
            if option in raw_counts:
                counts[option] = raw_counts[option]
        
        # Then add any unexpected options (like "Other") at the end
        for value_str, count in raw_counts.items():
            if value_str not in counts:
                counts[value_str] = count
        
        return counts
    
    # Get count distribution for matrix-type questions, organized by item and rating
    def get_matrix_counts(self, question: str, filtered: bool = True) -> Dict[str, Dict[str, int]]:
        values = self.get_question_values(question, filtered)
        
        # Verify this is a matrix question
        question_type = self.get_question_type(question)
        if question_type != 'matrix':
            raise ValueError(f"Question '{question}' is not a matrix-type question")
        
        matrix_counts = {}
        
        for value in values:
            if isinstance(value, dict):
                for item, rating in value.items():
                    if rating is not None:
                        if item not in matrix_counts:
                            matrix_counts[item] = {}
                        rating_str = str(rating)
                        matrix_counts[item][rating_str] = matrix_counts[item].get(rating_str, 0) + 1
        
        return matrix_counts
    
    # Get weighted scores for ranking-type questions
    def get_ranking_scores(self, question: str, filtered: bool = True, max_rank: int = 3) -> Dict[str, float]:
        values = self.get_question_values(question, filtered)
        
        # Verify this is a ranking question
        question_type = self.get_question_type(question)
        if question_type != 'ranking':
            raise ValueError(f"Question '{question}' is not a ranking-type question")
        
        ranking_scores = {}
        
        for value in values:
            if isinstance(value, list):
                # Calculate weighted scores: rank 1 = max_rank points, rank 2 = max_rank-1 points, etc.
                for rank, item in enumerate(value[:max_rank], 1):  # Only consider top max_rank items
                    if item not in ranking_scores:
                        ranking_scores[item] = 0.0
                    # Higher ranks get more points (rank 1 = max_rank points, rank 2 = max_rank-1 points, etc.)
                    ranking_scores[item] += max_rank - rank + 1
        
        return ranking_scores
    
    # Get position distribution for ranking-type questions
    def get_ranking_positions(self, question: str, filtered: bool = True, max_rank: int = 3) -> Dict[str, Dict[int, int]]:
        values = self.get_question_values(question, filtered)
        
        # Verify this is a ranking question
        question_type = self.get_question_type(question)
        if question_type != 'ranking':
            raise ValueError(f"Question '{question}' is not a ranking-type question")
        
        position_counts = {}
        
        for value in values:
            if isinstance(value, list):
                for rank, item in enumerate(value[:max_rank], 1):  # Only consider top max_rank items
                    if item not in position_counts:
                        position_counts[item] = {i: 0 for i in range(1, max_rank + 1)}
                    position_counts[item][rank] += 1
        
        return position_counts
    
    # Get a summary of the current state of the analyzer
    def get_summary(self) -> Dict[str, Any]:
        self._ensure_loaded()
        assert self.df is not None and self.filtered_data is not None and self.schema is not None
        
        return {
            'total_responses': len(self.df),
            'filtered_responses': len(self.filtered_data),
            'active_filters': len(self.filters),
            'filter_logic': self.filter_logic.value,
            'filters': [str(f) for f in self.filters],
            'available_questions': len(self.schema['questions'])
        }
    
    # Get the current filtered DataFrame
    def get_filtered_dataframe(self) -> pd.DataFrame:
        self._ensure_loaded()
        assert self.filtered_data is not None
        return self.filtered_data.copy()


def get_colors(colormap_name, num_colors=20):
    # Check for simple color names
    if colormap_name in plt.colormaps():
        cmap = plt.get_cmap(colormap_name)
        if(cmap.N < num_colors):
           return [cmap(i / cmap.N) for i in range(cmap.N)]
        else:
           return [cmap(i / num_colors) for i in range(num_colors)]
    else:
        # Fallback to nice colors if colormap not found
        return get_nice_colors()[:num_colors]                

def get_nice_colors():
    # High saturation, print-friendly colors
    colors = [
        (155/255, 75/255, 160/255, 1.0),   # Rich purple
        (50/255, 185/255, 155/255, 1.0),   # Vibrant teal  
        (225/255, 180/255, 40/255, 1.0),   # Golden yellow
        (215/255, 70/255, 55/255, 1.0),    # Bold coral
        (70/255, 130/255, 180/255, 1.0),   # Strong blue
        (220/255, 125/255, 35/255, 1.0),   # Vibrant orange
        (120/255, 185/255, 45/255, 1.0),   # Bright green
        (140/255, 120/255, 190/255, 1.0),  # Rich lavender
        (220/255, 140/255, 180/255, 1.0),  # Vibrant pink
        (210/255, 200/255, 95/255, 1.0),   # Rich cream
        (140/255, 140/255, 140/255, 1.0),  # Neutral gray
        (140/255, 200/255, 130/255, 1.0),  # Vibrant mint
    ]
    return colors

font_size = 23

# Configure matplotlib for consistent styling across all plots
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif', 'serif'],
    'font.size': font_size,
    'axes.titlesize': 18,
    'axes.labelsize': font_size,
    'xtick.labelsize': font_size,
    'ytick.labelsize': font_size,
    'legend.fontsize': 18,
    'figure.titlesize': 0,
    'axes.grid': True,
    'grid.alpha': 0.5,
    'axes.axisbelow': True,
    'axes.titlelocation': 'center',
    'axes.titlesize': 0
})

    
# A plotting utility class that works with SurveyAnalyzer to create visualizations.
class SurveyPlotter:
        
    # Initialize the plotter with a SurveyAnalyzer instance
    def __init__(self, analyzer: SurveyAnalyzer):
        self.analyzer = analyzer

        # self.colors = get_colors("tab10")
        self.role_colors = get_nice_colors()
    
    # Create a bar chart for a question's response distribution
    def create_bar_chart(self,
                        question: str,
                        title: Optional[str] = None, 
                        filtered: bool = True,
                        horizontal: bool = True,
                        figsize: tuple = (12, 8),
                        colormap: Optional[str] = None,
                        show_percentages: bool = False,
                        sort: bool = False,
                        label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        
        counts = self.analyzer.get_question_counts(question, filtered)
        
        if not counts:
            raise ValueError(f"No data found for question '{question}'")
        
        # Sort by count and optionally limit to top N
        if sort:
            sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        else:
            sorted_items = list(counts.items())
        
        labels, values = zip(*sorted_items) if sorted_items else ([], [])
        
        # Wrap long labels for better display based on label_wrap_width setting
        wrapped_labels = [wrap_label_smart(label, label_wrap_width) for label in labels]
        
        # Convert to percentages if requested
        if show_percentages:
            total = sum(values)
            percentages = [(v / total) * 100 for v in values]
            display_values = percentages            
            value_format = lambda x: f'{x:.1f}%'
        else:
            display_values = values
            value_format = lambda x: str(int(x))
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using colormap if specified, otherwise golden ratio system
        if colormap:
            colors = get_colors(colormap)
        else:
            colors = self.role_colors

        if horizontal:
            bars = ax.barh(range(len(labels)), display_values, color=colors)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(wrapped_labels)
            ax.invert_yaxis()  # Top item at top
            
            # Extend x-axis to make room for labels
            max_value = max(display_values) if display_values else 0
            ax.set_xlim(0, max_value * 1.22)  # Add padding
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                label_text = value_format(display_values[i])
                ax.text(width + max_value * 0.01, bar.get_y() + bar.get_height()/2, 
                    label_text, ha='left', va='center', fontsize=font_size)
        else:
            bars = ax.bar(range(len(labels)), display_values, color=colors)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(wrapped_labels, rotation=45, ha='right')
            
            # Extend y-axis to make room for labels
            max_value = max(display_values) if display_values else 0
            ax.set_ylim(0, max_value * 1.15)  # Add 15% padding
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                label_text = value_format(display_values[i])
                ax.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.01,
                    label_text, ha='center', va='bottom', fontsize=font_size)
        
        # Title removed for cleaner paper presentation
        
        # Use tight_layout with padding to prevent label cutoff
        # plt.tight_layout(pad=0.0)
        
        return fig
    
    # Create a comparison chart for the same question across different filter conditions
    def create_comparison_chart(self, question: str, filter_configs: List[Dict], 
                               labels: List[str], title: Optional[str] = None,
                               figsize: tuple = (12, 8),
                               show_percentages: bool = False, label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        if len(filter_configs) != len(labels):
            raise ValueError("filter_configs and labels must have the same length")
        
        data_sets = []
        
        # Store original state
        original_filters = self.analyzer.filters.copy()
        original_logic = self.analyzer.filter_logic
        
        try:
            for config, label in zip(filter_configs, labels):
                self.analyzer.clear_filters()
                
                # Apply filters for this dataset
                filters = config.get('filters', [])
                logic = config.get('logic', 'AND')
                
                for filter_def in filters:
                    self.analyzer.add_filter(
                        filter_def['question'], 
                        filter_def['value'], 
                        filter_def.get('negate', False)
                    )
                
                if filters:
                    self.analyzer.set_filter_logic(logic)
                    self.analyzer.apply_filters()
                
                # Get counts for the question
                counts = self.analyzer.get_question_counts(question)
                
                # Calculate total for percentage conversion if needed
                if show_percentages:
                    total = sum(counts.values())
                    if total > 0:
                        percentages = {k: (v / total) * 100 for k, v in counts.items()}
                        data_sets.append((label, percentages))
                    else:
                        data_sets.append((label, {}))
                else:
                    data_sets.append((label, counts))
        
        finally:
            # Restore original state
            self.analyzer.filters = original_filters
            self.analyzer.filter_logic = original_logic
            if original_filters:
                self.analyzer.apply_filters()
        
        # Find all unique options and preserve original survey order
        all_options_set = set()
        for _, counts in data_sets:
            all_options_set.update(counts.keys())
        
        # Get the original order from the survey schema
        question_info = self.analyzer.get_question_info(question)
        schema_options = question_info.get('options', [])
        
        # Preserve original schema order, then add any unexpected options at the end
        all_options = []
        for option in schema_options:
            if option in all_options_set:
                all_options.append(option)
                all_options_set.remove(option)
        
        # Add any remaining options (e.g., "Other") that weren't in the schema
        all_options.extend(sorted(all_options_set))
        
        # Apply label wrapping based on label_wrap_width setting
        wrapped_options = [wrap_label_smart(option, label_wrap_width) for option in all_options]
        
        # Prepare data for plotting
        x = np.arange(len(all_options))
        width = 0.8 / len(data_sets)  # Adjust width based on number of datasets
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using golden ratio color system for optimal visual separation
        colors = self.role_colors
        
        for i, (label, values_dict) in enumerate(data_sets):
            values = [values_dict.get(option, 0) for option in all_options]
            offset = width * (i - len(data_sets)/2 + 0.5)
            bars = ax.bar(x + offset, values, width, label=label, color=colors[i])
            
            # Add value labels on bars with consistent styling
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    if show_percentages:
                        label_text = f'{height:.1f}%'
                    else:
                        label_text = str(int(height))
                    ax.text(bar.get_x() + bar.get_width()/2., height + max(values) * 0.02,
                           label_text, ha='center', va='bottom')
        
        # Find the maximum value across all datasets for proper y-axis scaling
        all_values = []
        for _, values_dict in data_sets:
            all_values.extend(values_dict.values())
        max_value = max(all_values) if all_values else 0
        
        # Set y-axis limits with extra space for percentage labels (20% padding)
        ax.set_ylim(0, max_value * 1.2)
        
        ax.set_xlabel('Options')
        ax.set_ylabel('Percentage' if show_percentages else 'Count')
        ax.set_xticks(x)
        ax.set_xticklabels(wrapped_options, rotation=45, ha='right')
        ax.legend()
        
        # Title removed for cleaner paper presentation
        
        # Use tight_layout with padding to prevent label cutoff (consistent with other methods)
        plt.tight_layout(pad=3.0)
        
        return fig
    
    # Create a stacked bar chart for matrix-type questions (like Likert scales)
    def create_matrix_stacked_bar_chart(self, matrix_question: str,
                                        title: Optional[str] = None,
                                       filtered: bool = True,
                                       figsize: tuple = (14, 10),
                                       colormap: Optional[str] = None,
                                       horizontal: bool = True,
                                       label_wrap_width: Optional[int] = None,
                                       show_percentages: bool = False) -> mpl_figure.Figure:
        self.analyzer._ensure_loaded()
        assert self.analyzer.df is not None and self.analyzer.filtered_data is not None
        
        # Get the matrix counts using our new method
        matrix_counts = self.analyzer.get_matrix_counts(matrix_question, filtered)
        
        if not matrix_counts:
            raise ValueError(f"No data found for matrix question '{matrix_question}'")
        
        # Get the schema order for ratings and items
        question_info = self.analyzer.get_question_info(matrix_question)
        schema_scale = question_info.get('scale', [])
        schema_items = question_info.get('items', [])
        
        # Get all possible rating levels, preserving schema order
        all_ratings_set = set()
        for item_counts in matrix_counts.values():
            all_ratings_set.update(item_counts.keys())
        
        # Preserve schema order for ratings
        all_ratings = []
        for rating in schema_scale:
            if rating in all_ratings_set:
                all_ratings.append(rating)
                all_ratings_set.remove(rating)
        # Add any unexpected ratings at the end
        all_ratings.extend(sorted(all_ratings_set))
        
        # Get items preserving schema order
        items_set = set(matrix_counts.keys())
        items = []
        for item in schema_items:
            if item in items_set:
                items.append(item)
                items_set.remove(item)
        # Add any unexpected items at the end
        items.extend(sorted(items_set))
        # Wrap item labels based on label_wrap_width setting (default to 25 if None)
        effective_width = label_wrap_width if label_wrap_width is not None else 25
        wrapped_items = [wrap_label_smart(item, effective_width) for item in items]
        
        # Prepare data for stacked bar chart
        data = {}
        if show_percentages:
            # Calculate total responses per item for percentage calculation
            totals_per_item = [sum(matrix_counts[item].values()) for item in items]
            for rating in all_ratings:
                data[rating] = []
                for i, item in enumerate(items):
                    count = matrix_counts[item].get(rating, 0)
                    total = totals_per_item[i] if totals_per_item[i] > 0 else 1  # Avoid division by zero
                    percentage = (count / total) * 100
                    data[rating].append(percentage)
        else:
            for rating in all_ratings:
                data[rating] = [matrix_counts[item].get(rating, 0) for item in items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        if(colormap):
            colors = get_colors(colormap, len(all_ratings))
        else:
            colors = self.role_colors
        
        if horizontal:
            # Create horizontal stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, rating in enumerate(all_ratings):
                bars.append(ax.barh(wrapped_items, data[rating], left=bottom, 
                                   label=rating, color=colors[i]))
                bottom += data[rating]
        else:
            # Create vertical stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, rating in enumerate(all_ratings):
                bars.append(ax.bar(wrapped_items, data[rating], bottom=bottom, 
                                  label=rating, color=colors[i]))
                bottom += data[rating]
        
        # Customize the plot (remove axis labels as requested)
        if horizontal:
            # Rotate item labels if they're long
            plt.setp(ax.get_yticklabels(), rotation=0)
        else:
            # Rotate item labels if they're long
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Adjust layout to make room for legend first
        plt.subplots_adjust(bottom=0.25)
        
        # Add horizontal legend at bottom without title
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.05), ncol=len(all_ratings), frameon=False)
        
        return fig
    
    
    # Create a stacked position chart for ranking-type questions showing distribution across ranks
    def create_ranking_position_chart(self, ranking_question: str, title: Optional[str] = None,
                                     filtered: bool = True, figsize: tuple = (14, 8),
                                     colormap: Optional[str] = None,
                                     horizontal: bool = True, max_rank: int = 3,
                                     label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        # Get position distribution for ranking
        positions = self.analyzer.get_ranking_positions(ranking_question, filtered, max_rank)
        
        if not positions:
            raise ValueError(f"No data found for ranking question '{ranking_question}'")
        
        # Sort by total appearances (sum of all positions)
        total_mentions = {item: sum(pos_counts.values()) for item, pos_counts in positions.items()}
        sorted_items = sorted(total_mentions.items(), key=lambda x: x[1], reverse=True)
        items = [item for item, _ in sorted_items]
        
        # Wrap long labels for better display based on label_wrap_width setting (default to 30 if None)
        effective_width = label_wrap_width if label_wrap_width is not None else 30
        wrapped_items = [wrap_label_smart(item, effective_width) for item in items]
        
        # Prepare data for stacked bar chart
        rank_data = {}
        for rank in range(1, max_rank + 1):
            rank_data[f'Rank {rank}'] = [positions.get(item, {}).get(rank, 0) for item in items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using colormap if specified, otherwise golden ratio system
        colors = self.role_colors
        
        if horizontal:
            # Create horizontal stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, (rank_name, values) in enumerate(rank_data.items()):
                bars.append(ax.barh(wrapped_items, values, left=bottom, 
                                   label=rank_name, color=colors[i]))
                bottom += values
            ax.set_xlabel('Number of Times Ranked')
            ax.set_ylabel('Features')
            ax.invert_yaxis()  # Top item at top
        else:
            # Create vertical stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, (rank_name, values) in enumerate(rank_data.items()):
                bars.append(ax.bar(wrapped_items, values, bottom=bottom, 
                                  label=rank_name, color=colors[i]))
                bottom += values
            ax.set_xlabel('Features')
            ax.set_ylabel('Number of Times Ranked')
            plt.xticks(rotation=45, ha='right')
        
        # Add legend positioned in bottom right (empty space in horizontal charts)
        ax.legend(title='Ranking Position', bbox_to_anchor=(1.0, 0.0), loc='lower right')
        
        # Title removed for cleaner paper presentation
        plt.tight_layout()
        
        return fig


    # Create a stacked bar chart showing responses broken down by professional roles
    def create_role_stacked_chart(self,                                
                                question: str,
                                title: Optional[str] = None,
                                horizontal: bool = True,
                                figsize: Tuple[int, int] = (12, 8),
                                show_percentages: bool = True,
                                label_wrap_width: Optional[int] = None,
                                legend_loc: str = 'lower right',
                                legend_fontsize: int = 14,
                                legend_ncol: int = 1) -> mpl_figure.Figure:
        # Get all professional roles in the dataset
        role_data = self.analyzer.get_question_counts('professional_role')
        roles = list(role_data.keys())
        
        # Get main question data
        main_question_data = self.analyzer.get_question_counts(question)
        main_categories = list(main_question_data.keys())
        
        # Calculate total responses for percentage calculation
        total_responses = len(self.analyzer.responses) if self.analyzer.responses is not None else 0
        
        # Create data matrix: main_categories x roles
        role_breakdown = {}
        
        for role in roles:
            self.analyzer.clear_filters()
            self.analyzer.add_filter('professional_role', role)
            self.analyzer.apply_filters()
            role_counts = self.analyzer.get_question_counts(question, filtered=True)
            role_breakdown[role] = role_counts
        
        # Clear filters and reset logic
        self.analyzer.clear_filters()
        self.analyzer.set_filter_logic('AND')  # Reset to default
        
        # Prepare stacked percentage data
        # Each main category will have a stack of role contributions as percentages
        stack_data = {}
        for role in roles:
            stack_data[role] = [(role_breakdown[role].get(cat, 0) / total_responses) * 100 for cat in main_categories]
        
        # Get role colors
        role_colors = self.role_colors
        # [self.role_colors.get(role, '#CCCCCC') for role in roles]
        
        # Create shortened role names for legend
        def shorten_role(role):
            """Create shortened versions of role names for legend"""
            role_shortcuts = {
                'Level Designer': 'LD',
                'Game Designer': 'GD',
                'Technical Artist': 'TA',
                'Environment Artist': 'EA',
                'Programmer/Technical Designer': 'PTD',
                'Academic/Researcher': 'AR',
                'Other': 'Oth'
            }
            return role_shortcuts.get(role, role[:3])  # Default to first 3 chars if not found
        
        shortened_roles = [shorten_role(role) for role in roles]
        
        # Wrap labels based on label_wrap_width setting
        wrapped_main_categories = [wrap_label_smart(cat, label_wrap_width) for cat in main_categories]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        if horizontal:
            # Create horizontal stacked bars
            left = np.zeros(len(main_categories))
            bars = []
            
            for i, role in enumerate(roles):
                values = stack_data[role]
                bars.append(ax.barh(wrapped_main_categories, values, left=left, 
                                   label=shortened_roles[i], color=role_colors[i]))
                left += values
            
            # Show cumulative percentages at the end of bars if requested
            if show_percentages:
                max_percentage = max(left) if len(left) > 0 else 0
                for j, cumulative_percentage in enumerate(left):
                    if cumulative_percentage > 0:
                        ax.text(cumulative_percentage + 0.5, j, f'{cumulative_percentage:.1f}%', 
                               ha='left', va='center', fontsize=font_size)
                
                # Extend x-axis to accommodate percentage text within chart area
                if max_percentage > 0:
                    ax.set_xlim(0, max_percentage + 12)  # Add extra space for text
            
            # Remove y-axis label as requested
            ax.invert_yaxis()  # Top category at top
            
        else:
            # Create vertical stacked bars
            bottom = np.zeros(len(main_categories))
            bars = []
            
            for i, role in enumerate(roles):
                values = stack_data[role]
                bars.append(ax.bar(wrapped_main_categories, values, bottom=bottom,
                                  label=shortened_roles[i], color=role_colors[i]))
                bottom += values
            
            # Show cumulative percentages at the end of bars if requested
            if show_percentages:
                max_percentage = max(bottom) if len(bottom) > 0 else 0
                for j, cumulative_percentage in enumerate(bottom):
                    if cumulative_percentage > 0:
                        ax.text(j, cumulative_percentage + 0.5, f'{cumulative_percentage:.1f}%', 
                               ha='center', va='bottom', fontsize=10)
                
                # Extend y-axis to accommodate percentage text within chart area
                if max_percentage > 0:
                    ax.set_ylim(0, max_percentage + 8)  # Add extra space for text
            
            ax.set_ylabel('Percentage of Total Responses')
            # Remove x-axis label as requested when horizontal=False
            plt.xticks(rotation=45, ha='right')
        
        # Add legend with shortened role names inside the chart area
        ax.legend(loc=legend_loc, fontsize=legend_fontsize, ncol=legend_ncol)
        
        # Title removed for cleaner paper presentation
        plt.tight_layout()
                
        return fig

if __name__ == "__main__":
    # call the main function in survey_plot.py
    from survey_plot import main
    main()
