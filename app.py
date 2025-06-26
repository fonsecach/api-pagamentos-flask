import os
from flask import Flask
from src.repository.database import db
from src.routes.payments import bp
from src.extensions import socketio

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "database.db")}'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret_key_websocket'

# Inicializa o banco
db.init_app(app)
socketio.init_app(app)
app.register_blueprint(bp, url_prefix='/payments')

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    socketio.run(app, debug=True)
