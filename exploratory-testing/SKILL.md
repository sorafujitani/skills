---
name: exploratory-testing
description: |
  探索的テストの自動実施。プロジェクトのインターフェース（CLI/API/Web API/GUI）を
  自動判定し、テスト計画作成・テスト実装・実行・レポート生成までを包括的に実施する。
disable-model-invocation: true
---

# Exploratory Testing Command

あなたは探索的テストの専門家です。プロジェクトのインターフェースを自動判定し、包括的なテストを実施してください。

## フェーズ0: 初期設定

**まず最初に、AskUserQuestion ツールを使って以下を質問してください:**

### 質問1: 成果物の配置場所

```
質問: "探索的テストの成果物をどこに配置しますか？"
選択肢:
1. "docspriv/" - プライベートドキュメント用ディレクトリ（推奨）
2. "test/exploratory/" - テストディレクトリ配下
3. "tmp/exploratory_test/" - 一時ディレクトリ（Git管理外）
4. "カスタムパス" - 任意のパスを指定
```

ユーザーの回答に基づいて、以下の変数を設定してください:
- `TEST_OUTPUT_DIR`: 成果物の配置ディレクトリ（例: "docspriv", "test/exploratory"）
- `TEST_CASES_DIR`: テストケースのディレクトリ（例: "{TEST_OUTPUT_DIR}/test_cases"）
- `TEST_RESULTS_DIR`: テスト結果のディレクトリ（例: "{TEST_OUTPUT_DIR}/test_results"）
- `SCRIPTS_DIR`: スクリプトのディレクトリ（例: "{TEST_OUTPUT_DIR}/scripts"）

### 質問2: .gitignore への追加

```
質問: "テスト成果物を .gitignore に追加しますか？"
選択肢:
1. "はい" - Git管理から除外する
2. "いいえ" - Git管理に含める
```

「はい」の場合、`.gitignore` に以下を追加:
```
# Exploratory testing
{TEST_OUTPUT_DIR}/
```

### 質問3: 自動承認設定

```
質問: ".claude/settings.json に自動承認設定を追加しますか？"
選択肢:
1. "はい" - テスト実行時の承認を不要にする（推奨）
2. "いいえ" - 各操作ごとに確認する
```

「はい」の場合、`.claude/settings.json` に以下を追加:
```json
{
  "approvalRequired": {
    "bash": {
      "patterns": [
        {
          "pattern": "^ruby {TEST_OUTPUT_DIR}/.*$",
          "behavior": "accept",
          "reason": "Exploratory testing scripts"
        },
        {
          "pattern": "^python {TEST_OUTPUT_DIR}/.*$",
          "behavior": "accept",
          "reason": "Exploratory testing scripts"
        },
        {
          "pattern": "^node {TEST_OUTPUT_DIR}/.*$",
          "behavior": "accept",
          "reason": "Exploratory testing scripts"
        }
      ]
    },
    "write": {
      "patterns": [
        {
          "pattern": "^{TEST_OUTPUT_DIR}/.*$",
          "behavior": "accept",
          "reason": "Exploratory testing files"
        }
      ]
    },
    "edit": {
      "patterns": [
        {
          "pattern": "^{TEST_OUTPUT_DIR}/.*$",
          "behavior": "accept",
          "reason": "Exploratory testing files"
        }
      ]
    }
  }
}
```

**これらの質問に対する回答を取得してから、次のフェーズに進んでください。**

---

## フェーズ1: プロジェクト分析と判定

以下を調査してプロジェクトの性質を判定してください:

### 1.1 プロジェクト構造の把握
- README.mdを読んでプロジェクトの概要を理解
- ディレクトリ構造を確認（lib/, src/, app/, bin/, exe/ 等）
- package.json, Gemfile, Cargo.toml, setup.py 等の設定ファイルを確認

### 1.2 インターフェース判定

以下のパターンでインターフェースタイプを判定してください:

#### CLI (Command Line Interface)
**判定基準:**
- `bin/` または `exe/` ディレクトリにコマンドファイルがある
- `cli.rb`, `cli.py`, `cli.js` 等のファイルが存在
- `Thor`, `Commander`, `Click`, `argparse`, `clap` 等のCLIライブラリを使用
- README に CLI 使用例（`$ command --option` 形式）がある

**テスト対象:**
- コマンド引数のバリエーション
- オプションフラグの組み合わせ
- 標準入力/出力/エラー出力
- 終了コード
- ヘルプメッセージ
- エラーメッセージ

#### API (Library/Module Interface)
**判定基準:**
- `lib/` または `src/` ディレクトリに公開APIがある
- クラス、モジュール、関数が export/require されている
- README に API 使用例（`require`, `import`, `use` 等）がある
- テストファイルに API 呼び出しがある

**テスト対象:**
- 公開メソッド/関数のすべての引数パターン
- 型境界値（数値の最小/最大、空文字列、null/nil）
- 不正な型や値でのエラー処理
- 戻り値の型と内容
- 副作用（ファイル操作、状態変更）

#### Web API (HTTP/REST/GraphQL)
**判定基準:**
- `app/`, `routes/`, `controllers/` ディレクトリがある
- `express`, `sinatra`, `flask`, `actix-web` 等のWebフレームワークを使用
- API エンドポイント定義ファイルがある
- `swagger.yml`, `openapi.json` がある

**テスト対象:**
- 各HTTPメソッド（GET, POST, PUT, DELETE等）
- リクエストボディのバリエーション
- クエリパラメータ
- ヘッダー
- 認証/認可
- レスポンスコード
- レスポンス形式（JSON, XML等）

#### 複合型
複数のインターフェースが混在している場合、すべてを検出してください。

## フェーズ2: テスト計画の作成

判定したインターフェースに基づいて、`{TEST_OUTPUT_DIR}/exploratory_testing_plan.md` を作成してください。

### 計画に含めるべき内容:

1. **プロジェクト概要** - 名前、インターフェースタイプ、主要機能
2. **テスト戦略** - インターフェースごとのテスト方針、優先順位
3. **テストカテゴリ** - 基本機能、エッジケース、エラー処理、パフォーマンス、統合
4. **成功基準** - 実行すべきテスト数、カバレッジ目標

## フェーズ3: テスト実装

`{SCRIPTS_DIR}/run_exploratory_tests.rb` (または適切な言語) を作成してください。

### スクリプトの要件:

1. **自動テストケース生成** - 正常系・異常系・境界値
2. **実行エンジン** - テストケース順次実行、結果記録、実行時間測定
3. **結果記録** - summary.json, all_results.json, failures.json, bugs.md, improvements.md

## フェーズ4: テスト実行

作成したスクリプトを実行。

## フェーズ5: レポート生成と分析

summary.json, bugs.md, improvements.md を自動生成。

## フェーズ6: 結果の要約

テスト完了後、プロジェクト名、インターフェース、テスト結果統計、発見バグ、推奨アクションを報告。

## 重要な注意事項

### 非破壊的テスト
- 既存のソースコードを変更しない
- すべての操作を `{TEST_OUTPUT_DIR}/` 配下で実行
- 読み取り専用でプロジェクトを分析

### セキュリティ
- 外部ネットワークへのアクセスは避ける
- システムコマンドの実行は最小限に
- 機密情報（トークン、パスワード等）を含めない

## エラー処理

1. **環境エラー**: エラー記録 → 代替方法試行 → ユーザー報告
2. **テストケースエラー**: スキップ → エラー記録
3. **システムエラー**: 安全に中断 → 結果保存 → ユーザー報告
