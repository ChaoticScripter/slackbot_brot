#==========================
# app/utils/db/database.py
#==========================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.app_config import settings
import logging

logger = logging.getLogger(__name__)

# Die Engine ist das zentrale Objekt für die Verbindung zur Datenbank.
# Sie wird mit den Einstellungen aus der Konfiguration erstellt.
engine = create_engine(
    settings.DATABASE.URL,           # Datenbank-URL (z.B. mysql+pymysql://...)
    echo=settings.DATABASE.ECHO,     # SQL-Statements im Log ausgeben?
    pool_size=settings.DATABASE.POOL_SIZE,           # Größe des Connection-Pools
    max_overflow=settings.DATABASE.MAX_OVERFLOW,     # Zusätzliche Verbindungen über pool_size hinaus
    pool_timeout=settings.DATABASE.POOL_TIMEOUT,     # Timeout für Pool-Verbindungen
    pool_recycle=settings.DATABASE.POOL_RECYCLE,     # Zeit bis zur Wiederverwendung einer Verbindung
    pool_pre_ping=settings.DATABASE.POOL_PRE_PING    # Verbindung vor Nutzung prüfen
)

# SessionLocal ist eine Factory für neue Session-Objekte.
# Jede Session repräsentiert eine einzelne, unabhängige DB-Transaktion.
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

@contextmanager
def db_session() -> Session:
    """
    Context Manager für Datenbank-Sessions.
    Erzeugt eine neue Session, gibt sie an den Aufrufer weiter und sorgt für sauberes Commit/Rollback.
    Ablauf:
    1. Session wird erzeugt
    2. Code im 'with'-Block kann die Session nutzen
    3. Bei Erfolg: Commit
    4. Bei Fehler: Rollback und Fehlerausgabe
    5. Immer: Session schließen
    Beispiel:
        with db_session() as session:
            ... # Datenbankoperationen
    """
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        session.rollback()
        raise
    finally:
        session.close()