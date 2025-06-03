from slack_bolt import App
import os
from app.handlers.order import handle_order_add
from app.handlers.name import handle_name
from app.handlers.help import handle_help

app = App(
    token=os.getenv("SLACK_BOT_TOKEN"),
    signing_secret=os.getenv("SLACK_SIGNING_SECRET"),
    process_before_response=True
)

@app.command("/help")
def help_command(ack, respond):
    handle_help(ack, respond)

@app.command("/name")
def name_command(ack, respond, command):
    handle_name(ack, respond, command)


@app.command("/order")
def order_command(ack, respond, command):
    ack()
    text = command.get("text", "").strip()

    if not text:
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ Bitte gib einen gültigen Befehl ein.\nVerwende `/help` um alle verfügbaren Befehle anzuzeigen."
                }
            }
        ]
        respond(blocks=blocks)
        return

    if text == "add":
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "⚠️ Bitte gib mindestens ein Produkt mit Menge an.\nBeispiel: `/order add normal 2, vollkorn 1`"
                }
            }
        ]
        respond(blocks=blocks)
        return

    if text.startswith("add"):
        handle_order_add(ack, respond, command)