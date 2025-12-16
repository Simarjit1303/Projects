"""
UI Components Module for BookVault

Contains reusable UI components and shared styles for the Streamlit application.

Modules:
    modern_book_card: Interactive book card component with hover effects
        - Function: render(book, key) - Renders a clickable book card
        - Features: Cover image, title, author, click-to-detail navigation

    styles: Shared CSS styles and theme configuration
        - Contains: Grid layouts, card styles, hover effects, typography
        - Applied globally via st.markdown with unsafe_allow_html=True

Usage:
    from Bookvault_UI.Components import modern_book_card

    # Render a book card
    for idx, book in enumerate(books):
        modern_book_card.render(book, f"book_{idx}")

Architecture:
    - Components are designed to be stateless and reusable
    - Styling is centralized in the styles module
    - All components support Streamlit's session state for navigation
"""

from . import modern_book_card
from . import styles

__all__ = ["modern_book_card", "styles"]
