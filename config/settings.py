#==========================
# config/settings.py
#==========================

from dataclasses import dataclass, field
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

@dataclass
class SlackConfig:
    BOT_TOKEN: str = os.getenv('SLACK_BOT_TOKEN', '')
    SIGNING_SECRET: str = os.getenv('SLACK_SIGNING_SECRET', '')

@dataclass
class DatabaseConfig:
    URL: str = os.getenv('DATABASE_URL', '')
    ECHO: bool = False
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    POOL_TIMEOUT: int = 30
    POOL_RECYCLE: int = 3600
    POOL_PRE_PING: bool = True

@dataclass
class Settings:
    DEBUG: bool = True
    REMINDER_HOUR: int = 9
    REMINDER_MINUTE: int = 0
    SLACK: SlackConfig = field(default_factory=SlackConfig)
    DATABASE: DatabaseConfig = field(default_factory=DatabaseConfig)

settings = Settings()