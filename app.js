// Procedural Level Generation Survey Analysis Tool
// Version 5.0 - Demographics Filtering Enhancement

console.log('Survey Analysis Tool Initialized');

// Convert HSV to RGB color
function hsvToRgb(h, s, v) {
    let r, g, b;
    const i = Math.floor(h * 6);
    const f = h * 6 - i;
    const p = v * (1 - s);
    const q = v * (1 - f * s);
    const t = v * (1 - (1 - f) * s);

    switch (i % 6) {
        case 0: r = v; g = t; b = p; break;
        case 1: r = q; g = v; b = p; break;
        case 2: r = p; g = v; b = t; break;
        case 3: r = p; g = q; b = v; break;
        case 4: r = t, g = p, b = v; break;
        case 5: r = v, g = p, b = q; break;
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
}

function rgbToHex(r, g, b) {
    return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;
}

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

        const scaleSelect = document.getElementById('scaleSelect');
        if (scaleSelect) {
            scaleSelect.addEventListener('change', () => this.redrawCurrentChart());
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
        const progressBar = document.getElementById('demographicsProgress');
        const progressLabel = document.getElementById('demographicsProgressLabel');
        
        if (!progressBar || !progressLabel) return;

        const { responses } = this.data;
        const demographicData = this.getCurrentData();
        
        const totalResponses = responses.length;
        const filteredCount = demographicData.length;
        const percentage = ((filteredCount / totalResponses) * 100).toFixed(1);
                
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
                        let match;
                        if (Array.isArray(responseValue)) {
                            match = responseValue.includes(filter.value);
                        } else {
                            match = responseValue === filter.value;
                        }
                        return filter.negate ? !match : match;
                    });
                } else {
                    return activeAdvancedFilters.every(filter => {
                        const responseValue = response[filter.question];
                        let match;
                        if (Array.isArray(responseValue)) {
                            match = responseValue.includes(filter.value);
                        } else {
                            match = responseValue === filter.value;
                        }
                        return filter.negate ? !match : match;
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
            const negateCheckbox = filterDiv.querySelector('.negate-checkbox');
            
            if (questionSelect.value && valueSelect.value) {
                activeFilters.push({
                    question: questionSelect.value,
                    value: valueSelect.value,
                    negate: negateCheckbox.checked
                });
            }
        });
        
        return activeFilters;
    },

    // Get current dataset (filtered)
    getCurrentData() {
        return this.filters.filteredData || this.data.responses || [];
    },

    // Get selected chart scale
    getChartScale() {
        const scaleSelect = document.getElementById('scaleSelect');
        return scaleSelect ? parseInt(scaleSelect.value) : 1;
    },

    // Redraw current chart with new scale
    redrawCurrentChart() {
        const currentQuestion = document.getElementById('questionSelect')?.value;
        if (currentQuestion) {
            this.analyzeQuestion(currentQuestion);
        }
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

        const negateContainer = document.createElement('div');
        negateContainer.className = 'negate-filter';
        const negateCheckbox = document.createElement('input');
        negateCheckbox.type = 'checkbox';
        negateCheckbox.id = `negate_${filterId}`;
        negateCheckbox.className = 'negate-checkbox';
        const negateLabel = document.createElement('label');
        negateLabel.htmlFor = negateCheckbox.id;
        negateLabel.textContent = 'Negate';
        negateContainer.appendChild(negateCheckbox);
        negateContainer.appendChild(negateLabel);
        
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

        negateCheckbox.addEventListener('change', () => {
            this.applyAllFilters();
        });
        
        removeBtn.addEventListener('click', () => {
            this.removeAdvancedFilter(filterId);
        });
        
        filterDiv.appendChild(document.createTextNode('Filter by: '));
        filterDiv.appendChild(questionSelect);
        filterDiv.appendChild(document.createTextNode(' = '));
        filterDiv.appendChild(valueSelect);
        filterDiv.appendChild(negateContainer);
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

    // Utility function to wrap text into multiple lines for legends
    // Returns an object with 'lines' array and 'lineCount' number
    wrapLegendText(label, value, percentage, maxLength = 35) {
        const words = label.split(' ');
        const lines = [];
        let currentLine = '';
        
        // Build lines by adding words until we exceed maxLength
        for (let word of words) {
            const testLine = currentLine + (currentLine ? ' ' : '') + word;
            
            if (testLine.length <= maxLength) {
                currentLine = testLine;
            } else {
                // Current line is full, start a new one
                if (currentLine) {
                    lines.push(currentLine);
                }
                currentLine = word;
            }
        }
        
        // Add the last line with percentage
        if (currentLine) {
            lines.push(currentLine + ` (${percentage}%)`);
        } else if (lines.length > 0) {
            // If we have lines but no current line, add percentage to the last line
            lines[lines.length - 1] += ` (${percentage}%)`;
        } else {
            // Fallback for edge cases
            lines.push(`${label} (${percentage}%)`);
        }
        
        return {
            lines: lines,
            lineCount: lines.length
        };
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

        // Initialize counts
        for (const option of question.options || []) {
            counts[option] = 0;
        }

        // Count responses        
        responseData.forEach(response => {
            const isOtherAnswer = question.options && !question.options.includes(response);
            
            if (isOtherAnswer) {
                otherAnswers.push(response);
            } else {
                counts[response] += 1;
            }
        });
        
        if (otherAnswers.length > 0) {
            counts['Other'] = otherAnswers.length;
        }
        
        this.createPieChart(question.question, counts, currentData.length);
        this.showOtherAnswers(otherAnswers);
    },

        // Analyze multiple choice questions (bar chart)
    analyzeMultipleChoice(questionKey, question) {
        const currentData = this.getCurrentData();
        const counts = {};
        const otherAnswers = [];

        // Initialize counts
        question.options.forEach(option => {
            counts[option] = 0;
        });
        
        // Count all individual selections across all responses
        currentData.forEach(response => {
            const value = response[questionKey];
            if (value) {
                if (Array.isArray(value)) {
                    value.forEach(item => {
                        const isOtherAnswer = question.options && !question.options.includes(item);
                        if (isOtherAnswer) {
                            otherAnswers.push(item);
                        } else {
                            counts[item] = (counts[item] || 0) + 1;
                        }
                    });
                } else if (typeof value === 'string') {
                    // Handle single string values (shouldn't happen for multiple choice, but just in case)
                    const isOtherAnswer = question.options && !question.options.includes(value);
                    if (isOtherAnswer) {
                        otherAnswers.push(value);
                    } else {
                        counts[value] = (counts[value] || 0) + 1;
                    }
                }
            }
        });
        
        if (otherAnswers.length > 0) {
            counts['Other'] = otherAnswers.length;
        }
        
        this.createBarChart(question.question, counts, currentData.length);
        this.showOtherAnswers(otherAnswers);
    },

    // Analyze matrix questions (stacked bar chart)
    analyzeMatrix(questionKey, question) {
        const currentData = this.getCurrentData();
        const matrixData = {};
        
        // Get matrix structure
        const items = question.items || [];
        const scale = question.scale || [];
        
        if (items.length === 0 || scale.length === 0) {
            console.log('Matrix question missing items or scale');
            this.clearChart();
            this.clearOtherAnswers();
            return;
        }
        
        // Initialize data structure
        items.forEach(item => {
            matrixData[item] = {};
            scale.forEach(scaleItem => {
                matrixData[item][scaleItem] = 0;
            });
        });
        
        // Count responses
        currentData.forEach(response => {
            const matrixResponses = response[questionKey];
            if (matrixResponses && typeof matrixResponses === 'object') {
                Object.entries(matrixResponses).forEach(([item, value]) => {
                    if (matrixData[item] && scale.includes(value)) {
                        matrixData[item][value]++;
                    }
                });
            }
        });
        
        this.createStackedBarChart(question.question, matrixData, scale, currentData.length);
        this.clearOtherAnswers(); // Matrix questions don't typically have "other" answers
    },

    // Analyze open text questions (text list)
    analyzeOpenText(questionKey, question) {
        const currentData = this.getCurrentData();
        const responses = [];
        
        // Collect all text responses
        currentData.forEach(response => {
            const value = response[questionKey];
            if (value && typeof value === 'string' && value.trim() !== '') {
                responses.push(value.trim());
            }
        });
        
        // Clear any existing chart and show text responses
        this.clearChart();
        this.showTextResponses(question.question, responses, currentData.length);
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
        
        // Calculate total for percentages
        const total = values.reduce((a, b) => a + b, 0);
        
        const maxLineWidth = 40;

        // Calculate dynamic padding based on maximum line count from wrapped text
        let maxLineCount = 1;
        
        labels.forEach(label => {
            const percentage = ((data[label] / total) * 100).toFixed(1);
            const wrappedText = this.wrapLegendText(label, '', percentage, maxLineWidth);
            maxLineCount = Math.max(maxLineCount, wrappedText.lineCount);
        });
        const basePadding = 15;
        const dynamicPadding = Math.max(basePadding, basePadding + (maxLineCount - 1) * 15);
        
        this.charts.current = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.background,
                    borderWidth: 0,
                    borderRadius: 0, // Rounded corners for spacing
                    spacing: 0 // Space between segments
                }]
            },
            options: {
                cutout: '60%', // Creates the hole in the middle
                responsive: true,
                maintainAspectRatio: false,
                devicePixelRatio: this.getChartScale(),
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        position: 'right',
                        align: 'end',
                        labels: {
                            padding: dynamicPadding, // Dynamic space between legend items
                            usePointStyle: true,
                            boxWidth: 12,
                            boxHeight: 12,
                            textAlign: 'left',
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        const percentage = ((value / total) * 100).toFixed(1);
                                        
                                        // Use the utility function to wrap text  
                                        const wrappedText = SurveyApp.wrapLegendText(label, '', percentage, maxLineWidth);
                                        
                                        return {
                                            text: wrappedText.lines,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].backgroundColor[i],
                                            lineWidth: 0,
                                            pointStyle: 'circle',
                                            hidden: isNaN(data.datasets[0].data[i]) || chart.getDatasetMeta(0).data[i].hidden,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
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
        
        this.showDownloadButton();
        console.log(`Created pie chart for: ${title}`);
    },

    // Create a bar chart for multiple choice questions
    createBarChart(title, data, totalResponses) {
        const ctx = document.getElementById('analysisChart');
        if (!ctx) return;
        
        // Destroy existing chart if it exists
        if (this.charts.current) {
            this.charts.current.destroy();
        }
        
        const labels = Object.keys(data);
        const values = Object.values(data);
        
        // Sort by frequency (descending)
        const sortedData = labels.map((label, index) => ({
            label,
            value: values[index]
        })).sort((a, b) => b.value - a.value);
        
        const sortedLabels = sortedData.map(item => item.label);
        const sortedValues = sortedData.map(item => item.value);
        
        // Calculate dynamic padding based on maximum line count from wrapped text
        let maxLineCount = 1;
        sortedLabels.forEach(label => {
            const value = data[label];
            const percentage = ((value / totalResponses) * 100).toFixed(1);
            const wrappedText = this.wrapLegendText(label, value, percentage, 35);
            maxLineCount = Math.max(maxLineCount, wrappedText.lineCount);
        });
        const basePadding = 12;
        const dynamicPadding = Math.max(basePadding, basePadding + (maxLineCount - 1) * 15);
        
        // Generate colors
        const colors = this.generateColors(sortedLabels.length);

        this.charts.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: sortedLabels,
                datasets: [{
                    label: 'Responses',
                    data: sortedValues,
                    backgroundColor: colors.background,
                    borderWidth: 0,
                    borderRadius: 0, // Rounded corners for spacing
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                devicePixelRatio: this.getChartScale(),
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        position: 'right',
                        align: 'end',
                        maxColumns: 0,
                        maxWidth: 260,
                        labels: {
                            padding: dynamicPadding, // Dynamic space between legend items
                            usePointStyle: true,
                            boxWidth: 190,
                            boxHeight: 12,
                            textAlign: 'left',
                            generateLabels: function(chart) {
                                const data = chart.data;
                                if (data.labels.length && data.datasets.length) {
                                    return data.labels.map((label, i) => {
                                        const value = data.datasets[0].data[i];
                                        const percentage = ((value / totalResponses) * 100).toFixed(1);
                                        
                                        // Use the utility function to wrap text with longer max length for bar charts
                                        const wrappedText = SurveyApp.wrapLegendText(label, value, percentage, 35);
                                        
                                        return {
                                            text: wrappedText.lines,
                                            fillStyle: data.datasets[0].backgroundColor[i],
                                            strokeStyle: data.datasets[0].backgroundColor[i],                                            
                                            lineWidth: 0,
                                            pointStyle: 'circle',
                                            hidden: false,
                                            index: i
                                        };
                                    });
                                }
                                return [];
                            }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const percentage = ((context.parsed.y / totalResponses) * 100).toFixed(1);
                                return `${context.parsed.y} responses (${percentage}% of total)`;
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Number of Responses'
                        }
                    },
                    x: {
                        ticks: {
                            display: false // Hide x-axis labels since legend shows the info
                        }
                    }
                }
            }
        });
        
        this.showDownloadButton();
        console.log(`Created bar chart for: ${title}`);
    },

    // Create a stacked bar chart for matrix questions
    createStackedBarChart(title, matrixData, scale, totalResponses) {
        const ctx = document.getElementById('analysisChart');
        if (!ctx) return;
        
        // Destroy existing chart if it exists
        if (this.charts.current) {
            this.charts.current.destroy();
        }
        
        const items = Object.keys(matrixData);
        const datasets = [];
        
        // Create a dataset for each scale item
        scale.forEach((scaleItem, index) => {
            const data = items.map(item => matrixData[item][scaleItem] || 0);
            const color = this.generateColors(scale.length).background[index];
            
            datasets.push({
                label: scaleItem,
                data: data,
                backgroundColor: color,
                borderWidth: 0
            });
        });

        this.charts.current = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: items,
                datasets: datasets                
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        stacked: true,
                        ticks: {
                            maxRotation: 45,
                            minRotation: 0
                        }
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        },
                        title: {
                            display: true,
                            text: 'Number of Responses'
                        }
                    }
                },
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: {
                            size: 16,
                            weight: 'bold'
                        },
                        padding: 20
                    },
                    legend: {
                        position: 'top',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false,
                        callbacks: {
                            label: function(context) {
                                const percentage = ((context.parsed.y / totalResponses) * 100).toFixed(1);
                                return `${context.dataset.label}: ${context.parsed.y} (${percentage}% of total)`;
                            }
                        }
                    }
                },
                interaction: {
                    mode: 'index',
                    intersect: false
                }
            }
        });
        
        this.showDownloadButton();
        console.log(`Created stacked bar chart for: ${title}`);
    },

     // Show text responses for open text questions
    showTextResponses(questionTitle, responses, totalResponses) {
        const chartContainer = document.getElementById('chartContainer');
        const otherContainer = document.getElementById('otherAnswers');
        
        if (!chartContainer) return;
        
        // Clear other answers container
        if (otherContainer) {
            otherContainer.classList.add('hidden');
            otherContainer.innerHTML = '';
        }
        
        // Replace chart container content with text responses
        chartContainer.innerHTML = `
            <div class="text-responses">
                <h3>${questionTitle}</h3>
                <div class="response-count">${responses.length} text responses:</div>
                <div class="responses-list">
                    ${responses.length > 0 
                        ? responses.map((response, index) => `
                            <div class="response-item">
                                <span class="response-number">${index + 1}.</span>
                                <span class="response-text">"${response}"</span>
                            </div>
                        `).join('')
                        : '<div class="no-responses">No responses found for this question.</div>'
                    }
                </div>
            </div>
        `;
    },

    // Generate colors for chart
    generateColors(count) {
        const colors = []
        let hue = 0.6
        let hueIncrement = 0.618033988749895; // Golden ratio increment for hue
        for(let i = 0; i < count; i++) {            
            const saturation = 1.0;
            const value = 0.8;
            // Convert HSV to RGB and then to Hex
            let [r, g, b] = hsvToRgb(hue, saturation, value);
            const color = rgbToHex(r, g, b);
            colors.push(color);
            hue += hueIncrement;
            hue %= 1.0; // Wrap around to stay within [0, 1]
        }
                    
        const background = [];
        
        for (let i = 0; i < count; i++) {
            const color = colors[i % colors.length];
            background.push(color + 'A0'); // Add transparency
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

    // Show download button for charts
    showDownloadButton() {
        const downloadBtn = document.getElementById('downloadPngBtn');
        if (downloadBtn) {
            downloadBtn.style.display = 'inline-block';
            downloadBtn.onclick = () => this.downloadChartAsPNG();
        }
    },

    // Download chart as PNG
    downloadChartAsPNG() {
        if (!this.charts.current) return;
        
        const canvas = document.getElementById('analysisChart');
        if (!canvas) return;
        
        const scale = this.getChartScale();
        
        try {
            const link = document.createElement('a');
            link.href = canvas.toDataURL('image/png', 1.0);
            link.download = `chart_${scale}x.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Error downloading PNG:', error);
            alert('Error downloading chart as PNG.');
        }
    },

    // Hide download button
    hideDownloadButton() {
        const downloadBtn = document.getElementById('downloadPngBtn');
        if (downloadBtn) {
            downloadBtn.style.display = 'none';
        }
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
        
        this.hideDownloadButton();
    }
};

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    SurveyApp.init();
});