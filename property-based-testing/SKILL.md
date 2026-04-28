---
name: property-based-testing
description: |
  Property-Based Testing（PBT）の自動設計・実装支援。テスト対象コードを静的分析し、
  プロパティパターン選定・ジェネレータ合成・テストコード生成・実行・レポートを自動実行する。
  フレームワーク自動検出。サブエージェント並列調査。
disable-model-invocation: true
argument-hint: "<target-path> [--focus <focus-area>]"
---

# Property-Based Testing Skill

## CONSTRAINT

```yaml
mode: write  # テストコードを生成・実行する
source_modification: false  # テスト対象のソースコードは変更しない
output_scope: test_files_only
```

## INPUT_SCHEMA

```yaml
arguments: "$ARGUMENTS"
parse_rules:
  - pattern: "^(?<target_path>\\S+)(?:\\s+--focus\\s+(?<focus>.+))?$"
    extract:
      target_path: required  # ファイルパス or モジュール名
      focus: optional        # カンマ区切りの重点観点
  - pattern: "^$"
    action: AskUserQuestion("テスト対象のファイルパスを指定してください")
focus_mapping:
  "境界値|boundary":        [invariant, metamorphic]
  "エラー処理|error":       [invariant, oracle]
  "冪等性|idempotent":      [idempotent]
  "シリアライズ|serialize": [roundtrip]
  "状態|state|stateful":    [stateful]
  "性能|performance":       [oracle, metamorphic]
  "代数|algebraic":         [algebraic]
  "全般|all":               [ALL]
```

## EXECUTION_PIPELINE

```
Phase1:Analyze ──gate:data_ready──▶ Phase2:Design ──gate:plan_ready──▶ Phase3:Generate ──▶ Phase4:Execute ──▶ Phase5:Report
```

各 gate は前フェーズの出力が後フェーズの入力要件を満たすことを検証する内部チェック。ユーザー確認ゲートは不要（自動実行）。

---

## PHASE_1: ANALYZE

### 1.1 サブエージェント起動（並列）

```yaml
parallel_tasks:
  - agent: Task(Explore)
    id: agent_a
    label: "対象コード静的分析"
    prompt: |
      {target_path} を読み込み、以下を構造化して返却せよ:
      1. 全 public 関数/メソッドの一覧
         各エントリ: {name, params: [{name, type, nullable, default}], return_type, is_pure, has_side_effects, mutates_state}
      2. 関数ペア検出: {pairs: [{fn_a, fn_b, relation: "encode/decode"|"serialize/deserialize"|"to/from"|"write/read"}]}
      3. 依存グラフ: {imports, internal_calls, external_calls}
      4. 推定不変条件: [{function, invariant_description}]

  - agent: Task(Explore)
    id: agent_b
    label: "テスト基盤調査"
    prompt: |
      プロジェクトルートから以下を特定せよ:
      1. 言語: {lang: "typescript"|"python"|"rust"|"go"|"java"|"kotlin"|"ruby"}
      2. テストFW: {test_framework, config_file, test_dir_pattern, test_file_pattern}
      3. PBTライブラリ: {pbt_lib: string|null, version: string|null}
      4. 既存テストスタイル: {sample_test_file, assertion_style, describe_pattern}
      5. パッケージマネージャ: {manager, lockfile}
```

### 1.2 フレームワーク解決

