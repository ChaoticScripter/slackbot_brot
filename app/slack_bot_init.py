# ==========================
# app/slack_bot_init.py
# ==========================

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from datetime import datetime
from config.app_config import settings
from app.handlers.order.order_commands import OrderHandler
from app.handlers.user.user_commands import UserHandler
from app.handlers.admin.admin_commands import AdminHandler
from app.utils.logging.log_config import setup_logger
from app.utils.db.database import db_session
from app.utils.message_blocks.home_view import create_home_view
from app.models import User, Order
from core.order_service import OrderService

logger = setup_logger(__name__)

# Slack App initialisieren
app = App(
    token=settings.SLACK.BOT_TOKEN,
    signing_secret=settings.SLACK.SIGNING_SECRET
)

# Handler initialisieren
order_handler = OrderHandler(slack_app=app)
user_handler = UserHandler(slack_app=app)
admin_handler = AdminHandler(slack_app=app)


@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    """Handler für App Home Opened Event"""
    try:
        user_id = event["user"]

        with db_session() as session:
            user = session.query(User).filter_by(slack_id=user_id).first()
            if not user:
                logger.warning(f"User {user_id} not found")
                return

            recent_orders = (
                session.query(Order)
                .filter(Order.user_id == user.user_id)
                .order_by(Order.order_date.desc())
                .limit(5)
                .all()
            )

            view = create_home_view(user, recent_orders)
            client.views_publish(user_id=user_id, view=view)

    except Exception as e:
        logger.error(f"Error publishing home view: {str(e)}")


@app.command("/user")
def handle_user_command(ack, body, logger):
    """Handler für den /name Command"""
    ack()
    user_handler.handle_user_command(body, logger)


@app.command("/order")
def handle_order_command(ack, body, logger):
    """Handler für den /order Command"""
    ack()
    order_handler.handle_order(body, logger)


@app.command("/admin")
def handle_admin_command(ack, body, logger):
    """Handler für den /admin Command"""
    ack()
    admin_handler.handle_admin(body, logger)


@app.error
def handle_errors(error, body, logger):
    """Globaler Error Handler"""
    logger.error(f"Error: {error}")
    logger.debug(f"Error body: {body}")


handler = SlackRequestHandler(app)


@app.action("remove_confirm")
def handle_remove_confirm(ack, body, client):
    ack()
    try:
        # Original Message löschen
        client.chat_delete(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"]
        )

        with db_session() as session:
            service = OrderService(session)
            order = service.remove_items(body["user"]["id"], body["private_metadata"])
            session.commit()

        client.chat_postMessage(
            channel=body["container"]["channel_id"],
            text="✅ Bestellung wurde erfolgreich aktualisiert"
        )

    except Exception as e:
        logger.error(f"Error confirming remove: {str(e)}")
        client.chat_postMessage(
            channel=body["container"]["channel_id"],
            text=f"❌ Fehler beim Aktualisieren der Bestellung: {str(e)}"
        )


@app.action("remove_cancel")
def handle_remove_cancel(ack, body, client):
    ack()
    client.chat_delete(
        channel=body["container"]["channel_id"],
        ts=body["container"]["message_ts"]
    )
    client.chat_postMessage(
        channel=body["container"]["channel_id"],
        text="❌ Änderung wurde abgebrochen"
    )
