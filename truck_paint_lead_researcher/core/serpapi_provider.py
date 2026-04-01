from __future__ import annotations

import requests

from core.models import SearchResult
from core.search_provider import SearchProvider


class SerpApiProvider(SearchProvider):
    def __init__(self, api_key: str, timeout_sec: int = 12) -> None:
        self.api_key = api_key
        self.timeout_sec = timeout_sec

    @property
    def name(self) -> str:
        return "SerpAPI"

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        params = {
            "engine": "google",
            "q": query,
            "api_key": self.api_key,
            "num": min(limit, 100),
            "hl": "ja",
            "gl": "jp",
        }
        resp = requests.get("https://serpapi.com/search", params=params, timeout=self.timeout_sec)
        resp.raise_for_status()
        data = resp.json()
        out: list[SearchResult] = []
        for item in data.get("organic_results", [])[:limit]:
            link = item.get("link")
            if not link:
                continue
            out.append(
                SearchResult(
                    query=query,
                    title=item.get("title", ""),
                    url=link,
                    snippet=item.get("snippet", ""),
                )
            )
        return out
