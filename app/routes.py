#==========================
# app/routes.py
#==========================
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from app.bot import app as slack_app

flask_app = Flask(__name__)
handler = SlackRequestHandler(slack_app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)