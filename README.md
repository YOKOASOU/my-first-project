# X 自動投稿ツール

コマンドラインからX (Twitter) に投稿できるツールです。

## セットアップ

### 1. X API キーの取得

1. [X Developer Portal](https://developer.x.com/en/portal/dashboard) にアクセス
2. アカウントがなければ「Sign up」から開発者アカウントを作成
3. 「Projects & Apps」からプロジェクトを作成
4. アプリの「Keys and tokens」タブから以下を取得:
   - **API Key** と **API Key Secret**
   - **Access Token** と **Access Token Secret**

> **注意**: Access Token の権限は「Read and Write」に設定してください。「Read」のみだと投稿できません。

### 2. 環境設定

```bash
# ライブラリをインストール
pip install -r requirements.txt

# 環境変数ファイルを作成
cp .env.example .env
```

`.env` ファイルを開いて、取得したAPIキーを入力してください。

### 3. 投稿する

```bash
python post.py "こんにちは、Xから投稿テスト！"
```

投稿に成功すると、投稿のURLが表示されます。
