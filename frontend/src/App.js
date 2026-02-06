const API_URL = '/api/todos';

// 1. Display Time & Date (Attached to window not needed, runs on load)
function updateDate() {
    const now = new Date();
    const dateString = now.toLocaleDateString('en-US', { 
        weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
    });
    const dateEl = document.getElementById('currentDate');
    if (dateEl) dateEl.innerText = dateString;
}

// 2. Quick Notes Template -> EXPORT TO WINDOW
window.fillTemplate = function(text) {
    document.getElementById('taskInput').value = text;
}

// 3. Fetch & Render Tasks
async function loadTasks() {
    try {
        const res = await fetch(API_URL);
        if (!res.ok) throw new Error(`HTTP error! status: ${res.status}`);
        
        const tasks = await res.json();
        const list = document.getElementById('taskList');
        if (!list) return; // Guard clause
        
        list.innerHTML = '';
        
        let pending = 0;
        tasks.forEach(task => {
            if(!task.completed) pending++;
            
            const isOverdue = task.due_date && new Date(task.due_date) < new Date();
            const dateClass = isOverdue ? "text-red-500 font-bold" : "text-gray-400";
            const displayDate = task.due_date ? new Date(task.due_date).toLocaleString() : '';

            // Note: onclick calls window.toggleComplete and window.deleteTask
            list.innerHTML += `
                <li class="p-4 hover:bg-gray-50 flex justify-between items-start group transition">
                    <div class="flex items-start gap-3">
                        <button onclick="window.toggleComplete(${task.id}, ${task.completed})" class="mt-1 text-xl ${task.completed ? 'text-green-500' : 'text-gray-300 hover:text-indigo-500'}">
                            <i class="fas ${task.completed ? 'fa-check-circle' : 'fa-circle'}"></i>
                        </button>
                        <div>
                            <p class="font-medium ${task.completed ? 'line-through text-gray-400' : 'text-gray-800'}">${task.content}</p>
                            ${task.notes ? `<p class="text-xs text-gray-500 mt-1"><i class="fas fa-sticky-note mr-1"></i>${task.notes}</p>` : ''}
                            ${displayDate ? `<p class="text-xs ${dateClass} mt-1"><i class="far fa-clock mr-1"></i>${displayDate}</p>` : ''}
                        </div>
                    </div>
                    <button onclick="window.deleteTask(${task.id})" class="text-gray-300 hover:text-red-500 opacity-0 group-hover:opacity-100 transition">
                        <i class="fas fa-trash"></i>
                    </button>
                </li>
            `;
        });
        const countEl = document.getElementById('pendingCount');
        if (countEl) countEl.innerText = pending;
    } catch (error) {
        console.error("Error loading tasks:", error);
    }
}

// 4. Add Task -> EXPORT TO WINDOW
window.addTask = async function() {
    const content = document.getElementById('taskInput').value;
    const notes = document.getElementById('noteInput').value;
    const due_date = document.getElementById('dateInput').value;
    
    if (!content) return alert("Task cannot be empty!");

    try {
        await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content, notes, due_date })
        });
        
        document.getElementById('taskInput').value = '';
        document.getElementById('noteInput').value = '';
        document.getElementById('dateInput').value = ''; 
        loadTasks();
    } catch (error) {
        console.error("Error adding task:", error);
    }
}

// 5. Delete Task -> EXPORT TO WINDOW
window.deleteTask = async function(id) {
    if(!confirm("Are you sure?")) return;
    await fetch(`${API_URL}/${id}`, { method: 'DELETE' });
    loadTasks();
}

// 6. Complete Task -> EXPORT TO WINDOW
window.toggleComplete = async function(id, currentStatus) {
    await fetch(`${API_URL}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !currentStatus })
    });
    loadTasks();
}

// Initialize on load
window.onload = function() {
    updateDate();
    loadTasks();
};