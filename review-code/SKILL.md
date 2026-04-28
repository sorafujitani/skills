---
name: review-code
description: |
  PRベースの多角的コードレビューを実行する。
  4つの独立subagentが並列にレビューし、指摘箇所のコード実在確認・
  WebSearchによる公式ドキュメント裏取りでハルシネーションを防止する。
  各指摘に前提知識・公式リファレンスURLを付与し教育的なレビューを提供する。
  言語・フレームワークを自動検出し、プロジェクト設定+公式ガイドラインに基づくレビューを実施。
  以下の場合に使用:
  (1) PRのコードレビューを依頼されたとき
  (2) git diffに対するコードレビュー
  (3) マージ前の品質チェック
  (4) コードの改善提案が欲しいとき
disable-model-invocation: true
argument-hint: "[PR-url, branch-name, or empty for current branch]"
---

# Code Review: 多角的PRレビュー

## 核心原則

- **教育的レビュー**: 指摘ごとに「なぜ問題か」の理由と、理解に必要な前提知識・公式ドキュメントURLを提示する
- **証拠ベース**: すべての指摘は `file:line` で特定し、`Read` でコード実在を確認済みであること
- **ハルシネーション防止**: API仕様・言語仕様に言及する場合は `WebSearch` で公式ドキュメントを裏取りする
- **コード変更禁止**: レビューのみ。修正は行わない

## 入力処理

`$ARGUMENTS` の内容に応じて:

1. **GitHub PR URL**: `Task(ctx:github)` でPR情報を取得（diff, comments, files, body）
2. **ブランチ名**: `git diff main...{branch}` で差分取得
3. **引数なし**: 現在のブランチの `git diff main...HEAD` を使用

## Phase 1: Context Collection（コンテキスト収集）

**目的**: レビュー対象の差分取得 + プロジェクトの言語・フレームワーク・lint設定を把握

**Step 1: 差分取得**
- PR URL → `Task(ctx:github)` で構造化情報取得
- ブランチ → `git diff` で差分取得
- 変更ファイル一覧と変更行数を把握

**Step 2: 言語・フレームワーク自動検出**
- [lang-detection.md](references/lang-detection.md) に従い、設定ファイルを `Glob` → `Read` で検出
- 検出結果: 言語、フレームワーク、linter設定

**Step 3: 公式レビューガイドラインの取得**
- [lang-detection.md](references/lang-detection.md) の「動的参照戦略」に記載された `site:` 付き検索クエリを使用する
- 必ず公式サイトに限定した検索を行う（例: `site:typescriptlang.org`, `site:go.dev`）
- 検索クエリには現在の年（`$CURRENT_YEAR`）を含めて最新ドキュメントを優先する
- `WebFetch` で公式ドキュメントページの詳細を取得し、Phase 2 の Agent D に渡す
- ブログ記事やサードパーティの解説ではなく、言語・フレームワーク公式ドキュメントのみを信頼する

**Phase 1 出力**: 差分サマリー、検出言語/FW、lint設定、取得した公式ガイドライン

## Phase 2: Multi-perspective Review（多角的レビュー）

**目的**: 4つの独立subagentが異なる観点から並列にレビューする

`Task(Explore)` を最大4並列で起動。各agentは他のagentの結果を知らない。

各agentに渡す情報:
- 差分（git diff 出力）
- 変更ファイルの全体コンテキスト（`Read` で変更関数の前後を含む）
- Phase 1 で検出した言語・FW情報

**Agent A: Correctness** — ロジックの正確性、エラーハンドリング、要件一致
**Agent B: Security & Performance** — セキュリティ脆弱性、パフォーマンス問題
**Agent C: Design & Maintainability** — 設計品質、可読性、テスト網羅性
**Agent D: Language-specific** — 言語固有の観点（公式ガイドライン + プロジェクトlint設定ベース）

各agentの出力スキーマ: [review-dimensions.md](references/review-dimensions.md) を参照

## Phase 3: Synthesis & Verification（統合・検証）

**目的**: 指摘の品質保証と教育的レポートの生成

**Step 1: 統合と重複排除**
- 4 agentの指摘を統合
- 同一箇所への重複指摘をマージ（重大度は高い方を採用）

**Step 2: ハルシネーション防止チェック**
- 全指摘の `file:line` を `Read` で再確認
- API仕様や言語仕様への言及を `WebSearch` で裏取り（`site:` 付きで公式ドキュメントに限定）

**Step 3: 教育的リファレンスの付与**
各指摘に対して:
1. **前提知識**: この指摘を理解するために必要な概念を簡潔に説明
2. **公式リファレンス**: `WebSearch` で該当する公式ドキュメントのURLを取得し付与
3. **学習ポイント**: この指摘から学べること、同様の問題を今後防ぐ方法

**Step 4: 重大度スコアリング**
- [severity-scoring.md](references/severity-scoring.md) に従い分類
- マージ判定（LGTM / 要修正 / 要検討）

## 出力フォーマット

```markdown
## PR レビューサマリー

**対象**: {PR タイトル / ブランチ名}
**言語**: {検出された言語・フレームワーク}
**変更規模**: {ファイル数}ファイル, +{追加行} -{削除行}

## 強み
- {具体的に良い点} — `file:line`

## 課題

### 🚨 Critical（修正必須）

#### {問題タイトル}
- **箇所**: `file:line`
- **コード**: `引用`
- **問題**: {なぜ問題か}
- **改善案**: {具体的な修正方法}
- **前提知識**: {理解に必要な概念の簡潔な説明}
- **リファレンス**: [{ドキュメント名}]({URL}) — {該当セクション}

### ⚠️ Important（修正推奨）
{同一形式}

### 💡 Minor（提案）
{同一形式}

## 学習リソース
- [{概念名}]({公式ドキュメントURL}) — {この PR で特に関連する箇所}

## 評価
{マージ可否と理由（1-2文）}
```

## エラーハンドリング

| 状況 | 対応 |
|------|------|
| PR URLが無効 | 再入力を求める、またはブランチ名にフォールバック |
| 差分が巨大（1000行超） | 変更ファイルを重要度で優先順位付けし、上位を集中レビュー |
| 言語検出失敗 | Agent D をスキップし、Agent A-C の3並列で実行 |
| WebSearch で公式ドキュメントが見つからない | リファレンスなしで指摘を出力（「公式ドキュメント未確認」と明記） |
