---
name: karin-info
description: "シンガーソングライターKarin.の最新情報を取得・整理するスキル。Web SearchとWebFetchを使い、ニュース、リリース情報、ライブ・イベント情報、MV公開情報などを収集して構造化された形式で提示する。以下の場合に使用: (1) Karin.の最新ニュースを知りたいとき (2) Karin.の新曲・アルバムリリース情報を確認したいとき (3) Karin.のライブ・イベント情報を確認したいとき (4) Karin.のアーティスト情報を知りたいとき"
---

# Karin. 最新情報エージェント

シンガーソングライターKarin.に関する最新情報をWebから収集し、構造化して提示する。

## 情報収集ワークフロー

### Step 1: WebSearchで最新情報を検索

以下のクエリで最新情報を幅広く収集する:

```
"Karin." シンガーソングライター [年] ニュース
"Karin." 新曲 リリース [年]
"Karin." ライブ ツアー [年]
```

`[年]` には現在の年を入れる。結果のURLを次のステップで使う。

### Step 2: WebFetchで詳細情報を取得

検索結果から得たURLのうち、以下の信頼できるソースをWebFetchで読み取る:

| ソース | URL | 取得可能な情報 |
|--------|-----|----------------|
| Universal Music Japan | `https://www.universal-music.co.jp/karin/` | ニュース、ディスコグラフィー |
| 音楽ナタリー | `https://natalie.mu/music/artist/112029` | ニュース記事一覧 |

**注意**: 公式サイト `karin-official.com` はWix製で動的レンダリングのためWebFetchでは読み取れない。WebSearchで `site:karin-official.com` を使い間接的に取得する。

### Step 3: 情報を構造化して出力

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
