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
        active: {},
        filteredData: null
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

        // Add filter listeners
        const filterIds = ['filterRole', 'filterExperience', 'filterEngine', 'filterFrequency'];
        filterIds.forEach(filterId => {
            const filterElement = document.getElementById(filterId);
            if (filterElement) {
                filterElement.addEventListener('change', () => this.applyFilters());
            }
        });

        // Add clear filters button listener
        const clearFiltersBtn = document.getElementById('clearFilters');
        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
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
        
        // Initialize filters and populate dropdowns
        this.populateFilterDropdowns();
        this.populateQuestionDropdown();
        this.updateFilterCount();
    },

    // Populate filter dropdowns
    populateFilterDropdowns() {
        const { responses } = this.data;
        if (!responses) return;

        // Professional Role filter
        const roles = [...new Set(responses.map(r => r.professional_role).filter(Boolean))].sort();
        this.populateDropdown('filterRole', roles);

        // Experience filter
        const experienceLevels = [...new Set(responses.map(r => r.years_experience).filter(Boolean))];
        // Sort experience levels in logical order
        const orderedExperience = ['0-2 years', '3-5 years', '6-10 years', '10+ years'];
        const sortedExperience = orderedExperience.filter(exp => experienceLevels.includes(exp));
        this.populateDropdown('filterExperience', sortedExperience);

        // Game Engine filter (handle arrays)
        const engines = new Set();
        responses.forEach(r => {
            if (r.game_engines && Array.isArray(r.game_engines)) {
                r.game_engines.forEach(engine => engines.add(engine));
            } else if (r.game_engines && typeof r.game_engines === 'string') {
                engines.add(r.game_engines);
            }
        });
        this.populateDropdown('filterEngine', [...engines].sort());

        // PCG Usage Frequency filter
        const frequencies = [...new Set(responses.map(r => r.level_generation_frequency).filter(Boolean))];
        // Sort frequencies in logical order
        const orderedFrequencies = [
            'Always (essential part of workflow)',
            'Often (most projects)',
            'Sometimes (about half of projects)',
            'Rarely (a few projects)',
            'Never'
        ];
        const sortedFrequencies = orderedFrequencies.filter(freq => frequencies.includes(freq));
        this.populateDropdown('filterFrequency', sortedFrequencies);
    },

    // Helper to populate a dropdown
    populateDropdown(elementId, options) {
        const dropdown = document.getElementById(elementId);
        if (!dropdown) return;

        // Keep the "All" option and add new options
        const allOption = dropdown.querySelector('option[value=""]');
        dropdown.innerHTML = '';
        dropdown.appendChild(allOption);

        options.forEach(option => {
            const optionElement = document.createElement('option');
            optionElement.value = option;
            optionElement.textContent = option;
            dropdown.appendChild(optionElement);
        });
    },

    // Apply filters to the data
    applyFilters() {
        const { responses } = this.data;
        if (!responses) return;

        // Get filter values
        const filters = {
            role: document.getElementById('filterRole')?.value || '',
            experience: document.getElementById('filterExperience')?.value || '',
            engine: document.getElementById('filterEngine')?.value || '',
            frequency: document.getElementById('filterFrequency')?.value || ''
        };

        // Store active filters
        this.filters.active = Object.fromEntries(
            Object.entries(filters).filter(([key, value]) => value !== '')
        );

        // Filter the data
        this.filters.filteredData = responses.filter(response => {
            // Professional role filter
            if (filters.role && response.professional_role !== filters.role) {
                return false;
            }

            // Experience filter
            if (filters.experience && response.years_experience !== filters.experience) {
                return false;
            }

            // Game engine filter (handle arrays)
            if (filters.engine) {
                if (Array.isArray(response.game_engines)) {
                    if (!response.game_engines.includes(filters.engine)) {
                        return false;
                    }
                } else if (response.game_engines !== filters.engine) {
                    return false;
                }
            }

            // PCG frequency filter
            if (filters.frequency && response.level_generation_frequency !== filters.frequency) {
                return false;
            }

            return true;
        });

        // Update UI
        this.updateFilterCount();
        this.showClearFiltersButton();
        
        // Re-analyze current question with filtered data
        const currentQuestion = document.getElementById('questionSelect')?.value;
        if (currentQuestion) {
            this.analyzeQuestion(currentQuestion);
        }
    },

    // Clear all filters
    clearFilters() {
        // Reset all filter dropdowns
        document.getElementById('filterRole').value = '';
        document.getElementById('filterExperience').value = '';
        document.getElementById('filterEngine').value = '';
        document.getElementById('filterFrequency').value = '';

        // Clear filter state
        this.filters.active = {};
        this.filters.filteredData = null;

        // Update UI
        this.updateFilterCount();
        this.hideClearFiltersButton();

        // Re-analyze current question with full data
        const currentQuestion = document.getElementById('questionSelect')?.value;
        if (currentQuestion) {
            this.analyzeQuestion(currentQuestion);
        }
    },

    // Update filter count display
    updateFilterCount() {
        const filterCountElement = document.getElementById('filterCount');
        if (!filterCountElement) return;

        const totalResponses = this.data.responses?.length || 0;
        const filteredCount = this.filters.filteredData?.length || totalResponses;
        
        if (Object.keys(this.filters.active).length > 0) {
            filterCountElement.textContent = `Showing ${filteredCount} of ${totalResponses} responses`;
        } else {
            filterCountElement.textContent = `Showing all ${totalResponses} responses`;
        }
    },

    // Show/hide clear filters button
    showClearFiltersButton() {
        const clearBtn = document.getElementById('clearFilters');
        if (clearBtn && Object.keys(this.filters.active).length > 0) {
            clearBtn.classList.remove('hidden');
        }
    },

    hideClearFiltersButton() {
        const clearBtn = document.getElementById('clearFilters');
        if (clearBtn) {
            clearBtn.classList.add('hidden');
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
        const filterInfo = Object.keys(this.filters.active).length > 0 
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