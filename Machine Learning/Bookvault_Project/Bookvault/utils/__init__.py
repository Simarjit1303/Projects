"""
Utilities Module for BookVault

Provides utility classes for image processing and other helper functions.

Key Classes:
    ImageProcessor: OCR-based text extraction from book cover images

Key Functions:
    get_ai_book_recommendations: AI-powered natural language book search

Usage:
    from Bookvault.utils import ImageProcessor, get_ai_book_recommendations

    processor = ImageProcessor()
    text = processor.extract_text(uploaded_file)

    books = get_ai_book_recommendations(
        user_query="scary books",
        search_function=service.search_books
    )
"""

from .image_processor import ImageProcessor
from .ai_helpers import get_ai_book_recommendations

__all__ = ["ImageProcessor", "get_ai_book_recommendations"]
