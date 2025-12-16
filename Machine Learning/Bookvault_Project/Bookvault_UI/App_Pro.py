"""
BookVault Pro - AI-Powered Book Discovery Platform
Modern redesign with dark theme and modular architecture
"""

import sys
sys.path.insert(0, ".")

from typing import Dict, Optional
import streamlit as st
from Bookvault.service import BookVaultService
from Bookvault_UI.Components.styles import get_global_styles
from Bookvault_UI.Pages import HomePage, DetailPage
from Bookvault_UI.UI_config import APP_TITLE, APP_ICON, PAGE_ICON


# ============================================================================
# CACHING LAYER
# ============================================================================

@st.cache_resource
def get_service() -> BookVaultService:
    """Get or create service instance (cached across reruns)"""
    return BookVaultService()


def cached_search_books(query: str, max_results: int = 20, lang: str = "en", start_index: int = 0, cache_key: str = "", verify_genre: bool = False, expected_genre: str = ""):
    """Search books - SQLite cache handles caching at service layer"""
    service = get_service()
    return service.search_books(query, max_results, lang, start_index, verify_genre, expected_genre)


@st.cache_data(ttl=7200, show_spinner=False)
def cached_ai_recommendations(title: str, author: str, description: str, categories: str, lang: str = "en", max_results: int = 5):
    """Cached wrapper for AI recommendations (2 hours TTL)"""
    service = get_service()
    return service.get_similar_books_ai(title, author, description, categories, lang, max_results)


# ============================================================================
# STATE MANAGEMENT
# ============================================================================

