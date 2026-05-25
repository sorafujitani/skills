# Linter Documentation Reference

3 つの linter の公式ドキュメント構造・命名規則・特性をまとめる。動的検索（WebFetch / WebSearch）時の道しるべとして使う。

## ESLint (core)

- **公式ルール一覧**: https://eslint.org/docs/latest/rules/
- **個別ルール URL パターン**: `https://eslint.org/docs/latest/rules/<rule-name>`
  - 例: `https://eslint.org/docs/latest/rules/no-unused-vars`
- **命名規則**: `kebab-case`（例: `no-unused-vars`, `prefer-const`, `eqeqeq`）
- **特徴**:
  - 言語非依存のコアルール。型情報は使わない（JS としての構文ベース）
  - TypeScript 固有のルールは含まれない → typescript-eslint 側を見る
  - カテゴリ: `Possible Problems`, `Suggestions`, `Layout & Formatting` (廃止予定)

## typescript-eslint

- **公式ルール一覧**: https://typescript-eslint.io/rules/
- **個別ルール URL パターン**: `https://typescript-eslint.io/rules/<rule-name>/`
  - 例: `https://typescript-eslint.io/rules/no-floating-promises/`
- **設定時のルール名**: `@typescript-eslint/<rule-name>`
  - 例: `@typescript-eslint/no-floating-promises`
- **命名規則**: `kebab-case`
- **特徴**:
  - ESLint プラグインとして動作。ESLint コアと併用が前提
  - 型情報を使うルールには ❶ アイコンや `Requires Type Information` 表記がある
    - これらは `parserOptions.project` の設定が必須
  - `extension rules`: ESLint コアの同名ルールを TypeScript 構文対応に拡張したもの（例: `@typescript-eslint/no-unused-vars`）。コア側を無効化して使う

## oxlint (Oxc)

- **公式ルール一覧**: https://oxc.rs/docs/guide/usage/linter/rules.html
- **個別ルール URL パターン**: `https://oxc.rs/docs/guide/usage/linter/rules/<category>/<rule-name>.html`
  - 例: `https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-floating-promises.html`
- **設定時のルール名**: `<category>/<rule-name>` または ESLint コアの場合はカテゴリなしで `<rule-name>`
- **命名規則**: ESLint / 各プラグインの命名をそのまま移植する方針 → 多くが `kebab-case`
- **カテゴリ (category prefix)**:
  - `eslint` (コア相当)
  - `typescript` (typescript-eslint 相当)
  - `react` / `react-hooks` / `react-perf`
  - `unicorn`
  - `import`
  - `jsdoc`
  - `node`
  - `promise`
  - `vitest` / `jest`
  - `nextjs`
  - `oxc` (oxlint 独自ルール)
- **特徴**:
  - Rust 製で高速。ESLint との互換を目指して移植中（カバレッジは全部ではない）
  - 型情報を使うルールは限定的にサポート。`--type-aware` フラグや tsconfig 連携で有効化
  - 未実装ルールは "Not yet supported" として一覧に明示されることがある

## Biome lint

- **公式ルール一覧**: https://biomejs.dev/linter/rules/
- **個別ルール URL パターン**: `https://biomejs.dev/linter/rules/<kebab-case-rule-name>/`
  - 例: `https://biomejs.dev/linter/rules/no-floating-promises/`
- **設定時のルール名**: `<camelCaseRuleName>`（biome.json 内で使う）
  - 例: `noFloatingPromises`
- **命名規則**: ドキュメント URL は `kebab-case`、設定キーは `camelCase`
  - `no-*` → `noXxx` (例: `no-floating-promises` → `noFloatingPromises`)
  - Biome 独自に `use-*` プレフィックスがある (例: `useConst`, `useExhaustiveDependencies`)
- **グループ**: ドキュメントは以下のグループに分かれている
  - `a11y` (Accessibility)
  - `complexity`
  - `correctness`
  - `nursery` ⚠️ — 安定前。挙動が変わる可能性あり
  - `performance`
  - `security`
  - `style`
  - `suspicious`
- **特徴**:
  - 命名規則がほぼ ESLint と 1:1 対応するが camelCase に変換される
  - 各ルールページに "Sources" セクションがあり、ESLint / typescript-eslint 等の元ルールへのリンクが書かれている → **3-way マッピングの一次資料として有用**
  - 型情報を使うルールは新しい機能 (`nursery` に入っているものが多い)。プロジェクト設定で `typescript` が必要

## 検索のコツ

### 一覧ページからキーワード検索

- 各 linter の一覧ページは長いので、Ctrl-F 相当でキーワードを引く（WebFetch で取得後、テキスト中から `floating`, `promise`, `unused`, `shadow` 等で grep する）
- ESLint と typescript-eslint は別ページなので両方見る

### Biome の Sources 欄を逆引きに使う

- Biome のルールページには「元の ESLint / typescript-eslint ルール名」が書いてある
- 例: `noFloatingPromises` のページ → "Sources: @typescript-eslint/no-floating-promises"
- これにより `ESLint 名 ⇄ Biome 名` の確証が取れる

### oxlint で見つからない時の判別

- oxlint はカバレッジが部分的。一覧ページに無ければ "Not yet supported" と判定して良い
- ただし、新しい ESLint ルールが移植され続けているので、不確実な場合は WebSearch で `"<rule-name>" oxlint` を引く

### よくある誤マッピング注意

- ESLint コアの `no-unused-vars` と typescript-eslint の `no-unused-vars` は **別ルール**（後者は前者を TypeScript 構文対応に拡張したもの）
- Biome の `noUnusedVariables` は ESLint の `no-unused-vars` と typescript-eslint の `@typescript-eslint/no-unused-vars` の双方を Sources に挙げている（実体は 1 つ）
- `consistent-return` のように似た名前でも検出範囲が違うルールがある → 「同等」と書く前に各ドキュメントの説明文を見る
