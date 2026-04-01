# Truck Paint Lead Researcher

公開Web情報のみを対象に、トラックペイント広告に親和性が高い企業候補・個人候補を収集し、CSVに出力するWindows向けGUIアプリです。

## セットアップ

```bash
cd truck_paint_lead_researcher
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## 実行手順

```bash
python app.py
```

- ターゲット種別（企業/個人/両方）を選択
- キーワード（空ならプリセット自動展開）
- 地域キーワード
- 取得件数上限（最大1000）
- 出力フォルダ
- 実行

## SerpAPI キー設定方法

`data/config.json` の `serpapi_key` にキーを設定します。

```json
{
  "serpapi_key": "YOUR_SERPAPI_KEY"
}
```

検索優先順位は以下です。
1. SerpAPI
2. DuckDuckGo
3. URLシードCSV

## 検索失敗時の代替運用（URLリストCSV投入）

`data/url_seed_sample.csv` を複製し、`url`列に処理対象の公開URLを記載してください。`config.json` の `seed_url_csv_path` を差し替えると読み込まれます。

## 利用上の注意

- X API / ログイン自動化 / DM自動送信は行いません。
- 公開ページのみ対象です。
- robots.txt と過剰アクセス回避のため、待機・タイムアウト・リトライを設定しています。
- 出力は調査補助用途です。利用可否判断・連絡実施は必ず人間が行ってください。

## CSV列説明

出力列:
- category
- source_keyword
- name
- company_name
- title_or_affiliation
- location
- website_url
- x_account_url
- x_handle
- followers
- following
- ff_ratio
- last_activity_estimate
- active_status
- revenue_estimate
- lead_score
- sponsor_fit_score
- support_intent_score
- activity_score
- visibility_score
- reasoning
- source_page_title
- source_page_url
- collected_at

## exe化手順（PyInstaller）

```bash
cd truck_paint_lead_researcher
pyinstaller --noconfirm --onefile --windowed --name TruckPaintLeadResearcher app.py
```

生成物は `dist/TruckPaintLeadResearcher.exe` です。

## インストーラーパッケージ化（Inno Setup）

### 前提
- Windows
- Inno Setup 6（`ISCC.exe` が利用可能）

### ビルド手順

```bat
cd truck_paint_lead_researcher\installer
build_installer.bat
```

上記で以下が生成されます。
- 実行ファイル: `truck_paint_lead_researcher/dist/TruckPaintLeadResearcher.exe`
- インストーラー: `truck_paint_lead_researcher/dist_installer/TruckPaintLeadResearcherSetup.exe`

### スクリプト説明
- `installer/truck_paint_lead_researcher.spec`: PyInstaller用設定（`data/` 同梱）
- `installer/installer.iss`: Inno Setup用インストーラースクリプト
- `installer/build_installer.bat`: exe生成 + インストーラー生成の一括実行
