from __future__ import annotations

from duckduckgo_search import DDGS

from core.models import SearchResult
from core.search_provider import SearchProvider


class DuckDuckGoProvider(SearchProvider):
    @property
    def name(self) -> str:
        return "DuckDuckGo"

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        results: list[SearchResult] = []
        with DDGS() as ddgs:
            for row in ddgs.text(query, region="jp-jp", max_results=limit):
                url = row.get("href")
                if not url:
                    continue
                results.append(
                    SearchResult(
                        query=query,
                        title=row.get("title", ""),
                        url=url,
                        snippet=row.get("body", ""),
                    )
                )
        return results
