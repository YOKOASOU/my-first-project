"""X (Twitter) 自動投稿スクリプト"""

import argparse
import sys

import tweepy
from dotenv import load_dotenv
import os


def get_client():
    """認証済みのX APIクライアントを返す"""
    load_dotenv()

    required_keys = [
        "X_API_KEY",
        "X_API_SECRET",
        "X_ACCESS_TOKEN",
        "X_ACCESS_TOKEN_SECRET",
    ]

    missing = [key for key in required_keys if not os.getenv(key)]
    if missing:
        print(f"エラー: 以下の環境変数が .env に設定されていません:")
        for key in missing:
            print(f"  - {key}")
        print("\n.env.example を参考に .env ファイルを作成してください。")
        sys.exit(1)

    client = tweepy.Client(
        consumer_key=os.getenv("X_API_KEY"),
        consumer_secret=os.getenv("X_API_SECRET"),
        access_token=os.getenv("X_ACCESS_TOKEN"),
        access_token_secret=os.getenv("X_ACCESS_TOKEN_SECRET"),
    )
    return client


def post_tweet(text):
    """テキストをXに投稿する"""
    if len(text) > 280:
        print(f"エラー: 投稿は280文字以内にしてください（現在 {len(text)} 文字）")
        sys.exit(1)

    client = get_client()
    response = client.create_tweet(text=text)
    tweet_id = response.data["id"]
    print(f"投稿しました！")
    print(f"https://x.com/i/status/{tweet_id}")
    return response


def main():
    parser = argparse.ArgumentParser(description="X (Twitter) に投稿する")
    parser.add_argument("text", help="投稿するテキスト")
    args = parser.parse_args()

    post_tweet(args.text)


if __name__ == "__main__":
    main()
