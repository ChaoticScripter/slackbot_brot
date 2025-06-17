#==========================
# app/reminder_jobs.py
#==========================

from apscheduler.schedulers.background import BackgroundScheduler
from app.handlers.order.order_commands import OrderHandler
from app.slack_bot_init import app as slack_app
from config.app_config import settings
import logging

logger = logging.getLogger(__name__)


def init_scheduler() -> BackgroundScheduler:
    """Initialisiert und startet den Scheduler"""
    scheduler = BackgroundScheduler()

    order_handler = OrderHandler(slack_app=slack_app)

    # Tägliche Erinnerung einrichten
    scheduler.add_job(
        order_handler.send_daily_reminder,
        'cron',
        hour=settings.REMINDER_HOUR,
        minute=settings.REMINDER_MINUTE
    )

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler