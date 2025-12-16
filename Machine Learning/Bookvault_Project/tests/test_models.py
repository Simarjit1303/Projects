"""
Tests for BookVault data models

This module tests the Book model and its factory methods.
"""

import pytest
from Bookvault.models import Book


class TestBook:
    """Test suite for the Book model"""

    def test_book_initialization(self):
        """Test Book object initialization with kwargs"""
        book = Book(
            id="test123",
            title="Test Book",
            author="Test Author",
            description="A test book description"
        )

        assert book.id == "test123"
        assert book.title == "Test Book"
        assert book.author == "Test Author"
        assert book.description == "A test book description"

    def test_book_to_dict(self):
        """Test Book to_dict method"""
        book = Book(
            id="test123",
            title="Test Book",
            author="Test Author"
        )

        book_dict = book.to_dict()

        assert isinstance(book_dict, dict)
        assert book_dict["id"] == "test123"
        assert book_dict["title"] == "Test Book"
        assert book_dict["author"] == "Test Author"

    def test_book_from_google_api(self):
        """Test Book creation from Google API response"""
        api_response = {
            "id": "google123",
            "volumeInfo": {
                "title": "Sample Book",
                "authors": ["Author One", "Author Two"],
                "description": "Sample description",
                "publisher": "Test Publisher",
                "publishedDate": "2023-01-01",
                "pageCount": 300,
                "language": "en",
                "categories": ["Fiction", "Adventure"],
                "averageRating": 4.5,
                "infoLink": "https://example.com/book",
                "imageLinks": {
                    "thumbnail": "http://example.com/cover.jpg"
                }
            }
        }

        book = Book.from_google_api(api_response)

        assert book.id == "google123"
        assert book.title == "Sample Book"
        assert book.author == "Author One, Author Two"
        assert book.description == "Sample description"
        assert book.publisher == "Test Publisher"
        assert book.published_date == "2023-01-01"
        assert book.page_count == 300
        assert book.language == "en"
        assert book.categories == ["Fiction", "Adventure"]
        assert book.rating == 4.5
        assert book.cover_url.startswith("https://")  # HTTP upgraded to HTTPS

    def test_book_from_google_api_with_missing_fields(self):
        """Test Book creation with missing fields in API response"""
        api_response = {
            "id": "google456",
            "volumeInfo": {
                "title": "Minimal Book"
            }
        }

        book = Book.from_google_api(api_response)

        assert book.id == "google456"
        assert book.title == "Minimal Book"
        assert book.author == "Unknown"  # Default for missing authors
        assert book.description == ""
        assert book.cover_url == ""

    def test_book_cover_url_upgrade_http_to_https(self):
        """Test that HTTP cover URLs are upgraded to HTTPS"""
        api_response = {
            "id": "google789",
            "volumeInfo": {
                "title": "Test Book",
                "imageLinks": {
                    "thumbnail": "http://example.com/cover.jpg"
                }
            }
        }

        book = Book.from_google_api(api_response)

        assert book.cover_url.startswith("https://")
        assert "http://" not in book.cover_url
