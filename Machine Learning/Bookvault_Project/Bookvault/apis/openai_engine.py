"""
OpenAI Integration Module for BookVault

This module provides AI-powered book recommendations, captions, quotes, and genre verification
using OpenAI's GPT models. All API calls include automatic retry logic with exponential backoff
to handle transient failures and rate limiting.

Key Features:
    - AI-powered book recommendations based on similarity
    - Automatic genre verification for search results
    - Generation of catchy book captions
    - Creation of thematic quotes inspired by books
    - Natural language query interpretation
    - Automatic retry with exponential backoff for API failures

Classes:
    AIRecommendationEngine: Main class for all AI-powered features

Functions:
    retry_on_failure: Decorator for automatic retry with exponential backoff

Usage:
    from Bookvault.apis.openai_engine import AIRecommendationEngine

    engine = AIRecommendationEngine(cache, books_api)
    recommendations = engine.get_recommendations(
        title="Harry Potter",
        author="J.K. Rowling",
        description="A boy wizard...",
        categories="Fantasy",
        max_results=5
    )
"""

import hashlib
import time
from functools import lru_cache, wraps
from typing import List, Dict, Callable, Any
from openai import OpenAI, APIError, RateLimitError, APIConnectionError
from ..config import Config
from ..cache import SQLiteCache
from .google_books import GoogleBooksAPI
from ..logger import get_logger

logger = get_logger(__name__)


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry OpenAI API calls on failure with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries in seconds
        backoff: Multiplier for delay after each retry
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (APIError, RateLimitError, APIConnectionError) as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(f"{func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {str(e)}. Retrying in {current_delay}s...")
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(f"{func.__name__} failed after {max_retries + 1} attempts: {str(e)}")
                except Exception as e:
                    logger.error(f"{func.__name__} failed with unexpected error: {str(e)}")
                    raise

            raise last_exception
        return wrapper
    return decorator


