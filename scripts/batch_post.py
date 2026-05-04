"""
複数記事を一括投稿するバッチスクリプト
使い方: python scripts/batch_post.py
articles/ready/ 内の全HTMLファイルをWordPressに下書き投稿します。
"""

import os
import sys
import subprocess
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

READY_DIR = Path("articles/ready")

def main():
    html_files = sorted(READY_DIR.glob("*.html"))

    if not html_files:
        print("❌ articles/ready/ にHTMLファイルがありません")
        return

    print(f"📦 {len(html_files)}件のファイルを投稿します")
    print()

    success = 0
    failed = 0

    for filepath in html_files:
        print(f"▶ 投稿中: {filepath.name}")
        result = subprocess.run(
            [sys.executable, "scripts/post_to_wordpress.py", "--file", str(filepath)],
            capture_output=True,
            text=True,
            encoding="utf-8"
        )
        if result.returncode == 0:
            print(result.stdout)
            success += 1
        else:
            print(f"❌ エラー: {result.stderr}")
            failed += 1
        print("─" * 50)

    print()
    print(f"✅ 完了: 成功{success}件 / 失敗{failed}件")

if __name__ == "__main__":
    main()