```yaml
detection_rules:
  typescript:
    indicators: ["package.json", "tsconfig.json", ".ts files"]
    test_fw_detect:
      - {file: "jest.config.*", result: "jest"}
      - {file: "vitest.config.*", result: "vitest"}
      - {file: "package.json", key: "mocha", result: "mocha"}
    pbt_lib_detect:
      - {package: "fast-check", result: "fast-check"}
    fallback_pbt: "fast-check"
    install_cmd: "npm install --save-dev fast-check"

  python:
    indicators: ["setup.py", "pyproject.toml", "requirements*.txt", ".py files"]
    test_fw_detect:
      - {file: "pytest.ini|pyproject.toml[tool.pytest]|setup.cfg[tool:pytest]", result: "pytest"}
      - {fallback: "unittest"}
    pbt_lib_detect:
      - {package: "hypothesis", result: "hypothesis"}
    fallback_pbt: "hypothesis"
    install_cmd: "pip install hypothesis"

  rust:
    indicators: ["Cargo.toml", ".rs files"]
    test_fw_detect:
      - {builtin: "cargo test", result: "cargo_test"}
    pbt_lib_detect:
      - {dep: "proptest", result: "proptest"}
    fallback_pbt: "proptest"
    install_cmd: 'Cargo.toml に追記: [dev-dependencies] proptest = "1"'

  go:
    indicators: ["go.mod", ".go files"]
    test_fw_detect:
      - {builtin: "go test", result: "go_test"}
    pbt_lib_detect:
      - {module: "pgregory.net/rapid", result: "rapid"}
    fallback_pbt: "rapid"
    install_cmd: "go get pgregory.net/rapid"

  java:
    indicators: ["pom.xml", "build.gradle", ".java files"]
    test_fw_detect:
      - {dep: "junit-jupiter", result: "junit5"}
    pbt_lib_detect:
      - {dep: "jqwik", result: "jqwik"}
    fallback_pbt: "jqwik"
    install_cmd: "pom.xml/build.gradle に jqwik 依存追加"

  kotlin:
    indicators: ["build.gradle.kts", ".kt files"]
    test_fw_detect:
      - {dep: "junit-jupiter|kotest", result: "junit5|kotest"}
    pbt_lib_detect:
      - {dep: "jqwik|kotest-property", result: "jqwik|kotest-property"}
    fallback_pbt: "jqwik"

  ruby:
    indicators: ["Gemfile", ".rb files"]
    test_fw_detect:
      - {gem: "rspec", result: "rspec"}
      - {fallback: "minitest"}
    pbt_lib_detect:
      - {gem: "rantly", result: "rantly"}
      - {gem: "prop_check", result: "prop_check"}
    fallback_pbt: "rantly"
    install_cmd: "Gemfile に追記: gem 'rantly', group: :test"
```

### 1.3 PBTライブラリ未導入時

```
IF pbt_lib == null:
  1. ユーザーに AskUserQuestion で確認:
     "PBTライブラリ {fallback_pbt} が未導入です。インストールしますか？"
     options: ["はい（推奨）", "いいえ（中断）"]
  2. IF "はい": install_cmd を実行
  3. IF "いいえ": 処理中断、理由を報告
```

### 1.4 Phase1 出力スキーマ

```yaml
# gate:data_ready の検証対象
phase1_output:
  functions: [{name, params, return_type, is_pure, has_side_effects, mutates_state}]
  function_pairs: [{fn_a, fn_b, relation}]
  invariants: [{function, description}]
  env:
    lang: string
    test_fw: string
    pbt_lib: string
    test_dir: string
    test_file_pattern: string
    assertion_style: string
  focus_areas: string[] | null  # --focus のパース結果
```

---

## PHASE_2: DESIGN

`references/property-patterns.md` のパターン選定アルゴリズムを適用する。

### 2.1 プロパティ選定アルゴリズム

