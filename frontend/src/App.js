// Function to add a task
async function addTask() {
    const input = document.getElementById('taskInput');
    const text = input.value;
    if (!text) return;

    // Send data to the Backend Container (NOT Lambda)
    const response = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task: text })
    });

    if (response.ok) {
        input.value = '';
        loadTasks(); // Refresh list
    }
}

// Function to load tasks
async function loadTasks() {
    const response = await fetch('/api/todos');
    const tasks = await response.json();
    const list = document.getElementById('taskList');
    list.innerHTML = '';
    tasks.forEach(todo => {
        const li = document.createElement('li');
        li.textContent = todo.task;
        list.appendChild(li);
    });
}

// Load tasks on startup
window.onload = loadTasks;
