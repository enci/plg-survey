// Global variables
let csvData = [];
let headers = [];
let currentChart = null;
let questionCategoriesData = {};
let showingFullData = false;
let matrixQuestions = {};
let processedQuestions = [];

// Define matrix question patterns
const matrixPatterns = {
    'Tool Experience Rating': {
        columns: ['Houdini', 'Unreal Engine PCG tools', 'Blender Geometry Nodes', 
                 'Plugins/Tools that use Wave Function Collapse', 
                 'Plugins/Tools that use other methods', 'Custom code-based PCG solutions'],
        originalQuestion: 'How would you rate your current experience with the following procedural tools?'
    },
    'Genre Interest Rating': {
        columns: ['Action/Adventure', 'First-person Shooters', 'Platformers', 
                 'Racing games', 'Puzzle games', 'RPGs', 'Strategy games', 'Roguelikes / Roguelites'],
        originalQuestion: 'If your project were of the following game genre, how interested would you be in using procedural level generation?'
    }
};

// DOM elements
const statusDiv = document.getElementById('status');
const summaryOverview = document.getElementById('summaryOverview');
const insightsSection = document.getElementById('insightsSection');
const questionCategoriesDiv = document.getElementById('questionCategories');
const dataPreview = document.getElementById('dataPreview');

// Load CSV data automatically
async function loadCSVData() {
    try {
        showStatus('Loading survey data...');
        
        const response = await fetch('plg_survey.csv');
        if (!response.ok) {
            throw new Error('Failed to load CSV file');
        }
        
        const csvText = await response.text();
        
        Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true,
            complete: function(results) {
                if (results.errors.length > 0) {
                    showStatus('Error parsing CSV: ' + results.errors[0].message, 'error');
                    return;
                }
                
                csvData = results.data;
                headers = results.meta.fields;
                
                if (csvData.length === 0) {
                    showStatus('The CSV file appears to be empty.', 'error');
                    return;
                }
                
                showStatus(`Successfully loaded ${csvData.length} survey responses with ${headers.length} questions.`);
                processAndDisplayData();
            },
            error: function(error) {
                showStatus('Error parsing CSV: ' + error.message, 'error');
            }
        });
        
    } catch (error) {
        showStatus('Error loading CSV file: ' + error.message + '. Make sure plg_survey.csv is in the same folder as this HTML file.', 'error');
    }
}

// Utility functions
function showStatus(message, type = 'info') {
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.classList.remove('hidden');
}

function hideStatus() {
    statusDiv.classList.add('hidden');
}

function showElement(element) {
    element.classList.remove('hidden');
}

function hideElement(element) {
    element.classList.add('hidden');
}

// Process data and display summaries
function processAndDisplayData() {
    categorizeQuestions();
    displaySummaryOverview();
    displayKeyInsights();
    displayQuestionCategories();
    displayDataPreview();
    hideStatus();
}

