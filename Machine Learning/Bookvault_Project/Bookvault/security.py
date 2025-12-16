"""
Security utilities for BookVault application
Includes input validation, sanitization, and rate limiting
"""
import re
import html
import time
from typing import Optional, Dict, Any
from collections import defaultdict
from datetime import datetime, timedelta
from .logger import get_logger

logger = get_logger(__name__)


class InputValidator:
    """Validates and sanitizes user inputs"""

    # Regex patterns
    QUERY_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-.,!?\'"]+$')
    SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_.,]+$')

    # Maximum lengths
    MAX_QUERY_LENGTH = 500
    MAX_DESCRIPTION_LENGTH = 5000
    MAX_TITLE_LENGTH = 300

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = None) -> str:
        """
        Sanitize string input by removing dangerous characters

        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not input_str:
            return ""

        # Convert to string and strip
        sanitized = str(input_str).strip()

        # HTML escape
        sanitized = html.escape(sanitized)

        # Remove control characters
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char == '\n')

        # Truncate if needed
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            logger.warning(f"Input truncated from {len(input_str)} to {max_length} characters")

        return sanitized

    @staticmethod
    def validate_search_query(query: str) -> tuple[bool, Optional[str]]:
        """
        Validate search query input

        Args:
            query: Search query string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not query:
            return False, "Search query cannot be empty"

        if len(query) > InputValidator.MAX_QUERY_LENGTH:
            return False, f"Search query too long (max {InputValidator.MAX_QUERY_LENGTH} characters)"

        # Allow most characters for search flexibility
        # Just check for obvious injection attempts
        dangerous_patterns = ['<script', 'javascript:', 'onerror=', 'onclick=']
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if pattern in query_lower:
                logger.warning(f"Potentially dangerous pattern detected in query: {pattern}")
                return False, "Invalid characters in search query"

        return True, None

    @staticmethod
    def validate_book_title(title: str) -> tuple[bool, Optional[str]]:
        """
        Validate book title

        Args:
            title: Book title string

        Returns:
            Tuple of (is_valid, error_message)
        """
        if not title:
            return False, "Book title cannot be empty"

        if len(title) > InputValidator.MAX_TITLE_LENGTH:
            return False, f"Title too long (max {InputValidator.MAX_TITLE_LENGTH} characters)"

        return True, None

    @staticmethod
    def validate_integer(value: Any, min_val: int = 1, max_val: int = 100) -> tuple[bool, int]:
        """
        Validate and convert integer input

        Args:
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Tuple of (is_valid, sanitized_value)
        """
        try:
            int_val = int(value)
            if int_val < min_val or int_val > max_val:
                logger.warning(f"Integer value {int_val} outside range [{min_val}, {max_val}]")
                return False, min_val
            return True, int_val
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value: {value}")
            return False, min_val


class RateLimiter:
    """
    Simple in-memory rate limiter
    Limits requests per time window per identifier (IP, user ID, etc.)
    """

    def __init__(self, max_requests: int = 100, time_window: int = 60):
        """
        Initialize rate limiter

        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests: Dict[str, list] = defaultdict(list)
        logger.info(f"RateLimiter initialized: {max_requests} requests per {time_window}s")

    def is_allowed(self, identifier: str) -> tuple[bool, Optional[str]]:
        """
        Check if request is allowed for identifier

        Args:
            identifier: Unique identifier (IP address, user ID, etc.)

        Returns:
            Tuple of (is_allowed, error_message)
        """
        now = time.time()
        cutoff = now - self.time_window

        # Clean old requests
        self.requests[identifier] = [
            req_time for req_time in self.requests[identifier]
            if req_time > cutoff
        ]

        # Check if limit exceeded
        if len(self.requests[identifier]) >= self.max_requests:
            logger.warning(f"Rate limit exceeded for identifier: {identifier}")
            return False, f"Rate limit exceeded. Max {self.max_requests} requests per {self.time_window}s"

        # Add current request
        self.requests[identifier].append(now)
        return True, None


# Global rate limiter instances
search_rate_limiter = RateLimiter(max_requests=100, time_window=60)  # 100 searches per minute
