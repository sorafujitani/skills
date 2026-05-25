# Query Disambiguation Guide

ユーザーがよく使う表現と、その**真の意図**・**該当ルール**・**混同しがちな別ルール**の対応集。SKILL.md のワークフロー Step 1（入力解釈）と Step 4（意味検証）の判断材料。

## Contents

1. 使い方
2. 「await 忘れ」「await し忘れ」 — `no-floating-promises` vs `require-await`（async 過剰）
3. 「any 禁止」「any 検出」 — 明示 any vs any 値の利用
4. 「未使用」— 変数 / import / 関数
5. 「依存配列」「deps」— React Hooks `exhaustive-deps`
6. 「シャドウイング」「shadow」— 変数 / 型
7. 「型安全」「safe」— 多義のため確認質問へ
8. 「console を消したい」— `no-console` + `no-debugger`
9. 「null チェック」「null 安全」— non-null assertion / nullish coalescing / optional chain / strict-boolean
10. 「import 整理」— 未使用 / 順序 / 重複 / `import type`
11. 「マジックナンバー」
12. 「constructor で複雑」「クラスの設計」— 多義のため確認質問へ
13. まとめ — 判断の優先順位

## 使い方

1. ユーザー入力に含まれるキーワードを下記の「典型表現」と照合
2. 該当エントリの「典型的な意図」「該当ルール」「混同しがちな別ルール」を確認
3. **混同しがちな別ルール** は「検出対象」表に並べず、補足の「関連ルール」に降ろす
4. 「矛盾入力パターン」に当てはまる場合は読み替えを明示するか、確認質問

---

## 「await 忘れ」「await し忘れ」「await されてない」

**典型的な意図**: Promise を返す関数を呼んで、その戻り値を await / .then / .catch せず捨てている

**該当ルール**: `no-floating-promises` 系
- `@typescript-eslint/no-floating-promises`
- `typescript/no-floating-promises`
- `noFloatingPromises` (Biome `nursery`)

**混同しがちな別ルール**（**同じ表に並べない**）:
- `require-await` / `useAwait` → 「**async** を付けたのに本体に await が無い」検出。これは「**async 過剰**」であって「await 忘れ」ではない
- `no-misused-promises` → 「Promise を boolean 文脈や void 期待の場所に渡している」検出。これも別目的

**矛盾入力パターン**:
- 「**同期**関数の await 忘れ」 → 同期関数に await は付かない。typo（非同期）の可能性高い → 読み替えを明示
- 「await 忘れ + require-await」 → ユーザーが両者を同じ概念と思っている可能性。明示的に区別する

---

## 「any 禁止」「any 検出」「any を使わせない」

**典型的な意図** (2 通り):

(a) コード中の **明示的な `: any`** アノテーションを禁止
→ `no-explicit-any` 系
- `@typescript-eslint/no-explicit-any`
- `typescript/no-explicit-any`
- `noExplicitAny`

(b) **any 型の値の利用**（明示・暗黙問わず、any 経由で型情報が抜けたもの）を禁止
→ `no-unsafe-*` 系（type-aware）
- `@typescript-eslint/no-unsafe-assignment`
- `@typescript-eslint/no-unsafe-call`
- `@typescript-eslint/no-unsafe-member-access`
- `@typescript-eslint/no-unsafe-return`
- `@typescript-eslint/no-unsafe-argument`

**判断**: 主解釈は (a)。末尾で「(b) も探していますか？」と 1 行。

---

## 「未使用」「使ってない」

**典型的な意図** (3 通り):

(a) 変数 → `no-unused-vars` / `@typescript-eslint/no-unused-vars` / `noUnusedVariables`
(b) import → `noUnusedImports`（Biome）。ESLint 側は `eslint-plugin-unused-imports` プラグインが慣例
(c) 関数・メソッド → 多くは (a) でカバー。private メソッド検出は `@typescript-eslint/no-unused-private-class-members` (ESLint コア同名)

**判断**: 主解釈 = (a) 変数。末尾で「import / 関数の意図もあれば言ってください」と 1 行。

---

## 「依存配列」「deps」「useEffect の依存」

**典型的な意図**: React `useEffect` / `useCallback` / `useMemo` の依存配列の不足検出

**該当ルール**:
- `react-hooks/exhaustive-deps`（ESLint + eslint-plugin-react-hooks）
- `react-hooks/exhaustive-deps`（oxlint, 部分対応）
- `useExhaustiveDependencies`（Biome）

