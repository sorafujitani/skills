# Rule Mappings (3-way)

よく聞かれる lint ルールの 3-way マッピング表。ここに載っているものは即答してよい。載っていない or 鮮度が怪しい場合は [linter-docs.md](linter-docs.md) の方針で WebFetch / WebSearch して確認すること。

## Contents

1. 表の読み方
2. 非同期 / Promise — floating promise / misused promise / require-await / async executor
3. 型安全性 (TypeScript 固有) — no-explicit-any / no-non-null-assertion / 不要な型アサーション / strict-boolean-expressions
4. 未使用検出 — 変数 / import / 式
5. 可読性・スタイル — prefer-const / nullish coalescing / optional chain / prefer-template / eqeqeq / no-shadow
6. 危険・バグ — no-debugger / no-console / no-eval / no-empty / no-fallthrough
7. import / export — 循環 / 重複 / `import type` 強制
8. React / React Hooks — rules-of-hooks / exhaustive-deps
9. クラス / 構造 — no-misused-new / no-this-alias
10. 表に無い時の手順
11. 更新ポリシー

## 表の読み方

- **状態の凡例**: ✅ Stable / ⚠️ Nursery (Biome) / ⚠️ Type-aware (型情報必須) / 🟡 Partial (検出範囲が違う) / ❌ Not supported
- **ルール名**: 設定時に書く形で記す
  - typescript-eslint: `@typescript-eslint/<rule>`
  - oxlint: `<category>/<rule>`（ESLint コア相当はカテゴリ無しで書ける場合もある）
  - Biome: `<camelCaseName>`（設定キー）
- **URL**: 公式の個別ルールページ。`?` は URL 形式から構成しただけで未確認の場合に付ける（最終提示前に WebFetch で実在確認すると安全）
- **鮮度**: このファイルは 2026-05 時点のスナップショット。`nursery` の昇格や oxlint の新規移植は頻繁に起こる。曖昧な時は確認する

---

## 1. 非同期 / Promise

### Floating promise（戻り値を await / .then せず捨てている）

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-floating-promises` | ⚠️ Type-aware | https://typescript-eslint.io/rules/no-floating-promises/ |
| oxlint | `typescript/no-floating-promises` | ✅ (型情報部分対応) | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-floating-promises.html |
| Biome | `noFloatingPromises` | ⚠️ Nursery + Type-aware | https://biomejs.dev/linter/rules/no-floating-promises/ |

### Promise を await すべきでない場所に渡している

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-misused-promises` | ⚠️ Type-aware | https://typescript-eslint.io/rules/no-misused-promises/ |
| oxlint | `typescript/no-misused-promises` | 🟡 部分対応 | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-misused-promises.html |
| Biome | `noMisusedPromises` | ⚠️ Nursery | https://biomejs.dev/linter/rules/no-misused-promises/ |

### async 関数が await を持たない (= async 過剰)

> ⚠️ **混同注意**: これは「await 忘れ」ではない。「async を付けたのに本体に await が無い (async が不要)」を検出するルール。ユーザーが「await 忘れ」と言った時に並べないこと。本物の「await 忘れ」は前述の **Floating promise** セクション (`no-floating-promises`) を見る。

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `require-await` | ✅ | https://eslint.org/docs/latest/rules/require-await |
| typescript-eslint | `@typescript-eslint/require-await` | ⚠️ Type-aware | https://typescript-eslint.io/rules/require-await/ |
| oxlint | `eslint/require-await` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/require-await.html |
| Biome | `useAwait` | ✅ | https://biomejs.dev/linter/rules/use-await/ |

### Promise executor 内で async を使う

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-async-promise-executor` | ✅ | https://eslint.org/docs/latest/rules/no-async-promise-executor |
| typescript-eslint | (ESLint コアと同名) | — | — |
| oxlint | `eslint/no-async-promise-executor` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-async-promise-executor.html |
| Biome | `noAsyncPromiseExecutor` | ✅ | https://biomejs.dev/linter/rules/no-async-promise-executor/ |

---

## 2. 型安全性 (TypeScript 固有)

### `any` の明示利用

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-explicit-any` | ✅ | https://typescript-eslint.io/rules/no-explicit-any/ |
| oxlint | `typescript/no-explicit-any` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-explicit-any.html |
| Biome | `noExplicitAny` | ✅ | https://biomejs.dev/linter/rules/no-explicit-any/ |

### Non-null assertion (`!`) の利用

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-non-null-assertion` | ✅ | https://typescript-eslint.io/rules/no-non-null-assertion/ |
| oxlint | `typescript/no-non-null-assertion` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-non-null-assertion.html |
| Biome | `noNonNullAssertion` | ✅ | https://biomejs.dev/linter/rules/no-non-null-assertion/ |

### 不要な型アサーション

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-unnecessary-type-assertion` | ⚠️ Type-aware | https://typescript-eslint.io/rules/no-unnecessary-type-assertion/ |
| oxlint | (移植検討中) | ❌ または 🟡 | — |
| Biome | `noUselessTypeConstraint` ※別目的 / 該当無し | 🟡 | — |

