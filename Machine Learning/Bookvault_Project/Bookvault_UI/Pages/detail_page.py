"""
Book detail page with metadata, quotes, recommendations, and AI chatbot
"""
import streamlit as st
from typing import Dict, List
from Bookvault.service import BookVaultService


class DetailPage:
    """Book detail page with comprehensive information"""

    def __init__(self, service: BookVaultService, book: Dict):
        self.service = service
        self.book = book

    def render(self):
        """Render the detail page"""
        # Initialize chatbot state
        if "chatbot_open" not in st.session_state:
            st.session_state.chatbot_open = False
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = []

        # Top navigation bar: Back button + Search bar + AI Chat toggle
        self._render_top_navigation()

        # Add CSS to prevent layout shift when opening chat
        st.markdown("""
        <style>
        /* Prevent layout shift */
        .main .block-container {
            transition: padding-right 0.3s ease;
        }

        /* Chat sidebar fixed positioning */
        .chat-sidebar-fixed {
            position: sticky;
            top: 20px;
            max-height: calc(100vh - 100px);
            overflow-y: auto;
        }

        /* MEGA FIX: Make ALL columns and their wrappers transparent when chat is open */
        [data-testid="column"] {
            background: transparent !important;
            background-color: transparent !important;
        }

        [data-testid="column"] > div {
            background: transparent !important;
            background-color: transparent !important;
        }

        [data-testid="column"] [data-testid="stVerticalBlock"] {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* Remove any black backgrounds from the entire detail page */
        [data-testid="stAppViewContainer"] [data-testid="stVerticalBlock"],
        [data-testid="stAppViewContainer"] [data-testid="element-container"] {
            background: transparent !important;
            background-color: transparent !important;
        }
        </style>

        <script>
        // JavaScript to remove black backgrounds dynamically
        (function() {
            function removeBlackBackgrounds() {
                // Find all elements
                const allElements = document.querySelectorAll('*');

                allElements.forEach(el => {
                    const bgColor = window.getComputedStyle(el).backgroundColor;

                    // Check if background is black or very dark
                    if (bgColor === 'rgb(0, 0, 0)' ||
                        bgColor === 'rgba(0, 0, 0, 1)' ||
                        bgColor.match(/rgba?\\(0,\\s*0,\\s*0/)) {

                        // Don't touch chat elements we want to keep
                        if (!el.classList.contains('chat-container') &&
                            !el.classList.contains('chat-header-box') &&
                            !el.classList.contains('chat-messages-area') &&
                            !el.classList.contains('chat-user-message') &&
                            !el.classList.contains('chat-ai-message')) {

                            el.style.backgroundColor = 'transparent';
                            el.style.background = 'transparent';
                        }
                    }
                });
            }

            // Run immediately
            removeBlackBackgrounds();

            // Run when DOM changes (Streamlit re-renders)
            const observer = new MutationObserver(removeBlackBackgrounds);
            observer.observe(document.body, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class']
            });

            // Also run periodically as backup
            setInterval(removeBlackBackgrounds, 500);
        })();
        </script>
        """, unsafe_allow_html=True)

        # If chat is open, split page into main content + chat sidebar
        if st.session_state.get("chat_open", False):
            col_main, col_chat = st.columns([2.5, 1], gap="medium")

            with col_main:
                # Book details header
                self._render_header()
                # Quotes section
                self._render_quotes()
                # Recommendations
                self._render_recommendations()

            with col_chat:
                # Chat sidebar with fixed positioning
                st.markdown('<div class="chat-sidebar-fixed">', unsafe_allow_html=True)
                self._render_chat_sidebar()
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            # Normal full-width layout when chat is closed
            self._render_header()
            self._render_quotes()
            self._render_recommendations()

    def _render_top_navigation(self):
        """Render top navigation bar with back button, search bar, and AI chat button"""
        # Initialize chat state
        if "chat_open" not in st.session_state:
            st.session_state.chat_open = False

        # Add custom CSS for detail page buttons with higher specificity
        st.markdown("""
        <style>
        /* Detail page: All primary buttons should have cyan gradient */
        div[data-testid="column"] button[data-testid="baseButton-primary"] {
            height: 56px !important;
            padding: 0px 24px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            border: none !important;
            box-shadow: 0 6px 20px rgba(6, 182, 212, 0.4) !important;
        }

        div[data-testid="column"] button[data-testid="baseButton-primary"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 30px rgba(8, 145, 178, 0.6) !important;
            background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
        }

        div[data-testid="column"] button[data-testid="baseButton-primary"]:active {
            transform: translateY(0px) !important;
        }

        /* Secondary button (Close Chat) - red styling */
        div[data-testid="column"] button[data-testid="baseButton-secondary"] {
            height: 56px !important;
            padding: 0px 24px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
            background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%) !important;
            color: white !important;
            border: 2px solid rgba(220, 38, 38, 0.8) !important;
            box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4) !important;
        }

        div[data-testid="column"] button[data-testid="baseButton-secondary"]:hover {
            transform: translateY(-2px) !important;
            background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%) !important;
            box-shadow: 0 8px 30px rgba(220, 38, 38, 0.5) !important;
        }
        </style>
        """, unsafe_allow_html=True)

        # Create a beautiful horizontal layout: Back button | Search bar | AI Chat button
        col1, col2, col3 = st.columns([1.5, 9, 1.5])

        with col1:
            if st.button("⬅️ Back", key="back_button", type="primary"):
                st.session_state.back_clicked = True
                st.session_state.page = "home"
                st.session_state.selected_book = None
                st.session_state.chat_messages = []
                st.session_state.chatbot_open = False
                st.session_state.chat_open = False
                st.query_params.clear()  # Clear query params to prevent re-navigation
                st.rerun()

        with col2:
            # Search bar always visible
            search_query = st.text_input(
                "Search for another book...",
                placeholder="🤖 Try AI search: 'books about mystery' or 'scary thriller novels' or 'fantasy like Harry Potter'...",
                label_visibility="collapsed",
                key="detail_search"
            )

            if search_query and len(search_query) > 2:
                self._handle_ai_search(search_query)

        with col3:
            # AI Chat toggle button in top-right with dynamic styling
            if st.session_state.chat_open:
                button_label = "✖ Close Chat"
                button_type = "secondary"
            else:
                button_label = "🤖 AI Chat"
                button_type = "primary"

            if st.button(button_label, key="toggle_chat_top", type=button_type, use_container_width=True):
                st.session_state.chat_open = not st.session_state.chat_open
                st.rerun()

        # Add some spacing after the navigation bar
        st.markdown('<div style="margin-bottom: 16px;"></div>', unsafe_allow_html=True)

    def _handle_ai_search(self, query: str):
        """Handle AI-powered natural language search"""
        try:
            from ..App_Pro import cached_search_books

            # Check if it's a natural language query
            nl_keywords = ['about', 'books', 'novel', 'read', 'want', 'looking for', 'recommend', 'like', 'similar to']
            is_nl_query = any(keyword in query.lower() for keyword in nl_keywords)

            if is_nl_query:
                # Use AI to extract search terms and get recommendations
                with st.spinner("🤖 AI is understanding your request..."):
                    ai_results = self._get_ai_book_recommendations(query)
                    if ai_results:
                        st.session_state.search_results = ai_results
                        st.session_state.ai_search_query = query
                        st.session_state.page = "search_results"
                        st.rerun()
                    else:
                        st.warning("No books found for your query. Try a different description.")
            else:
                # Direct search for book title/author
                results = cached_search_books(query, max_results=24, cache_key=st.session_state.cache_key)
                if results:
                    st.session_state.search_results = results
                    st.session_state.page = "search_results"
                    st.rerun()
                else:
                    st.warning("No books found. Try a different search term.")
        except Exception as e:
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

    def _render_header(self):
        """Render book details header"""
        # Add some top spacing
        st.markdown('<div style="margin-top: 20px;"></div>', unsafe_allow_html=True)

        col1, col2 = st.columns([1, 2.5])

        with col1:
            # Book cover - centered with max width
            cover_url = self.book.get("cover_url", "")
            if cover_url:
                st.markdown(f"""
                <div style="
                    display: flex;
                    justify-content: center;
                    align-items: flex-start;
                ">
                    <img src="{cover_url}"
                         alt="{self.book.get('title', '')}"
                         style="
                            max-width: 280px;
                            width: 100%;
                            height: auto;
                            border-radius: 12px;
                            box-shadow: 0 16px 48px rgba(6, 182, 212, 0.5), 0 0 0 1px rgba(6, 182, 212, 0.3);
                            transition: transform 0.3s ease;
                         "
                         onmouseover="this.style.transform='translateY(-8px) scale(1.02)'"
                         onmouseout="this.style.transform='translateY(0) scale(1)'">
                </div>
                """, unsafe_allow_html=True)

        with col2:
            # Title
            title = self.book.get("title", "Unknown Title")
            st.markdown(f"""
            <h1 style="
                color: #22d3ee;
                font-size: 2.8rem;
                font-weight: 800;
                margin-bottom: 16px;
                line-height: 1.15;
                text-shadow: 0 2px 8px rgba(6, 182, 212, 0.4);
                letter-spacing: -0.5px;
            ">{title}</h1>
            """, unsafe_allow_html=True)

            # Author
            author = self.book.get("author", "Unknown Author")
            st.markdown(f"""
            <p style="
                font-size: 1.5rem;
                color: #06b6d4;
                margin-bottom: 24px;
                font-weight: 600;
                letter-spacing: 0.3px;
            ">by <span style="color: #67e8f9;">{author}</span></p>
            """, unsafe_allow_html=True)

            # Rating
            rating = self.book.get("rating", 0)
            if rating:
                stars = "⭐" * int(rating)
                st.markdown(f"""
                <div style="
                    font-size: 1.4rem;
                    margin-bottom: 20px;
                    background: linear-gradient(135deg, rgba(6, 182, 212, 0.2) 0%, rgba(8, 145, 178, 0.15) 100%);
                    padding: 14px 28px;
                    border-radius: 16px;
                    border: 2px solid rgba(6, 182, 212, 0.5);
                    display: inline-block;
                    box-shadow: 0 4px 16px rgba(6, 182, 212, 0.4);
                    font-weight: 700;
                    color: #fbbf24;
                ">{stars} <span style="color: #22d3ee;">{rating}/5</span></div>
                """, unsafe_allow_html=True)

            # Metadata
            self._render_metadata()

            # Description
            description = self.book.get("description", "No description available")
            st.markdown(f"""
            <div style="
                margin-top: 28px;
                background: linear-gradient(135deg, rgba(15, 23, 42, 0.8) 0%, rgba(30, 30, 46, 0.6) 100%);
                padding: 28px 32px;
                border-radius: 18px;
                border: 2px solid rgba(6, 182, 212, 0.25);
                box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
            ">
                <h3 style="
                    color: #22d3ee;
                    margin-bottom: 20px;
                    font-size: 1.5rem;
                    font-weight: 700;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                "><span style="font-size: 1.6rem;">📖</span> About This Book</h3>
                <p style="
                    color: #e2e8f0;
                    line-height: 1.9;
                    font-size: 1.08rem;
                    text-align: justify;
                ">{description}</p>
            </div>
            """, unsafe_allow_html=True)

    def _render_metadata(self):
        """Render book metadata"""
        metadata_items = []

        # Published date
        published = self.book.get("published_date", "")
        if published:
            metadata_items.append(f'''<div style="
                background: rgba(6, 182, 212, 0.12);
                padding: 12px 18px;
                border-radius: 12px;
                border: 1px solid rgba(6, 182, 212, 0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(6, 182, 212, 0.2)'; this.style.borderColor='rgba(6, 182, 212, 0.5)'"
               onmouseout="this.style.background='rgba(6, 182, 212, 0.12)'; this.style.borderColor='rgba(6, 182, 212, 0.3)'">
                <span style="color: #22d3ee; font-weight: 700; font-size: 1.05rem;">📅 Release:</span><br>
                <span style="color: #e8eaed; font-size: 1rem; font-weight: 500;">{published}</span>
            </div>''')

        # Page count
        pages = self.book.get("page_count", 0)
        if pages:
            metadata_items.append(f'''<div style="
                background: rgba(6, 182, 212, 0.12);
                padding: 12px 18px;
                border-radius: 12px;
                border: 1px solid rgba(6, 182, 212, 0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(6, 182, 212, 0.2)'; this.style.borderColor='rgba(6, 182, 212, 0.5)'"
               onmouseout="this.style.background='rgba(6, 182, 212, 0.12)'; this.style.borderColor='rgba(6, 182, 212, 0.3)'">
                <span style="color: #22d3ee; font-weight: 700; font-size: 1.05rem;">📄 Pages:</span><br>
                <span style="color: #e8eaed; font-size: 1rem; font-weight: 500;">{pages}</span>
            </div>''')

        # Publisher
        publisher = self.book.get("publisher", "")
        if publisher:
            metadata_items.append(f'''<div style="
                background: rgba(6, 182, 212, 0.12);
                padding: 12px 18px;
                border-radius: 12px;
                border: 1px solid rgba(6, 182, 212, 0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(6, 182, 212, 0.2)'; this.style.borderColor='rgba(6, 182, 212, 0.5)'"
               onmouseout="this.style.background='rgba(6, 182, 212, 0.12)'; this.style.borderColor='rgba(6, 182, 212, 0.3)'">
                <span style="color: #22d3ee; font-weight: 700; font-size: 1.05rem;">🏢 Publisher:</span><br>
                <span style="color: #e8eaed; font-size: 1rem; font-weight: 500;">{publisher}</span>
            </div>''')

        # Language
        language = self.book.get("language", "")
        if language:
            metadata_items.append(f'''<div style="
                background: rgba(6, 182, 212, 0.12);
                padding: 12px 18px;
                border-radius: 12px;
                border: 1px solid rgba(6, 182, 212, 0.3);
                transition: all 0.3s ease;
            " onmouseover="this.style.background='rgba(6, 182, 212, 0.2)'; this.style.borderColor='rgba(6, 182, 212, 0.5)'"
               onmouseout="this.style.background='rgba(6, 182, 212, 0.12)'; this.style.borderColor='rgba(6, 182, 212, 0.3)'">
                <span style="color: #22d3ee; font-weight: 700; font-size: 1.05rem;">🌐 Language:</span><br>
                <span style="color: #e8eaed; font-size: 1rem; font-weight: 500;">{language.upper()}</span>
            </div>''')

        if metadata_items:
            metadata_html = f"""
            <div style="
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                gap: 14px;
                margin: 24px 0;
            ">
                {''.join(metadata_items)}
            </div>
            """
            st.markdown(metadata_html, unsafe_allow_html=True)

    def _render_quotes(self):
        """Render thematic quotes inspired by the book"""
        st.markdown("""
        <div style="margin: 48px 0;">
            <h2 style="
                color: #06b6d4;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 24px;
                text-align: center;
            ">✨ Inspired Quotes</h2>
            <p style="
                color: #9ca3af;
                text-align: center;
                margin-top: -16px;
                margin-bottom: 24px;
                font-size: 0.95rem;
            ">AI-generated quotes capturing the essence of this book</p>
        </div>
        """, unsafe_allow_html=True)

        try:
            with st.spinner("📚 Fetching quotes..."):
                # Get quotes from AI
                quotes = self.service.ai_engine.get_famous_quotes(
                    title=self.book.get("title", ""),
                    author=self.book.get("author", ""),
                    description=self.book.get("description", ""),
                    num_quotes=3
                )

                if quotes:
                    cols = st.columns(len(quotes))
                    for idx, quote in enumerate(quotes):
                        with cols[idx]:
                            st.markdown(f"""
                            <div style="
                                background: rgba(15, 23, 42, 0.8);
                                padding: 24px;
                                border-radius: 16px;
                                border: 2px solid rgba(6, 182, 212, 0.4);
                                height: 200px;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                text-align: center;
                                box-shadow: 0 8px 24px rgba(6, 182, 212, 0.3);
                                transition: all 0.3s ease;
                            ">
                                <p style="
                                    color: #e8eaed;
                                    font-size: 1rem;
                                    line-height: 1.6;
                                    font-style: italic;
                                    font-weight: 500;
                                ">"{quote}"</p>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("📚 Quotes are being generated...")
        except Exception as e:
            st.warning("Could not load quotes at this time.")

    def _render_recommendations(self):
        """Render recommended books"""
        st.markdown("""
        <div style="margin-top: 64px;">
            <h2 style="
                color: #06b6d4;
                font-size: 2rem;
                font-weight: 700;
                margin-bottom: 24px;
                text-align: center;
            ">✨ YOU MIGHT ALSO ENJOY</h2>
        </div>
        """, unsafe_allow_html=True)

        try:
            from ..App_Pro import cached_ai_recommendations
            from ..Components import modern_book_card

            categories = self.book.get("categories", [])
            categories_str = ", ".join(categories) if isinstance(categories, list) else str(categories)

            with st.spinner("🤖 Finding perfect recommendations for you..."):
                recommendations = cached_ai_recommendations(
                    title=self.book.get("title", ""),
                    author=self.book.get("author", ""),
                    description=self.book.get("description", ""),
                    categories=categories_str,
                    max_results=24
                )

                # Filter out current book
                recommendations = [
                    r for r in recommendations
                    if r.get("title", "").lower() != self.book.get("title", "").lower()
                ]

                if recommendations:
                    # Store recommended books in session state
                    if "all_books" not in st.session_state:
                        st.session_state.all_books = {}
                    for rec_book in recommendations[:18]:
                        book_id = rec_book.get("id") or f"{rec_book.get('title', '')}_{rec_book.get('author', '')}"
                        if book_id:
                            st.session_state.all_books[book_id] = rec_book

                    # Display in grid
                    st.markdown('<div class="book-grid">', unsafe_allow_html=True)
                    cols = st.columns(6)
                    for idx, rec_book in enumerate(recommendations[:18]):
                        with cols[idx % 6]:
                            modern_book_card.render(rec_book, f"rec_{idx}")
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.info("No recommendations available at this time.")

        except Exception as e:
            st.error(f"Could not load recommendations: {str(e)}")

    def _get_chat_styles(self) -> str:
        """Get CSS styles for chat sidebar"""
        return """
        <style>
        /* Chat sidebar - modern glassmorphism design */
        .chat-container {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.98) 0%, rgba(17, 24, 39, 0.98) 100%);
            border: 2px solid rgba(6, 182, 212, 0.6);
            border-radius: 24px;
            padding: 28px;
            margin: 0;
            box-shadow:
                0 20px 60px rgba(6, 182, 212, 0.25),
                0 0 0 1px rgba(6, 182, 212, 0.1) inset,
                0 8px 32px rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(16px);
            position: relative;
            overflow: hidden;
        }

        /* Animated gradient overlay */
        .chat-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg,
                transparent 0%,
                rgba(6, 182, 212, 0.8) 50%,
                transparent 100%);
            animation: shimmer 3s ease-in-out infinite;
        }

        @keyframes shimmer {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }

        /* Chat header - enhanced with icon and gradient */
        .chat-header-box {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 50%, #0e7490 100%);
            border-radius: 18px;
            padding: 24px 20px;
            margin-bottom: 24px;
            text-align: center;
            box-shadow:
                0 8px 24px rgba(6, 182, 212, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
            position: relative;
            overflow: hidden;
        }

        .chat-header-box::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg,
                transparent,
                rgba(255, 255, 255, 0.2),
                transparent);
            animation: slide 3s ease-in-out infinite;
        }

        @keyframes slide {
            0% { left: -100%; }
            100% { left: 100%; }
        }

        /* Chat messages area - improved depth */
        .chat-messages-area {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.95) 0%, rgba(7, 11, 21, 0.98) 100%);
            border: 2px solid rgba(6, 182, 212, 0.3);
            border-radius: 18px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow:
                inset 0 2px 12px rgba(0, 0, 0, 0.4),
                0 0 0 1px rgba(6, 182, 212, 0.1) inset;
        }

        /* User message bubbles - modern blue gradient */
        .chat-user-message {
            background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            padding: 16px 20px;
            border-radius: 18px 18px 4px 18px;
            margin-bottom: 16px;
            border: 1px solid rgba(59, 130, 246, 0.4);
            box-shadow:
                0 4px 16px rgba(37, 99, 235, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
            transition: transform 0.2s ease;
            animation: slideInRight 0.3s ease-out;
        }

        .chat-user-message:hover {
            transform: translateX(-4px);
        }

        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        /* AI message bubbles - modern green gradient */
        .chat-ai-message {
            background: linear-gradient(135deg, #059669 0%, #047857 100%);
            padding: 16px 20px;
            border-radius: 18px 18px 18px 4px;
            margin-bottom: 16px;
            border: 1px solid rgba(16, 185, 129, 0.4);
            box-shadow:
                0 4px 16px rgba(5, 150, 105, 0.3),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset;
            transition: transform 0.2s ease;
            animation: slideInLeft 0.3s ease-out;
        }

        .chat-ai-message:hover {
            transform: translateX(4px);
        }

        @keyframes slideInLeft {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }

        /* Enhanced close button */
        .close-chat-btn button {
            background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%) !important;
            border: 2px solid rgba(239, 68, 68, 0.4) !important;
            width: 100% !important;
            padding: 16px !important;
            border-radius: 14px !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            box-shadow:
                0 6px 20px rgba(220, 38, 38, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.05) inset !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
            color: white !important;
        }

        .close-chat-btn button:hover {
            background: linear-gradient(135deg, #b91c1c 0%, #7f1d1d 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow:
                0 10px 28px rgba(220, 38, 38, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
        }

        .close-chat-btn button:active {
            transform: translateY(-1px) !important;
        }

        /* Enhanced chat input styling */
        .stTextInput input {
            border-radius: 14px !important;
            border: 2px solid rgba(6, 182, 212, 0.4) !important;
            background: rgba(15, 23, 42, 0.9) !important;
            color: white !important;
            padding: 14px 18px !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
        }

        .stTextInput input:focus {
            border-color: #06b6d4 !important;
            box-shadow:
                0 0 0 4px rgba(6, 182, 212, 0.15),
                0 0 20px rgba(6, 182, 212, 0.3) !important;
            background: rgba(15, 23, 42, 1) !important;
        }

        .stTextInput input::placeholder {
            color: rgba(156, 163, 175, 0.6) !important;
        }

        /* Enhanced send button */
        .stForm button[kind="primary"] {
            background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%) !important;
            color: white !important;
            border: 2px solid rgba(6, 182, 212, 0.4) !important;
            border-radius: 14px !important;
            padding: 14px 24px !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            box-shadow:
                0 6px 16px rgba(6, 182, 212, 0.4),
                0 0 0 1px rgba(255, 255, 255, 0.05) inset !important;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        }

        .stForm button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0891b2 0%, #0e7490 100%) !important;
            transform: translateY(-3px) !important;
            box-shadow:
                0 10px 24px rgba(8, 145, 178, 0.5),
                0 0 0 1px rgba(255, 255, 255, 0.1) inset !important;
        }

        .stForm button[kind="primary"]:active {
            transform: translateY(-1px) !important;
        }

        /* Enhanced clear button */
        .stForm button[kind="secondary"] {
            background: rgba(71, 85, 105, 0.6) !important;
            color: white !important;
            border: 2px solid rgba(148, 163, 184, 0.4) !important;
            border-radius: 14px !important;
            padding: 14px 24px !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2) !important;
        }

        .stForm button[kind="secondary"]:hover {
            background: rgba(100, 116, 139, 0.8) !important;
            border-color: rgba(148, 163, 184, 0.6) !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        }

        /* Section headers in chat */
        .chat-section-title {
            color: #22d3ee;
            font-size: 1.1rem;
            font-weight: 700;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        /* Empty state styling - compact and centered */
        .chat-empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #64748b;
            animation: fadeIn 0.5s ease-out;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }

        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }

        /* Streamlit container height override for chat */
        [data-testid="stVerticalBlock"] > div > div[style*="height"] {
            min-height: auto !important;
        }

        /* Hide/style text inputs in chat sidebar to prevent black boxes */
        .chat-container input[type="text"]:not(:focus):placeholder-shown {
            opacity: 0.7;
        }

        /* Fix Streamlit container rendering - prevent black boxes */
        .chat-container [data-testid="stVerticalBlock"],
        .chat-container [data-testid="stVerticalBlock"] > div,
        .chat-container [data-testid="stVerticalBlockBorderWrapper"],
        .chat-container [data-testid="stHorizontalBlock"],
        .chat-container [data-testid="column"],
        .chat-container .element-container {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* Force transparent backgrounds for all Streamlit elements in chat */
        .chat-container > div,
        .chat-container > div > div {
            background: transparent !important;
        }

        /* Hide Streamlit elements that appear above chat container in the column */
        [data-testid="column"]:has(.chat-sidebar-fixed) > div:first-child {
            display: none !important;
        }

        /* Alternative: Make all elements in chat column transparent except our custom divs */
        [data-testid="column"]:has(.chat-sidebar-fixed) [data-testid="stVerticalBlock"] {
            background: transparent !important;
        }

        /* More aggressive: Hide all elements before chat-sidebar-fixed */
        .chat-sidebar-fixed ~ * {
            /* This won't work, need different approach */
        }

        /* Target the specific column and hide empty containers */
        [data-testid="column"] [data-testid="stVerticalBlock"]:empty,
        [data-testid="column"] [data-testid="element-container"]:empty {
            display: none !important;
        }

        /* AGGRESSIVE FIX: Hide all Streamlit containers in chat column that appear before chat content */
        [data-testid="column"]:last-child > [data-testid="stVerticalBlock"] > div:not(:has(.chat-sidebar-fixed)) {
            display: none !important;
        }

        /* Make chat column wrapper completely transparent */
        [data-testid="column"]:last-child {
            background: transparent !important;
        }

        [data-testid="column"]:last-child > div {
            background: transparent !important;
        }

        /* Hide the specific black box element */
        .chat-sidebar-fixed::before {
            display: none !important;
        }

        /* Hide any element-container that appears before chat in the chat column */
        .chat-sidebar-fixed ~ [data-testid="element-container"] {
            display: none !important;
        }

        /* SUPER AGGRESSIVE: Remove ALL black backgrounds in chat column */
        [data-testid="column"]:last-child * {
            background-color: transparent !important;
        }

        /* Override any black/dark backgrounds in the chat area */
        [data-testid="column"]:last-child [style*="background"],
        [data-testid="column"]:last-child [style*="background-color"] {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* Force transparent backgrounds on all Streamlit elements in chat column */
        [data-testid="column"]:last-child [data-testid="stVerticalBlock"],
        [data-testid="column"]:last-child [data-testid="stHorizontalBlock"],
        [data-testid="column"]:last-child [data-testid="element-container"],
        [data-testid="column"]:last-child [class*="st"],
        [data-testid="column"]:last-child div:not(.chat-container):not(.chat-header-box):not(.chat-messages-area):not(.chat-user-message):not(.chat-ai-message):not(.chat-empty-state) {
            background: transparent !important;
            background-color: transparent !important;
        }

        /* Hide any standalone divs that might create black boxes */
        [data-testid="column"]:last-child > div:not(:has(.chat-sidebar-fixed)):not(:has(.chat-container)) {
            display: none !important;
        }
        </style>
        """

    def _render_chat_header(self) -> None:
        """Render chat header box"""
        st.markdown("""
        <div class="chat-header-box">
            <h2 style="color: white; margin: 0; font-size: 1.4rem;">🤖 AI Book Assistant</h2>
            <p style="color: rgba(255,255,255,0.9); margin: 8px 0 0 0; font-size: 0.9rem;">Ask anything about this book</p>
        </div>
        """, unsafe_allow_html=True)

    def _render_chat_messages(self) -> None:
        """Render chat message history"""
        st.markdown('<p class="chat-section-title" style="margin-top: 20px;">💬 Conversation</p>', unsafe_allow_html=True)

        if st.session_state.chat_messages:
            messages_html = '<div class="chat-messages-area" style="max-height: 280px; overflow-y: auto; padding: 20px;">'
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    messages_html += f"""
                    <div class="chat-user-message">
                        <strong style="color: #bfdbfe; font-size: 0.95rem; letter-spacing: 0.3px;">👤 You</strong>
                        <p style="color: #eff6ff; margin: 10px 0 0 0; line-height: 1.7; font-size: 0.95rem;">{msg['content']}</p>
                    </div>
                    """
                else:
                    messages_html += f"""
                    <div class="chat-ai-message">
                        <strong style="color: #a7f3d0; font-size: 0.95rem; letter-spacing: 0.3px;">🤖 AI Assistant</strong>
                        <p style="color: #ecfdf5; margin: 10px 0 0 0; line-height: 1.7; font-size: 0.95rem;">{msg['content']}</p>
                    </div>
                    """
            messages_html += '</div>'
            st.markdown(messages_html, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="chat-messages-area">
                <div class="chat-empty-state" style="min-height: 200px;">
                    <div style="font-size: 3rem; margin-bottom: 12px; opacity: 0.4;">💬</div>
                    <p style="margin: 0; font-size: 1.1rem; font-weight: 700; color: #94a3b8;">Start a conversation!</p>
                    <p style="font-size: 0.9rem; margin: 8px 0 0 0; color: #64748b;">Ask me anything about this book</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    def _render_chat_input_form(self) -> None:
        """Render chat input form with send and clear buttons"""
        st.markdown('<p class="chat-section-title" style="margin-top: 20px;">✏️ Ask a Question</p>', unsafe_allow_html=True)

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Your question",
                placeholder="💭 Type your question and press Enter...",
                label_visibility="collapsed",
                key="chat_input_field"
            )

            # Buttons row
            col1, col2 = st.columns([3, 1])
            with col1:
                submitted = st.form_submit_button("✈️ Send Message", type="primary", use_container_width=True)
            with col2:
                clear = st.form_submit_button("🗑️ Clear", use_container_width=True)

            # Handle form submission
            if submitted and user_input and user_input.strip():
                st.session_state.chat_messages.append({"role": "user", "content": user_input})
                with st.spinner("🤖 Thinking..."):
                    ai_response = self._get_ai_response(user_input)
                    st.session_state.chat_messages.append({"role": "assistant", "content": ai_response})
                st.rerun()

            # Handle clear button
            if clear:
                st.session_state.chat_messages = []
                st.rerun()

    def _render_chat_sidebar(self):
        """Render AI chat UI in the right sidebar column"""
        # Apply chat styles
        st.markdown(self._get_chat_styles(), unsafe_allow_html=True)

        # Main chat container
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        # Render chat components
        self._render_chat_header()
        self._render_chat_messages()
        self._render_chat_input_form()

        st.markdown('</div>', unsafe_allow_html=True)

    @st.dialog("🤖 AI Book Assistant", width="large")
    def _show_chat_dialog(self):
        """Show the chat dialog popup"""
        # Suggested quick questions
        st.markdown("### 💡 Quick Start Questions")
        st.caption("Click a question below or ask your own")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📖 What's the plot?", use_container_width=True, key="q1"):
                st.session_state.quick_question = "What is the plot of this book?"
                st.rerun()

        with col2:
            if st.button("👥 Main characters?", use_container_width=True, key="q2"):
                st.session_state.quick_question = "Who are the main characters in this book?"
                st.rerun()

        with col3:
            if st.button("🎯 Main themes?", use_container_width=True, key="q3"):
                st.session_state.quick_question = "What are the main themes of this book?"
                st.rerun()

        col4, col5, col6 = st.columns(3)

        with col4:
            if st.button("📊 Reading level?", use_container_width=True, key="q4"):
                st.session_state.quick_question = "What is the reading level of this book?"
                st.rerun()

        with col5:
            if st.button("⭐ Why read this?", use_container_width=True, key="q5"):
                st.session_state.quick_question = "Why should I read this book?"
                st.rerun()

        with col6:
            if st.button("📚 Similar books?", use_container_width=True, key="q6"):
                st.session_state.quick_question = "What books are similar to this one?"
                st.rerun()

        st.divider()

        # Chat history in scrollable container
        st.markdown("### 💬 Chat History")
        chat_container = st.container(height=300)

        with chat_container:
            if st.session_state.chat_messages:
                for idx, msg in enumerate(st.session_state.chat_messages):
                    if msg["role"] == "user":
                        st.info(f"**👤 You:** {msg['content']}")
                    else:
                        st.success(f"**🤖 AI:** {msg['content']}")
            else:
                st.caption("No messages yet. Ask a question to start chatting!")

        st.divider()

        # Input section
        user_input = st.text_input(
            "Ask anything about this book...",
            value=st.session_state.quick_question,
            key="dialog_chat_input",
            placeholder="e.g., What makes this book unique? Who would enjoy it?"
        )

        # Clear quick question after displaying
        if st.session_state.quick_question:
            st.session_state.quick_question = ""

        col1, col2 = st.columns([3, 1])

        with col1:
            if st.button("✈️ Send Message", type="primary", use_container_width=True, key="send_dialog"):
                if user_input and user_input.strip():
                    # Add user message
                    st.session_state.chat_messages.append({
                        "role": "user",
                        "content": user_input
                    })

                    # Generate AI response
                    with st.spinner("🤖 AI is thinking..."):
                        ai_response = self._get_ai_response(user_input)
                        st.session_state.chat_messages.append({
                            "role": "assistant",
                            "content": ai_response
                        })

                    st.rerun()
                else:
                    st.warning("⚠️ Please enter a question first!")

        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True, key="clear_dialog"):
                st.session_state.chat_messages = []
                st.rerun()

    def _get_ai_response(self, user_question: str) -> str:
        """Get AI response for user question about the book"""
        try:
            from openai import OpenAI
            from ..App_Pro import get_service

            service = get_service()
            client = OpenAI(api_key=service.ai_engine.client.api_key)

            title = self.book.get("title", "")
            author = self.book.get("author", "")
            description = self.book.get("description", "")
            categories = self.book.get("categories", [])

            context = f"""
Book Title: {title}
Author: {author}
Categories: {', '.join(categories) if isinstance(categories, list) else categories}
Description: {description[:500]}

User Question: {user_question}

Provide a helpful, concise answer about this book. Be friendly and informative.
"""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": context}],
                max_tokens=200,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try asking your question again."
