"""
Intelligent Search Module with Fuzzy Matching and AI-Powered Typo Correction

This module provides advanced search intelligence features including fuzzy matching,
automatic typo correction, query enhancement, and alternative query suggestions.
It implements Google-like "Did you mean...?" functionality for improved search UX.

Key Features:
    - Fuzzy matching using RapidFuzz for typo-tolerant search
    - AI-powered typo detection and correction
    - Query understanding and intent extraction
    - Alternative query suggestions for better results
    - Automatic retry logic for all AI operations

Classes:
    SearchIntelligence: Main class providing all search intelligence features

Methods:
    analyze_query_and_results: Analyze search results and suggest corrections
    fuzzy_match_books: Perform fuzzy matching on book titles/authors
    enhance_query_understanding: Extract intent and parameters from queries
    suggest_alternative_queries: Provide alternative search suggestions

Usage:
    from Bookvault.search_intelligence import SearchIntelligence

    search_ai = SearchIntelligence()

    # Check if correction is needed
    correction, should_auto_correct = search_ai.analyze_query_and_results(
        query="harry poter",
        results=[]
    )

    # Get alternative suggestions
    alternatives = search_ai.suggest_alternative_queries("obscure sci-fi")

Configuration:
    All AI operations use centralized configuration from Config class:
    - OPENAI_MODEL: Model to use for AI operations
    - RETRY_MAX_ATTEMPTS: Number of retries for failed API calls
    - OPENAI_TEMPERATURE_*: Temperature settings for different task types
"""

import os

from typing import List, Dict, Optional, Tuple
from rapidfuzz import fuzz
from openai import OpenAI
from .apis.openai_engine import retry_on_failure
from .config import Config


