from __future__ import annotations

import re
from datetime import datetime
from typing import Optional

from dateutil import parser as date_parser

from core.models import CrawlResult

X_URL_RE = re.compile(r"https?://(?:x|twitter)\.com/[A-Za-z0-9_]{1,15}")
FOLLOWERS_RE = re.compile(r"([0-9,]+)\s*followers", re.I)
FOLLOWING_RE = re.compile(r"([0-9,]+)\s*following", re.I)
DATE_RE = re.compile(r"(20\d{2}[/-]\d{1,2}[/-]\d{1,2})")
JAPAN_PREF_RE = re.compile(r"(東京都|北海道|(?:京都|大阪)府|..県)")


def extract_last_activity(text: str) -> tuple[str, str]:
    m = DATE_RE.search(text)
    if not m:
        return "", "unknown"
    try:
        dt = date_parser.parse(m.group(1)).date()
        days = (datetime.utcnow().date() - dt).days
        if days <= 31:
            return dt.isoformat(), "active"
        if days <= 90:
            return dt.isoformat(), "semi-active"
        return dt.isoformat(), "inactive"
    except Exception:
        return "", "unknown"


def extract_revenue(text: str) -> str:
    if "売上" in text or "年商" in text:
        m = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*億", text)
        if m:
            return f"約{m.group(1)}億"
    return "不明"


def extract_basic(crawl: CrawlResult) -> dict[str, Optional[str]]:
    x_url = ""
    x_handle = ""
    m = X_URL_RE.search(crawl.text)
    if m:
        x_url = m.group(0)
        x_handle = "@" + x_url.rstrip("/").split("/")[-1]
    followers = FOLLOWERS_RE.search(crawl.text)
    following = FOLLOWING_RE.search(crawl.text)
    last_act, status = extract_last_activity(crawl.text)
    location_match = JAPAN_PREF_RE.search(crawl.text)
    return {
        "x_account_url": x_url,
        "x_handle": x_handle,
        "followers": int(followers.group(1).replace(",", "")) if followers else None,
        "following": int(following.group(1).replace(",", "")) if following else None,
        "last_activity_estimate": last_act,
        "active_status": status,
        "location": location_match.group(1) if location_match else "",
        "revenue_estimate": extract_revenue(crawl.text),
    }
