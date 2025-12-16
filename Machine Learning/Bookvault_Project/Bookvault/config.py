"""
Configuration Module for BookVault Application

This module provides centralized configuration management for the entire application.
All settings can be overridden via environment variables for different deployment environments.

Environment Variables:
    Database:
        BOOKVAULT_DB: Path to SQLite cache database (default: "bookvault_cache.db")
        CACHE_TTL_HOURS: Cache expiry time in hours (default: 24)
        CACHE_SIZE: LRU cache size (default: 256)

    API Keys:
        GOOGLE_BOOKS_API_KEY: Google Books API key (optional)
        OPENAI_API_KEY: OpenAI API key (required)

    API Settings:
        API_TIMEOUT: Request timeout in seconds (default: 30)
        MAX_RETRIES: Maximum retry attempts for failed requests (default: 3)
        RETRY_INITIAL_DELAY: Initial retry delay in seconds (default: 1.0)
        RETRY_BACKOFF_MULTIPLIER: Exponential backoff multiplier (default: 2.0)

    OpenAI Model Settings:
        OPENAI_MODEL: Model name (default: "gpt-4o-mini")
        OPENAI_MAX_TOKENS_SHORT: Max tokens for short responses (default: 50)
        OPENAI_MAX_TOKENS_MEDIUM: Max tokens for medium responses (default: 150)
        OPENAI_MAX_TOKENS_LONG: Max tokens for long responses (default: 500)
        OPENAI_TEMPERATURE_PRECISE: Temperature for precise tasks (default: 0.1)
        OPENAI_TEMPERATURE_BALANCED: Temperature for balanced tasks (default: 0.3)
        OPENAI_TEMPERATURE_CREATIVE: Temperature for creative tasks (default: 0.7)

    UI Settings:
        BOOKS_PER_PAGE_INITIAL: Initial books to display (default: 12)
        BOOKS_PER_LOAD_MORE: Books to add per "Load More" click (default: 6)
        MAX_BOOKS_PER_GENRE: Maximum books per genre (default: 48)
        GENRE_API_DELAY_SECONDS: Delay between genre API calls (default: 5)

Usage:
    from Bookvault.config import Config

    # Access configuration values
    api_key = Config.OPENAI_API_KEY
    timeout = Config.TIMEOUT

    # Validate configuration
    Config.validate()
"""

import os
import sys
import warnings
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
warnings.filterwarnings('ignore')
os.environ.update({'TF_CPP_MIN_LOG_LEVEL': '3', 'PYTHONWARNINGS': 'ignore'})
if not sys.warnoptions:
    warnings.simplefilter('ignore')


class Config:
    """
    Application Configuration Class

    Provides centralized access to all configuration settings.
    All values can be overridden via environment variables.

    Attributes:
        BASE_DIR: Project base directory path
        DB_PATH: SQLite database path for caching
        LOG_DIR: Directory for log files
        GOOGLE_BOOKS_API: Google Books API key
        OPENAI_API_KEY: OpenAI API key
        TIMEOUT: API request timeout in seconds
        MAX_RETRIES: Maximum number of retry attempts
        CACHE_SIZE: LRU cache size
        CACHE_TTL_HOURS: Cache time-to-live in hours
        [... and many more - see module docstring for full list]
    """

    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DB_PATH = os.getenv("BOOKVAULT_DB", "bookvault_cache.db")
    LOG_DIR = BASE_DIR / "logs"

    # API Keys
    GOOGLE_BOOKS_API = os.getenv("GOOGLE_BOOKS_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # API Settings
    TIMEOUT = int(os.getenv("API_TIMEOUT", "30"))  # seconds
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))

    # Cache Settings
    CACHE_SIZE = int(os.getenv("CACHE_SIZE", "256"))  # LRU cache size
    CACHE_TTL_HOURS = int(os.getenv("CACHE_TTL_HOURS", "24"))  # Cache expiry

    # Image Processing
    OCR_RESIZE_FACTOR = int(os.getenv("OCR_RESIZE_FACTOR", "2"))
    MAX_IMAGE_SIZE_MB = int(os.getenv("MAX_IMAGE_SIZE_MB", "10"))

    # Content Settings
    MAX_CAPTIONS = int(os.getenv("MAX_CAPTIONS", "3"))
    MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "40"))

    # OpenAI Model Settings
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_MAX_TOKENS_SHORT = int(os.getenv("OPENAI_MAX_TOKENS_SHORT", "50"))  # For short responses
    OPENAI_MAX_TOKENS_MEDIUM = int(os.getenv("OPENAI_MAX_TOKENS_MEDIUM", "150"))  # For medium responses
    OPENAI_MAX_TOKENS_LONG = int(os.getenv("OPENAI_MAX_TOKENS_LONG", "500"))  # For long responses
    OPENAI_TEMPERATURE_PRECISE = float(os.getenv("OPENAI_TEMPERATURE_PRECISE", "0.1"))  # For corrections
    OPENAI_TEMPERATURE_BALANCED = float(os.getenv("OPENAI_TEMPERATURE_BALANCED", "0.3"))  # For analysis
    OPENAI_TEMPERATURE_CREATIVE = float(os.getenv("OPENAI_TEMPERATURE_CREATIVE", "0.7"))  # For suggestions

    # Retry Settings
    RETRY_MAX_ATTEMPTS = int(os.getenv("RETRY_MAX_ATTEMPTS", "3"))
    RETRY_INITIAL_DELAY = float(os.getenv("RETRY_INITIAL_DELAY", "1.0"))  # seconds
    RETRY_BACKOFF_MULTIPLIER = float(os.getenv("RETRY_BACKOFF_MULTIPLIER", "2.0"))

    # UI Settings
    BOOKS_PER_PAGE_INITIAL = int(os.getenv("BOOKS_PER_PAGE_INITIAL", "12"))
    BOOKS_PER_LOAD_MORE = int(os.getenv("BOOKS_PER_LOAD_MORE", "6"))
    MAX_BOOKS_PER_GENRE = int(os.getenv("MAX_BOOKS_PER_GENRE", "48"))
    GENRE_API_DELAY_SECONDS = int(os.getenv("GENRE_API_DELAY_SECONDS", "5"))

    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    MAX_SEARCHES_PER_MINUTE = int(os.getenv("MAX_SEARCHES_PER_MINUTE", "100"))
    MAX_API_CALLS_PER_MINUTE = int(os.getenv("MAX_API_CALLS_PER_MINUTE", "50"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

    # Security
    ENABLE_INPUT_VALIDATION = os.getenv("ENABLE_INPUT_VALIDATION", "true").lower() == "true"

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []

        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not found in .env or environment variables")

        if cls.TIMEOUT <= 0:
            errors.append(f"Invalid TIMEOUT value: {cls.TIMEOUT}")

        if cls.CACHE_SIZE <= 0:
            errors.append(f"Invalid CACHE_SIZE value: {cls.CACHE_SIZE}")

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {err}" for err in errors))

        return True


# Validate configuration on import
Config.validate()