class StateManager:
    """Manages Streamlit session state"""

    @staticmethod
    def initialize():
        """Initialize all session state variables"""
        import time

        if "session_initialized" not in st.session_state:
            try:
                service = get_service()
                service.clear_old_cache()
            except:
                pass
            st.session_state.session_initialized = True

        # Generate cache key only once per session (for consistent book ordering)
        if "cache_key" not in st.session_state:
            st.session_state.cache_key = str(time.time())

        defaults = {
            "page": "home",
            "nav_tab": "home",
            "selected_book": None,
            "search_results": [],
            "show_image_modal": False,
            "last_page": "home",
            "all_books": {},  # Persistent storage for all rendered books
            "back_clicked": False  # Track back button clicks to prevent query param re-processing
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value


# ============================================================================
# MAIN APPLICATION
# ============================================================================

class BookVaultApp:
    """Main application class"""

    def __init__(self):
        self.service = get_service()
        self.setup_page()
        StateManager.initialize()

    def setup_page(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title=APP_TITLE,
            page_icon=APP_ICON,
            layout="wide",
            initial_sidebar_state="collapsed"
        )

        # Apply global styles
        st.markdown(get_global_styles(), unsafe_allow_html=True)

    def _fetch_book_by_api(self, book_id: str) -> Optional[Dict]:
        """
        Fetch book from Google Books API by ID

        Args:
            book_id: Google Books API book ID

        Returns:
            Book dictionary or None if not found
        """
        import requests
        from Bookvault.models import Book
        import logging

        logger = logging.getLogger(__name__)

        try:
            logger.info(f"Attempting to fetch book from Google Books API with ID: {book_id}")
            response = requests.get(
                f"https://www.googleapis.com/books/v1/volumes/{book_id}",
                params={"key": self.service.books_api.api_key} if self.service.books_api.api_key else {},
                timeout=10
            )

            if response.status_code == 404:
                logger.info(f"ID not found in Google Books API (404), treating as fallback ID")
                return None

            response.raise_for_status()
            item = response.json()

            # Convert to Book object and then to dict
            book = Book.from_google_api(item)
            book_dict = book.to_dict()

            logger.info(f"Successfully fetched book: {book_dict.get('title', 'Unknown')}")
            return book_dict

        except Exception as e:
            logger.error(f"Failed to fetch book from API with ID '{book_id}': {str(e)}", exc_info=True)
            return None

    def _search_book_by_fallback_id(self, book_id: str) -> Optional[Dict]:
        """
        Search for book using fallback ID (Title_Author format)

        Args:
            book_id: Fallback ID in format "Title_Author"

        Returns:
            Book dictionary or None if not found
        """
        import logging
        logger = logging.getLogger(__name__)

        parts = book_id.split("_")
        if len(parts) < 2:
            return None

        title = parts[0]
        author = parts[1] if len(parts) > 1 else ""

        logger.info(f"Fallback ID detected, searching for book: {title} by {author}")

        try:
            search_query = f"{title} {author}".strip()
            books = self.service.search_books(search_query, max_results=1)

            if books and len(books) > 0:
                found_book = books[0]
                logger.info(f"Found book via search: {found_book.get('title', 'Unknown')}")
                return found_book
            else:
                logger.error(f"Could not find book via search")
                return None

        except Exception as e:
            logger.error(f"Failed to search for book '{title}' by '{author}': {str(e)}", exc_info=True)
            return None

    def _handle_query_params(self) -> bool:
        """
        Handle query parameters for book navigation

        Returns:
            True if query param was handled, False otherwise
        """
        from urllib.parse import unquote
        import logging
        logger = logging.getLogger(__name__)

        query_params = st.query_params

        # Check if we have a pending book navigation from query params
        # Only process the query param if back button wasn't just clicked
        if "selected" not in query_params or st.session_state.get("back_clicked", False):
            return False

        if st.session_state.get("back_clicked", False):
            st.session_state.back_clicked = False
            return False

        encoded_book_id = query_params["selected"]
        book_id = unquote(encoded_book_id)

        logger.info(f"Query param detected: book_id={book_id}. Attempting direct navigation...")

        # Check if book is already in session state
        all_books = st.session_state.get("all_books", {})
        if book_id in all_books:
            logger.info(f"Book found in all_books! Navigating immediately")
            st.session_state.selected_book = all_books[book_id]
            st.session_state.page = "detail"
            st.query_params.clear()
            st.rerun()
            return True

        # Determine if fallback ID or real Google Books ID
        is_fallback_id = "_" in book_id and (" " in book_id or not book_id.isalnum())

        if is_fallback_id:
            # Handle fallback ID
            logger.info(f"Detected fallback ID format: {book_id}")
            with st.spinner(f"📚 Finding book..."):
                found_book = self._search_book_by_fallback_id(book_id)

                if found_book:
                    st.session_state.all_books[book_id] = found_book
                    st.session_state.selected_book = found_book
                    st.session_state.page = "detail"
                    st.query_params.clear()
                    st.rerun()
                    return True
                else:
                    st.query_params.clear()
                    st.warning("⚠️ Could not find this book in the catalog.")
                    st.info(f"💡 Tip: Try clicking on books from different genres!")
                    if st.button("⬅️ Back", type="primary"):
                        st.session_state.page = "home"
                        st.rerun()
                    return True
        else:
            # Handle real Google Books ID
            logger.info(f"Book not in session, fetching directly from API...")
            with st.spinner("📚 Loading book..."):
                book_dict = self._fetch_book_by_api(book_id)

                if book_dict:
                    st.session_state.all_books[book_id] = book_dict
                    st.session_state.selected_book = book_dict
                    st.session_state.page = "detail"
                    st.query_params.clear()
                    st.rerun()
                    return True
                else:
                    st.query_params.clear()
                    st.warning("⚠️ This book is not available in the catalog.")
                    st.info(f"💡 Tip: Try clicking on books from different genres!")
                    if st.button("⬅️ Back", type="primary"):
                        st.session_state.page = "home"
                        st.rerun()
                    return True

    def run(self):
        """Run the application"""
        # Handle query parameters for book navigation
        if self._handle_query_params():
            return

        # Reset back_clicked flag
        if st.session_state.get("back_clicked", False):
            st.session_state.back_clicked = False

        # Route to appropriate page
        self.route()

    def route(self):
        """Route to the appropriate page"""
        page = st.session_state.get("page", "home")

        # Track page changes for cache invalidation
        if "last_page" in st.session_state and st.session_state.last_page != page:
            st.session_state.last_page = page

        if page == "home":
            # Normal home page rendering
            home_page = HomePage(self.service)
            home_page.render()

        elif page == "detail":
            selected_book = st.session_state.get("selected_book")
            if selected_book:
                detail_page = DetailPage(self.service, selected_book)
                detail_page.render()
            else:
                st.error("No book selected")
                if st.button("⬅️ Back", type="primary"):
                    st.query_params.clear()
                    st.session_state.page = "home"
                    st.rerun()

        elif page == "search_results":
            self.render_search_results()

        else:
            st.session_state.page = "home"
            st.rerun()

    def render_search_results(self):
        """Render search results page with AI-powered suggestions"""
        from Bookvault_UI.Components import modern_book_card

        if st.button("⬅️ Back", key="search_back", type="primary"):
            st.query_params.clear()
            st.session_state.page = "home"
            st.session_state.search_results = []
            # Clean up search-related session state
            for key in ["ai_search_query", "original_query", "suggested_correction", "corrected_query", "alternative_queries"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

        results = st.session_state.get("search_results", [])
        ai_query = st.session_state.get("ai_search_query")
        original_query = st.session_state.get("original_query")
        corrected_query = st.session_state.get("corrected_query")
        suggested_correction = st.session_state.get("suggested_correction")
        alternative_queries = st.session_state.get("alternative_queries", [])

        # Show correction notice if query was auto-corrected
        if corrected_query and corrected_query != original_query:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(5, 150, 105, 0.05));
                        border-left: 4px solid #10b981; padding: 16px 20px; margin: 0 24px 20px 24px;
                        border-radius: 8px;">
                <p style="color: #10b981; margin: 0; font-size: 1rem;">
                    🔍 Showing results for: <strong>"{corrected_query}"</strong>
                </p>
                <p style="color: #9ca3af; margin: 8px 0 0 0; font-size: 0.9rem;">
                    Original search: "{original_query}"
                </p>
            </div>
            """, unsafe_allow_html=True)

        if results:
            # Show AI search indicator if it was an AI search
            if ai_query:
                st.markdown(f"""
                <div class="section-header">
                    🤖 AI Recommendations for: "{ai_query}"
                </div>
                <p style="color: #9ca3af; padding: 0 24px 16px 24px; font-size: 1rem;">
                    ✨ Found {len(results)} books curated by AI based on your request
                </p>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="section-header">
                    🔍 Search Results
                </div>
                <p style="color: #9ca3af; padding: 0 24px 16px 24px; font-size: 1rem;">
                    Found {len(results)} books matching your search
                </p>
                """, unsafe_allow_html=True)

            # Show "Did you mean?" suggestion if few results and we have a correction
            if len(results) < 5 and suggested_correction and suggested_correction != (corrected_query or original_query):
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6;
                            padding: 16px 20px; margin: 0 24px 20px 24px; border-radius: 8px;">
                    <p style="color: #3b82f6; margin: 0; font-size: 1rem;">
                        💡 Did you mean: <strong>"{suggested_correction}"</strong>?
                    </p>
                </div>
                """, unsafe_allow_html=True)

                # Add clickable button to search with correction
                if st.button(f"🔍 Search for '{suggested_correction}' instead", key="search_correction", type="secondary"):
                    from Bookvault_UI.Pages.home_page import HomePage
                    home_page = HomePage(self.service)
                    # Trigger new search with corrected query
                    st.session_state.page = "home"
                    # Set a flag to trigger search on next render
                    st.session_state.pending_search = suggested_correction
                    st.rerun()

            # Display in grid
            st.markdown('<div class="book-grid">', unsafe_allow_html=True)
            cols = st.columns(6)
            for idx, book in enumerate(results):
                with cols[idx % 6]:
                    modern_book_card.render(book, f"search_{idx}")
            st.markdown('</div>', unsafe_allow_html=True)

        else:
            # No results found - show helpful suggestions
            st.markdown(f"""
            <div class="section-header">
                🔍 No Results Found
            </div>
            <p style="color: #9ca3af; padding: 0 24px 16px 24px; font-size: 1rem;">
                No books found for: "{original_query or 'your search'}"
            </p>
            """, unsafe_allow_html=True)

            # Show correction suggestion if available
            if suggested_correction:
                st.markdown(f"""
                <div style="background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6;
                            padding: 20px 24px; margin: 0 24px 24px 24px; border-radius: 8px;">
                    <p style="color: #3b82f6; margin: 0 0 12px 0; font-size: 1.1rem; font-weight: 600;">
                        💡 Did you mean: <strong>"{suggested_correction}"</strong>?
                    </p>
                </div>
                """, unsafe_allow_html=True)

                if st.button(f"🔍 Search for '{suggested_correction}'", key="search_correction_empty", type="primary"):
                    # Trigger new search with corrected query
                    st.session_state.pending_search = suggested_correction
                    st.session_state.page = "home"
                    st.rerun()

            # Show alternative search suggestions
            if alternative_queries:
                st.markdown("""
                <div style="margin: 24px 24px 12px 24px;">
                    <p style="color: #e5e7eb; font-size: 1.1rem; font-weight: 600; margin: 0;">
                        🎯 Try these alternative searches:
                    </p>
                </div>
                """, unsafe_allow_html=True)

                for alt_query in alternative_queries:
                    if st.button(f"📚 {alt_query}", key=f"alt_{alt_query}", type="secondary"):
                        st.session_state.pending_search = alt_query
                        st.session_state.page = "home"
                        st.rerun()

            # General search tips
            st.markdown("""
            <div style="background: rgba(107, 114, 128, 0.1); padding: 20px 24px;
                        margin: 24px; border-radius: 8px; border: 1px solid rgba(107, 114, 128, 0.2);">
                <p style="color: #e5e7eb; font-size: 1rem; font-weight: 600; margin: 0 0 12px 0;">
                    💡 Search Tips:
                </p>
                <ul style="color: #9ca3af; margin: 0; padding-left: 20px;">
                    <li>Try searching by author name (e.g., "Stephen King")</li>
                    <li>Search by genre (e.g., "mystery", "fantasy")</li>
                    <li>Use natural language (e.g., "books about space")</li>
                    <li>Check your spelling and try again</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = BookVaultApp()
    app.run()
