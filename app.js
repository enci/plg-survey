// Procedural Level Generation Survey Analysis Tool
// Version 3.0 - Complete with Filtering System

console.log('Survey Analysis Tool Initialized');

// Global application state
const SurveyApp = {
    data: {
        responses: null,
        schema: null,
        loaded: false
    },
    charts: {},
    filters: {
        active: [],
        filteredData: null,
        nextId: 1
    },
    
    // Initialize the application
    init() {
        console.log('Initializing Survey Analysis Tool...');
        this.setupEventListeners();
        // Auto-load data on startup
        this.loadData();
    },
    
    // Set up event listeners
    setupEventListeners() {
        // Add question selector listener
        const questionSelect = document.getElementById('questionSelect');
        if (questionSelect) {
            questionSelect.addEventListener('change', (e) => this.analyzeQuestion(e.target.value));
        }

        // Add filter button listeners
        const addFilterBtn = document.getElementById('addFilterBtn');
        if (addFilterBtn) {
            addFilterBtn.addEventListener('click', () => this.addFilter());
        }

        const clearAllFiltersBtn = document.getElementById('clearAllFilters');
        if (clearAllFiltersBtn) {
            clearAllFiltersBtn.addEventListener('click', () => this.clearAllFilters());
        }

        // Add filter logic selector listener
        const filterLogic = document.getElementById('filterLogic');
        if (filterLogic) {
            filterLogic.addEventListener('change', () => this.applyFilters());
        }
    },
    
    // Load survey data and schema
    async loadData() {
        try {
            // Load both files concurrently
            const [responsesResponse, schemaResponse] = await Promise.all([
                fetch('procedural-level-generation-survey.json'),
                fetch('survey-questions-schema.json')
            ]);
            
            // Check if both requests were successful
            if (!responsesResponse.ok) {
                throw new Error(`Failed to load survey responses: ${responsesResponse.status}`);
            }
            if (!schemaResponse.ok) {
                throw new Error(`Failed to load survey schema: ${schemaResponse.status}`);
            }
            
            // Parse JSON data
            const responsesData = await responsesResponse.json();
            const schemaData = await schemaResponse.json();
            
            // Store data
            this.data.responses = responsesData;
            this.data.schema = schemaData;
            this.data.loaded = true;
            
            // Validate and show success
            this.validateData();
            this.showDataSummary();
            
        } catch (error) {
            console.error('Error loading data:', error);
            alert(`Failed to load data: ${error.message}`);
        }
    },
    
    // Validate loaded data
    validateData() {
        const { responses, schema } = this.data;
        
        if (!Array.isArray(responses)) {
            throw new Error('Survey responses is not an array');
        }
        
        if (!schema || !schema.questions) {
            throw new Error('Survey schema is invalid or missing questions');
        }
        
        console.log(`✓ Loaded ${responses.length} survey responses`);
        console.log(`✓ Loaded schema with ${Object.keys(schema.questions).length} question definitions`);
        
        // Basic data validation
        if (responses.length === 0) {
            throw new Error('No survey responses found');
        }
        
        // Check if first response has expected structure
        const firstResponse = responses[0];
        if (!firstResponse.id || !firstResponse.professional_role) {
            throw new Error('Survey responses missing expected fields');
        }
        
        console.log('✓ Data validation passed');
    },
    
    // Show data summary
    showDataSummary() {
        const { responses, schema } = this.data;
        
        console.log('Survey data loaded successfully:', {
            responses: responses.length,
            schema_questions: Object.keys(schema.questions).length
        });
        
        // Initialize and populate dropdowns
        this.populateQuestionDropdown();
        this.updateFilterCount();
    },

    // Add a new dynamic filter
    addFilter() {
        const filterId = `filter_${this.filters.nextId++}`;
        const filterContainer = document.getElementById('filtersContainer');
        
        if (!filterContainer) return;
        
        // Create filter element
        const filterDiv = document.createElement('div');
        filterDiv.className = 'dynamic-filter';
        filterDiv.setAttribute('data-filter-id', filterId);
        
        // Create question selector
        const questionSelect = document.createElement('select');
        questionSelect.className = 'filter-question-select';
        questionSelect.innerHTML = '<option value="">Select question...</option>';
        
        // Populate with all questions that can be filtered
        this.populateFilterQuestionOptions(questionSelect);
        
        // Create value selector (initially empty)
        const valueSelect = document.createElement('select');
        valueSelect.className = 'filter-value-select';
        valueSelect.innerHTML = '<option value="">Select value...</option>';
        valueSelect.disabled = true;
        
        // Create remove button
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-filter-btn';
        removeBtn.textContent = '✕';
        removeBtn.title = 'Remove filter';
        
        // Add event listeners
        questionSelect.addEventListener('change', (e) => {
            this.onFilterQuestionChange(filterId, e.target.value, valueSelect);
        });
        
        valueSelect.addEventListener('change', () => {
            this.applyFilters();
        });
        
        removeBtn.addEventListener('click', () => {
            this.removeFilter(filterId);
        });
        
        // Assemble filter
        filterDiv.appendChild(document.createTextNode('Filter by: '));
        filterDiv.appendChild(questionSelect);
        filterDiv.appendChild(document.createTextNode(' = '));
        filterDiv.appendChild(valueSelect);
        filterDiv.appendChild(removeBtn);
        
        filterContainer.appendChild(filterDiv);
        this.updateClearAllButton();
        this.highlightLogicSelector();
    },

    // Populate filter question dropdown with all filterable questions
    populateFilterQuestionOptions(selectElement) {
        const { schema } = this.data;
        if (!schema) return;
        
        Object.entries(schema.questions).forEach(([key, question]) => {
            // Skip identifier questions and include single_choice and some multiple_choice
            if (key === 'id' || question.type === 'open_text') return;
            
            const option = document.createElement('option');
            option.value = key;
            option.textContent = this.truncateText(question.question, 60);
            selectElement.appendChild(option);
        });
    },

    // Handle question selection change in a filter
    onFilterQuestionChange(filterId, questionKey, valueSelect) {
        if (!questionKey) {
            valueSelect.innerHTML = '<option value="">Select value...</option>';
            valueSelect.disabled = true;
            this.applyFilters();
            return;
        }
        
        const { responses, schema } = this.data;
        const question = schema.questions[questionKey];
        
        if (!question) return;
        
        // Get unique values for this question
        const values = new Set();
        
        responses.forEach(response => {
            const value = response[questionKey];
            if (value !== null && value !== undefined && value !== '') {
                if (Array.isArray(value)) {
                    // For multiple choice questions, add each individual choice
                    value.forEach(v => values.add(v));
                } else {
                    values.add(value);
                }
            }
        });
        
        // Sort values appropriately
        let sortedValues = [...values];
        if (questionKey === 'years_experience') {
            const order = ['0-2 years', '3-5 years', '6-10 years', '10+ years'];
            sortedValues = order.filter(exp => values.has(exp));
        } else if (questionKey === 'level_generation_frequency') {
            const order = [
                'Always (essential part of workflow)',
                'Often (most projects)',
                'Sometimes (about half of projects)',
                'Rarely (a few projects)',
                'Never'
            ];
            sortedValues = order.filter(freq => values.has(freq));
        } else {
            sortedValues.sort();
        }
        
        // Populate value dropdown
        valueSelect.innerHTML = '<option value="">Select value...</option>';
        sortedValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = this.truncateText(value, 50);
            valueSelect.appendChild(option);
        });
        
        valueSelect.disabled = false;
        this.applyFilters();
    },

    // Remove a filter
    removeFilter(filterId) {
        const filterElement = document.querySelector(`[data-filter-id="${filterId}"]`);
        if (filterElement) {
            filterElement.remove();
            this.applyFilters();
            this.updateClearAllButton();
            this.highlightLogicSelector();
        }
    },

    // Apply all active filters
    applyFilters() {
        const { responses } = this.data;
        if (!responses) return;
        
        // Get all active filters
        const activeFilters = [];
        const filterElements = document.querySelectorAll('.dynamic-filter');
        
        filterElements.forEach(filterDiv => {
            const questionSelect = filterDiv.querySelector('.filter-question-select');
            const valueSelect = filterDiv.querySelector('.filter-value-select');
            
            if (questionSelect.value && valueSelect.value) {
                activeFilters.push({
                    question: questionSelect.value,
                    value: valueSelect.value
                });
            }
        });
        
        // Get filter logic (AND/OR)
        const filterLogic = document.getElementById('filterLogic')?.value || 'AND';
        
        // Store active filters
        this.filters.active = activeFilters;
        
        // Filter the data
        if (activeFilters.length === 0) {
            this.filters.filteredData = null;
        } else {
            this.filters.filteredData = responses.filter(response => {
                if (filterLogic === 'OR') {
                    // OR logic: response passes if ANY filter matches
                    return activeFilters.some(filter => {
                        const responseValue = response[filter.question];
                        
                        if (Array.isArray(responseValue)) {
                            return responseValue.includes(filter.value);
                        } else {
                            return responseValue === filter.value;
                        }
                    });
                } else {
                    // AND logic: response passes if ALL filters match (default)
                    return activeFilters.every(filter => {
                        const responseValue = response[filter.question];
                        
                        if (Array.isArray(responseValue)) {
                            return responseValue.includes(filter.value);
                        } else {
                            return responseValue === filter.value;
                        }
                    });
                }
            });
        }
        
        // Update UI
        this.updateFilterCount();
        this.updateClearAllButton();
        this.highlightLogicSelector();
        this.highlightLogicSelector();
        
        // Re-analyze current question with filtered data
        const currentQuestion = document.getElementById('questionSelect')?.value;
        if (currentQuestion) {
            this.analyzeQuestion(currentQuestion);
        }
    },

    // Clear all filters
    clearAllFilters() {
        const filterContainer = document.getElementById('filtersContainer');
        if (filterContainer) {
            filterContainer.innerHTML = '';
        }
        
        this.filters.active = [];
        this.filters.filteredData = null;
        
        this.updateFilterCount();
        this.updateClearAllButton();
        
        // Re-analyze current question with full data
        const currentQuestion = document.getElementById('questionSelect')?.value;
        if (currentQuestion) {
            this.analyzeQuestion(currentQuestion);
        }
    },

    // Update clear all button visibility
    updateClearAllButton() {
        const clearBtn = document.getElementById('clearAllFilters');
        const hasFilters = document.querySelectorAll('.dynamic-filter').length > 0;
        
        if (clearBtn) {
            if (hasFilters) {
                clearBtn.classList.remove('hidden');
            } else {
                clearBtn.classList.add('hidden');
            }
        }
    },

    // Highlight logic selector when filters are active
    highlightLogicSelector() {
        const logicDropdown = document.getElementById('filterLogic');
        const hasMultipleFilters = document.querySelectorAll('.dynamic-filter').length > 1;
        
        if (logicDropdown) {
            if (hasMultipleFilters) {
                logicDropdown.classList.add('logic-highlight');
            } else {
                logicDropdown.classList.remove('logic-highlight');
            }
        }
    },

    // Utility function to truncate text
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    },

    // Update filter count display
    updateFilterCount() {
        const filterCountElement = document.getElementById('filterCount');
        if (!filterCountElement) return;

        const totalResponses = this.data.responses?.length || 0;
        const filteredCount = this.filters.filteredData?.length || totalResponses;
        const filterLogic = document.getElementById('filterLogic')?.value || 'AND';
        
        if (this.filters.active.length > 0) {
            const logicText = this.filters.active.length > 1 ? ` (${filterLogic} logic)` : '';
            filterCountElement.textContent = `Showing ${filteredCount} of ${totalResponses} responses${logicText}`;
        } else {
            filterCountElement.textContent = `Showing all ${totalResponses} responses`;
        }
    },

    // Get current dataset (filtered or full)
    getCurrentData() {
        return this.filters.filteredData || this.data.responses || [];
    },
    
    // Populate the question dropdown with single choice questions
    populateQuestionDropdown() {
        const questionSelect = document.getElementById('questionSelect');
        const { schema } = this.data;
        
        if (!questionSelect || !schema) return;
        
        // Clear existing options except the first one
        questionSelect.innerHTML = '<option value="">Choose a question...</option>';
        
        // Add single choice questions to dropdown
        Object.entries(schema.questions).forEach(([key, question]) => {
            if (question.type === 'single_choice') {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = question.question;
                questionSelect.appendChild(option);
            }
        });
        
        console.log('Question dropdown populated with single choice questions');
    },

    // Analyze the selected question
    analyzeQuestion(questionKey) {
        if (!questionKey || !this.data.loaded) {
            this.clearChart();
            this.clearOtherAnswers();
            return;
        }
        
        const { schema } = this.data;
        const question = schema.questions[questionKey];
        
        if (!question || question.type !== 'single_choice') {
            console.log('Question not found or not single choice');
            this.clearChart();
            this.clearOtherAnswers();
            return;
        }
        
        console.log(`Analyzing question: ${question.question}`);
        
        // Use filtered data if available, otherwise use all data
        const currentData = this.getCurrentData();
        
        // Get response data for this question
        const responseData = currentData.map(r => r[questionKey]).filter(Boolean);
        
        // Count responses and separate "other" answers
        const counts = {};
        const otherAnswers = [];
        
        responseData.forEach(response => {
            // Check if this is an "other" type answer (not in predefined options)
            const isOtherAnswer = question.options && !question.options.includes(response);
            
            if (isOtherAnswer) {
                otherAnswers.push(response);
            } else {
                counts[response] = (counts[response] || 0) + 1;
            }
        });
        
        // If there are "other" answers, group them
        if (otherAnswers.length > 0) {
            counts['Other'] = otherAnswers.length;
        }
        
        // Create pie chart and show other answers
        this.createPieChart(question.question, counts, currentData.length);
        this.showOtherAnswers(otherAnswers);
    },

    // Create a pie chart
    createPieChart(title, data, totalResponses) {
        const ctx = document.getElementById('analysisChart');
        if (!ctx) return;
        
        // Destroy existing chart if it exists
        if (this.charts.current) {
            this.charts.current.destroy();
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        // Generate colors for each slice
        const colors = this.generateColors(labels.length);
        
        // Add filter info to title if filters are active
        const filterInfo = this.filters.active.length > 0 
            ? ` (${totalResponses} responses)` 
            : '';
        
        this.charts.current = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.background,
                    borderWidth: 0  // Remove border/outline
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: title + filterInfo,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((context.parsed / total) * 100).toFixed(1);
                                return `${context.label}: ${context.parsed} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
        
        console.log(`Created pie chart for: ${title}`);
    },

    // Generate colors for chart
    generateColors(count) {
        const colors = [
            '#667eea', '#764ba2', '#f093fb', '#f5576c',
            '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
            '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3',
            '#ff9a9e', '#fecfef', '#ffeaa7', '#fab1a0'
        ];
        
        const background = [];
        
        for (let i = 0; i < count; i++) {
            const color = colors[i % colors.length];
            background.push(color + '80'); // Add transparency
        }
        
        return { background };
    },

    // Show other answers below the chart
    showOtherAnswers(otherAnswers) {
        const otherContainer = document.getElementById('otherAnswers');
        if (!otherContainer) return;
        
        if (otherAnswers.length === 0) {
            otherContainer.classList.add('hidden');
            return;
        }
        
        otherContainer.innerHTML = `
            <h3>Other Responses (${otherAnswers.length}):</h3>
            <ul>
                ${otherAnswers.map(answer => `<li>"${answer}"</li>`).join('')}
            </ul>
        `;
        
        otherContainer.classList.remove('hidden');
    },

    // Clear other answers display
    clearOtherAnswers() {
        const otherContainer = document.getElementById('otherAnswers');
        if (otherContainer) {
            otherContainer.classList.add('hidden');
            otherContainer.innerHTML = '';
        }
    },

    // Clear the chart
    clearChart() {
        if (this.charts.current) {
            this.charts.current.destroy();
            this.charts.current = null;
        }
    },
    
    // Get unique values for a field
    getUniqueValues(field) {
        if (!this.data.loaded) return [];
        return [...new Set(this.data.responses.map(r => r[field]).filter(Boolean))];
    },
    
    // Filter responses by criteria (legacy method)
    filterResponses(criteria) {
        if (!this.data.loaded) return [];
        
        return this.data.responses.filter(response => {
            return Object.entries(criteria).every(([field, value]) => {
                if (Array.isArray(value)) {
                    return value.includes(response[field]);
                }
                return response[field] === value;
            });
        });
    },
    
    // Placeholder for chart creation (legacy method)
    createChart(type, containerId, data) {
        console.log(`Chart creation placeholder: ${type} in ${containerId}`);
        // Legacy placeholder - actual chart creation now handled by specific methods
    }
};

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    SurveyApp.init();
});