注: oxlint と Biome の対応は変動しやすい領域。確認するなら最新版のドキュメント。

### 厳格な boolean 判定（truthy 評価の落とし穴）

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/strict-boolean-expressions` | ⚠️ Type-aware | https://typescript-eslint.io/rules/strict-boolean-expressions/ |
| oxlint | — | ❌ | — |
| Biome | — | ❌ | — |

---

## 3. 未使用検出

### 未使用変数

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-unused-vars` | ✅ | https://eslint.org/docs/latest/rules/no-unused-vars |
| typescript-eslint | `@typescript-eslint/no-unused-vars` | ✅ (コア拡張) | https://typescript-eslint.io/rules/no-unused-vars/ |
| oxlint | `eslint/no-unused-vars` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-unused-vars.html |
| Biome | `noUnusedVariables` | ✅ | https://biomejs.dev/linter/rules/no-unused-variables/ |

### 未使用 import

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — (`no-unused-vars` で部分検出) | 🟡 | — |
| typescript-eslint | (同上) | 🟡 | — |
| oxlint | `import/no-unused-modules` 等 | 🟡 | https://oxc.rs/docs/guide/usage/linter/rules.html |
| Biome | `noUnusedImports` | ✅ | https://biomejs.dev/linter/rules/no-unused-imports/ |

注: ESLint 側は伝統的に `eslint-plugin-unused-imports` プラグインを併用するパターン。

### 未使用式

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-unused-expressions` | ✅ | https://eslint.org/docs/latest/rules/no-unused-expressions |
| typescript-eslint | `@typescript-eslint/no-unused-expressions` | ✅ | https://typescript-eslint.io/rules/no-unused-expressions/ |
| oxlint | `eslint/no-unused-expressions` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-unused-expressions.html |
| Biome | `noUnusedExpressions` ※`nursery` 経由のことあり | ⚠️ | https://biomejs.dev/linter/rules/no-unused-expressions/ |

---

## 4. 可読性 / スタイル / 推奨表現

### `const` を優先

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `prefer-const` | ✅ | https://eslint.org/docs/latest/rules/prefer-const |
| typescript-eslint | (コアと同名) | — | — |
| oxlint | `eslint/prefer-const` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/prefer-const.html |
| Biome | `useConst` | ✅ | https://biomejs.dev/linter/rules/use-const/ |

### Nullish coalescing (`??`) を優先

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/prefer-nullish-coalescing` | ⚠️ Type-aware (一部) | https://typescript-eslint.io/rules/prefer-nullish-coalescing/ |
| oxlint | `typescript/prefer-nullish-coalescing` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/prefer-nullish-coalescing.html |
| Biome | `useNullishCoalescing` ※グループは要確認 | ⚠️ | https://biomejs.dev/linter/rules/use-nullish-coalescing/ |

### Optional chaining (`?.`) を優先

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/prefer-optional-chain` | ✅ | https://typescript-eslint.io/rules/prefer-optional-chain/ |
| oxlint | `typescript/prefer-optional-chain` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/prefer-optional-chain.html |
| Biome | `useOptionalChain` | ✅ | https://biomejs.dev/linter/rules/use-optional-chain/ |

### テンプレートリテラル優先

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `prefer-template` | ✅ | https://eslint.org/docs/latest/rules/prefer-template |
| oxlint | `eslint/prefer-template` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/prefer-template.html |
| Biome | `useTemplate` | ✅ | https://biomejs.dev/linter/rules/use-template/ |

### `==` 禁止 (`===` 強制)

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `eqeqeq` | ✅ | https://eslint.org/docs/latest/rules/eqeqeq |
| oxlint | `eslint/eqeqeq` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/eqeqeq.html |
| Biome | `noDoubleEquals` | ✅ | https://biomejs.dev/linter/rules/no-double-equals/ |

注: Biome は「悪い形」を名前にする傾向。`eqeqeq` ↔ `noDoubleEquals` は名前が真逆だが等価。

### 変数 shadowing

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-shadow` | ✅ | https://eslint.org/docs/latest/rules/no-shadow |
| typescript-eslint | `@typescript-eslint/no-shadow` | ✅ | https://typescript-eslint.io/rules/no-shadow/ |
| oxlint | `eslint/no-shadow` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-shadow.html |
| Biome | `noShadow` ※`nursery` で扱われることあり | ⚠️ | https://biomejs.dev/linter/rules/no-shadow/ |

---

## 5. 危険・バグになりやすいパターン

### `debugger` 文

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-debugger` | ✅ | https://eslint.org/docs/latest/rules/no-debugger |
| oxlint | `eslint/no-debugger` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-debugger.html |
| Biome | `noDebugger` | ✅ | https://biomejs.dev/linter/rules/no-debugger/ |

### `console` 利用

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-console` | ✅ | https://eslint.org/docs/latest/rules/no-console |
| oxlint | `eslint/no-console` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-console.html |
| Biome | `noConsole` (旧 `noConsoleLog`) | ✅ | https://biomejs.dev/linter/rules/no-console/ |

