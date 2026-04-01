from __future__ import annotations

import random
import time
import urllib.parse
import urllib.robotparser
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_fixed

from core.config import AppConfig
from core.models import CrawlResult


class Crawler:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": config.user_agent})

    def _robots_allowed(self, url: str) -> bool:
        parsed = urllib.parse.urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        try:
            rp.set_url(robots_url)
            rp.read()
            return rp.can_fetch(self.config.user_agent, url)
        except Exception:
            return True

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def _fetch(self, url: str) -> requests.Response:
        return self.session.get(url, timeout=self.config.request_timeout_sec, allow_redirects=True)

    def get(self, url: str) -> CrawlResult:
        if not self._robots_allowed(url):
            raise PermissionError("robots.txt disallow")
        time.sleep(random.uniform(self.config.min_delay_sec, self.config.max_delay_sec))
        resp = self._fetch(url)
        if resp.status_code >= 400:
            raise ValueError(f"HTTP {resp.status_code}")
        soup = BeautifulSoup(resp.text, "lxml")
        title = (soup.title.string or "").strip() if soup.title else ""
        text = soup.get_text(" ", strip=True)
        return CrawlResult(url=url, status_code=resp.status_code, title=title, text=text[:80000], fetched_at=datetime.utcnow())
