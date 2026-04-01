from __future__ import annotations

import os
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox

try:
    import customtkinter as ctk
except Exception:  # fallback
    import tkinter as ctk  # type: ignore

from core.config import CORP_PRESET, PERSON_PRESET, DEFAULT_CONFIG_PATH, AppConfig, load_config, save_config
from core.crawler import Crawler
from core.exporter import Exporter
from core.extractor import extract_basic
from core.logger import get_logger
from core.models import ErrorRecord, LeadRecord, SearchResult
from core.query_builder import build_queries
from core.scorer import calc_scores
from core.serpapi_provider import SerpApiProvider
from core.duckduckgo_provider import DuckDuckGoProvider
from core.url_seed_provider import UrlSeedProvider
from core.utils import safe_ratio, utc_now_iso


class MainWindow(ctk.CTk if hasattr(ctk, "CTk") else ctk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Truck Paint Lead Researcher")
        self.geometry("1100x800")
        self.config_obj: AppConfig = load_config(DEFAULT_CONFIG_PATH)
        self.logger = get_logger()
        self.stop_event = threading.Event()
        self.worker: threading.Thread | None = None
        self.last_csv_path: str = ""

        self._build_ui()
        self._load_form_from_config()

    def _build_ui(self) -> None:
        self.target_var = ctk.StringVar(value="両方")
        self.limit_var = ctk.StringVar(value=str(self.config_obj.max_results_default))
        self.region_var = ctk.StringVar()
        self.output_var = ctk.StringVar(value=self.config_obj.output_dir)

        row = 0
        ctk.CTkLabel(self, text="ターゲット種別").grid(row=row, column=0, sticky="w")
        ctk.CTkOptionMenu(self, values=["企業", "個人", "両方"], variable=self.target_var).grid(row=row, column=1, sticky="ew")
        row += 1
        ctk.CTkLabel(self, text="キーワード（改行区切り）").grid(row=row, column=0, sticky="nw")
        self.keyword_text = ctk.CTkTextbox(self, width=500, height=120)
        self.keyword_text.grid(row=row, column=1, sticky="ew")
        row += 1
        ctk.CTkLabel(self, text="地域キーワード（改行区切り）").grid(row=row, column=0, sticky="nw")
        self.region_text = ctk.CTkTextbox(self, width=500, height=80)
        self.region_text.grid(row=row, column=1, sticky="ew")
        row += 1

        ctk.CTkLabel(self, text="取得件数上限(<=1000)").grid(row=row, column=0, sticky="w")
        ctk.CTkEntry(self, textvariable=self.limit_var).grid(row=row, column=1, sticky="ew")
        row += 1

        ctk.CTkLabel(self, text="出力先フォルダ").grid(row=row, column=0, sticky="w")
        ctk.CTkEntry(self, textvariable=self.output_var).grid(row=row, column=1, sticky="ew")
        ctk.CTkButton(self, text="参照", command=self._choose_output).grid(row=row, column=2)
        row += 1

        ctk.CTkButton(self, text="実行", command=self.start).grid(row=row, column=0)
        ctk.CTkButton(self, text="停止", command=self.stop).grid(row=row, column=1, sticky="w")
        ctk.CTkButton(self, text="CSVを開く", command=self.open_csv).grid(row=row, column=1, sticky="e")
        ctk.CTkButton(self, text="設定保存", command=self.save_settings).grid(row=row, column=2)
        ctk.CTkButton(self, text="設定読込", command=self.load_settings).grid(row=row, column=3)
        row += 1

        self.progress_label = ctk.CTkLabel(self, text="進捗: 待機中")
        self.progress_label.grid(row=row, column=0, columnspan=4, sticky="w")
        row += 1

        self.log_text = ctk.CTkTextbox(self, width=1000, height=280)
        self.log_text.grid(row=row, column=0, columnspan=4, sticky="nsew")
        row += 1

        caution = "このツールは公開Web情報の調査補助を目的としています。取得データの利用可否や連絡実施は、法令・利用規約・相手先ポリシーを確認のうえ、必ず人間が判断してください。"
        ctk.CTkLabel(self, text=caution, wraplength=980, justify="left").grid(row=row, column=0, columnspan=4, sticky="w")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(row - 1, weight=1)

    def _log(self, msg: str) -> None:
        self.logger.info(msg)
        self.log_text.insert("end", msg + "\n")
        self.log_text.see("end")

    def _choose_output(self) -> None:
        folder = filedialog.askdirectory(initialdir=self.output_var.get())
        if folder:
            self.output_var.set(folder)

    def _load_form_from_config(self) -> None:
        self.keyword_text.delete("1.0", "end")
        self.region_text.delete("1.0", "end")
        self.region_text.insert("1.0", "")

    def _pick_provider(self):
        if self.config_obj.serpapi_key:
            return SerpApiProvider(self.config_obj.serpapi_key, self.config_obj.request_timeout_sec)
        try:
            return DuckDuckGoProvider()
        except Exception:
            return UrlSeedProvider(self.config_obj.seed_url_csv_path)

    def _collect_keywords(self, target: str) -> list[str]:
        raw = self.keyword_text.get("1.0", "end").strip()
        if raw:
            return [x.strip() for x in raw.splitlines() if x.strip()]
        if target == "企業":
            return CORP_PRESET
        if target == "個人":
            return PERSON_PRESET
        return list(dict.fromkeys(CORP_PRESET + PERSON_PRESET))

    def start(self) -> None:
        if self.worker and self.worker.is_alive():
            messagebox.showinfo("Info", "実行中です")
            return
        self.stop_event.clear()
        self.worker = threading.Thread(target=self._run_pipeline, daemon=True)
        self.worker.start()

    def stop(self) -> None:
        self.stop_event.set()
        self._log("停止要求を受け付けました。")

    def _run_pipeline(self) -> None:
        try:
            target = self.target_var.get()
            keywords = self._collect_keywords(target)
            regions = [x.strip() for x in self.region_text.get("1.0", "end").splitlines() if x.strip()]
            limit = min(int(self.limit_var.get() or 300), self.config_obj.max_results_cap)
            provider = self._pick_provider()
            crawler = Crawler(self.config_obj)
            exporter = Exporter(self.output_var.get())

            queries = build_queries(keywords, regions, self.config_obj.max_queries)
            self._log(f"検索プロバイダ: {provider.name}, クエリ数: {len(queries)}")

            seen_urls: set[str] = set()
            leads: list[LeadRecord] = []
            errors: list[ErrorRecord] = []
            q_count = len(queries)

            for i, q in enumerate(queries, start=1):
                if self.stop_event.is_set() or len(leads) >= limit:
                    break
                self.progress_label.configure(text=f"進捗: クエリ {i}/{q_count}")
                results: list[SearchResult] = provider.search(q, limit=10)
                for r in results:
                    if self.stop_event.is_set() or len(leads) >= limit:
                        break
                    if r.url in seen_urls:
                        continue
                    seen_urls.add(r.url)
                    try:
                        c = crawler.get(r.url)
                        if any(x in r.url.lower() for x in ["/login", "signin", "404"]):
                            continue
                        basic = extract_basic(c)
                        sc = calc_scores(c.text, str(basic["active_status"]), self.config_obj.weights)
                        cat = "企業" if target != "個人" and any(k in c.text for k in ["株式会社", "有限会社", "Inc", "Corp"]) else "個人"
                        followers = basic["followers"]
                        following = basic["following"]
                        lead = LeadRecord(
                            category=cat,
                            source_keyword=q,
                            name=c.title[:80] or "不明",
                            company_name=c.title[:80] if cat == "企業" else "",
                            title_or_affiliation="",
                            location=str(basic["location"] or ""),
                            website_url=r.url,
                            x_account_url=str(basic["x_account_url"] or ""),
                            x_handle=str(basic["x_handle"] or ""),
                            followers=followers,
                            following=following,
                            ff_ratio=safe_ratio(followers, following),
                            last_activity_estimate=str(basic["last_activity_estimate"] or ""),
                            active_status=str(basic["active_status"]),
                            revenue_estimate=str(basic["revenue_estimate"]),
                            lead_score=float(sc["lead_score"]),
                            sponsor_fit_score=float(sc["sponsor_fit_score"]),
                            support_intent_score=float(sc["support_intent_score"]),
                            activity_score=float(sc["activity_score"]),
                            visibility_score=float(sc["visibility_score"]),
                            reasoning=str(sc["reasoning"]),
                            source_page_title=c.title,
                            source_page_url=c.url,
                            collected_at=utc_now_iso(),
                        )
                        leads.append(lead)
                        if len(leads) % 20 == 0:
                            self.last_csv_path = str(exporter.export_leads(leads, "leads_incremental.csv"))
                    except Exception as e:
                        errors.append(ErrorRecord(url=r.url, reason=str(e), at=utc_now_iso()))

            self.last_csv_path = str(exporter.export_leads(leads, "leads_final.csv"))
            exporter.export_errors(errors, "errors.csv")
            self.progress_label.configure(text=f"完了: {len(leads)}件 / error {len(errors)}件")
            self._log(f"完了: {self.last_csv_path}")
        except Exception as e:
            self._log(f"致命的エラー: {e}")

    def open_csv(self) -> None:
        if not self.last_csv_path or not Path(self.last_csv_path).exists():
            messagebox.showwarning("Warning", "CSVが見つかりません")
            return
        if os.name == "nt":
            os.startfile(self.last_csv_path)  # type: ignore[attr-defined]
        else:
            webbrowser.open(f"file://{Path(self.last_csv_path).resolve()}")

    def save_settings(self) -> None:
        self.config_obj.output_dir = self.output_var.get().strip() or self.config_obj.output_dir
        self.config_obj.max_results_default = min(int(self.limit_var.get() or "300"), self.config_obj.max_results_cap)
        save_config(self.config_obj, DEFAULT_CONFIG_PATH)
        self._log("設定を保存しました。")

    def load_settings(self) -> None:
        self.config_obj = load_config(DEFAULT_CONFIG_PATH)
        self.limit_var.set(str(self.config_obj.max_results_default))
        self.output_var.set(self.config_obj.output_dir)
        self._log("設定を読み込みました。")
