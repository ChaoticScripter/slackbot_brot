#==========================
# app/core/slack_endpoints.py
#==========================

from flask import Blueprint, request, Response
from app.slack_bot_init import handler
from app.utils.logging.log_config import setup_logger

logger = setup_logger(__name__)

slack_routes = Blueprint('slack', __name__)

@slack_routes.route('/slack/events', methods=['POST'])
def slack_events():
    """Endpunkt für Slack Events"""
    return handler.handle(request)

@slack_routes.route('/slack/interactivity', methods=['POST'])
def slack_interactivity():
    """Endpunkt für interaktive Komponenten (Buttons, Modals, etc.)"""
    return handler.handle(request)

@slack_routes.route('/slack/actions', methods=['POST'])
def slack_actions():
    """Endpunkt für Slack Aktionen"""
    return handler.handle(request)
