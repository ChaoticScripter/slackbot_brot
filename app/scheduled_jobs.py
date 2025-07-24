#==========================
# app/scheduled_jobs.py
#==========================

from apscheduler.schedulers.background import BackgroundScheduler
from app.handlers.order.order_commands import OrderHandler
from app.slack_bot_init import app as slack_app
from config.app_config import settings
import logging

logger = logging.getLogger(__name__)


def init_scheduler() -> BackgroundScheduler:
    """
    Initialisiert und startet den Scheduler für wiederkehrende Aufgaben.
    - Tägliche Erinnerungen an alle aktiven User
    - Wöchentliche Bestellzusammenfassung an berechtigte User
    Ablauf:
    1. Scheduler-Objekt wird erstellt
    2. OrderHandler wird mit Slack-App initialisiert
    3. Täglicher Job für Erinnerungen wird hinzugefügt
    4. Wöchentlicher Job für die Bestellübersicht wird hinzugefügt
    5. Scheduler wird gestartet und zurückgegeben
    """
    scheduler = BackgroundScheduler()

    order_handler = OrderHandler(slack_app=slack_app)

    # Tägliche Erinnerung einrichten (z.B. 09:00 Uhr)
    scheduler.add_job(
        order_handler.send_daily_reminder,
        'cron',
        hour=settings.REMINDER_HOUR,
        minute=settings.REMINDER_MINUTE
    )

    # Wöchentliche Bestellzusammenfassung einrichten (z.B. Mittwoch 09:30 Uhr)
    scheduler.add_job(
        order_handler.send_weekly_summary,
        'cron',
        day_of_week='wed',  # Mittwoch
        hour=9,            # 09:30 Uhr
        minute=30
    )

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler