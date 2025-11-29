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
    document.getElementById('suggest-btn').addEventListener('click', handleSuggest);
    document.getElementById('delete-all-btn').addEventListener('click', handleDeleteAll);
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

function clearFieldErrors() {
    document.querySelectorAll('.error-text').forEach(el => {
        el.textContent = '';
    });
    document.querySelectorAll('.form-input, .json-textarea-compact').forEach(el => {
        el.classList.remove('error');
    });
}

function setFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorEl = document.getElementById(`error-${fieldId}`);
    
    if (errorEl) {
        errorEl.textContent = message;
    }
    if (field) {
        field.classList.add('error');
    }
}

function handleAddTask() {
    clearFieldErrors();
    
    const title = document.getElementById('task-title').value.trim();
    const dueDate = document.getElementById('task-due-date').value;
    const importance = parseInt(document.getElementById('task-importance').value) || 5;
    const hours = parseFloat(document.getElementById('task-hours').value) || 2;
    const dependenciesStr = document.getElementById('task-dependencies').value.trim();

    let isValid = true;

    if (!title) {
        setFieldError('task-title', 'Title required');
        isValid = false;
    }

    if (!dueDate) {
        setFieldError('task-due-date', 'Date required');
        isValid = false;
    }

    if (importance < 1 || importance > 10) {
        setFieldError('task-importance', 'Must be 1-10');
        isValid = false;
    }

    if (hours <= 0) {
        setFieldError('task-hours', 'Must be positive');
        isValid = false;
    }

    if (!isValid) return;

    const dependencies = dependenciesStr
        ? dependenciesStr.split(',').map(d => parseInt(d.trim())).filter(d => !isNaN(d))
        : [];

    const newTask = {
        id: tasksData.length > 0 ? Math.max(...tasksData.map(t => t.id)) + 1 : 1,
        title: title,
        due_date: dueDate,
        importance: importance,
        estimated_hours: hours,
        dependencies: dependencies
    };

    tasksData.push(newTask);
    renderTaskList();
    handleClearForm();
}

function handleClearForm() {
    clearFieldErrors();
    document.getElementById('task-title').value = '';
    document.getElementById('task-due-date').value = '';
    document.getElementById('task-importance').value = '5';
    document.getElementById('task-hours').value = '2';
    document.getElementById('task-dependencies').value = '';
}

function handleLoadJSON() {
    clearFieldErrors();
    const jsonInput = document.getElementById('json-input').value.trim();

    if (!jsonInput) {
        setFieldError('json-input', 'Paste JSON data');
        return;
    }

    try {
        const parsedData = JSON.parse(jsonInput);

        if (!Array.isArray(parsedData)) {
            setFieldError('json-input', 'Must be array: [{...}]');
            return;
        }

        const newTasks = parsedData.map((task, index) => ({
            id: task.id || (tasksData.length > 0 ? Math.max(...tasksData.map(t => t.id)) : 0) + index + 1,
            title: task.title || 'Untitled',
            due_date: task.due_date || new Date().toISOString().split('T')[0],
            importance: task.importance || 5,
            estimated_hours: task.estimated_hours || 2,
            dependencies: task.dependencies || []
        }));

        tasksData.push(...newTasks);
        renderTaskList();
        document.getElementById('json-input').value = '';
    } catch (error) {
        setFieldError('json-input', 'Invalid JSON: ' + error.message);
    }
}

function renderTaskList() {
    const taskList = document.getElementById('task-list');
    const deleteAllBtn = document.getElementById('delete-all-btn');

    if (tasksData.length === 0) {
        taskList.innerHTML = '<p class="empty-state-small">No tasks added</p>';
        deleteAllBtn.style.display = 'none';
        return;
    }

    deleteAllBtn.style.display = 'block';

    taskList.innerHTML = tasksData.map(task => `
        <div class="task-item-compact">
            <div class="task-item-title-compact">${escapeHtml(task.title)}</div>
            <div class="task-item-details-compact">
                ${task.due_date} | ${task.importance}/10 | ${task.estimated_hours}h
            </div>
            <button class="task-item-remove-compact" onclick="removeTask(${task.id})" title="Remove task">X</button>
        </div>
    `).join('');
}

function removeTask(taskId) {
    tasksData = tasksData.filter(t => t.id !== taskId);
    renderTaskList();
}

