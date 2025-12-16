"""
Pytest configuration and shared fixtures for BookVault tests

This file contains pytest fixtures that are shared across all test modules.
"""

import pytest
import os
import tempfile
from pathlib import Path


@pytest.fixture
def temp_db_path():
    """
    Provide a temporary database path for testing

    Yields:
        str: Path to temporary database file

    Cleanup:
        Removes the temporary database file after test completion
    """
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp_file:
        db_path = tmp_file.name

    yield db_path

    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def mock_google_api_response():
    """
    Provide a mock Google Books API response

    Returns:
        dict: Mock API response with sample book data
    """
    return {
        "items": [
            {
                "id": "test_book_1",
                "volumeInfo": {
                    "title": "Test Book 1",
                    "authors": ["Test Author"],
                    "description": "A test book description",
                    "publisher": "Test Publisher",
                    "publishedDate": "2023-01-01",
                    "pageCount": 250,
                    "language": "en",
                    "categories": ["Fiction"],
                    "averageRating": 4.5,
                    "infoLink": "https://example.com/book1",
                    "imageLinks": {
                        "thumbnail": "https://example.com/cover1.jpg"
                    }
                }
            },
            {
                "id": "test_book_2",
                "volumeInfo": {
                    "title": "Test Book 2",
                    "authors": ["Another Author"],
                    "description": "Another test book",
                    "imageLinks": {
                        "thumbnail": "https://example.com/cover2.jpg"
                    }
                }
            }
        ]
    }


@pytest.fixture
def sample_book_data():
    """
    Provide sample book data for testing

    Returns:
        dict: Sample book dictionary
    """
    return {
        "id": "sample123",
        "title": "Sample Book",
        "author": "Sample Author",
        "description": "This is a sample book for testing",
        "cover_url": "https://example.com/cover.jpg",
        "publisher": "Sample Publisher",
        "published_date": "2023-01-01",
        "page_count": 300,
        "language": "en",
        "categories": ["Fiction", "Adventure"],
        "rating": 4.5,
        "info_link": "https://example.com/book"
    }


@pytest.fixture(autouse=True)
def set_test_environment():
    """
    Set up test environment variables

    This fixture automatically runs for every test to ensure
    test environment is properly configured.
    """
    # Set test environment variables
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["LOG_LEVEL"] = "ERROR"  # Reduce log noise during tests

    yield

    # Cleanup is not needed as environment variables are process-scoped