// Reconstruct matrix questions from exploded columns
function reconstructMatrixQuestions() {
    matrixQuestions = {};
    processedQuestions = [...headers]; // Start with all original headers
    
    // Process each matrix pattern
    Object.entries(matrixPatterns).forEach(([matrixName, pattern]) => {
        const { columns, originalQuestion } = pattern;
        
        // Check if all columns exist in our data
        const existingColumns = columns.filter(col => headers.includes(col));
        
        if (existingColumns.length > 0) {
            // Create the matrix question
            matrixQuestions[matrixName] = {
                originalQuestion,
                columns: existingColumns,
                data: csvData.map(row => {
                    const matrixData = {};
                    existingColumns.forEach(col => {
                        matrixData[col] = row[col];
                    });
                    return matrixData;
                })
            };
            
            // Remove the individual columns from processed questions
            // and add the matrix question
            processedQuestions = processedQuestions.filter(h => !existingColumns.includes(h));
            processedQuestions.push(matrixName);
            
            console.log(`Reconstructed matrix question: ${matrixName} with ${existingColumns.length} items`);
        }
    });
    
    console.log(`Total questions after reconstruction: ${processedQuestions.length}`);
    console.log('Matrix questions created:', Object.keys(matrixQuestions));
}
// Categorize questions based on their content and type
// Categorize questions based on their content and type
function categorizeQuestions() {
    questionCategoriesData = {
        'Demographics': [],
        'Experience & Tools': [],
        'Game Development': [],
        'Procedural Generation': [],
        'AI & Technology': [],
        'Other': []
    };
    
    // Define metadata fields to exclude
    const metadataFields = ['ID', 'Start time', 'Completion time', 'Email', 'Name', 'Last modified time'];
    
    // Process both regular questions and matrix questions
    processedQuestions.forEach(header => {
        // Skip metadata fields
        if (metadataFields.includes(header)) {
            return;
        }
        
        const lowerHeader = header.toLowerCase();
        
        // Special handling for matrix questions
        if (matrixQuestions[header]) {
            if (header === 'Tool Experience Rating') {
                questionCategoriesData['Experience & Tools'].push(header);
            } else if (header === 'Genre Interest Rating') {
                questionCategoriesData['Game Development'].push(header);
            }
            return;
        }
        
        // Regular question categorization
        if (lowerHeader.includes('role') || lowerHeader.includes('experience')) {
            questionCategoriesData['Demographics'].push(header);
        } else if (lowerHeader.includes('engine') || lowerHeader.includes('tool') || 
                   lowerHeader.includes('houdini') || lowerHeader.includes('blender') ||
                   lowerHeader.includes('unreal') || lowerHeader.includes('plugin')) {
            questionCategoriesData['Experience & Tools'].push(header);
        } else if (lowerHeader.includes('game') || lowerHeader.includes('genre') ||
                   lowerHeader.includes('action') || lowerHeader.includes('shooter') ||
                   lowerHeader.includes('platform') || lowerHeader.includes('rpg') ||
                   lowerHeader.includes('racing') || lowerHeader.includes('puzzle') ||
                   lowerHeader.includes('strategy') || lowerHeader.includes('roguelike')) {
            questionCategoriesData['Game Development'].push(header);
        } else if (lowerHeader.includes('procedural') || lowerHeader.includes('pcg') ||
                   lowerHeader.includes('level') || lowerHeader.includes('generation') ||
                   lowerHeader.includes('generator')) {
            questionCategoriesData['Procedural Generation'].push(header);
        } else if (lowerHeader.includes('ai') || lowerHeader.includes('artificial')) {
            questionCategoriesData['AI & Technology'].push(header);
        } else {
            questionCategoriesData['Other'].push(header);
        }
    });
    
    console.log('Question categories:', questionCategoriesData);
}

// Display summary overview statistics
function displaySummaryOverview() {
    const statsGrid = document.getElementById('statsGrid');
    
    // Calculate key statistics
    const totalResponses = csvData.length;
    
    // Count actual survey questions (exclude only metadata, not matrix questions)
    const metadataFields = ['ID', 'Start time', 'Completion time', 'Email', 'Name', 'Last modified time'];
    const totalQuestions = processedQuestions.filter(h => !metadataFields.includes(h)).length;
    
    // Calculate completion rate (responses with substantial data)
    const completeResponses = csvData.filter(row => {
        const filledFields = Object.values(row).filter(value => value && value.trim()).length;
        return filledFields > 5; // More than 5 filled fields considered complete
    }).length;
    
    const completionRate = Math.round((completeResponses / totalResponses) * 100);
    
    // Get most recent response date
    const timestamps = csvData.map(row => row['Completion time']).filter(t => t);
    const latestDate = timestamps.length > 0 ? 
        new Date(Math.max(...timestamps.map(t => new Date(t)))).toLocaleDateString() : 
        'Unknown';
    
    const stats = [
        { number: totalResponses, label: 'Total Responses' },
        { number: totalQuestions, label: 'Survey Questions' },
        { number: `${completionRate}%`, label: 'Completion Rate' },
        { number: latestDate, label: 'Latest Response' }
    ];
    
    statsGrid.innerHTML = stats.map(stat => `
        <div class="stat-card">
            <div class="stat-number">${stat.number}</div>
            <div class="stat-label">${stat.label}</div>
        </div>
    `).join('');
    
    showElement(summaryOverview);
}

