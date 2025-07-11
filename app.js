// Procedural Level Generation Survey Analysis Tool
// Version 5.0 - Demographics Filtering Enhancement

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
        demographics: {
            professional_role: new Set(),
            years_experience: new Set()
        },
        advanced: [],
        filteredData: null,
        nextId: 1
    },
    
    // Initialize the application
    init() {
        console.log('Initializing Survey Analysis Tool...');
        this.setupEventListeners();
        this.loadData();
    },
    
    // Set up event listeners
    setupEventListeners() {
        const questionSelect = document.getElementById('questionSelect');
        if (questionSelect) {
            questionSelect.addEventListener('change', (e) => this.analyzeQuestion(e.target.value));
        }

        const addFilterBtn = document.getElementById('addFilterBtn');
        if (addFilterBtn) {
            addFilterBtn.addEventListener('click', () => this.addAdvancedFilter());
        }

        const clearAllFiltersBtn = document.getElementById('clearAllFilters');
        if (clearAllFiltersBtn) {
            clearAllFiltersBtn.addEventListener('click', () => this.clearAllAdvancedFilters());
        }

        const filterLogic = document.getElementById('filterLogic');
        if (filterLogic) {
            filterLogic.addEventListener('change', () => this.applyAllFilters());
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
    },
    
    // Show data summary and initialize demographics
    showDataSummary() {
        const { responses, schema } = this.data;
        
        console.log('Survey data loaded successfully:', {
            responses: responses.length,
            schema_questions: Object.keys(schema.questions).length
        });
        
        this.populateQuestionDropdown();
        this.initializeDemographics();
        this.updateDemographicsSummary();
    },

    // Initialize demographics filters
    initializeDemographics() {
        this.populateDemographicOptions('professional_role');
        this.populateDemographicOptions('years_experience');
    },

    // Populate demographic options with checkboxes
    populateDemographicOptions(demographicKey) {
        const container = document.getElementById(`${demographicKey}_options`);
        if (!container) return;

        const { responses, schema } = this.data;
        const question = schema.questions[demographicKey];
        
        if (!question || !question.options) return;

        // Count occurrences of each option
        const counts = {};
        let otherCount = 0;
        
        question.options.forEach(option => {
            counts[option] = responses.filter(r => r[demographicKey] === option).length;
        });

        // Count non-schema responses as "Other"
        responses.forEach(response => {
            const value = response[demographicKey];
            if (value && value !== null && value !== undefined && value.trim() !== '' && 
                !question.options.includes(value)) {
                otherCount++;
            }
        });

        // Add "Other" if there are non-schema responses
        const allOptions = [...question.options];
        if (otherCount > 0) {
            allOptions.push('Other');
            counts['Other'] = otherCount;
        }

        // Sort options by count (descending)
        const sortedOptions = allOptions.sort((a, b) => counts[b] - counts[a]);

        container.innerHTML = '';
        sortedOptions.forEach(option => {
            const optionDiv = document.createElement('div');
            optionDiv.className = 'demographic-option';
            
            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.id = `${demographicKey}_${option.replace(/\s+/g, '_').replace(/[^\w]/g, '_')}`;
            checkbox.checked = true; // Start with all selected
            checkbox.addEventListener('change', () => this.onDemographicChange(demographicKey, option, checkbox.checked));
            
            const label = document.createElement('label');
            label.htmlFor = checkbox.id;
            label.textContent = option;
            
            const count = document.createElement('span');
            count.className = 'option-count';
            count.textContent = counts[option];
            
            optionDiv.appendChild(checkbox);
            optionDiv.appendChild(label);
            optionDiv.appendChild(count);
            
            container.appendChild(optionDiv);
        });

        // Initialize with all options selected (including "Other" if it exists)
        this.filters.demographics[demographicKey] = new Set(allOptions);
    },

    // Handle demographic option change
    onDemographicChange(demographicKey, option, isChecked) {
        if (isChecked) {
            this.filters.demographics[demographicKey].add(option);
        } else {
            this.filters.demographics[demographicKey].delete(option);
        }
        
        this.applyAllFilters();
        this.updateDemographicsSummary();
    },

    // Toggle all demographics for a specific field
    toggleAllDemographic(demographicKey) {
        const container = document.getElementById(`${demographicKey}_options`);
        if (!container) return;

        const checkboxes = container.querySelectorAll('input[type="checkbox"]');
        const allChecked = Array.from(checkboxes).every(cb => cb.checked);
        
        // If all are checked, uncheck all; otherwise, check all
        const newState = !allChecked;
        
        checkboxes.forEach(checkbox => {
            checkbox.checked = newState;
            const option = checkbox.labels[0].textContent;
            if (newState) {
                this.filters.demographics[demographicKey].add(option);
            } else {
                this.filters.demographics[demographicKey].delete(option);
            }
        });
        
        this.applyAllFilters();
        this.updateDemographicsSummary();
    },

    // Clear all demographic filters
    clearDemographics() {
        Object.keys(this.filters.demographics).forEach(demographicKey => {
            const { responses, schema } = this.data;
            const question = schema.questions[demographicKey];
            
            if (question && question.options) {
                const allOptions = [...question.options];
                
                // Check if there are non-schema responses to add "Other"
                const hasOtherResponses = responses.some(response => {
                    const value = response[demographicKey];
                    return value && value !== null && value !== undefined && value.trim() !== '' && 
                           !question.options.includes(value);
                });
                
                if (hasOtherResponses) {
                    allOptions.push('Other');
                }
                
                // Set all to checked and add to filter set
                this.filters.demographics[demographicKey] = new Set(allOptions);
                
                // Update UI checkboxes
                const container = document.getElementById(`${demographicKey}_options`);
                if (container) {
                    const checkboxes = container.querySelectorAll('input[type="checkbox"]');
                    checkboxes.forEach(cb => cb.checked = true);
                }
            }
        });
        
        this.applyAllFilters();
        this.updateDemographicsSummary();
    },

    // Update demographics summary
    updateDemographicsSummary() {
        const summaryElement = document.getElementById('demographicsSummary');
        const progressBar = document.getElementById('demographicsProgress');
        const progressLabel = document.getElementById('demographicsProgressLabel');
        
        if (!summaryElement || !progressBar || !progressLabel) return;

        const { responses } = this.data;
        const demographicData = this.getCurrentData();
        
        const totalResponses = responses.length;
        const filteredCount = demographicData.length;
        const percentage = ((filteredCount / totalResponses) * 100).toFixed(1);

        const roleCount = this.filters.demographics.professional_role.size;
        const expCount = this.filters.demographics.years_experience.size;
        
        const totalRoles = this.data.schema?.questions?.professional_role?.options?.length || 0;
        const totalExperiences = this.data.schema?.questions?.years_experience?.options?.length || 0;
        
        // Add 1 to totals if "Other" exists
        const hasOtherRole = [...this.filters.demographics.professional_role].includes('Other');
        const finalTotalRoles = totalRoles + (hasOtherRole ? 1 : 0);
        
        // Update summary text
        summaryElement.textContent = 
            `${roleCount}/${finalTotalRoles} roles, ${expCount}/${totalExperiences} experience levels selected`;
        
        // Update progress bar
        progressBar.style.width = `${percentage}%`;
        
        // Update progress label
        progressLabel.textContent = `${filteredCount} / ${totalResponses} responses (${percentage}%)`;
    },

    // Apply all filters (demographics + advanced)
    applyAllFilters() {
        const { responses } = this.data;
        if (!responses) return;

        // First apply demographic filters
        let filteredData = responses.filter(response => {
            const { schema } = this.data;
            
            // Check professional role
            const roleValue = response.professional_role;
            const roleQuestion = schema.questions.professional_role;
            let roleMatch = false;
            
            if (roleValue && roleQuestion) {
                if (roleQuestion.options.includes(roleValue)) {
                    // Standard option
                    roleMatch = this.filters.demographics.professional_role.has(roleValue);
                } else {
                    // Non-standard option - check if "Other" is selected
                    roleMatch = this.filters.demographics.professional_role.has('Other');
                }
            }
            
            // Check years experience (standard field)
            const expValue = response.years_experience;
            const expMatch = this.filters.demographics.years_experience.has(expValue);
            
            return roleMatch && expMatch;
        });

        // Then apply advanced filters if any
        const activeAdvancedFilters = this.getActiveAdvancedFilters();
        
        if (activeAdvancedFilters.length > 0) {
            const filterLogic = document.getElementById('filterLogic')?.value || 'AND';
            
            filteredData = filteredData.filter(response => {
                if (filterLogic === 'OR') {
                    return activeAdvancedFilters.some(filter => {
                        const responseValue = response[filter.question];
                        if (Array.isArray(responseValue)) {
                            return responseValue.includes(filter.value);
                        } else {
                            return responseValue === filter.value;
                        }
                    });
                } else {
                    return activeAdvancedFilters.every(filter => {
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

        this.filters.filteredData = filteredData;
        this.updateDemographicsSummary();
        
        // Re-analyze current question with filtered data
        const currentQuestion = document.getElementById('questionSelect')?.value;
        if (currentQuestion) {
            this.analyzeQuestion(currentQuestion);
        }
    },

    // Get active advanced filters
    getActiveAdvancedFilters() {
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
        
        return activeFilters;
    },

    // Get current dataset (filtered)
    getCurrentData() {
        return this.filters.filteredData || this.data.responses || [];
    },

    // Populate the question dropdown with analyzable questions
    populateQuestionDropdown() {
        const questionSelect = document.getElementById('questionSelect');
        const { schema } = this.data;
        
        if (!questionSelect || !schema) return;
        
        questionSelect.innerHTML = '<option value="">Choose a question...</option>';
        
        Object.entries(schema.questions).forEach(([key, question]) => {
            if (key === 'id') return;
            
            if (['single_choice', 'multiple_choice', 'matrix', 'open_text'].includes(question.type)) {
                const option = document.createElement('option');
                option.value = key;
                option.textContent = `${this.getQuestionTypeLabel(question.type)} - ${question.question}`;
                questionSelect.appendChild(option);
            }
        });
        
        console.log('Question dropdown populated with analyzable questions');
    },

    // Get a user-friendly label for question types
    getQuestionTypeLabel(type) {
        const labels = {
            'single_choice': '📊 Single Choice',
            'multiple_choice': '📈 Multiple Choice', 
            'matrix': '📋 Matrix',
            'open_text': '📝 Open Text'
        };
        return labels[type] || type;
    },

    // Add a new advanced filter
    addAdvancedFilter() {
        const filterId = `filter_${this.filters.nextId++}`;
        const filterContainer = document.getElementById('filtersContainer');
        
        if (!filterContainer) return;
        
        const filterDiv = document.createElement('div');
        filterDiv.className = 'dynamic-filter';
        filterDiv.setAttribute('data-filter-id', filterId);
        
        const questionSelect = document.createElement('select');
        questionSelect.className = 'filter-question-select';
        questionSelect.innerHTML = '<option value="">Select question...</option>';
        
        this.populateFilterQuestionOptions(questionSelect);
        
        const valueSelect = document.createElement('select');
        valueSelect.className = 'filter-value-select';
        valueSelect.innerHTML = '<option value="">Select value...</option>';
        valueSelect.disabled = true;
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'remove-filter-btn';
        removeBtn.textContent = '✕';
        removeBtn.title = 'Remove filter';
        
        questionSelect.addEventListener('change', (e) => {
            this.onAdvancedFilterQuestionChange(filterId, e.target.value, valueSelect);
        });
        
        valueSelect.addEventListener('change', () => {
            this.applyAllFilters();
        });
        
        removeBtn.addEventListener('click', () => {
            this.removeAdvancedFilter(filterId);
        });
        
        filterDiv.appendChild(document.createTextNode('Filter by: '));
        filterDiv.appendChild(questionSelect);
        filterDiv.appendChild(document.createTextNode(' = '));
        filterDiv.appendChild(valueSelect);
        filterDiv.appendChild(removeBtn);
        
        filterContainer.appendChild(filterDiv);
        this.updateClearAllAdvancedButton();
    },

    // Populate filter question dropdown with all filterable questions (excluding demographics)
    populateFilterQuestionOptions(selectElement) {
        const { schema } = this.data;
        if (!schema) return;
        
        Object.entries(schema.questions).forEach(([key, question]) => {
            // Skip identifier questions, open text, and demographics
            if (key === 'id' || question.type === 'open_text' || 
                key === 'professional_role' || key === 'years_experience') return;
            
            const option = document.createElement('option');
            option.value = key;
            option.textContent = question.question; // Show full question text
            selectElement.appendChild(option);
        });
    },

    // Handle advanced filter question selection change
    onAdvancedFilterQuestionChange(filterId, questionKey, valueSelect) {
        if (!questionKey) {
            valueSelect.innerHTML = '<option value="">Select value...</option>';
            valueSelect.disabled = true;
            this.applyAllFilters();
            return;
        }
        
        const { schema } = this.data;
        const question = schema.questions[questionKey];
        
        if (!question) return;
        
        // Get unique values for this question from current filtered data
        const currentData = this.getCurrentData();
        const values = new Set();
        
        currentData.forEach(response => {
            const value = response[questionKey];
            if (value !== null && value !== undefined && value !== '') {
                if (Array.isArray(value)) {
                    value.forEach(v => values.add(v));
                } else {
                    values.add(value);
                }
            }
        });
        
        const sortedValues = [...values].sort();
        
        valueSelect.innerHTML = '<option value="">Select value...</option>';
        sortedValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = this.truncateText(value, 50);
            valueSelect.appendChild(option);
        });
        
        valueSelect.disabled = false;
        this.applyAllFilters();
    },

    // Remove an advanced filter
    removeAdvancedFilter(filterId) {
        const filterElement = document.querySelector(`[data-filter-id="${filterId}"]`);
        if (filterElement) {
            filterElement.remove();
            this.applyAllFilters();
            this.updateClearAllAdvancedButton();
        }
    },

    // Clear all advanced filters
    clearAllAdvancedFilters() {
        const filterContainer = document.getElementById('filtersContainer');
        if (filterContainer) {
            filterContainer.innerHTML = '';
        }
        
        this.applyAllFilters();
        this.updateClearAllAdvancedButton();
    },

    // Update clear all advanced filters button visibility
    updateClearAllAdvancedButton() {
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

    // Utility function to truncate text
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    },

    // Analyze the selected question
    analyzeQuestion(questionKey) {
        this.clearChart();
        this.clearOtherAnswers();

        if (!questionKey || !this.data.loaded) {
            return;
        }
        
        const { schema } = this.data;
        const question = schema.questions[questionKey];
        
        if (!question) {
            console.log('Question not found');
            return;
        }
        
        console.log(`Analyzing question: ${question.question} (${question.type})`);
        
        switch (question.type) {
            case 'single_choice':
                this.analyzeSingleChoice(questionKey, question);
                break;
            case 'multiple_choice':
                this.analyzeMultipleChoice(questionKey, question);
                break;
            case 'matrix':
                this.analyzeMatrix(questionKey, question);
                break;
            case 'open_text':
                this.analyzeOpenText(questionKey, question);
                break;
            default:
                console.log(`Question type ${question.type} not supported for visualization`);
                this.clearChart();
                this.clearOtherAnswers();
        }
    },

    // Analyze single choice questions (pie chart)
    analyzeSingleChoice(questionKey, question) {
        const currentData = this.getCurrentData();
        const responseData = currentData.map(r => r[questionKey]).filter(Boolean);
        
        const counts = {};
        const otherAnswers = [];
        
        responseData.forEach(response => {
            const isOtherAnswer = question.options && !question.options.includes(response);
            
            if (isOtherAnswer) {
                otherAnswers.push(response);
            } else {
                counts[response] = (counts[response] || 0) + 1;
            }
        });
        
        if (otherAnswers.length > 0) {
            counts['Other'] = otherAnswers.length;
        }
        
        this.createPieChart(question.question, counts, currentData.length);
        this.showOtherAnswers(otherAnswers);
    },

    // Create a pie chart
    createPieChart(title, data, totalResponses) {
        const ctx = document.getElementById('analysisChart');
        if (!ctx) return;
        
        if (this.charts.current) {
            this.charts.current.destroy();
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        const colors = this.generateColors(labels.length);
        
        const filterInfo = this.filters.filteredData 
            ? ` (${totalResponses} responses)` 
            : '';
        
        this.charts.current = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.background,
                    borderWidth: 0
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
            background.push(color + '80');
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
        
        const chartContainer = document.getElementById('chartContainer');
        if (chartContainer) {
            chartContainer.innerHTML = '<canvas id="analysisChart"></canvas>';
        }
    }
};

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    SurveyApp.init();
});