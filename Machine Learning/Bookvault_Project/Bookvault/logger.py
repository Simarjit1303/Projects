"""
Logging configuration for BookVault application
Provides structured logging with file rotation and different log levels
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime


class BookVaultLogger:
    """Centralized logging configuration"""

    _loggers = {}

    @classmethod
    def get_logger(cls, name: str, log_level: str = "INFO") -> logging.Logger:
        """
        Get or create a logger with the specified name

        Args:
            name: Name of the logger (typically __name__)
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]

        # Create logger
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Avoid duplicate handlers
        if logger.handlers:
            return logger

        # Create logs directory if it doesn't exist
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        # File handler with rotation (10MB max, keep 5 backups)
        log_file = log_dir / f"bookvault_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # Cache logger
        cls._loggers[name] = logger

        return logger


# Convenience function
def get_logger(name: str) -> logging.Logger:
    """Get a logger instance"""
    return BookVaultLogger.get_logger(name)
