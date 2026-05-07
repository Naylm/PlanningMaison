// ==========================================
// Initialisation Globale
// ==========================================
// ==========================================
// Recherche globale
// ==========================================
function initGlobalSearch() {
    const input = document.getElementById('globalSearch');
    const box = document.getElementById('searchResults');
    if (!input || !box) return;
    let timer;
    const ICONS = { events: '📅', tasks: '✅', notes: '📝', shopping: '🛒' };
    const LABELS = { events: 'Calendrier', tasks: 'Tâches', notes: 'Notes', shopping: 'Courses' };
    const URLS = { events: '/calendar', tasks: '/tasks', notes: '/notes', shopping: '/shopping' };

    input.addEventListener('input', () => {
        clearTimeout(timer);
        const q = input.value.trim();
        if (q.length < 2) { box.style.display = 'none'; return; }
        timer = setTimeout(async () => {
            const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
            if (!res.ok) return;
            const data = await res.json();
            const total = Object.values(data).reduce((a, b) => a + b.length, 0);
            if (total === 0) {
                box.innerHTML = '<div style="padding:0.8rem 1rem; color:var(--sidebar-text); font-size:0.88rem;">Aucun résultat</div>';
                box.style.display = 'block';
                return;
            }
            let html = '';
            for (const [key, items] of Object.entries(data)) {
                if (!items.length) continue;
                html += `<div style="padding:4px 12px; font-size:0.72rem; font-weight:700; color:var(--sidebar-text); text-transform:uppercase; letter-spacing:0.05em; margin-top:4px;">${ICONS[key]} ${LABELS[key]}</div>`;
                for (const item of items) {
                    const label = item.title || item.name;
                    const sub = item.start ? ` <span style="color:var(--sidebar-text);font-size:0.75rem;">${item.start.slice(0,10)}</span>` : (item.is_done ? ' ✅' : '') + (item.points ? ` ⭐${item.points}` : '');
                    html += `<a href="${URLS[key]}" style="display:block; padding:6px 14px; font-size:0.88rem; color:var(--text-color); text-decoration:none; border-radius:6px; margin:1px 4px;" onmouseover="this.style.background='rgba(128,128,128,0.1)'" onmouseout="this.style.background=''">${label}${sub}</a>`;
                }
            }
            box.innerHTML = html;
            box.style.display = 'block';
        }, 250);
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('#headerSearch')) box.style.display = 'none';
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
    initSidebarToggle();
    initGlobalSearch();

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
// Avatar Picker
// ==========================================
const AVATAR_CATEGORIES = [
    { label: 'Neutre', emojis: ['👤','🧑','🧑🏻','🧑🏼','🧑🏽','🧑🏾','🧑🏿'] },
    { label: 'Enfants', emojis: [
        '👶','👶🏻','👶🏼','👶🏽','👶🏾','👶🏿',
        '🧒','🧒🏻','🧒🏼','🧒🏽','🧒🏾','🧒🏿',
        '👦','👦🏻','👦🏼','👦🏽','👦🏾','👦🏿',
        '👧','👧🏻','👧🏼','🏽','👧🏾','👧🏿'
    ]},
    { label: 'Hommes', emojis: [
        '👨','👨🏻','🏼','👨🏽','👨🏾','👨🏿',
        '👨‍🦰','👨🏻‍🦰','👨🏼‍🦰','👨🏽‍🦰','👨🏾‍🦰','👨🏿‍🦰',
        '👨‍🦱','👨🏻‍🦱','👨🏼‍🦱','👨🏽‍🦱','👨🏾‍🦱','👨🏿‍🦱',
        '👨‍🦳','👨🏻‍🦳','👨🏼‍🦳','👨🏽‍🦳','👨🏾‍🦳','👨🏿‍🦳',
        '👨‍🦲','👨🏻‍🦲','👨🏼‍🦲','👨🏽‍🦲','👨🏾‍🦲','👨🏿‍🦲',
        '🧔','🧔🏻','🧔🏼','🧔🏽','🧔🏾','🧔🏿',
        '🧔‍♂️','🧔🏻‍♂️','🧔🏼‍♂️','🧔🏽‍♂️','🧔🏾‍♂️','🧔🏿‍♂️',
        '👱‍♂️','👱🏻‍♂️','👱🏼‍♂️','👱🏽‍♂️','👱🏾‍♂️','👱🏿‍♂️'
    ]},
    { label: 'Femmes', emojis: [
        '👩','👩🏻','👩🏼','👩🏽','👩🏾','👩🏿',
        '👩‍🦰','👩🏻‍🦰','👩🏼‍🦰','👩🏽‍🦰','👩🏾‍🦰','👩🏿‍🦰',
        '👩‍🦱','👩🏻‍🦱','👩🏼‍🦱','👩🏽‍🦱','👩🏾‍🦱','👩🏿‍🦱',
        '👩‍🦳','👩🏻‍🦳','👩🏼‍🦳','👩🏽‍🦳','👩🏾‍🦳','👩🏿‍🦳',
        '👩‍🦲','👩🏻‍🦲','👩🏼‍🦲','👩🏽‍🦲','👩🏾‍🦲','👩🏿‍🦲',
        '👱‍♀️','👱🏻‍♀️','👱🏼‍♀️','👱🏽‍♀️','👱🏾‍♀️','👱🏿‍♀️'
    ]},
    { label: 'Seniors', emojis: [
        '🧓','🧓🏻','🧓🏼','🧓🏽','🧓🏾','🧓🏿',
        '👴','👴🏻','👴🏼','👴🏽','👴🏾','👴🏿',
        '👵','👵🏻','👵🏼','👵🏽','👵🏾','👵🏿'
    ]},
    { label: 'Visages', emojis: ['😀','😄','😁','😎','🥸','🤓','😍','🥰','😇','🤩','😜','🤪','😏','🙂','😊','😂','🤣','😆'] },
    { label: 'Animaux', emojis: ['🐶','🐱','🐻','🐼','🐨','🦊','🐯','🦁','🐸','🐧','🦄','🐲','🐺','🦝','🐮','🐰','🐹','🐭'] },
    { label: 'Divers', emojis: ['⚽','🏀','🎮','🎸','🎵','🎨','📚','🌟','❤️','🔥','💎','🏆','🚀','🌈','👑','🎯','🍕','🌙'] }
];

function initAvatarPicker(prefix) {
    const grid = document.getElementById(`${prefix}EmojiGrid`);
    if (!grid || grid.dataset.init) return;
    grid.dataset.init = '1';

    AVATAR_CATEGORIES.forEach((cat, ci) => {
        const label = document.createElement('div');
        label.className = 'emoji-section-label';
        label.textContent = cat.label;
        if (ci === 0) label.style.borderTop = 'none';
        grid.appendChild(label);

        cat.emojis.forEach(emoji => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.textContent = emoji;
            btn.title = emoji;
            btn.onclick = () => {
                grid.querySelectorAll('button').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                const input = document.getElementById(prefix === 'add' ? 'memberAvatar' : 'editMemberAvatar');
                if (input) input.value = emoji;
                updateAvatarPreview(prefix);
            };
            grid.appendChild(btn);
        });
    });
}

window.switchAvatarTab = function(prefix, tab, btnEl) {
    document.querySelectorAll(`#${prefix === 'add' ? 'memberModal' : 'editMemberModal'} .avatar-tab`).forEach(b => b.classList.remove('active'));
    btnEl.classList.add('active');
    document.getElementById(`${prefix}EmojiPanel`).style.display = tab === 'emoji' ? '' : 'none';
    document.getElementById(`${prefix}PhotoPanel`).style.display = tab === 'photo' ? '' : 'none';
    if (tab === 'emoji') initAvatarPicker(prefix);
}

window.updateAvatarPreview = function(prefix) {
    const preview = document.getElementById(`${prefix}AvatarPreview`);
    const photoData = document.getElementById(prefix === 'add' ? 'memberPhotoData' : 'editMemberPhotoData')?.value;
    const emoji = document.getElementById(prefix === 'add' ? 'memberAvatar' : 'editMemberAvatar')?.value || '👤';
    const color = document.getElementById(prefix === 'add' ? 'memberColor' : 'editMemberColor')?.value || '#3498db';
    if (!preview) return;
    if (photoData) {
        preview.innerHTML = `<img src="${photoData}" style="width:100%;height:100%;object-fit:cover;">`;
        preview.style.background = 'transparent';
    } else {
        preview.innerHTML = emoji;
        preview.style.background = color;
    }
}

window.handlePhotoUpload = function(prefix, input) {
    const file = input.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (e) => {
        // Redimensionner à max 200x200 pour ne pas surcharger la DB
        const img = new Image();
        img.onload = () => {
            const canvas = document.createElement('canvas');
            const MAX = 200;
            let w = img.width, h = img.height;
            if (w > h) { if (w > MAX) { h = h * MAX / w; w = MAX; } }
            else { if (h > MAX) { w = w * MAX / h; h = MAX; } }
            canvas.width = w; canvas.height = h;
            canvas.getContext('2d').drawImage(img, 0, 0, w, h);
            const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
            const hiddenInput = document.getElementById(prefix === 'add' ? 'memberPhotoData' : 'editMemberPhotoData');
            if (hiddenInput) hiddenInput.value = dataUrl;
            updateAvatarPreview(prefix);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

window.clearPhoto = function(prefix) {
    const hiddenInput = document.getElementById(prefix === 'add' ? 'memberPhotoData' : 'editMemberPhotoData');
    if (hiddenInput) hiddenInput.value = '';
    const fileInput = document.getElementById(prefix === 'add' ? 'memberPhoto' : 'editMemberPhoto');
    if (fileInput) fileInput.value = '';
    updateAvatarPreview(prefix);
}

// Sync la couleur avec l'aperçu en temps réel
document.addEventListener('input', (e) => {
    if (e.target.id === 'memberColor') updateAvatarPreview('add');
    if (e.target.id === 'editMemberColor') updateAvatarPreview('edit');
});

// Init grilles emoji à l'ouverture des modals
const _origOpenModal = window.openModal;
window.openModal = function(modalId) {
    _origOpenModal(modalId);
    if (modalId === 'memberModal') { initAvatarPicker('add'); updateAvatarPreview('add'); }
    if (modalId === 'editMemberModal') { initAvatarPicker('edit'); }
}

// ==========================================
// API & Fonctions Membres
// ==========================================
async function handleAddMember(e) {
    e.preventDefault();
    const name = document.getElementById('memberName').value;
    const color = document.getElementById('memberColor').value;
    const avatar = document.getElementById('memberAvatar').value;
    const photo = document.getElementById('memberPhotoData')?.value || '';

    const res = await fetch('/api/members', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color, avatar, photo: photo || null })
    });
    if (res.ok) location.reload();
}

window.editMember = function(id, name, color, avatar, photo) {
    document.getElementById('editMemberId').value = id;
    document.getElementById('editMemberName').value = name;
    document.getElementById('editMemberColor').value = color;
    document.getElementById('editMemberAvatar').value = avatar;
    const photoInput = document.getElementById('editMemberPhotoData');
    if (photoInput) photoInput.value = photo || '';
    openModal('editMemberModal');
    // Mettre à jour l'aperçu après ouverture
    setTimeout(() => updateAvatarPreview('edit'), 50);
    // Si photo existante, basculer sur l'onglet photo
    if (photo) {
        const photoTab = document.getElementById('editPhotoTab');
        if (photoTab) switchAvatarTab('edit', 'photo', photoTab);
    }
}

async function handleUpdateMember(e) {
    e.preventDefault();
    const id = document.getElementById('editMemberId').value;
    const name = document.getElementById('editMemberName').value;
    const color = document.getElementById('editMemberColor').value;
    const avatar = document.getElementById('editMemberAvatar').value;
    const photo = document.getElementById('editMemberPhotoData')?.value || '';

    const res = await fetch(`/api/members/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color, avatar, photo: photo || null })
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
        timeZone: 'local',
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
            const members = info.event.extendedProps.members_info || [];
            const names = members.length > 0 ? members.map(m => m.name).join(', ') : 'Tous';
            info.el.setAttribute('title', `${info.event.title}\n� ${names}\n⏰ ${start}`);
        },
        dateClick: function(info) {
            const clicked = info.dateStr;
            const startInput = document.getElementById('eventStart');
            if (startInput) {
                startInput.value = clicked.length === 10 ? clicked + 'T08:00' : clicked.slice(0,16);
            }
            openModal('eventModal');
        },
        eventContent: function(arg) {
            const props = arg.event.extendedProps;
            const members = props.members_info || [];
            let avatarHtml = '';
            if (members.length > 0) {
                avatarHtml = '<span class="fc-event-avatars">' +
                    members.map(m => `<span title="${m.name}">${m.avatar}</span>`).join('') +
                    '</span>';
            }
            return { html: `<span class="fc-event-title">${arg.event.title}${avatarHtml}</span>` };
        },
        eventClick: function(info) {
            const start = info.event.start.toLocaleTimeString('fr-FR', {hour: '2-digit', minute:'2-digit'});
            const props = info.event.extendedProps;
            const members = props.members_info || [];
            const memberName = members.length > 0 ? members.map(m => m.name).join(', ') : 'Tous';

            document.getElementById('detailTitle').innerText = info.event.title;
            document.getElementById('detailMember').innerText = memberName;
            document.getElementById('detailTime').innerText = start;

            const avatarsEl = document.getElementById('detailMembersAvatars');
            if (avatarsEl) {
                avatarsEl.innerHTML = members.map(m =>
                    `<span style="display:inline-flex;align-items:center;gap:4px;padding:3px 8px;border-radius:20px;background:${m.color}22;border:1.5px solid ${m.color};font-size:0.8rem;">
                        <span style="font-size:1rem">${m.avatar}</span> ${m.name}
                    </span>`
                ).join('');
            }
            
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
                
                function toLocalInput(d) {
                    const off = d.getTimezoneOffset() * 60000;
                    return new Date(d - off).toISOString().slice(0, 16);
                }
                document.getElementById('editEventStart').value = toLocalInput(new Date(event.start));
                if (event.end) {
                    document.getElementById('editEventEnd').value = toLocalInput(new Date(event.end));
                } else {
                    document.getElementById('editEventEnd').value = '';
                }

                setCheckedMemberIds('editEventMemberChecks', props.member_ids || []);
                closeModal('eventDetailModal');
                openModal('editEventModal');
            };
            
            openModal('eventDetailModal');
        }
    });
    calendar.render();
    window.fcCalendar = calendar;
}

// ── Helpers multi-membres ───────────────────────────────
window.getCheckedMemberIds = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];
    return [...container.querySelectorAll('input.event-member-cb:checked')].map(cb => parseInt(cb.value));
}

window.toggleAllMembers = function(containerId, allCb) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.querySelectorAll('input.event-member-cb').forEach(cb => {
        cb.checked = false;
    });
}

window.syncAllCheckbox = function(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const allCb = container.querySelector('input[type="checkbox"]:not(.event-member-cb)');
    const anyChecked = container.querySelectorAll('input.event-member-cb:checked').length > 0;
    if (allCb) allCb.checked = !anyChecked;
}

function setCheckedMemberIds(containerId, ids) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const allCb = container.querySelector('input[type="checkbox"]:not(.event-member-cb)');
    container.querySelectorAll('input.event-member-cb').forEach(cb => {
        cb.checked = ids.includes(parseInt(cb.value));
    });
    if (allCb) allCb.checked = ids.length === 0;
}
// ────────────────────────────────────────────────────────

function localInputToUTC(val) {
    if (!val) return '';
    return new Date(val).toISOString();
}

async function handleAddEvent(e) {
    e.preventDefault();
    const title = document.getElementById('eventTitle').value;
    const start_time = localInputToUTC(document.getElementById('eventStart').value);
    const end_time = localInputToUTC(document.getElementById('eventEnd').value);
    const member_ids = getCheckedMemberIds('eventMemberChecks');

    const res = await fetch('/api/events', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, start_time, end_time, member_ids })
    });
    if (res.ok) {
        if(window.fcCalendar) window.fcCalendar.refetchEvents();
        closeModal('eventModal');
        document.getElementById('addEventForm').reset();
        setCheckedMemberIds('eventMemberChecks', []);
        showToast('Événement ajouté au calendrier');
    }
}

async function handleUpdateEvent(e) {
    e.preventDefault();
    const id = document.getElementById('editEventId').value;
    const title = document.getElementById('editEventTitle').value;
    const start_time = localInputToUTC(document.getElementById('editEventStart').value);
    const end_time = localInputToUTC(document.getElementById('editEventEnd').value);
    const member_ids = getCheckedMemberIds('editEventMemberChecks');

    const res = await fetch(`/api/events/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, start_time, end_time, member_ids })
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

window.resetPoints = async function() {
    const confirmed = await customConfirm(
        '⚠️ Réinitialiser les points',
        'Cela va supprimer toutes les tâches terminées et remettre le classement à zéro. Cette action est irréversible.'
    );
    if (!confirmed) return;
    const res = await fetch('/api/tasks/reset-points', { method: 'POST' });
    if (res.ok) {
        showToast('Points réinitialisés ✅');
        setTimeout(() => location.reload(), 800);
    }
}

window.triggerBackup = async function() {
    showToast('Sauvegarde en cours...', 'info');
    const res = await fetch('/api/backup/now', { method: 'POST' });
    if (res.ok) {
        const data = await res.json();
        showToast(`✅ Sauvegarde créée (${data.copies} copie${data.copies > 1 ? 's' : ''} conservée${data.copies > 1 ? 's' : ''})`);
    } else {
        showToast('Erreur lors de la sauvegarde', 'danger');
    }
};

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
