# backend/racing_manager.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///racing.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    color = db.Column(db.String(20), nullable=False)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class RaceResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_name = db.Column(db.String(100), nullable=False)
    car_color = db.Column(db.String(20), nullable=False)
    lap_time = db.Column(db.Float, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/results', methods=['POST'])
def add_result():
    data = request.json
    result = RaceResult(
        driver_name=data['driver_name'],
        car_color=data['car_color'],
        lap_time=data['lap_time']
    )
    db.session.add(result)
    db.session.commit()
    return jsonify({'message':'Result saved'})

@app.route('/results', methods=['GET'])
def get_results():
    results = RaceResult.query.order_by(RaceResult.lap_time).all()
    return jsonify([
        {'driver_name': r.driver_name, 'car_color': r.car_color, 'lap_time': r.lap_time}
        for r in results
    ])

if __name__ == '__main__':
    app.run(debug=True)
