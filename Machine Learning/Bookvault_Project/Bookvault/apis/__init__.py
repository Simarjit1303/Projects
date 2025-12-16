"""
APIs Module for BookVault

Provides integrations with external APIs including Google Books and OpenAI.

Key Classes:
    GoogleBooksAPI: Interface to Google Books API for book search
    AIRecommendationEngine: AI-powered recommendations using OpenAI

Key Functions:
    retry_on_failure: Decorator for automatic retry with exponential backoff

Usage:
    from Bookvault.apis import GoogleBooksAPI, AIRecommendationEngine, retry_on_failure

    # Use retry decorator for API calls
    @retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
    def my_api_call():
        # Your API call here
        pass
"""

from .google_books import GoogleBooksAPI
from .openai_engine import AIRecommendationEngine, retry_on_failure

__all__ = ["GoogleBooksAPI", "AIRecommendationEngine", "retry_on_failure"]
