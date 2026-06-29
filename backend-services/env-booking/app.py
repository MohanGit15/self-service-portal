from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///env_booking.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

COST_MAPPING = {
    'DEVE': 20000, 'DEVD': 20000, 'DEVF': 20000,
    'EBS01': 15000, 'EBS02': 15000, 'EBS03': 15000, 'DTESF': 15000, 'EBS06': 15000
}

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.String(100), nullable=False)
    environment = db.Column(db.String(20), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=True)
    summary = db.Column(db.String(200), nullable=True)
    total_cost = db.Column(db.Float, nullable=False)

@app.route('/api/booking/calculate', methods=['POST'])
def calculate_cost():
    data = request.json
    env = data.get('environment')
    start_str = data.get('start_date')
    end_str = data.get('end_date')
    
    if env not in COST_MAPPING or not start_str or not end_str:
        return jsonify({'error': 'Invalid payload'}), 400
        
    try:
        start = datetime.strptime(start_str, "%Y-%m-%d")
        end = datetime.strptime(end_str, "%Y-%m-%d")
        days = max((end - start).days, 1)
        cost = days * COST_MAPPING[env]
        return jsonify({'days': days, 'total_cost': cost})
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

@app.route('/api/booking', methods=['POST'])
def create_booking():
    data = request.json
    try:
        start = datetime.strptime(data['start_date'], "%Y-%m-%d")
        end = datetime.strptime(data['end_date'], "%Y-%m-%d")
        days = max((end - start).days, 1)
        cost = days * COST_MAPPING[data['environment']]
        
        new_booking = Booking(
            requester=data['requester'],
            environment=data['environment'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            description=data.get('description'),
            summary=data.get('summary'),
            total_cost=cost
        )
        db.session.add(new_booking)
        db.session.commit()
        return jsonify({'message': 'Booking saved successfully', 'id': new_booking.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5001)