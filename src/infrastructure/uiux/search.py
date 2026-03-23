# src/infrastructure/uiux/search.py
"""
BM25-style search for UI/UX resources.

Provides relevance ranking for design resource search.
"""

import logging
from typing import List, Dict, Any, Optional
import math

from .loader import get_loader
from .resources import UIUXResource, UIUXCategory

logger = logging.getLogger(__name__)


class BM25Search:
    """
    BM25 ranking algorithm for UI/UX resources.

    Provides weighted search across resource fields.
    """

    def __init__(self):
        self.loader = get_loader()
        self._index: Dict[str, List[Dict[str, Any]]] = {}

    def search(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 3
    ) -> List[UIUXResource]:
        """
        Search for UI/UX resources.

        Args:
            query: Natural language search query
            category: Optional category filter
            max_results: Maximum number of results

        Returns:
            List of ranked UIUXResource
        """
        if not query:
            return []

        # Get resources from category or all
        if category:
            resources = self.loader.load_category(category)
        else:
            # Search across all categories
            all_data = self.loader.load_all()
            resources = []
            for cat_resources in all_data.values():
                resources.extend(cat_resources)

        # Score and rank
        scored = self._bm25_score(resources, query)

        # Convert to UIUXResource and limit
        results = []
        for item in scored[:max_results]:
            cat = UIUXCategory(item.get("category", "styles"))
            resource = UIUXResource(
                id=item.get("id", ""),
                category=cat,
                name=item.get("name", ""),
                description=item.get("description", ""),
                data=item.get("data", {}),
                score=item.get("_score", 0.0),
                tags=item.get("tags", []),
            )
            results.append(resource)

        logger.info(f"Search '{query}' in {category or 'all'}: {len(results)} results")
        return results

    def _bm25_score(
        self,
        documents: List[Dict[str, Any]],
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Score documents using BM25-inspired ranking.

        Args:
            documents: List of resource dicts
            query: Search query

        Returns:
            List of documents with scores
        """
        if not documents:
            return []

        # Parse query terms
        query_terms = query.lower().split()

        # Calculate average document length
        avg_dl = sum(len(self._get_text(doc)) for doc in documents) / len(documents)

        # BM25 parameters
        k1 = 1.5
        b = 0.75

        # Calculate IDF for each term
        idf = {}
        for term in query_terms:
            doc_freq = sum(1 for doc in documents if term in self._get_text(doc).lower())
            if doc_freq > 0:
                idf[term] = math.log((len(documents) - doc_freq + 0.5) / (doc_freq + 0.5) + 1)
            else:
                idf[term] = 0

        # Score each document
        scored_docs = []
        for doc in documents:
            doc_text = self._get_text(doc).lower()
            doc_len = len(doc_text)

            score = 0.0
            for term in query_terms:
                if term in doc_text:
                    # Term frequency in document
                    tf = doc_text.count(term)
                    # BM25 term weight
                    tf_weight = (tf * (k1 + 1)) / (tf + k1 * (1 - b + b * (doc_len / avg_dl)))
                    score += idf.get(term, 0) * tf_weight

            if score > 0:
                doc_copy = doc.copy()
                doc_copy["_score"] = score
                scored_docs.append(doc_copy)

        # Sort by score
        scored_docs.sort(key=lambda x: x.get("_score", 0), reverse=True)
        return scored_docs

    def _get_text(self, doc: Dict[str, Any]) -> str:
        """Get searchable text from document."""
        parts = [
            doc.get("name", ""),
            doc.get("description", ""),
            " ".join(doc.get("tags", [])),
            " ".join(str(v) for v in doc.get("data", {}).values() if isinstance(v, str))
        ]
        return " ".join(parts)

    # Convenience methods for each category

    def search_styles(self, query: str, max_results: int = 3) -> List[UIUXResource]:
        """Search UI styles."""
        return self.search(query, category="styles", max_results=max_results)

    def search_colors(self, query: str, max_results: int = 3) -> List[UIUXResource]:
        """Search color palettes."""
        return self.search(query, category="colors", max_results=max_results)

    def search_typography(self, query: str, max_results: int = 3) -> List[UIUXResource]:
        """Search typography."""
        return self.search(query, category="typography", max_results=max_results)

    def search_icons(self, query: str, max_results: int = 3) -> List[UIUXResource]:
        """Search icons."""
        return self.search(query, category="icons", max_results=max_results)

    def search_ux_guidelines(self, query: str, max_results: int = 3) -> List[UIUXResource]:
        """Search UX guidelines."""
        return self.search(query, category="ux_guidelines", max_results=max_results)

    def search_stack(self, query: str, framework: Optional[str] = None, max_results: int = 3) -> List[UIUXResource]:
        """Search framework guidelines."""
        results = self.search(query, category="stack", max_results=max_results * 2)
        if framework:
            # Check both root level (legacy) and data level
            results = [r for r in results if r.data.get("framework") == framework or r.tags.get(0) == framework]
        return results[:max_results]


# Singleton instance
_search: Optional[BM25Search] = None


def get_search() -> BM25Search:
    """Get the BM25 search singleton."""
    global _search
    if _search is None:
        _search = BM25Search()
    return _search
