# arXiv-db

1. arXiv から最新の論文を取得
2. LLM を用いて概要を要約
3. Notion のデータベースに格納

## 利用方法

`src/app.py` を実行しておくと、午前9時~10時ごろに Notion に論文データが格納され、Slack に更新通知が来る。

## 設定項目

### 環境変数

- `ARXIV_DATABASE_ID`: Notion で利用する DB の ID (URLの'/{DATABASE_ID}?v='部分)
- `NOTION_TOKEN`: Notion API を利用するためのトークン
- `OPENAI_APIKEY`: OpenAI の ChatGPT API を利用するための環境変数
- `SLACK_API_TOKEN`: Slack SDK を用いるためのトークン

### Notionの設定

- DB を用意し、カラムを追加
  - Interest: Select
  - Title: Title
  - LLM-summary: Text
  - Catgories: Multi Select
  - Authors: Text
  - Abstract: Text
  - Comments: Text
  - Submission Date: Date
  - arXiv-ID: Text
- DB を用意したページにコネクトを設定
  - https://www.notion.so/help/add-and-manage-connections-with-the-api

### Slackの設定

Slack app を作成し、通知投稿用のチャンネルと連携を済ませておく。
チャンネル名は現状`app.py`にハードコードされている。

### OpenAI APIの設定

API Key を発行して入金する。
