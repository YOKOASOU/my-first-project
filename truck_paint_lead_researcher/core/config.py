from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class WeightConfig:
    sponsor_fit_score: float = 0.35
    support_intent_score: float = 0.20
    activity_score: float = 0.30
    visibility_score: float = 0.15


@dataclass
class AppConfig:
    max_results_default: int = 300
    max_results_cap: int = 1000
    max_queries: int = 60
    request_timeout_sec: int = 12
    retry_count: int = 2
    min_delay_sec: float = 0.5
    max_delay_sec: float = 1.2
    user_agent: str = "TruckPaintLeadResearcher/1.0 (+public-web-research)"
    serpapi_key: str = ""
    seed_url_csv_path: str = "truck_paint_lead_researcher/data/url_seed_sample.csv"
    output_dir: str = "truck_paint_lead_researcher/data/output"
    weights: WeightConfig = field(default_factory=WeightConfig)


DEFAULT_CONFIG_PATH = Path("truck_paint_lead_researcher/data/config.json")


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> AppConfig:
    if not path.exists():
        cfg = AppConfig()
        save_config(cfg, path)
        return cfg
    data = json.loads(path.read_text(encoding="utf-8"))
    weights = WeightConfig(**data.get("weights", {}))
    data["weights"] = weights
    return AppConfig(**data)


def save_config(config: AppConfig, path: Path = DEFAULT_CONFIG_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(asdict(config), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


CORP_PRESET = [
    "物流支援", "地方創生 PR", "採用広報", "OOH 広告", "ブランド認知", "スポンサー 企業",
    "社会貢献 企業", "D2C PR", "飲食チェーン PR", "観光 PR", "地域応援 企業", "インフラ 支援",
]

PERSON_PRESET = [
    "運送業界 応援", "物流 支援", "寄付 広告", "トラック 好き", "地域経済 応援", "社会インフラ 支援",
    "ドライバー 応援", "物流 啓発", "交通 安全 発信", "地方創生 個人支援",
]
