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
from typing import Dict, List, Any, Optional, Union, Set
from dataclasses import dataclass
from enum import Enum
from collections import Counter

# Configure matplotlib for better-looking plots
plt.rcParams.update({
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'Bitstream Vera Serif', 'serif'],
    'font.size': 10,
    'axes.titlesize': 18,
    'axes.labelsize': 16,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 14,
    'figure.titlesize': 20,
    'axes.grid': True,
    'grid.alpha': 0.3,
    'axes.axisbelow': True
})


class FilterLogic(Enum):
    """Enum for filter logic operations"""
    AND = "AND"
    OR = "OR"


@dataclass
class Filter:
    """Represents a single filter condition"""
    question: str
    value: Union[str, List[str]]
    negate: bool = False
    
    def __str__(self):
        negation = "NOT " if self.negate else ""
        return f"{negation}{self.question} = {self.value}"


class SurveyAnalyzer:
    """
    A comprehensive survey analysis tool that supports flexible filtering
    and data extraction from survey responses.
    """
    
    def __init__(self, schema_path: str, data_path: str):
        """
        Initialize the SurveyAnalyzer with schema and data files.
        
        Args:
            schema_path: Path to the JSON schema file
            data_path: Path to the JSON survey responses file
        """
        self.schema_path = schema_path
        self.data_path = data_path
        self.schema: Optional[Dict[str, Any]] = None
        self.responses: Optional[List[Dict[str, Any]]] = None
        self.df: Optional[pd.DataFrame] = None
        self.filtered_data: Optional[pd.DataFrame] = None
        self.filters: List[Filter] = []
        self.filter_logic = FilterLogic.AND
        
        self._load_data()
    
    def _load_data(self):
        """Load schema and survey response data from JSON files."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.responses = json.load(f)
            
            # Convert to DataFrame for easier analysis
            self.df = pd.DataFrame(self.responses)
            self.filtered_data = self.df.copy()
            
            if self.responses and self.schema:
                print(f"Loaded {len(self.responses)} survey responses")
                print(f"Available questions: {list(self.schema['questions'].keys())}")
            
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Could not find file: {e}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    def _ensure_loaded(self):
        """Ensure data is loaded, raise error if not."""
        if self.schema is None or self.responses is None or self.df is None:
            raise RuntimeError("Data not loaded. Check file paths and try again.")
    
    def get_question_info(self, question_key: str) -> Dict[str, Any]:
        """
        Get information about a specific question from the schema.
        
        Args:
            question_key: The key of the question in the schema
            
        Returns:
            Dictionary containing question information
        """
        self._ensure_loaded()
        assert self.schema is not None  # for type checker
        
        if question_key not in self.schema['questions']:
            raise ValueError(f"Question '{question_key}' not found in schema")
        
        return self.schema['questions'][question_key]
    
    def get_available_questions(self) -> List[str]:
        """Get list of all available question keys."""
        self._ensure_loaded()
        assert self.schema is not None  # for type checker
        return list(self.schema['questions'].keys())
    
    def get_question_options(self, question_key: str) -> List[str]:
        """
        Get available options for a question.
        
        Args:
            question_key: The key of the question
            
        Returns:
            List of available options, or empty list if not applicable
        """
        question_info = self.get_question_info(question_key)
        return question_info.get('options', [])
    
    def get_question_type(self, question_key: str) -> str:
        """
        Get the type of a question.
        
        Args:
            question_key: The key of the question
            
        Returns:
            Question type (e.g., 'single_choice', 'multiple_choice', etc.)
        """
        question_info = self.get_question_info(question_key)
        return question_info.get('type', 'unknown')
    
    def add_filter(self, question: str, value: Union[str, List[str]], negate: bool = False):
        """
        Add a filter condition.
        
        Args:
            question: Question key to filter on
            value: Value(s) to filter for
            negate: If True, filter for responses that DON'T match the value
        """
        self._ensure_loaded()
        assert self.schema is not None  # for type checker
        
        if question not in self.schema['questions']:
            raise ValueError(f"Question '{question}' not found in schema")
        
        filter_obj = Filter(question=question, value=value, negate=negate)
        self.filters.append(filter_obj)
        print(f"Added filter: {filter_obj}")
    
    def remove_filter(self, index: int):
        """
        Remove a filter by index.
        
        Args:
            index: Index of the filter to remove
        """
        if 0 <= index < len(self.filters):
            removed_filter = self.filters.pop(index)
            print(f"Removed filter: {removed_filter}")
        else:
            raise IndexError(f"Filter index {index} out of range")
    
    def clear_filters(self):
        """Remove all filters."""
        self._ensure_loaded()
        assert self.df is not None  # for type checker
        
        self.filters.clear()
        self.filtered_data = self.df.copy()
        print("All filters cleared")
    
    def set_filter_logic(self, logic: Union[FilterLogic, str]):
        """
        Set the logic for combining multiple filters.
        
        Args:
            logic: Either FilterLogic.AND, FilterLogic.OR, or string 'AND'/'OR'
        """
        if isinstance(logic, str):
            logic = FilterLogic(logic.upper())
        
        self.filter_logic = logic
        print(f"Filter logic set to: {logic.value}")
    
    def apply_filters(self) -> pd.DataFrame:
        """
        Apply all current filters to the data and return filtered DataFrame.
        
        Returns:
            Filtered DataFrame
        """
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
    
    def get_question_values(self, question: str, filtered: bool = True) -> List[Any]:
        """
        Get all values for a specific question from the (optionally filtered) data.
        
        Args:
            question: Question key to get values for
            filtered: If True, use filtered data; if False, use all data
            
        Returns:
            List of values for the specified question
        """
        self._ensure_loaded()
        assert self.schema is not None and self.df is not None and self.filtered_data is not None
        
        if question not in self.schema['questions']:
            raise ValueError(f"Question '{question}' not found in schema")
        
        data = self.filtered_data if filtered else self.df
        
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
    
    def get_question_counts(self, question: str, filtered: bool = True, group_other: bool = True) -> Dict[str, int]:
        """
        Get count distribution for a specific question.
        
        Args:
            question: Question key to analyze
            filtered: If True, use filtered data; if False, use all data
            group_other: If True, group values not in schema as "Other"
            
        Returns:
            Dictionary mapping values to their counts
        """
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
        
        # Get valid options from schema if grouping "Other"
        valid_options = set()
        if group_other:
            schema_options = self.get_question_options(question)
            if schema_options:  # Only apply if options are defined in schema
                valid_options = set(schema_options)
        
        # Count occurrences
        counts = {}
        other_count = 0
        
        for value in values:
            # Convert to string to ensure hashability
            value_str = str(value) if not isinstance(value, str) else value
            
            if group_other and valid_options and value_str not in valid_options:
                other_count += 1
            else:
                counts[value_str] = counts.get(value_str, 0) + 1
        
        # Add "Other" category if there are ungrouped values
        if other_count > 0:
            counts["Other"] = other_count
        
        return counts
    
    def get_matrix_counts(self, question: str, filtered: bool = True) -> Dict[str, Dict[str, int]]:
        """
        Get count distribution for matrix-type questions, organized by item and rating.
        
        Args:
            question: Matrix question key to analyze
            filtered: If True, use filtered data; if False, use all data
            
        Returns:
            Dictionary mapping items to rating counts
        """
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
    
    def get_ranking_scores(self, question: str, filtered: bool = True, max_rank: int = 3) -> Dict[str, float]:
        """
        Get weighted scores for ranking-type questions.
        
        Args:
            question: Ranking question key to analyze
            filtered: If True, use filtered data; if False, use all data
            max_rank: Maximum rank to consider (default 3 for "top 3" rankings)
            
        Returns:
            Dictionary mapping items to their weighted scores
        """
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
    
    def get_ranking_positions(self, question: str, filtered: bool = True, max_rank: int = 3) -> Dict[str, Dict[int, int]]:
        """
        Get position distribution for ranking-type questions.
        
        Args:
            question: Ranking question key to analyze
            filtered: If True, use filtered data; if False, use all data
            max_rank: Maximum rank to consider (default 3 for "top 3" rankings)
            
        Returns:
            Dictionary mapping items to position counts {item: {1: count, 2: count, 3: count}}
        """
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
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current state of the analyzer.
        
        Returns:
            Dictionary with summary information
        """
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
    
    def print_summary(self):
        """Print a formatted summary of the analyzer state."""
        summary = self.get_summary()
        
        print("\n=== Survey Analyzer Summary ===")
        print(f"Total responses: {summary['total_responses']}")
        print(f"Filtered responses: {summary['filtered_responses']}")
        print(f"Active filters: {summary['active_filters']}")
        print(f"Filter logic: {summary['filter_logic']}")
        print(f"Available questions: {summary['available_questions']}")
        
        if self.filters:
            print("\nActive filters:")
            for i, filter_str in enumerate(summary['filters']):
                print(f"  {i}: {filter_str}")
        else:
            print("\nNo active filters")
    
    def get_filtered_dataframe(self) -> pd.DataFrame:
        """
        Get the current filtered DataFrame.
        
        Returns:
            Filtered pandas DataFrame
        """
        self._ensure_loaded()
        assert self.filtered_data is not None
        return self.filtered_data.copy()
    
    def export_filtered_data(self, output_path: str, format: str = 'json'):
        """
        Export filtered data to a file.
        
        Args:
            output_path: Path to save the filtered data
            format: Output format ('json', 'csv', 'excel')
        """
        self._ensure_loaded()
        assert self.filtered_data is not None
        
        if format.lower() == 'json':
            self.filtered_data.to_json(output_path, orient='records', indent=2)
        elif format.lower() == 'csv':
            self.filtered_data.to_csv(output_path, index=False)
        elif format.lower() == 'excel':
            self.filtered_data.to_excel(output_path, index=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        print(f"Exported {len(self.filtered_data)} filtered responses to {output_path}")


class SurveyPlotter:
    """
    A plotting utility class that works with SurveyAnalyzer to create visualizations.
    """
    
    def __init__(self, analyzer: SurveyAnalyzer):
        """
        Initialize the plotter with a SurveyAnalyzer instance.
        
        Args:
            analyzer: SurveyAnalyzer instance to use for data
        """
        self.analyzer = analyzer
        
    def create_bar_chart(self, question: str, title: Optional[str] = None, 
                        filtered: bool = True, top_n: Optional[int] = None,
                        horizontal: bool = True, figsize: tuple = (10, 6),
                        save_path: Optional[str] = None, colormap: str = 'Dark2',
                        show_percentages: bool = False, label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        """
        Create a bar chart for a question's response distribution.
        
        Args:
            question: Question key to plot
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True, all data if False
            top_n: Show only top N responses
            horizontal: Create horizontal bar chart if True
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            colormap: Matplotlib colormap name for bar colors
            show_percentages: If True, show percentages instead of counts
            label_wrap_width: Width for label wrapping (None = no wrapping)
            
        Returns:
            matplotlib Figure object
        """
        counts = self.analyzer.get_question_counts(question, filtered)
        
        if not counts:
            raise ValueError(f"No data found for question '{question}'")
        
        # Sort by count and optionally limit to top N
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        if top_n:
            sorted_items = sorted_items[:top_n]
        
        labels, values = zip(*sorted_items) if sorted_items else ([], [])
        
        # Wrap long labels for better display only if label_wrap_width is specified
        if label_wrap_width:
            wrapped_labels = [textwrap.fill(label, width=label_wrap_width, break_long_words=False) for label in labels]
        else:
            wrapped_labels = labels
        
        # Convert to percentages if requested
        if show_percentages:
            total = sum(values)
            percentages = [(v / total) * 100 for v in values]
            display_values = percentages
            y_label = 'Percentage (%)'
            value_format = lambda x: f'{x:.1f}%'
        else:
            display_values = values
            y_label = 'Count'
            value_format = lambda x: str(int(x))
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using the specified colormap
        import matplotlib.cm as cm
        colors = cm.get_cmap(colormap)(np.linspace(0, 1, len(labels)))
        
        if horizontal:
            bars = ax.barh(range(len(labels)), display_values, color=colors)
            ax.set_yticks(range(len(labels)))
            ax.set_yticklabels(wrapped_labels)
            ax.set_xlabel(y_label)
            ax.invert_yaxis()  # Top item at top
            
            # Extend x-axis to make room for labels
            max_value = max(display_values) if display_values else 0
            ax.set_xlim(0, max_value * 1.15)  # Add 15% padding
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                width = bar.get_width()
                label_text = value_format(display_values[i])
                ax.text(width + max_value * 0.01, bar.get_y() + bar.get_height()/2, 
                    label_text, ha='left', va='center', fontweight='bold')
        else:
            bars = ax.bar(range(len(labels)), display_values, color=colors)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(wrapped_labels, rotation=45, ha='right')
            ax.set_ylabel(y_label)
            
            # Extend y-axis to make room for labels
            max_value = max(display_values) if display_values else 0
            ax.set_ylim(0, max_value * 1.15)  # Add 15% padding
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                label_text = value_format(display_values[i])
                ax.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.01,
                    label_text, ha='center', va='bottom', fontweight='bold')
        
        # Set title
        if title is None:
            question_info = self.analyzer.get_question_info(question)
            title = question_info.get('question', question)
        
        if filtered and len(self.analyzer.filters) > 0 and self.analyzer.filtered_data is not None:
            title = f"{title}\n(Filtered: {len(self.analyzer.filtered_data)} responses)"
        
        ax.set_title(title or question)
        
        # Use tight_layout with padding to prevent label cutoff
        plt.tight_layout(pad=2.0)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Chart saved to {save_path}")
        
        return fig
    
    def create_comparison_chart(self, question: str, filter_configs: List[Dict], 
                               labels: List[str], title: Optional[str] = None,
                               figsize: tuple = (14, 8), save_path: Optional[str] = None,
                               show_percentages: bool = False, label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        """
        Create a comparison chart for the same question across different filter conditions.
        
        Args:
            question: Question key to analyze
            filter_configs: List of filter configurations, each a dict with 'filters' and optional 'logic'
            labels: Labels for each filter configuration
            title: Chart title (auto-generated if None)
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            show_percentages: Show percentages instead of raw counts
            label_wrap_width: Width for wrapping x-axis labels (optional)
            
        Returns:
            matplotlib Figure object
            
        Example filter_configs:
        [
            {'filters': [{'question': 'years_experience', 'value': '0-2 years'}]},
            {'filters': [{'question': 'years_experience', 'value': '10+ years'}]}
        ]
        """
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
        
        # Apply label wrapping if specified
        if label_wrap_width:
            import textwrap
            wrapped_options = [textwrap.fill(option, width=label_wrap_width, break_long_words=False) 
                              for option in all_options]
        else:
            wrapped_options = all_options
        
        # Prepare data for plotting
        x = np.arange(len(all_options))
        width = 0.8 / len(data_sets)  # Adjust width based on number of datasets
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using highly contrasting colors for better comparison visibility
        import matplotlib.cm as cm
        
        # Define high-contrast color palette for comparison charts
        # These colors are specifically chosen for maximum visual distinction
        contrast_colors = [
            '#1f77b4',  # Strong blue
            '#ff7f0e',  # Strong orange
            '#2ca02c',  # Strong green
            '#d62728',  # Strong red
            '#9467bd',  # Strong purple
            '#8c564b',  # Strong brown
            '#e377c2',  # Strong pink
            '#7f7f7f',  # Strong gray
            '#bcbd22',  # Strong olive
            '#17becf'   # Strong cyan
        ]
        
        # Use high-contrast colors if we have enough, otherwise fall back to Dark2 with better spacing
        if len(data_sets) <= len(contrast_colors):
            colors = [contrast_colors[i] for i in range(len(data_sets))]
        else:
            # For more than 10 categories, use Dark2 with maximum spacing
            colormap = cm.get_cmap('Dark2')
            colors = [colormap(i / max(len(data_sets)-1, 1)) for i in range(len(data_sets))]
        
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
                           label_text, ha='center', va='bottom', fontweight='bold')
        
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
        
        if title is None:
            question_info = self.analyzer.get_question_info(question)
            base_title = question_info.get('question', question)
            title = f"{base_title}\nComparison"
        
        # Ensure title is not None
        final_title = title if title is not None else "Comparison Chart"
        ax.set_title(final_title)
        
        # Use tight_layout with padding to prevent label cutoff (consistent with other methods)
        plt.tight_layout(pad=3.0)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Comparison chart saved to {save_path}")
        
        return fig
    
    def create_stacked_bar_chart(self, question: str, stack_by: str, 
                                title: Optional[str] = None, filtered: bool = True,
                                figsize: tuple = (12, 8), save_path: Optional[str] = None) -> mpl_figure.Figure:
        """
        Create a stacked bar chart showing question responses broken down by another variable.
        
        Args:
            question: Main question to plot
            stack_by: Question to use for stacking/grouping
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            
        Returns:
            matplotlib Figure object
        """
        self.analyzer._ensure_loaded()
        assert self.analyzer.df is not None and self.analyzer.filtered_data is not None
        
        data = self.analyzer.filtered_data if filtered else self.analyzer.df
        
        if question not in data.columns or stack_by not in data.columns:
            raise ValueError(f"Questions '{question}' or '{stack_by}' not found in data")
        
        # Create crosstab
        ct = pd.crosstab(data[question], data[stack_by])
        
        fig, ax = plt.subplots(figsize=figsize)
        ct.plot(kind='bar', stacked=True, ax=ax)
        
        if title is None:
            q_info = self.analyzer.get_question_info(question)
            s_info = self.analyzer.get_question_info(stack_by)
            title = f"{q_info.get('question', question)}\nby {s_info.get('question', stack_by)}"
        
        ax.set_title(title or f"{question} by {stack_by}")
        ax.set_xlabel(question.replace('_', ' ').title())
        ax.set_ylabel('Count')
        plt.xticks(rotation=45, ha='right')
        plt.legend(title=stack_by.replace('_', ' ').title(), bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout(pad=2.0)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Stacked bar chart saved to {save_path}")
        
        return fig
    
    def create_pie_chart(self, question: str, title: Optional[str] = None,
                        filtered: bool = True, top_n: Optional[int] = None,
                        figsize: tuple = (8, 8), save_path: Optional[str] = None,
                        colormap: str = 'Set3') -> mpl_figure.Figure:
        """
        Create a pie chart for a question's response distribution.
        
        Args:
            question: Question key to plot
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True
            top_n: Show only top N responses, group others as "Other"
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            colormap: Matplotlib colormap name for slice colors
            
        Returns:
            matplotlib Figure object
        """
        counts = self.analyzer.get_question_counts(question, filtered)
        
        if not counts:
            raise ValueError(f"No data found for question '{question}'")
        
        # Sort by count
        sorted_items = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        
        if top_n and len(sorted_items) > top_n:
            top_items = sorted_items[:top_n]
            other_count = sum(count for _, count in sorted_items[top_n:])
            if other_count > 0:
                top_items.append(("Other", other_count))
            sorted_items = top_items
        
        labels, values = zip(*sorted_items) if sorted_items else ([], [])
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using the specified colormap
        import matplotlib.cm as cm
        colors = [cm.get_cmap(colormap)(i / len(labels)) for i in range(len(labels))]
        
        pie_result = ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90,
                           colors=colors, shadow=True, explode=[0.05] * len(labels))
        
        if title is None:
            question_info = self.analyzer.get_question_info(question)
            title = question_info.get('question', question)
        
        if filtered and len(self.analyzer.filters) > 0 and self.analyzer.filtered_data is not None:
            title = f"{title}\n(Filtered: {len(self.analyzer.filtered_data)} responses)"
        
        ax.set_title(title or question)
        
        # Use tight_layout with padding for pie charts
        plt.tight_layout(pad=2.0)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Pie chart saved to {save_path}")
        
        return fig
    
    def create_matrix_heatmap(self, matrix_question: str, title: Optional[str] = None,
                             filtered: bool = True, figsize: tuple = (12, 8),
                             save_path: Optional[str] = None, colormap: str = 'Blues') -> mpl_figure.Figure:
        """
        Create a heatmap for matrix-type questions (like Likert scales).
        
        Args:
            matrix_question: Matrix question key to plot
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            colormap: Matplotlib colormap name for heatmap colors
            
        Returns:
            matplotlib Figure object
        """
        self.analyzer._ensure_loaded()
        assert self.analyzer.df is not None and self.analyzer.filtered_data is not None
        
        data = self.analyzer.filtered_data if filtered else self.analyzer.df
        
        if matrix_question not in data.columns:
            raise ValueError(f"Question '{matrix_question}' not found in data")
        
        # Extract matrix data
        matrix_data = data[matrix_question].dropna()
        
        if len(matrix_data) == 0:
            raise ValueError(f"No data found for matrix question '{matrix_question}'")
        
        # Build matrix from responses
        all_tools = set()
        all_levels = set()
        for response in matrix_data:
            if isinstance(response, dict):
                for tool, level in response.items():
                    if level is not None:  # Skip None values
                        all_tools.add(tool)
                        all_levels.add(level)
        
        all_tools = sorted(all_tools)
        all_levels = sorted(all_levels)
        
        # Create count matrix
        matrix = np.zeros((len(all_tools), len(all_levels)))
        
        for response in matrix_data:
            if isinstance(response, dict):
                for tool, level in response.items():
                    if tool in all_tools and level in all_levels and level is not None:
                        tool_idx = all_tools.index(tool)
                        level_idx = all_levels.index(level)
                        matrix[tool_idx][level_idx] += 1
        
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(matrix, cmap=colormap, aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(all_levels)))
        ax.set_yticks(np.arange(len(all_tools)))
        ax.set_xticklabels(all_levels, rotation=45, ha='right')
        ax.set_yticklabels(all_tools)
        
        # Add text annotations with contrasting colors
        for i in range(len(all_tools)):
            for j in range(len(all_levels)):
                value = int(matrix[i, j])
                # Choose text color based on background intensity
                text_color = 'white' if value > matrix.max() * 0.5 else 'black'
                ax.text(j, i, str(value), ha="center", va="center", 
                       color=text_color, fontweight='bold', fontsize=10)
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Count')
        
        if title is None:
            question_info = self.analyzer.get_question_info(matrix_question)
            title = question_info.get('question', matrix_question)
        
        ax.set_title(title or matrix_question)
        plt.tight_layout(pad=2.0)
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Heatmap saved to {save_path}")
        
        return fig
    
    def create_matrix_stacked_bar_chart(self, matrix_question: str, title: Optional[str] = None,
                                       filtered: bool = True, figsize: tuple = (14, 10),
                                       save_path: Optional[str] = None, colormap: str = 'Set3',
                                       horizontal: bool = True, label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        """
        Create a stacked bar chart for matrix-type questions (like Likert scales).
        Each bar represents one item (tool/feature) with segments for each rating level.
        
        Args:
            matrix_question: Matrix question key to plot
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            colormap: Matplotlib colormap name
            horizontal: If True, create horizontal bars
            label_wrap_width: Width for label wrapping (None = default wrapping)
            
        Returns:
            matplotlib Figure object
        """
        self.analyzer._ensure_loaded()
        assert self.analyzer.df is not None and self.analyzer.filtered_data is not None
        
        # Get the matrix counts using our new method
        matrix_counts = self.analyzer.get_matrix_counts(matrix_question, filtered)
        
        if not matrix_counts:
            raise ValueError(f"No data found for matrix question '{matrix_question}'")
        
        # Get all possible rating levels across all items
        all_ratings = set()
        for item_counts in matrix_counts.values():
            all_ratings.update(item_counts.keys())
        all_ratings = sorted(all_ratings)
        
        # Get all items (tools/features) and wrap long names if specified
        items = sorted(matrix_counts.keys())
        if label_wrap_width:
            wrapped_items = [textwrap.fill(item, width=label_wrap_width, break_long_words=False) for item in items]
        else:
            wrapped_items = [textwrap.fill(item, width=25, break_long_words=False) for item in items]
        
        # Prepare data for stacked bar chart
        data = {}
        for rating in all_ratings:
            data[rating] = [matrix_counts[item].get(rating, 0) for item in items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors for different rating levels
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, len(all_ratings)))
        
        if horizontal:
            # Create horizontal stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, rating in enumerate(all_ratings):
                bars.append(ax.barh(wrapped_items, data[rating], left=bottom, 
                                   label=rating, color=colors[i], alpha=0.8))
                bottom += data[rating]
        else:
            # Create vertical stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, rating in enumerate(all_ratings):
                bars.append(ax.bar(wrapped_items, data[rating], bottom=bottom, 
                                  label=rating, color=colors[i], alpha=0.8))
                bottom += data[rating]
        
        # Customize the plot
        if horizontal:
            ax.set_xlabel('Number of Responses')
            ax.set_ylabel('Tools/Features')
            # Rotate item labels if they're long
            plt.setp(ax.get_yticklabels(), rotation=0)
        else:
            ax.set_xlabel('Tools/Features')
            ax.set_ylabel('Number of Responses')
            # Rotate item labels if they're long
            plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        # Add legend
        ax.legend(title='Experience Level', bbox_to_anchor=(1.05, 1), loc='upper left')
        
        # Set title
        if title is None:
            question_info = self.analyzer.get_question_info(matrix_question)
            title = question_info.get('question', matrix_question)
        
        ax.set_title(title or matrix_question)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Matrix stacked bar chart saved to {save_path}")
        
        return fig
    
    def create_ranking_weighted_chart(self, ranking_question: str, title: Optional[str] = None,
                                     filtered: bool = True, figsize: tuple = (14, 8),
                                     save_path: Optional[str] = None, colormap: str = 'viridis',
                                     horizontal: bool = True, max_rank: int = 3,
                                     label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        """
        Create a weighted score chart for ranking-type questions.
        
        Args:
            ranking_question: Ranking question key to plot
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            colormap: Matplotlib colormap name
            horizontal: If True, create horizontal bars
            max_rank: Maximum rank to consider (e.g., 3 for "top 3")
            label_wrap_width: Width for label wrapping (None = default wrapping)
            
        Returns:
            matplotlib Figure object
        """
        # Get weighted scores for ranking
        scores = self.analyzer.get_ranking_scores(ranking_question, filtered, max_rank)
        
        if not scores:
            raise ValueError(f"No data found for ranking question '{ranking_question}'")
        
        # Sort by score (highest first)
        sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        items, values = zip(*sorted_items) if sorted_items else ([], [])
        
        # Wrap long labels for better display if specified
        if label_wrap_width:
            wrapped_items = [textwrap.fill(item, width=label_wrap_width, break_long_words=False) for item in items]
        else:
            wrapped_items = [textwrap.fill(item, width=30, break_long_words=False) for item in items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors using colormap
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, len(items)))
        
        if horizontal:
            bars = ax.barh(wrapped_items, values, color=colors, alpha=0.8)
            ax.set_xlabel('Weighted Score')
            ax.set_ylabel('Features')
            ax.invert_yaxis()  # Top item at top
            
            # Add value labels on bars
            max_value = max(values) if values else 0
            for i, bar in enumerate(bars):
                width = bar.get_width()
                ax.text(width + max_value * 0.01, bar.get_y() + bar.get_height()/2, 
                       f'{values[i]:.1f}', ha='left', va='center', fontweight='bold')
        else:
            bars = ax.bar(wrapped_items, values, color=colors, alpha=0.8)
            ax.set_xlabel('Features')
            ax.set_ylabel('Weighted Score')
            plt.xticks(rotation=45, ha='right')
            
            # Add value labels on bars
            max_value = max(values) if values else 0
            for i, bar in enumerate(bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + max_value * 0.01,
                       f'{values[i]:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Set title
        if title is None:
            question_info = self.analyzer.get_question_info(ranking_question)
            title = question_info.get('question', ranking_question)
        
        # Add subtitle explaining the scoring
        full_title = f"{title}\n(Weighted scores: Rank 1 = {max_rank} pts, Rank 2 = {max_rank-1} pts, etc.)"
        ax.set_title(full_title)
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Ranking weighted chart saved to {save_path}")
        
        return fig
    
    def create_ranking_position_chart(self, ranking_question: str, title: Optional[str] = None,
                                     filtered: bool = True, figsize: tuple = (14, 8),
                                     save_path: Optional[str] = None, colormap: str = 'Set3',
                                     horizontal: bool = True, max_rank: int = 3,
                                     label_wrap_width: Optional[int] = None) -> mpl_figure.Figure:
        """
        Create a stacked position chart for ranking-type questions.
        Shows how often each item appears in rank 1, 2, 3, etc.
        
        Args:
            ranking_question: Ranking question key to plot
            title: Chart title (auto-generated if None)
            filtered: Use filtered data if True
            figsize: Figure size tuple
            save_path: Path to save the chart (optional)
            colormap: Matplotlib colormap name
            horizontal: If True, create horizontal bars
            max_rank: Maximum rank to consider (e.g., 3 for "top 3")
            label_wrap_width: Width for label wrapping (None = default wrapping)
            
        Returns:
            matplotlib Figure object
        """
        # Get position distribution for ranking
        positions = self.analyzer.get_ranking_positions(ranking_question, filtered, max_rank)
        
        if not positions:
            raise ValueError(f"No data found for ranking question '{ranking_question}'")
        
        # Sort by total appearances (sum of all positions)
        total_mentions = {item: sum(pos_counts.values()) for item, pos_counts in positions.items()}
        sorted_items = sorted(total_mentions.items(), key=lambda x: x[1], reverse=True)
        items = [item for item, _ in sorted_items]
        
        # Wrap long labels for better display if specified
        if label_wrap_width:
            wrapped_items = [textwrap.fill(item, width=label_wrap_width, break_long_words=False) for item in items]
        else:
            wrapped_items = [textwrap.fill(item, width=30, break_long_words=False) for item in items]
        
        # Prepare data for stacked bar chart
        rank_data = {}
        for rank in range(1, max_rank + 1):
            rank_data[f'Rank {rank}'] = [positions.get(item, {}).get(rank, 0) for item in items]
        
        # Create the plot
        fig, ax = plt.subplots(figsize=figsize)
        
        # Generate colors for different ranks
        colors = plt.cm.get_cmap(colormap)(np.linspace(0, 1, max_rank))
        
        if horizontal:
            # Create horizontal stacked bars
            bottom = np.zeros(len(items))
            bars = []
            for i, (rank_name, values) in enumerate(rank_data.items()):
                bars.append(ax.barh(wrapped_items, values, left=bottom, 
                                   label=rank_name, color=colors[i], alpha=0.8))
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
                                  label=rank_name, color=colors[i], alpha=0.8))
                bottom += values
            ax.set_xlabel('Features')
            ax.set_ylabel('Number of Times Ranked')
            plt.xticks(rotation=45, ha='right')
        
        # Add legend positioned in bottom right (empty space in horizontal charts)
        ax.legend(title='Ranking Position', bbox_to_anchor=(1.0, 0.0), loc='lower right')
        
        # Set title
        if title is None:
            question_info = self.analyzer.get_question_info(ranking_question)
            title = question_info.get('question', ranking_question)
        
        ax.set_title(title)
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Ranking position chart saved to {save_path}")
        
        return fig


