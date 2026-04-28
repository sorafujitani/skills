# Framework Templates — 検出ルール・構造化テンプレート・設定仕様

## TEMPLATE_SCHEMA

各フレームワークテンプレートは以下の構造に従う:

```yaml
template:
  lang: string
  pbt_lib: string
  install: {cmd: string, file_edit: string | null}
  imports: string          # テストファイル先頭の import 文
  config: {key: value}     # 実行設定のデフォルト値
  patterns:                # パターン別テストコード骨格
    roundtrip: string
    invariant: string
    idempotent: string
    oracle: string
    metamorphic: string
    algebraic: string
    stateful: string
  custom_generator: string # カスタムジェネレータの書き方
  output_path_rule: string # テストファイルの配置規則
```

---

## T01: TypeScript/JavaScript — fast-check

```yaml
lang: typescript
pbt_lib: fast-check
install:
  cmd: "npm install --save-dev fast-check"
  alt: "yarn add -D fast-check"

imports: |
  import fc from 'fast-check';
  import { /* target functions */ } from '{target_module_path}';

config:
  numRuns: 100
  seed: null            # null = ランダム、整数 = 再現用
  endOnFailure: true
  verbose: 1            # 0: silent, 1: on failure, 2: all
  timeout: 5000         # ms

output_path_rule: |
  IF exists("__tests__/"): "__tests__/{target_name}.pbt.test.ts"
  ELIF test_file_pattern == "*.spec.ts": "{target_dir}/{target_name}.pbt.spec.ts"
  ELSE: "{target_dir}/{target_name}.pbt.test.ts"

patterns:
  roundtrip: |
    it('roundtrip: decode(encode(x)) === x', () => {
      fc.assert(
        fc.property({generator}, (input) => {
          expect({decode}({encode}(input))).toEqual(input);
        }),
        { numRuns: {numRuns} }
      );
    });

  invariant: |
    it('invariant: {invariant_description}', () => {
      fc.assert(
        fc.property({generator}, (input) => {
          const result = {target_fn}(input);
          expect({assertion}).toBe(true);
        }),
        { numRuns: {numRuns} }
      );
    });

  idempotent: |
    it('idempotent: f(f(x)) === f(x)', () => {
      fc.assert(
        fc.property({generator}, (input) => {
          const once = {target_fn}(input);
          const twice = {target_fn}(once);
          expect(twice).toEqual(once);
        }),
        { numRuns: {numRuns} }
      );
    });

  oracle: |
    it('oracle: optimized === reference', () => {
      fc.assert(
        fc.property({generator}, (input) => {
          expect({target_fn}(input)).toEqual({oracle_fn}(input));
        }),
        { numRuns: {numRuns} }
      );
    });

  metamorphic: |
    it('metamorphic: {relation_description}', () => {
      fc.assert(
        fc.property({generator}, (input) => {
          const original = {target_fn}(input);
          const transformed = {target_fn}({transform}(input));
          expect({relation_assertion}).toBe(true);
        }),
        { numRuns: {numRuns} }
      );
    });

  algebraic: |
    it('algebraic: {law_name}', () => {
      fc.assert(
        fc.property({generator_a}, {generator_b}, {generator_c}, (a, b, c) => {
          // e.g., associativity
          expect({target_fn}({target_fn}(a, b), c)).toEqual({target_fn}(a, {target_fn}(b, c)));
        }),
        { numRuns: {numRuns} }
      );
    });

  stateful: |
    // Model-based test
    class {Model}Model {
      state: {ModelState} = {initial_state};
      {model_methods}
    }

    const commands = [
      {command_definitions}
    ];

    it('stateful: matches model', () => {
      fc.assert(
        fc.property(fc.commands(commands, { maxCommands: 100 }), (cmds) => {
          const model = new {Model}Model();
          const real = new {RealImpl}();
          fc.modelRun(() => ({ model, real }), cmds);
        }),
        { numRuns: {numRuns} }
      );
    });

custom_generator: |
  // record 合成
  const {name}Gen = fc.record({
    {field_name}: {field_generator},
    // ...
  });

  // flatMap（依存合成）
  const dependentGen = {base_gen}.chain(baseVal =>
    {dependent_gen_factory}(baseVal)
  );

  // frequency（エッジケース注入）
  const withEdgeCases = fc.frequency(
    { weight: 75, arbitrary: {base_gen} },
    { weight: 15, arbitrary: fc.constantFrom({edge_values}) },
    { weight: 10, arbitrary: {extreme_gen} }
  );
```

---

## T02: Python — hypothesis

