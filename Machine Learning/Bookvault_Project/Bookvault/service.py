from typing import List, Dict, Optional, Any
from .config import Config
from .cache import SQLiteCache
from .apis import GoogleBooksAPI, AIRecommendationEngine
from .utils import ImageProcessor
from .logger import get_logger
from .security import InputValidator, search_rate_limiter

logger = get_logger(__name__)


def filter_books_with_images(books: List[Dict]) -> List[Dict]:
    """
    Filter out books without valid cover images

    Args:
        books: List of book dictionaries

    Returns:
        List of books that have valid cover images
    """
    filtered = []
    for book in books:
        cover_url = book.get("cover_url", "")
        if cover_url and isinstance(cover_url, str) and cover_url.strip() and len(cover_url) > 10:
            filtered.append(book)
    return filtered


class BookVaultService:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        logger.info("Initializing BookVaultService")
        self.cache = SQLiteCache(Config.DB_PATH, Config.CACHE_TTL_HOURS)
        self.books_api = GoogleBooksAPI(self.cache)
        self.ai_engine = AIRecommendationEngine(self.cache, self.books_api)
        self.image_processor = ImageProcessor()
        self._initialized = True
        logger.info("BookVaultService initialized successfully")

    def search_books(self, query: str, max_results: int = 20, lang: str = "en", start_index: int = 0, verify_genre: bool = False, expected_genre: str = "") -> List[Dict]:
        # Validate input
        if Config.ENABLE_INPUT_VALIDATION:
            is_valid, error_msg = InputValidator.validate_search_query(query)
            if not is_valid:
                logger.warning(f"Invalid search query: {error_msg}")
                return []

        # Sanitize query
        query = InputValidator.sanitize_string(query, InputValidator.MAX_QUERY_LENGTH)

        # Rate limiting (optional identifier - can be extended with user ID/IP)
        if Config.RATE_LIMIT_ENABLED:
            is_allowed, limit_msg = search_rate_limiter.is_allowed("global")
            if not is_allowed:
                logger.warning(f"Search rate limit exceeded: {limit_msg}")
                return []

        logger.info(f"Searching books: query='{query[:50]}', max_results={max_results}")
        books = self.books_api.search(query, max_results, lang, start_index)
        logger.info(f"Found {len(books)} books for query: {query[:50]}")

        # Optional AI verification BEFORE filtering for images (more efficient)
        if verify_genre and expected_genre and books:
            # First: AI verifies genre (fast, uses only title/author)
            verified_books = self.ai_engine.verify_books_batch(books, expected_genre)
            logger.info(f"AI verification: {len(verified_books)}/{len(books)} books matched {expected_genre}")

            # Second: Filter for books with valid cover images from AI-verified books
            books_with_covers = filter_books_with_images(verified_books)
            logger.info(f"Cover filter: {len(books_with_covers)}/{len(verified_books)} verified books have covers")
            return books_with_covers

        # No verification - just filter for images
        return filter_books_with_images(books)

    def search_with_ai(self, query: str, max_results: int = 20, lang: str = "en") -> Dict:
        """
        Smart search that can handle both regular queries and natural language requests

        Args:
            query: Search query (can be regular or natural language)
            max_results: Maximum results to return
            lang: Language code

        Returns:
            Dict with 'is_ai_search' (bool), 'books' (list), and optional 'message' (str)
        """
        # Try natural language interpretation first
        nl_result = self.ai_engine.interpret_natural_language_query(query, max_results, lang)

        if nl_result['is_nl_query'] and nl_result['books']:
            return {
                'is_ai_search': True,
                'books': filter_books_with_images(nl_result['books']),
                'search_terms': nl_result.get('search_terms', []),
                'message': f"🤖 AI found {len(nl_result['books'])} recommendations based on your request!"
            }
        elif nl_result['is_nl_query']:
            # It was a natural language query but no results, fall back to regular search
            regular_results = self.books_api.search(query, max_results, lang)
            return {
                'is_ai_search': True,
                'books': filter_books_with_images(regular_results),
                'message': "🤖 AI couldn't find specific matches, showing general search results"
            }
        else:
            # Regular search query
            regular_results = self.books_api.search(query, max_results, lang)
            return {
                'is_ai_search': False,
                'books': filter_books_with_images(regular_results),
                'message': None
            }

    def get_books_by_genre(self, genre: str, max_results: int = 10, lang: str = "en", start_index: int = 0) -> List[Dict]:
        books = self.books_api.search(f"subject:{genre}", max_results, lang, start_index)
        return filter_books_with_images(books)

    def get_random_popular_books(self, count: int = 10, lang: str = "en") -> List[Dict]:
        books = self.books_api.search("bestseller", count, lang)
        return filter_books_with_images(books)

    def get_similar_books_ai(self, title: str, author: str, description: str,
                             categories: str, lang: str = "en", max_results: int = 5) -> List[Dict]:
        books = self.ai_engine.get_recommendations(title, author, description, categories, lang, max_results)
        return filter_books_with_images(books)

    def get_best_captions(self, title: str, description: str,
                          max_captions: int = Config.MAX_CAPTIONS) -> List[str]:
        return self.ai_engine.get_captions(title, description, max_captions)

    def get_famous_quotes(self, title: str, author: str, description: str, num_quotes: int = 3) -> List[str]:
        return self.ai_engine.get_famous_quotes(title, author, description, num_quotes)

    def extract_text_from_image(self, uploaded_file) -> Optional[str]:
        return self.image_processor.extract_text(uploaded_file)

    def clear_cache(self) -> None:
        """Clear all cache entries"""
        self.cache.clear()

    def clear_old_cache(self) -> int:
        """Clear old cache entries and return count"""
        return self.cache.clear_old_entries()

    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache.get_stats()
