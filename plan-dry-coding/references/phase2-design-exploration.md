# Phase 2: Design Exploration — Plan Agent Prompts & Comparison

## Plan Agent 起動仕様

2-3の `Task(Plan)` を **並列** に起動。各agentに異なる設計制約（bias）を付与。

### 設計制約プロファイル

| Profile | 主眼 | 副次 |
|---------|------|------|
| testability-first | DI可能性、pure function化、テストseam | 変更容易性 |
| minimal-change | 既存パターン準拠、変更ファイル最小化 | パフォーマンス |
| extensibility-first | OCP、拡張ポイント設計、プラグイン化 | テスタビリティ |

### プロンプトテンプレート

```
以下の要件に対するシステム設計アプローチを提案せよ。
設計制約: {profile_name} — {profile主眼}を最優先とする。

## Context
{Phase 1 context_summary をここに埋め込む}

## Requirements
{structured requirements}

## 制約
- 既存コードベースのパターンに可能な限り従うこと
- 新規外部依存は最小限にすること
- 各設計判断にWHY（なぜその選択か）を付与すること

出力は以下のYAMLスキーマに従うこと:
{approach_schema}
```

### 出力スキーマ（Schema Contract）

```yaml
approach:
  name: str                    # e.g., "Strategy Pattern + DI"
  overview: str                # 2-3 sentences
  components:
    - name: str
      responsibility: str     # single responsibility
      interface: str          # key signatures in target language
      deps: [str]             # what it depends on
  data_flow:
    happy: str                # sequence description
    error: str                # error propagation path
  files_changed: [str]        # existing files to modify
  files_new: [str]            # new files to create
  new_deps: [str]             # new external dependencies
  pattern: str                # design pattern name
  pattern_why: str            # why this pattern fits
  prereqs:
    - concept: str            # e.g., "Strategy Pattern"
      url: str                # official doc or reference URL
      relevance: str          # why user should know this
```

## 収束防止メカニズム

全アプローチが同一パターンに収束した場合:

1. 最も異なるアプローチを強制生成する追加 `Task(Plan)` を起動
2. 追加agentのプロンプトに「他のagentが{pattern}を提案済み。それ以外のアプローチを提案せよ」と明記
3. 「アプローチが収束した理由」自体を Design Decision として記録

## 比較表テンプレート

```markdown
## アプローチ比較

| 観点 | A: {name} | B: {name} | C: {name} |
|------|-----------|-----------|-----------|
| 変更ファイル数 | {N} | {N} | {N} |
| 新規依存 | {list} | {list} | {list} |
| テスト容易性 | {D1 score}/5 | /5 | /5 |
| 変更容易性 | {D2}/5 | /5 | /5 |
| パターン適合 | {D3}/5 | /5 | /5 |
| 言語適合 | {D4}/5 | /5 | /5 |
| 依存管理 | {D5}/5 | /5 | /5 |
| エラー戦略 | {D6}/5 | /5 | /5 |
| 性能 | {D7}/5 | /5 | /5 |
| **合計** | **/35** | **/35** | **/35** |

## 推奨

**推奨アプローチ**: {name}

**根拠**:
1. {reason}: {evidence from codebase}
2. {reason}: {evidence}

**リスク**:
- {risk} → 対策: {mitigation}
```

## WebSearch クエリパターン

設計判断の裏付けに使用:

```
"{framework} {pattern} best practice"
"{language} {concept} official documentation"
"{library} migration guide {version}"
"github {similar-project} architecture"
```