```
FOR EACH function f IN phase1_output.functions:
  candidates = []

  # Rule 1: Round-trip
  IF ∃ pair(f, g) IN function_pairs WHERE relation ∈ {"encode/decode", "serialize/deserialize", "to/from", "write/read"}:
    candidates.append({pattern: "roundtrip", fn: [f, g], weight: 10})

  # Rule 2: Invariant
  IF f operates on collection OR f has output constraints:
    FOR EACH inv IN known_invariants(f):
      candidates.append({pattern: "invariant", fn: f, invariant: inv, weight: 8})

  # Rule 3: Idempotent
  IF f.return_type == f.params[0].type AND f.is_pure AND f.name matches /normalize|format|clean|trim|canonicalize|dedupe|sanitize/:
    candidates.append({pattern: "idempotent", fn: f, weight: 7})

  # Rule 4: Oracle
  IF ∃ reference_impl(f) IN {stdlib, naive_impl, previous_version}:
    candidates.append({pattern: "oracle", fn: f, oracle: reference_impl, weight: 9})

  # Rule 5: Metamorphic
  IF f is search/query/filter/sort/numeric_computation:
    FOR EACH relation IN metamorphic_relations(f):
      candidates.append({pattern: "metamorphic", fn: f, relation: relation, weight: 6})

  # Rule 6: Algebraic
  IF f is binary_operation AND (associative OR commutative OR has_identity):
    FOR EACH law IN algebraic_laws(f):
      candidates.append({pattern: "algebraic", fn: f, law: law, weight: 5})

  # Rule 7: Stateful
  IF f.mutates_state:
    candidates.append({pattern: "stateful", fn: f, weight: 7})

  # Focus boost
  IF focus_areas != null:
    FOR EACH c IN candidates:
      IF c.pattern IN focus_mapping[focus_area]: c.weight += 5

  # 選定: weight 降順、上位N個（N = min(candidates.length, 5)）
  selected += candidates.sort_by(weight DESC).take(5)
```

### 2.2 プロパティ仕様の構造化

```yaml
# 各選定プロパティの出力フォーマット
property_spec:
  id: "P{seq_number}"
  pattern: "roundtrip|invariant|idempotent|oracle|metamorphic|algebraic|stateful"
  target_functions: [string]
  formal_definition: "∀ x ∈ Gen<T>: postcondition(x)"
  precondition: "assume(x) 条件" | null
  postcondition: "検証する不変条件"
  generator_requirements:
    input_types: [{param_name, type, constraints}]
    edge_cases: [string]
  expected_bug_class: "このプロパティが検出するバグの種類"
  priority: integer  # weight値
```

---

## PHASE_3: GENERATE

`references/generator-patterns.md` と `references/framework-templates.md` を参照。

### 3.1 ジェネレータ合成ルール

```
FOR EACH property IN selected_properties:
  FOR EACH param IN property.generator_requirements.input_types:
    generator = resolve_generator(param)

FUNCTION resolve_generator(param) -> GeneratorExpr:
  MATCH param.type:
    # プリミティブ型 → 組み込み
    "integer"           → gen.integer(param.constraints.min, param.constraints.max)
    "float"             → gen.float(param.constraints.min, param.constraints.max)
    "string"            → gen.string(param.constraints.minLen, param.constraints.maxLen)
    "boolean"           → gen.boolean()

    # コレクション型 → 再帰合成
    "Array<T>"          → gen.array(resolve_generator(T), {minLength, maxLength})
    "Map<K,V>"          → gen.map(resolve_generator(K), resolve_generator(V))
    "Set<T>"            → gen.set(resolve_generator(T))

    # nullable → oneOf合成
    "T | null"          → gen.oneOf(gen.constant(null), resolve_generator(T))
    "T | undefined"     → gen.option(resolve_generator(T))

    # ドメイン型 → record合成
    "Record{fields}"    → gen.record({f.name: resolve_generator(f.type) for f in fields})

    # Union型 → oneOf合成
    "A | B | C"         → gen.oneOf(resolve_generator(A), resolve_generator(B), resolve_generator(C))

    # 列挙型 → constant選択
    "Enum{values}"      → gen.oneOf(...[gen.constant(v) for v in values])

    # 依存型 → flatMap合成
    "Dependent(a, f)"   → resolve_generator(a).flatMap(a_val => f(a_val))

  # エッジケース注入（frequency ラッピング）
  WRAP WITH gen.frequency([
    [75, base_generator],
    [15, edge_case_generator(param.type)],
    [10, extreme_value_generator(param.type)]
  ])
```

