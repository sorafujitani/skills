# Phase 1: Context Collection — Subagent Prompts & Schema

## Explore Agent 起動仕様

3つの `Task(Explore)` を **並列** に起動する。各agentは独立（他の結果を知らない）。

### Agent A: Architecture Mapping

**プロンプトテンプレート**:
```
対象リポジトリのアーキテクチャを調査せよ。

調査項目:
1. ディレクトリ構成からモジュール境界を特定
2. 主要モジュール間の依存方向を把握（import/require文を追跡）
3. 既存のアーキテクチャパターンを特定（Layered/Hexagonal/Event-driven/MVC等）
4. 以下の要件に関連するエントリポイントを特定: {requirements}

出力は以下のYAMLスキーマに従うこと:
{schema_a}
```

**出力スキーマ**:
```yaml
architecture:
  modules:
    - path: str           # e.g., "src/domain/user"
      responsibility: str # single sentence
      public_api: [str]   # exported functions/classes
  dep_graph: str          # mermaid graph TD format
  arch_pattern: str       # Layered|Hexagonal|Event-driven|MVC|Monolith|Microservice
  entry_points: [str]     # files relevant to requirements
```

### Agent B: Pattern Inventory

**プロンプトテンプレート**:
```
対象リポジトリの設計パターンとコーディング規約を調査せよ。

調査項目:
1. 使用されているデザインパターン（Repository, Factory, Strategy, Observer等）を特定し、具体的なファイルパスを記録
2. コーディング規約を推定（命名規則、ファイル構成、import順序等）
3. エラー処理の方針を把握
4. テストの書き方（フレームワーク、スタイル、カバレッジ設定）
5. 依存注入(DI)のアプローチ

出力は以下のYAMLスキーマに従うこと:
{schema_b}
```

**出力スキーマ**:
```yaml
patterns:
  design_patterns:
    - name: str       # pattern name
      location: str   # file path
      usage: str      # how it's used
  conventions:
    - rule: str       # e.g., "camelCase for functions"
      evidence: str   # file path or config file
  error_handling: str # description of approach
  test_patterns:
    framework: str    # e.g., "Jest", "pytest"
    style: str        # e.g., "AAA", "BDD", "table-driven"
    coverage_config: str
  di: str             # e.g., "constructor injection", "container-based"
```

### Agent C: Tech Stack Analysis

**プロンプトテンプレート**:
```
対象リポジトリの技術スタックを調査せよ。

調査項目:
1. 言語とランタイムバージョン（package.json, go.mod, Cargo.toml等から）
2. フレームワークとそのバージョン
3. 主要な依存関係とその用途
4. ビルドツール、テストランナー、リンター
5. CI/CD設定

出力は以下のYAMLスキーマに従うこと:
{schema_c}
```

**出力スキーマ**:
```yaml
tech_stack:
  lang: str              # e.g., "TypeScript"
  runtime_ver: str       # e.g., "Node.js 20.x"
  framework: str         # e.g., "NestJS"
  framework_ver: str     # e.g., "10.x"
  deps:
    - name: str
      ver: str
      purpose: str
  build: str             # e.g., "tsc + esbuild"
  test_runner: str       # e.g., "Jest"
  lint: str              # e.g., "ESLint + Prettier"
  ci: str                # e.g., "GitHub Actions"
```

## 要件構造化テンプレート

```yaml
requirements:
  functional:
    - id: FR-{N}
      description: str
      priority: must|should|could
  non_functional:
    - id: NFR-{N}
      description: str
      category: performance|security|reliability|maintainability
  constraints:
    - id: C-{N}
      description: str
  scope:
    in: [str]
    out: [str]
```

## 粒度判定ロジック

```
files_changed ≤5 AND components ≤2  → PR granularity
files_changed >5 OR components >2   → epic granularity
user_override                       → always honored
```

components = Phase 1 Agent A の modules で、entry_points が属するモジュール数。
