import os
from flask import Flask
from src.repository.database import db
from src.routes.payments import bp
from src.extensions import socketio


def create_app(testing=False):
    """Application factory pattern for creating Flask app instances."""
    app = Flask(__name__)
    
    # Configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    if testing:
        # Test configuration
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
    else:
        # Production/Development configuration
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "database.db")}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'secret_key_websocket')
    
    # Initialize extensions
    db.init_app(app)
    socketio.init_app(app)
    
    # Register blueprints
    app.register_blueprint(bp, url_prefix='/payments')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app


def create_socketio_app():
    """Create app with SocketIO for running the server."""
    app = create_app()
    return app, socketio


if __name__ == '__main__':
    app, socketio_instance = create_socketio_app()
    socketio_instance.run(app, debug=True)
