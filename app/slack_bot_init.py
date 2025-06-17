#==========================
# app/slack_bot_init.py
#==========================

from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler
from config.app_config import settings
from app.handlers.order.order_commands import OrderHandler
from app.handlers.user.user_commands import UserHandler
from app.handlers.admin.admin_commands import AdminHandler

app = App(
    token=settings.SLACK.BOT_TOKEN,
    signing_secret=settings.SLACK.SIGNING_SECRET
)

# Handler initialisieren
order_handler = OrderHandler(slack_app=app)
user_handler = UserHandler()
admin_handler = AdminHandler()

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
    user_handler.handle_name(body, logger)

@app.command("/admin")
def handle_admin_command(ack, body, logger):
    """Wrapper für den Admin Command"""
    ack()
    admin_handler.handle_admin(body, logger)

@app.event("app_home_opened")
def handle_app_home_opened(body, logger):
    """Handler für App Home Opened Event"""
    logger.info("App Home wurde geöffnet")
    logger.debug(body)