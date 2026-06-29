from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///raise_request.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class GeneralRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester = db.Column(db.String(100), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    end_date = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)

@app.route('/api/raise-request', methods=['POST'])
def raise_request():
    data = request.json
    try:
        new_req = GeneralRequest(
            requester=data['requester'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            description=data['description']
        )
        db.session.add(new_req)
        db.session.commit()
        return jsonify({'message': 'General request captured', 'id': new_req.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5002)