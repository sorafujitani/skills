---
name: dry-coding
description: "PR〜エピック単位のシステム設計 + dry-coding。要件→多角的評価→設計ドキュメント。plan mode wrapper。必要な場合だけExplore/Plan subagentを使い、Schema Contractに従う。コード変更は行わず、設計ドキュメントとレビュー可能な実装コードを会話内で出力。(1)新機能設計 (2)リファクタ設計 (3)PR前設計レビュー (4)アーキ判断文書化 (5)アプローチ比較 (6)エピック段階計画 (7)実装コードのdry提示"
allowed-tools: Bash, Read, Glob, Grep, WebSearch, WebFetch
argument-hint: "[requirements | issue-url | description]"
---

# System Design + Dry Coding

plan mode前提。コード変更禁止。設計ドキュメントと実装コードを読み取り専用で出力し、成果物は会話内のsession stateとして保持する。ファイル保存はユーザーが明示的に求めた場合のみ行う。

## 原則

```
P1: read-only — ファイル編集なし。Read/Grep/Bash(読取のみ)
P2: evidence-based — コードベースの実態を引用。理想論でなく既存パターンとの整合
P3: WHY-driven — 各設計判断に根拠を付与
P4: schema-contracted — subagent出力はスキーマ定義に従う。ドリフト防止
P5: educational — 前提知識・公式ドキュメントリンク・パターンリファレンスを提供
P6: sequential + gates — フェーズ順守。各フェーズ完了後にユーザーOKを待つ
```

## 入力処理

`$ARGUMENTS` に応じて処理:

1. **GitHub URL** → `gh issue view` / `gh pr view --json`（`ctx:github` エージェントが登録されていればそれでもよい） でIssue/PR情報取得
2. **テキスト** → 要件として使用
3. **空** → ユーザーに要件を求める

## フェーズ進捗

```
Progress:
- [ ] Phase 1: Context Collection（要件理解 + コードベース調査）
- [ ] Phase 2: Design Exploration（設計探索 + アプローチ比較 + 7次元評価）
- [ ] Phase 3: Design Synthesis + Dry Coding（設計ドキュメント + 実装コード生成）
```

## 確認ゲートプロトコル

各フェーズ完了時:

1. 成果物を提示
2. 進捗チェックリストを更新表示
3. ユーザー応答を待つ: OK→次へ / 質問→回答後再確認 / 戻って→再調査 / 中断→現時点の成果出力

## Phase 1: Context Collection

**目的**: 要件構造化 + コードベース現状把握 + 粒度判定

**Step 1**: 入力処理（上記参照）

**Step 2**: 粒度と調整コストを見て調査方法を選ぶ。

- 小規模な依頼や、親の直接調査で必要な情報が揃う場合は、subagentを使わず直接調査する。
- 独立した成果物や競合する仮説があり、調整コストを上回る場合だけ、必要な観点の `Task(Explore)` を並列起動する。固定数を必須にしない。
- 起動する場合は、以下の候補から必要なものだけ選び、各agentを独立して調査させる。

| Agent | 調査対象 | 出力キー |
| ------- | --------- | --------- |
| A: Architecture Mapping | モジュール構造、依存グラフ、アーキパターン | `architecture` |
| B: Pattern Inventory | デザインパターン、規約、エラー処理、テスト、DI | `patterns` |
| C: Tech Stack Analysis | 言語、FW、依存、ビルド、テスト、lint、CI | `tech_stack` |

各agentの出力スキーマとプロンプト: [phase1-context-collection.md](references/phase1-context-collection.md)

**Step 3**: `WebSearch` で関連公式ドキュメント収集

**Step 4**: 粒度判定

- files_changed ≤5 AND components ≤2 → **PR**
- else → **epic**
- ユーザー指定は常に優先

**出力**: context_summary + granularity判定

**確認ゲート**: サマリー提示 → ユーザーOK（粒度修正も受付）

## Phase 2: Design Exploration

**目的**: 複数アプローチ生成 → 7次元評価 → 比較 → 推奨

**Step 1**: 独立した比較成果物が必要で、調整コストを上回る場合だけ `Task(Plan)` を必要な数だけ並列起動する。小規模な依頼は直接比較し、固定数を必須にしない。

- A: testability-first
- B: minimal-change
- C: extensibility-first

各agentの出力スキーマとプロンプト: [phase2-design-exploration.md](references/phase2-design-exploration.md)

**Step 2**: 7次元評価 — [evaluation-framework.md](references/evaluation-framework.md) のルーブリック適用

7次元（Testability / Changeability / Pattern Appropriateness / Language-Runtime Fit / Dependency Management / Error Handling / Performance）を根拠付きで比較し、弱い次元と再設計の要否を文章で結論する。点数化は補助であり必須ではない。

**Step 3**: 比較表 + 推奨アプローチ + リスク評価

**出力**: approaches[] + scores + tradeoff_table + recommendation

**確認ゲート**: 比較表提示 → ユーザーがアプローチ選択

## Phase 3: Design Synthesis + Dry Coding

**目的**: 設計ドキュメント + 実装コード生成

**Step 1**: 独立した組み立て作業が必要で、調整コストを上回る場合だけ `Task(Plan)` を使って設計ドキュメントを組み立てる。小規模な依頼は直接組み立てる。

- テンプレート: [design-document-template.md](references/design-document-template.md)

**Step 2**: 教育的リファレンス

- 各設計判断に `WebSearch` で公式ドキュメントURL取得
- 前提知識の説明（デザインパターン、言語固有考慮）
- パターンリファレンスリンク

**Step 3**: 粒度別出力

- **PR**: Implementation Roadmap（ステップ、ファイル、依存）
- **epic**: PR分割計画（各PRスコープ、依存順序、マージ戦略）

**Step 4**: Dry Coding — 実装コード提示

- 完全で実行可能なコードを提示（ファイル編集はしない）
- 既存パターンに従う
- 必要なimport文を含める
- 以下の形式で出力:

```
### {ファイルパス}
\`\`\`{lang}
{完全な実装コード}
\`\`\`
**実装ポイント**: {重要な設計判断の説明}
```

**Step 5**: ハルシネーション防止

- ファイルパス → `Read`/`Grep` で実在確認
- API/ライブラリ参照 → `WebSearch` で照合
- 各主張に証拠タグ: `direct_code` | `inference`

**成果物の保持**: 設計ドキュメントとDry Codingは会話内のsession stateとして保持する。ファイル保存はユーザーが明示的に求めた場合のみ、保存先を確認して行う。

**確認ゲート**: ドキュメント提示 → ユーザー承認。保存を求められた場合のみ、保存先を確認してファイルへ書き出す。

## エラーハンドリング

| 状況 | 対応 |
| ------ | ------ |
| 無効なGitHub URL | 再入力 or テキストフォールバック |
| プライベートリポジトリ | `gh auth login` ガイド |
| テスト基盤なし | D1評価時に明記、テスト基盤セットアップを計画に含める |
| コードベースが巨大 | 要件に関連する領域に限定してGrep/Glob |
| 全アプローチ収束 | 発散的アプローチを強制生成する追加Plan agent起動 |
| 情報不足 | ユーザーに追加情報を求める + WebSearchで補完 |
