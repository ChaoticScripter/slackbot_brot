# new/app/api/slack_routes.py
from flask import Blueprint, request, Response
from slack_bolt.adapter.flask import SlackRequestHandler
from app.bot import app as slack_app

slack_routes = Blueprint('slack_routes', __name__)
handler = SlackRequestHandler(slack_app)

@slack_routes.route("/slack/events", methods=["POST"])
def slack_events() -> Response:
    return handler.handle(request)

@slack_routes.route("/slack/interactivity", methods=["POST"])
def slack_interactivity() -> Response:
    return handler.handle(request)

@slack_routes.route("/slack/actions", methods=["POST"])
def slack_actions() -> Response:
    return handler.handle(request)