class SearchIntelligence:
    """Handles intelligent search with fuzzy matching and typo correction"""

    def __init__(self):
        self.openai_client = None
        try:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        except Exception:
            pass

    def analyze_query_and_results(
        self,
        query: str,
        results: List[Dict],
        threshold: int = 3
    ) -> Tuple[Optional[str], bool]:
        """
        Analyze search query and results to determine if we should suggest a correction.

        Args:
            query: The user's search query
            results: List of search results
            threshold: Minimum number of results to consider successful (default: 3)

        Returns:
            Tuple of (suggested_correction, should_auto_correct)
            - suggested_correction: The corrected query or None
            - should_auto_correct: Whether to automatically apply correction
        """
        # If we have enough results, no correction needed
        if results and len(results) >= threshold:
            return None, False

        # Try to get AI-powered correction
        correction = self._get_ai_correction(query)

        # If we have very few or no results, suggest auto-correction
        should_auto_correct = len(results) == 0 and correction is not None

        return correction, should_auto_correct

    def fuzzy_match_books(
        self,
        query: str,
        books: List[Dict],
        min_score: int = 60
    ) -> List[Dict]:
        """
        Perform fuzzy matching on book titles and authors to find close matches.

        Args:
            query: Search query
            books: List of books to search through
            min_score: Minimum similarity score (0-100)

        Returns:
            List of books that match, sorted by relevance
        """
        if not books:
            return []

        query_lower = query.lower().strip()
        scored_books = []

        for book in books:
            title = book.get('title', '').lower()
            author = book.get('author', '').lower()

            # Calculate fuzzy match scores
            title_score = fuzz.partial_ratio(query_lower, title)
            author_score = fuzz.partial_ratio(query_lower, author)
            combined_text = f"{title} {author}"
            combined_score = fuzz.partial_ratio(query_lower, combined_text)

            # Use the best score
            best_score = max(title_score, author_score, combined_score)

            if best_score >= min_score:
                scored_books.append((book, best_score))

        # Sort by score (descending)
        scored_books.sort(key=lambda x: x[1], reverse=True)

        return [book for book, score in scored_books]

    @retry_on_failure(
        max_retries=Config.RETRY_MAX_ATTEMPTS,
        delay=Config.RETRY_INITIAL_DELAY,
        backoff=Config.RETRY_BACKOFF_MULTIPLIER
    )
    def _get_ai_correction(self, query: str) -> Optional[str]:
        """
        Use OpenAI to detect and correct typos in the search query.

        Args:
            query: The user's search query

        Returns:
            Corrected query or None if no correction needed
        """
        if not self.openai_client:
            return None

        prompt = f"""You are a search query correction assistant for a book discovery platform.

User's search query: "{query}"

Analyze this query and:
1. Detect if there are any typos or spelling mistakes
2. If there are typos, provide a corrected version
3. If the query is already correct, return "CORRECT"

Return ONLY the corrected query or "CORRECT", nothing else.

Examples:
- "harry poter" -> "harry potter"
- "lord of the rigns" -> "lord of the rings"
- "stephan king" -> "stephen king"
- "sci fi books" -> "CORRECT"
- "mistery thriler" -> "mystery thriller"
- "agatha cristie" -> "agatha christie"

Corrected query:"""

        response = self.openai_client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=Config.OPENAI_MAX_TOKENS_SHORT,
            temperature=Config.OPENAI_TEMPERATURE_PRECISE  # Low temperature for consistent corrections
        )

        correction = response.choices[0].message.content.strip()

        # If AI says it's correct or returns the same query, no correction needed
        if correction == "CORRECT" or correction.lower() == query.lower():
            return None

        return correction

    def enhance_query_understanding(self, query: str) -> Dict[str, any]:
        """
        Use AI to understand the user's intent and extract search parameters.

        Args:
            query: Natural language query

        Returns:
            Dictionary with extracted information (keywords, genre, author, etc.)
        """
        # Fallback response
        fallback = {
            "keywords": query,
            "genre": None,
            "author": None,
            "intent": "general_search"
        }

        if not self.openai_client:
            return fallback

        try:
            result = self._call_enhance_query_ai(query)

            # Parse the response
            info = {
                "keywords": query,
                "genre": None,
                "author": None,
                "intent": "general_search"
            }

            for line in result.split('\n'):
                if line.startswith('KEYWORDS:'):
                    keywords = line.replace('KEYWORDS:', '').strip()
                    if keywords and keywords.lower() != 'none':
                        info["keywords"] = keywords
                elif line.startswith('GENRE:'):
                    genre = line.replace('GENRE:', '').strip()
                    if genre and genre.lower() != 'none':
                        info["genre"] = genre
                elif line.startswith('AUTHOR:'):
                    author = line.replace('AUTHOR:', '').strip()
                    if author and author.lower() != 'none':
                        info["author"] = author
                elif line.startswith('INTENT:'):
                    intent = line.replace('INTENT:', '').strip()
                    if intent:
                        info["intent"] = intent

            return info

        except Exception:
            # Fallback to basic extraction
            return fallback

    @retry_on_failure(
        max_retries=Config.RETRY_MAX_ATTEMPTS,
        delay=Config.RETRY_INITIAL_DELAY,
        backoff=Config.RETRY_BACKOFF_MULTIPLIER
    )
    def _call_enhance_query_ai(self, query: str) -> str:
        """Call OpenAI API for query understanding with retry logic"""
        prompt = f"""Analyze this book search query and extract structured information.

Query: "{query}"

Extract and return in this exact format:
KEYWORDS: <main search terms>
GENRE: <genre if mentioned, or "none">
AUTHOR: <author name if mentioned, or "none">
INTENT: <one of: title_search, author_search, genre_search, recommendation_request, general_search>

Examples:
Query: "books like Harry Potter"
KEYWORDS: fantasy adventure magic
GENRE: fantasy
AUTHOR: none
INTENT: recommendation_request

Query: "Stephen King horror novels"
KEYWORDS: horror novels
GENRE: horror
AUTHOR: Stephen King
INTENT: author_search

Query: "the great gatsby"
KEYWORDS: the great gatsby
GENRE: none
AUTHOR: none
INTENT: title_search

Now analyze: "{query}"
"""

        response = self.openai_client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=Config.OPENAI_MAX_TOKENS_MEDIUM,
            temperature=Config.OPENAI_TEMPERATURE_BALANCED
        )

        return response.choices[0].message.content.strip()

    def suggest_alternative_queries(self, query: str) -> List[str]:
        """
        Suggest alternative search queries based on the original query.

        Args:
            query: Original search query

        Returns:
            List of suggested alternative queries
        """
        if not self.openai_client:
            return []

        try:
            suggestions_text = self._call_suggest_alternatives_ai(query)
            suggestions = suggestions_text.strip().split('\n')
            return [s.strip() for s in suggestions if s.strip() and s.strip() != query][:3]

        except Exception:
            return []

    @retry_on_failure(
        max_retries=Config.RETRY_MAX_ATTEMPTS,
        delay=Config.RETRY_INITIAL_DELAY,
        backoff=Config.RETRY_BACKOFF_MULTIPLIER
    )
    def _call_suggest_alternatives_ai(self, query: str) -> str:
        """Call OpenAI API for alternative query suggestions with retry logic"""
        prompt = f"""Given this book search query that returned few or no results: "{query}"

Suggest 3 alternative ways to search that might yield better results. Consider:
- Related genres or themes
- Similar authors
- Broader or more specific terms

Return ONLY the 3 alternative queries, one per line, nothing else.

Examples:
Query: "obscure sci-fi from the 80s"
hard science fiction
classic science fiction
cyberpunk novels

Query: "books about cooking"
cookbook
culinary arts
food and wine

Now suggest for: "{query}"
"""

        response = self.openai_client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=Config.OPENAI_MAX_TOKENS_MEDIUM,
            temperature=Config.OPENAI_TEMPERATURE_CREATIVE
        )

        return response.choices[0].message.content
