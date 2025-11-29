const API_BASE_URL = 'http://127.0.0.1:8000/api/tasks';

let tasksData = [];

document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
});

function initializeEventListeners() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', handleTabSwitch);
    });

    document.getElementById('add-task-btn').addEventListener('click', handleAddTask);
    document.getElementById('clear-form-btn').addEventListener('click', handleClearForm);
    document.getElementById('load-json-btn').addEventListener('click', handleLoadJSON);
    document.getElementById('analyze-btn').addEventListener('click', handleAnalyze);
}

function handleTabSwitch(event) {
    const mode = event.target.dataset.mode;
    
    document.querySelectorAll('.input-mode').forEach(el => {
        el.classList.remove('active');
    });
    
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    document.getElementById(`${mode}-mode`).classList.add('active');
    event.target.classList.add('active');
}

function handleAddTask() {
    const title = document.getElementById('task-title').value.trim();
    const dueDate = document.getElementById('task-due-date').value;
    const importance = parseInt(document.getElementById('task-importance').value) || 5;
    const hours = parseFloat(document.getElementById('task-hours').value) || 2;
    const dependenciesStr = document.getElementById('task-dependencies').value.trim();

    if (!title) {
        showError('Please enter a task title');
        return;
    }

    if (!dueDate) {
        showError('Please select a due date');
        return;
    }

    if (importance < 1 || importance > 10) {
        showError('Importance must be between 1 and 10');
        return;
    }

    if (hours <= 0) {
        showError('Estimated hours must be positive');
        return;
    }

    const dependencies = dependenciesStr
        ? dependenciesStr.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d))
        : [];

    const newTask = {
        id: tasksData.length + 1,
        title: title,
        due_date: dueDate,
        importance: importance,
        estimated_hours: hours,
        dependencies: dependencies
    };

    tasksData.push(newTask);
    renderTaskList();
    handleClearForm();
    showSuccess(`Task "${title}" added successfully`);
}

function handleClearForm() {
    document.getElementById('task-title').value = '';
    document.getElementById('task-due-date').value = '';
    document.getElementById('task-importance').value = '5';
    document.getElementById('task-hours').value = '2';
    document.getElementById('task-dependencies').value = '';
}

function handleLoadJSON() {
    const jsonInput = document.getElementById('json-input').value.trim();

    if (!jsonInput) {
        showError('Please paste JSON data');
        return;
    }

    try {
        const parsedData = JSON.parse(jsonInput);

        if (!Array.isArray(parsedData)) {
            showError('JSON must be an array of tasks');
            return;
        }

        tasksData = parsedData.map((task, index) => ({
            id: task.id || index + 1,
            title: task.title || 'Untitled',
            due_date: task.due_date || new Date().toISOString().split('T')[0],
            importance: task.importance || 5,
            estimated_hours: task.estimated_hours || 2,
            dependencies: task.dependencies || []
        }));

        renderTaskList();
        document.getElementById('json-input').value = '';
        showSuccess(`Loaded ${tasksData.length} tasks from JSON`);
    } catch (error) {
        showError('Invalid JSON format: ' + error.message);
    }
}

function renderTaskList() {
    const taskList = document.getElementById('task-list');

    if (tasksData.length === 0) {
        taskList.innerHTML = '<p class="empty-state">No tasks added yet. Add a task or load from JSON.</p>';
        return;
    }

    taskList.innerHTML = tasksData.map(task => `
        <div class="task-item">
            <div class="task-item-info">
                <div class="task-item-title">${escapeHtml(task.title)}</div>
                <div class="task-item-details">
                    Due: ${task.due_date} | Importance: ${task.importance}/10 | Hours: ${task.estimated_hours}
                </div>
            </div>
            <button class="task-item-remove" onclick="removeTask(${task.id})">Remove</button>
        </div>
    `).join('');
}

function removeTask(taskId) {
    tasksData = tasksData.filter(t => t.id !== taskId);
    renderTaskList();
    showSuccess('Task removed');
}

async function handleAnalyze() {
    if (tasksData.length === 0) {
        showError('Please add at least one task to analyze');
        return;
    }

    const strategy = document.getElementById('strategy-select').value;

    showLoading(true);
    clearResults();

    try {
        const response = await fetch(`${API_BASE_URL}/analyze/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                tasks: tasksData,
                strategy: strategy
            })
        });

        const data = await response.json();

        showLoading(false);

        if (!response.ok || !data.success) {
            showError(data.message || data.error || 'Analysis failed');
            return;
        }

        displayResults(data);
    } catch (error) {
        showLoading(false);
        showError('Network error: ' + error.message);
        console.error('API Error:', error);
    }
}

function displayResults(data) {
    const resultsContainer = document.getElementById('results-container');
    const summaryDiv = document.getElementById('results-summary');
    const summaryText = document.getElementById('summary-text');

    summaryText.textContent = `Analyzed ${data.total_tasks} task(s) using "${data.strategy}" strategy`;
    summaryDiv.classList.remove('hidden');

    if (data.results.length === 0) {
        resultsContainer.innerHTML = '<p class="empty-state">No results to display</p>';
        return;
    }

    resultsContainer.innerHTML = data.results.map(task => {
        const priorityClass = task.priority_level.toLowerCase();

        return `
            <div class="task-card ${priorityClass}">
                <div class="task-card-header">
                    <div class="task-card-title">${escapeHtml(task.title)}</div>
                    <span class="priority-badge ${priorityClass}">${task.priority_level}</span>
                </div>

                <div class="task-card-explanation">
                    ${escapeHtml(task.explanation)}
                </div>

                <div class="task-card-metrics">
                    <div class="metric">
                        <div class="metric-label">Priority Score</div>
                        <div class="metric-value">${task.priority_score}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Urgency</div>
                        <div class="metric-value">${task.urgency}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Importance</div>
                        <div class="metric-value">${task.importance_score}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Effort</div>
                        <div class="metric-value">${task.effort > 0 ? '+' : ''}${task.effort}</div>
                    </div>
                </div>

                <div class="task-card-details">
                    <div class="detail-row">
                        <span class="detail-label">Due Date:</span>
                        <span class="detail-value">${task.due_date}</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Importance:</span>
                        <span class="detail-value">${task.importance}/10</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Estimated Hours:</span>
                        <span class="detail-value">${task.estimated_hours} hrs</span>
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Dependencies Count:</span>
                        <span class="detail-value">${task.dependencies_count}</span>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function showLoading(isLoading) {
    const spinner = document.getElementById('loading-spinner');
    const analyzeBtn = document.getElementById('analyze-btn');

    if (isLoading) {
        spinner.classList.remove('hidden');
        analyzeBtn.disabled = true;
    } else {
        spinner.classList.add('hidden');
        analyzeBtn.disabled = false;
    }
}

function showError(message) {
    const errorDiv = document.getElementById('error-message');
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');

    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

function showSuccess(message) {
    console.log('Success:', message);
}

function clearResults() {
    document.getElementById('results-container').innerHTML = '<p class="empty-state">Results will appear here after analysis</p>';
    document.getElementById('results-summary').classList.add('hidden');
    document.getElementById('error-message').classList.add('hidden');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
