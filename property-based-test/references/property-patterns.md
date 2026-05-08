# Property Patterns — 形式定義・適用述語・スコアリング

## PATTERN_REGISTRY

各パターンを `{id, formal_def, applicability_predicate, score_base, variants, bug_class, caveats}` で定義する。

---

### P01: ROUNDTRIP

```yaml
id: roundtrip
formal_def: "∀ x ∈ Gen<T>: g(f(x)) ≡ x"
  # f: encoder/serializer, g: decoder/deserializer
  # ≡: 構造的等価（deep equal）

applicability_predicate: |
  ∃ (f, g) IN codebase WHERE:
    f: T → U ∧ g: U → T ∧
    relation(f, g) ∈ {
      "encode/decode", "serialize/deserialize", "marshal/unmarshal",
      "to/from", "parse/format", "compress/decompress",
      "toJSON/fromJSON", "toString/fromString", "write/read",
      "encrypt/decrypt", "pack/unpack"
    }

score_base: 10

variants:
  - id: "roundtrip_lossy"
    condition: "f は非可逆変換（情報損失あり）"
    formal_def: "∀ x ∈ Gen<T>: g(f(x)) ≡ normalize(x)"
    note: "正規化後の値で比較"
  - id: "roundtrip_approx"
    condition: "浮動小数点を含む"
    formal_def: "∀ x ∈ Gen<T>: |g(f(x)) - x| < ε"
    note: "近似等価、ε は精度要件に依存"

bug_class:
  - "エンコーディング不整合"
  - "パース漏れ（特殊文字、Unicode、エスケープ）"
  - "データ損失（切り捨て、オーバーフロー）"
  - "型変換エラー"

caveats:
  - "浮動小数点 → approx variant を使用"
  - "正規化あり → lossy variant を使用"
  - "非可逆変換 → 適用不可"
```

---

### P02: INVARIANT

```yaml
id: invariant
formal_def: "∀ x ∈ Gen<T>: φ(f(x)) ∧ ψ(x, f(x))"
  # φ: 出力に対する述語（型、値域、構造）
  # ψ: 入出力間の関係述語（サイズ保存、要素保存等）

applicability_predicate: |
  f: T → U WHERE:
    (∃ measurable_property(U) that should be preserved) ∨
    (f operates on collection: sort, filter, map, group, partition, dedupe) ∨
    (f has documented output constraints: range, format, type)

score_base: 8

subtypes:
  - id: "size_preservation"
    formal_def: "∀ xs ∈ Gen<T[]>: |f(xs)| = |xs|"
    applies_to: "sort, shuffle, map, reverse"
  - id: "element_preservation"
    formal_def: "∀ xs ∈ Gen<T[]>: multiset(f(xs)) = multiset(xs)"
    applies_to: "sort, shuffle, reverse"
  - id: "ordering"
    formal_def: "∀ xs ∈ Gen<T[]>, ∀ i < |f(xs)|-1: f(xs)[i] ≤ f(xs)[i+1]"
    applies_to: "sort"
  - id: "range_bound"
    formal_def: "∀ x ∈ Gen<T>: lo ≤ f(x) ≤ hi"
    applies_to: "clamp, normalize_to_range, percentage"
  - id: "type_preservation"
    formal_def: "∀ x ∈ Gen<T>: typeof(f(x)) = expected_type"
    applies_to: "any function with typed return"
  - id: "subset"
    formal_def: "∀ xs ∈ Gen<T[]>: set(f(xs)) ⊆ set(xs)"
    applies_to: "filter, search, select"
  - id: "non_empty"
    formal_def: "∀ x ∈ Gen<T> WHERE precondition(x): f(x) ≠ empty"
    applies_to: "required field validation, non-null guarantees"

bug_class:
  - "要素の消失/重複"
  - "範囲外の値"
  - "型の不一致"
  - "コレクション長の変化"
```

---

### P03: IDEMPOTENT

