from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
import shutil
import threading
import time
from sqlalchemy import func

DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

def _text_color(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        return '#222222'
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return '#222222' if luminance > 0.5 else '#ffffff'

app.jinja_env.filters['text_color'] = _text_color

from datetime import timedelta as _timedelta
app.jinja_env.globals['enumerate'] = enumerate
app.jinja_env.globals['timedelta'] = _timedelta
app.jinja_env.globals['timedelta_7'] = _timedelta(days=6)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'fredo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
def _load_secret_key():
    env_file = os.path.join(basedir, '.env')
    key = os.environ.get('SECRET_KEY')
    if key:
        return key
    if os.path.exists(env_file):
        with open(env_file) as _f:
            for line in _f:
                line = line.strip()
                if line.startswith('SECRET_KEY='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    import secrets as _sec
    key = _sec.token_hex(32)
    with open(env_file, 'a') as _f:
        _f.write(f'\nSECRET_KEY={key}\n')
    return key

app.config['SECRET_KEY'] = _load_secret_key()

db = SQLAlchemy(app)

# ==========================================
# Models
# ==========================================

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    color = db.Column(db.String(20), default='#3498db')
    avatar = db.Column(db.String(10), default='👤')
    photo = db.Column(db.Text, nullable=True)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    color = db.Column(db.String(20), default='#ffffff')
    archived = db.Column(db.Boolean, default=False)

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    member = db.relationship('Member', backref=db.backref('logs', lazy=True))

class MonthlyScore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)
    member = db.relationship('Member', backref=db.backref('scores', lazy=True))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    member_ids = db.Column(db.Text, nullable=True)
    recurrence = db.Column(db.String(10), nullable=True)  # none | daily | weekly | monthly
    recurrence_end = db.Column(db.DateTime, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=True)
    member = db.relationship('Member', backref=db.backref('events', lazy=True))

    def get_member_ids(self):
        import json
        if self.member_ids:
            try: return json.loads(self.member_ids)
            except: pass
        return [self.member_id] if self.member_id else []

    def set_member_ids(self, ids):
        import json
        ids = [i for i in ids if i]
        self.member_ids = json.dumps(ids) if ids else None
        self.member_id = ids[0] if ids else None

class Meal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)  # 0=Lundi … 6=Dimanche
    slot = db.Column(db.String(5), nullable=False)  # 'midi' ou 'soir'
    week = db.Column(db.String(8), nullable=False)  # 'YYYY-WNN'
    title = db.Column(db.String(150), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    ingredients = db.Column(db.Text, nullable=True)  # une ligne = un ingrédient

class FamilyMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    pinned = db.Column(db.Boolean, default=False)
    member = db.relationship('Member', backref=db.backref('messages', lazy=True))

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=1)
    assigned_to = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    done_by = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    done_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    room = db.Column(db.String(50), nullable=True)
    recurrence = db.Column(db.String(10), nullable=True)
    assignee = db.relationship('Member', foreign_keys=[assigned_to], backref=db.backref('assigned_tasks', lazy=True))
    doer = db.relationship('Member', foreign_keys=[done_by], backref=db.backref('done_tasks', lazy=True))

# ==========================================
# Routes
# ==========================================

@app.route('/')
def index():
    from datetime import date as _date
    now = datetime.now(timezone.utc)
    upcoming_events = Event.query.filter(Event.start_time >= now).order_by(Event.start_time.asc()).limit(3).all()
    recent_notes = Note.query.order_by(Note.created_at.desc()).limit(3).all()
    shopping_items = ShoppingItem.query.filter_by(is_completed=False).limit(5).all()
    pending_tasks = Task.query.filter_by(is_done=False).order_by(Task.points.desc()).limit(5).all()
    leaderboard = _get_leaderboard()
    today = _date.today()
    week_key = today.strftime('%G-W%V')
    today_meals = Meal.query.filter_by(week=week_key, day=today.weekday()).order_by(Meal.slot).all()
    recent_messages = FamilyMessage.query.order_by(FamilyMessage.pinned.desc(), FamilyMessage.created_at.desc()).limit(3).all()
    return render_template('dashboard.html', events=upcoming_events, notes=recent_notes, shopping=shopping_items,
        pending_tasks=pending_tasks, leaderboard=leaderboard, today_meals=today_meals, today=today,
        recent_messages=recent_messages)

