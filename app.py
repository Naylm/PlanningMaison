from flask import Flask, render_template, request, jsonify, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import os
from sqlalchemy import func

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
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
    member = db.relationship('Member', backref=db.backref('events', lazy=True))

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
    now = datetime.now(timezone.utc)
    upcoming_events = Event.query.filter(Event.start_time >= now).order_by(Event.start_time.asc()).limit(3).all()
    recent_notes = Note.query.order_by(Note.created_at.desc()).limit(3).all()
    shopping_items = ShoppingItem.query.filter_by(is_completed=False).limit(5).all()
    pending_tasks = Task.query.filter_by(is_done=False).order_by(Task.points.desc()).limit(5).all()
    leaderboard = _get_leaderboard()
    return render_template('dashboard.html', events=upcoming_events, notes=recent_notes, shopping=shopping_items, pending_tasks=pending_tasks, leaderboard=leaderboard)

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
    events = Event.query.all()
    events_data = []
    for event in events:
        color = event.member.color if event.member else '#4a90e2'
        events_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'backgroundColor': color,
            'borderColor': color,
            'extendedProps': {
                'member_id': event.member_id,
                'member_name': event.member.name if event.member else 'Tous',
                'member_avatar': event.member.avatar if event.member else '🏡'
            }
        })
    return jsonify(events_data)

@app.route('/api/events', methods=['POST'])
def add_event():
    data = request.json
    start_time = datetime.fromisoformat(data['start_time'])
    end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else start_time
    member_id = data.get('member_id')
    
    new_event = Event(title=data['title'], start_time=start_time, end_time=end_time, member_id=member_id if member_id else None)
    db.session.add(new_event)
    db.session.commit()
    
    color = new_event.member.color if new_event.member else '#4a90e2'
    return jsonify({
        'id': new_event.id,
        'title': new_event.title,
        'start': new_event.start_time.isoformat(),
        'end': new_event.end_time.isoformat(),
        'backgroundColor': color,
        'borderColor': color
    })

@app.route('/api/events/<int:event_id>', methods=['PUT'])
def update_event(event_id):
    data = request.json
    event = Event.query.get_or_404(event_id)
    event.title = data['title']
    event.start_time = datetime.fromisoformat(data['start_time'])
    event.end_time = datetime.fromisoformat(data['end_time']) if data.get('end_time') else event.start_time
    event.member_id = data.get('member_id') if data.get('member_id') else None
    db.session.commit()
    return jsonify({'success': True})

@app.route('/api/events/<int:event_id>', methods=['DELETE'])
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
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
