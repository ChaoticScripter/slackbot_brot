#==========================
# app/slack_bot_init.py
#==========================

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from datetime import datetime, timedelta
from config.app_config import settings
from app.handlers.order.order_commands import OrderHandler
from app.handlers.user.user_commands import UserHandler
from app.handlers.admin.admin_commands import AdminHandler
from app.utils.logging.log_config import setup_logger
from app.utils.db.database import db_session
from app.utils.message_blocks.home_view import create_home_view
from app.models import User, Order

logger = setup_logger(__name__)

app = App(
    token=settings.SLACK.BOT_TOKEN,
    signing_secret=settings.SLACK.SIGNING_SECRET
)

# Handler initialisieren
order_handler = OrderHandler(slack_app=app)
user_handler = UserHandler()
admin_handler = AdminHandler(slack_app=app)


# Synchrone Command Handler
@app.command("/order")
def handle_order_command(ack, body, logger):
    """Wrapper für den Order Command"""
    ack()
    order_handler.handle_order(body, logger)


@app.command("/name")
def handle_name_command(ack, body, logger):
    """Wrapper für den Name Command"""
    ack()
    user_handler.handle_name_command(body, logger)


@app.command("/admin")
def handle_admin_command(ack, body, logger):
    """Wrapper für den Admin Command"""
    ack()
    admin_handler.handle_admin(body, logger)


@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    """Handler für App Home Opened Event"""
    try:
        user_id = event["user"]

        with db_session() as session:
            # Benutzer abrufen
            user = session.query(User).filter_by(slack_id=user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return

            # Letzte Bestellungen des Benutzers abrufen (z.B. letzte 30 Tage)
            recent_orders = session.query(Order) \
                .filter(
                Order.user_id == user.user_id,
                Order.order_date >= datetime.now() - timedelta(days=30)
            ) \
                .order_by(Order.order_date.desc()) \
                .limit(5) \
                .all()

            # Home View erstellen und publishen
            view = create_home_view(user, recent_orders)

            client.views_publish(
                user_id=user_id,
                view=view
            )

    except Exception as e:
        logger.error(f"Error publishing home view: {str(e)}")


@app.event("message")
def handle_message_event(body, logger):
    """Handler für Nachrichten-Events"""
    try:
        logger.info("Nachricht empfangen")
        logger.debug(body)
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")


# Error Handler
@app.error
def handle_errors(error, body, logger):
    """Globaler Error Handler"""
    logger.error(f"Error: {error}")
    logger.debug(f"Error body: {body}")


handler = SlackRequestHandler(app)