// ==========================================
// Initialisation Globale
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initSidebarToggle();

    if (document.getElementById('shoppingList')) initShoppingList();
    if (document.getElementById('calendar')) initCalendar();
    
    setupFormListener('addMemberForm', handleAddMember);
    setupFormListener('editMemberForm', handleUpdateMember);
    setupFormListener('addNoteForm', handleAddNote);
    setupFormListener('editNoteForm', handleUpdateNote);
    setupFormListener('addShoppingForm', handleAddShoppingItem);
    setupFormListener('addEventForm', handleAddEvent);
    setupFormListener('editEventForm', handleUpdateEvent);
    setupFormListener('addTaskForm', handleAddTask);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal.show').forEach(m => closeModal(m.id));
        }
    });
});

// ==========================================
// Dark Mode
// ==========================================
function initDarkMode() {
    const btn = document.getElementById('darkToggle');
    if (!btn) return;
    const saved = localStorage.getItem('darkMode');
    if (saved === '1') {
        document.body.classList.add('dark-mode');
        btn.textContent = '☀️';
    }
    btn.addEventListener('click', () => {
        const isDark = document.body.classList.toggle('dark-mode');
        btn.textContent = isDark ? '☀️' : '🌙';
        localStorage.setItem('darkMode', isDark ? '1' : '0');
    });
}

// ==========================================
// Sidebar Toggle (mobile)
// ==========================================
function initSidebarToggle() {
    const toggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    if (!toggle || !sidebar) return;

    toggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
        overlay.classList.toggle('show');
    });
    overlay.addEventListener('click', () => {
        sidebar.classList.remove('open');
        overlay.classList.remove('show');
    });
}

// ==========================================
// Confetti
// ==========================================
function spawnConfetti(x, y) {
    const colors = ['#f6ad55','#48bb78','#4a90e2','#f56565','#9f7aea','#ed64a6'];
    for (let i = 0; i < 12; i++) {
        const el = document.createElement('div');
        el.className = 'confetti-piece';
        el.style.left = (x + (Math.random() - 0.5) * 80) + 'px';
        el.style.top = (y + (Math.random() - 0.5) * 40) + 'px';
        el.style.background = colors[Math.floor(Math.random() * colors.length)];
        el.style.transform = `rotate(${Math.random()*360}deg)`;
        document.body.appendChild(el);
        setTimeout(() => el.remove(), 900);
    }
}

function setupFormListener(id, handler) {
    const form = document.getElementById(id);
    if (form) {
        form.removeEventListener('submit', handler);
        form.addEventListener('submit', handler);
    }
}

// ==========================================
// Notifications (Toasts) & Confirmation
// ==========================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    let icon = type === 'success' ? 'check-circle' : 'exclamation-circle';
    if (type === 'danger') icon = 'trash';

    toast.innerHTML = `<i class="fas fa-${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        if(toast.parentElement) {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(100%)';
            setTimeout(() => toast.remove(), 300);
        }
    }, 2700);
}

function customConfirm(title, message) {
    return new Promise((resolve) => {
        const modal = document.getElementById('confirmModal');
        const titleEl = document.getElementById('confirmTitle');
        const messageEl = document.getElementById('confirmMessage');
        const yesBtn = document.getElementById('confirmBtnYes');
        const noBtn = document.getElementById('confirmBtnNo');

        titleEl.innerText = title;
        messageEl.innerText = message;
        
        openModal('confirmModal');

        const handleYes = () => {
            closeModal('confirmModal');
            resolve(true);
            cleanup();
        };

        const handleNo = () => {
            closeModal('confirmModal');
            resolve(false);
            cleanup();
        };

        function cleanup() {
            yesBtn.removeEventListener('click', handleYes);
            noBtn.removeEventListener('click', handleNo);
        }

        yesBtn.addEventListener('click', handleYes);
        noBtn.addEventListener('click', handleNo);
    });
}

// ==========================================
// Modals
// ==========================================
window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.add('show');
    const firstInput = modal.querySelector('input, textarea');
    if(firstInput) firstInput.focus();
}

window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (!modal) return;
    modal.classList.remove('show');
}

window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        closeModal(event.target.id);
    }
}

// ==========================================
// API & Fonctions Membres
// ==========================================
async function handleAddMember(e) {
    e.preventDefault();
    const name = document.getElementById('memberName').value;
    const color = document.getElementById('memberColor').value;
    const avatar = document.getElementById('memberAvatar').value;

    const res = await fetch('/api/members', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color, avatar })
    });
    if (res.ok) location.reload();
}

window.editMember = function(id, name, color, avatar) {
    document.getElementById('editMemberId').value = id;
    document.getElementById('editMemberName').value = name;
    document.getElementById('editMemberColor').value = color;
    document.getElementById('editMemberAvatar').value = avatar;
    openModal('editMemberModal');
}

async function handleUpdateMember(e) {
    e.preventDefault();
    const id = document.getElementById('editMemberId').value;
    const name = document.getElementById('editMemberName').value;
    const color = document.getElementById('editMemberColor').value;
    const avatar = document.getElementById('editMemberAvatar').value;

    const res = await fetch(`/api/members/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color, avatar })
    });
    if (res.ok) location.reload();
}

window.deleteMember = async function(id) {
    const confirmed = await customConfirm("Suppression Membre", "Voulez-vous vraiment supprimer ce membre ? Cela effacera aussi ses événements.");
    if (confirmed) {
        const res = await fetch(`/api/members/${id}`, { method: 'DELETE' });
        if (res.ok) location.reload();
    }
}

// ==========================================
// API & Fonctions Liste de Courses
// ==========================================
function initShoppingList() {
    document.querySelectorAll('.todo-item input[type="checkbox"]').forEach(box => {
        box.addEventListener('change', handleToggleItem);
    });
}

async function handleToggleItem(e) {
    const listItem = e.target.closest('.todo-item');
    const id = listItem.dataset.id;
    await fetch(`/api/shopping/${id}`, { method: 'PUT' });
    if (e.target.checked) listItem.classList.add('completed');
    else listItem.classList.remove('completed');
}

async function handleAddShoppingItem(e) {
    e.preventDefault();
    const input = document.getElementById('newShoppingItem');
    if (!input) return;
    const name = input.value;

    const res = await fetch('/api/shopping', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (res.ok) {
        const item = await res.json();
        const ul = document.getElementById('shoppingList');
        if (ul) {
            const li = document.createElement('li');
            li.className = 'todo-item';
            li.dataset.id = item.id;
            li.innerHTML = `
                <input type="checkbox" id="item-${item.id}">
                <label for="item-${item.id}">${item.name}</label>
                <button class="delete-btn" onclick="deleteShoppingItem(${item.id})"><i class="fas fa-trash"></i></button>
            `;
            ul.appendChild(li);
            li.querySelector('input').addEventListener('change', handleToggleItem);
        }
        input.value = '';
        input.focus();
        showToast(`Article ajouté`);
    }
}

window.deleteShoppingItem = async function(id) {
    const res = await fetch(`/api/shopping/${id}`, { method: 'DELETE' });
    if(res.ok) {
        const item = document.querySelector(`.todo-item[data-id="${id}"]`);
        if (item) item.remove();
        showToast('Article supprimé', 'danger');
    }
}

// ==========================================
// API & Fonctions Notes
// ==========================================
async function handleAddNote(e) {
    e.preventDefault();
    const title = document.getElementById('noteTitle').value;
    const content = document.getElementById('noteContent').value;
    const color = document.getElementById('noteColor').value;

    const res = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, color })
    });
    if (res.ok) location.reload();
}

window.editNote = function(id, title, content, color) {
    document.getElementById('editNoteId').value = id;
    document.getElementById('editNoteTitle').value = title;
    document.getElementById('editNoteContent').value = content;
    document.getElementById('editNoteColor').value = color;
    openModal('editNoteModal');
}

async function handleUpdateNote(e) {
    e.preventDefault();
    const id = document.getElementById('editNoteId').value;
    const title = document.getElementById('editNoteTitle').value;
    const content = document.getElementById('editNoteContent').value;
    const color = document.getElementById('editNoteColor').value;

    const res = await fetch(`/api/notes/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, content, color })
    });
    if (res.ok) location.reload();
}

window.deleteNote = async function(id) {
    const confirmed = await customConfirm("Suppression Note", "Êtes-vous sûr de vouloir supprimer cette note ?");
    if(confirmed) {
        const res = await fetch(`/api/notes/${id}`, { method: 'DELETE' });
        if(res.ok) location.reload();
    }
}

// ==========================================
// Initialisation Calendrier (FullCalendar)
// ==========================================
function initCalendar() {
    const calendarEl = document.getElementById('calendar');
    if (!calendarEl) return;

    const calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        locale: 'fr',
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek'
        },
        buttonText: { today: "Aujourd'hui", month: 'Mois', week: 'Semaine' },
        height: 'auto',
        events: '/api/events',
        eventDidMount: function(info) {
            const start = info.event.start.toLocaleTimeString('fr-FR', {hour: '2-digit', minute:'2-digit'});
            const member = info.event.extendedProps.member_name || 'Tous';
            const avatar = info.event.extendedProps.member_avatar || '🏡';
            info.el.setAttribute('title', `${avatar} ${info.event.title}\n👤 Membre : ${member}\n⏰ Heure : ${start}`);
        },
        dateClick: function(info) {
            const clicked = info.dateStr;
            const startInput = document.getElementById('eventStart');
            if (startInput) {
                startInput.value = clicked.length === 10 ? clicked + 'T08:00' : clicked.slice(0,16);
            }
            openModal('eventModal');
        },
        eventClick: function(info) {
            const start = info.event.start.toLocaleTimeString('fr-FR', {hour: '2-digit', minute:'2-digit'});
            const member = info.event.extendedProps.member_name || 'Tous';
            const avatar = info.event.extendedProps.member_avatar || '🏡';
            
            document.getElementById('detailTitle').innerText = `${avatar} ${info.event.title}`;
            document.getElementById('detailMember').innerText = member;
            document.getElementById('detailTime').innerText = start;
            
            const deleteBtn = document.getElementById('deleteEventBtn');
            deleteBtn.onclick = async () => {
                const confirmed = await customConfirm("Suppression Événement", "Voulez-vous supprimer cet événement ?");
                if(confirmed) {
                    const res = await fetch(`/api/events/${info.event.id}`, { method: 'DELETE' });
                    if(res.ok) {
                        info.event.remove();
                        closeModal('eventDetailModal');
                        showToast('Événement supprimé', 'danger');
                    }
                }
            };
            
            const editBtn = document.getElementById('editEventBtn');
            editBtn.onclick = () => {
                const event = info.event;
                document.getElementById('editEventId').value = event.id;
                document.getElementById('editEventTitle').value = event.title;
                
                // Formater la date pour datetime-local (YYYY-MM-DDTHH:mm)
                const start = new Date(event.start);
                start.setMinutes(start.getMinutes() - start.getTimezoneOffset());
                document.getElementById('editEventStart').value = start.toISOString().slice(0, 16);
                
                if (event.end) {
                    const end = new Date(event.end);
                    end.setMinutes(end.getMinutes() - end.getTimezoneOffset());
                    document.getElementById('editEventEnd').value = end.toISOString().slice(0, 16);
                } else {
                    document.getElementById('editEventEnd').value = '';
                }
                
                // Note: member_id n'est pas directement dans event, mais on peut le stocker dans extendedProps
                // Si non présent, on essaie de matcher le nom du membre (moins précis)
                // Idéalement, l'API devrait renvoyer le member_id dans extendedProps
                // Je vais mettre à jour l'API get_events pour inclure member_id
                document.getElementById('editEventMember').value = event.extendedProps.member_id || '';
                
                closeModal('eventDetailModal');
                openModal('editEventModal');
            };
            
            openModal('eventDetailModal');
        }
    });
    calendar.render();
    window.fcCalendar = calendar;
}

async function handleAddEvent(e) {
    e.preventDefault();
    const title = document.getElementById('eventTitle').value;
    const start_time = document.getElementById('eventStart').value;
    const end_time = document.getElementById('eventEnd').value;
    const member_id = document.getElementById('eventMember').value;

    const res = await fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, start_time, end_time, member_id })
    });
    if (res.ok) {
        if(window.fcCalendar) window.fcCalendar.refetchEvents();
        closeModal('eventModal');
        showToast('Événement ajouté au calendrier');
    }
}

async function handleUpdateEvent(e) {
    e.preventDefault();
    const id = document.getElementById('editEventId').value;
    const title = document.getElementById('editEventTitle').value;
    const start_time = document.getElementById('editEventStart').value;
    const end_time = document.getElementById('editEventEnd').value;
    const member_id = document.getElementById('editEventMember').value;

    const res = await fetch(`/api/events/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, start_time, end_time, member_id })
    });
    if (res.ok) {
        if(window.fcCalendar) window.fcCalendar.refetchEvents();
        closeModal('editEventModal');
        showToast('Événement mis à jour');
    }
}

// ==========================================
// API & Fonctions Tâches
// ==========================================
async function handleAddTask(e) {
    e.preventDefault();
    const title = document.getElementById('taskTitle').value.trim();
    const points = document.querySelector('input[name="taskPoints"]:checked')?.value || 1;
    const assigned_to = document.getElementById('taskMember')?.value || '';

    const res = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, points: parseInt(points), assigned_to })
    });
    if (res.ok) {
        closeModal('taskModal');
        showToast('Tâche ajoutée !');
        location.reload();
    }
}

window.completeTask = async function(taskId, memberSelectId, btnEl) {
    const member_id = document.getElementById(memberSelectId)?.value || '';
    if (!member_id) {
        showToast('Choisis qui a fait la tâche !', 'warning');
        document.getElementById(memberSelectId)?.focus();
        return;
    }
    const res = await fetch(`/api/tasks/${taskId}/complete`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ member_id: parseInt(member_id) })
    });
    if (res.ok) {
        const rect = btnEl.getBoundingClientRect();
        spawnConfetti(rect.left + rect.width / 2, rect.top);
        showToast('Tâche accomplie ! 🎉');
        setTimeout(() => location.reload(), 600);
    }
}

window.uncompleteTask = async function(taskId) {
    const res = await fetch(`/api/tasks/${taskId}/uncomplete`, { method: 'PUT' });
    if (res.ok) location.reload();
}

window.deleteTask = async function(taskId) {
    const confirmed = await customConfirm('Supprimer la tâche', 'Voulez-vous vraiment supprimer cette tâche ?');
    if (confirmed) {
        const res = await fetch(`/api/tasks/${taskId}`, { method: 'DELETE' });
        if (res.ok) {
            const el = document.querySelector(`.task-item[data-id="${taskId}"]`);
            if (el) el.remove();
            showToast('Tâche supprimée', 'danger');
        }
    }
}
