from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)

class Schedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule.id'))

@app.route('/')
def index():
    return "Telegram Mini App для записи клиентов"

@app.route('/services', methods=['GET', 'POST'])
def manage_services():
    if request.method == 'POST':
        data = request.json
        new_service = Service(name=data['name'], price=data['price'])
        db.session.add(new_service)
        db.session.commit()
        return jsonify({"message": "Услуга добавлена", "id": new_service.id}), 201
    else:
        services = Service.query.all()
        return jsonify([{"id": s.id, "name": s.name, "price": s.price} for s in services]), 200

@app.route('/services/<int:service_id>', methods=['PUT', 'DELETE'])
def manage_service(service_id):
    service = Service.query.get_or_404(service_id)
    if request.method == 'PUT':
        data = request.json
        service.name = data.get('name', service.name)
        service.price = data.get('price', service.price)
        db.session.commit()
        return jsonify({"message": "Услуга обновлена", "id": service.id}), 200
    elif request.method == 'DELETE':
        db.session.delete(service)
        db.session.commit()
        return jsonify({"message": "Услуга удалена", "id": service.id}), 200

@app.route('/schedule', methods=['GET', 'POST'])
def manage_schedule():
    if request.method == 'POST':
        data = request.json
        new_schedule = Schedule(date=datetime.fromisoformat(data['date']), service_id=data['service_id'])
        db.session.add(new_schedule)
        db.session.commit()
        return jsonify({"message": "Слот расписания добавлен", "id": new_schedule.id}), 201
    else:
        schedules = Schedule.query.all()
        return jsonify([{"id": s.id, "date": s.date.isoformat(), "service_id": s.service_id} for s in schedules]), 200

@app.route('/schedule/<int:schedule_id>', methods=['PUT', 'DELETE'])
def manage_schedule_slot(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if request.method == 'PUT':
        data = request.json
        schedule.date = datetime.fromisoformat(data.get('date', schedule.date.isoformat()))
        schedule.service_id = data.get('service_id', schedule.service_id)
        db.session.commit()
        return jsonify({"message": "Слот расписания обновлён", "id": schedule.id}), 200
    elif request.method == 'DELETE':
        db.session.delete(schedule)
        db.session.commit()
        return jsonify({"message": "Слот расписания удалён", "id": schedule.id}), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)