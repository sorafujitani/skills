# Harness log formats

Measured on macOS, 2026-08. Update this file when a collector breaks.

## Codex

```
~/.codex/sessions/YYYY/MM/DD/rollout-<iso>-<uuid>.jsonl
~/.codex/archived_sessions/rollout-*.jsonl
```

Line envelope: `{timestamp, type, payload}`. **`session_meta` carries its type on the OUTER
envelope**; every other event type lives on `payload.type`. Read both.

| payload.type | fields used |
|---|---|
| `session_meta` (outer) | `payload.cwd`, `payload.source` — dict form means subagent: `source.subagent.thread_spawn.parent_thread_id`, `.agent_nickname` |
| `token_count` | `info.last_token_usage{input_tokens, cached_input_tokens, output_tokens, reasoning_output_tokens, total_tokens}`, `info.total_token_usage` (cumulative), `rate_limits` |
| `turn_context` | `model`, `cwd` |
| `thread_settings_applied` | `thread_settings.model`, `.reasoning_effort`, `.service_tier` |
| `task_started` | `model_context_window` |
| `user_message` | `message` |
| `context_compacted` | compaction marker |
| `custom_tool_call` / `function_call` | `name`, `input` / `arguments` |
| `custom_tool_call_output` / `function_call_output` | `output` |

`rate_limits` is the only weekly-quota ground truth across all harnesses:

```json
{"primary": {"used_percent": 26.0, "window_minutes": 10080, "resets_at": 1786499933},
 "plan_type": "prolite", "credits": {"balance": "0"}}
```

`resets_at` drifts a few seconds between events in the same window. Bucket it (600s) before
grouping, and prefer the densest window — isolated single-event windows are stale sessions.

Note: `~/.codex/sqlite/state_5.sqlite` has a `threads.tokens_used` column, but it was stale
by ~7 weeks on inspection. Do not trust it. Parse the rollouts.

## Claude Code

```
~/.claude/projects/<url-encoded-cwd>/<sessionId>.jsonl
~/.claude/projects/<url-encoded-cwd>/<sessionId>/subagents/agent-<id>.jsonl
```

Flat records, `type` at top level: `user` | `assistant` | others.

```json
{"type": "assistant", "timestamp": "...", "cwd": "...", "sessionId": "...",
 "isSidechain": true, "attributionAgent": "reviewer", "attributionSkill": "sora-mode",
 "message": {"model": "claude-opus-4-8",
   "usage": {"input_tokens": 2, "cache_creation_input_tokens": 8456,
             "cache_read_input_tokens": 0, "output_tokens": 5, "service_tier": "standard"}}}
```

- Context size per turn = `input_tokens + cache_creation_input_tokens + cache_read_input_tokens`.
  `input_tokens` alone is near-zero on cache hits and is NOT the context size.
- `isSidechain: true` + `subagents/` path marks subagent work.
- `attributionSkill` names the skill that was active — useful for per-skill cost attribution.
- Tool calls: `message.content[].type == "tool_use"` (`name`, `input`);
  results arrive on the next `user` record as `content[].type == "tool_result"`.

## Grok

```
~/.grok/sessions/<url-encoded-cwd>/<sessionId>/updates.jsonl
```

JSON-RPC shaped: `{timestamp, method: "_x.ai/session/update", params: {sessionId, update}}`.
Dispatch on `params.update.sessionUpdate`:

| sessionUpdate | fields |
|---|---|
| `turn_completed` | `usage{inputTokens, outputTokens, totalTokens, cachedReadTokens, reasoningTokens, modelCalls, apiDurationMs, costUsdTicks, modelUsage{<model>: {...}}, numTurns}` |
| `tool_call` | `title`, `rawInput`, `_meta["x.ai/tool"]{name, kind, read_only}` |
| `tool_call_update` | tool result |
| `user_message_chunk` / `agent_message_chunk` / `agent_thought_chunk` | streaming text |

`timestamp` is unix seconds, not ISO. One `turn_completed` covers `modelCalls` inference calls,
so grok's "turn" is coarser than codex's — do not compare turn counts across harnesses.
`costUsdTicks` / 1e9 = USD.

## pi

```
~/.pi/agent/sessions/<encoded-cwd>/<iso>_<uuid>.jsonl
```

Records: `{type: "message" | "session" | "model_change" | "thinking_level_change", ...}`.
Assistant usage:

```json
{"input": 20402, "output": 225, "cacheRead": 0, "cacheWrite": 0,
 "reasoning": 67, "totalTokens": 20627,
 "cost": {"input": 0.10201, "output": 0.00675, "total": 0.10876}}
```

Content is Anthropic-shaped (`message.content[].type == "tool_use"`), so the Claude walker
works on it.

## Other

- `~/.local/share/opencode/opencode.db` — SQLite (`session_message`, `part`). Not wired up.
- `~/.codex/logs_2.sqlite` — harness debug logs, no token accounting.
