---
name: propose-pi-extensions
description: Propose a Pi extension from repeated harness friction. Use when the user asks for extension ideas, or when the same retry, huge tool output, or manual step happened twice or more.
---

# Propose Pi Extensions

このセッションで観測した摩擦から、Pi extension 案を最大 1 件出す。実装は求められない限りしない。

## 先に除外する

次は拡張にしない。

- 1回限りの作業、文言修正、単発コマンド
- スキル、prompt template、`AGENTS.md` で足りるもの
- 既にあるもの。先に確認する。
  - `~/.pi/agent/extensions/`
  - `~/.pi/agent/settings.json` の `packages`
  - 公式例: `@earendil-works/pi-coding-agent` の `examples/extensions/`

## 拡張にする条件

次のどれかを満たすときだけ提案する。

- 同じ失敗や再試行がループしている
- ツール結果が大きすぎて再読・再実行が増えている
- ターンをまたいで同じ手作業をしている
- イベントで機械的に直せる（`tool_call` / `tool_result` / `before_agent_start` / `before_provider_request` / `session_before_compact`）

モデルに「短く書け」と足すだけの案は出さない。

## 出力

日本語で、この形だけ。

```text
拡張: <name>
きっかけ: <このセッションで起きた具体>
フック: <event / API>
効果: <減るターン、再送、手作業>
作らない理由がないか: <既存拡張・skill・設定で足りない理由>
```

候補が弱ければ「今は作らない」と書いて終わる。
