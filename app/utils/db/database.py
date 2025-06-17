#==========================
# app/utils/db/database.py
#==========================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from config.app_config import settings
import logging

logger = logging.getLogger(__name__)

# Datenbankengine erstellen
engine = create_engine(
    settings.DATABASE.URL,
    echo=settings.DATABASE.ECHO,
    pool_size=settings.DATABASE.POOL_SIZE,
    max_overflow=settings.DATABASE.MAX_OVERFLOW,
    pool_timeout=settings.DATABASE.POOL_TIMEOUT,
    pool_recycle=settings.DATABASE.POOL_RECYCLE,
    pool_pre_ping=settings.DATABASE.POOL_PRE_PING
)

# Session Factory erstellen
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

@contextmanager
def db_session() -> Session:
    """Context Manager für Datenbank-Sessions"""
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