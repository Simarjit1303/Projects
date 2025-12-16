"""
Application Constants for BookVault

This module contains all hardcoded values and magic numbers used throughout the application.
Centralizing these values makes them easier to maintain and modify.

Categories:
    - Genre Configuration: Genre browsing and fetching limits
    - Search Limits: Pagination and result limits
    - UI Constants: Display and layout values
    - Retry Values: Fallback retry configuration

Usage:
    from Bookvault.constants import GenreConstants, SearchConstants

    max_books = GenreConstants.MAX_BOOKS_PER_FETCH
    random_start = SearchConstants.RANDOM_START_RANGE
"""


class GenreConstants:
    """Constants related to genre browsing and book fetching"""

    # Maximum number of books to fetch in a single API call
    MAX_BOOKS_PER_FETCH = 150

    # Smaller range for quality results in single genre view
    SINGLE_GENRE_START_RANGE = 10

    # Larger range for variety in all genres view
    ALL_GENRES_START_RANGE = 100

    # Target number of books to fetch for single genre
    SINGLE_GENRE_TARGET_BOOKS = 50

    # Maximum total API fetches allowed per genre
    MAX_TOTAL_FETCHES_PER_GENRE = 30

    # Number of consecutive empty responses before repositioning
    MAX_CONSECUTIVE_EMPTY = 3

    # Increment for pagination to avoid overlapping results
    PAGINATION_INCREMENT = 80


class SearchConstants:
    """Constants related to search functionality"""

    # Random start index range for variety (conservative)
    RANDOM_START_RANGE_MIN = 0
    RANDOM_START_RANGE_MAX = 100

    # Minimum query length for natural language processing
    MIN_QUERY_LENGTH = 3


class UIConstants:
    """Constants related to UI display and layout"""

    # Chat message display height
    CHAT_MESSAGES_MAX_HEIGHT_PX = 280

    # Number of genres to display in "All Genres" view
    ALL_GENRES_DISPLAY_COUNT = 6

    # Maximum book title display length before truncation
    MAX_TITLE_DISPLAY_LENGTH = 35

    # Maximum author display length before truncation
    MAX_AUTHOR_DISPLAY_LENGTH = 25

    # Minimum cover URL length for validation
    MIN_COVER_URL_LENGTH = 10

    # Grid columns for book display
    BOOK_GRID_COLUMNS = 6


class CacheConstants:
    """Constants related to caching behavior"""

    # Additional books to keep beyond what's displayed (buffer)
    CACHE_BUFFER_SIZE = 3


class RetryConstants:
    """Constants for retry mechanisms and error handling"""

    # Request timeout for book fetching (seconds)
    BOOK_FETCH_TIMEOUT = 10


# Export all constant classes
__all__ = [
    "GenreConstants",
    "SearchConstants",
    "UIConstants",
    "CacheConstants",
    "RetryConstants",
]