def main():
    """Example usage of the SurveyAnalyzer"""
    
    # Initialize analyzer
    analyzer = SurveyAnalyzer(
        schema_path='survey-questions-schema.json',
        data_path='procedural-level-generation-survey.json'
    )
    
    # Show initial summary
    analyzer.print_summary()
    
    # Example: Filter for experienced programmers/technical designers
    print("\n=== Example: Filtering for experienced technical roles ===")
    
    # Add filters
    analyzer.add_filter('professional_role', 'Programmer/Technical Designer')
    analyzer.add_filter('years_experience', ['6-10 years', '10+ years'])
    
    # Set filter logic to AND (default)
    analyzer.set_filter_logic('AND')
    
    # Apply filters
    filtered_data = analyzer.apply_filters()
    
    # Get values for a specific question from filtered data
    print("\n=== Primary concerns of experienced technical designers ===")
    concerns = analyzer.get_question_counts('primary_concerns', filtered=True)
    for concern, count in sorted(concerns.items(), key=lambda x: x[1], reverse=True):
        print(f"{concern}: {count}")
    
    # Show summary again
    analyzer.print_summary()
    
    # Clear filters and try OR logic
    print("\n=== Example: OR logic with multiple experience levels ===")
    analyzer.clear_filters()
    analyzer.add_filter('years_experience', '0-2 years')
    analyzer.add_filter('years_experience', '10+ years')
    analyzer.set_filter_logic('OR')
    analyzer.apply_filters()
    
    # Analyze game engine preferences for beginners OR very experienced developers
    engine_counts = analyzer.get_question_counts('game_engines', filtered=True)
    print("\nGame engine preferences (beginners OR very experienced):")
    for engine, count in sorted(engine_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{engine}: {count}")
