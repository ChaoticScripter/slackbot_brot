#==========================
# app/utils/logging/log_config.py
#==========================

import os
import logging
import sys
from logging.handlers import RotatingFileHandler
from config.app_config import settings


def setup_logger(name: str) -> logging.Logger:
    """Konfiguriert einen einheitlichen Logger"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)

        # Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(console_handler)

        # Logs-Verzeichnis erstellen, falls nicht vorhanden
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # File Handler
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'brotbot.log'),
            maxBytes=1024 * 1024,
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

    return logger