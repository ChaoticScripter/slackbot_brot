#==========================
# app/utils/message_blocks/constants.py
#==========================

from typing import Dict

# Design-System Konstanten
COLORS = {
    "SUCCESS": "#36a64f",   # Grün für positive Aktionen
    "ERROR": "#dc3545",     # Rot für Fehler
    "WARNING": "#ffc107",   # Gelb für Warnungen
    "INFO": "#17a2b8",      # Blau für Informationen
    "PRIMARY": "#0d6efd",   # Primärfarbe
    "SECONDARY": "#6c757d"  # Sekundärfarbe
}

# Emojis für verschiedene Nachrichtentypen
EMOJIS = {
    "SUCCESS": "✅",
    "ERROR": "❌",
    "WARNING": "⚠️",
    "INFO": "ℹ️",
    "ORDER": "🛒",
    "REMINDER": "⏰",
    "ADMIN": "👑",
    "PRODUCT": "📦",
    "USER": "👤",
    "LIST": "📋",
    "CALENDAR": "📅",
    "SETTINGS": "⚙️",
    "TIME": "⌚",
    "NEW": "🆕",
    "DELETE": "🗑️",
    "EDIT": "✏️",
    "SAVE": "💾",
    "MONEY": "💰"
}

# Standard Block-Templates
BLOCK_DEFAULTS = {
    "DIVIDER": {"type": "divider"},
    "SPACER": {"type": "section", "text": {"type": "mrkdwn", "text": " "}},
    "HEADER": lambda text: {
        "type": "header",
        "text": {"type": "plain_text", "text": text}
    },
    "CONTEXT": lambda text: {
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": text}]
    }
}

# Layout-Strukturen
LAYOUTS = {
    "BASIC": [
        "HEADER",
        "DIVIDER",
        "CONTENT",
        "SPACER"
    ],
    "DETAILED": [
        "HEADER",
        "CONTEXT",
        "DIVIDER",
        "CONTENT",
        "DIVIDER",
        "FOOTER"
    ]
}