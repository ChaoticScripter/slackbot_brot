#==========================
# app_server.py
#==========================

from flask import Flask
from app.api.slack_endpoints import slack_routes
from app.utils.db.database import engine
from app.utils.logging.log_config import setup_logger
from app.scheduled_jobs import init_scheduler
from config.app_config import settings
from app.models import Base
import logging

logger = setup_logger(__name__)


def create_app() -> Flask:
    """Erstellt und konfiguriert die Flask-Anwendung"""
    app = Flask(__name__)

    # Registriere die Slack-Routen mit dem korrekten URL-Präfix
    app.register_blueprint(slack_routes, url_prefix='')

    return app

if __name__ == "__main__":
    try:
        # Datenbank-Tabellen erstellen

        Base.metadata.create_all(bind=engine)

        # Scheduler initialisieren
        scheduler = init_scheduler()

        # Flask-App erstellen und starten
        app = create_app()
        logger.info("Starting BrotBot server...")
        app.run(
            host="0.0.0.0",
            port=3000,
            debug=settings.DEBUG
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise