"""
Modern book card component - clickable image cards
"""
import streamlit as st
from urllib.parse import quote


def render(book: dict, unique_id: str):
    """
    Render a modern book card as a clickable HTML container

    Args:
        book: dict with 'title', 'author', 'cover_url'
        unique_id: unique identifier for the card
    """
    cover_url = book.get("cover_url", "")
    title = book.get("title", "Unknown Title")
    author = book.get("author", "Unknown Author")

    if not cover_url:
        return

    # Create a unique book identifier
    book_id = book.get("id") or f"{title}_{author}"

    # Store book in session state with the ID as key (persistent storage)
    if "all_books" not in st.session_state:
        st.session_state.all_books = {}
    st.session_state.all_books[book_id] = book

    # URL-encode the book_id
    encoded_book_id = quote(book_id, safe='')

    # Truncate long titles and authors
    display_title = title[:35] + '...' if len(title) > 35 else title
    display_author = author[:25] + '...' if len(author) > 25 else author

    # Create clickable card using HTML anchor tag (like friend's movie app)
    card_html = f"""
    <a href='?selected={encoded_book_id}' target="_self" style="text-decoration: none; display: block;">
        <div class="book-card-container book-card-{unique_id}" style="
            width: 100%;
            height: 320px;
            border-radius: 16px;
            overflow: hidden;
            background: rgba(30, 30, 46, 0.4);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            border: 2px solid rgba(6, 182, 212, 0.3);
            position: relative;
            cursor: pointer;
        ">
            <div style="position: relative; width: 100%; height: 100%; padding: 0; margin: 0;">
                <img src="{cover_url}"
                     alt="{title}"
                     style="
                         width: 100%;
                         height: 100%;
                         object-fit: cover;
                         display: block;
                         margin: 0;
                         padding: 0;
                     ">
                <div class="book-overlay" style="
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    background: linear-gradient(180deg, transparent 0%, rgba(0, 0, 0, 0.9) 100%);
                    padding: 12px;
                    color: white;
                    opacity: 0;
                    transition: opacity 0.3s ease;
                    pointer-events: none;
                ">
                    <div style="font-size: 0.875rem; font-weight: 600; margin-bottom: 4px;
                                overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {display_title}
                    </div>
                    <div style="font-size: 0.75rem; color: #d1d5db;
                                overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                        {display_author}
                    </div>
                </div>
            </div>
        </div>
    </a>

    <style>
        /* Hover effects when hovering over the anchor tag */
        a:has(.book-card-{unique_id}):hover .book-card-{unique_id} {{
            transform: translateY(-8px) scale(1.02) !important;
            box-shadow: 0 20px 40px rgba(6, 182, 212, 0.6) !important;
            border-color: #06b6d4 !important;
        }}

        a:has(.book-card-{unique_id}):hover .book-overlay {{
            opacity: 1 !important;
        }}
    </style>
    """

    st.markdown(card_html, unsafe_allow_html=True)
