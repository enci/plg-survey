// Procedural Level Generation Survey Analysis Tool
// Version 2.0 - Data Loading Implementation

console.log('Survey Analysis Tool Initialized');

// Global application state
const SurveyApp = {
    data: {
        responses: null,
        schema: null,
        loaded: false
    },
    charts: {},
    filters: {},
    
    // Initialize the application
    init() {
        console.log('Initializing Survey Analysis Tool...');
        this.setupEventListeners();
    },
    
    // Set up event listeners
    setupEventListeners() {
        // Add load data button listener
        const loadBtn = document.getElementById('loadDataBtn');
        if (loadBtn) {
            loadBtn.addEventListener('click', () => this.loadData());
        }

        // Add question selector listener
        const questionSelect = document.getElementById('questionSelect');
        if (questionSelect) {
            questionSelect.addEventListener('change', (e) => this.analyzeQuestion(e.target.value));
        }
    },
    
    // Load survey data and schema
    async loadData() {
        const statusDiv = document.getElementById('dataStatus');
        const loadBtn = document.getElementById('loadDataBtn');
        
        try {
            // Show loading state
            this.showStatus('loading', 'Loading survey data and schema...');
            loadBtn.disabled = true;
            
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
            this.showStatus('error', `Failed to load data: ${error.message}`);
            loadBtn.disabled = false;
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
        const loadBtn = document.getElementById('loadDataBtn');
        
        // Count unique roles
        const roles = responses.map(r => r.professional_role).filter(Boolean);
        const uniqueRoles = new Set(roles).size;
        
        // Count experience levels
        const experienceLevels = responses.map(r => r.years_experience).filter(Boolean);
        const uniqueExperience = new Set(experienceLevels).size;
        
        const summaryText = `
            ✓ Successfully loaded survey data!
            <br><strong>${responses.length}</strong> total responses
            <br><strong>${Object.keys(schema.questions).length}</strong> question types in schema
            <br><strong>${uniqueRoles}</strong> different professional roles
            <br><strong>${uniqueExperience}</strong> experience level categories
            <br><br>Data is ready for analysis and visualization.
        `;
        
        this.showStatus('success', summaryText);
        loadBtn.textContent = 'Data Loaded ✓';
        loadBtn.disabled = true;
        
        // Show analysis section and populate question dropdown
        this.showAnalysisSection();
        this.populateQuestionDropdown();
        
        console.log('Survey data loaded successfully:', {
            responses: responses.length,
            schema_questions: Object.keys(schema.questions).length,
            unique_roles: uniqueRoles,
            unique_experience: uniqueExperience
        });
    },

    // Show the analysis section
    showAnalysisSection() {
        const analysisSection = document.getElementById('analysisSection');
        if (analysisSection) {
            analysisSection.classList.remove('hidden');
        }
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
            return;
        }
        
        const { responses, schema } = this.data;
        const question = schema.questions[questionKey];
        
        if (!question || question.type !== 'single_choice') {
            console.log('Question not found or not single choice');
            this.clearChart();
            return;
        }
        
        console.log(`Analyzing question: ${question.question}`);
        
        // Get response data for this question
        const responseData = responses.map(r => r[questionKey]).filter(Boolean);
        
        // Count responses
        const counts = {};
        responseData.forEach(response => {
            counts[response] = (counts[response] || 0) + 1;
        });
        
        // Create pie chart
        this.createPieChart(question.question, counts);
    },

    // Create a pie chart
    createPieChart(title, data) {
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
        
        this.charts.current = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: values,
                    backgroundColor: colors.background,
                    borderColor: colors.border,
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
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
        const border = [];
        
        for (let i = 0; i < count; i++) {
            const color = colors[i % colors.length];
            background.push(color + '80'); // Add transparency
            border.push(color);
        }
        
        return { background, border };
    },

    // Clear the chart
    clearChart() {
        if (this.charts.current) {
            this.charts.current.destroy();
            this.charts.current = null;
        }
    },
    
    // Show status message
    showStatus(type, message) {
        const statusDiv = document.getElementById('dataStatus');
        if (!statusDiv) return;
        
        statusDiv.className = `data-status ${type}`;
        statusDiv.innerHTML = message;
        statusDiv.classList.remove('hidden');
    },
    
    // Get unique values for a field
    getUniqueValues(field) {
        if (!this.data.loaded) return [];
        return [...new Set(this.data.responses.map(r => r[field]).filter(Boolean))];
    },
    
    // Filter responses by criteria
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
    
    // Placeholder for chart creation
    createChart(type, containerId, data) {
        console.log(`Chart creation placeholder: ${type} in ${containerId}`);
        // Legacy placeholder - actual chart creation now handled by specific methods
    }
};

// Initialize the app when the page loads
document.addEventListener('DOMContentLoaded', () => {
    SurveyApp.init();
});