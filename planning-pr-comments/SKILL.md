---
name: planning-pr-comments
description: |
  GitHub PRのレビューコメント分析と改善計画の策定。
  現在のブランチに関連するPRの未解決コメントを取得・分析し、
  重要度分類（Critical/Important/Minor）と体系的な改善実行計画を生成する。
disable-model-invocation: true
---

# PR Comment Analysis & Improvement Planning

あなたはGitHub PRのレビューコメント分析と改善計画の専門家です。現在のブランチに関連するPRの未解決コメントを取得・分析し、体系的な改善計画を策定します。

## 実行手順

1. **PR特定**
   - 現在のブランチ名を確認: `git branch --show-current`
   - 関連するPR番号を特定: `gh pr list --head [branch-name] --json number,url --jq '.[0]'`

2. **PRコンテキスト取得**
   - `ctx:github` エージェント（`Task` ツールで `subagent_type: "ctx:github"`）を呼び出し、PR情報を一括取得する
   - プロンプト例: `"{owner}/{repo}#{PR番号} のPR情報を取得して"`
   - 返却される構造化コンテキスト（`=== GITHUB_CONTEXT: PR ===` ブロック）からメタデータ・BODY・REVIEW_STATUS・FILES・COMMENTSを利用する
   - インラインレビューコメント（ファイル・行単位）が必要な場合は追加で取得: `gh api repos/{owner}/{repo}/pulls/{PR番号}/comments --jq '.[] | {path, line, body, user: .user.login, created_at}'`

3. **コメント内容の分析**
   - **重要度分類**:
     - 🔴 Critical: バグ、セキュリティ、パフォーマンス問題
     - 🟡 Important: 設計改善、コード品質
     - 🟢 Minor: スタイル、命名、ドキュメント
   - **カテゴリ分類**:
     - Logic/Bug: ロジックエラーやバグ
     - Performance: パフォーマンス関連
     - Security: セキュリティ懸念
     - Design: 設計・アーキテクチャ
     - Code Quality: コード品質・可読性
     - Testing: テスト関連
     - Documentation: ドキュメント・コメント

4. **改善計画の策定**
   - コメントの優先順位付け
   - 依存関係の特定
   - 実装順序の決定
   - 各改善の影響範囲評価

5. **実行計画の作成**
   - 具体的な修正手順
   - 各修正のコミット計画
   - テスト・検証方法

## 出力形式

### 📊 PR情報
- **PR番号**: #[番号]
- **タイトル**: [PRタイトル]
- **URL**: [GitHub URL]
- **未解決コメント数**: [数]

### 🔍 コメント分析

#### Critical Issues 🔴
1. **[コメント作成者]: [コメント内容の要約]**
   - 場所: `file.ts:L123`
   - カテゴリ: [カテゴリ]
   - 原文: "[実際のコメント]"
   - 影響: [影響範囲の説明]

#### Important Issues 🟡
[同様の形式で記載]

#### Minor Issues 🟢
[同様の形式で記載]

### 📝 改善実行計画

#### Phase 1: Critical修正
```bash
# 1. [修正内容の説明]
# 対象: file.ts
# 理由: [コメント#1への対応]
[具体的なコマンドや修正内容]

git add file.ts
git commit -m "fix: [修正内容]"
```

#### Phase 2: Important修正
[同様の形式で記載]

#### Phase 3: Minor修正
[同様の形式で記載]

### ✅ 検証チェックリスト
- [ ] すべてのCriticalコメントに対応
- [ ] テストが通過することを確認
- [ ] 新たな問題を導入していないことを確認
- [ ] コメントへの返信を準備

### 📃 関連Reference
```markdown
# コメント内容に関連するReference URL

- [Reference 1](https://example.com/ref1)
- [Reference 2](https://example.com/ref2)
```

## 考慮事項

- **優先順位**: Criticalから順に対応し、ブロッカーを解消
- **一貫性**: 同種の問題は一括で修正
- **透明性**: 各修正がどのコメントに対応するか明確化
- **検証可能性**: 修正が適切に機能することを確認
- **情報の公式な引用**: 正確な理解や対応を促す
