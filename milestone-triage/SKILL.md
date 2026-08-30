---
name: milestone-triage
description: Manage a personal triage-grouped wishlist ("やりたいこと") with local JSON persistence at ~/.claude/data/milestone-triage/state.json. INVOKE ONLY when the user explicitly mentions "milestone-triage" / "milestone triage" / "トリアージ" in the context of their own task list, or directly asks to view/add/move/edit/remove items in this triage backlog. Do NOT trigger from generic todo, task, or planning discussions — this skill is opt-in. Use for (1) showing items grouped by triage, (2) adding new items, (3) moving items between triages, (4) editing/removing items, (5) reshaping the triage groups themselves (add/remove/rename/reorder).
---

# Milestone Triage

A triage-grouped wishlist for the user's "やりたいこと". State lives in a single JSON file so it persists across sessions.

## Storage

- Path: `~/.claude/data/milestone-triage/state.json` (auto-created on first write)
- Override for testing: set `MILESTONE_TRIAGE_STATE` env var to a different path
- Format: `{"version": 1, "triages": [...names in display order...], "items": [{id, title, note, triage, created_at, updated_at}, ...]}`
- Default triages on first run: `now, next, later, someday, done`
- IDs are 4-char hex generated on add; reference items by id everywhere

## CLI

All operations go through `scripts/milestone.py`. Run via the user's `python3`:

```
python3 ~/.claude/skills/milestone-triage/scripts/milestone.py <subcommand> [...]
```

### Item commands

| Command | Purpose |
|---|---|
| `list [--triage NAME] [--json]` | Show items grouped by triage (default: all triages, in declared order) |
| `add "TITLE" [--triage NAME] [--note "TEXT"]` | Add item. Default triage is the first one |
| `move ID NEW_TRIAGE` | Move item between triages (the core "入れ替え" operation) |
| `edit ID [--title "..."] [--note "..."]` | Update an item's title and/or note |
| `remove ID` | Permanently delete an item |
| `show ID` | Print one item as JSON |

### Triage-group commands

| Command | Purpose |
|---|---|
| `triages [--json]` | List triage groups with item counts |
| `triage-add NAME [--after EXISTING]` | Add a new triage group (default: append at end) |
| `triage-remove NAME [--move-to OTHER]` | Delete a group. `--move-to` required if it has items |
| `triage-rename OLD NEW` | Rename a triage group (items follow) |
| `triage-reorder NAME1 NAME2 ...` | Reorder; must list every existing triage exactly once |
| `path` | Print the state file path |

Errors exit nonzero with a single-line message (e.g. `unknown triage 'foo'. known: ...`, `item not found: abcd`).

## Typical workflow

When the user explicitly invokes this skill:

1. **Show first** — start with `list` (or `list --triage X` if they named one) so the user sees current state with ids. Render the grouped output as-is; it's already formatted for humans.
2. **Apply the change** — translate the user's natural-language request into one or more subcommand calls. Examples:
   - "ブログ書くを now に上げて" → `move <id> now` (look up the id from the prior list output)
   - "Redis 移行を追加、優先度は next" → `add "Redis 移行" --triage next`
   - "someday を消して、中身は later に" → `triage-remove someday --move-to later`
   - "triage の順番を urgent, now, later にして" → `triage-reorder urgent now later` (every existing group must appear)
3. **Confirm with a fresh list** — re-run `list` (or the affected `list --triage X`) so the user sees the updated state.

## Selection rules

- If the user references an item by title rather than id, run `list --json` (or scan the previous output), match the title, then call the command with the resolved id. If there are multiple matches, show them and ask which.
- If the user asks to add an item without naming a triage, default to the first triage (`state["triages"][0]`); mention which one you chose.
- Destructive ops (`remove`, `triage-remove` without `--move-to`) — confirm with the user before running if they didn't specify the id/name explicitly.
- Never edit `state.json` directly; always go through the CLI so timestamps and validation stay consistent.

## Output rendering

The default `list` output is already grouped and easy to read. When showing it back to the user, prefer pasting the raw CLI output in a code block rather than reformatting — the alignment and group headers carry meaning. If the user asks for a different shape (markdown table, sorted by date, etc.), use `list --json` and reformat from there.