```yaml
id: idempotent
formal_def: "∀ x ∈ Gen<T>: f(f(x)) ≡ f(x)"

applicability_predicate: |
  f: T → T WHERE:
    f.is_pure ∧
    f.name MATCHES /(normalize|format|clean|trim|strip|canonicalize|
                     dedupe|dedup|sanitize|prettify|minify|compact|
                     flatten|resolve|simplify|standardize)/ ∨
    f is HTTP_PUT handler ∨
    f is cache_operation ∨
    f is config_apply ∨
    f is cleanup_operation

score_base: 7

variants:
  - id: "idempotent_n"
    formal_def: "∀ x ∈ Gen<T>, ∀ n ≥ 1: f^n(x) ≡ f(x)"
    note: "n=3 まで検証すれば十分"
  - id: "idempotent_projection"
    formal_def: "∀ x ∈ Gen<T>: f(f(x)) ≡ f(x) ∧ f(x) is_canonical_form"

bug_class:
  - "二重適用によるデータ破壊"
  - "フォーマット不安定性（適用ごとに結果が変化）"
  - "エスケープの多重適用"
  - "正規化の不完全性"
```

---

### P04: ORACLE

```yaml
id: oracle
formal_def: "∀ x ∈ Gen<T>: f(x) ≡ oracle(x)"
  # f: テスト対象（最適化版）
  # oracle: 参照実装（素朴版/標準ライブラリ/旧版）

applicability_predicate: |
  ∃ oracle_function WHERE:
    oracle ∈ {
      stdlib_equivalent(f),    # 標準ライブラリに同等関数
      naive_implementation(f), # 素朴な実装が書ける
      previous_version(f),     # リファクタリング前の旧実装
      parallel_version(f)      # 逐次版 vs 並列版
    } ∧
    oracle is_trusted

score_base: 9

variants:
  - id: "oracle_set_equal"
    formal_def: "∀ x ∈ Gen<T>: set(f(x)) = set(oracle(x))"
    condition: "出力の順序が非決定的"
  - id: "oracle_approx"
    formal_def: "∀ x ∈ Gen<T>: |f(x) - oracle(x)| < ε"
    condition: "浮動小数点精度の差異がある"

bug_class:
  - "最適化によるコーナーケース見落とし"
  - "リファクタリングリグレッション"
  - "アルゴリズム変更時の等価性破壊"
```

---

### P05: METAMORPHIC

```yaml
id: metamorphic
formal_def: "∀ x ∈ Gen<T>: R(f(x), f(transform(x)))"
  # R: 出力間の関係（⊆, =, ≤, ≥）
  # transform: 入力変換

applicability_predicate: |
  f: T → U WHERE:
    (oracle(f) does not exist) ∧
    (∃ input_transform t: T → T, ∃ output_relation R: U × U → bool,
     such that ∀ x: R(f(x), f(t(x))) holds)

  # 典型的な適用先
  f IS {search_function, query_function, filter_function,
        numeric_computation, ML_prediction, distance_metric,
        pricing_function, ranking_function}

score_base: 6

relation_catalog:
  - id: "subset_restriction"
    transform: "add_constraint(x)"
    relation: "f(transform(x)) ⊆ f(x)"
    example: "search(db, q1 AND q2) ⊆ search(db, q1)"
  - id: "linearity"
    transform: "scale(x, k)"
    relation: "f(transform(x)) = k * f(x)"
  - id: "symmetry"
    transform: "swap(x)"
    relation: "f(transform(x)) = f(x)"
    example: "distance(a, b) = distance(b, a)"
  - id: "monotonicity"
    transform: "increase(x)"
    relation: "f(transform(x)) ≥ f(x)"
  - id: "permutation_invariance"
    transform: "permute(x)"
    relation: "f(transform(x)) = f(x)"
    example: "set_union(permute(xs)) = set_union(xs)"
  - id: "negation"
    transform: "negate(x)"
    relation: "f(transform(x)) = -f(x) ∨ f(transform(x)) = complement(f(x))"

bug_class:
  - "検索漏れ"
  - "数値計算精度問題"
  - "対称性の破壊"
  - "単調性違反"
```

---

### P06: ALGEBRAIC

