#!/usr/bin/env python3
"""
Procedural Level Generation Survey Analysis Tool - Desktop Application
Python GUI version using tkinter and matplotlib
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from collections import Counter, defaultdict
import colorsys
import os

class SurveyAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Procedural Level Generation Survey Analysis Tool")
        self.root.geometry("1400x900")
        self.root.configure(bg='#f0f0f0')
        
        # Data storage
        self.survey_data = None
        self.schema_data = None
        self.filtered_data = None
        
        # Filter states
        self.demographic_filters = {
            'professional_role': set(),
            'years_experience': set()
        }
        self.advanced_filters = []
        
        # Current analysis
        self.current_question = None
        self.current_chart = None
        
        # Create the GUI
        self.create_widgets()
        self.load_data()
        
    def create_widgets(self):
        """Create the main GUI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 Procedural Level Generation Survey Analysis", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W+tk.E)
        
        # Left panel for controls
        self.create_control_panel(main_frame)
        
        # Right panel for charts
        self.create_chart_panel(main_frame)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Load data to begin analysis")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def create_control_panel(self, parent):
        """Create the left control panel"""
        control_frame = ttk.Frame(parent, padding="5")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_frame.columnconfigure(0, weight=1)
        
        # Data loading section
        data_frame = ttk.LabelFrame(control_frame, text="Data", padding="5")
        data_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        data_frame.columnconfigure(0, weight=1)
        
        ttk.Button(data_frame, text="Load Survey Data", 
                  command=self.load_data).grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        
        self.data_summary_var = tk.StringVar()
        self.data_summary_var.set("No data loaded")
        ttk.Label(data_frame, textvariable=self.data_summary_var).grid(row=1, column=0, sticky=tk.W, pady=2)
        
        # Question selection
        question_frame = ttk.LabelFrame(control_frame, text="Question Analysis", padding="5")
        question_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        question_frame.columnconfigure(0, weight=1)
        
        ttk.Label(question_frame, text="Select Question:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.question_var = tk.StringVar()
        self.question_combo = ttk.Combobox(question_frame, textvariable=self.question_var, 
                                          state="readonly", width=30)
        self.question_combo.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        self.question_combo.bind('<<ComboboxSelected>>', self.on_question_selected)
        
        # Chart type selection
        chart_frame = ttk.LabelFrame(control_frame, text="Chart Options", padding="5")
        chart_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        chart_frame.columnconfigure(0, weight=1)
        
        ttk.Label(chart_frame, text="Chart Type:").grid(row=0, column=0, sticky=tk.W, pady=2)
        
        self.chart_type_var = tk.StringVar(value="bar")
        chart_types = [("Bar Chart", "bar"), ("Pie Chart", "pie"), ("Horizontal Bar", "barh")]
        
        for i, (text, value) in enumerate(chart_types):
            ttk.Radiobutton(chart_frame, text=text, variable=self.chart_type_var, 
                           value=value, command=self.redraw_chart).grid(row=i+1, column=0, sticky=tk.W, pady=1)
        
        # Demographics filtering
        self.create_demographics_panel(control_frame)
        
        # Advanced filtering
        self.create_advanced_filtering_panel(control_frame)
        
    def create_demographics_panel(self, parent):
        """Create demographics filtering panel"""
        demo_frame = ttk.LabelFrame(parent, text="Demographics Filters", padding="5")
        demo_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        demo_frame.columnconfigure(0, weight=1)
        
        # Professional role
        role_frame = ttk.LabelFrame(demo_frame, text="Professional Role", padding="3")
        role_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        role_frame.columnconfigure(0, weight=1)
        
        self.role_vars = {}
        self.role_frame = role_frame
        
        # Years experience
        exp_frame = ttk.LabelFrame(demo_frame, text="Years Experience", padding="3")
        exp_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=2)
        exp_frame.columnconfigure(0, weight=1)
        
        self.exp_vars = {}
        self.exp_frame = exp_frame
        
        # Summary
        self.demo_summary_var = tk.StringVar()
        self.demo_summary_var.set("Filters not applied")
        ttk.Label(demo_frame, textvariable=self.demo_summary_var, 
                 font=('Arial', 9)).grid(row=2, column=0, sticky=tk.W, pady=5)
        
    def create_advanced_filtering_panel(self, parent):
        """Create advanced filtering panel"""
        filter_frame = ttk.LabelFrame(parent, text="Advanced Filters", padding="5")
        filter_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        filter_frame.columnconfigure(0, weight=1)
        
        button_frame = ttk.Frame(filter_frame)
        button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=2)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        
        ttk.Button(button_frame, text="Add Filter", 
                  command=self.add_advanced_filter).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 2))
        
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all_filters).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(2, 0))
        
        # Filter list (will be populated dynamically)
        self.filter_list_frame = ttk.Frame(filter_frame)
        self.filter_list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        self.filter_list_frame.columnconfigure(0, weight=1)
        
    def create_chart_panel(self, parent):
        """Create the right chart panel"""
        chart_frame = ttk.Frame(parent, padding="5")
        chart_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        chart_frame.columnconfigure(0, weight=1)
        chart_frame.rowconfigure(0, weight=1)
        
        # Create matplotlib figure
        self.fig, self.ax = plt.subplots(figsize=(10, 8))
        self.fig.patch.set_facecolor('white')
        
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add navigation toolbar
        toolbar_frame = ttk.Frame(chart_frame)
        toolbar_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        self.toolbar = NavigationToolbar2Tk(self.canvas, toolbar_frame)
        self.toolbar.update()
        
        # Initial empty chart
        self.show_welcome_chart()
        
    def show_welcome_chart(self):
        """Show a welcome message in the chart area"""
        self.ax.clear()
        self.ax.text(0.5, 0.5, '📊\n\nWelcome to Survey Analysis Tool\n\nLoad data and select a question to begin analysis', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=self.ax.transAxes, fontsize=16, alpha=0.7)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        self.canvas.draw()
        
    def load_data(self):
        """Load survey data and schema from JSON files"""
        try:
            # Check if files exist in current directory
            survey_file = "procedural-level-generation-survey.json"
            schema_file = "survey-questions-schema.json"
            
            if not os.path.exists(survey_file) or not os.path.exists(schema_file):
                messagebox.showerror("Error", 
                    f"Data files not found in current directory.\n"
                    f"Please ensure these files exist:\n"
                    f"• {survey_file}\n"
                    f"• {schema_file}")
                return
            
            # Load survey responses
            with open(survey_file, 'r', encoding='utf-8') as f:
                self.survey_data = json.load(f)
            
            # Load schema
            with open(schema_file, 'r', encoding='utf-8') as f:
                self.schema_data = json.load(f)
            
            # Validate data
            if not isinstance(self.survey_data, list) or len(self.survey_data) == 0:
                raise ValueError("Survey data is empty or invalid")
                
            if 'questions' not in self.schema_data:
                raise ValueError("Schema data is missing questions")
            
            # Initialize filtered data
            self.filtered_data = self.survey_data.copy()
            
            # Update UI
            self.update_data_summary()
            self.populate_question_dropdown()
            self.initialize_demographics()
            self.update_demographics_summary()
            
            self.status_var.set(f"Data loaded successfully - {len(self.survey_data)} responses")
            
        except Exception as e:
            messagebox.showerror("Error Loading Data", f"Failed to load data:\n{str(e)}")
            self.status_var.set("Error loading data")
            
    def update_data_summary(self):
        """Update the data summary display"""
        if self.survey_data and self.schema_data:
            summary = f"Responses: {len(self.survey_data)}\nQuestions: {len(self.schema_data['questions'])}"
            self.data_summary_var.set(summary)
        else:
            self.data_summary_var.set("No data loaded")
            
    def populate_question_dropdown(self):
        """Populate the question selection dropdown"""
        if not self.schema_data:
            return
            
        questions = []
        for q_id, q_data in self.schema_data['questions'].items():
            if q_id != 'id':  # Skip ID field
                question_text = q_data.get('question', q_id)
                # Truncate long questions for display
                if len(question_text) > 50:
                    question_text = question_text[:47] + "..."
                questions.append((f"{q_id}: {question_text}", q_id))
        
        # Sort questions
        questions.sort(key=lambda x: x[1])
        
        # Update combobox
        self.question_combo['values'] = [q[0] for q in questions]
        self.question_combo.state(['readonly'])
        
        # Store mapping for easy lookup
        self.question_mapping = {q[0]: q[1] for q in questions}
        
    def initialize_demographics(self):
        """Initialize demographics filter checkboxes"""
        if not self.survey_data or not self.schema_data:
            return
            
        # Initialize professional role filters
        self.initialize_demographic_checkboxes('professional_role', self.role_vars, self.role_frame)
        
        # Initialize years experience filters  
        self.initialize_demographic_checkboxes('years_experience', self.exp_vars, self.exp_frame)
        
    def initialize_demographic_checkboxes(self, field_name, var_dict, frame):
        """Initialize checkboxes for a demographic field"""
        # Clear existing checkboxes
        for widget in frame.winfo_children():
            if isinstance(widget, ttk.Checkbutton):
                widget.destroy()
                
        # Get options from schema
        question_data = self.schema_data['questions'].get(field_name, {})
        options = question_data.get('options', [])
        
        # Count occurrences and identify "Other" responses
        counts = Counter()
        other_count = 0
        
        for response in self.survey_data:
            value = response.get(field_name, '')
            if value in options:
                counts[value] += 1
            elif value and value.strip():
                other_count += 1
                
        # Add "Other" if there are non-schema responses
        if other_count > 0:
            options = options + ['Other']
            counts['Other'] = other_count
            
        # Sort by count (descending)
        sorted_options = sorted(options, key=lambda x: counts[x], reverse=True)
        
        # Create checkboxes
        var_dict.clear()
        
        for i, option in enumerate(sorted_options):
            var = tk.BooleanVar(value=True)  # Start with all selected
            var_dict[option] = var
            
            text = f"{option} ({counts[option]})"
            cb = ttk.Checkbutton(frame, text=text, variable=var, 
                               command=lambda f=field_name: self.on_demographic_change(f))
            cb.grid(row=i+1, column=0, sticky=tk.W, pady=1)
            
        # Initialize filter sets
        self.demographic_filters[field_name] = set(sorted_options)
        
    def on_demographic_change(self, field_name):
        """Handle demographic filter changes"""
        var_dict = self.role_vars if field_name == 'professional_role' else self.exp_vars
        
        # Update filter set
        selected_options = set()
        for option, var in var_dict.items():
            if var.get():
                selected_options.add(option)
                
        self.demographic_filters[field_name] = selected_options
        
        # Apply filters and update display
        self.apply_all_filters()
        self.update_demographics_summary()
        
    def apply_all_filters(self):
        """Apply all active filters to the data"""
        if not self.survey_data:
            return
            
        # Start with all data
        filtered = self.survey_data.copy()
        
        # Apply demographic filters
        for field_name, selected_options in self.demographic_filters.items():
            if not selected_options:  # If no options selected, skip this field
                continue
                
            question_data = self.schema_data['questions'].get(field_name, {})
            schema_options = question_data.get('options', [])
            
            filtered = [
                response for response in filtered
                if self.matches_demographic_filter(response, field_name, selected_options, schema_options)
            ]
            
        self.filtered_data = filtered
        
        # Redraw current chart if a question is selected
        if self.current_question:
            self.analyze_question(self.current_question)
            
    def matches_demographic_filter(self, response, field_name, selected_options, schema_options):
        """Check if a response matches the demographic filter"""
        value = response.get(field_name, '')
        
        if value in schema_options:
            return value in selected_options
        elif value and value.strip() and 'Other' in selected_options:
            return True
        else:
            return not value or not value.strip()
            
    def update_demographics_summary(self):
        """Update the demographics summary display"""
        if not self.filtered_data:
            self.demo_summary_var.set("No data filtered")
            return
            
        total_responses = len(self.survey_data) if self.survey_data else 0
        filtered_responses = len(self.filtered_data)
        
        if total_responses > 0:
            percentage = (filtered_responses / total_responses) * 100
            summary = f"Showing {filtered_responses} of {total_responses} responses ({percentage:.1f}%)"
        else:
            summary = "No data available"
            
        self.demo_summary_var.set(summary)
        
    def on_question_selected(self, event=None):
        """Handle question selection"""
        selected_display = self.question_var.get()
        if selected_display in self.question_mapping:
            question_id = self.question_mapping[selected_display]
            self.analyze_question(question_id)
            
    def analyze_question(self, question_id):
        """Analyze and visualize a specific question"""
        if not self.filtered_data or not self.schema_data:
            return
            
        self.current_question = question_id
        question_data = self.schema_data['questions'].get(question_id, {})
        question_type = question_data.get('type', '')
        
        # Clear previous chart
        self.ax.clear()
        
        try:
            if question_type in ['single_choice', 'multiple_choice']:
                self.create_choice_chart(question_id, question_data)
            elif question_type == 'matrix':
                self.create_matrix_chart(question_id, question_data)
            elif question_type == 'ranking':
                self.create_ranking_chart(question_id, question_data)
            else:
                self.create_text_analysis_chart(question_id, question_data)
                
            self.canvas.draw()
            self.status_var.set(f"Analyzing: {question_data.get('question', question_id)}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze question:\n{str(e)}")
            self.status_var.set("Error analyzing question")
            
    def create_choice_chart(self, question_id, question_data):
        """Create chart for single/multiple choice questions"""
        # Collect responses
        responses = []
        for response in self.filtered_data:
            value = response.get(question_id, None)
            if value:
                if isinstance(value, list):
                    responses.extend(value)
                else:
                    responses.append(value)
                    
        if not responses:
            self.ax.text(0.5, 0.5, 'No data available for this question', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14, alpha=0.7)
            return
            
        # Count responses
        counts = Counter(responses)
        
        # Get schema options for ordering
        schema_options = question_data.get('options', [])
        
        # Separate schema and non-schema responses
        schema_counts = {opt: counts.get(opt, 0) for opt in schema_options}
        other_counts = {k: v for k, v in counts.items() if k not in schema_options}
        
        # Combine, putting "Other" responses at the end
        final_counts = {}
        final_counts.update(schema_counts)
        
        if other_counts:
            other_total = sum(other_counts.values())
            final_counts['Other'] = other_total
            
        # Remove zero counts
        final_counts = {k: v for k, v in final_counts.items() if v > 0}
        
        if not final_counts:
            self.ax.text(0.5, 0.5, 'No responses for this question', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14, alpha=0.7)
            return
            
        # Create chart based on selected type
        chart_type = self.chart_type_var.get()
        
        if chart_type == "pie":
            self.create_pie_chart(final_counts, question_data)
        elif chart_type == "barh":
            self.create_horizontal_bar_chart(final_counts, question_data)
        else:
            self.create_bar_chart(final_counts, question_data)
            
    def create_bar_chart(self, counts, question_data):
        """Create a vertical bar chart"""
        labels = list(counts.keys())
        values = list(counts.values())
        
        # Generate colors
        colors = self.generate_colors(len(labels))
        
        bars = self.ax.bar(labels, values, color=colors)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom')
        
        self.ax.set_ylabel('Number of Responses')
        self.ax.set_title(question_data.get('question', 'Question Analysis'), wrap=True)
        
        # Rotate labels if they're long
        if any(len(label) > 10 for label in labels):
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
            
        self.ax.grid(True, alpha=0.3, axis='y')
        
    def create_horizontal_bar_chart(self, counts, question_data):
        """Create a horizontal bar chart"""
        labels = list(counts.keys())
        values = list(counts.values())
        
        # Sort by value
        sorted_items = sorted(zip(labels, values), key=lambda x: x[1])
        labels, values = zip(*sorted_items)
        
        colors = self.generate_colors(len(labels))
        
        bars = self.ax.barh(labels, values, color=colors)
        
        # Add value labels
        for bar in bars:
            width = bar.get_width()
            self.ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{int(width)}', ha='left', va='center', 
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        self.ax.set_xlabel('Number of Responses')
        self.ax.set_title(question_data.get('question', 'Question Analysis'), wrap=True)
        self.ax.grid(True, alpha=0.3, axis='x')
        
    def create_pie_chart(self, counts, question_data):
        """Create a pie chart"""
        labels = list(counts.keys())
        values = list(counts.values())
        
        colors = self.generate_colors(len(labels))
        
        # Create pie chart with percentages
        wedges, texts, autotexts = self.ax.pie(values, labels=labels, colors=colors, 
                                              autopct='%1.1f%%', startangle=90)
        
        # Improve text readability
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            
        self.ax.set_title(question_data.get('question', 'Question Analysis'), wrap=True)
        
    def create_matrix_chart(self, question_id, question_data):
        """Create chart for matrix questions"""
        # Matrix questions have sub-questions
        sub_questions = question_data.get('sub_questions', {})
        scale_options = question_data.get('scale_options', [])
        
        if not sub_questions or not scale_options:
            self.ax.text(0.5, 0.5, 'Matrix question structure not available', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14, alpha=0.7)
            return
            
        # Collect matrix data
        matrix_data = {}
        for response in self.filtered_data:
            matrix_response = response.get(question_id, {})
            if isinstance(matrix_response, dict):
                for sub_q, value in matrix_response.items():
                    if sub_q not in matrix_data:
                        matrix_data[sub_q] = Counter()
                    if value in scale_options:
                        matrix_data[sub_q][value] += 1
                        
        if not matrix_data:
            self.ax.text(0.5, 0.5, 'No matrix data available', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14, alpha=0.7)
            return
            
        # Create stacked bar chart
        sub_q_labels = list(matrix_data.keys())
        scale_labels = scale_options
        
        # Prepare data for stacked bars
        bottom = np.zeros(len(sub_q_labels))
        colors = self.generate_colors(len(scale_labels))
        
        for i, scale_value in enumerate(scale_labels):
            values = [matrix_data.get(sub_q, {}).get(scale_value, 0) for sub_q in sub_q_labels]
            self.ax.bar(sub_q_labels, values, bottom=bottom, label=scale_value, color=colors[i])
            bottom += values
            
        self.ax.set_ylabel('Number of Responses')
        self.ax.set_title(question_data.get('question', 'Matrix Question Analysis'))
        self.ax.legend()
        
        # Rotate labels if needed
        if any(len(label) > 15 for label in sub_q_labels):
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
            
    def create_ranking_chart(self, question_id, question_data):
        """Create chart for ranking questions"""
        # Collect ranking data
        ranking_data = defaultdict(list)
        
        for response in self.filtered_data:
            ranking_response = response.get(question_id, {})
            if isinstance(ranking_response, dict):
                for item, rank in ranking_response.items():
                    try:
                        ranking_data[item].append(int(rank))
                    except (ValueError, TypeError):
                        continue
                        
        if not ranking_data:
            self.ax.text(0.5, 0.5, 'No ranking data available', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14, alpha=0.7)
            return
            
        # Calculate average rankings
        avg_rankings = {}
        for item, ranks in ranking_data.items():
            avg_rankings[item] = np.mean(ranks)
            
        # Sort by average ranking (lower is better)
        sorted_items = sorted(avg_rankings.items(), key=lambda x: x[1])
        
        items, avg_ranks = zip(*sorted_items)
        colors = self.generate_colors(len(items))
        
        bars = self.ax.bar(items, avg_ranks, color=colors)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            self.ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}', ha='center', va='bottom')
        
        self.ax.set_ylabel('Average Ranking (Lower = Better)')
        self.ax.set_title(question_data.get('question', 'Ranking Analysis'))
        
        if any(len(item) > 10 for item in items):
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
            
        self.ax.grid(True, alpha=0.3, axis='y')
        
    def create_text_analysis_chart(self, question_id, question_data):
        """Create basic analysis for text questions"""
        responses = []
        for response in self.filtered_data:
            value = response.get(question_id, '')
            if value and isinstance(value, str) and value.strip():
                responses.append(value.strip())
                
        if not responses:
            self.ax.text(0.5, 0.5, 'No text responses available', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=14, alpha=0.7)
            return
            
        # Simple word frequency analysis
        all_words = []
        for response in responses:
            words = response.lower().split()
            # Filter out very short words and common stop words
            filtered_words = [word for word in words if len(word) > 3 and 
                            word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'way', 'who']]
            all_words.extend(filtered_words)
            
        if not all_words:
            self.ax.text(0.5, 0.5, f'Text Analysis\n\nTotal responses: {len(responses)}\nNo common words found', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=12, alpha=0.7)
            return
            
        # Get top 10 words
        word_counts = Counter(all_words)
        top_words = word_counts.most_common(10)
        
        if top_words:
            words, counts = zip(*top_words)
            colors = self.generate_colors(len(words))
            
            bars = self.ax.bar(words, counts, color=colors)
            
            for bar in bars:
                height = bar.get_height()
                self.ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{int(height)}', ha='center', va='bottom')
            
            self.ax.set_ylabel('Frequency')
            self.ax.set_title(f'{question_data.get("question", "Text Analysis")}\n(Top Words)')
            plt.setp(self.ax.get_xticklabels(), rotation=45, ha='right')
        else:
            self.ax.text(0.5, 0.5, f'Text Analysis\n\nTotal responses: {len(responses)}', 
                        horizontalalignment='center', verticalalignment='center', 
                        transform=self.ax.transAxes, fontsize=12, alpha=0.7)
            
    def generate_colors(self, n):
        """Generate n distinct colors"""
        colors = []
        for i in range(n):
            hue = i / n
            saturation = 0.7
            value = 0.8
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(rgb)
        return colors
        
    def redraw_chart(self):
        """Redraw the current chart with new settings"""
        if self.current_question:
            self.analyze_question(self.current_question)
            
    def add_advanced_filter(self):
        """Add an advanced filter (placeholder implementation)"""
        messagebox.showinfo("Advanced Filters", "Advanced filtering feature coming soon!\n\nFor now, use the demographics filters to narrow down your analysis.")
        
    def clear_all_filters(self):
        """Clear all filters and reset to original data"""
        # Reset demographic filters
        for field_name in self.demographic_filters:
            if field_name == 'professional_role':
                var_dict = self.role_vars
            else:
                var_dict = self.exp_vars
                
            for var in var_dict.values():
                var.set(True)
                
            # Update filter set
            self.demographic_filters[field_name] = set(var_dict.keys())
            
        # Clear advanced filters
        self.advanced_filters.clear()
        
        # Reapply filters (which should now include everything)
        self.apply_all_filters()
        self.update_demographics_summary()
        
        self.status_var.set("All filters cleared")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = SurveyAnalysisApp(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')  # Optional: add icon file
    except:
        pass
        
    # Center window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Start the application
    root.mainloop()

if __name__ == "__main__":
    main()
