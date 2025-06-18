// Global variables
let csvData = [];
let headers = [];
let currentChart = null;

// DOM elements
const statusDiv = document.getElementById('status');
const questionSelector = document.getElementById('questionSelector');
const mainQuestionSelect = document.getElementById('mainQuestion');
const filtersContainer = document.getElementById('filtersContainer');
const dataPreview = document.getElementById('dataPreview');
const chartContainer = document.getElementById('chartContainer');

// Event listeners
mainQuestionSelect.addEventListener('change', handleQuestionChange);

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
                populateQuestionSelector();
                displayDataPreview();
            },
            error: function(error) {
                showStatus('Error parsing CSV: ' + error.message, 'error');
            }
        });
        
    } catch (error) {
        showStatus('Error loading CSV file: ' + error.message + '. Make sure plg_survey.csv is in the same folder as this HTML file.', 'error');
    }
}

// Populate question selector dropdown
function populateQuestionSelector() {
    mainQuestionSelect.innerHTML = '<option value="">Choose a question...</option>';
    
    headers.forEach(header => {
        const option = document.createElement('option');
        option.value = header;
        option.textContent = header;
        mainQuestionSelect.appendChild(option);
    });
    
    showElement(questionSelector);
}

// Display data preview table
function displayDataPreview() {
    const tableHead = document.getElementById('tableHead');
    const tableBody = document.getElementById('tableBody');
    
    // Clear existing content
    tableHead.innerHTML = '';
    tableBody.innerHTML = '';
    
    // Create header row
    const headerRow = document.createElement('tr');
    headers.forEach(header => {
        const th = document.createElement('th');
        th.textContent = header;
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);
    
    // Create data rows (limit to first 50 for performance)
    const rowsToShow = Math.min(csvData.length, 50);
    for (let i = 0; i < rowsToShow; i++) {
        const row = document.createElement('tr');
        headers.forEach(header => {
            const td = document.createElement('td');
            td.textContent = csvData[i][header] || '';
            row.appendChild(td);
        });
        tableBody.appendChild(row);
    }
    
    // Show preview with row count info
    if (csvData.length > 50) {
        const infoRow = document.createElement('tr');
        const infoCell = document.createElement('td');
        infoCell.colSpan = headers.length;
        infoCell.textContent = `... and ${csvData.length - 50} more rows`;
        infoCell.style.textAlign = 'center';
        infoCell.style.fontStyle = 'italic';
        infoCell.style.backgroundColor = '#f0f0f0';
        infoRow.appendChild(infoCell);
        tableBody.appendChild(infoRow);
    }
    
    showElement(dataPreview);
}

// Handle question selection change
function handleQuestionChange() {
    const selectedQuestion = mainQuestionSelect.value;
    
    if (!selectedQuestion) {
        hideElement(chartContainer);
        return;
    }
    
    // For now, just show a placeholder
    showStatus(`Selected question: ${selectedQuestion}. Chart functionality will be added in the next step.`);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    loadCSVData();
});

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