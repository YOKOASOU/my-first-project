from __future__ import annotations

from core.config import WeightConfig

SPONSOR_HINTS = ["広告", "PR", "スポンサー", "採用", "ブランド", "OOH", "協賛"]
SUPPORT_HINTS = ["物流", "運送", "ドライバー", "支援", "応援", "地域", "インフラ"]
VISIBILITY_HINTS = ["メディア", "フォロワー", "note", "YouTube", "Instagram", "X"]


def _score_by_hits(text: str, hints: list[str], base: int = 20, gain: int = 12) -> int:
    hits = sum(1 for h in hints if h.lower() in text.lower())
    return max(0, min(100, base + hits * gain))


def score_activity(active_status: str, text: str) -> int:
    if active_status == "active":
        return 90
    if active_status == "semi-active":
        return 65
    if active_status == "inactive":
        return 30
    return 40 if "更新" in text else 25


def calc_scores(text: str, active_status: str, weights: WeightConfig) -> dict[str, float | str]:
    sponsor = _score_by_hits(text, SPONSOR_HINTS)
    support = _score_by_hits(text, SUPPORT_HINTS)
    visibility = _score_by_hits(text, VISIBILITY_HINTS, base=15, gain=14)
    activity = score_activity(active_status, text)
    lead = (
        sponsor * weights.sponsor_fit_score
        + support * weights.support_intent_score
        + activity * weights.activity_score
        + visibility * weights.visibility_score
    )
    reasoning = f"広告親和性:{sponsor}, 支援意図:{support}, 活動性:{activity}, 露出:{visibility}の加重平均。"
    return {
        "sponsor_fit_score": float(sponsor),
        "support_intent_score": float(support),
        "activity_score": float(activity),
        "visibility_score": float(visibility),
        "lead_score": round(float(lead), 2),
        "reasoning": reasoning,
    }
