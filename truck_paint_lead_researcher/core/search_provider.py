from __future__ import annotations

from abc import ABC, abstractmethod

from core.models import SearchResult


class SearchProvider(ABC):
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> list[SearchResult]:
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError
