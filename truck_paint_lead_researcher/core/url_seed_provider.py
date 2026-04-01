from __future__ import annotations

import csv
from pathlib import Path

from core.models import SearchResult
from core.search_provider import SearchProvider


class UrlSeedProvider(SearchProvider):
    def __init__(self, csv_path: str) -> None:
        self.csv_path = Path(csv_path)

    @property
    def name(self) -> str:
        return "URLSeedCSV"

    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        if not self.csv_path.exists():
            return []
        out: list[SearchResult] = []
        with self.csv_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                url = (row.get("url") or "").strip()
                if not url:
                    continue
                out.append(SearchResult(query=query, title=row.get("title", "seed"), url=url, snippet="seed"))
                if len(out) >= limit:
                    break
        return out
