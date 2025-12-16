"""
Tests for BookVault security features

This module tests input validation, sanitization, and rate limiting.
"""

import pytest
from Bookvault.security import InputValidator, RateLimiter
import time


class TestInputValidator:
    """Test suite for InputValidator"""

    def test_sanitize_string_basic(self):
        """Test basic string sanitization"""
        result = InputValidator.sanitize_string("  Hello World  ")
        assert result == "Hello World"

    def test_sanitize_string_html_escape(self):
        """Test HTML escaping in sanitization"""
        result = InputValidator.sanitize_string("<script>alert('XSS')</script>")
        assert "&lt;script&gt;" in result
        assert "<script>" not in result

    def test_sanitize_string_max_length(self):
        """Test string truncation based on max_length"""
        long_string = "a" * 1000
        result = InputValidator.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_control_characters(self):
        """Test removal of control characters"""
        input_str = "Hello\x00World\x01Test"
        result = InputValidator.sanitize_string(input_str)
        assert "\x00" not in result
        assert "\x01" not in result

    def test_validate_search_query_valid(self):
        """Test validation of valid search queries"""
        is_valid, error = InputValidator.validate_search_query("Harry Potter")
        assert is_valid is True
        assert error is None

    def test_validate_search_query_empty(self):
        """Test validation rejects empty queries"""
        is_valid, error = InputValidator.validate_search_query("")
        assert is_valid is False
        assert error is not None

    def test_validate_search_query_too_long(self):
        """Test validation rejects overly long queries"""
        long_query = "a" * 600
        is_valid, error = InputValidator.validate_search_query(long_query)
        assert is_valid is False
        assert "too long" in error.lower()

    def test_validate_search_query_dangerous_patterns(self):
        """Test validation rejects queries with dangerous patterns"""
        dangerous_queries = [
            "<script>alert('test')</script>",
            "javascript:void(0)",
            "onclick=alert('xss')"
        ]

        for query in dangerous_queries:
            is_valid, error = InputValidator.validate_search_query(query)
            assert is_valid is False

    def test_validate_integer_valid(self):
        """Test integer validation with valid input"""
        is_valid, value = InputValidator.validate_integer(25, min_val=1, max_val=100)
        assert is_valid is True
        assert value == 25

    def test_validate_integer_out_of_range(self):
        """Test integer validation rejects out-of-range values"""
        is_valid, value = InputValidator.validate_integer(150, min_val=1, max_val=100)
        assert is_valid is False

    def test_validate_integer_invalid_type(self):
        """Test integer validation handles invalid types"""
        is_valid, value = InputValidator.validate_integer("not a number", min_val=1, max_val=100)
        assert is_valid is False


class TestRateLimiter:
    """Test suite for RateLimiter"""

    def test_rate_limiter_allows_within_limit(self):
        """Test that requests within limit are allowed"""
        limiter = RateLimiter(max_requests=3, time_window=10)

        is_allowed, msg = limiter.is_allowed("user1")
        assert is_allowed is True

        is_allowed, msg = limiter.is_allowed("user1")
        assert is_allowed is True

        is_allowed, msg = limiter.is_allowed("user1")
        assert is_allowed is True

    def test_rate_limiter_blocks_over_limit(self):
        """Test that requests over limit are blocked"""
        limiter = RateLimiter(max_requests=2, time_window=10)

        limiter.is_allowed("user2")
        limiter.is_allowed("user2")

        # Third request should be blocked
        is_allowed, msg = limiter.is_allowed("user2")
        assert is_allowed is False
        assert "exceeded" in msg.lower()

    def test_rate_limiter_resets_after_window(self):
        """Test that rate limit resets after time window"""
        limiter = RateLimiter(max_requests=1, time_window=1)  # 1 second window

        # First request allowed
        is_allowed, msg = limiter.is_allowed("user3")
        assert is_allowed is True

        # Second request blocked
        is_allowed, msg = limiter.is_allowed("user3")
        assert is_allowed is False

        # Wait for window to expire
        time.sleep(1.1)

        # Should be allowed again
        is_allowed, msg = limiter.is_allowed("user3")
        assert is_allowed is True

    def test_rate_limiter_separate_identifiers(self):
        """Test that different identifiers have separate limits"""
        limiter = RateLimiter(max_requests=1, time_window=10)

        is_allowed_user1, _ = limiter.is_allowed("user1")
        is_allowed_user2, _ = limiter.is_allowed("user2")

        assert is_allowed_user1 is True
        assert is_allowed_user2 is True