**混同しがちな別ルール**:
- `react-hooks/rules-of-hooks` / `useHookAtTopLevel` → Hooks をトップレベルで呼んでいるかの検出。「依存配列」とは別

---

## 「シャドウイング」「shadow」「同名変数」

**典型的な意図**: 同名変数で外側のスコープを覆い隠している

**該当ルール**: `no-shadow` 系
- `no-shadow`
- `@typescript-eslint/no-shadow`（型シャドウも含めて検出）
- `eslint/no-shadow`（oxlint）
- `noShadow`（Biome, 状態は要確認）

**混同しがちな別ルール**:
- `no-redeclare` → 同一スコープでの再宣言。シャドウとは別

---

## 「型安全」「safe」「タイプセーフ」

**曖昧度 = 高**。5 つ以上のルールに展開しうる:
- 明示 any 禁止 → `no-explicit-any`
- any 値の利用禁止 → `no-unsafe-*` 系
- 厳格な boolean 評価 → `strict-boolean-expressions`
- non-null assertion 禁止 → `no-non-null-assertion`
- 不要な型アサーション禁止 → `no-unnecessary-type-assertion`
- `consistent-type-imports` → `import type` の強制

**判断**: 主解釈を選ばず **AskUserQuestion で意図を絞る**。並列で全部出さない。

---

## 「console を消したい」「debug コード残し」

**典型的な意図** (2 通り、補完関係):
- console.log 検出 → `no-console` / `noConsole` (Biome は旧 `noConsoleLog`)
- debugger 文検出 → `no-debugger` / `noDebugger`

**判断**: 補完関係なので 2 つの「検出対象」セクションに分けて並列出力して良い（別目的ではあるが同じユーザー意図にまとめて答える価値がある）。

---

## 「null チェック」「null 安全」

**典型的な意図** (複数ありえる):
- non-null assertion `!` を禁止 → `no-non-null-assertion`
- nullish coalescing `??` を優先 → `prefer-nullish-coalescing`
- optional chain `?.` を優先 → `prefer-optional-chain`
- 厳格な boolean 評価 → `strict-boolean-expressions`（typescript-eslint のみ）

**判断**: 曖昧度 = 中。主解釈は文脈次第（コード例があるならそれで判断）。無ければ確認。

---

## 「import を整理」「import 整理」

**典型的な意図** (複数):
- 未使用 import → `noUnusedImports`
- import 順序 → `sort-imports` / `import/order` / Biome は `useSortedKeys` 系ではない（formatter 側で対応）
- 重複 import → `no-duplicate-imports`
- `import type` 強制 → `consistent-type-imports`

**判断**: 曖昧度 = 中。主解釈は「未使用 import」。

---

## 「console.log 残ってる」「テストコード残し」

**典型的な意図**: 開発中のデバッグコードが残ってないか

**該当ルール群** (補完関係):
- `no-console` / `noConsole`
- `no-debugger` / `noDebugger`
- `no-alert` / `noAlert`（Biome）

---

## 「マジックナンバー」

**典型的な意図**: 意味不明な数値リテラルをコード中に直書きしている

**該当ルール**:
- `no-magic-numbers` / `@typescript-eslint/no-magic-numbers`
- `eslint/no-magic-numbers`（oxlint）
- Biome は該当ルール無し（要確認）

---

## 「constructor で複雑なことしてる」「クラスの設計」

**曖昧度 = 高**。具体的に何を検出したいかで全く違う:
- empty constructor → `@typescript-eslint/no-useless-constructor`
- parameter properties の使用制限 → `@typescript-eslint/parameter-properties`
- new の誤用 → `@typescript-eslint/no-misused-new`
- this 別名 → `@typescript-eslint/no-this-alias`

**判断**: AskUserQuestion で意図を絞る。

---

## まとめ: 判断の優先順位

1. **入力をそのまま読む**（読み替えるなら明示）
2. **このファイルにエントリがあるか**確認
3. エントリの「典型的な意図」が 1 つなら主解釈で進める
4. エントリの「典型的な意図」が複数なら、曖昧度を判定して低/中/高で行動を分ける
5. エントリの「混同しがちな別ルール」は **検出対象表に並べず、補足の関連ルールに降ろす**
6. エントリに無い表現なら、Step 3 の動的検索へ
