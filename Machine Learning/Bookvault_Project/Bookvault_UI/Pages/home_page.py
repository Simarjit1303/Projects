"""
Home page with hero section and genre-based browsing
"""
import streamlit as st
import random
from typing import List, Dict, Optional, Tuple
from Bookvault.service import BookVaultService
from Bookvault.logger import get_logger
from Bookvault.config import Config

logger = get_logger(__name__)


class HomePage:
    """Home page with hero banner and genre browsing"""

    def __init__(self, service: BookVaultService):
        self.service = service
        # Genre list: First 7 are shown in "All Genres" view (6 genres displayed)
        self.genres = [
            "All Genres",  # Shows first 6 genres below
            "Fiction",
            "Thriller",
            "Mystery",
            "Fantasy",
            "Romance",
            "Horror"
        ]

    def render(self) -> None:
        """Render the home page"""
        # Hero section
        self._render_hero()

        # Search bar
        self._render_search()

        # Genre browsing
        self._render_genre_browsing()

    def _render_hero(self) -> None:
        """Render hero section"""
        st.markdown("""
        <div class="hero-section">
            <h1 class="hero-title">📚 BOOKVAULT</h1>
            <h2 class="hero-subtitle">Discover Your Next Literary Adventure</h2>
            <p class="hero-description">✨ AI-Powered Discovery • 🎯 Smart Recommendations • 🌍 Millions of Titles</p>
        </div>
        """, unsafe_allow_html=True)

    def _render_search(self) -> None:
        """Render AI-powered search bar and image upload"""
        # Check if there's a pending search from suggestions
        if "pending_search" in st.session_state:
            pending_query = st.session_state.pending_search
            del st.session_state.pending_search
            self._handle_ai_search(pending_query)
            return

        col1, col2 = st.columns([20, 1])

        with col1:
            search_query = st.text_input(
                "Search for a book...",
                placeholder="🤖 Try AI search: 'books about mystery' or 'scary thriller novels' or 'fantasy like Harry Potter'...",
                label_visibility="collapsed",
                key="home_search"
            )

            if search_query and len(search_query) > 2:
                self._handle_ai_search(search_query)

        with col2:
            # Pure HTML camera icon - same approach as book images
            st.markdown("""
            <a href="?camera=true" style="text-decoration: none; display: block; text-align: center;">
                <div class="camera-icon" style="
                    font-size: 2.2rem;
                    cursor: pointer;
                    margin-top: -4px;
                    line-height: 1;
                    transition: transform 0.2s ease, filter 0.2s ease;
                    user-select: none;
                ">📸</div>
            </a>

            <style>
            .camera-icon:hover {
                transform: scale(1.15);
                filter: drop-shadow(0 0 16px rgba(6, 182, 212, 0.9));
            }
            .camera-icon:active {
                transform: scale(1.05);
            }
            </style>
            """, unsafe_allow_html=True)

            # Check if camera was clicked via URL parameter
            if st.query_params.get("camera") == "true":
                st.session_state.show_image_modal = True
                st.query_params.clear()
                st.rerun()

        # Image upload modal (shows when button clicked)
        if st.session_state.get('show_image_modal', False):
            self._render_image_modal()

    def _render_image_modal(self) -> None:
        """Render image upload modal"""
        st.markdown("### 📸 Search by Book Cover")
        uploaded_file = st.file_uploader(
            "Upload a book cover image",
            type=['png', 'jpg', 'jpeg'],
            key="image_uploader"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Cancel", key="cancel_image", type="primary"):
                st.session_state.show_image_modal = False
                st.rerun()

        with col2:
            if uploaded_file and st.button("Search", key="search_image", type="primary"):
                try:
                    with st.spinner("📸 Analyzing image..."):
                        extracted_text = self.service.extract_text_from_image(uploaded_file)
                        if extracted_text:
                            from ..App_Pro import cached_search_books
                            st.session_state.search_results = cached_search_books(
                                extracted_text,
                                max_results=24,
                                cache_key=st.session_state.cache_key
                            )
                            st.session_state.show_image_modal = False
                            st.session_state.page = "search_results"
                            st.rerun()
                        else:
                            st.error("Could not extract text from image")
                except Exception as e:
                    st.error(f"Error processing image: {str(e)}")

    def _handle_ai_search(self, query: str) -> None:
        """Handle AI-powered natural language search with typo correction"""
        try:
            from ..App_Pro import cached_search_books
            from Bookvault.search_intelligence import SearchIntelligence

            # Initialize search intelligence
            search_ai = SearchIntelligence()

            # Check if it's a natural language query (contains keywords like "about", "books", "want", etc.)
            nl_keywords = ['about', 'books', 'novel', 'read', 'want', 'looking for', 'recommend', 'like', 'similar to']
            is_nl_query = any(keyword in query.lower() for keyword in nl_keywords)

            if is_nl_query:
                # Use AI to extract search terms and get recommendations
                with st.spinner("🤖 AI is understanding your request..."):
                    ai_results = self._get_ai_book_recommendations(query)

                    # Analyze results for quality
                    suggested_correction, should_auto_correct = search_ai.analyze_query_and_results(
                        query, ai_results
                    )

                    if ai_results:
                        st.session_state.search_results = ai_results
                        st.session_state.ai_search_query = query
                        st.session_state.original_query = query
                        st.session_state.suggested_correction = suggested_correction
                        st.session_state.alternative_queries = search_ai.suggest_alternative_queries(query)
                        st.session_state.page = "search_results"
                        st.rerun()
                    elif suggested_correction and should_auto_correct:
                        # Auto-correct and search again
                        logger.info(f"Auto-correcting '{query}' to '{suggested_correction}'")
                        st.info(f"🔍 Searching for: '{suggested_correction}' (corrected from '{query}')")
                        ai_results = self._get_ai_book_recommendations(suggested_correction)
                        if ai_results:
                            st.session_state.search_results = ai_results
                            st.session_state.ai_search_query = suggested_correction
                            st.session_state.original_query = query
                            st.session_state.corrected_query = suggested_correction
                            st.session_state.page = "search_results"
                            st.rerun()
                        else:
                            st.warning("No books found even with correction. Try a different description.")
                    else:
                        st.warning("No books found for your query. Try a different description.")
            else:
                # Direct search for book title/author
                with st.spinner("🔍 Searching..."):
                    results = cached_search_books(query, max_results=24, cache_key=st.session_state.cache_key)

                    # Analyze results and suggest corrections
                    suggested_correction, should_auto_correct = search_ai.analyze_query_and_results(
                        query, results
                    )

                    if results and len(results) >= 3:
                        # Good results, show them
                        st.session_state.search_results = results
                        st.session_state.original_query = query
                        st.session_state.page = "search_results"
                        st.rerun()
                    elif suggested_correction and should_auto_correct:
                        # No results, auto-correct and try again
                        logger.info(f"Auto-correcting '{query}' to '{suggested_correction}'")
                        corrected_results = cached_search_books(
                            suggested_correction, max_results=24, cache_key=st.session_state.cache_key
                        )
                        if corrected_results:
                            st.session_state.search_results = corrected_results
                            st.session_state.original_query = query
                            st.session_state.corrected_query = suggested_correction
                            st.session_state.page = "search_results"
                            st.rerun()
                        else:
                            # Still no results, show suggestions
                            st.session_state.search_results = []
                            st.session_state.original_query = query
                            st.session_state.suggested_correction = suggested_correction
                            st.session_state.alternative_queries = search_ai.suggest_alternative_queries(query)
                            st.session_state.page = "search_results"
                            st.rerun()
                    elif results:
                        # Few results, show them with suggestions
                        st.session_state.search_results = results
                        st.session_state.original_query = query
                        st.session_state.suggested_correction = suggested_correction
                        st.session_state.alternative_queries = search_ai.suggest_alternative_queries(query)
                        st.session_state.page = "search_results"
                        st.rerun()
                    else:
                        # No results at all
                        st.session_state.search_results = []
                        st.session_state.original_query = query
                        st.session_state.suggested_correction = suggested_correction
                        st.session_state.alternative_queries = search_ai.suggest_alternative_queries(query)
                        st.session_state.page = "search_results"
                        st.rerun()
        except Exception as e:
            logger.error(f"Search error: {str(e)}")
            st.error(f"Search error: {str(e)}")

    def _get_ai_book_recommendations(self, user_query: str) -> List[Dict]:
        """Use AI to understand natural language and recommend books"""
        from Bookvault.utils.ai_helpers import get_ai_book_recommendations
        from ..App_Pro import cached_search_books

        return get_ai_book_recommendations(
            user_query=user_query,
            search_function=cached_search_books,
            max_results=24,
            cache_key=st.session_state.cache_key
        )

    def _render_genre_browsing(self) -> None:
        """Render genre browsing section"""
        st.markdown("""
        <div class="section-header">
            🎭 EXPLORE BY GENRE
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p style="color: #9ca3af; padding-left: 24px; margin-bottom: 20px; font-size: 1rem;">Choose your favorite genre and start exploring:</p>', unsafe_allow_html=True)

        selected_genre = st.selectbox(
            "Genre",
            options=self.genres,
            index=0,
            label_visibility="collapsed",
            key="genre_selector"
        )

        # Show books for selected genre
        if selected_genre == "All Genres":
            self._render_all_genres()
        else:
            self._render_single_genre(selected_genre)

    def _render_all_genres(self) -> None:
        """Render books from multiple genres - 12 books initially, with Load More option"""
        import time

        display_genres = [g for g in self.genres if g != "All Genres"][:6]

        for idx, genre in enumerate(display_genres):
            is_last_genre = (idx == len(display_genres) - 1)
            made_api_call = self._render_genre_section(genre, idx, is_last_genre)

            # Add delay between API calls to avoid rate limiting (but not after last genre)
            if not is_last_genre and made_api_call:
                time.sleep(Config.GENRE_API_DELAY_SECONDS)
                logger.info(f"Added {Config.GENRE_API_DELAY_SECONDS}s delay after loading {genre} to avoid rate limiting")

    def _render_genre_section(self, genre: str, idx: int, is_last_genre: bool) -> bool:
        """
        Render a single genre section in the All Genres view

        Returns:
            bool: True if an API call was made, False otherwise
        """
        from ..App_Pro import cached_search_books
        from ..Components import modern_book_card

        st.markdown(f"""
        <div class="section-header">
            {self._get_genre_emoji(genre)} {genre.upper()}
        </div>
        """, unsafe_allow_html=True)

        state_key = f"all_genres_{genre}_count"
        books_cache_key = f"all_genres_{genre}_books"

        # Initialize state
        if state_key not in st.session_state:
            st.session_state[state_key] = Config.BOOKS_PER_PAGE_INITIAL

        books_to_display = st.session_state[state_key]
        made_api_call = False

        try:
            # Get or fetch books for this genre
            all_books, api_called = self._get_or_fetch_genre_books(
                genre, books_cache_key, books_to_display
            )
            made_api_call = api_called

            # Display the books
            self._display_genre_books(genre, all_books, books_to_display, state_key)

        except Exception as e:
            logger.error(f"EXCEPTION [{genre}]: {str(e)}", exc_info=True)
            st.error(f"Could not load {genre} books: {str(e)}")

        return made_api_call

    def _get_or_fetch_genre_books(
        self, genre: str, books_cache_key: str, books_to_display: int
    ) -> Tuple[List[Dict], bool]:
        """
        Get cached books or fetch new ones for a genre

        Returns:
            tuple: (list of books, whether API call was made)
        """
        from ..App_Pro import cached_search_books

        made_api_call = False

        # Check if we have cached books
        if books_cache_key in st.session_state:
            all_books = st.session_state[books_cache_key]
            logger.info(f"Using cached books for [{genre}]: {len(all_books)} books available")

            # Lazy load more if needed
            if books_to_display > len(all_books) - 3 and len(all_books) < Config.MAX_BOOKS_PER_GENRE:
                made_api_call = True
                all_books = self._fetch_more_books_for_genre(genre, all_books)
                st.session_state[books_cache_key] = all_books
        else:
            # First time - fetch and cache
            made_api_call = True
            all_books = self._fetch_initial_books_for_genre(genre)
            st.session_state[books_cache_key] = all_books

        return all_books, made_api_call

    def _fetch_more_books_for_genre(self, genre: str, all_books: List[Dict]) -> List[Dict]:
        """Fetch additional books for a genre (lazy loading)"""
        from ..App_Pro import cached_search_books

        logger.info(f"Need more books for [{genre}]. Have {len(all_books)}")
        existing_ids = {
            book.get("id") or f"{book.get('title', '')}_{book.get('author', '')}"
            for book in all_books
        }

        # Fetch next batch from a new position
        random.seed(hash(genre + st.session_state.cache_key + str(len(all_books))))
        next_position = random.randint(len(all_books), 150)

        books = cached_search_books(
            f"subject:{genre}",
            max_results=40,
            start_index=next_position,
            cache_key=st.session_state.cache_key,
            verify_genre=False,
            expected_genre=genre
        )

        logger.info(f"Fetched {len(books)} more books for [{genre}] at position {next_position}")

        # Add unique books
        for book in books:
            book_id = book.get("id") or f"{book.get('title', '')}_{book.get('author', '')}"
            if book_id and book_id not in existing_ids:
                all_books.append(book)
                existing_ids.add(book_id)

        logger.info(f"Updated cache for [{genre}]: now {len(all_books)} books")
        return all_books

    def _fetch_initial_books_for_genre(self, genre: str) -> List[Dict]:
        """Fetch initial books for a genre (first time)"""
        from ..App_Pro import cached_search_books

        random.seed(hash(genre + st.session_state.cache_key))
        random_start = random.randint(0, 20)

        all_books = []
        existing_ids = set()
        target_books = 20

        books = cached_search_books(
            f"subject:{genre}",
            max_results=40,
            start_index=random_start,
            cache_key=st.session_state.cache_key,
            verify_genre=False,
            expected_genre=genre
        )

        logger.info(f"DEBUG [{genre}]: Received {len(books)} books from API at position {random_start}")
        if books:
            logger.info(f"   First book: {books[0].get('title', 'NO TITLE')} (ID: {books[0].get('id', 'NO ID')})")

        # Add unique books
        for book in books:
            book_id = book.get("id") or f"{book.get('title', '')}_{book.get('author', '')}"
            if book_id and book_id not in existing_ids:
                all_books.append(book)
                existing_ids.add(book_id)

        logger.info(f"   Total unique books: {len(all_books)}")

        # Shuffle once and cache
        random.shuffle(all_books)
        logger.info(f"Cached shuffled books for [{genre}]: {len(all_books)} books")
        return all_books

    def _display_genre_books(
        self, genre: str, all_books: List[Dict], books_to_display: int, state_key: str
    ) -> None:
        """Display books in a grid with Load More button"""
        from ..Components import modern_book_card

        books_shown = all_books[:books_to_display]
        has_more_books = len(all_books) > books_to_display

        logger.info(f"FINAL [{genre}]: Showing {len(books_shown)} books, {len(all_books)} available")

        # Store books in session state for detail page access
        self._store_books_in_session(all_books)

        # Display books grid
        if books_shown:
            st.markdown('<div class="book-grid">', unsafe_allow_html=True)
            cols = st.columns(6)
            for idx, book in enumerate(books_shown):
                with cols[idx % 6]:
                    modern_book_card.render(book, f"all_{genre}_{idx}")
            st.markdown('</div>', unsafe_allow_html=True)

            # Show Load More button
            not_at_limit = books_to_display < Config.MAX_BOOKS_PER_GENRE
            if has_more_books and not_at_limit:
                st.markdown('<div style="margin-top: -8px;"></div>', unsafe_allow_html=True)
                if st.button(f"📚 Load More {genre}", key=f"load_more_all_{genre}", type="primary"):
                    st.session_state[state_key] += Config.BOOKS_PER_LOAD_MORE
                    st.rerun()
        else:
            st.info(f"No {genre} books found")

    def _store_books_in_session(self, books: List[Dict]) -> None:
        """Store books in session state for detail page access"""
        if "all_books" not in st.session_state:
            st.session_state.all_books = {}

        for book in books:
            book_id = book.get("id") or f"{book.get('title', '')}_{book.get('author', '')}"
            if book_id:
                st.session_state.all_books[book_id] = book

    def _initialize_single_genre_state(self, genre: str) -> None:
        """Initialize session state for single genre view"""
        if f"genre_page_{genre}" not in st.session_state:
            st.session_state[f"genre_page_{genre}"] = 0

    def _fetch_single_genre_books(self, genre: str, books_cache_key: str) -> List[Dict]:
        """Fetch and cache books for a single genre"""
        from ..App_Pro import cached_search_books

        # Use cached books if available
        if books_cache_key in st.session_state:
            return st.session_state[books_cache_key]

        # First time - fetch and shuffle books
        random.seed(hash(genre + st.session_state.cache_key))
        random_start = random.randint(0, 10)

        all_valid_books = []
        existing_ids = set()
        target_books = 50
        start_index = random_start
        fetch_count = 0
        max_total_fetches = 30
        consecutive_empty = 0

        # Fetch books with pagination
        while len(all_valid_books) < target_books and fetch_count < max_total_fetches:
            books = cached_search_books(
                f"subject:{genre}",
                max_results=40,
                start_index=start_index,
                cache_key=st.session_state.cache_key,
                verify_genre=False,
                expected_genre=genre
            )

            fetch_count += 1

            if not books:
                consecutive_empty += 1
                if consecutive_empty >= 3:
                    start_index = 0
                    consecutive_empty = 0
                else:
                    start_index = random.randint(0, 100)
                continue

            consecutive_empty = 0

            # Add unique books
            for book in books:
                book_id = book.get("id") or f"{book.get('title', '')}_{book.get('author', '')}"
                if book_id and book_id not in existing_ids:
                    all_valid_books.append(book)
                    existing_ids.add(book_id)

                    if len(all_valid_books) >= target_books:
                        break

            start_index += 80

        # Shuffle and cache
        random.shuffle(all_valid_books)
        st.session_state[books_cache_key] = all_valid_books
        logger.info(f"Cached shuffled books for [{genre}]: {len(all_valid_books)} books")

        return all_valid_books

    def _render_single_genre(self, genre: str) -> None:
        """Render books from a single genre with load more - start with 12, add 6 each time"""
        from ..Components import modern_book_card

        st.markdown(f"""
        <div class="section-header">
            {self._get_genre_emoji(genre)} {genre.upper()}
        </div>
        """, unsafe_allow_html=True)

        # Initialize state
        self._initialize_single_genre_state(genre)

        # Cache key for storing books
        books_cache_key = f"single_genre_{genre}_books"

        try:
            # Calculate how many books to show (start with 12, add 6 per click)
            page = st.session_state[f"genre_page_{genre}"]
            books_to_display = 12 + (page * 6)  # Initial 12 + 6 per load more click

            # Fetch books (uses cache if available)
            all_valid_books = self._fetch_single_genre_books(genre, books_cache_key)

            # Display books in grid (6 per row)
            if all_valid_books:
                books_shown = all_valid_books[:books_to_display]

                # CRITICAL: Store ALL books in session state BEFORE rendering
                # This ensures they're available when user clicks (before cards render)
                if "all_books" not in st.session_state:
                    st.session_state.all_books = {}
                for book in all_valid_books:  # Store ALL fetched books, not just shown ones
                    book_id = book.get("id") or f"{book.get('title', '')}_{book.get('author', '')}"
                    if book_id:
                        st.session_state.all_books[book_id] = book

                st.markdown('<div class="book-grid">', unsafe_allow_html=True)
                cols = st.columns(6)
                for idx, book in enumerate(books_shown):
                    with cols[idx % 6]:
                        modern_book_card.render(book, f"{genre}_single_{idx}")
                st.markdown('</div>', unsafe_allow_html=True)

                # Show load more button if there are more books available
                has_more_books = len(all_valid_books) > books_to_display
                not_at_limit = books_to_display < 48  # Max 48 books (8 rows)

                if has_more_books and not_at_limit:
                    st.markdown('<div style="margin-top: -8px;"></div>', unsafe_allow_html=True)
                    if st.button(f"📚 Load More", key=f"load_more_{genre}", type="primary"):
                        st.session_state[f"genre_page_{genre}"] += 1
                        st.rerun()
                elif not has_more_books and len(books_shown) < books_to_display:
                    st.info(f"Found {len(books_shown)} {genre} books with covers (tried {fetch_count} fetches)")
            else:
                st.info(f"No {genre} books found (tried {fetch_count} fetches)")

        except Exception as e:
            st.error(f"Could not load {genre} books: {str(e)}")

    @staticmethod
    def _get_genre_emoji(genre: str) -> str:
        """Get emoji for genre"""
        emoji_map = {
            "Fiction": "📚",
            "Thriller": "⚡",
            "Mystery": "🔍",
            "Fantasy": "🐉",
            "Romance": "💖",
            "Horror": "🎃",
            "Biography": "👤",
            "History": "📜",
            "Self-Help": "💡",
            "Poetry": "✍️"
        }
        return emoji_map.get(genre, "📖")
