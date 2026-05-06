from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
from sqlalchemy import func

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
app.config['SECRET_KEY'] = 'dev-key-fredo-1234'

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

class ShoppingItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    member_ids = db.Column(db.Text, nullable=True)
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

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    points = db.Column(db.Integer, default=1)
    assigned_to = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    done_by = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    done_at = db.Column(db.DateTime, nullable=True)
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
    return render_template('dashboard.html', events=upcoming_events, notes=recent_notes, shopping=shopping_items,
        pending_tasks=pending_tasks, leaderboard=leaderboard, today_meals=today_meals, today=today)

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
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes.html', notes=notes)

@app.route('/tasks')
def tasks_page():
    members = Member.query.all()
    pending = Task.query.filter_by(is_done=False).order_by(Task.points.desc()).all()
    done = Task.query.filter_by(is_done=True).order_by(Task.done_at.desc()).limit(20).all()
    leaderboard = _get_leaderboard()
    return render_template('tasks.html', members=members, pending=pending, done=done, leaderboard=leaderboard)

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
    member = Member.query.get_or_404(member_id)
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

# API: Liste de courses
@app.route('/api/shopping', methods=['POST'])
def add_shopping_item():
    data = request.json
    new_item = ShoppingItem(name=data['name'])
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'id': new_item.id, 'name': new_item.name, 'is_completed': new_item.is_completed})

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

# API: Tâches
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = Task.query.order_by(Task.is_done.asc(), Task.points.desc()).all()
    return jsonify([_task_to_dict(t) for t in tasks])

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    task = Task(
        title=data['title'],
        points=int(data.get('points', 1)),
        assigned_to=data.get('assigned_to') or None
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(_task_to_dict(task)), 201

@app.route('/api/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    data = request.json
    task = Task.query.get_or_404(task_id)
    task.is_done = True
    task.done_by = data.get('member_id') or None
    task.done_at = datetime.now(timezone.utc)
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

@app.route('/api/leaderboard')
def get_leaderboard():
    return jsonify(_get_leaderboard())

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
        'done_at': task.done_at.isoformat() if task.done_at else None
    }

# API: Événements (Calendrier)
@app.route('/api/events', methods=['GET'])
def get_events():
    import json as _json
    events = Event.query.all()
    all_members = {m.id: m for m in Member.query.all()}
    events_data = []
    for event in events:
        ids = event.get_member_ids()
        members_info = [all_members[i] for i in ids if i in all_members]
        color = members_info[0].color if members_info else '#4a90e2'
        names = ', '.join(m.name for m in members_info) if members_info else 'Tous'
        avatars = ' '.join(m.avatar for m in members_info) if members_info else '🏡'
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat() + 'Z',
            'end': event.end_time.isoformat() + 'Z',
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'member_ids': ids,
                'member_id': event.member_id,
                'member_name': names,
                'member_avatar': avatars,
                'members_info': [{'id': m.id, 'name': m.name, 'avatar': m.avatar, 'color': m.color} for m in members_info]
            }
        })
    return jsonify(events_data)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else start_time
    ids = [int(i) for i in data.get('member_ids', []) if i]
    if not ids and data.get('member_id'):
        ids = [int(data['member_id'])]
    new_event = Event(title=data['title'], start_time=start_time, end_time=end_time)
    new_event.set_member_ids(ids)
    db.session.add(new_event)
    db.session.commit()
    color = new_event.member.color if new_event.member else '#4a90e2'
    return jsonify({'id': new_event.id, 'title': new_event.title,
        'start': new_event.start_time.isoformat() + 'Z', 'end': new_event.end_time.isoformat() + 'Z',
        'backgroundColor': color, 'borderColor': color})

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

@app.route('/api/backup')
def backup_db():
    try:
        return send_file(os.path.join(basedir, 'fredo.db'), as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
