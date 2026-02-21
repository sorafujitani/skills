# Karin. 情報源ガイド

## 情報源の優先順位と特性

### 1. WebSearch（最優先）
最新情報の取得に最も有効。以下のクエリパターンを使う:
- `"Karin." ユニバーサルミュージック [検索キーワード]`
- `"Karin." シンガーソングライター [検索キーワード]`
- `site:natalie.mu "Karin."`
- `site:universal-music.co.jp karin`
- `site:karin-official.com [検索キーワード]`

**混同注意**: 「Karin.」は一般的な名前のため、KARA（K-pop）等の別アーティストが検索結果に混入しやすい。結果のURLドメインやコンテキストで必ずフィルタリングすること。

### 2. Universal Music Japan（WebFetch可能）
- URL: `https://www.universal-music.co.jp/karin/`
- 内容: ニュース、ディスコグラフィー、プロフィール
- 特徴: 公式レーベルページ。リリース情報が正確

### 3. 音楽ナタリー（WebFetch可能）
- URL: `https://natalie.mu/music/artist/112029`
- 内容: ニュース記事一覧
- 特徴: 日本の音楽メディア。ライブ・リリース・MV公開などの速報性が高い

### 4. 公式サイト（ページ本文はWebFetch不可、sitemapは可能）
- URL: `https://www.karin-official.com/`
- 注意: Wix製サイト。JavaScriptで動的レンダリングのため通常ページのWebFetchでは内容を取得できない
- **sitemapは読み取り可能**。以下のsitemapからイベントURL・日付を抽出できる:
  - `https://www.karin-official.com/sitemap.xml` （サイトマップインデックス）
  - `https://www.karin-official.com/event-pages-sitemap.xml` （ライブイベント一覧）
  - `https://www.karin-official.com/pages-sitemap.xml` （全ページ一覧、日付ページ含む）
- URLに日付・会場名が含まれるため、sitemapだけでもライブスケジュールの概要が把握できる

### 5. SNS
- X (Twitter): `@_Karin_official`
- Instagram: プロフィールのリンクから確認可能

## アーティスト基本情報

- **名前**: Karin.（ピリオド付き）
- **生年月日**: 2001年5月30日
- **職業**: シンガーソングライター
- **所属レーベル**: ユニバーサルシグマ（UNIVERSAL MUSIC JAPAN）
- **活動開始**: 2018年楽曲制作開始、2019年6月8日デビュー発表
- **代表作**:
  - 1st Album「アイデンティティクライシス」(2019.08.07)
  - 2nd Album「solitude ability」(2021.03.10)
  - 4th Album「私達の幸せは」(2023.03.01)
- **代表曲**: 「愛だけは叫ばせて」「青春脱衣所」「君の嘘なら」「知らない言葉を愛せない」
- **公式サイト**: https://www.karin-official.com/
