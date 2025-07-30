# ==========================
# app/slack_bot_init.py
# ==========================

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
from app.utils.message_blocks.messages import create_user_help_blocks, create_feedback_message_blocks
from app.utils.message_blocks.modals import create_feedback_modal
from app.core.user_service import UserService
from app.models import User, Order
from app.core.order_service import OrderService
import json

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

def check_user_registered(user_id: str) -> bool:
    """Prüft, ob ein User registriert ist"""
    with db_session() as session:
        return session.query(User).filter_by(slack_id=user_id).first() is not None

# Event- und Command-Handler für Slack

@app.event("app_home_opened")
def handle_app_home_opened(client, event, logger):
    """Handler für das Öffnen der App Home Ansicht in Slack"""
    try:
        user_id = event["user"]
        with db_session() as session:
            user = session.query(User).filter_by(slack_id=user_id).first()

            # Wenn User nicht registriert ist, zeige Registrierungsview
            if not user:
                view = create_home_view()  # Ohne User-Parameter für unregistrierte Ansicht
                client.views_publish(user_id=user_id, view=view)
                return

            # Normale Home-View für registrierte User
            now = datetime.now()
            current_weekday = now.weekday()
            days_since_wednesday = (current_weekday - 2) % 7
            last_wednesday = now - timedelta(days=days_since_wednesday)
            period_start = last_wednesday.replace(hour=10, minute=0, second=0, microsecond=0)

            if current_weekday == 2 and now.hour < 10:
                period_start = period_start - timedelta(days=7)

            period_end = period_start + timedelta(days=7) - timedelta(minutes=1)

            recent_orders = (
                session.query(Order)
                .filter(
                    Order.user_id == user.user_id,
                    Order.order_date.between(period_start, period_end)
                )
                .order_by(Order.order_date.desc())
                .all()
            )

            view = create_home_view(user, recent_orders)
            client.views_publish(user_id=user_id, view=view)

    except Exception as e:
        logger.error(f"Error publishing home view: {str(e)}")

@app.action("submit_registration")
def handle_registration_submit(ack, body, client):
    """Handler für den Registrierungsbutton im Home-View"""
    ack()
    try:
        user_id = body["user"]["id"]
        input_value = body["view"]["state"]["values"]["registration_name"]["registration_name_input"]["value"]

        if not input_value:
            client.chat_postMessage(
                channel=user_id,
                text="❌ Bitte gib einen Namen ein."
            )
            return

        with db_session() as session:
            service = UserService(session)
            user = service.register_user(user_id, input_value)
            session.commit()

            # Aktualisiere Home-View nach erfolgreicher Registrierung
            view = create_home_view(user)
            client.views_publish(user_id=user_id, view=view)

            client.chat_postMessage(
                channel=user_id,
                text=f"✅ Erfolgreich registriert als {input_value}!"
            )

    except Exception as e:
        logger.error(f"Error handling registration: {str(e)}")
        client.chat_postMessage(
            channel=body["user"]["id"],
            text=f"❌ Fehler bei der Registrierung: {str(e)}"
        )

@app.command("/user")
def handle_user_command(ack, body, logger):
    """Handler für den /user Command"""
    ack()
    if not body.get('text', '').startswith('register') and not check_user_registered(body['user_id']):
        blocks = create_registration_blocks()
        app.client.chat_postMessage(
            channel=body['user_id'],
            blocks=blocks
        )
        return
    user_handler.handle_user_command(body, logger)

@app.command("/order")
def handle_order_command(ack, body, logger):
    """Handler für den /order Command"""
    ack()
    if not check_user_registered(body['user_id']):
        blocks = create_registration_blocks()
        app.client.chat_postMessage(
            channel=body['user_id'],
            blocks=blocks
        )
        return
    order_handler.handle_order(body, logger)

@app.command("/admin")
def handle_admin_command(ack, body, logger):
    """Handler für den /admin Command"""
    ack()
    if not check_user_registered(body['user_id']):
        blocks = create_registration_blocks()
        app.client.chat_postMessage(
            channel=body['user_id'],
            blocks=blocks
        )
        return
    admin_handler.handle_admin(body, logger)


@app.error
def handle_errors(error, body, logger):
    """
    Globaler Error Handler für alle Slack-Events und Commands.
    Gibt Fehler im Log aus und kann für User-Feedback genutzt werden.
    """
    logger.error(f"Error: {error}")
    logger.debug(f"Error body: {body}")


