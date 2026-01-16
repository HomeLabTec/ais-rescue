import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect


db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()


def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    # Ensure instance folder exists (stores SQLite DB by default)
    os.makedirs(app.instance_path, exist_ok=True)

    # Basic config
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-change-me")

    db_path = os.path.join(app.instance_path, "app.db")
    default_db = f"sqlite:///{db_path}"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", default_db)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "admin.login"
    login_manager.login_message_category = "warning"

    # Blueprints
    from .routes import public_bp, admin_bp
    app.register_blueprint(public_bp)
    app.register_blueprint(admin_bp)

    # CLI commands
    from .cli import register_cli
    register_cli(app)

    return app