```yaml
lang: python
pbt_lib: hypothesis
install:
  cmd: "pip install hypothesis"
  alt: "poetry add --group dev hypothesis"

imports: |
  from hypothesis import given, assume, settings, HealthCheck
  from hypothesis import strategies as st
  from {target_module} import {target_functions}

config:
  max_examples: 100
  deadline: null          # None = no timeout
  suppress_health_check: [HealthCheck.too_slow]
  database: null          # None = disable example DB

output_path_rule: |
  IF exists("tests/"): "tests/test_{target_name}_pbt.py"
  ELSE: "test_{target_name}_pbt.py"

patterns:
  roundtrip: |
    @given(st.{strategy}())
    def test_roundtrip(input_val):
        assert {decode}({encode}(input_val)) == input_val

  invariant: |
    @given(st.{strategy}())
    def test_{invariant_name}(input_val):
        result = {target_fn}(input_val)
        assert {assertion}

  idempotent: |
    @given(st.{strategy}())
    def test_idempotent(input_val):
        once = {target_fn}(input_val)
        twice = {target_fn}(once)
        assert twice == once

  oracle: |
    @given(st.{strategy}())
    def test_oracle(input_val):
        assert {target_fn}(input_val) == {oracle_fn}(input_val)

  metamorphic: |
    @given(st.{strategy}())
    def test_metamorphic_{relation}(input_val):
        original = {target_fn}(input_val)
        transformed = {target_fn}({transform}(input_val))
        assert {relation_assertion}

  algebraic: |
    @given(st.{strategy}(), st.{strategy}(), st.{strategy}())
    def test_{law_name}(a, b, c):
        assert {target_fn}({target_fn}(a, b), c) == {target_fn}(a, {target_fn}(b, c))

  stateful: |
    from hypothesis.stateful import RuleBasedStateMachine, rule, precondition

    class {Model}Machine(RuleBasedStateMachine):
        def __init__(self):
            super().__init__()
            self.model = {initial_model}
            self.real = {RealImpl}()

        {rule_methods}

    Test{Model} = {Model}Machine.TestCase

custom_generator: |
  # builds で合成
  {name}_strategy = st.builds(
      {TargetClass},
      {field_name}=st.{field_strategy}(),
  )

  # composite で依存合成
  @st.composite
  def {name}_strategy(draw):
      {base} = draw(st.{base_strategy}())
      {dependent} = draw(st.{dependent_strategy}({base}))
      return {constructor}({base}, {dependent})

  # one_of でエッジケース注入
  {name}_with_edges = st.one_of(
      st.{base_strategy}(),
      st.sampled_from([{edge_values}])
  )
```

---

## T03: Rust — proptest

```yaml
lang: rust
pbt_lib: proptest
install:
  file_edit: |
    # Cargo.toml
    [dev-dependencies]
    proptest = "1"

imports: |
  use proptest::prelude::*;
  use super::{target_items};

config:
  cases: 100
  max_shrink_iters: 10000

output_path_rule: |
  IF exists("tests/"): "tests/{target_name}_pbt.rs"
  ELSE: "src/{target_module}.rs 内の #[cfg(test)] mod tests"

patterns:
  roundtrip: |
    proptest! {
        #[test]
        fn roundtrip(input in {strategy}) {
            let encoded = {encode}(&input);
            let decoded = {decode}(&encoded);
            prop_assert_eq!(decoded, input);
        }
    }

  invariant: |
    proptest! {
        #[test]
        fn {invariant_name}(input in {strategy}) {
            let result = {target_fn}(&input);
            prop_assert!({assertion});
        }
    }

  idempotent: |
    proptest! {
        #[test]
        fn idempotent(input in {strategy}) {
            let once = {target_fn}(&input);
            let twice = {target_fn}(&once);
            prop_assert_eq!(once, twice);
        }
    }

  oracle: |
    proptest! {
        #[test]
        fn oracle(input in {strategy}) {
            prop_assert_eq!({target_fn}(&input), {oracle_fn}(&input));
        }
    }

custom_generator: |
  // prop_compose! で合成
  prop_compose! {
      fn {name}_strategy()(
          {field_name} in {field_strategy},
      ) -> {TargetType} {
          {TargetType} { {field_name} }
      }
  }

  // prop_oneof! でエッジケース
  fn {name}_with_edges() -> impl Strategy<Value = {Type}> {
      prop_oneof![
          8 => {base_strategy},
          2 => prop::sample::select(vec![{edge_values}]),
      ]
  }
```

---

## T04: Go — rapid

