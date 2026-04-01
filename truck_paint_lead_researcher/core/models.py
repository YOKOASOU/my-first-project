from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

Category = Literal["企業", "個人"]
ActiveStatus = Literal["active", "semi-active", "inactive", "unknown"]


@dataclass
class SearchResult:
    query: str
    title: str
    url: str
    snippet: str = ""


@dataclass
class CrawlResult:
    url: str
    status_code: int
    title: str
    text: str
    fetched_at: datetime


@dataclass
class LeadRecord:
    category: Category
    source_keyword: str
    name: str
    company_name: str
    title_or_affiliation: str
    location: str
    website_url: str
    x_account_url: str
    x_handle: str
    followers: Optional[int]
    following: Optional[int]
    ff_ratio: Optional[float]
    last_activity_estimate: str
    active_status: ActiveStatus
    revenue_estimate: str
    lead_score: float
    sponsor_fit_score: float
    support_intent_score: float
    activity_score: float
    visibility_score: float
    reasoning: str
    source_page_title: str
    source_page_url: str
    collected_at: str

    @staticmethod
    def columns() -> list[str]:
        return [
            "category",
            "source_keyword",
            "name",
            "company_name",
            "title_or_affiliation",
            "location",
            "website_url",
            "x_account_url",
            "x_handle",
            "followers",
            "following",
            "ff_ratio",
            "last_activity_estimate",
            "active_status",
            "revenue_estimate",
            "lead_score",
            "sponsor_fit_score",
            "support_intent_score",
            "activity_score",
            "visibility_score",
            "reasoning",
            "source_page_title",
            "source_page_url",
            "collected_at",
        ]


@dataclass
class ErrorRecord:
    url: str
    reason: str
    at: str