@app.route('/menu')
def menu_page():
    from datetime import date as _date
    import datetime as _dt
    req_week = request.args.get('week')
    today = _date.today()
    if req_week:
        week_key = req_week
        year, wnum = int(req_week.split('-W')[0]), int(req_week.split('-W')[1])
        week_start = _dt.date.fromisocalendar(year, wnum, 1)
    else:
        week_key = today.strftime('%G-W%V')
        iso = today.isocalendar()
        week_start = _dt.date.fromisocalendar(iso[0], iso[1], 1)
    prev_week = (week_start - _dt.timedelta(weeks=1)).strftime('%G-W%V')
    next_week = (week_start + _dt.timedelta(weeks=1)).strftime('%G-W%V')
    meals = Meal.query.filter_by(week=week_key).all()
    meals_map = {(m.day, m.slot): m for m in meals}
    days = ['Lundi','Mardi','Mercredi','Jeudi','Vendredi','Samedi','Dimanche']
    return render_template('menu.html', week_key=week_key, week_start=week_start,
        prev_week=prev_week, next_week=next_week, meals_map=meals_map,
        days=days, today=today)

@app.route('/members')
def members_page():
    members = Member.query.all()
    return render_template('members.html', members=members)

@app.route('/calendar')
def calendar_page():
    members = Member.query.all()
    return render_template('calendar.html', members=members)

@app.route('/shopping')
def shopping_page():
    shopping_items = ShoppingItem.query.all()
    return render_template('shopping.html', shopping_items=shopping_items)

@app.route('/notes')
def notes_page():
    notes = Note.query.filter_by(archived=False).order_by(Note.created_at.desc()).all()
    archived = Note.query.filter_by(archived=True).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=notes, archived=archived)

@app.route('/tasks')
def tasks_page():
    members = Member.query.all()
    pending = Task.query.filter_by(is_done=False).order_by(Task.points.desc()).all()
    done = Task.query.filter_by(is_done=True).order_by(Task.done_at.desc()).limit(20).all()
    leaderboard = _get_leaderboard()
    return render_template('tasks.html', members=members, pending=pending, done=done, leaderboard=leaderboard, now=datetime.now(timezone.utc))

# API: Membres
@app.route('/api/members', methods=['POST'])
def add_member():
    data = request.json
    new_member = Member(
        name=data['name'],
        color=data.get('color', '#3498db'),
        avatar=data.get('avatar', '👤'),
        photo=data.get('photo') or None
    )
    db.session.add(new_member)
    db.session.commit()
    return jsonify({'id': new_member.id, 'name': new_member.name, 'color': new_member.color, 'avatar': new_member.avatar, 'photo': new_member.photo})

@app.route('/api/members/<int:member_id>', methods=['PUT'])
def update_member(member_id):
    data = request.json
    member = db.session.get(Member, member_id)
    if not member: return jsonify({'error': 'not found'}), 404
    member.name = data['name']
    member.color = data['color']
    member.avatar = data['avatar']
    if 'photo' in data:
        member.photo = data['photo'] or None
    db.session.commit()
    return jsonify({'id': member.id, 'name': member.name, 'color': member.color, 'avatar': member.avatar, 'photo': member.photo})

@app.route('/api/members/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
    member = Member.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    return jsonify({'success': True})

def _log(action, member_id=None):
    db.session.add(ActivityLog(action=action, member_id=member_id))

# API: Liste de courses
@app.route('/api/shopping', methods=['POST'])
def add_shopping_item():
    data = request.json
    new_item = ShoppingItem(name=data['name'], category=data.get('category') or None)
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'id': new_item.id, 'name': new_item.name, 'is_completed': new_item.is_completed, 'category': new_item.category})

@app.route('/api/shopping/<int:item_id>', methods=['PUT'])
def toggle_shopping_item(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    item.is_completed = not item.is_completed
    db.session.commit()
    return jsonify({'id': item.id, 'is_completed': item.is_completed})

@app.route('/api/shopping/<int:item_id>', methods=['DELETE'])
def delete_shopping_item(item_id):
    item = ShoppingItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({'success': True})

# API: Notes
@app.route('/api/notes', methods=['POST'])
def add_note():
    data = request.json
    new_note = Note(title=data['title'], content=data['content'], color=data.get('color', '#ffffff'))
    db.session.add(new_note)
    db.session.commit()
    return jsonify({'id': new_note.id, 'title': new_note.title, 'content': new_note.content, 'color': new_note.color})

@app.route('/api/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    data = request.json
    note = Note.query.get_or_404(note_id)
    note.title = data['title']
    note.content = data['content']
    note.color = data['color']
    db.session.commit()
    return jsonify({'id': note.id, 'title': note.title, 'content': note.content, 'color': note.color})

@app.route('/api/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notes/<int:note_id>/archive', methods=['PUT'])
def archive_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.archived = True
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/notes/<int:note_id>/unarchive', methods=['PUT'])
def unarchive_note(note_id):
    note = Note.query.get_or_404(note_id)
    note.archived = False
    db.session.commit()
    return jsonify({'success': True})

# API: Tâches
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.order_by(Task.is_done.asc(), Task.points.desc()).all()
    return jsonify([_task_to_dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    due = None
    if data.get('due_date'):
        try: due = datetime.fromisoformat(data['due_date'])
        except: pass
    task = Task(
        title=data['title'],
        points=int(data.get('points', 1)),
        assigned_to=data.get('assigned_to') or None,
        due_date=due,
        room=data.get('room') or None,
        recurrence=data.get('recurrence') or None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(_task_to_dict(task)), 201

@app.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    task = db.session.get(Task, task_id)
    if not task: return jsonify({'error': 'not found'}), 404
    task.title = data.get('title', task.title)
    task.points = int(data.get('points', task.points))
    task.assigned_to = data.get('assigned_to') or None
    if 'due_date' in data:
        try: task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        except: task.due_date = None
    if 'room' in data:
        task.room = data.get('room') or None
    if 'recurrence' in data:
        task.recurrence = data.get('recurrence') or None
    db.session.commit()
    return jsonify(_task_to_dict(task))


@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    data = request.json
    task = Task.query.get_or_404(task_id)
    task.is_done = True
    task.done_by = data.get('member_id') or None
    task.done_at = datetime.now(timezone.utc)
    doer = Member.query.get(task.done_by) if task.done_by else None
    doer_name = doer.name if doer else 'Quelqu’un'
    pts_label = 'pts' if task.points > 1 else 'pt'
    _log(f"✅ {doer_name} a accompli \"{task.title}\" (+{task.points} {pts_label})", task.done_by)
    # Auto-recréation si tâche récurrente
    if task.recurrence:
        from datetime import timedelta
        next_due = None
        if task.due_date:
            if task.recurrence == 'daily':
                next_due = task.due_date + timedelta(days=1)
            elif task.recurrence == 'weekly':
                next_due = task.due_date + timedelta(weeks=1)
            elif task.recurrence == 'monthly':
                next_due = task.due_date + timedelta(days=30)
        new_task = Task(
            title=task.title,
            points=task.points,
            assigned_to=task.assigned_to,
            room=task.room,
            recurrence=task.recurrence,
            due_date=next_due
        )
        db.session.add(new_task)
    db.session.commit()
    return jsonify(_task_to_dict(task))

@app.route('/api/tasks/<int:task_id>/uncomplete', methods=['PUT'])
def uncomplete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.is_done = False
    task.done_by = None
    task.done_at = None
    db.session.commit()
    return jsonify(_task_to_dict(task))

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/tasks/reset-points', methods=['POST'])
def reset_points():
    now = datetime.now(timezone.utc)
    for m in Member.query.all():
        pts = db.session.query(func.sum(Task.points)).filter(
            Task.done_by == m.id, Task.is_done == True,
            func.strftime('%Y-%m', Task.done_at) == now.strftime('%Y-%m')
        ).scalar() or 0
        if pts > 0:
            existing = MonthlyScore.query.filter_by(member_id=m.id, year=now.year, month=now.month).first()
            if existing:
                existing.points = pts
            else:
                db.session.add(MonthlyScore(member_id=m.id, year=now.year, month=now.month, points=pts))
    Task.query.filter_by(is_done=True).delete()
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/leaderboard/history')
def leaderboard_history():
    scores = db.session.query(MonthlyScore).order_by(MonthlyScore.year.desc(), MonthlyScore.month.desc()).limit(60).all()
    result = {}
    for s in scores:
        key = f"{s.year}-{s.month:02d}"
        if key not in result:
            result[key] = []
        result[key].append({'member_id': s.member_id, 'name': s.member.name, 'avatar': s.member.avatar, 'color': s.member.color, 'points': s.points})
    for key in result:
        result[key].sort(key=lambda x: x['points'], reverse=True)
    return jsonify(result)

@app.route('/api/search')
def search():
    q = request.args.get('q', '').strip()
    if len(q) < 2:
        return jsonify({'events': [], 'tasks': [], 'notes': [], 'shopping': []})
    like = f'%{q}%'
    events = Event.query.filter(Event.title.ilike(like)).limit(10).all()
    tasks = Task.query.filter(Task.title.ilike(like)).limit(10).all()
    notes = Note.query.filter((Note.title.ilike(like)) | (Note.content.ilike(like))).limit(10).all()
    shopping = ShoppingItem.query.filter(ShoppingItem.name.ilike(like)).limit(10).all()
    return jsonify({
        'events': [{'id': e.id, 'title': e.title, 'start': e.start_time.isoformat()} for e in events],
        'tasks': [{'id': t.id, 'title': t.title, 'is_done': t.is_done, 'points': t.points} for t in tasks],
        'notes': [{'id': n.id, 'title': n.title, 'color': n.color} for n in notes],
        'shopping': [{'id': s.id, 'name': s.name, 'is_completed': s.is_completed} for s in shopping]
    })

@app.route('/api/activity')
def get_activity():
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(50).all()
    return jsonify([{'id': l.id, 'action': l.action, 'member': l.member.name if l.member else None,
                     'avatar': l.member.avatar if l.member else '🏡',
                     'created_at': l.created_at.isoformat()} for l in logs])

@app.route('/api/leaderboard')
def get_leaderboard():
    return jsonify(_get_leaderboard())

@app.route('/api/poll')
def poll_data():
    shopping_count = ShoppingItem.query.filter_by(is_completed=False).count()
    shopping_last = db.session.query(func.max(ShoppingItem.id)).scalar() or 0
    tasks_pending = Task.query.filter_by(is_done=False).count()
    tasks_last = db.session.query(func.max(Task.id)).scalar() or 0
    tasks_done_last = db.session.query(func.max(Task.done_at)).filter(Task.is_done == True).scalar()
    notes_count = Note.query.filter_by(archived=False).count()
    notes_last = db.session.query(func.max(Note.id)).scalar() or 0
    members_last = db.session.query(func.max(Member.id)).scalar() or 0
    leaderboard_sig = db.session.query(func.sum(Task.points)).filter(Task.is_done == True).scalar() or 0
    return jsonify({
        'shopping': {'count': shopping_count, 'last_id': shopping_last},
        'tasks': {'pending': tasks_pending, 'last_id': tasks_last, 'last_done': str(tasks_done_last)},
        'notes': {'count': notes_count, 'last_id': notes_last},
        'members': {'last_id': members_last},
        'leaderboard': {'sig': leaderboard_sig},
    })

def _get_leaderboard():
    now = datetime.now(timezone.utc)
    members = Member.query.all()
    result = []
    for m in members:
        pts = db.session.query(func.sum(Task.points)).filter(
            Task.done_by == m.id,
            Task.is_done == True,
            func.strftime('%Y-%m', Task.done_at) == now.strftime('%Y-%m')
        ).scalar() or 0
        total_pts = db.session.query(func.sum(Task.points)).filter(
            Task.done_by == m.id,
            Task.is_done == True
        ).scalar() or 0
        result.append({'id': m.id, 'name': m.name, 'avatar': m.avatar, 'color': m.color, 'photo': m.photo, 'points_month': pts, 'points_total': total_pts})
    result.sort(key=lambda x: x['points_month'], reverse=True)
    return result

def _task_to_dict(task):
    return {
        'id': task.id,
        'title': task.title,
        'points': task.points,
        'is_done': task.is_done,
        'assigned_to': task.assigned_to,
        'assignee_name': task.assignee.name if task.assignee else None,
        'assignee_avatar': task.assignee.avatar if task.assignee else None,
        'done_by': task.done_by,
        'doer_name': task.doer.name if task.doer else None,
        'done_at': task.done_at.isoformat() if task.done_at else None,
        'due_date': task.due_date.isoformat() if task.due_date else None,
        'room': task.room,
        'recurrence': task.recurrence or ''
    }

def _event_occurrences(event, all_members, horizon_days=180):
    from datetime import timedelta as _td
    ids = event.get_member_ids()
    members_info = [all_members[i] for i in ids if i in all_members]
    color = members_info[0].color if members_info else '#4a90e2'
    names = ', '.join(m.name for m in members_info) if members_info else 'Tous'
    avatars = ' '.join(m.avatar for m in members_info) if members_info else '🏡'
    duration = event.end_time - event.start_time
    rec = event.recurrence
    results = []
    if not rec or rec == 'none':
        results.append(event.start_time)
    else:
        horizon = datetime.utcnow() + _td(days=horizon_days)
        end_limit = min(event.recurrence_end, horizon) if event.recurrence_end else horizon
        cur = event.start_time
        steps = {'daily': _td(days=1), 'weekly': _td(weeks=1)}
        count = 0
        while cur <= end_limit and count < 365:
            results.append(cur)
            count += 1
            if rec == 'daily': cur += _td(days=1)
            elif rec == 'weekly': cur += _td(weeks=1)
            elif rec == 'monthly':
                m2 = cur.month % 12 + 1
                y2 = cur.year + (1 if cur.month == 12 else 0)
                try: cur = cur.replace(year=y2, month=m2)
                except: break
            else: break
    out = []
    for start in results:
        out.append({
            'id': event.id,
            'title': event.title,
            'start': start.isoformat() + 'Z',
            'end': (start + duration).isoformat() + 'Z',
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'member_ids': ids, 'member_id': event.member_id,
                'member_name': names, 'member_avatar': avatars,
                'recurrence': rec or 'none',
                'members_info': [{'id': m.id, 'name': m.name, 'avatar': m.avatar, 'color': m.color} for m in members_info]
            }
        })
    return out

# API: Événements (Calendrier)
@app.route('/api/events', methods=['GET'])
def get_events():
    events = Event.query.filter_by(parent_id=None).all()
    all_members = {m.id: m for m in Member.query.all()}
    events_data = []
    for event in events:
        events_data.extend(_event_occurrences(event, all_members))
    return jsonify(events_data)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else start_time
    ids = [int(i) for i in data.get('member_ids', []) if i]
    if not ids and data.get('member_id'):
        ids = [int(data['member_id'])]
    rec = data.get('recurrence') or None
    rec_end = datetime.fromisoformat(data['recurrence_end']) if data.get('recurrence_end') else None
    new_event = Event(title=data['title'], start_time=start_time, end_time=end_time,
                      recurrence=rec, recurrence_end=rec_end)
    new_event.set_member_ids(ids)
    db.session.add(new_event)
    db.session.commit()
    color = new_event.member.color if new_event.member else '#4a90e2'
    return jsonify({'id': new_event.id, 'title': new_event.title,
        'start': new_event.start_time.isoformat() + 'Z', 'end': new_event.end_time.isoformat() + 'Z',
        'backgroundColor': color, 'borderColor': color, 'recurrence': rec})

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.json
    event = Event.query.get_or_404(event_id)
    event.title = data['title']
    event.start_time = datetime.fromisoformat(data['start_time'])
    event.end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else event.start_time
    ids = [int(i) for i in data.get('member_ids', []) if i]
    if not ids and data.get('member_id'):
        ids = [int(data['member_id'])]
    event.set_member_ids(ids)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return jsonify({'success': True})

# API: Menu
def _meal_dict(m):
    return {'id': m.id, 'day': m.day, 'slot': m.slot, 'week': m.week,
            'title': m.title, 'notes': m.notes, 'ingredients': m.ingredients or ''}

@app.route('/api/meals', methods=['GET'])
def get_meals():
    week = request.args.get('week')
    if not week:
        from datetime import date as _date
        week = _date.today().strftime('%G-W%V')
    meals = Meal.query.filter_by(week=week).all()
    return jsonify([_meal_dict(m) for m in meals])

@app.route('/api/meals', methods=['POST'])
def add_meal():
    data = request.json
    existing = Meal.query.filter_by(week=data['week'], day=data['day'], slot=data['slot']).first()
    if existing:
        existing.title = data['title']
        existing.notes = data.get('notes', '')
        existing.ingredients = data.get('ingredients', '')
        db.session.commit()
        m = existing
    else:
        m = Meal(day=int(data['day']), slot=data['slot'], week=data['week'],
                 title=data['title'], notes=data.get('notes', ''), ingredients=data.get('ingredients', ''))
        db.session.add(m)
        db.session.commit()
    return jsonify(_meal_dict(m))

@app.route('/api/meals/<int:meal_id>', methods=['PUT'])
def update_meal(meal_id):
    data = request.json
    m = Meal.query.get_or_404(meal_id)
    m.title = data['title']
    m.notes = data.get('notes', m.notes)
    m.ingredients = data.get('ingredients', m.ingredients or '')
    db.session.commit()
    return jsonify(_meal_dict(m))

@app.route('/api/meals/<int:meal_id>/to-cart', methods=['POST'])
def meal_to_cart(meal_id):
    m = Meal.query.get_or_404(meal_id)
    if not m.ingredients:
        return jsonify({'added': 0})
    lines = [l.strip() for l in m.ingredients.splitlines() if l.strip()]
    added = 0
    for line in lines:
        item = ShoppingItem(name=line)
        db.session.add(item)
        added += 1
    db.session.commit()
    return jsonify({'added': added})

@app.route('/api/meals/<int:meal_id>', methods=['DELETE'])
def delete_meal(meal_id):
    m = Meal.query.get_or_404(meal_id)
    db.session.delete(m)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/meals/copy-week', methods=['POST'])
def copy_week():
    data = request.json
    src = data.get('from_week')
    dst = data.get('to_week')
    if not src or not dst:
        return jsonify({'error': 'from_week and to_week required'}), 400
    src_meals = Meal.query.filter_by(week=src).all()
    copied = 0
    for sm in src_meals:
        existing = Meal.query.filter_by(week=dst, day=sm.day, slot=sm.slot).first()
        if existing:
            existing.title = sm.title
            existing.notes = sm.notes
            existing.ingredients = sm.ingredients
        else:
            db.session.add(Meal(week=dst, day=sm.day, slot=sm.slot,
                                title=sm.title, notes=sm.notes, ingredients=sm.ingredients))
        copied += 1
    db.session.commit()
    return jsonify({'copied': copied})

def _msg_dict(m):
    return {
        'id': m.id,
        'content': m.content,
        'member_id': m.member_id,
        'member_name': m.member.name if m.member else 'Maison',
        'member_avatar': m.member.avatar if m.member else '🏡',
        'member_color': m.member.color if m.member else '#2eb49e',
        'created_at': m.created_at.isoformat() if m.created_at else None,
        'pinned': m.pinned
    }

@app.route('/messages')
def messages_page():
    members = Member.query.all()
    messages = FamilyMessage.query.order_by(FamilyMessage.pinned.desc(), FamilyMessage.created_at.desc()).limit(100).all()
    return render_template('messages.html', members=members, messages=messages)

@app.route('/api/messages', methods=['GET'])
def get_messages():
    msgs = FamilyMessage.query.order_by(FamilyMessage.pinned.desc(), FamilyMessage.created_at.desc()).limit(50).all()
    return jsonify([_msg_dict(m) for m in msgs])

@app.route('/api/messages', methods=['POST'])
def add_message():
    data = request.json
    content = (data.get('content') or '').strip()[:300]
    if not content:
        return jsonify({'error': 'empty'}), 400
    msg = FamilyMessage(content=content, member_id=data.get('member_id') or None)
    db.session.add(msg)
    db.session.commit()
    return jsonify(_msg_dict(msg)), 201

@app.route('/api/messages/<int:msg_id>/pin', methods=['PUT'])
def pin_message(msg_id):
    msg = db.session.get(FamilyMessage, msg_id)
    if not msg:
        return jsonify({'error': 'not found'}), 404
    msg.pinned = not msg.pinned
    db.session.commit()
    return jsonify(_msg_dict(msg))

@app.route('/api/messages/<int:msg_id>', methods=['DELETE'])
def delete_message(msg_id):
    msg = db.session.get(FamilyMessage, msg_id)
    if not msg:
        return jsonify({'error': 'not found'}), 404
    db.session.delete(msg)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/sw.js')
def service_worker():
    return send_file(os.path.join(basedir, 'static', 'sw.js'), mimetype='application/javascript')

@app.route('/api/backup')
def backup_db():
    try:
        return send_file(os.path.join(basedir, 'fredo.db'), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ==========================================
# Sauvegarde automatique journalière
# ==========================================
BACKUP_DIR = os.path.join(basedir, 'backups')
BACKUP_KEEP = 7
BACKUP_INTERVAL = 24 * 3600  # secondes

def _do_backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    src = os.path.join(basedir, 'fredo.db')
    if not os.path.exists(src):
        return
    stamp = datetime.now().strftime('%Y-%m-%d_%Hh%M')
    dst = os.path.join(BACKUP_DIR, f'fredo_{stamp}.db')
    shutil.copy2(src, dst)
    # Garder seulement les N plus récentes
    copies = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith('fredo_') and f.endswith('.db')]
    )
    for old in copies[:-BACKUP_KEEP]:
        os.remove(os.path.join(BACKUP_DIR, old))
    print(f'[Backup] {dst}')

def _backup_loop():
    # Attendre 1 min au démarrage avant le premier backup
    time.sleep(60)
    while True:
        try:
            _do_backup()
        except Exception as e:
            print(f'[Backup] Erreur : {e}')
        time.sleep(BACKUP_INTERVAL)

@app.route('/api/backup/now', methods=['POST'])
def manual_backup():
    try:
        _do_backup()
        copies = sorted(os.listdir(BACKUP_DIR)) if os.path.exists(BACKUP_DIR) else []
        return jsonify({'success': True, 'copies': len(copies), 'latest': copies[-1] if copies else None})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backup/list')
def list_backups():
    if not os.path.exists(BACKUP_DIR):
        return jsonify([])
    copies = sorted(
        [f for f in os.listdir(BACKUP_DIR) if f.startswith('fredo_') and f.endswith('.db')],
        reverse=True
    )
    return jsonify([{'name': f, 'size': os.path.getsize(os.path.join(BACKUP_DIR, f))} for f in copies])

def _auto_migrate():
    import sqlite3 as _sql
    db_path = os.path.join(basedir, 'fredo.db')
    if not os.path.exists(db_path):
        return
    con = _sql.connect(db_path)
    cur = con.cursor()
    migrations = [
        'ALTER TABLE shopping_item ADD COLUMN category VARCHAR(50)',
        'ALTER TABLE note ADD COLUMN archived BOOLEAN DEFAULT 0',
        'ALTER TABLE event ADD COLUMN recurrence VARCHAR(10)',
        'ALTER TABLE event ADD COLUMN recurrence_end DATETIME',
        'ALTER TABLE event ADD COLUMN parent_id INTEGER',
        'ALTER TABLE task ADD COLUMN due_date DATETIME',
        'ALTER TABLE task ADD COLUMN room VARCHAR(50)',
        'ALTER TABLE task ADD COLUMN recurrence VARCHAR(10)',
    ]
    # Nouvelle table messages
    cur.execute('''
        CREATE TABLE IF NOT EXISTS family_message (
            id INTEGER PRIMARY KEY,
            content TEXT NOT NULL,
            member_id INTEGER REFERENCES member(id),
            created_at DATETIME,
            pinned BOOLEAN DEFAULT 0
        )
    ''')
    for sql in migrations:
        try:
            cur.execute(sql)
        except Exception:
            pass
    for tbl, cols in [
        ('activity_log', 'id INTEGER PRIMARY KEY, action VARCHAR(200) NOT NULL, member_id INTEGER, created_at DATETIME'),
        ('monthly_score', 'id INTEGER PRIMARY KEY, member_id INTEGER NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL, points INTEGER DEFAULT 0'),
    ]:
        cur.execute(f'CREATE TABLE IF NOT EXISTS {tbl} ({cols})')
    con.commit()
    con.close()

# ==========================================
# Mise à jour automatique
# ==========================================
GITHUB_REPO  = 'Naylm/PlanningMaison'
GITHUB_RELEASES_API = f'https://api.github.com/repos/{GITHUB_REPO}/releases'
VERSION_FILE = os.path.join(basedir, 'version.txt')
UPDATE_CHECK_INTERVAL = 2 * 60  # 2 minutes

# Conservés lors de la mise à jour
PRESERVE = {'fredo.db', 'backups', 'venv', '.env', 'version.txt', 'scripts', 'docs'}

_update_available = {'flag': False, 'tag': '', 'message': '', 'body': '', 'current_tag': ''}

def _read_local_version():
    try:
        with open(VERSION_FILE) as f:
            return f.read().strip()
    except Exception:
        return ''

def _write_local_version(tag):
    with open(VERSION_FILE, 'w') as f:
        f.write(tag.strip() + '\n')

def _fetch_releases():
    import urllib.request, json as _json
    req = urllib.request.Request(GITHUB_RELEASES_API,
          headers={'User-Agent': 'PlanningMaison-Updater'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return _json.loads(r.read())

def _check_update_once():
    try:
        releases = _fetch_releases()
        if not releases:
            return
        latest = releases[0]
        latest_tag = latest['tag_name']
        local_tag  = _read_local_version()
        _update_available['current_tag'] = local_tag
        if latest_tag and local_tag and latest_tag != local_tag:
            body = latest.get('body') or ''
            first_line = next((l.strip() for l in body.splitlines() if l.strip()), '')
            msg = first_line or latest.get('name') or 'Nouvelle version disponible'
            _update_available['flag'] = True
            _update_available['tag']  = latest_tag
            _update_available['message'] = msg[:80]
            _update_available['body'] = body[:1500]
        else:
            _update_available['flag'] = False
    except Exception as e:
        print(f'[Update] Vérification échouée : {e}')

def _update_check_loop():
    time.sleep(30)   # attendre 30s après démarrage
    while True:
        _check_update_once()
        time.sleep(UPDATE_CHECK_INTERVAL)

def _install_from_zip(zip_url, new_tag):
    import urllib.request, zipfile, tempfile, sys, shutil
    print(f'[Update] Téléchargement {zip_url}...')
    req = urllib.request.Request(zip_url, headers={'User-Agent': 'PlanningMaison-Updater'})
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
        tmp_path = tmp.name
        with urllib.request.urlopen(req, timeout=60) as r:
            tmp.write(r.read())

    print('[Update] Extraction...')
    tmp_dir = tempfile.mkdtemp()
    with zipfile.ZipFile(tmp_path) as z:
        z.extractall(tmp_dir)
    os.unlink(tmp_path)

    extracted = [d for d in os.listdir(tmp_dir) if os.path.isdir(os.path.join(tmp_dir, d))]
    if not extracted:
        print('[Update] Erreur : dossier extrait introuvable')
        return False
    src_dir = os.path.join(tmp_dir, extracted[0])

    print('[Update] Copie des fichiers...')
    for item in os.listdir(src_dir):
        if item in PRESERVE:
            continue
        s = os.path.join(src_dir, item)
        d = os.path.join(basedir, item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.copy2(s, d)

    _write_local_version(new_tag)
    _update_available['flag'] = False
    _update_available['current_tag'] = new_tag
    print(f'[Update] Installé : {new_tag}')
    return True

@app.route('/api/update/check')
def update_check():
    _update_available['current_tag'] = _read_local_version()
    return jsonify(_update_available)

@app.route('/api/update/apply', methods=['POST'])
def update_apply():
    import sys
    def _do_update():
        try:
            releases = _fetch_releases()
            if not releases:
                print('[Update] Aucune release trouvée')
                return
            latest = releases[0]
            zip_url = latest['zipball_url']
            new_tag = latest['tag_name']
            if not _install_from_zip(zip_url, new_tag):
                return
            time.sleep(1)
            print('[Update] Redémarrage...')
            import subprocess
            subprocess.Popen([sys.executable] + sys.argv, cwd=basedir)
            os._exit(0)
        except Exception as e:
            print(f'[Update] Erreur lors de la mise à jour : {e}')

    t = threading.Thread(target=_do_update, daemon=True)
    t.start()
    return jsonify({'started': True})

@app.route('/api/releases')
def list_releases():
    try:
        releases = _fetch_releases()
        current = _read_local_version()
        result = []
        for r in releases[:10]:
            result.append({
                'tag': r['tag_name'],
                'name': r.get('name') or r['tag_name'],
                'body': (r.get('body') or '').split('\n')[0][:80],
                'date': r.get('published_at', '')[:10],
                'zip_url': r['zipball_url'],
                'current': r['tag_name'] == current,
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rollback', methods=['POST'])
def rollback():
    import sys
    data = request.json or {}
    tag = data.get('tag', '')
    zip_url = data.get('zip_url', '')
    if not tag or not zip_url:
        return jsonify({'error': 'tag et zip_url requis'}), 400
    def _do_rollback():
        try:
            if not _install_from_zip(zip_url, tag):
                return
            time.sleep(1)
            print(f'[Rollback] Redémarrage vers {tag}...')
            import subprocess
            subprocess.Popen([sys.executable] + sys.argv, cwd=basedir)
            os._exit(0)
        except Exception as e:
            print(f'[Rollback] Erreur : {e}')
    t = threading.Thread(target=_do_rollback, daemon=True)
    t.start()
    return jsonify({'started': True})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        _auto_migrate()
    threading.Thread(target=_backup_loop, daemon=True).start()
    threading.Thread(target=_update_check_loop, daemon=True).start()
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
