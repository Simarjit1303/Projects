"""
📚 BookVault UI Layer

Streamlit-based frontend for BookVault application.

Modules:
    UI_config: UI configuration and theme settings
    Components: Reusable UI components (book cards, styles)
    Pages: Page components (HomePage, DetailPage)

Structure:
    - App_Pro.py: Main application entry point
    - Pages/: Page-level components
        - home_page.py: Home page with genre browsing and search
        - detail_page.py: Book detail page with recommendations
    - Components/: Reusable UI components
        - modern_book_card.py: Book card component
        - styles.py: Shared CSS styles

Usage:
    Run the application:
        streamlit run Bookvault_UI/App_Pro.py
"""

# Import top-level modules
from . import UI_config
from . import Components
from . import Pages

__all__ = [
    "UI_config",
    "Components",
    "Pages",
]