handler = SlackRequestHandler(app)

# ==========================
# Interaktive Aktionen (Buttons, Modals, etc.)
# ==========================

@app.action("remove_confirm")
def handle_remove_confirm(ack, body, client):
    """
    Handler für den Bestätigen-Button beim Entfernen von Produkten aus der Bestellung.
    Aktualisiert die Bestellung in der Datenbank und die Slack-Nachricht.
    """
    ack()
    try:
        logger.debug(f"Received action body: {json.dumps(body)}")
        if not body.get("actions") or not body["actions"][0].get("value"):
            raise ValueError("Keine Button-Daten gefunden")
        button_data = json.loads(body["actions"][0]["value"])
        if button_data.get("type") != "remove_order":
            raise ValueError("Ungültiger Datentyp")
        data = button_data.get("data", {})
        items = data.get("items")
        user_id = data.get("user_id")
        if not items or not user_id:
            raise ValueError("Unvollständige Daten")
        blocks = body["message"]["blocks"]
        blocks = blocks[:-2]  # Entferne Timer-Info und Action-Block
        with db_session() as session:
            service = OrderService(session)
            service.remove_items(user_id, items)
            session.commit()
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "✅ Die Änderungen wurden erfolgreich übernommen."
                }
            ]
        })
        client.chat_update(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"],
            blocks=blocks,
            text="Bestellung wurde aktualisiert"
        )
    except Exception as e:
        logger.error(f"Error confirming remove: {str(e)}")
        client.chat_postMessage(
            channel=body["container"]["channel_id"],
            text=f"❌ Fehler beim Aktualisieren der Bestellung: {str(e)}"
        )


@app.action("remove_cancel")
def handle_remove_cancel(ack, body, client):
    """
    Handler für den Abbrechen-Button beim Entfernen von Produkten.
    Bricht den Vorgang ab und aktualisiert die Slack-Nachricht.
    """
    ack()
    try:
        blocks = body["message"]["blocks"]
        blocks = blocks[:-2]  # Entferne Timer-Info und Action-Block
        blocks.append({
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": "❌ Der Vorgang wurde abgebrochen. Die Bestellung bleibt unverändert."
                }
            ]
        })
        client.chat_update(
            channel=body["container"]["channel_id"],
            ts=body["container"]["message_ts"],
            blocks=blocks,
            text="Vorgang abgebrochen"
        )
    except Exception as e:
        logger.error(f"Error handling cancel: {str(e)}")
        client.chat_postMessage(
            channel=body["container"]["channel_id"],
            text="❌ Fehler beim Abbrechen des Vorgangs"
        )


@app.action("submit_feedback")
def handle_feedback_submission(ack, body, client):
    """
    Handler für Feedback-Einreichungen aus der Home-View.
    Liest die Feedbackdaten aus dem Modal, postet sie in den Feedback-Channel und bestätigt dem User.
    """
    ack()
    try:
        home_view_values = body.get("view", {}).get("state", {}).get("values", {})
        feedback_title = home_view_values.get("feedback_title", {}).get("feedback_title_input", {}).get("value", "")
        feedback_text = home_view_values.get("feedback_text", {}).get("feedback_text_input", {}).get("value", "")
        user_id = body["user"]["id"]
        with db_session() as session:
            user = session.query(User).filter_by(slack_id=user_id).first()
            if not user:
                raise ValueError("Benutzer nicht gefunden")
            blocks = create_feedback_message_blocks(
                user_name=user.name,
                slack_name=body['user']['name'],
                feedback_title=feedback_title,
                feedback_text=feedback_text
            )
            client.chat_postMessage(
                channel="feedback",  # Der Channel-Name oder die Channel-ID
                text=f"Neues Feedback von {user.name} (@{body['user']['name']})\n\nÜberschrift: {feedback_title}\n\nFeedback: {feedback_text}",
                blocks=blocks
            )
            client.chat_postMessage(
                channel=user_id,
                text="✅ Vielen Dank für dein Feedback! Es wurde erfolgreich übermittelt."
            )
    except Exception as e:
        logger.error(f"Error handling feedback submission: {str(e)}")
        client.chat_postMessage(
            channel=body["user"]["id"],
            text="❌ Es gab einen Fehler beim Senden des Feedbacks. Bitte versuche es später erneut."
        )