### 3.2 テストコード生成

```
PROCEDURE generate_test_code(properties, env):
  template = load_template(env.lang, env.pbt_lib)  # references/framework-templates.md
  style = env.assertion_style
  test_file_path = resolve_test_path(env.test_dir, env.test_file_pattern, target_path)

  code_blocks = []
  FOR EACH prop IN properties:
    code_blocks.append(template.render(
      property_spec=prop,
      generators=prop.generators,
      assertion_style=style
    ))

  output_file = assemble(
    imports=template.imports(env.pbt_lib, target_path),
    body=code_blocks,
    config={numRuns: 100, seed: null, timeout: env.timeout_ms}
  )

  WRITE output_file TO test_file_path
```

### 3.3 シュリンキング品質チェック

```yaml
shrinking_rules:
  - rule: "filter の使用を検出した場合"
    check: "フィルタ通過率 > 10% を推定"
    fix: "map ベースの制約埋め込みに書き換え"
  - rule: "ジェネレータ外での値変換を検出した場合"
    fix: "map でジェネレータ内に移動"
  - rule: "深い flatMap チェーンを検出した場合（depth > 3）"
    fix: "依存を減らすか、中間構造を導入"
```

---

## PHASE_4: EXECUTE

```
PROCEDURE execute_tests(test_file_path, env):
  cmd = MATCH env.lang:
    "typescript" → "{npx|yarn} {jest|vitest} {test_file_path}"
    "python"     → "pytest {test_file_path} -v"
    "rust"       → "cargo test --test {test_name}"
    "go"         → "go test -run {test_func} -v {package}"
    "java"       → "mvn test -Dtest={test_class} | gradle test --tests {test_class}"
    "ruby"       → "bundle exec rspec {test_file_path}"

  result = Bash(cmd)

  IF result.exit_code != 0:
    failures = parse_failures(result.output, env.pbt_lib)
    FOR EACH failure IN failures:
      analysis = classify_failure(failure)
      # analysis.type ∈ {"true_bug", "false_positive", "generator_issue", "timeout"}
      MATCH analysis.type:
        "true_bug"        → record_bug(failure.property, failure.counterexample, failure.shrunk_value)
        "false_positive"  → fix_property(failure.property), re-run
        "generator_issue" → fix_generator(failure.generator), re-run
        "timeout"         → reduce_num_runs(failure.property), re-run
      # re-run は最大2回まで
```

---

## PHASE_5: REPORT

```yaml
report_schema:
  header:
    target: "{target_path}"
    lang: "{env.lang}"
    test_fw: "{env.test_fw} + {env.pbt_lib}"
    num_runs_per_property: integer
    total_execution_time: string

  properties:
    - id: "P1"
      pattern: string
      target_function: string
      formal_definition: string
      result: "PASS|FAIL"
      counterexample: object | null  # FAIL時のみ
      shrunk_value: object | null    # FAIL時のみ

  bugs_found:
    - property_id: string
      severity: "critical|major|minor"
      description: string
      counterexample: object
      shrunk_to: object
      suggested_fix: string | null

  generator_notes:
    - param: string
      strategy: string
      edge_cases_included: [string]
      shrinking_status: "auto|custom|none"

  recommendations:
    - type: "additional_property|generator_extension|coverage_gap"
      description: string
      priority: "high|medium|low"

  test_file: "{test_file_path}"
```

出力は上記スキーマに従った Markdown テーブル形式でユーザーに提示する。

---

## REFERENCE_FILES

```yaml
references:
  - path: "references/property-patterns.md"
    content: "7パターンの形式定義、適用述語、選定スコアリングルール"
  - path: "references/generator-patterns.md"
    content: "型代数に基づくジェネレータ合成規則、エッジケース分布仕様、シュリンキング不変条件"
  - path: "references/framework-templates.md"
    content: "6言語×PBTライブラリのコードテンプレート（検出ルール、import、assertion、config）"
```
