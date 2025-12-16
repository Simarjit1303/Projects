"""
📚 BookVault — Modular Book Search and AI Recommendation System

Main package providing book search, AI recommendations, and intelligent search features.

Key Classes:
    BookVaultService: Main service layer for all book operations
    SearchIntelligence: AI-powered search with typo correction and suggestions
    Config: Centralized application configuration
    Book: Book data model
    SQLiteCache: Caching layer for API responses
    InputValidator: Input validation and sanitization
    RateLimiter: Rate limiting for API calls

Usage:
    from Bookvault import BookVaultService, Config

    service = BookVaultService()
    books = service.search_books("Harry Potter")
"""

from .service import BookVaultService
from .config import Config
from .models import Book
from .cache import SQLiteCache
from .logger import get_logger
from .security import InputValidator, RateLimiter
from .search_intelligence import SearchIntelligence
from .constants import (
    GenreConstants,
    SearchConstants,
    UIConstants,
    CacheConstants,
    RetryConstants,
)

__all__ = [
    "BookVaultService",
    "SearchIntelligence",
    "Config",
    "Book",
    "SQLiteCache",
    "get_logger",
    "InputValidator",
    "RateLimiter",
    "GenreConstants",
    "SearchConstants",
    "UIConstants",
    "CacheConstants",
    "RetryConstants",
]