```yaml
lang: go
pbt_lib: rapid
install:
  cmd: "go get pgregory.net/rapid"

imports: |
  import (
      "testing"
      "pgregory.net/rapid"
  )

config:
  # rapid は go test の -count フラグで実行回数制御
  # rapid.Check 内部でデフォルト 100 回

output_path_rule: "{target_dir}/{target_name}_pbt_test.go"

patterns:
  roundtrip: |
    func TestRoundtrip(t *testing.T) {
        rapid.Check(t, func(t *rapid.T) {
            input := {generator}.Draw(t, "input")
            encoded := {Encode}(input)
            decoded := {Decode}(encoded)
            if !reflect.DeepEqual(decoded, input) {
                t.Fatalf("roundtrip failed: %v -> %v -> %v", input, encoded, decoded)
            }
        })
    }

  invariant: |
    func Test{InvariantName}(t *testing.T) {
        rapid.Check(t, func(t *rapid.T) {
            input := {generator}.Draw(t, "input")
            result := {TargetFn}(input)
            if !({assertion}) {
                t.Fatalf("invariant violated: input=%v result=%v", input, result)
            }
        })
    }

  idempotent: |
    func TestIdempotent(t *testing.T) {
        rapid.Check(t, func(t *rapid.T) {
            input := {generator}.Draw(t, "input")
            once := {TargetFn}(input)
            twice := {TargetFn}(once)
            if !reflect.DeepEqual(once, twice) {
                t.Fatalf("not idempotent: once=%v twice=%v", once, twice)
            }
        })
    }

  stateful: |
    func TestStateful(t *testing.T) {
        rapid.Check(t, func(t *rapid.T) {
            model := {NewModel}()
            real := {NewReal}()
            rapid.Repeat(t, func(t *rapid.T) {
                action := rapid.SampledFrom([]string{ {actions} }).Draw(t, "action")
                switch action {
                {switch_cases}
                }
            })
        })
    }

custom_generator: |
  // Custom ジェネレータ
  func {name}Generator() *rapid.Generator[{Type}] {
      return rapid.Custom(func(t *rapid.T) {Type} {
          return {Type}{
              {FieldName}: {field_generator}.Draw(t, "{field_name}"),
          }
      })
  }
```

---

## T05: Java/Kotlin — jqwik

```yaml
lang: java
pbt_lib: jqwik
install:
  file_edit: |
    <!-- pom.xml -->
    <dependency>
        <groupId>net.jqwik</groupId>
        <artifactId>jqwik</artifactId>
        <version>1.8.0</version>
        <scope>test</scope>
    </dependency>

imports: |
  import net.jqwik.api.*;
  import static org.assertj.core.api.Assertions.*;

config:
  tries: 100
  seed: ""  # empty = random

output_path_rule: "src/test/java/{package_path}/{TargetName}PbtTest.java"

patterns:
  roundtrip: |
    @Property
    void roundtrip(@ForAll {ParamType} input) {
        assertThat({decode}({encode}(input))).isEqualTo(input);
    }

  invariant: |
    @Property
    void {invariantName}(@ForAll {ParamType} input) {
        var result = {targetFn}(input);
        assertThat({assertion}).isTrue();
    }

  idempotent: |
    @Property
    void idempotent(@ForAll {ParamType} input) {
        var once = {targetFn}(input);
        var twice = {targetFn}(once);
        assertThat(twice).isEqualTo(once);
    }

custom_generator: |
  @Provide
  Arbitrary<{Type}> {name}s() {
      return Combinators.combine(
          Arbitraries.{field1_arb}(),
          Arbitraries.{field2_arb}()
      ).as({Type}::new);
  }

  // エッジケース注入
  @Provide
  Arbitrary<{Type}> {name}WithEdges() {
      return Arbitraries.frequencyOf(
          Tuple.of(8, {base_arb}),
          Tuple.of(2, Arbitraries.of({edge_values}))
      );
  }
```

---

## T06: Ruby — rantly

```yaml
lang: ruby
pbt_lib: rantly
install:
  file_edit: |
    # Gemfile
    gem 'rantly', group: :test

  cmd: "bundle install"

imports: |
  require 'rantly'
  require 'rantly/rspec_extensions'

config:
  # Rantly デフォルト: 100 回
  # .check(N) で変更可能

output_path_rule: |
  IF exists("spec/"): "spec/{target_name}_pbt_spec.rb"
  ELSE: "test/{target_name}_pbt_test.rb"

patterns:
  roundtrip: |
    it 'roundtrip: decode(encode(x)) == x' do
      property_of {
        {generator}
      }.check { |input|
        expect({decode}({encode}(input))).to eq(input)
      }
    end

  invariant: |
    it '{invariant_description}' do
      property_of {
        {generator}
      }.check { |input|
        result = {target_fn}(input)
        expect({assertion}).to be true
      }
    end

  idempotent: |
    it 'idempotent: f(f(x)) == f(x)' do
      property_of {
        {generator}
      }.check { |input|
        once = {target_fn}(input)
        twice = {target_fn}(once)
        expect(twice).to eq(once)
      }
    end

custom_generator: |
  # Rantly ブロック内で合成
  property_of {
    Rantly {
      {
        {field_name}: {field_generator},
      }
    }
  }

  # guard で前提条件
  property_of {
    n = integer
    guard n != 0
    n
  }
```
