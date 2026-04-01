from __future__ import annotations

from itertools import product

SUPPORT_TERMS = ["支援", "応援", "寄付", "協賛", "社会課題"]
AD_TERMS = ["広告", "PR", "OOH", "スポンサー", "採用広報"]


def build_queries(
    base_keywords: list[str],
    region_keywords: list[str],
    max_queries: int,
) -> list[str]:
    regions = region_keywords or [""]
    queries: list[str] = []
    for base, region, support, ad in product(base_keywords, regions, SUPPORT_TERMS, AD_TERMS):
        q = " ".join([p for p in [base, region.strip(), support, ad] if p]).strip()
        if q not in queries:
            queries.append(q)
        if len(queries) >= max_queries:
            break
    return queries[:max_queries]
