"""
Pages Module for BookVault UI

Contains modular page-level components for the Streamlit application.

Classes:
    HomePage: Main landing page with hero section, search, and genre browsing
        - Features: AI-powered search, image search, genre filtering
        - Methods: render(), _render_search(), _render_all_genres(), etc.

    DetailPage: Individual book detail page
        - Features: Book details, AI recommendations, quotes, captions
        - Methods: render(), show_book_details(), etc.

Usage:
    from Bookvault_UI.Pages import HomePage, DetailPage

    # Initialize with service
    home = HomePage(service)
    home.render()

    # Or use directly in App_Pro.py
    if st.session_state.page == "home":
        home_page = HomePage(service)
        home_page.render()
"""

from .home_page import HomePage
from .detail_page import DetailPage

__all__ = [
    'HomePage',
    'DetailPage'
]
