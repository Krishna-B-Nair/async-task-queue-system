from flask import Flask
from flask_socketio import SocketIO
from redis import Redis
from rq import Queue
from app.config import Config

socketio = SocketIO()

def create_app(config_class: type = Config) -> Flask:
    """
    Application factory pattern to create and configure the Flask app.
    Injects Redis and Queue into app.extensions to avoid global mutable state.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Dependency Injection: Redis & RQ attached to app context
    redis_conn = Redis.from_url(app.config["REDIS_URL"])
    app.extensions["redis"] = redis_conn
    app.extensions["task_queue"] = Queue(connection=redis_conn)

    # Initialize extensions
    socketio.init_app(app, cors_allowed_origins="*")

    # Register Blueprints
    from app.api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api/v1")

    return app