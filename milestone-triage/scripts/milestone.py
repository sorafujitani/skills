#!/usr/bin/env python3
"""milestone-triage CLI: triage-grouped wishlist with local JSON persistence."""

from __future__ import annotations

import argparse
import json
import os
import secrets
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_TRIAGES = ["now", "next", "later", "someday", "done"]
STATE_VERSION = 1


def state_path() -> Path:
    env = os.environ.get("MILESTONE_TRIAGE_STATE")
    if env:
        return Path(env).expanduser()
    return Path.home() / ".claude" / "data" / "milestone-triage" / "state.json"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def new_id(existing: set[str]) -> str:
    while True:
        candidate = secrets.token_hex(2)
        if candidate not in existing:
            return candidate


def load_state() -> dict:
    path = state_path()
    if not path.exists():
        return {"version": STATE_VERSION, "triages": list(DEFAULT_TRIAGES), "items": []}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"failed to read state at {path}: {exc}")
    data.setdefault("version", STATE_VERSION)
    data.setdefault("triages", list(DEFAULT_TRIAGES))
    data.setdefault("items", [])
    return data


def save_state(state: dict) -> None:
    path = state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".state.", suffix=".json", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(state, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(tmp, path)
    except Exception:
        Path(tmp).unlink(missing_ok=True)
        raise


def find_item(state: dict, item_id: str) -> dict:
    for item in state["items"]:
        if item["id"] == item_id:
            return item
    raise SystemExit(f"item not found: {item_id}")


def require_triage(state: dict, name: str) -> None:
    if name not in state["triages"]:
        raise SystemExit(
            f"unknown triage '{name}'. known: {', '.join(state['triages']) or '(none)'}"
        )


def cmd_list(state: dict, args: argparse.Namespace) -> None:
    if args.json:
        if args.triage:
            require_triage(state, args.triage)
            payload = [i for i in state["items"] if i["triage"] == args.triage]
        else:
            payload = state["items"]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    triages = [args.triage] if args.triage else state["triages"]
    if args.triage:
        require_triage(state, args.triage)

    by_triage: dict[str, list[dict]] = {t: [] for t in triages}
    for item in state["items"]:
        if item["triage"] in by_triage:
            by_triage[item["triage"]].append(item)

    total = sum(len(v) for v in by_triage.values())
    if total == 0:
        scope = f"triage '{args.triage}'" if args.triage else "all triages"
        print(f"(no items in {scope})")
        return

    for t in triages:
        items = by_triage[t]
        print(f"[{t}] ({len(items)})")
        if not items:
            print("  -")
        for item in items:
            print(f"  {item['id']}  {item['title']}")
            if item.get("note"):
                for line in item["note"].splitlines():
                    print(f"        {line}")
        print()


def cmd_add(state: dict, args: argparse.Namespace) -> None:
    if not state["triages"]:
        raise SystemExit("no triage groups exist. run 'triage-add <name>' first.")
    triage = args.triage or state["triages"][0]
    require_triage(state, triage)
    item_id = new_id({i["id"] for i in state["items"]})
    now = now_iso()
    item = {
        "id": item_id,
        "title": args.title,
        "note": args.note or "",
        "triage": triage,
        "created_at": now,
        "updated_at": now,
    }
    state["items"].append(item)
    save_state(state)
    print(f"added {item_id} -> [{triage}] {args.title}")


def cmd_move(state: dict, args: argparse.Namespace) -> None:
    require_triage(state, args.triage)
    item = find_item(state, args.id)
    prev = item["triage"]
    if prev == args.triage:
        print(f"{args.id} already in [{args.triage}]")
        return
    item["triage"] = args.triage
    item["updated_at"] = now_iso()
    save_state(state)
    print(f"moved {args.id}: [{prev}] -> [{args.triage}]")


def cmd_edit(state: dict, args: argparse.Namespace) -> None:
    item = find_item(state, args.id)
    if args.title is None and args.note is None:
        raise SystemExit("nothing to change. pass --title and/or --note.")
    if args.title is not None:
        item["title"] = args.title
    if args.note is not None:
        item["note"] = args.note
    item["updated_at"] = now_iso()
    save_state(state)
    print(f"edited {args.id}")


def cmd_remove(state: dict, args: argparse.Namespace) -> None:
    item = find_item(state, args.id)
    state["items"] = [i for i in state["items"] if i["id"] != args.id]
    save_state(state)
    print(f"removed {args.id} [{item['triage']}] {item['title']}")


def cmd_show(state: dict, args: argparse.Namespace) -> None:
    item = find_item(state, args.id)
    print(json.dumps(item, ensure_ascii=False, indent=2))


def cmd_triages(state: dict, args: argparse.Namespace) -> None:
    if args.json:
        print(json.dumps(state["triages"], ensure_ascii=False, indent=2))
        return
    counts: dict[str, int] = {t: 0 for t in state["triages"]}
    for item in state["items"]:
        if item["triage"] in counts:
            counts[item["triage"]] += 1
    for t in state["triages"]:
        print(f"{t}\t{counts[t]}")


def cmd_triage_add(state: dict, args: argparse.Namespace) -> None:
    if args.name in state["triages"]:
        raise SystemExit(f"triage '{args.name}' already exists")
    if args.after:
        require_triage(state, args.after)
        idx = state["triages"].index(args.after) + 1
        state["triages"].insert(idx, args.name)
    else:
        state["triages"].append(args.name)
    save_state(state)
    print(f"added triage '{args.name}'. order: {', '.join(state['triages'])}")


def cmd_triage_remove(state: dict, args: argparse.Namespace) -> None:
    require_triage(state, args.name)
    in_use = [i["id"] for i in state["items"] if i["triage"] == args.name]
    if in_use and not args.move_to:
        raise SystemExit(
            f"triage '{args.name}' has {len(in_use)} item(s). "
            f"use --move-to <triage> to relocate them first."
        )
    if in_use:
        require_triage(state, args.move_to)
        if args.move_to == args.name:
            raise SystemExit("--move-to must differ from the triage being removed")
        now = now_iso()
        for item in state["items"]:
            if item["triage"] == args.name:
                item["triage"] = args.move_to
                item["updated_at"] = now
    state["triages"] = [t for t in state["triages"] if t != args.name]
    save_state(state)
    moved = f", moved {len(in_use)} item(s) to '{args.move_to}'" if in_use else ""
    print(f"removed triage '{args.name}'{moved}")


def cmd_triage_rename(state: dict, args: argparse.Namespace) -> None:
    require_triage(state, args.old)
    if args.new in state["triages"]:
        raise SystemExit(f"triage '{args.new}' already exists")
    state["triages"] = [args.new if t == args.old else t for t in state["triages"]]
    now = now_iso()
    for item in state["items"]:
        if item["triage"] == args.old:
            item["triage"] = args.new
            item["updated_at"] = now
    save_state(state)
    print(f"renamed '{args.old}' -> '{args.new}'")


def cmd_triage_reorder(state: dict, args: argparse.Namespace) -> None:
    given = list(args.order)
    if sorted(given) != sorted(state["triages"]):
        raise SystemExit(
            "reorder must list every existing triage exactly once. "
            f"current: {', '.join(state['triages'])}"
        )
    state["triages"] = given
    save_state(state)
    print(f"new order: {', '.join(state['triages'])}")


def cmd_path(state: dict, args: argparse.Namespace) -> None:
    print(state_path())


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="milestone",
        description="Triage-grouped wishlist stored at ~/.claude/data/milestone-triage/state.json",
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="show items grouped by triage")
    sp.add_argument("--triage", help="restrict to one triage group")
    sp.add_argument("--json", action="store_true", help="emit JSON")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("add", help="add a new item")
    sp.add_argument("title")
    sp.add_argument("--triage", help="triage group (default: first one)")
    sp.add_argument("--note", help="optional note/description")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("move", help="move an item to another triage")
    sp.add_argument("id")
    sp.add_argument("triage")
    sp.set_defaults(func=cmd_move)

    sp = sub.add_parser("edit", help="edit an item's title or note")
    sp.add_argument("id")
    sp.add_argument("--title")
    sp.add_argument("--note")
    sp.set_defaults(func=cmd_edit)

    sp = sub.add_parser("remove", help="permanently delete an item")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_remove)

    sp = sub.add_parser("show", help="show one item as JSON")
    sp.add_argument("id")
    sp.set_defaults(func=cmd_show)

    sp = sub.add_parser("triages", help="list triage groups and counts")
    sp.add_argument("--json", action="store_true")
    sp.set_defaults(func=cmd_triages)

    sp = sub.add_parser("triage-add", help="add a new triage group")
    sp.add_argument("name")
    sp.add_argument("--after", help="insert after this existing triage (default: append)")
    sp.set_defaults(func=cmd_triage_add)

    sp = sub.add_parser("triage-remove", help="delete a triage group")
    sp.add_argument("name")
    sp.add_argument("--move-to", help="relocate items in the removed triage to this one")
    sp.set_defaults(func=cmd_triage_remove)

    sp = sub.add_parser("triage-rename", help="rename a triage group")
    sp.add_argument("old")
    sp.add_argument("new")
    sp.set_defaults(func=cmd_triage_rename)

    sp = sub.add_parser("triage-reorder", help="reorder triages (provide every name)")
    sp.add_argument("order", nargs="+")
    sp.set_defaults(func=cmd_triage_reorder)

    sp = sub.add_parser("path", help="print the state file path")
    sp.set_defaults(func=cmd_path)

    return p


def main() -> None:
    args = build_parser().parse_args()
    state = load_state()
    args.func(state, args)


if __name__ == "__main__":
    main()
