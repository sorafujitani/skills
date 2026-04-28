# 言語・フレームワーク検出と動的参照戦略

## Phase 1 で検出するファイル

### 言語検出

| 言語 | 検出ファイル | Glob パターン |
|------|-----------|--------------|
| TypeScript | `tsconfig.json`, `tsconfig.*.json` | `**/tsconfig*.json` |
| Go | `go.mod`, `go.sum` | `go.mod` |
| Python | `pyproject.toml`, `setup.py`, `requirements.txt` | `pyproject.toml` |
| Rust | `Cargo.toml` | `Cargo.toml` |

### フレームワーク検出

| フレームワーク | 検出方法 |
|--------------|---------|
| Prisma | `schema.prisma` の存在 |
| GraphQL | `*.graphql`, `*.gql` ファイル、または `graphql` 依存 |
| Next.js | `next.config.*` の存在 |
| Express | `package.json` 内の `express` 依存 |
| Fastify | `package.json` 内の `fastify` 依存 |
| gin | `go.mod` 内の `github.com/gin-gonic/gin` |
| echo | `go.mod` 内の `github.com/labstack/echo` |

### Linter/Formatter 設定

| ツール | 検出ファイル |
|--------|-----------|
| ESLint | `eslint.config.*`, `.eslintrc.*` |
| Prettier | `.prettierrc*`, `prettier.config.*` |
| golangci-lint | `.golangci.yml`, `.golangci.yaml` |
| rustfmt | `rustfmt.toml` |

## 動的参照戦略

言語固有の観点は自前で定義せず、以下の外部リソースを `WebSearch` で動的に取得する。

### TypeScript

| 参照先 | 検索クエリ例 | 用途 |
|--------|------------|------|
| TypeScript Handbook | `site:typescriptlang.org {specific topic}` | 型システムの正確な仕様確認 |
| ESLint Rules | `site:eslint.org rules {rule-name}` | ルールの意図と正しい適用 |
| typescript-eslint | `site:typescript-eslint.io rules {rule-name}` | TS固有ルールの確認 |

### Go

| 参照先 | 検索クエリ例 | 用途 |
|--------|------------|------|
| Go Code Review Comments | `go code review comments wiki` | 公式レビューガイドライン |
| Effective Go | `site:go.dev doc effective_go` | 慣用的な書き方の確認 |
| Go Blog | `site:go.dev blog {topic}` | 公式推奨パターン |

### フレームワーク固有

| 参照先 | 検索クエリ例 |
|--------|------------|
| Prisma Docs | `site:prisma.io docs {topic}` |
| Next.js Docs | `site:nextjs.org docs {topic}` |
| GraphQL Best Practices | `site:graphql.org learn best-practices` |

## 検出結果の活用

1. 検出された言語・フレームワークを Agent D のプロンプトに含める
2. プロジェクトの linter 設定を Agent D に渡し、設定に準拠したレビューを実施
3. 指摘に関連する公式ドキュメントのURLを `WebSearch` → `WebFetch` で取得し、教育的リファレンスとして出力に含める
