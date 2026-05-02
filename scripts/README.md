# スクリプト一覧

## post_to_wordpress.py
WordPressに記事を投稿するスクリプト

### 使い方
1. .envファイルに認証情報を設定
2. 記事をarticles/ready/に配置
3. 以下を実行

```
python scripts/post_to_wordpress.py --file articles/ready/記事名.html
```

### 記事ファイルの形式
HTMLファイルの先頭に以下のメタ情報を記載してください

```html
<!-- title: 記事タイトル | slug: my-slug | category: メモリニュース -->
<p>記事本文...</p>
```

### 環境変数（.envファイル）
```
WP_URL=https://semistructure.com
WP_USERNAME=WordPressユーザー名
WP_PASSWORD=アプリケーションパスワード
```
