---
name: pr-generator
description: |
  明示的に `pr-generator` を呼び出した場合のみ使用する。
  現在のgit状態を分析し、簡潔なPRを自動生成する。
  Linear統合なしのシンプルなPR作成コマンド。
disable-model-invocation: true
---

# PR Generation Command (without Linear Integration)

現在のgit状態を分析し、簡潔なPRを作成します。

## 実行手順

1. **Git状態の分析**
   - `git status` で未コミットの変更を確認
   - `git diff main...HEAD` と `git log main..HEAD --oneline` で差分とコミット履歴を確認
   - **base ブランチを確認する**: feature 作業では initiative の release ブランチが base のことがある。無指定で main に向けない
   - 現在のブランチ名を確認

2. **リポジトリの既存フォーマットに寄せる**
   - `gh pr list --limit 5` で直近のマージ済みPRを見て、タイトル・本文のセクション構成と粒度を踏襲する
   - 既存フォーマットが見つからない場合のみ下記の既定フォーマットを使う

3. **PR作成の実行**

   **既定フォーマット**（What / How / Test を各2〜3項目に絞る。長い説明はレビュアーの負担）:

   ```markdown
   ## What
   [何を変えたか、2-3項目]

   ## How
   [どう実現したか、2-3項目]

   ## Test
   [実行した検証と結果、2-3項目。再現可能なコマンドを含める]
   ```

   関連Issueがあれば `Closes #XX` を添える。破壊的変更・移行手順は該当する場合のみ節を足す。

4. **フォローアップ**
   - 作成されたPR URLの提供
   - CI/CDステータスの確認

## ルール

- **AI署名・絵文字・定型フッターを入れない。** `Generated with Claude Code` や `Co-Authored-By: Claude` は外部に残る文面なので禁止（ユーザーの反復指示）
- **言語**: toridori 系リポジトリは日本語。`github.com/sorafujitani/*` や `fs0414/*` などOSS・公開個人リポは英語で書く
- **ブランチ名は英数字とハイフンのみ。** 日本語入りブランチ名は GitHub の Hidden character warning を出し、rename すると旧PRが閉じられる副作用がある
- 目的外の差分（他アプリの変更・再生成された lock ファイル・未追跡の生成物）が混入していないか push 前に確認する
- コミットされていない重要な変更がある場合は先にコミットを促す

## 成功基準

- レビュアーが1画面で変更の意図と検証内容を把握できる
- テスト手順が再現可能
- 既存PRと並べて違和感がない
