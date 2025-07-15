#==========================
# app_server.py
#==========================

from flask import Flask
from app.api.slack_endpoints import slack_routes
from app.utils.db.database import engine
from app.utils.logging.log_config import setup_logger
from app.models import Base
from app.scheduled_jobs import init_scheduler
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

        # Flask-App erstellen und Scheduler starten
        app = create_app()
        scheduler = init_scheduler()  # Starte den Scheduler

        logger.info("Starting BrotBot server...")
        app.run(
            host="0.0.0.0",
            port=3000,
            debug=False  # Debug auf False setzen, um doppelte Ausführung zu verhindern
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise