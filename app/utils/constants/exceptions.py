#==========================
# app/utils/constants/exceptions.py
#==========================

class BrotBotError(Exception):
    """Basis-Ausnahmeklasse für alle Bot-Fehler"""
    pass

class DatabaseError(BrotBotError):
    """Datenbankbezogene Fehler"""
    pass

class ValidationError(BrotBotError):
    """Validierungsfehler"""
    pass

class SlackError(BrotBotError):
    """Slack API Fehler"""
    pass

class OrderError(BrotBotError):
    """Bestellungsbezogene Fehler"""
    pass