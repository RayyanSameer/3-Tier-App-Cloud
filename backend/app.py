#Placeholder FLASK app

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
# Allow CORS so Frontend can talk to Backend
CORS(app)

# Database Config (Uses the 'postgres' service name from K8s)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://admin:secretpassword@postgres/todo_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- NEW DATABASE MODEL ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    notes = db.Column(db.Text, nullable=True)          # Feature 6 & 8: Notes/Subtasks
    due_date = db.Column(db.DateTime, nullable=True)   # Feature 3 & 7: Reminder/Time
    completed = db.Column(db.Boolean, default=False)   # Feature 5: Complete
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "notes": self.notes,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()

# --- API ROUTES ---

@app.route('/todos', methods=['GET'])
def get_todos():
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.json
    # Parse Date string to Python Date Object
    due = datetime.fromisoformat(data['due_date']) if data.get('due_date') else None
    
    new_task = Task(content=data['content'], notes=data.get('notes'), due_date=due)
    db.session.add(new_task)
    db.session.commit()
    return jsonify(new_task.to_dict()), 201

@app.route('/todos/<int:id>', methods=['PUT']) # Feature 4 & 5: Modify/Complete
def update_todo(id):
    task = Task.query.get_or_404(id)
    data = request.json
    
    if 'content' in data: task.content = data['content']
    if 'completed' in data: task.completed = data['completed']
    if 'notes' in data: task.notes = data['notes']
    
    db.session.commit()
    return jsonify(task.to_dict())

@app.route('/todos/<int:id>', methods=['DELETE']) # Feature 2: Delete
def delete_todo(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Deleted'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)