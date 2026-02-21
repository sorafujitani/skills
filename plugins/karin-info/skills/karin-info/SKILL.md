---
name: karin-info
description: "シンガーソングライターKarin.の最新情報を取得・整理するスキル。Web SearchとWebFetchを使い、ニュース、リリース情報、ライブ・イベント情報、MV公開情報などを収集して構造化された形式で提示する。以下の場合に使用: (1) Karin.の最新ニュースを知りたいとき (2) Karin.の新曲・アルバムリリース情報を確認したいとき (3) Karin.のライブ・イベント情報を確認したいとき (4) Karin.のアーティスト情報を知りたいとき"
---

# Karin. 最新情報エージェント

シンガーソングライターKarin.（かりん、2001年生まれ、ユニバーサルシグマ所属）に関する最新情報をWebから収集し、構造化して提示する。

**重要: 同名・類似名アーティストとの混同に注意**
- KARA（K-popグループ）は別アーティスト
- 花凛、華凛、かりん等の同音異名も別人
- 検索結果にこれらが含まれる場合は必ず除外すること

## 情報収集ワークフロー

### Step 1: WebSearchで最新情報を検索

以下のクエリで最新情報を幅広く収集する。`[年]` には現在の年を入れる:

```
"Karin." ユニバーサルミュージック [年]
"Karin." シンガーソングライター 新曲 [年]
"Karin." シンガーソングライター ライブ [年]
site:natalie.mu "Karin."
site:universal-music.co.jp karin
```

検索結果の判別ポイント:
- **正しい結果**: ユニバーサルミュージック、karin-official.com、音楽ナタリーのKarin.ページ
- **除外すべき結果**: K-pop関連、韓国アーティスト、アニメキャラクター

結果のURLを次のステップで使う。

### Step 2: 公式サイトのsitemapからイベント情報を取得

公式サイト `karin-official.com` はWix製で動的レンダリングのため通常ページのWebFetchでは読み取れない。
ただし **sitemapはWebFetchで読み取れる** ため、以下の手順でイベント情報を取得する:

1. `https://www.karin-official.com/event-pages-sitemap.xml` をWebFetchで取得
   - ライブイベントのURLと最終更新日が取得できる
   - URLに日付・会場名が含まれる（例: `2025-10-25-shimokitazawalaguna`）
2. `https://www.karin-official.com/pages-sitemap.xml` をWebFetchで取得
   - ニュース・ライブ個別ページのURL一覧が取得できる
   - 日付ページ（例: `2026-02-28`）から直近のイベント日程を把握できる

**URLからの情報抽出パターン:**
- `/event-details/YYYY-MM-DD-会場名` → ライブ日程・会場
- `/YYYY-MM-DD` → ニュースまたはライブ告知の日付

### Step 3: WebFetchで詳細情報を補完

以下の信頼できるソースをWebFetchで読み取り、sitemapで得た情報を補完する:

| ソース | URL | 取得可能な情報 |
|--------|-----|----------------|
| Universal Music Japan | `https://www.universal-music.co.jp/karin/` | ニュース、ディスコグラフィー |
| 音楽ナタリー | `https://natalie.mu/music/artist/112029` | ニュース記事一覧 |

### Step 4: 情報を構造化して出力

収集した情報を以下の形式で整理して提示する:

```markdown
## Karin. 最新情報 ([取得日])

### ニュース
- [日付] タイトル（ソース名）

### リリース情報
- [リリース日] タイトル / 種別（シングル/アルバム/EP）

### ライブ・イベント
- [日程] イベント名 / 会場

### 関連リンク
- 公式サイト: https://www.karin-official.com/
- X (Twitter): @_Karin_official
- Universal Music: https://www.universal-music.co.jp/karin/
```

情報が見つからないセクションは省略する。

## リファレンス

- 情報源の詳細と基本プロフィール: [references/sources.md](references/sources.md)
