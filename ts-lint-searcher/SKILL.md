---
name: ts-lint-searcher
description: ESLint (typescript-eslint 含む) / oxlint / Biome lint の 3 つの TypeScript linter のルールを横断検索する。挙動ベース「await し忘れを検出したい」やルール名ベース「`no-floating-promises` の Biome 版は？」の問いに対し、3-way 比較表 + 公式ドキュメント URL を返す。トリガー — (1) 検出したい挙動からルールを特定、(2) ルール名から他 linter 同等品を照合、(3) カテゴリ単位で 3 linter を並列確認、(4) `/ts-lint-searcher` の明示呼び出し。SKIP — lint 設定ファイル (eslint.config / biome.json) の生成、lint 実行、コードレビュー、TypeScript 言語仕様の一般質問。
---

# ts-lint-searcher

ESLint + typescript-eslint / oxlint / Biome lint の 3 つを横断して TypeScript の lint ルールを検索する。出力は常に「3-way 比較表 + ドキュメントリンク + 補足」。

**やらないこと**: lint 設定ファイルの生成、lint の実行、コードレビュー、ルール採否の意思決定。

## 入力パターン

| 種類 | 例 |
|---|---|
| 挙動ベース | 「await し忘れを検出したい」 |
| ルール名ベース | 「`no-floating-promises` の Biome 版は？」 |
| カテゴリ列挙 | 「React Hooks 関連を 3 linter で並べたい」 |

## ワークフロー

1. **入力を読む**。読み替え（typo修正など）をする時は出力冒頭で必ず明示する。多義語が極端（「型安全」「safe」など 5 つ以上のルールに展開しうる）なら AskUserQuestion で意図を絞る。曖昧入力ごとの典型解釈は [references/query-disambiguation.md](references/query-disambiguation.md)。

2. **マッピング表を引く**: [references/rule-mappings.md](references/rule-mappings.md)。well-known なルールはここで即解決する。

3. **動的検索**（マッピング外、または鮮度を確認したい時のみ）: 以下 4 ページを並列 WebFetch してキーワード grep。命名規則やカテゴリ prefix は [references/linter-docs.md](references/linter-docs.md)。
   - `https://eslint.org/docs/latest/rules/`
   - `https://typescript-eslint.io/rules/`
   - `https://oxc.rs/docs/guide/usage/linter/rules.html`
   - `https://biomejs.dev/linter/rules/`

4. **意味検証**: 候補を表に並べる前に、ルールの実際の検出対象がユーザー語彙と一致するかを 1 文で確認する。**ルール名が似ているだけで並べない**。別目的なら同表に並べず、補足の「関連ルール」に降ろす（例: 「await 忘れ」に `require-await` は並べない — 後者は「async 過剰」検出）。

5. **出力**: 下記テンプレート。

## 出力テンプレート

````markdown
(読み替えがあった場合のみ冒頭に 1 行)
> 注: 「<元の語>」を「<読み替え後>」と解釈しました。意図と違えば教えてください。

## 検出対象: <ユーザーの意図を 1 行>
> このルール群が実際に検出するもの: <ルール定義の言葉で 1 行>

| Linter | Rule | 状態 | ドキュメント |
|---|---|---|---|
| ESLint (core) | `<rule>` または `—` | ✅/⚠️/🟡/❌ | <URL> |
| typescript-eslint | `@typescript-eslint/<rule>` | ... | <URL> |
| oxlint | `<category>/<rule>` | ... | <URL> |
| Biome | `<camelCaseName>` | ... | <URL> |

### 補足
- 型情報の要否（type-aware ルールがあれば）
- 検出範囲の差（linter 間で挙動が違う場合のみ）
- 関連ルール（**別目的**だが混同されやすいもの）
- 別解釈の存在（入力が曖昧だった場合 1 行）
- 出典（動的検索した場合は取得日 YYYY-MM-DD、マッピング経由なら「mapping table 経由」）
````

**状態の凡例**: ✅ Stable / ⚠️ Nursery (Biome) または Type-aware / 🟡 関連だが範囲違う / ❌ Not supported。
該当が無い行は `—` と `❌` で正直に埋め、似たルールで穴埋めしない。

## 落とし穴

- **別目的を同表に並べない**: 意味検証で弾く。代表例: 「await 忘れ」(`no-floating-promises`) と「async 過剰」(`require-await`) は別物
- **読み替えは明示**: 「同期 → 非同期」のような解釈を黙ってやらない
- **複数解釈を全部並列で出さない**: 主解釈 1 つで進め、別解釈の存在は末尾に 1 行
- **公式ドメインのみ引用**: `eslint.org` / `typescript-eslint.io` / `oxc.rs` / `biomejs.dev` 以外は引かない
- **意見は聞かれた時だけ**: どの linter を採用すべきかは事実の提示で止め、求められたら型情報の要否・速度・カバレッジの 3 軸で短く整理する

## ミニ例

入力: 「**同期関数**の await 忘れを検出したい」

判断: 「同期 → 非同期」の typo と解釈（曖昧度低）。「await 忘れ」は `no-floating-promises` 系に一致。`require-await` は別目的なので関連ルールに降ろす。

出力:

```markdown
> 注: 「同期関数」を「非同期関数」の typo と解釈しました。意図と違えば教えてください。

## 検出対象: 非同期関数の戻り値の Promise を await/.then/.catch せず捨てる
> このルール群が実際に検出するもの: Promise 型の式が一切ハンドリングされず文として置かれている箇所

| Linter | Rule | 状態 | ドキュメント |
|---|---|---|---|
| ESLint (core) | — | ❌ Not supported | — |
| typescript-eslint | `@typescript-eslint/no-floating-promises` | ⚠️ Type-aware | https://typescript-eslint.io/rules/no-floating-promises/ |
| oxlint | `typescript/no-floating-promises` | ✅ (型情報部分対応) | https://oxc.rs/docs/guide/usage/linter/rules/typescript/no-floating-promises.html |
| Biome | `noFloatingPromises` | ⚠️ Nursery + Type-aware | https://biomejs.dev/linter/rules/no-floating-promises/ |

### 補足
- 型情報の要否: typescript-eslint / Biome は `parserOptions.project` 相当が必須。oxlint は型情報なしで近似
- 関連ルール（別目的）: `require-await` / `useAwait` は「async を付けたのに本体に await が無い」(async 過剰) の検出
- 別解釈: 「async 過剰」を求めていたなら `require-await` 系
- 出典: mapping table 経由
```