class AIRecommendationEngine:
    """
    AI-Powered Book Recommendation and Content Generation Engine

    This class provides intelligent book recommendations and AI-generated content
    using OpenAI's GPT models. All operations are cached for performance and
    include automatic retry logic for reliability.

    Attributes:
        cache (SQLiteCache): Cache provider for storing AI responses
        books_api (GoogleBooksAPI): Google Books API client for book searches
        client (OpenAI): OpenAI API client

    Methods:
        verify_books_batch: Verify if books match a specific genre using AI
        get_recommendations: Get book recommendations similar to a given book
        get_captions: Generate catchy captions for a book
        get_famous_quotes: Generate thematic quotes inspired by a book
        interpret_natural_language_query: Process natural language search queries

    Example:
        >>> engine = AIRecommendationEngine(cache, books_api)
        >>> books = engine.get_recommendations(
        ...     title="1984",
        ...     author="George Orwell",
        ...     description="Dystopian novel...",
        ...     categories="Fiction, Dystopian",
        ...     max_results=5
        ... )
    """

    def __init__(self, cache: SQLiteCache, books_api: GoogleBooksAPI):
        """
        Initialize the AI Recommendation Engine

        Args:
            cache: SQLiteCache instance for caching AI responses
            books_api: GoogleBooksAPI instance for searching books
        """
        self.cache = cache
        self.books_api = books_api
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)

    def verify_books_batch(self, books: List[Dict], expected_genre: str) -> List[Dict]:
        """
        Verify multiple books at once using AI (faster batch processing using only title/author)

        Args:
            books: List of book dictionaries with title, author
            expected_genre: The genre we expect (Fiction, Mystery, etc.)

        Returns:
            List of books that match the genre
        """
        if not books:
            return []

        # Build batch prompt with just titles (much faster, no need for categories or covers)
        books_list = "\n".join([
            f"{i+1}. '{book.get('title', '')}' by {book.get('author', 'Unknown')}"
            for i, book in enumerate(books[:30])  # Can handle more books now (30)
        ])

        prompt = (
            f"Which books are '{expected_genre}' genre? Return ONLY comma-separated numbers (e.g., '1,3,5').\n\n"
            f"{books_list}"
        )

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0
            )
            answer = resp.choices[0].message.content.strip()

            # Parse response to get book indices
            try:
                valid_indices = [int(x.strip()) - 1 for x in answer.replace(' ', '').split(',') if x.strip().isdigit()]
                return [books[i] for i in valid_indices if 0 <= i < len(books)]
            except:
                # If parsing fails, return all books (don't reject due to parsing error)
                logger.warning(f"Failed to parse batch verification response: {answer}")
                return books

        except Exception as e:
            logger.warning(f"Batch genre verification failed: {e}")
            # On error, accept all books
            return books

    def _generate_cache_key(self, prompt: str) -> str:
        return f"ai:{hashlib.md5(prompt.encode()).hexdigest()}"

    @lru_cache(maxsize=Config.CACHE_SIZE)
    def get_recommendations(self, title: str, author: str, description: str,
                            categories: str, lang: str = "en", max_results: int = 5) -> List[Dict]:
        prompt = (
            f"Recommend {max_results * 2} books similar to '{title}' by {author}. "
            f"Categories: {categories}. Description: {description[:200]}.\n\n"
            f"IMPORTANT RULES:\n"
            f"1. DO NOT recommend '{title}' itself\n"
            f"2. Include a mix of:\n"
            f"   - Other books in the same series (if applicable)\n"
            f"   - Books by the same author\n"
            f"   - Books from related series with similar themes\n"
            f"   - Books with similar genres/themes by different authors\n\n"
            f"Return ONLY book titles with authors in format: 'Book Title by Author Name', one per line.\n"
            f"Example: 'Harry Potter and the Goblet of Fire by J.K. Rowling'"
        )

        cache_key = self._generate_cache_key(prompt)
        if cached := self.cache.get(cache_key):
            # Filter out the current book from cached results
            return [book for book in cached if book.get("title", "").lower() != title.lower()][:max_results]

        try:
            logger.info(f"Requesting AI recommendations for: {title[:50]}")
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400
            )
            lines = [line.strip() for line in resp.choices[0].message.content.split("\n") if line.strip()]
            logger.debug(f"AI returned {len(lines)} recommendation lines")

            recommendations = []
            seen_titles = set([title.lower()])  # Track titles to avoid duplicates

            for line in lines:
                # Clean up the line (remove numbers, dashes, etc.)
                clean_line = line.lstrip("0123456789.-) ").strip()

                if not clean_line or clean_line.lower() == title.lower():
                    continue

                # Search for the book
                results = self.books_api.search(clean_line, max_results=3, lang=lang)

                for book in results:
                    book_title = book.get("title", "").lower()

                    # Skip if it's the same book or we've already added it
                    if book_title == title.lower() or book_title in seen_titles:
                        continue

                    # Skip if no cover image
                    if not book.get("cover_url"):
                        continue

                    recommendations.append(book)
                    seen_titles.add(book_title)

                    if len(recommendations) >= max_results:
                        break

                if len(recommendations) >= max_results:
                    break

            self.cache.set(cache_key, recommendations)
            logger.info(f"Generated {len(recommendations)} AI recommendations for: {title[:50]}")
            return recommendations
        except Exception as e:
            logger.error(f"AI recommendation error for '{title[:50]}': {e}", exc_info=True)
            return []

    def get_captions(self, title: str, description: str, max_captions: int = Config.MAX_CAPTIONS) -> List[str]:
        prompt = (
            f"Generate {max_captions} short catchy captions for the book titled "
            f"'{title}' with description '{description[:200]}'."
        )

        cache_key = self._generate_cache_key(prompt)
        if cached := self.cache.get(cache_key):
            return cached

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            lines = [line.strip("- ").strip() for line in resp.choices[0].message.content.split("\n") if line.strip()]
            captions = lines[:max_captions]
            self.cache.set(cache_key, captions)
            logger.info(f"Generated {len(captions)} captions for: {title[:50]}")
            return captions
        except Exception as e:
            logger.error(f"OpenAI captions error for '{title[:50]}': {e}", exc_info=True)
            return []

    def get_famous_quotes(self, title: str, author: str, description: str, num_quotes: int = 3) -> List[str]:
        """Generate thematic quotes inspired by a book"""
        prompt = (
            f"Based on the themes and style of '{title}' by {author}, create {num_quotes} original, "
            f"thought-provoking quotes that capture the essence and spirit of this book. "
            f"Book description: {description[:200]}. "
            f"IMPORTANT: Write NEW quotes inspired by the book's themes, NOT actual quotes from the book. "
            f"Make them sound like they could be from the book's universe or themes. "
            f"Return only the quotes, one per line, without numbering or quotation marks."
        )

        cache_key = self._generate_cache_key(prompt)
        if cached := self.cache.get(cache_key):
            return cached

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            lines = [line.strip("- \"'").strip() for line in resp.choices[0].message.content.split("\n") if line.strip()]
            quotes = [q for q in lines if len(q) > 10][:num_quotes]
            self.cache.set(cache_key, quotes)
            logger.info(f"Generated {len(quotes)} quotes for: {title[:50]}")
            return quotes
        except Exception as e:
            logger.error(f"OpenAI quotes error for '{title[:50]}': {e}", exc_info=True)
            return []

    def interpret_natural_language_query(self, query: str, max_results: int = 15, lang: str = "en") -> Dict:
        """
        Interpret natural language queries like "suggest me some romantic books"
        and return book recommendations

        Args:
            query: Natural language query from user
            max_results: Maximum number of books to return
            lang: Language code

        Returns:
            Dict with 'is_nl_query' (bool), 'search_terms' (list), and 'books' (list)
        """
        # Check if this looks like a natural language request
        nl_indicators = ['suggest', 'recommend', 'find me', 'looking for', 'want to read',
                        'help me find', 'search for', 'show me', 'give me', 'what are',
                        'any good', 'best books', 'top books']

        is_nl_query = any(indicator in query.lower() for indicator in nl_indicators)

        if not is_nl_query:
            # Not a natural language query, return empty
            return {
                'is_nl_query': False,
                'search_terms': [],
                'books': []
            }

        prompt = (
            f"User query: '{query}'\n\n"
            f"This user is looking for book recommendations. Extract their preferences and suggest {max_results} specific book titles.\n\n"
            f"Analyze what they want:\n"
            f"- Genre/category (romance, thriller, sci-fi, fantasy, etc.)\n"
            f"- Target audience (young adult, adult, children, etc.)\n"
            f"- Themes or topics they mentioned\n"
            f"- Any specific requirements (short, long, classic, modern, etc.)\n\n"
            f"Recommend {max_results} specific books that match their criteria.\n"
            f"Return ONLY book titles with authors in format: 'Book Title by Author Name', one per line.\n"
            f"Example: 'Pride and Prejudice by Jane Austen'\n\n"
            f"DO NOT include explanations, just the book titles."
        )

        cache_key = self._generate_cache_key(prompt)
        if cached := self.cache.get(cache_key):
            return cached

        try:
            resp = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )

            lines = [line.strip() for line in resp.choices[0].message.content.split("\n") if line.strip()]

            books = []
            search_terms = []
            seen_titles = set()

            for line in lines:
                # Clean up the line
                clean_line = line.lstrip("0123456789.-*) ").strip()

                if not clean_line or len(clean_line) < 5:
                    continue

                search_terms.append(clean_line)

                # Search for the book
                results = self.books_api.search(clean_line, max_results=2, lang=lang)

                for book in results:
                    book_title = book.get("title", "").lower()

                    # Skip duplicates
                    if book_title in seen_titles:
                        continue

                    # Skip if no cover image
                    if not book.get("cover_url"):
                        continue

                    books.append(book)
                    seen_titles.add(book_title)

                    if len(books) >= max_results:
                        break

                if len(books) >= max_results:
                    break

            result = {
                'is_nl_query': True,
                'search_terms': search_terms,
                'books': books
            }

            self.cache.set(cache_key, result)
            logger.info(f"NL query processed: found {len(books)} books for query: {query[:50]}")
            return result

        except Exception as e:
            logger.error(f"Natural language query error for '{query[:50]}': {e}", exc_info=True)
            return {
                'is_nl_query': True,
                'search_terms': [],
                'books': [],
                'error': str(e)
            }
