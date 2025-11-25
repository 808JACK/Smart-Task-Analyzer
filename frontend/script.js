// API Configuration
const API_BASE_URL = window.ENV?.API_URL || 'http://localhost:8000/api/tasks';

// State
let tasks = [];
let taskIdCounter = 1;

// DOM Elements
const taskForm = document.getElementById('taskForm');
const jsonInput = document.getElementById('jsonInput');
const loadJsonBtn = document.getElementById('loadJsonBtn');
const analyzeBtn = document.getElementById('analyzeBtn');
const tasksList = document.getElementById('tasksList');
const taskCount = document.getElementById('taskCount');
const outputSection = document.getElementById('outputSection');
const loadingOverlay = document.getElementById('loadingOverlay');
const strategySelect = document.getElementById('strategySelect');

// Event Listeners
taskForm.addEventListener('submit', handleAddTask);
loadJsonBtn.addEventListener('click', handleLoadJson);
analyzeBtn.addEventListener('click', handleAnalyzeTasks);

// Initialize
updateTasksList();

// Add Task from Form
function handleAddTask(e) {
    e.preventDefault();
    
    const title = document.getElementById('title').value.trim();
    const dueDate = document.getElementById('dueDate').value;
    const estimatedHours = parseFloat(document.getElementById('estimatedHours').value);
    const importance = parseInt(document.getElementById('importance').value);
    const dependenciesInput = document.getElementById('dependencies').value.trim();
    
    // Validate
    if (!title || !dueDate || !estimatedHours || !importance) {
        showError('Please fill in all required fields');
        return;
    }
    
    if (importance < 1 || importance > 10) {
        showError('Importance must be between 1 and 10');
        return;
    }
    
    // Parse dependencies
    const dependencies = dependenciesInput 
        ? dependenciesInput.split(',').map(d => d.trim()).filter(d => d)
        : [];
    
    // Create task
    const task = {
        id: `task${taskIdCounter++}`,
        title,
        due_date: dueDate,
        estimated_hours: estimatedHours,
        importance,
        dependencies
    };
    
    tasks.push(task);
    updateTasksList();
    taskForm.reset();
    
    showSuccess('Task added successfully!');
}

// Load Tasks from JSON
function handleLoadJson() {
    const jsonText = jsonInput.value.trim();
    
    if (!jsonText) {
        showError('Please paste JSON data');
        return;
    }
    
    try {
        const parsedTasks = JSON.parse(jsonText);
        
        if (!Array.isArray(parsedTasks)) {
            showError('JSON must be an array of tasks');
            return;
        }
        
        // Validate tasks
        for (let i = 0; i < parsedTasks.length; i++) {
            const task = parsedTasks[i];
            if (!task.title) {
                showError(`Task at index ${i} is missing title`);
                return;
            }
            // Add ID if missing
            if (!task.id) {
                task.id = `task${taskIdCounter++}`;
            }
        }
        
        tasks = parsedTasks;
        updateTasksList();
        jsonInput.value = '';
        
        showSuccess(`Loaded ${parsedTasks.length} tasks from JSON`);
    } catch (error) {
        showError('Invalid JSON format: ' + error.message);
    }
}

// Update Tasks List Display
function updateTasksList() {
    taskCount.textContent = tasks.length;
    
    if (tasks.length === 0) {
        tasksList.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">No tasks added yet</p>';
        return;
    }
    
    tasksList.innerHTML = tasks.map((task, index) => `
        <div class="task-item">
            <div class="task-item-content">
                <h4>${task.title}</h4>
                <p>Due: ${task.due_date} | Hours: ${task.estimated_hours} | Importance: ${task.importance}/10</p>
            </div>
            <button onclick="removeTask(${index})">Remove</button>
        </div>
    `).join('');
}

// Remove Task
function removeTask(index) {
    tasks.splice(index, 1);
    updateTasksList();
}