### `eval` 利用

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-eval` | ✅ | https://eslint.org/docs/latest/rules/no-eval |
| oxlint | `eslint/no-eval` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-eval.html |
| Biome | `noGlobalEval` | ✅ | https://biomejs.dev/linter/rules/no-global-eval/ |

### 空ブロック

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-empty` | ✅ | https://eslint.org/docs/latest/rules/no-empty |
| oxlint | `eslint/no-empty` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-empty.html |
| Biome | `noEmptyBlockStatements` | ✅ | https://biomejs.dev/linter/rules/no-empty-block-statements/ |

### switch case フォールスルー

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-fallthrough` | ✅ | https://eslint.org/docs/latest/rules/no-fallthrough |
| oxlint | `eslint/no-fallthrough` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-fallthrough.html |
| Biome | `noFallthroughSwitchClause` | ✅ | https://biomejs.dev/linter/rules/no-fallthrough-switch-clause/ |

---

## 6. import / export

### 循環 import

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| eslint-plugin-import | `import/no-cycle` | ✅ | https://github.com/import-js/eslint-plugin-import/blob/main/docs/rules/no-cycle.md |
| oxlint | `import/no-cycle` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/import/no-cycle.html |
| Biome | `noCycle` ※グループは要確認 / `nursery` の可能性 | ⚠️ | https://biomejs.dev/linter/rules/ |

### 重複 import

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | `no-duplicate-imports` | ✅ | https://eslint.org/docs/latest/rules/no-duplicate-imports |
| oxlint | `eslint/no-duplicate-imports` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/eslint/no-duplicate-imports.html |
| Biome | `noDuplicateImports` ※ある場合 / 代替 `useImportType` | 🟡 | https://biomejs.dev/linter/rules/ |

### `import type` 強制

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/consistent-type-imports` | ✅ | https://typescript-eslint.io/rules/consistent-type-imports/ |
| oxlint | `typescript/consistent-type-imports` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/consistent-type-imports.html |
| Biome | `useImportType` | ✅ | https://biomejs.dev/linter/rules/use-import-type/ |

---

## 7. React / React Hooks

### Hooks ルール（ルールオブフックス）

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint + eslint-plugin-react-hooks | `react-hooks/rules-of-hooks` | ✅ | https://react.dev/reference/rules/rules-of-hooks |
| oxlint | `react-hooks/rules-of-hooks` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/react-hooks/rules-of-hooks.html |
| Biome | `useHookAtTopLevel` | ✅ | https://biomejs.dev/linter/rules/use-hook-at-top-level/ |

### useEffect の依存配列

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint + eslint-plugin-react-hooks | `react-hooks/exhaustive-deps` | ✅ | https://react.dev/reference/react/useEffect#specifying-reactive-dependencies |
| oxlint | `react-hooks/exhaustive-deps` ※部分対応 | 🟡 | https://oxc.rs/docs/guide/usage/linter/rules/react-hooks/exhaustive-deps.html |
| Biome | `useExhaustiveDependencies` | ✅ | https://biomejs.dev/linter/rules/use-exhaustive-dependencies/ |

---

## 8. クラス / 構造

### `new` の誤用 (interface に new を持たせる等)

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-misused-new` | ✅ | https://typescript-eslint.io/rules/no-misused-new/ |
| oxlint | `typescript/no-misused-new` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-misused-new.html |
| Biome | `noMisleadingInstantiator` ※近い目的 | 🟡 | https://biomejs.dev/linter/rules/no-misleading-instantiator/ |

### `this` の別名代入禁止

| Linter | Rule | 状態 | URL |
|---|---|---|---|
| ESLint (core) | — | ❌ | — |
| typescript-eslint | `@typescript-eslint/no-this-alias` | ✅ | https://typescript-eslint.io/rules/no-this-alias/ |
| oxlint | `typescript/no-this-alias` | ✅ | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-this-alias.html |
| Biome | `noThisInStatic` ※別目的に近い / 該当ルールは要確認 | 🟡 | — |

---

## 表に無い時の手順

1. [linter-docs.md](linter-docs.md) で各 linter の一覧ページ URL を確認
2. 4 つを WebFetch で並列取得（ESLint core / typescript-eslint / oxlint / Biome）
3. ページ内をキーワード grep（`floating`, `unused`, `shadow` 等）
4. 不明確なら WebSearch で `"<rule-name>" biome` のように補助検索（公式ドメイン優先）
5. Biome のルールページの **Sources セクション** が他 linter との対応関係の一次資料として使える

## このファイル自体の更新ポリシー

- `nursery` 昇格や oxlint の新規移植は頻繁。**確証が無い行は「URL 確認推奨」と添える** か、状態列を `⚠️` で示す
- 「mapping table 経由で答えた」ことは出力に明示する。利用者が鮮度を判断できる
- 表に無いルールが繰り返し聞かれるようなら、このファイルに追記する（メンテは利用者の関心ドメインに合わせる）