async function handleAnalyze() {
    if (tasksData.length === 0) {
        showResultsError('Add at least one task to analyze');
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
            showResultsError(data.message || data.error || 'Analysis failed');
            return;
        }

        displayResults(data);
    } catch (error) {
        showLoading(false);
        showResultsError('Network error: ' + error.message);
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
        resultsContainer.innerHTML = '<p class="empty-state-large">No results</p>';
        return;
    }

    resultsContainer.innerHTML = data.results.map((task, index) => {
        const priorityClass = task.priority_level.toLowerCase();

        return `
            <div class="task-card-compact ${priorityClass}">
                <div class="task-card-header-compact">
                    <div class="task-card-title-compact">${escapeHtml(task.title)}</div>
                    <span class="priority-badge-compact ${priorityClass}">${task.priority_level}</span>
                </div>

                <div class="task-card-explanation-compact">
                    ${escapeHtml(task.explanation)}
                </div>

                <div class="task-card-metrics-compact">
                    <div class="metric-compact">
                        <div class="metric-label-compact">Priority</div>
                        <div class="metric-value-compact">${task.priority_score}</div>
                    </div>
                    <div class="metric-compact">
                        <div class="metric-label-compact">Urgency</div>
                        <div class="metric-value-compact">${task.urgency}</div>
                    </div>
                    <div class="metric-compact">
                        <div class="metric-label-compact">Importance</div>
                        <div class="metric-value-compact">${task.importance_score}</div>
                    </div>
                    <div class="metric-compact">
                        <div class="metric-label-compact">Effort</div>
                        <div class="metric-value-compact">${task.effort > 0 ? '+' : ''}${task.effort}</div>
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

function showResultsError(message) {
    const resultsContainer = document.getElementById('results-container');
    resultsContainer.innerHTML = `
        <div style="background-color: rgba(220, 38, 38, 0.1); border-left: 3px solid #dc2626; padding: 12px; border-radius: 6px; color: #dc2626; font-size: 0.9rem;">
            <strong>Error:</strong> ${escapeHtml(message)}
        </div>
    `;
}

function clearResults() {
    document.getElementById('results-container').innerHTML = '<p class="empty-state-large">Results will appear here</p>';
    document.getElementById('results-summary').classList.add('hidden');
}

async function handleSuggest() {
    if (tasksData.length === 0) {
        showResultsError('Add at least one task to get suggestions');
        return;
    }

    const strategy = document.getElementById('strategy-select').value;

    showLoading(true);
    clearResults();

    try {
        const response = await fetch(`${API_BASE_URL}/suggest/`, {
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
            showResultsError(data.message || data.error || 'Failed to get suggestions');
            return;
        }

        displaySuggestions(data);
    } catch (error) {
        showLoading(false);
        showResultsError('Network error: ' + error.message);
        console.error('API Error:', error);
    }
}

function displaySuggestions(data) {
    const resultsContainer = document.getElementById('results-container');
    const summaryDiv = document.getElementById('results-summary');
    const summaryText = document.getElementById('summary-text');

    summaryText.textContent = `Top ${data.suggestions.length} recommended tasks using "${data.strategy}" strategy`;
    summaryDiv.classList.remove('hidden');

    if (data.suggestions.length === 0) {
        resultsContainer.innerHTML = '<p class="empty-state-large">No suggestions available</p>';
        return;
    }

    resultsContainer.innerHTML = data.suggestions.map((task, index) => {
        const priorityClass = task.priority.toLowerCase();
        const rank = index + 1;

        return `
            <div class="task-card-compact ${priorityClass}">
                <div class="task-card-header-compact">
                    <div class="task-card-title-compact">#${rank} - ${escapeHtml(task.title)}</div>
                    <span class="priority-badge-compact ${priorityClass}">${task.priority}</span>
                </div>

                <div class="task-card-explanation-compact">
                    ${escapeHtml(task.reason)}
                </div>

                <div class="task-card-metrics-compact">
                    <div class="metric-compact">
                        <div class="metric-label-compact">Priority Score</div>
                        <div class="metric-value-compact">${task.priority_score}</div>
                    </div>
                    <div class="metric-compact">
                        <div class="metric-label-compact">Due Date</div>
                        <div class="metric-value-compact">${task.due_date}</div>
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function handleDeleteAll() {
    if (tasksData.length === 0) {
        return;
    }

    if (confirm(`Are you sure you want to delete all ${tasksData.length} tasks?`)) {
        tasksData = [];
        renderTaskList();
        clearResults();
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
