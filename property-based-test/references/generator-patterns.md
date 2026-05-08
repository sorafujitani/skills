# Generator Patterns — 型代数・合成規則・エッジケース分布・シュリンキング不変条件

## COMPOSITION_ALGEBRA

ジェネレータを型代数として定義。各操作は型レベルの変換に対応する。

```
Gen<T>       := 型 T の値を生成するジェネレータ
pure(v)      := Gen<typeof(v)>                     # 定数ジェネレータ
map(g, f)    := Gen<T> → (T → U) → Gen<U>         # 構造保存変換
flatMap(g,f) := Gen<T> → (T → Gen<U>) → Gen<U>    # 依存合成
filter(g, p) := Gen<T> → (T → bool) → Gen<T>      # 条件フィルタ（注意: 非効率の可能性）
oneOf(gs)    := Gen<T>[] → Gen<T>                  # 均等選択
frequency(ws):= [(int, Gen<T>)][] → Gen<T>         # 重み付き選択
record(spec) := {k: Gen<V>} → Gen<{k: V}>          # レコード合成
tuple(gs)    := (Gen<A>, Gen<B>, ...) → Gen<[A, B, ...]>  # タプル合成
array(g, sz) := Gen<T> → SizeSpec → Gen<T[]>       # 配列生成
option(g)    := Gen<T> → Gen<T | null>             # nullable 化
recursive(f) := (Gen<T> → Gen<T>) → DepthLimit → Gen<T>  # 再帰構造
```

---

## TYPE_TO_GENERATOR_RULES

```yaml
resolution_table:
  # === プリミティブ型 ===
  integer:
    generator: "gen.integer({min}, {max})"
    default_range: [-2147483648, 2147483647]
    shrink_toward: 0

  float:
    generator: "gen.float({min}, {max})"
    default_range: [-1e308, 1e308]
    shrink_toward: 0.0
    caveat: "NaN, Infinity は別途 edge_case として注入"

  string:
    generator: "gen.string({minLength}, {maxLength})"
    default_range: [0, 256]
    shrink_toward: '""'
    charset_variants:
      ascii: "gen.string({ascii_printable})"
      unicode: "gen.unicode_string()"
      alphanumeric: "gen.string({alphanumeric})"

  boolean:
    generator: "gen.boolean()"
    shrink_toward: false

  # === コレクション型 ===
  "Array<T>":
    generator: "gen.array(resolve(T), {minLength: 0, maxLength: 50})"
    shrink_toward: "[]"

  "Set<T>":
    generator: "gen.array(resolve(T)).map(unique).map(Set)"
    shrink_toward: "Set([])"

  "Map<K,V>":
    generator: "gen.array(gen.tuple(resolve(K), resolve(V))).map(Map)"
    shrink_toward: "Map([])"

  # === 合成型 ===
  "T | null":
    generator: "gen.option(resolve(T))"
    distribution: "frequency([[85, resolve(T)], [15, pure(null)]])"

  "T | undefined":
    generator: "gen.option(resolve(T))"

  "A | B":
    generator: "gen.oneOf(resolve(A), resolve(B))"

  "A | B | C":
    generator: "gen.oneOf(resolve(A), resolve(B), resolve(C))"

  "Record{f1: T1, f2: T2, ...}":
    generator: "gen.record({f1: resolve(T1), f2: resolve(T2), ...})"

  "Enum{v1, v2, ...}":
    generator: "gen.oneOf(pure(v1), pure(v2), ...)"

  "Tuple<A, B>":
    generator: "gen.tuple(resolve(A), resolve(B))"

  # === 依存型 ===
  "Dependent(a: T, f: T → Gen<U>)":
    generator: "resolve(T).flatMap(a => f(a))"
    example: |
      # 配列の長さに依存するインデックス
      gen.integer(0, 100).flatMap(len =>
        gen.tuple(
          gen.array(gen.integer(), {length: len}),
          gen.integer(0, max(0, len - 1))
        )
      )
```

---

## DOMAIN_GENERATOR_CATALOG

よく使うドメイン固有ジェネレータの合成規則。

```yaml
email:
  structure: "{local}@{domain}.{tld}"
  generator: |
    gen.tuple(
      gen.string({charset: /[a-z0-9._%+-]/, minLength: 1, maxLength: 64}),
      gen.string({charset: /[a-z0-9.-]/, minLength: 1, maxLength: 63}),
      gen.oneOf(pure("com"), pure("org"), pure("net"), pure("co.jp"), pure("io"))
    ).map(([local, domain, tld]) => `${local}@${domain}.${tld}`)

url:
  structure: "{protocol}://{domain}{path}{query}"
  generator: |
    gen.record({
      protocol: gen.oneOf(pure("http"), pure("https")),
      domain: gen.string({charset: /[a-z0-9.-]/, minLength: 3, maxLength: 63}),
      path: gen.array(gen.string({charset: /[a-z0-9-]/, minLength: 1, maxLength: 20}), {maxLength: 5})
              .map(segs => "/" + segs.join("/")),
      query: gen.option(
        gen.array(gen.tuple(gen.string({alphanumeric}), gen.string({alphanumeric})), {maxLength: 5})
          .map(pairs => "?" + pairs.map(([k,v]) => `${k}=${v}`).join("&"))
      )
    }).map(r => `${r.protocol}://${r.domain}${r.path}${r.query ?? ""}`)

