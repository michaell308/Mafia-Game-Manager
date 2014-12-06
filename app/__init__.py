from flask import Flask, session
from flask.ext.socketio import SocketIO
import datetime

socketio = SocketIO()


def create_app(debug=False):
    """Create an application."""
    
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = 'sufjdhlauknyrioe3q8740918ur-013umu4liyusa'
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(1)
    app.secret_key = 'deep is secret zomg'

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    socketio.init_app(app)
    return app