import requests
import time
from typing import List, Dict
from ..config import Config
from ..cache import CacheProvider
from ..models import Book
from ..logger import get_logger

logger = get_logger(__name__)


class GoogleBooksAPI:
    def __init__(self, cache: CacheProvider):
        self.cache = cache
        self.api_key = Config.GOOGLE_BOOKS_API

    def search(self, query: str, max_results: int = 20, lang: str = "en", start_index: int = 0) -> List[Dict]:
        cache_key = f"search:{query}:{lang}:{max_results}:{start_index}"
        if cached := self.cache.get(cache_key):
            logger.debug(f"Cache hit for query: {query[:50]}")
            return cached

        logger.info(f"Google Books API search: query='{query[:50]}', max_results={max_results}, start_index={start_index}")

        retry_count = 0
        while retry_count < Config.MAX_RETRIES:
            try:
                params = {"q": query, "maxResults": min(max_results, Config.MAX_SEARCH_RESULTS), "langRestrict": lang}
                if start_index > 0:
                    params["startIndex"] = start_index
                if self.api_key:
                    params["key"] = self.api_key

                res = requests.get("https://www.googleapis.com/books/v1/volumes", params=params, timeout=Config.TIMEOUT)
                res.raise_for_status()

                books = []
                items = res.json().get("items", [])
                logger.debug(f"Received {len(items)} items from Google Books API")

                for item in items:
                    book = Book.from_google_api(item)
                    # Only include books with valid cover images
                    cover_url = getattr(book, 'cover_url', '')
                    if cover_url and cover_url.strip() and len(cover_url) > 10:  # Must have actual URL
                        books.append(book.to_dict())

                logger.info(f"Processed {len(books)} valid books (with covers) from {len(items)} items")
                self.cache.set(cache_key, books)
                return books

            except requests.exceptions.HTTPError as e:
                # Handle 429 rate limit errors with exponential backoff
                if e.response is not None and e.response.status_code == 429:
                    retry_count += 1
                    if retry_count >= Config.MAX_RETRIES:
                        logger.error(f"Google Books API rate limit - failed after {Config.MAX_RETRIES} retries")
                        return []

                    # Exponential backoff: 2s, 4s, 8s
                    backoff_time = 2 ** retry_count
                    logger.warning(f"Google Books API rate limit (429) - waiting {backoff_time}s before retry {retry_count}/{Config.MAX_RETRIES}")
                    time.sleep(backoff_time)
                    continue  # Retry the request
                else:
                    # Other HTTP errors - don't retry
                    logger.error(f"Google Books API HTTP error: {e}")
                    return []

            except requests.exceptions.Timeout:
                retry_count += 1
                logger.warning(f"Google Books API timeout (attempt {retry_count}/{Config.MAX_RETRIES})")
                if retry_count >= Config.MAX_RETRIES:
                    logger.error(f"Google Books API failed after {Config.MAX_RETRIES} retries")
                    return []
                # Add small delay before timeout retry
                time.sleep(1)
                continue

            except requests.exceptions.RequestException as e:
                # Check if this is a rate limit error without HTTPError wrapper
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 429:
                    retry_count += 1
                    if retry_count >= Config.MAX_RETRIES:
                        logger.error(f"Google Books API rate limit - failed after {Config.MAX_RETRIES} retries")
                        return []

                    backoff_time = 2 ** retry_count
                    logger.warning(f"Google Books API rate limit (429) - waiting {backoff_time}s before retry {retry_count}/{Config.MAX_RETRIES}")
                    time.sleep(backoff_time)
                    continue
                else:
                    # Other request errors - don't retry
                    logger.error(f"Google Books API request error: {e}")
                    return []

            except Exception as e:
                logger.error(f"Google Books API unexpected error: {e}", exc_info=True)
                return []

        return []
