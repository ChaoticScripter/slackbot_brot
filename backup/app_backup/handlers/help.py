#==========================
# app/handlers/help.py
#==========================

# app/handlers/help.py
from app.utils.slack_messages import create_help_blocks

def handle_help(ack, respond):
    ack()
    blocks, attachments = create_help_blocks()
    respond(blocks=blocks, attachments=attachments)