// Display key insights from the data
function displayKeyInsights() {
    const insightsGrid = document.getElementById('insightsGrid');
    
    // Analyze professional roles
    const roleQuestion = headers.find(h => h.toLowerCase().includes('professional role'));
    const roleInsight = roleQuestion ? analyzeTopResponses(roleQuestion, 3) : null;
    
    // Analyze experience levels
    const expQuestion = headers.find(h => h.toLowerCase().includes('years of experience'));
    const expInsight = expQuestion ? analyzeTopResponses(expQuestion, 3) : null;
    
    // Analyze game engines
    const engineQuestion = headers.find(h => h.toLowerCase().includes('game engine'));
    const engineInsight = engineQuestion ? analyzeTopResponses(engineQuestion, 3) : null;
    
    const insights = [];
    
    if (roleInsight) {
        insights.push({
            title: '👥 Developer Roles',
            text: `Top roles: ${roleInsight.top.map(item => `${item.value} (${item.count})`).join(', ')}`
        });
    }
    
    if (expInsight) {
        insights.push({
            title: '📈 Experience Levels',
            text: `Most common: ${expInsight.top.map(item => `${item.value} (${item.count})`).join(', ')}`
        });
    }
    
    if (engineInsight) {
        insights.push({
            title: '🎮 Game Engines',
            text: `Popular engines: ${engineInsight.top.map(item => `${item.value} (${item.count})`).join(', ')}`
        });
    }
    
    // Add general insights
    insights.push({
        title: '📊 Response Quality',
        text: `${csvData.filter(row => Object.values(row).filter(v => v && v.trim()).length > 10).length} detailed responses with rich data`
    });
    
    insightsGrid.innerHTML = insights.map(insight => `
        <div class="insight-card">
            <div class="insight-title">${insight.title}</div>
            <div class="insight-text">${insight.text}</div>
        </div>
    `).join('');
    
    showElement(insightsSection);
}

// Analyze top responses for a question (handles both regular and matrix questions)
function analyzeTopResponses(questionName, topN = 5) {
    // Handle matrix questions
    if (matrixQuestions[questionName]) {
        const matrixData = matrixQuestions[questionName];
        const allRatings = {};
        
        // Collect all ratings across all tools/genres
        matrixData.columns.forEach(column => {
            csvData.forEach(row => {
                const rating = row[column];
                if (rating && rating.trim()) {
                    const key = `${column}: ${rating}`;
                    allRatings[key] = (allRatings[key] || 0) + 1;
                }
            });
        });
        
        const sortedEntries = Object.entries(allRatings)
            .sort(([,a], [,b]) => b - a)
            .slice(0, topN);
        
        return {
            total: Object.values(allRatings).reduce((sum, count) => sum + count, 0),
            top: sortedEntries.map(([value, count]) => ({ value, count })),
            isMatrix: true
        };
    }
    
    // Handle regular questions (existing logic)
    const responses = csvData.map(row => row[questionName]).filter(response => response && response.trim());
    
    if (responses.length === 0) return null;
    
    // Handle multi-select questions (contains commas or semicolons)
    const hasMultipleSelections = responses.some(r => r.includes(',') || r.includes(';'));
    
    let counts;
    if (hasMultipleSelections) {
        // Split multi-select responses
        const allOptions = responses.flatMap(response => 
            response.split(/[,;]/).map(item => item.trim()).filter(item => item)
        );
        counts = allOptions.reduce((acc, option) => {
            acc[option] = (acc[option] || 0) + 1;
            return acc;
        }, {});
    } else {
        // Single select responses
        counts = responses.reduce((acc, response) => {
            acc[response] = (acc[response] || 0) + 1;
            return acc;
        }, {});
    }
    
    const sortedEntries = Object.entries(counts)
        .sort(([,a], [,b]) => b - a)
        .slice(0, topN);
    
    return {
        total: responses.length,
        top: sortedEntries.map(([value, count]) => ({ value, count })),
        isMatrix: false
    };
}

// Display question categories with summaries
function displayQuestionCategories() {
    const categoryTabs = document.getElementById('categoryTabs');
    const categoryContent = document.getElementById('categoryContent');
    
    // Create tabs
    const tabs = Object.keys(questionCategoriesData).filter(category => 
        questionCategoriesData[category].length > 0
    );
    
    categoryTabs.innerHTML = tabs.map((category, index) => `
        <div class="category-tab ${index === 0 ? 'active' : ''}" 
             onclick="showCategory('${category}')" data-category="${category}">
            ${category} (${questionCategoriesData[category].length})
        </div>
    `).join('');
    
    // Show first category by default
    if (tabs.length > 0) {
        showCategory(tabs[0]);
    }
    
    showElement(questionCategoriesDiv);
}