```yaml
id: algebraic
formal_def: |
  以下のいずれか（複数適用可）:
  associativity: ∀ a,b,c ∈ Gen<T>: f(f(a,b), c) ≡ f(a, f(b,c))
  commutativity: ∀ a,b ∈ Gen<T>: f(a,b) ≡ f(b,a)
  identity:      ∀ a ∈ Gen<T>: f(a, e) ≡ a ∧ f(e, a) ≡ a
  distributivity: ∀ a,b,c ∈ Gen<T>: f(a, g(b,c)) ≡ g(f(a,b), f(a,c))
  inverse:       ∀ a ∈ Gen<T>: f(a, inv(a)) ≡ e

applicability_predicate: |
  f: T × T → T WHERE:
    f IS binary_operation ∧
    (f IS {merge, concat, union, intersect, compose, add, multiply,
           combine, append, join, zip, reduce} ∨
     f operates on monoid/group/ring structure)

score_base: 5

law_detection:
  - check: "f(a, f(b, c)) = f(f(a, b), c)"
    law: "associativity"
  - check: "f(a, b) = f(b, a)"
    law: "commutativity"
  - check: "∃ e: f(a, e) = a"
    law: "identity"
    identity_candidates: ["0", "1", "[]", "{}", '""', "null", "empty()"]

bug_class:
  - "結合順序依存バグ"
  - "空入力の処理漏れ（identity 破壊）"
  - "結合操作の非結合性"
```

---

### P07: STATEFUL

```yaml
id: stateful
formal_def: |
  ∀ cmd_sequence ∈ Gen<Cmd[]>:
    LET model_state = apply_sequence(model, cmd_sequence)
    LET real_state  = apply_sequence(real,  cmd_sequence)
    model_state ≡ real_state

applicability_predicate: |
  target IS stateful_object WHERE:
    target.mutates_state = true ∧
    target HAS {multiple_operations, state_transitions} ∧
    target IS {data_structure, database_wrapper, file_system_api,
               protocol_impl, state_machine, session_manager,
               cache, connection_pool, queue, stack, map}

score_base: 7

modeling_procedure:
  1: "対象の public API からコマンド集合 Cmd を列挙"
  2: "各 Cmd の事前条件（precondition）を定義"
  3: "簡易モデル（例: 配列ベース）を実装"
  4: "ランダムコマンド列生成 → 実装とモデル両方に適用 → 各ステップで状態比較"

bug_class:
  - "状態遷移不整合"
  - "リソースリーク"
  - "並行性バグ"
  - "境界状態（空/満/初期化前）での不正動作"
```

---

## SELECTION_ALGORITHM

```
INPUT:  functions: FunctionInfo[], focus_areas: string[] | null
OUTPUT: selected_properties: PropertySpec[]

PROCEDURE select_properties(functions, focus_areas):
  all_candidates = []

  FOR EACH f IN functions:
    # Phase A: 各パターンの適用判定（述語評価）
    IF roundtrip.applicability_predicate(f):
      all_candidates.append({pattern: "roundtrip", fn: f, score: 10})

    IF invariant.applicability_predicate(f):
      FOR EACH subtype IN invariant.subtypes WHERE subtype.applies_to MATCHES f:
        all_candidates.append({pattern: "invariant", fn: f, subtype: subtype.id, score: 8})

    IF idempotent.applicability_predicate(f):
      all_candidates.append({pattern: "idempotent", fn: f, score: 7})

    IF oracle.applicability_predicate(f):
      all_candidates.append({pattern: "oracle", fn: f, score: 9})

    IF metamorphic.applicability_predicate(f):
      FOR EACH rel IN metamorphic.relation_catalog WHERE rel MATCHES f:
        all_candidates.append({pattern: "metamorphic", fn: f, relation: rel.id, score: 6})

    IF algebraic.applicability_predicate(f):
      FOR EACH law IN algebraic.law_detection WHERE law MATCHES f:
        all_candidates.append({pattern: "algebraic", fn: f, law: law.law, score: 5})

    IF stateful.applicability_predicate(f):
      all_candidates.append({pattern: "stateful", fn: f, score: 7})

  # Phase B: focus boost
  IF focus_areas != null:
    FOR EACH c IN all_candidates:
      IF c.pattern IN SKILL.md#focus_mapping[focus_area]:
        c.score += 5

  # Phase C: 重複排除 & ソート
  deduplicated = remove_redundant(all_candidates)  # 同一関数×同一パターンの重複除去
  sorted = deduplicated.sort_by(score DESC)

  # Phase D: 上限適用
  RETURN sorted.take(min(sorted.length, 15))  # 最大15プロパティ
```
