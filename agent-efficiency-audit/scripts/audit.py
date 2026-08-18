#!/usr/bin/env python3
"""Audit local agent-harness session logs for token efficiency.

Normalizes Codex / Claude Code / Grok / pi session logs into a common
turn model, then reports where the token budget actually went.

Usage:
    audit.py summary [--source all] [--days 7] [--since YYYY-MM-DD]
    audit.py session <substring>          # deep-dive one session
    audit.py carry   [--source all] [--days 7]
    audit.py dupes   [--source all] [--days 7]
    audit.py burn    [--days 14]          # codex only: rate-limit curve
    audit.py guard   --source codex       # current-session context checkpoint
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import glob
import json
import os
import re
import sys
from dataclasses import dataclass, field

HOME = os.path.expanduser("~")

# A turn is one model inference call. Its cost is the WHOLE context, not the delta.
POLLING_TOOLS = {
    "wait", "wait_agent", "list_agents", "sleep", "BashOutput",
    "check_agent", "poll", "get_status",
}
CARRY_KINDS = [
    ("skill", re.compile(r"/(?:\.agents/)?skills/")),
    ("brain", re.compile(r"/brain/")),
    ("agents-md", re.compile(r"(?:AGENTS|CLAUDE)\.md")),
]


@dataclass
class Turn:
    ts: float
    total: int
    inp: int
    cached: int
    out: int
    tool: str | None = None


@dataclass
class Sess:
    harness: str
    sid: str
    path: str
    cwd: str = ""
    model: str = ""
    ctx_window: int = 0
    turns: list[Turn] = field(default_factory=list)
    user_msgs: int = 0
    compacts: int = 0
    subagent_of: str = ""
    # (turn_index_at_read, path, bytes)
    reads: list[tuple[int, str, int]] = field(default_factory=list)

    @property
    def total(self) -> int:
        return sum(t.total for t in self.turns)

    @property
    def cached(self) -> int:
        return sum(t.cached for t in self.turns)

    @property
    def out(self) -> int:
        return sum(t.out for t in self.turns)

    @property
    def n(self) -> int:
        return len(self.turns)

    @property
    def start(self) -> float:
        return self.turns[0].ts if self.turns else 0.0

    def ctx_percentiles(self) -> tuple[int, int, int]:
        if not self.turns:
            return 0, 0, 0
        v = sorted(t.inp for t in self.turns)
        return v[len(v) // 2], v[int(len(v) * 0.9)], v[-1]

    def carry_cost(self) -> collections.Counter:
        """Tokens billed for material that sat in context after being read.

        A file read at turn i is re-sent on every later turn. That carry, not
        the read itself, is what the budget actually pays for.
        """
        out = collections.Counter()
        n = self.n
        for idx, path, nbytes in self.reads:
            kind = next((k for k, rx in CARRY_KINDS if rx.search(path)), None)
            if kind is None:
                kind = "large-file" if nbytes > 20_000 else None
            if kind:
                out[kind] += (nbytes // 4) * max(n - idx, 0)
        return out

    def polling_cost(self) -> tuple[int, int]:
        hit = [t for t in self.turns if t.tool in POLLING_TOOLS]
        return sum(t.total for t in hit), len(hit)

    def dupes(self) -> collections.Counter:
        c = collections.Counter(p for _, p, _ in self.reads)
        return collections.Counter({k: v for k, v in c.items() if v > 1})


# --------------------------------------------------------------------------
# collectors
# --------------------------------------------------------------------------

def _iso(s: str) -> float:
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()
    except Exception:
        return 0.0


def _paths_in(blob: str) -> list[str]:
    return re.findall(r"/[\w./@+-]{6,}\.(?:md|ts|tsx|js|py|rs|go|rb|toml|json|yaml|yml)", blob)


def collect_codex(since: float) -> list[Sess]:
    out = []
    root = f"{HOME}/.codex/sessions"
    for f in glob.glob(f"{root}/**/rollout-*.jsonl", recursive=True):
        if os.path.getmtime(f) < since:
            continue
        s = Sess("codex", os.path.basename(f)[8:-6], f)
        pending_tool: str | None = None
        pending_in = ""
        for line in open(f, errors="replace"):
            if '"type"' not in line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            p = o.get("payload") or {}
            t = p.get("type") or o.get("type")  # session_meta lives on the outer envelope
            ts = _iso(o.get("timestamp", ""))
            if t == "session_meta":
                s.cwd = p.get("cwd", "")
                src = p.get("source")
                if isinstance(src, dict):
                    sa = (src.get("subagent") or {}).get("thread_spawn") or {}
                    s.subagent_of = sa.get("parent_thread_id", "")
            elif t == "thread_settings_applied":
                s.model = (p.get("thread_settings") or {}).get("model", "") or s.model
            elif t == "task_started":
                s.ctx_window = p.get("model_context_window") or s.ctx_window
            elif t == "user_message":
                s.user_msgs += 1
            elif t == "context_compacted":
                s.compacts += 1
            elif t in ("custom_tool_call", "function_call"):
                pending_tool = p.get("name")
                pending_in = (p.get("input") or "") + (p.get("arguments") or "")
            elif t in ("custom_tool_call_output", "function_call_output"):
                nbytes = len(json.dumps(p.get("output") or ""))
                for path in set(_paths_in(pending_in)):
                    s.reads.append((len(s.turns), path, nbytes // max(len(set(_paths_in(pending_in))), 1)))
                pending_in = ""
            elif t == "token_count":
                if ts < since:
                    pending_tool = None
                    continue
                lt = (p.get("info") or {}).get("last_token_usage") or {}
                s.turns.append(Turn(
                    ts, lt.get("total_tokens", 0), lt.get("input_tokens", 0),
                    lt.get("cached_input_tokens", 0), lt.get("output_tokens", 0),
                    pending_tool,
                ))
                pending_tool = None
        if s.turns:
            out.append(s)
    return out


def _walk_content(msg: dict) -> tuple[str | None, str, int]:
    """Return (tool_name, tool_input_blob, result_bytes) from an Anthropic-shaped message."""
    name, blob, nbytes = None, "", 0
    content = msg.get("content")
    if not isinstance(content, list):
        return name, blob, nbytes
    for c in content:
        if not isinstance(c, dict):
            continue
        if c.get("type") == "tool_use":
            name = c.get("name")
            blob = json.dumps(c.get("input") or {}, ensure_ascii=False)
        elif c.get("type") == "tool_result":
            nbytes = len(json.dumps(c.get("content") or "", ensure_ascii=False))
    return name, blob, nbytes


def collect_claude(since: float) -> list[Sess]:
    out = []
    for f in glob.glob(f"{HOME}/.claude/projects/**/*.jsonl", recursive=True):
        if os.path.getmtime(f) < since:
            continue
        s = Sess("claude", os.path.basename(f)[:-6], f)
        pending_tool, pending_in = None, ""
        for line in open(f, errors="replace"):
            try:
                o = json.loads(line)
            except Exception:
                continue
            ts = _iso(o.get("timestamp", ""))
            s.cwd = s.cwd or o.get("cwd", "")
            if o.get("isSidechain"):
                s.subagent_of = o.get("parentUuid", "") or s.subagent_of
            typ = o.get("type")
            msg = o.get("message") or {}
            if typ == "user":
                name, blob, nbytes = _walk_content(msg)
                if nbytes:
                    parts = set(_paths_in(pending_in))
                    for path in parts:
                        s.reads.append((len(s.turns), path, nbytes // max(len(parts), 1)))
                    pending_in = ""
                elif isinstance(msg.get("content"), str):
                    s.user_msgs += 1
                if o.get("isCompactSummary"):
                    s.compacts += 1
            elif typ == "assistant":
                u = msg.get("usage") or {}
                if not u:
                    continue
                if ts < since:
                    continue
                s.model = msg.get("model", "") or s.model
                inp = (u.get("input_tokens", 0) + u.get("cache_creation_input_tokens", 0)
                       + u.get("cache_read_input_tokens", 0))
                name, blob, _ = _walk_content(msg)
                if name:
                    pending_tool, pending_in = name, blob
                s.turns.append(Turn(
                    ts, inp + u.get("output_tokens", 0), inp,
                    u.get("cache_read_input_tokens", 0), u.get("output_tokens", 0),
                    name,
                ))
        if s.turns:
            out.append(s)
    return out


def collect_grok(since: float) -> list[Sess]:
    out = []
    for f in glob.glob(f"{HOME}/.grok/sessions/*/*/updates.jsonl"):
        if os.path.getmtime(f) < since:
            continue
        s = Sess("grok", os.path.basename(os.path.dirname(f)), f)
        s.cwd = _unquote(os.path.basename(os.path.dirname(os.path.dirname(f))))
        pending_tool, pending_in = None, ""
        for line in open(f, errors="replace"):
            try:
                o = json.loads(line)
            except Exception:
                continue
            u = (o.get("params") or {}).get("update") or {}
            kind = u.get("sessionUpdate")
            ts = float(o.get("timestamp") or 0)
            if kind == "user_message_chunk":
                s.user_msgs += 1
            elif kind == "tool_call":
                pending_tool = u.get("title") or (u.get("_meta", {}).get("x.ai/tool", {}) or {}).get("name")
                pending_in = json.dumps(u.get("rawInput") or {}, ensure_ascii=False)
            elif kind == "tool_call_update":
                nbytes = len(json.dumps(u.get("content") or u.get("rawOutput") or "", ensure_ascii=False))
                parts = set(_paths_in(pending_in))
                for path in parts:
                    s.reads.append((len(s.turns), path, nbytes // max(len(parts), 1)))
            elif kind == "turn_completed":
                if ts < since:
                    continue
                us = u.get("usage") or {}
                for m in (us.get("modelUsage") or {}):
                    s.model = m
                s.turns.append(Turn(
                    ts, us.get("totalTokens", 0), us.get("inputTokens", 0),
                    us.get("cachedReadTokens", 0), us.get("outputTokens", 0),
                    pending_tool,
                ))
                pending_tool = None
        if s.turns:
            out.append(s)
    return out


def collect_pi(since: float) -> list[Sess]:
    out = []
    for f in glob.glob(f"{HOME}/.pi/agent/sessions/**/*.jsonl", recursive=True):
        if os.path.getmtime(f) < since:
            continue
        s = Sess("pi", os.path.basename(f)[:-6], f)
        pending_in = ""
        for line in open(f, errors="replace"):
            try:
                o = json.loads(line)
            except Exception:
                continue
            ts = _iso(o.get("timestamp", ""))
            if o.get("type") == "session":
                s.cwd = o.get("cwd", "") or s.cwd
            if o.get("type") != "message":
                continue
            msg = o.get("message") or {}
            if msg.get("role") == "user":
                name, blob, nbytes = _walk_content(msg)
                if nbytes:
                    parts = set(_paths_in(pending_in))
                    for path in parts:
                        s.reads.append((len(s.turns), path, nbytes // max(len(parts), 1)))
                    pending_in = ""
                elif isinstance(msg.get("content"), str):
                    s.user_msgs += 1
                continue
            u = msg.get("usage") or {}
            if not u or ts < since:
                continue
            name, blob, _ = _walk_content(msg)
            if name:
                pending_in = blob
            inp = u.get("input", 0) + u.get("cacheRead", 0) + u.get("cacheWrite", 0)
            s.turns.append(Turn(
                ts, u.get("totalTokens", inp + u.get("output", 0)), inp,
                u.get("cacheRead", 0), u.get("output", 0), name,
            ))
        if s.turns:
            out.append(s)
    return out


def _unquote(s: str) -> str:
    from urllib.parse import unquote
    return unquote(s)


COLLECTORS = {
    "codex": collect_codex, "claude": collect_claude,
    "grok": collect_grok, "pi": collect_pi,
}


def load(sources: list[str], since: float) -> list[Sess]:
    out = []
    for name in sources:
        try:
            out += COLLECTORS[name](since)
        except Exception as e:  # a broken harness must not kill the audit
            print(f"warn: {name} collector failed: {e}", file=sys.stderr)
    return sorted(out, key=lambda s: -s.total)


# --------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------

def fmt(n: int) -> str:
    return f"{n:,}"


def cmd_summary(ss: list[Sess], args) -> None:
    if not ss:
        print("no sessions in range")
        return
    grand = sum(s.total for s in ss)
    print(f"# 集計対象 {len(ss)} sessions / {sum(s.n for s in ss)} turns / {fmt(grand)} tokens\n")

    by_h = collections.Counter()
    for s in ss:
        by_h[s.harness] += s.total
    print("## harness別")
    for h, v in by_h.most_common():
        print(f"  {h:<7} {fmt(v):>14}  {v / grand * 100:5.1f}%")

    cached = sum(s.cached for s in ss)
    outp = sum(s.out for s in ss)
    print(f"\n## 内訳\n  cached入力 {fmt(cached)} ({cached / grand * 100:.1f}%)"
          f"\n  出力       {fmt(outp)} ({outp / grand * 100:.1f}%)")
    print("  → 出力比率が数%なら、消費の実体はコンテキスト再送。")

    print(f"\n## セッション別 上位\n{'tokens':>13} {'turns':>6} {'指示':>5} {'t/指示':>7} "
          f"{'ctx中央':>8} {'ctx p90':>8} {'cmpct':>5}  session")
    for s in ss[:15]:
        med, p90, _ = s.ctx_percentiles()
        amp = s.n / s.user_msgs if s.user_msgs else 0
        tag = "↳" if s.subagent_of else " "
        print(f"{fmt(s.total):>13} {s.n:>6} {s.user_msgs:>5} {amp:>7.1f} "
              f"{fmt(med):>8} {fmt(p90):>8} {s.compacts:>5} {tag}{s.harness}:{os.path.basename(s.cwd) or '?'}")

    diagnose(ss, grand)


def diagnose(ss: list[Sess], grand: int) -> None:
    print("\n" + "=" * 64 + "\n# 診断\n")
    findings = []

    heavy = [s for s in ss if s.ctx_percentiles()[0] > 100_000]
    if heavy:
        waste = sum(sum(t.total for t in s.turns if t.inp > 140_000) for s in heavy)
        findings.append((
            waste,
            f"[セッションが長すぎる] {len(heavy)}件が中央値10万トークン超。"
            f"140k超のターンだけで {fmt(waste)} ({waste / grand * 100:.1f}%)。\n"
            f"  コンテキストは毎ターン再送されるので、コストはturn数の二乗で効く。"
            f"100kを超えたら引き継ぎメモを書いて新セッションへ。",
        ))

    carry = collections.Counter()
    for s in ss:
        carry.update(s.carry_cost())
    ctotal = sum(carry.values())
    if ctotal > grand * 0.10:
        detail = ", ".join(f"{k}={fmt(v)}" for k, v in carry.most_common())
        findings.append((
            ctotal,
            f"[常駐ドキュメントが高い] 読み込み後も居座り続ける分が {fmt(ctotal)} "
            f"({ctotal / grand * 100:.1f}%)。内訳: {detail}\n"
            f"  skill/brain/AGENTS.mdは一度読めば十分。"
            f"「毎回全文読む」系の指示を疑う。",
        ))

    dupe_rows = []
    for s in ss:
        for path, cnt in s.dupes().most_common(3):
            if cnt >= 3:
                dupe_rows.append((cnt, path, s))
    if dupe_rows:
        dupe_rows.sort(reverse=True, key=lambda r: r[0])
        msg = "[同一ファイルの再読み込み] すでにコンテキストにあるものを読み直している。\n"
        for cnt, path, s in dupe_rows[:8]:
            msg += f"    {cnt:>3}x {path[-58:]}  ({s.harness}:{os.path.basename(s.cwd)})\n"
        findings.append((sum(r[0] for r in dupe_rows) * 10_000, msg.rstrip()))

    ptok = sum(s.polling_cost()[0] for s in ss)
    pn = sum(s.polling_cost()[1] for s in ss)
    if pn and ptok > grand * 0.02:
        findings.append((
            ptok,
            f"[待ちのポーリング] {pn}回の待機系ツール呼び出しで {fmt(ptok)} "
            f"({ptok / grand * 100:.1f}%)。1回あたり {fmt(ptok // pn)}。\n"
            f"  進捗確認は新情報ゼロなのに全コンテキストを課金される。"
            f"ブロッキング待ちか完了通知の一括読みに変える。",
        ))

    amp = [s for s in ss if s.user_msgs >= 3 and s.n / s.user_msgs > 20]
    if amp:
        findings.append((
            sum(s.total for s in amp),
            f"[1指示あたりのturnが多い] {len(amp)}件が指示あたり20turn超"
            f"(最大 {max(s.n / s.user_msgs for s in amp):.0f})。\n"
            f"  探索が発散している。着手前にスコープを詰めるか、turn上限を切る。",
        ))

    subs = [s for s in ss if s.subagent_of]
    if subs and sum(s.total for s in subs) > grand * 0.10:
        v = sum(s.total for s in subs)
        findings.append((
            v,
            f"[subagentの重複探索] {len(subs)}件のsubagentで {fmt(v)} "
            f"({v / grand * 100:.1f}%)。親と同じ調査をしていないか、"
            f"渡す文脈が過剰でないかを確認。",
        ))

    if not findings:
        print("目立った非効率は検出されず。")
        return
    for _, msg in sorted(findings, reverse=True, key=lambda x: x[0]):
        print(f"- {msg}\n")


def cmd_session(ss: list[Sess], args) -> None:
    hits = [s for s in ss if args.query in s.sid or args.query in s.path or args.query in s.cwd]
    if not hits:
        print("no match")
        return
    s = max(hits, key=lambda x: x.total)
    med, p90, mx = s.ctx_percentiles()
    print(f"# {s.harness} {s.sid}\n  cwd={s.cwd}\n  model={s.model}  ctx_window={fmt(s.ctx_window)}")
    print(f"  turns={s.n} 指示={s.user_msgs} compact={s.compacts} tokens={fmt(s.total)}")
    print(f"  ctx 中央={fmt(med)} p90={fmt(p90)} 最大={fmt(mx)}")

    print("\n## tool別コスト")
    c, n = collections.Counter(), collections.Counter()
    for t in s.turns:
        c[t.tool or "(なし)"] += t.total
        n[t.tool or "(なし)"] += 1
    for k, v in c.most_common(12):
        flag = "  ← 待機" if k in POLLING_TOOLS else ""
        print(f"  {str(k):>18} {fmt(v):>13} turns={n[k]:>4} avg={fmt(v // n[k]):>9}{flag}")

    cc = s.carry_cost()
    if cc:
        print("\n## 常駐コスト（読み込み量 × 以降の残りturn）")
        for k, v in cc.most_common():
            print(f"  {k:>12} {fmt(v):>13}  ({v / max(s.total, 1) * 100:.1f}% of session)")

    d = s.dupes()
    if d:
        print("\n## 重複読み込み")
        for path, cnt in d.most_common(10):
            print(f"  {cnt:>3}x {path[-64:]}")

    print("\n## コンテキスト推移（最初の12turn）")
    prev = 0
    for i, t in enumerate(s.turns[:12], 1):
        print(f"  turn{i:>3} input={fmt(t.inp):>9} 差分={t.inp - prev:>+9,} out={t.out:>6}  {t.tool or ''}")
        prev = t.inp
    tot_in = sum(t.inp for t in s.turns)
    if s.turns:
        print(f"\n  input合計 {fmt(tot_in)} / 最終ctx {fmt(s.turns[-1].inp)}"
              f" = 実質会話量の {tot_in / max(s.turns[-1].inp, 1):.1f} 倍を課金")


def cmd_carry(ss: list[Sess], args) -> None:
    grand = sum(s.total for s in ss) or 1
    tot = collections.Counter()
    rows = []
    for s in ss:
        c = s.carry_cost()
        if c:
            tot.update(c)
            rows.append((sum(c.values()), s, c))
    rows.sort(reverse=True, key=lambda r: r[0])
    print(f"# 常駐コスト 合計 {fmt(sum(tot.values()))} ({sum(tot.values()) / grand * 100:.1f}% of {fmt(grand)})\n")
    for k, v in tot.most_common():
        print(f"  {k:>12} {fmt(v):>14}  {v / grand * 100:5.1f}%")
    print(f"\n{'carry':>13} {'turns':>6}  session")
    for v, s, c in rows[:12]:
        print(f"{fmt(v):>13} {s.n:>6}  {s.harness}:{os.path.basename(s.cwd) or '?'}  {dict(c)}")


def cmd_dupes(ss: list[Sess], args) -> None:
    agg = collections.Counter()
    for s in ss:
        agg.update(s.dupes())
    if not agg:
        print("重複読み込みなし")
        return
    print("# 同一セッション内で複数回読まれたファイル\n")
    for path, cnt in agg.most_common(30):
        size = os.path.getsize(path) if os.path.exists(path) else 0
        print(f"  {cnt:>3}x  {fmt(size):>8}B  {path}")


def cmd_burn(ss: list[Sess], args) -> None:
    """Codex only: rate_limits.primary is the authoritative weekly gauge."""
    pts = []
    for s in ss:
        if s.harness != "codex":
            continue
        for line in open(s.path, errors="replace"):
            if '"rate_limits"' not in line:
                continue
            try:
                o = json.loads(line)
            except Exception:
                continue
            rl = (o.get("payload") or {}).get("rate_limits") or {}
            pr = rl.get("primary") or {}
            if pr.get("window_minutes") and pr.get("used_percent") is not None:
                pts.append((_iso(o.get("timestamp", "")), pr["used_percent"],
                            pr.get("resets_at"), pr["window_minutes"], os.path.basename(s.cwd)))
    if not pts:
        print("rate limit情報なし (codexのみ対応)")
        return
    pts.sort()
    # resets_at drifts a few seconds between events inside one window; bucket it.
    buckets = collections.defaultdict(list)
    for p in pts:
        if p[2]:
            buckets[round(p[2] / 600) * 600].append(p)
    if not buckets:
        print("rate limit情報なし")
        return
    now = dt.datetime.now().timestamp()
    live = [k for k in buckets if k > now and k - buckets[k][0][3] * 60 <= now]
    key = max(live or buckets, key=lambda k: len(buckets[k]))
    cur = buckets[key]
    win_min = cur[0][3]
    reset = max(p[2] for p in cur)
    print(f"# {'現在' if key in live else '直近'}の枠 (window={win_min}分) "
          f"reset={dt.datetime.fromtimestamp(reset)}")
    print(f"  枠開始 {dt.datetime.fromtimestamp(reset - win_min * 60)}")
    print(f"  到達 {max(p[1] for p in cur):.0f}%\n")
    seen = -1
    for ts, up, _, _, cwd in cur:
        if up > seen and up % 10 == 0:
            seen = up
            print(f"  {dt.datetime.fromtimestamp(ts):%m-%d %H:%M}  {up:5.0f}%  {cwd}")


def cmd_guard(ss: list[Sess], args) -> None:
    """Show the latest active session's context and a handoff verdict."""
    codex = [s for s in ss if s.harness == "codex" and s.turns]
    if not codex:
        print("Codex session情報なし")
        return
    s = max(codex, key=lambda item: item.turns[-1].ts)
    last = s.turns[-1]
    pct = last.inp / s.ctx_window * 100 if s.ctx_window else 0.0
    if last.inp >= 100_000 or s.compacts >= 2:
        verdict = "HANDOFF: 新しいscopeを始めず、resume noteを作って新セッションへ"
    elif last.inp >= 80_000 or s.compacts >= 1:
        verdict = "WARN: 現在のatomic stepを終え、次のphaseで新セッションへ"
    else:
        verdict = "OK: 現在のscopeを継続可能"
    print(f"# current Codex guard\n  session={s.sid}\n  cwd={s.cwd}")
    print(f"  last_context={fmt(last.inp)} / {fmt(s.ctx_window)} ({pct:.1f}%)")
    print(f"  turns={s.n} user_messages={s.user_msgs} compacts={s.compacts}")
    print(f"  verdict={verdict}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["summary", "session", "carry", "dupes", "burn", "guard"])
    ap.add_argument("query", nargs="?", default="")
    ap.add_argument("--source", default="all")
    ap.add_argument("--days", type=float, default=7)
    ap.add_argument("--since", default="")
    a = ap.parse_args()

    if a.since:
        since = dt.datetime.fromisoformat(a.since).timestamp()
    else:
        since = (dt.datetime.now() - dt.timedelta(days=a.days)).timestamp()

    srcs = list(COLLECTORS) if a.source == "all" else a.source.split(",")
    ss = load(srcs, since)
    {"summary": cmd_summary, "session": cmd_session, "carry": cmd_carry,
     "dupes": cmd_dupes, "burn": cmd_burn, "guard": cmd_guard}[a.cmd](ss, a)


if __name__ == "__main__":
    main()
