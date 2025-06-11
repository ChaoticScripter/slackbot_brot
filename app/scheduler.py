# new/app/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.handlers.order.handlers import OrderHandler
from config.settings import settings
import logging

logger = logging.getLogger(__name__)


def init_scheduler() -> BackgroundScheduler:
    """Initialisiert und startet den Scheduler"""
    scheduler = BackgroundScheduler()

    # Tägliche Erinnerung einrichten
    scheduler.add_job(
        OrderHandler().send_daily_reminder,
        'cron',
        hour=settings.REMINDER_HOUR,
        minute=settings.REMINDER_MINUTE
    )

    scheduler.start()
    logger.info("Scheduler started")
    return scheduler