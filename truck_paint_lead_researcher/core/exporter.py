from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

import pandas as pd

from core.models import ErrorRecord, LeadRecord


class Exporter:
    def __init__(self, output_dir: str) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_leads(self, leads: list[LeadRecord], filename: str) -> Path:
        p = self.output_dir / filename
        df = pd.DataFrame([asdict(x) for x in leads], columns=LeadRecord.columns())
        df.to_csv(p, index=False, encoding="utf-8-sig")
        return p

    def export_errors(self, errors: list[ErrorRecord], filename: str) -> Path:
        p = self.output_dir / filename
        df = pd.DataFrame([asdict(x) for x in errors], columns=["url", "reason", "at"])
        df.to_csv(p, index=False, encoding="utf-8-sig")
        return p
