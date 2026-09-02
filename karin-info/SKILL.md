---
name: karin-info
description: "シンガーソングライター Karin.（ピリオド付き）のニュース・リリース・ライブ・プロフィールを Web Search と WebFetch で収集して整理する。Karin. に関する情報を求められたときに使う。"
---

# Karin. 最新情報エージェント

## アーティスト識別情報

- 名前: Karin.（ピリオド付き、読み: かりん）
- 職業: シンガーソングライター
- 生年月日: 2001年5月30日
- 所属レーベル: ユニバーサルシグマ（UNIVERSAL MUSIC JAPAN）
- 公式サイト: https://www.karin-official.com/
- X: @_Karin_official

> **混同禁止**: 以下は全て別人。検索結果に含まれたら必ず除外すること。
> - KARA（K-popグループ）
> - 花凛、華凛、かりん（同音異名の別人）
> - アニメ・ゲームキャラクター

## ワークフロー

以下の Step 1〜3 を**並列実行**し、Step 4 で統合する。

### Step 1: WebSearch

`[YEAR]` は現在の年に置換する。クエリは目的に応じて選択:

| 目的 | クエリ |
|------|--------|
| 総合ニュース | `"Karin." ユニバーサルミュージック [YEAR]` |
| リリース | `"Karin." シンガーソングライター 新曲 [YEAR]` |
| ライブ | `"Karin." シンガーソングライター ライブ [YEAR]` |
| ナタリー記事 | `site:natalie.mu "Karin."` |
| レーベル | `site:universal-music.co.jp karin` |

**結果の判別ルール:**
- ACCEPT: ドメインが `karin-official.com`, `universal-music.co.jp`, `natalie.mu` のもの
- ACCEPT: 文脈が「シンガーソングライター」「ユニバーサルミュージック」に合致するもの
- REJECT: K-pop、韓国、アニメ関連の結果

### Step 2: 公式サイト sitemap（WebFetch）

公式サイトはWix製。通常ページはJSレンダリングのためWebFetchで読めないが、**sitemapは読める**。

以下の2つを WebFetch で取得:

```
https://www.karin-official.com/event-pages-sitemap.xml
https://www.karin-official.com/pages-sitemap.xml
```

**URLからの情報抽出ルール:**

| URLパターン | 含まれる情報 | 例 |
|-------------|-------------|-----|
| `/event-details/YYYY-MM-DD-venue` | ライブ日程 + 会場名 | `/event-details/2025-10-25-shimokitazawalaguna` |
| `/YYYY-MM-DD` | ニュースまたはライブ告知の日付 | `/2026-02-28` |
| `/ツアー`, `/ワンマン` 等 | ツアー・ワンマン情報ページ | `/2025-ワンマン` |

`lastmod` フィールドで更新日も確認できる。

### Step 3: 外部メディア（WebFetch）

| ソース | URL | 内容 |
|--------|-----|------|
| Universal Music Japan | `https://www.universal-music.co.jp/karin/` | ニュース、ディスコグラフィー |
| 音楽ナタリー | `https://natalie.mu/music/artist/112029` | ニュース記事一覧 |

### Step 4: 出力

収集した情報を以下のフォーマットで統合して出力する。
情報が見つからないセクションは省略する。

```markdown
## Karin. 最新情報（[YYYY-MM-DD]取得）

### ニュース
- [YYYY-MM-DD] タイトル（ソース名）

### リリース情報
- [YYYY-MM-DD] タイトル / 種別（シングル/アルバム/EP）

### ライブ・イベント
- [YYYY-MM-DD] イベント名 / 会場

### 関連リンク
- 公式サイト: https://www.karin-official.com/
- X: https://x.com/_Karin_official
- Universal Music: https://www.universal-music.co.jp/karin/
```

