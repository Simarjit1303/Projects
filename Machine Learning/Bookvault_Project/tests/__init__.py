"""
BookVault Test Suite

This package contains unit tests, integration tests, and end-to-end tests
for the BookVault application.

Test Structure:
    - test_models.py: Tests for data models
    - test_cache.py: Tests for caching functionality
    - test_security.py: Tests for input validation and rate limiting
    - test_service.py: Tests for main service layer
    - test_apis.py: Tests for API integrations
    - test_search_intelligence.py: Tests for AI-powered search features

Running Tests:
    # Run all tests
    pytest

    # Run specific test file
    pytest tests/test_models.py

    # Run with coverage
    pytest --cov=Bookvault --cov-report=html

    # Run with verbose output
    pytest -v
"""