// Show specific category content
window.showCategory = function(categoryName) {
    // Update active tab
    document.querySelectorAll('.category-tab').forEach(tab => {
        tab.classList.toggle('active', tab.dataset.category === categoryName);
    });
    
    const categoryContent = document.getElementById('categoryContent');
    const questions = questionCategoriesData[categoryName];
    
    if (questions.length === 0) {
        categoryContent.innerHTML = '<p>No questions in this category.</p>';
        return;
    }
    
    const questionList = questions.map(question => {
        const analysis = analyzeTopResponses(question, 3);
        
        // Handle matrix questions differently
        if (matrixQuestions[question]) {
            const matrixData = matrixQuestions[question];
            const responseCount = matrixData.data.reduce((count, row) => {
                return count + Object.values(row).filter(val => val && val.trim()).length;
            }, 0);
            
            let summary = `${responseCount} total ratings across ${matrixData.columns.length} items`;
            let preview = `<div class="response-preview">
                <strong>Matrix Question:</strong> ${matrixData.originalQuestion}<br>
                <strong>Items:</strong> ${matrixData.columns.join(', ')}
            </div>`;
            
            if (analysis && analysis.top.length > 0) {
                preview += `<div class="response-preview">
                    <strong>Most common ratings:</strong> ${analysis.top.map(item => 
                        `${item.value} (${item.count})`
                    ).join(', ')}
                </div>`;
            }
            
            return `
                <div class="question-item">
                    <div class="question-title">${question} <span style="color: #667eea; font-size: 0.8em;">[Matrix]</span></div>
                    <div class="question-summary">${summary}</div>
                    ${preview}
                </div>
            `;
        }
        
        // Regular questions
        const responseCount = csvData.filter(row => row[question] && row[question].trim()).length;
        
        let summary = `${responseCount} responses`;
        let preview = '';
        
        if (analysis && analysis.top.length > 0) {
            const topResponse = analysis.top[0];
            summary += ` • Top: ${topResponse.value} (${topResponse.count})`;
            
            preview = `<div class="response-preview">
                <strong>Top responses:</strong> ${analysis.top.map(item => 
                    `${item.value} (${item.count})`
                ).join(', ')}
            </div>`;
        }
        
        return `
            <div class="question-item">
                <div class="question-title">${question}</div>
                <div class="question-summary">${summary}</div>
                ${preview}
            </div>
        `;
    }).join('');
    
    categoryContent.innerHTML = `<div class="question-list">${questionList}</div>`;
}

// Display data preview
function displayDataPreview() {
    const tableHead = document.getElementById('tableHead');
    const tableBody = document.getElementById('tableBody');
    const toggleBtn = document.getElementById('toggleFullData');
    
    // Filter out metadata columns for preview
    const relevantHeaders = headers.filter(h => 
        !h.toLowerCase().includes('id') &&
        !h.toLowerCase().includes('time') &&
        !h.toLowerCase().includes('email')
    ).slice(0, 6); // Show first 6 relevant columns
    
    // Clear existing content
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';
    
    // Create header row
    const headerRow = document.createElement('tr');
    relevantHeaders.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header.length > 30 ? header.substring(0, 30) + '...' : header;
        th.title = header; // Full text on hover
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);
    
    // Create data rows
    const rowsToShow = showingFullData ? csvData.length : Math.min(csvData.length, 20);
    for (let i = 0; i < rowsToShow; i++) {
        const row = document.createElement('tr');
        relevantHeaders.forEach(header => {
            const td = document.createElement('td');
            const cellValue = csvData[i][header] || '';
            td.textContent = cellValue.length > 50 ? cellValue.substring(0, 50) + '...' : cellValue;
            td.title = cellValue; // Full text on hover
            row.appendChild(td);
        });
        tableBody.appendChild(row);
    }
    
    // Update toggle button
    toggleBtn.textContent = showingFullData ? 'Show Less Data' : 'Show All Data';
    toggleBtn.onclick = toggleDataView;
    
    showElement(dataPreview);
}

// Toggle between preview and full data view
function toggleDataView() {
    showingFullData = !showingFullData;
    displayDataPreview();
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadCSVData();
});