// Analyze Tasks
async function handleAnalyzeTasks() {
    if (tasks.length === 0) {
        showError('Please add at least one task before analyzing');
        return;
    }
    
    const strategy = strategySelect.value;
    
    showLoading(true);
    
    try {
        // Call analyze endpoint
        const analyzeResponse = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        if (!analyzeResponse.ok) {
            const errorData = await analyzeResponse.json();
            throw new Error(errorData.error || 'Failed to analyze tasks');
        }
        
        const analyzeData = await analyzeResponse.json();
        
        // Call suggest endpoint
        const suggestResponse = await fetch(`${API_BASE_URL}/suggest/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasks,
                strategy: strategy
            })
        });
        
        if (!suggestResponse.ok) {
            const errorData = await suggestResponse.json();
            throw new Error(errorData.error || 'Failed to get suggestions');
        }
        
        const suggestData = await suggestResponse.json();
        
        // Display results
        displayResults(analyzeData, suggestData);
        
    } catch (error) {
        showError('Error analyzing tasks: ' + error.message);
    } finally {
        showLoading(false);
    }
}

// Display Results
function displayResults(analyzeData, suggestData) {
    outputSection.style.display = 'block';
    
    // Update header
    document.getElementById('usedStrategy').textContent = getStrategyName(analyzeData.strategy);
    document.getElementById('totalTasks').textContent = analyzeData.total_count;
    
    // Display top 3 suggestions
    const suggestionsContainer = document.getElementById('suggestionsContainer');
    suggestionsContainer.innerHTML = '<h3>🏆 Top 3 Recommended Tasks</h3>';
    
    suggestData.suggestions.forEach(suggestion => {
        const card = createSuggestionCard(suggestion);
        suggestionsContainer.appendChild(card);
    });
    
    // Display all sorted tasks
    const sortedTasksContainer = document.getElementById('sortedTasks');
    sortedTasksContainer.innerHTML = '';
    
    analyzeData.tasks.forEach((task, index) => {
        const card = createTaskCard(task, index + 1);
        sortedTasksContainer.appendChild(card);
    });
    
    // Scroll to results
    outputSection.scrollIntoView({ behavior: 'smooth' });
}

// Create Suggestion Card
function createSuggestionCard(suggestion) {
    const card = document.createElement('div');
    card.className = `suggestion-card rank-${suggestion.rank}`;
    
    const task = suggestion.task;
    const breakdown = task.score_breakdown;
    
    card.innerHTML = `
        <div class="suggestion-header">
            <div class="rank-badge">#${suggestion.rank}</div>
            <div class="priority-score">${task.priority_score}</div>
        </div>
        <h3 class="task-title">${task.title}</h3>
        <div class="explanation">${suggestion.explanation}</div>
        <div class="task-details">
            <div class="detail-item">
                <div class="detail-label">Due Date</div>
                <div class="detail-value">${task.due_date}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Estimated Hours</div>
                <div class="detail-value">${task.estimated_hours}h</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Importance</div>
                <div class="detail-value">${task.importance}/10</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Dependencies</div>
                <div class="detail-value">${task.dependencies.length || 'None'}</div>
            </div>
        </div>
        <div class="score-breakdown">
            <div class="score-item">Urgency: <strong>${breakdown.urgency}</strong></div>
            <div class="score-item">Importance: <strong>${breakdown.importance}</strong></div>
            <div class="score-item">Effort: <strong>${breakdown.effort}</strong></div>
            <div class="score-item">Dependencies: <strong>${breakdown.dependencies}</strong></div>
        </div>
        ${task.has_circular_dependency ? '<span class="warning-badge">⚠️ Circular Dependency</span>' : ''}
    `;
    
    return card;
}

// Create Task Card
function createTaskCard(task, rank) {
    const card = document.createElement('div');
    const priorityClass = getPriorityClass(task.priority_score);
    card.className = `sorted-task-card priority-${priorityClass}`;
    
    const breakdown = task.score_breakdown;
    
    card.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
            <div>
                <span style="font-size: 1.2em; font-weight: bold; color: #667eea;">#{rank}</span>
                <strong style="font-size: 1.2em; margin-left: 10px;">${task.title}</strong>
                ${task.has_circular_dependency ? '<span class="warning-badge">⚠️ Circular Dependency</span>' : ''}
            </div>
            <div>
                <span class="priority-badge badge-${priorityClass}">${priorityClass.toUpperCase()}</span>
                <span style="font-size: 1.5em; font-weight: bold; color: #667eea; margin-left: 15px;">${task.priority_score}</span>
            </div>
        </div>
        <div class="task-details">
            <div class="detail-item">
                <div class="detail-label">Due Date</div>
                <div class="detail-value">${task.due_date}</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Estimated Hours</div>
                <div class="detail-value">${task.estimated_hours}h</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Importance</div>
                <div class="detail-value">${task.importance}/10</div>
            </div>
            <div class="detail-item">
                <div class="detail-label">Dependencies</div>
                <div class="detail-value">${task.dependencies.length || 'None'}</div>
            </div>
        </div>
        <div class="score-breakdown">
            <div class="score-item">Urgency: <strong>${breakdown.urgency}</strong></div>
            <div class="score-item">Importance: <strong>${breakdown.importance}</strong></div>
            <div class="score-item">Effort: <strong>${breakdown.effort}</strong></div>
            <div class="score-item">Dependencies: <strong>${breakdown.dependencies}</strong></div>
        </div>
    `;
    
    return card;
}

// Helper Functions
function getPriorityClass(score) {
    if (score >= 70) return 'high';
    if (score >= 50) return 'medium';
    return 'low';
}

function getStrategyName(strategy) {
    const names = {
        'smart_balance': 'Smart Balance',
        'fastest_wins': 'Fastest Wins',
        'high_impact': 'High Impact',
        'deadline_driven': 'Deadline Driven'
    };
    return names[strategy] || strategy;
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    
    document.querySelector('.input-section').insertBefore(errorDiv, document.querySelector('.input-section').firstChild);
    
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.style.cssText = 'background: #d4edda; color: #155724; padding: 15px; border-radius: 8px; margin: 15px 0; border: 1px solid #c3e6cb;';
    successDiv.textContent = message;
    
    document.querySelector('.input-section').insertBefore(successDiv, document.querySelector('.input-section').firstChild);
    
    setTimeout(() => successDiv.remove(), 3000);
}
