from __future__ import annotations

import logging

from flask import Flask, session
from flask_cors import CORS

from ai_engine.engine import AIEngine
from config import Config
from database.database import init_app as init_db
from routes.admin_routes import admin_bp
from routes.ai_routes import ai_bp
from routes.auth_routes import auth_bp
from routes.user_routes import user_bp


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    CORS(app)

    logging.basicConfig(level=getattr(logging, app.config.get("LOG_LEVEL", "INFO")))

    init_db(app)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(ai_bp)

    # Attach AI engine
    ai_engine = AIEngine()
    app.extensions["ai_engine"] = ai_engine
    with app.app_context():
        try:
            ai_engine.warm_start()
        except RuntimeError:
            app.logger.warning("AI engine warm start skipped; insufficient data")

    from datetime import datetime  
    @app.context_processor
    def inject_user():
        return {
            "active_user": {
                "id": session.get("user_id"),
                "username": session.get("username"),
                "role": session.get("role"),
                "full_name": session.get("full_name"),
            },
            "now": datetime.now, 
        }

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
