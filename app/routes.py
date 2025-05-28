#==========================
# app/routes.py
#==========================

from flask import Flask, request, make_response
from slack_bolt.adapter.flask import SlackRequestHandler
from app.bot import app as slack_app

flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    # Event handling
    return handler.handle(request)

@flask_app.route("/slack/interactivity", methods=["POST"])
def slack_interactivity():
    # Interactivity & shortcuts handling
    return handler.handle(request)

@flask_app.route("/slack/actions", methods=["POST"])
def slack_actions():
    # Actions handling
    return handler.handle(request)