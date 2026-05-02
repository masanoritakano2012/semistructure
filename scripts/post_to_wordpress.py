"""
WordPress REST API 投稿スクリプト
使い方: python scripts/post_to_wordpress.py --file articles/ready/記事名.html
"""

import os
import json
import csv
import argparse
import requests
from datetime import datetime
from pathlib import Path

# ===== 設定 =====
WP_URL = os.getenv("WP_URL", "https://semistructure.com")
WP_USERNAME = os.getenv("WP_USERNAME")
WP_PASSWORD = os.getenv("WP_PASSWORD")

# アイキャッチ画像（共通）
FEATURED_MEDIA_URL = "http://semistructure.com/wp-content/uploads/2026/05/semiconductor-news-thumbnail-template.jpg"
FEATURED_MEDIA_ID = 100  # WordPressのメディアID

# カテゴリIDマッピング（WordPress管理画面で確認して更新）
CATEGORY_MAP = {
    "半導体ニュース": 4,
    "AI×半導体": 5,
    "半導体企業分析": 3,
    "半導体とは": 2,
    "半導体キャリア": 6,
    "メモリニュース": None,
    "製造装置ニュース": None,
    "AI半導体ニュース": None,
    "ファウンドリニュース": None,
    "日本企業ニュース": None,
    "半導体材料ニュース": None,
    "企業ニュース": None,
}

LOGS_DIR = Path("logs")
POSTED_URLS_FILE = LOGS_DIR / "posted_urls.json"
WP_POSTS_CSV = LOGS_DIR / "wordpress_posts.csv"

def load_posted_urls():
    with open(POSTED_URLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return set(data.get("posted_urls", []))

def save_posted_url(url):
    with open(POSTED_URLS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["posted_urls"].append(url)
    with open(POSTED_URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def log_to_csv(date, title, slug, category, status, wp_url, source_file):
    with open(WP_POSTS_CSV, "a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([date, title, slug, category, status, wp_url, source_file])

def read_article(filepath):
    """HTMLファイルから記事情報を読み込む"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # 1行目からメタ情報を取得（コメント形式）
    # 例: <!-- title: タイトル | slug: my-slug | category: メモリニュース -->
    meta = {}
    if content.startswith("<!--"):
        meta_line = content.split("-->")[0].replace("<!--", "").strip()
        for item in meta_line.split("|"):
            if ":" in item:
                key, val = item.split(":", 1)
                meta[key.strip()] = val.strip()
        # メタ情報の後のHTMLを本文とする
        body = content.split("-->", 1)[1].strip()
    else:
        body = content

    return meta, body

def post_to_wordpress(title, slug, content, category_name, status="draft"):
    """WordPressに記事を投稿する"""
    api_url = f"{WP_URL}/wp-json/wp/v2/posts"

    category_id = CATEGORY_MAP.get(category_name)
    categories = [category_id] if category_id else []

    payload = {
        "title": title,
        "slug": slug,
        "content": content,
        "status": status,  # 必ずdraft
        "categories": categories,
        "featured_media": FEATURED_MEDIA_ID,
    }

    response = requests.post(
        api_url,
        json=payload,
        auth=(WP_USERNAME, WP_PASSWORD),
        headers={"Content-Type": "application/json"},
    )

    if response.status_code in [200, 201]:
        post_data = response.json()
        return True, post_data.get("link", ""), post_data.get("id", "")
    else:
        return False, response.text, None

def move_to_posted(filepath):
    """記事ファイルをposted/フォルダに移動"""
    src = Path(filepath)
    dst = Path("articles/posted") / src.name
    src.rename(dst)
    print(f"✅ 移動完了: {dst}")

def main():
    parser = argparse.ArgumentParser(description="WordPressに記事を投稿する")
    parser.add_argument("--file", required=True, help="投稿する記事ファイル（articles/ready/内）")
    parser.add_argument("--status", default="draft", help="投稿ステータス（draft推奨）")
    args = parser.parse_args()

    filepath = args.file

    if not Path(filepath).exists():
        print(f"❌ ファイルが見つかりません: {filepath}")
        return

    # 記事読み込み
    meta, content = read_article(filepath)

    title = meta.get("title", "タイトル未設定")
    slug = meta.get("slug", Path(filepath).stem)
    category = meta.get("category", "半導体ニュース")

    print(f"📄 投稿準備中...")
    print(f"   タイトル：{title}")
    print(f"   スラッグ：{slug}")
    print(f"   カテゴリ：{category}")
    print(f"   ステータス：{args.status}")
    print()

    # 投稿
    success, wp_url, post_id = post_to_wordpress(
        title=title,
        slug=slug,
        content=content,
        category_name=category,
        status=args.status,
    )

    if success:
        print(f"✅ 投稿成功！")
        print(f"   WordPress URL: {wp_url}")
        print(f"   Post ID: {post_id}")

        # ログ記録
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        log_to_csv(now, title, slug, category, args.status, wp_url, filepath)
        save_posted_url(wp_url)

        # ファイル移動
        move_to_posted(filepath)

    else:
        print(f"❌ 投稿失敗")
        print(f"   エラー: {wp_url}")

if __name__ == "__main__":
    main()
