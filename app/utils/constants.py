#==========================
# app/utils/constants.py
#==========================

from typing import Dict, Any

# Alle Fehlermeldungen an einem Ort
ERROR_MESSAGES: Dict[str, str] = {
    # Bestellungsfehler
    "ORDER_INVALID_FORMAT": "Ungültiges Format. Beispiel: `/order add normal 2, vollkorn 1`",
    "ORDER_PRODUCT_NOT_FOUND": "Produkt '{product}' nicht gefunden oder inaktiv",
    "ORDER_INVALID_QUANTITY": "Ungültige Menge für {product}",
    "ORDER_GENERAL_ERROR": "Ein Fehler ist aufgetreten. Bitte versuche es erneut.",

    # Registrierungsfehler
    "REGISTRATION_REQUIRED": "Du bist nicht registriert. Bitte registriere dich zuerst.",
    "REGISTRATION_INVALID_NAME": "Bitte gib einen gültigen Namen ein.",
    "REGISTRATION_ERROR": "Fehler bei der Registrierung. Bitte versuche es später erneut.",

    # Datenbankfehler
    "DB_CONNECTION_ERROR": "Datenbankverbindungsfehler. Bitte versuche es später erneut.",
    "DB_QUERY_ERROR": "Datenbankabfragefehler. Bitte versuche es später erneut."
}

# Befehlskonstanten
COMMANDS: Dict[str, str] = {
    "ORDER_ADD": "add",
    "ORDER_LIST": "list",
    "ORDER_REMOVE": "remove",
    "NAME_CHANGE": "change"
}

# Datenbankeinschränkungen
DB_CONSTRAINTS: Dict[str, Any] = {
    "MIN_QUANTITY": 1,
    "MAX_QUANTITY": 100,
    "MAX_NAME_LENGTH": 100,
    "MAX_DESCRIPTION_LENGTH": 255
}

# Slack Block-Typen
BLOCK_TYPES: Dict[str, str] = {
    "SECTION": "section",
    "DIVIDER": "divider",
    "ACTIONS": "actions",
    "INPUT": "input",
    "CONTEXT": "context"
}

# Admin-Fehlermeldungen
ADMIN_ERROR_MESSAGES: Dict[str, str] = {
    "NOT_ADMIN": "Du hast keine Admin-Berechtigung.",
    "INVALID_FORMAT": "Ungültiges Format für Admin-Befehl.",
    "PRODUCT_EXISTS": "Produkt '{product}' existiert bereits.",
    "PRODUCT_NOT_FOUND": "Produkt '{product}' nicht gefunden.",
    "MISSING_PRODUCT_NAME": "Bitte gib einen Produktnamen an.",
    "DB_ERROR": "Datenbankfehler. Bitte versuche es erneut."
}

# Admin-Befehle
ADMIN_COMMANDS: Dict[str, str] = {
    "HELP": "help",
    "PRODUCT_ADD": "product_add",
    "PRODUCT_DELETE": "product_delete",
    "PRODUCT_ACTIVATE": "product_activate",
    "PRODUCT_DEACTIVATE": "product_deactivate",
    "PRODUCT_LIST": "product_list",
    "ORDER_LIST": "order_list"
}

# Admin-Hilfetexte
ADMIN_HELP_TEXTS: Dict[str, str] = {
    "GENERAL": "Admin-Befehle:\n" +
              "• `/order admin help` - Diese Hilfe anzeigen\n" +
              "• `/order admin product_add <Name> [Beschreibung]` - Neues Produkt anlegen\n" +
              "• `/order admin product_delete <Name>` - Produkt löschen\n" +
              "• `/order admin product_activate <Name>` - Produkt aktivieren\n" +
              "• `/order admin product_deactivate <Name>` - Produkt deaktivieren\n" +
              "• `/order admin product_list` - Alle Produkte anzeigen\n" +
              "• `/order admin order_list` - Aktuelle Bestellungen anzeigen"
}