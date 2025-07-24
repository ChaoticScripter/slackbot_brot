#==========================
# app/utils/logging/log_config.py
#==========================

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from config.app_config import settings


def setup_logger(name: str) -> logging.Logger:
    """
    Konfiguriert und liefert einen Logger mit einheitlichem Format für das gesamte Projekt.
    - Gibt Log-Ausgaben auf die Konsole und in eine Logdatei aus.
    - Rotiert die Logdatei automatisch, um Speicherplatz zu sparen.
    - Nutzt das Debug-Level aus der Konfiguration.
    Ablauf:
    1. Logger-Objekt holen (oder erstellen)
    2. Falls noch keine Handler existieren, werden Console- und File-Handler hinzugefügt
    3. Log-Format wird gesetzt (Zeit, Name, Level, Nachricht)
    4. Logdatei wird im logs/-Verzeichnis gespeichert
    5. Logger wird zurückgegeben
    Beispiel:
        logger = setup_logger(__name__)
        logger.info("Starte Anwendung...")
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        # Console Handler für Ausgaben im Terminal
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)

        # Logs-Verzeichnis erstellen, falls nicht vorhanden
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File Handler für persistente Logdatei mit Rotation
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'brotbot.log'),
            maxBytes=1024 * 1024,   # 1 MB pro Datei
            backupCount=5           # Maximal 5 Logdateien behalten
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

    return logger