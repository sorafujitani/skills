# レビュー観点定義

## 概要

4つの独立したsubagentが並列にレビューする。各agentは他のagentの結果を知らない。

## Agent A: Correctness（正確性）

### 観点
- ロジックの正確性（条件分岐、境界値、オフバイワン）
- エラーハンドリング（例外伝播、リカバリ、ユーザーへのフィードバック）
- 要件との一致（PRの目的に対して過不足なく実装されているか）
- スコープクリープ（PR目的外の変更が混入していないか）
- 破壊的変更（後方互換性への影響）

### 出力スキーマ
```yaml
findings:
  - location: "file:line"
    category: correctness
    severity: critical / important / minor
    issue: "問題の説明"
    evidence: "コードの具体的な引用"
    suggestion: "改善案"
    prerequisite: "理解に必要な前提知識（あれば）"
```

## Agent B: Security & Performance

### セキュリティ観点
- 入力値検証の完全性（バリデーション、サニタイズ）
- 認証・認可の適切性
- インジェクション対策（SQL, XSS, コマンド）
- センシティブ情報の露出（ログ、エラーメッセージ、レスポンス）
- 依存ライブラリの既知脆弱性

### パフォーマンス観点
- N+1クエリ
- 不要なデータ取得・過剰なメモリ使用
- 並列化可能な直列処理
- キャッシュの活用
- 計算量（O記法での評価）

### 出力スキーマ
Agent A と同一形式。category は `security` または `performance`。

## Agent C: Design & Maintainability

### 設計観点
- 関心の分離（単一責任原則）
- DRY原則（重複ロジックの抽出）
- 命名の明確性と一貫性
- 関数の粒度（長すぎる関数、深いネスト）
- テストの網羅性（追加・更新の必要性、エッジケース）

### API設計（API変更がある場合）
- RESTful原則 / GraphQLスキーマ設計
- レスポンスフォーマットの一貫性
- ステータスコードの適切性
- APIバージョニング

### 出力スキーマ
Agent A と同一形式。category は `design` または `testing`。

## Agent D: Language-specific（言語固有）

Phase 1 で検出した言語・フレームワークに応じて観点を動的に構成する。

### 動的構成の手順

1. Phase 1 で検出した言語設定ファイルを Read（tsconfig.json, .golangci.yml 等）
2. `WebSearch` でその言語の公式レビューガイドラインを取得:
   - TypeScript: "TypeScript best practices code review" / ESLint recommended rules
   - Go: "Go Code Review Comments" / "Effective Go"
3. プロジェクト固有の設定（strict mode, linter rules）と公式ガイドラインを照合
4. 差分に対して言語固有の観点でレビュー

### TypeScript で典型的に検出すべき観点（参考）
- 型安全性: `any` 使用、型アサーション、union型の網羅チェック
- 非同期処理: floating promise、unhandled rejection
- Prisma/ORM: トランザクション管理、排他ロック、スキーマ整合性
- GraphQL: DataLoader活用、N+1 resolver

### Go で典型的に検出すべき観点（参考）
- エラーハンドリング: `err != nil` パターン、エラーラッピング
- goroutine/channel: リーク、競合状態
- インターフェース設計: 最小インターフェース原則
- context: キャンセル・タイムアウトの伝播

### 出力スキーマ
Agent A と同一形式。category は `language-specific`。

## フレームワーク固有の追加観点

Phase 1 で検出されたフレームワークに応じて Agent D に追加する:

| フレームワーク | 追加観点 |
|--------------|---------|
| Prisma | `@map` 使用、リレーション命名、マイグレーション整合性 |
| GraphQL | DataLoader、resolver N+1、スキーマ設計 |
| Next.js | Server/Client Component分離、データフェッチ戦略 |
| Express/Fastify | ミドルウェア順序、エラーミドルウェア |
| gin/echo (Go) | ミドルウェアチェーン、バインディングバリデーション |
