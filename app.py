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

@app.route('/clients', methods=['GET', 'POST'])
def manage_clients():
    if request.method == 'POST':
        data = request.json
        new_client = Client(name=data['name'], phone=data['phone'], service_id=data['service_id'], schedule_id=data['schedule_id'])
        db.session.add(new_client)
        db.session.commit()
        return jsonify({"message": "Клиент добавлен", "id": new_client.id}), 201
    else:
        clients = Client.query.all()
        return jsonify([{"id": c.id, "name": c.name, "phone": c.phone, "service_id": c.service_id, "schedule_id": c.schedule_id} for c in clients]), 200

@app.route('/clients/<int:client_id>', methods=['PUT', 'DELETE'])
def manage_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == 'PUT':
        data = request.json
        client.name = data.get('name', client.name)
        client.phone = data.get('phone', client.phone)
        client.service_id = data.get('service_id', client.service_id)
        client.schedule_id = data.get('schedule_id', client.schedule_id)
        db.session.commit()
        return jsonify({"message": "Данные клиента обновлены", "id": client.id}), 200
    elif request.method == 'DELETE':
        db.session.delete(client)
        db.session.commit()
        return jsonify({"message": "Клиент удалён", "id": client.id}), 200

@app.route('/notifications', methods=['POST'])
def send_notification():
    data = request.json
    client = Client.query.get_or_404(data['client_id'])
    schedule = Schedule.query.get_or_404(client.schedule_id)
    service = Service.query.get_or_404(schedule.service_id)

    notification_message = f"Напоминание: {service.name} запланировано на {schedule.date.isoformat()}"
    
    # Здесь можно добавить логику отправки уведомления клиенту (например, через SMS или Telegram API)
    # Пример: send_sms(client.phone, notification_message)

    return jsonify({"message": "Уведомление отправлено", "client_id": client.id}), 200

@app.route('/admin/setup', methods=['POST'])
def setup_admin():
    data = request.json
    admin_id = data.get('telegram_id')
    if not admin_id:
        return jsonify({"message": "Необходимо указать telegram_id"}), 400

    # Здесь можно добавить логику сохранения администратора в базе данных
    # Пример: save_admin(admin_id)

    return jsonify({"message": "Администратор назначен", "telegram_id": admin_id}), 200

@app.route('/admin/generate-link', methods=['GET'])
def generate_client_link():
    # Здесь можно добавить логику генерации уникальной ссылки для клиентской части
    client_link = "https://example.com/client"  # Пример ссылки
    return jsonify({"message": "Ссылка сгенерирована", "client_link": client_link}), 200

@app.route('/admin/history', methods=['GET'])
def get_history():
    date_filter = request.args.get('date')
    client_filter = request.args.get('client_id')
    service_filter = request.args.get('service_id')

    query = Client.query
    if date_filter:
        query = query.join(Schedule).filter(Schedule.date == date_filter)
    if client_filter:
        query = query.filter(Client.id == client_filter)
    if service_filter:
        query = query.filter(Client.service_id == service_filter)

    history = query.all()
    return jsonify([{
        "id": c.id,
        "name": c.name,
        "phone": c.phone,
        "service_id": c.service_id,
        "schedule_id": c.schedule_id,
        "date": Schedule.query.get(c.schedule_id).date.isoformat()
    } for c in history]), 200

@app.route('/notify/master', methods=['POST'])
def notify_master():
    data = request.json
    client_id = data.get('client_id')
    action = data.get('action')  # "new", "update", "cancel"

    if not client_id or not action:
        return jsonify({"message": "Необходимо указать client_id и action"}), 400

    client = Client.query.get_or_404(client_id)
    schedule = Schedule.query.get_or_404(client.schedule_id)
    service = Service.query.get_or_404(schedule.service_id)

    notification_message = f"Уведомление для мастера: {action} запись на {service.name} для {client.name} ({client.phone}) на {schedule.date.isoformat()}"

    # Здесь можно добавить логику отправки уведомления мастеру (например, через Telegram API)
    # Пример: send_telegram_message(master_telegram_id, notification_message)

    return jsonify({"message": "Уведомление отправлено мастеру", "client_id": client_id}), 200

@app.route('/notify/settings', methods=['POST'])
def set_notification_settings():
    data = request.json
    master_id = data.get('master_id')
    notifications_enabled = data.get('notifications_enabled', True)
    notification_frequency = data.get('notification_frequency', 'immediate')  # "immediate", "daily", "weekly"

    if not master_id:
        return jsonify({"message": "Необходимо указать master_id"}), 400

    # Здесь можно добавить логику сохранения настроек уведомлений в базе данных
    # Пример: save_notification_settings(master_id, notifications_enabled, notification_frequency)

    return jsonify({
        "message": "Настройки уведомлений обновлены",
        "master_id": master_id,
        "notifications_enabled": notifications_enabled,
        "notification_frequency": notification_frequency
    }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)