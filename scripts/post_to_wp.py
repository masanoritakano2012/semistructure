#!/usr/bin/env python3
"""
WordPress REST API 下書き投稿スクリプト
semistructure.com 専用

使い方:
  python scripts/post_to_wp.py articles/draft/article.html \
      --title "記事タイトル" \
      --category semiconductor-companies

注意: WordPressへの投稿は必ず draft（下書き）として行う。
      高野氏の確認・承認なしに公開ステータスにしない。
"""

import argparse
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

WP_URL = os.getenv("WP_URL", "https://semistructure.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

CATEGORY_SLUGS = {
    "semiconductor-basics": None,
    "semiconductor-companies": None,
    "semiconductor-news": None,
    "ai-semiconductor": None,
    "semiconductor-career": None,
}


def get_auth() -> tuple[str, str]:
    if not WP_USERNAME or not WP_PASSWORD:
        print("エラー: .env に WP_USERNAME / WP_PASSWORD が設定されていません。")
        sys.exit(1)
    return (WP_USERNAME, WP_PASSWORD)


def resolve_category_id(slug: str, auth: tuple) -> int:
    """カテゴリスラッグからIDを取得する。"""
    res = requests.get(
        f"{WP_URL}/wp-json/wp/v2/categories",
        params={"slug": slug},
        auth=auth,
        timeout=15,
    )
    res.raise_for_status()
    data = res.json()
    if not data:
        print(f"エラー: カテゴリ '{slug}' が WordPress に見つかりません。")
        sys.exit(1)
    return data[0]["id"]


def post_draft(title: str, content: str, category_slug: str) -> dict:
    """記事を下書きとして投稿する。"""
    auth = get_auth()
    category_id = resolve_category_id(category_slug, auth)

    payload = {
        "title": title,
        "content": content,
        "status": "draft",  # 必ず下書き
        "categories": [category_id],
    }

    res = requests.post(
        f"{WP_URL}/wp-json/wp/v2/posts",
        json=payload,
        auth=auth,
        timeout=30,
    )
    res.raise_for_status()
    return res.json()


def main():
    parser = argparse.ArgumentParser(description="WordPress に記事を下書き投稿する")
    parser.add_argument("file", help="投稿するHTMLファイルのパス（articles/draft/ 以下）")
    parser.add_argument("--title", required=True, help="記事タイトル")
    parser.add_argument(
        "--category",
        required=True,
        choices=list(CATEGORY_SLUGS.keys()),
        help="カテゴリスラッグ",
    )
    args = parser.parse_args()

    html_path = Path(args.file)
    if not html_path.exists():
        print(f"エラー: ファイルが見つかりません: {html_path}")
        sys.exit(1)

    if "draft" not in html_path.parts:
        print("警告: articles/draft/ 以下のファイルを指定してください。")

    content = html_path.read_text(encoding="utf-8")

    print(f"投稿中: '{args.title}' → {WP_URL} （下書き）")
    result = post_draft(args.title, content, args.category)

    post_id = result.get("id")
    edit_url = f"{WP_URL}/wp-admin/post.php?post={post_id}&action=edit"
    print(f"完了: 下書き投稿成功")
    print(f"  投稿ID  : {post_id}")
    print(f"  確認URL : {edit_url}")
    print("高野氏の確認・承認後に公開してください。")


if __name__ == "__main__":
    main()