date:
  structure: "{year}-{month}-{day}"
  generator: |
    gen.integer(1970, 2100).flatMap(year =>
      gen.integer(1, 12).flatMap(month =>
        gen.integer(1, daysInMonth(year, month)).map(day =>
          new Date(year, month - 1, day)
        )
      )
    )
  note: "flatMap で year → month → day の依存を表現"

money:
  structure: "{amount: integer, currency: string}"
  generator: |
    gen.record({
      currency: gen.oneOf(pure("JPY"), pure("USD"), pure("EUR")),
      amount_major: gen.integer(0, 999_999_999),
      amount_minor: gen.integer(0, 99)
    }).map(r => ({
      amount: r.currency === "JPY"
        ? r.amount_major
        : r.amount_major * 100 + r.amount_minor,
      currency: r.currency
    }))

json_value:
  structure: "recursive JSON"
  generator: |
    recursive(self => gen.oneOf(
      gen.string(),
      gen.integer(),
      gen.float(),
      gen.boolean(),
      pure(null),
      gen.array(self, {maxLength: 5}),
      gen.record_dynamic(gen.string(), self, {maxKeys: 5})
    ), {maxDepth: 4})
```

---

## EDGE_CASE_INJECTION

各型のエッジケース値と注入分布。

```yaml
edge_case_registry:
  integer:
    values: [0, 1, -1, 2, -2, MAX_INT, MIN_INT, MAX_SAFE_INTEGER, MIN_SAFE_INTEGER]
    injection_weight: 15  # frequency 中の重み（%）

  float:
    values: [0.0, -0.0, 1.0, -1.0, 0.1, 0.01, MAX_FLOAT, MIN_FLOAT, NaN, Infinity, -Infinity, "epsilon"]
    injection_weight: 15

  string:
    values:
      empty: '""'
      single_char: '"a"'
      long: '"a".repeat(10000)'
      unicode: ['"🎉"', '"漢字"', '"é"', '"👨‍👩‍👧‍👦"']
      control: ['"\0"', '"\n"', '"\r\n"', '"\t"']
      injection: ['"<script>"', "\"'; DROP TABLE\"", '"../../../etc/passwd"']
      whitespace: ['" "', '"  "', '" trim_me "']
    injection_weight: 20

  array:
    values:
      empty: "[]"
      single: "[x]"
      duplicates: "[a, a, a]"
      sorted_asc: "sorted(xs)"
      sorted_desc: "sorted(xs).reverse()"
      nested: "[[[]]]"
    injection_weight: 15

  object:
    values:
      empty: "{}"
      proto_pollution: '{"__proto__": {}, "constructor": {}, "toString": {}}'
      empty_key: '{"": "value"}'
      deep_nested: "{a: {b: {c: {d: {e: {}}}}}}"
    injection_weight: 10

  null_undefined:
    values: ["null", "undefined"]
    injection_context: "nullable な型パラメータに対してのみ注入"
    injection_weight: 15

# 合成時の分布テンプレート
distribution_template: |
  frequency([
    [{100 - edge_weight - extreme_weight}, base_generator],
    [{edge_weight}, oneOf(...edge_case_values)],
    [{extreme_weight}, extreme_value_generator]
  ])
  WHERE:
    edge_weight = edge_case_registry[type].injection_weight
    extreme_weight = 5  # 固定
```

---

## SHRINKING_INVARIANTS

シュリンキング品質を保証するためのルール。

```yaml
invariants:
  I1_no_external_transform:
    rule: "値変換は必ず gen.map() 内で行う"
    violation: "ジェネレータ外で生成値を変換している"
    fix: "変換ロジックを map() に移動"
    reason: "シュリンカーが変換を認識できず、シュリンク後の値が不正になる"

  I2_filter_efficiency:
    rule: "filter の通過率 > 10%"
    violation: "filter 条件が厳しすぎる（通過率 < 10%）"
    fix: "map ベースで制約を構造的に埋め込む"
    example: |
      # BAD: gen.integer().filter(n => n % 2 === 0)  — 通過率 50% は OK だが...
      # BAD: gen.integer().filter(n => isPrime(n))     — 通過率 << 10%
      # GOOD: gen.integer().map(n => n * 2)            — 偶数を直接生成
      # GOOD: gen.integer(1, 1000).map(nthPrime)       — 素数を直接生成

  I3_flatmap_depth:
    rule: "flatMap チェーン深さ ≤ 3"
    violation: "深い flatMap チェーンでシュリンク空間が爆発"
    fix: "中間構造を導入して分割するか、record 合成に書き換え"

  I4_framework_compatibility:
    rule: "フレームワーク推奨の合成APIを使用"
    mapping:
      fast-check: "map / chain / filter は自動シュリンキング対応"
      hypothesis: "@composite + draw() ベース。assume() で前提条件"
      proptest: "prop_compose! マクロ で合成"
      rapid: "Custom() + Draw() パターン"
      jqwik: "@Provide + Arbitraries チェーン"
      rantly: "Rantly ブロック内で guard() で前提条件"

validation_checklist:
  - "[ ] ドメインの有効値を網羅的に生成可能"
  - "[ ] 無効値は filter でなく map で構造的に排除"
  - "[ ] edge_case_registry の値が frequency で注入済み"
  - "[ ] シュリンキングが正しく動作（I1〜I4 準拠）"
  - "[ ] 生成効率 OK（filter 通過率 > 10%）"
  - "[ ] 再帰構造に深さ制限あり"
  - "[ ] テスト実行時間が許容範囲内"
```
