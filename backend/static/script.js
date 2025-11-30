const API_BASE_URL = 'https://task-analyzer-2827.onrender.com/api/tasks';

let tasksData = [];
let completedTasks = new Set();

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
    
    // Get selected dependencies from checkboxes
    const dependencyCheckboxes = document.querySelectorAll('.dependency-checkbox:checked');
    const dependencies = Array.from(dependencyCheckboxes).map(cb => parseInt(cb.value));

    let isValid = true;

    if (!title) {
        setFieldError('task-title', 'Title required');
        isValid = false;
    }

    if (!dueDate) {
        setFieldError('task-due-date', 'Date required');
        isValid = false;
    } else {
        const selectedDate = new Date(dueDate);
        const today = new Date();
        today.setHours(0, 0, 0, 0); // Reset time part
        
        // Calculate date 30 days ago
        const minDate = new Date(today);
        minDate.setDate(today.getDate() - 30);
        
        if (selectedDate < minDate) {
            setFieldError('task-due-date', 'Date cannot be older than 30 days');
            isValid = false;
        }
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

    const newTask = {
        id: tasksData.length > 0 ? Math.max(...tasksData.map(t => t.id)) + 1 : 1,
        title: title,
        due_date: dueDate,
        importance: importance,
        estimated_hours: hours,
        dependencies: dependencies
    };

    tasksData.push(newTask);
    updateDependencyDropdown();
    renderTaskList();
    handleClearForm();
}

function handleClearForm() {
    clearFieldErrors();
    document.getElementById('task-title').value = '';
    document.getElementById('task-due-date').value = '';
    document.getElementById('task-importance').value = '5';
    document.getElementById('task-hours').value = '2';
    
    // Uncheck all dependency checkboxes
    document.querySelectorAll('.dependency-checkbox').forEach(cb => {
        cb.checked = false;
    });
}

function updateDependencyDropdown() {
    const container = document.getElementById('dependencies-container');
    
    // Only show non-completed tasks in dependency list
    const availableTasks = tasksData.filter(task => !completedTasks.has(task.id));
    
    if (availableTasks.length === 0) {
        container.innerHTML = '<p class="empty-dependencies">No tasks available yet</p>';
        return;
    }
    
    container.innerHTML = availableTasks.map((task, index) => {
        return `
            <label class="dependency-item">
                <input type="checkbox" class="dependency-checkbox" value="${task.id}">
                <span class="dependency-text">${index + 1}. ${task.title}</span>
            </label>
        `;
    }).join('');
}

function handleLoadJSON() {
    clearFieldErrors();
    const jsonInput = document.getElementById('json-input').value.trim();

    if (!jsonInput) {
        setFieldError('json-input', 'Please paste JSON data first');
        return;
    }

    try {
        const parsedData = JSON.parse(jsonInput);

        if (!Array.isArray(parsedData)) {
            setFieldError('json-input', 'Format Error: Root must be an array [...]');
            return;
        }

        if (parsedData.length === 0) {
            setFieldError('json-input', 'Array is empty. Add at least one task object.');
            return;
        }

        // Validate first item structure
        if (typeof parsedData[0] !== 'object' || parsedData[0] === null) {
             setFieldError('json-input', 'Format Error: Array must contain objects {...}');
             return;
        }

        const newTasks = parsedData.map((task, index) => ({
            id: task.id || (tasksData.length > 0 ? Math.max(...tasksData.map(t => t.id)) : 0) + index + 1,
            title: task.title || 'Untitled Task',
            due_date: task.due_date || new Date().toISOString().split('T')[0],
            importance: task.importance || 5,
            estimated_hours: task.estimated_hours || 2,
            dependencies: task.dependencies || []
        }));

        tasksData.push(...newTasks);
        updateDependencyDropdown();
        renderTaskList();
        document.getElementById('json-input').value = '';
        
        // Show success feedback (optional but nice)
        // alert(`Successfully loaded ${newTasks.length} tasks!`);
        
    } catch (error) {
        // Show specific syntax error from JSON.parse
        setFieldError('json-input', `Invalid JSON: ${error.message}`);
    }
}

