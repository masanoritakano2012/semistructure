# semistructure.com 記事管理リポジトリ

半導体専門サイト [semistructure.com](https://semistructure.com) への記事投稿を管理するリポジトリです。

## ディレクトリ構成

```
semistructure/
├── articles/
│   ├── draft/        # 執筆中・レビュー待ちの記事
│   └── published/    # 投稿済み記事のアーカイブ
├── scripts/          # WordPress投稿スクリプト等
├── templates/        # 記事テンプレート
├── .env.example      # 環境変数テンプレート
└── CLAUDE.md         # サブエージェント設定
```

## セットアップ

```bash
cp .env.example .env
# .env に WordPress の認証情報を設定
```

## 環境変数

| 変数名 | 説明 |
|--------|------|
| `WP_URL` | WordPress サイトURL |
| `WP_USERNAME` | WordPress ユーザー名 |
| `WP_APP_PASSWORD` | WordPress アプリケーションパスワード |

## 記事ワークフロー

1. `articles/draft/` に Markdown で記事を作成
2. レビュー・編集
3. `scripts/` のスクリプトで WordPress へ投稿
4. 投稿後、`articles/published/` へ移動
