"""
AI Helper Utilities for BookVault

Provides shared AI-powered helper functions used across the application.

Functions:
    get_ai_book_recommendations: Extract search terms from natural language and get book recommendations

Usage:
    from Bookvault.utils.ai_helpers import get_ai_book_recommendations

    results = get_ai_book_recommendations(
        user_query="books about mystery",
        search_function=service.search_books,
        cache_key="session_key"
    )
"""

from typing import List, Dict, Callable
from openai import OpenAI
from ..apis.openai_engine import retry_on_failure
from ..config import Config
from ..logger import get_logger
import os

logger = get_logger(__name__)


@retry_on_failure(
    max_retries=Config.RETRY_MAX_ATTEMPTS,
    delay=Config.RETRY_INITIAL_DELAY,
    backoff=Config.RETRY_BACKOFF_MULTIPLIER
)
def _call_openai_with_retry(client: OpenAI, prompt: str) -> str:
    """
    Make OpenAI API call with retry logic

    Args:
        client: OpenAI client instance
        prompt: The prompt to send to OpenAI

    Returns:
        The AI-generated response text
    """
    response = client.chat.completions.create(
        model=Config.OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=Config.OPENAI_MAX_TOKENS_SHORT,
        temperature=Config.OPENAI_TEMPERATURE_BALANCED
    )
    return response.choices[0].message.content.strip()


def get_ai_book_recommendations(
    user_query: str,
    search_function: Callable,
    max_results: int = 24,
    cache_key: str = ""
) -> List[Dict]:
    """
    Use AI to understand natural language and recommend books

    Args:
        user_query: Natural language query from user (e.g., "books about mystery")
        search_function: Function to call for searching books (e.g., cached_search_books)
        max_results: Maximum number of results to return
        cache_key: Cache key for the search function

    Returns:
        List of book dictionaries matching the AI-interpreted query

    Example:
        >>> results = get_ai_book_recommendations(
        ...     user_query="scary thriller novels",
        ...     search_function=service.search_books,
        ...     max_results=20
        ... )
    """
    try:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        # Ask AI to extract search keywords from natural language
        prompt = f"""You are a book recommendation AI. The user said: "{user_query}"

Extract the key genre, theme, or topic they're interested in. Return ONLY a short search query (1-3 words) that can be used to search for books.

Examples:
- "books about mystery and thriller" -> "mystery thriller"
- "I want something scary to read" -> "horror"
- "recommend fantasy novels" -> "fantasy"
- "books like Harry Potter" -> "fantasy adventure"
- "something romantic" -> "romance"

Return ONLY the search query, nothing else."""

        search_query = _call_openai_with_retry(client, prompt)

        # Search with the AI-generated query
        if cache_key:
            results = search_function(search_query, max_results=max_results, cache_key=cache_key)
        else:
            results = search_function(search_query, max_results=max_results)

        logger.info(f"AI interpreted '{user_query}' as '{search_query}', found {len(results)} books")
        return results

    except Exception as e:
        logger.error(f"AI search error for '{user_query}': {str(e)}")
        # Fallback to regular search
        try:
            if cache_key:
                return search_function(user_query, max_results=max_results, cache_key=cache_key)
            else:
                return search_function(user_query, max_results=max_results)
        except Exception as fallback_error:
            logger.error(f"Fallback search also failed: {str(fallback_error)}")
            return []
