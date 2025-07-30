#==========================
# config/app_config.py
#==========================

from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
import os

# Lädt Umgebungsvariablen aus einer .env-Datei (z.B. für Tokens, DB-URL)
load_dotenv()

@dataclass
class SlackConfig:
    """
    Konfigurationsdaten für die Slack-Integration.
    Wird automatisch aus Umgebungsvariablen geladen.
    - BOT_TOKEN: Slack Bot Token
    - SIGNING_SECRET: Slack Signing Secret
    """
    BOT_TOKEN: str = os.getenv('SLACK_BOT_TOKEN', '')
    SIGNING_SECRET: str = os.getenv('SLACK_SIGNING_SECRET', '')

@dataclass
class DatabaseConfig:
    """
    Konfigurationsdaten für die Datenbankverbindung.
    Wird automatisch aus Umgebungsvariablen geladen.
    - URL: Verbindungs-URL zur Datenbank
    - ECHO: SQL-Statements im Log ausgeben?
    - POOL_SIZE: Größe des Connection-Pools
    - MAX_OVERFLOW: Zusätzliche Verbindungen über pool_size hinaus
    - POOL_TIMEOUT: Timeout für Pool-Verbindungen
    - POOL_RECYCLE: Zeit bis zur Wiederverwendung einer Verbindung
    - POOL_PRE_PING: Verbindung vor Nutzung prüfen
    """
    URL: str = os.getenv('DATABASE_URL', '')
    ECHO: bool = False
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600
    POOL_PRE_PING: bool = True

@dataclass
class Settings:
    """
    Zentrale Konfigurationsklasse für das gesamte Projekt.
    - DEBUG: Debug-Modus (True/False)
    - REMINDER_HOUR: Stunde für tägliche Erinnerungen
    - REMINDER_MINUTE: Minute für tägliche Erinnerungen
    - SLACK: SlackConfig-Objekt
    - DATABASE: DatabaseConfig-Objekt
    """
    DEBUG: bool = True
    REMINDER_HOUR: int = 9
    REMINDER_MINUTE: int = 0
    WEEKLY_SUMMARY_HOUR: int = 9
    WEEKLY_SUMMARY_MINUTE: int = 30
    WEEKLY_SUMMARY_DAY: str = 'wed'  # Wochentag für die Zusammenfassung
    SLACK: SlackConfig = field(default_factory=SlackConfig)
    DATABASE: DatabaseConfig = field(default_factory=DatabaseConfig)

# Globale Settings-Instanz für das gesamte Projekt
settings = Settings()