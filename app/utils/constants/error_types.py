#==========================
# app/utils/constants/error_types.py
#==========================

# Diese Datei definiert zentrale Fehlerklassen für den gesamten BrotBot.
# Sie dienen dazu, Fehlerquellen klar zu unterscheiden und gezielt abzufangen.
# Alle Fehler erben von BrotBotError, sodass sie gemeinsam behandelt werden können.

class BrotBotError(Exception):
    """
    Basis-Ausnahmeklasse für alle Bot-Fehler.
    Von dieser Klasse erben alle spezifischen Fehlerklassen.
    Ermöglicht ein zentrales Exception-Handling im gesamten Projekt.
    """
    pass

class DatabaseError(BrotBotError):
    """
    Fehler im Zusammenhang mit der Datenbank (z.B. Verbindungsfehler, Abfragefehler).
    """
    pass

class ValidationError(BrotBotError):
    """
    Fehler bei der Validierung von Benutzereingaben oder Daten.
    Wird z.B. geworfen, wenn Pflichtfelder fehlen oder ungültige Werte eingegeben werden.
    """
    pass

class SlackError(BrotBotError):
    """
    Fehler bei der Kommunikation mit der Slack API.
    """
    pass

class OrderError(BrotBotError):
    """
    Fehler im Zusammenhang mit Bestellungen (z.B. ungültige Produkte, Mengenprobleme).
    """
    pass