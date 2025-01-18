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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(port=5000)