function renderTaskList() {
    const taskList = document.getElementById('task-list');

    if (tasksData.length === 0) {
        taskList.innerHTML = '<p class="empty-state-small">No tasks added</p>';
        updateDependencyDropdown();
        return;
    }

    taskList.innerHTML = tasksData.map((task, index) => {
        const isCompleted = completedTasks.has(task.id);
        const dependencyText = task.dependencies && task.dependencies.length > 0 
            ? ` | Depends on: ${task.dependencies.join(', ')}`
            : '';
        
        return `
        <div class="task-item-compact ${isCompleted ? 'completed' : ''}">
            <input 
                type="checkbox" 
                class="task-checkbox" 
                ${isCompleted ? 'checked' : ''}
                onchange="toggleTaskCompletion(${task.id})"
            >
            <span class="task-serial">${index + 1}.</span>
            <div class="task-item-title-compact">${escapeHtml(task.title)}</div>
            <div class="task-item-details-compact">
                ${task.due_date} | ${task.importance}/10 | ${task.estimated_hours}h${dependencyText}
            </div>
            <button class="task-item-remove-compact" onclick="removeTask(${task.id})" title="Remove task">×</button>
        </div>
    `;
    }).join('');
}

function toggleTaskCompletion(taskId) {
    if (completedTasks.has(taskId)) {
        completedTasks.delete(taskId);
    } else {
        completedTasks.add(taskId);
        
        // Remove completed task from all dependencies
        tasksData.forEach(task => {
            if (task.dependencies) {
                task.dependencies = task.dependencies.filter(depId => depId !== taskId);
            }
        });
    }
    
    updateDependencyDropdown();
    renderTaskList();
    
    // Re-analyze if results were showing
    const summaryDiv = document.getElementById('results-summary');
    const isAnalysisShowing = !summaryDiv.classList.contains('hidden');
    
    if (isAnalysisShowing && tasksData.length > 0) {
        // Small delay to ensure DOM updates
        setTimeout(() => handleAnalyze(), 100);
    }
}

function removeTask(taskId) {
    tasksData = tasksData.filter(t => t.id !== taskId);
    completedTasks.delete(taskId);
    
    // Remove this task from other tasks' dependencies
    tasksData.forEach(task => {
        if (task.dependencies) {
            task.dependencies = task.dependencies.filter(depId => depId !== taskId);
        }
    });
    
    updateDependencyDropdown();
    renderTaskList();
    
    // Re-analyze if results were showing
    const summaryDiv = document.getElementById('results-summary');
    const isAnalysisShowing = !summaryDiv.classList.contains('hidden');
    
    if (isAnalysisShowing && tasksData.length > 0) {
        // Small delay to ensure DOM updates
        setTimeout(() => handleAnalyze(), 100);
    } else if (tasksData.length === 0) {
        clearResults();
    }
}

async function handleAnalyze() {
    // Only analyze non-completed tasks
    const activeTasks = tasksData.filter(task => !completedTasks.has(task.id));
    
    if (activeTasks.length === 0) {
        showResultsError('No active tasks to analyze. All tasks are completed.');
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
                tasks: activeTasks,
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

async function handleSuggest() {
    // Only suggest from non-completed tasks
    const activeTasks = tasksData.filter(task => !completedTasks.has(task.id));
    
    if (activeTasks.length === 0) {
        showResultsError('No active tasks for suggestions. All tasks are completed.');
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
                tasks: activeTasks,
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
                    <span class="task-serial-result">#${index + 1}</span>
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

        return `
            <div class="task-card-compact ${priorityClass}">
                <div class="task-card-header-compact">
                    <span class="task-serial-result">#${index + 1}</span>
                    <div class="task-card-title-compact">${escapeHtml(task.title)}</div>
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

function showLoading(isLoading) {
    const spinner = document.getElementById('loading-spinner');
    const analyzeBtn = document.getElementById('analyze-btn');
    const suggestBtn = document.getElementById('suggest-btn');

    if (isLoading) {
        spinner.classList.remove('hidden');
        if (analyzeBtn) analyzeBtn.disabled = true;
        if (suggestBtn) suggestBtn.disabled = true;
    } else {
        spinner.classList.add('hidden');
        if (analyzeBtn) analyzeBtn.disabled = false;
        if (suggestBtn) suggestBtn.disabled = false;
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

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
