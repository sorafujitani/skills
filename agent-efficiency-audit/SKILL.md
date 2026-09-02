---
name: agent-efficiency-audit
description: Audit local agent session logs (Codex, Claude Code, Grok, pi) to find where the token budget actually went, then tell the user what to change. Use when a weekly/usage limit burned unexpectedly fast, when the user asks why token consumption is high, whether they are using agents efficiently, which sessions or skills are expensive, or wants a usage/cost review across harnesses.
---

# agent-efficiency-audit

Answer one question with evidence: **is this person driving agents efficiently, and if not, what exactly should change?**

Never guess from the conversation. Read the logs.

## Core model

A **turn** is one model inference call, not one user message. LLMs are stateless, so every turn re-sends the entire context: system prompt + full history + every tool output so far.

Consequences that drive every finding here:

- Cost scales with the **square** of turn count, not linearly. $\sum_{i=1}^{n}(C_0 + i\,d) = O(n^2)$.
- A tool call returning 250 tokens still bills the whole 130k context.
- Anything read into context is **re-billed on every later turn**. A 10k-token skill read at turn 50 of 800 costs 7.5M, not 10k.
- Cache discounts the price but the tokens are still counted against rate limits.

So the expensive thing is almost never output. It is context that was loaded early and carried far.

## Workflow

1. Establish the window. For a rate-limit complaint, use the real quota window, not a guess:

   ```sh
   python3 scripts/audit.py burn --source codex --days 14
   ```

   Codex records `rate_limits.primary` (`used_percent`, `window_minutes`, `resets_at`) on every turn. This is authoritative. Other harnesses have no equivalent — for those, fall back to `--days`.

   For a live Codex session, check whether to hand off before starting another phase:

   ```sh
   python3 scripts/audit.py guard --source codex --days 1
   ```

   `last_context` is the latest recorded model input. `compacts` is the number of `context_compacted` events in the session. `HANDOFF` means finish the current atomic step and continue from a compact resume note in a new session.

2. Get the overall picture and automatic diagnosis:

   ```sh
   python3 scripts/audit.py summary --since 2026-08-05T10:58:53
   python3 scripts/audit.py summary --source claude --days 7
   ```

3. Deep-dive the top consumer. Do this before concluding anything:

   ```sh
   python3 scripts/audit.py session <cwd-or-id-substring> --days 7
   ```

4. Cross-cut when the diagnosis points at documents or repetition:

   ```sh
   python3 scripts/audit.py carry --days 7    # what sat in context and for how long
   python3 scripts/audit.py dupes --days 7    # files read again while already in context
   ```

5. If the user also asks about work quality, report it separately from token efficiency. Cost logs do not measure correctness. Use bounded proxies: direct user corrections, failed verification/rework, and reviewer → fixer → verifier artifacts. Prefer structured result files and sampled top sessions over delegating an unbounded archive scan. State that these measure final-gate effectiveness, not initial model accuracy.
6. Report in Japanese. Lead with the conclusion, then the numbers, then named fixes.

## What to look for

| 症状 | 閾値 | 意味 |
| --- | --- | --- |
| ctx 中央値 | > 100k | セッションを畳んでいない。二乗コストの本体 |
| turns / 指示 | > 20 | 探索が発散。スコープが曖昧なまま着手した |
| 出力比率 | < 2% | 消費はコンテキスト再送。出力を削っても無意味 |
| carry cost | > 10% | 常駐ドキュメントが重い。読み方の問題 |
| 同一ファイル再読 | >= 3x | すでにコンテキストにあるものを読み直している |
| ポーリング系 tool | > 2% | 新情報ゼロのターンに全コンテキストを課金 |
| compact 回数 | >= 2 | 次のphaseを同じ会話で始めない。resume noteから新セッションへ |
| subagent 合計 | > 10% | 親と重複探索、または渡す文脈が過剰 |

## Reporting rules

- **原因を機構で説明する。** 「トークンが多い」では行動が変わらない。「skill を指示ごとに読み直し、それが以後 600 turn 再送された」まで言う。
- **直す場所をファイル名で指す。** `~/.claude/CLAUDE.md` のこの行、`~/.codex/config.toml` のこの設定、というレベルまで。
- **相関を因果と偽らない。** 「skill 起動ありのほうが turn が多い」は、複雑なタスクで起動するルールなら当たり前。交絡は交絡と書く。
- **効果は測れないと認める。** このツールはコストしか見ない。skill や playbook が判断の質を上げたかはログからは出ない。コスト面だけの評価だと明示する。
- 週次の伸びが妥当かは `burn` の到達曲線で示す。何時に何%だったかを並べると、どの作業が枠を食ったか一目で分かる。

## Known approximations

- `carry cost` = 読み込みバイト数 ÷ 4 × 以降の残り turn 数。トークナイザではなくバイト数近似。compact でコンテキストから消えた分は差し引かれないので、compact が多いセッションでは過大に出る。
- ファイルパスは tool 入力からの正規表現抽出。1 回の呼び出しで複数ファイルを読んだ場合、出力バイト数を等分して按分する。
- Codex / Claude Code は tool 単位まで追える。Grok と pi は turn 集計は正確だが tool 属性は best-effort。
- Claude Code の `total` は `input + cache_creation + cache_read + output`。Codex の `total_tokens` とは定義が揃っているが、課金レートは揃っていない。**ハーネスをまたいだトークン数の直接比較はしない。**

## Log formats

`reference/log-formats.md` に4ハーネスの実測スキーマ。コレクタを直すときはそこを見る。
