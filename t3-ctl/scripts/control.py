#!/usr/bin/env python3
"""Pure routing and request-key helpers. Reads JSON; performs no T3 mutations."""
import argparse
import hashlib
import json
import sys


def digest(value):
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode()).hexdigest()


def select_project(data):
    projects = data["projects"]
    if not isinstance(projects, list):
        raise ValueError("projects must be a list")
    ids = [p["id"] for p in projects]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate project IDs; refresh the project snapshot")
    projects = [p for p in projects if not p.get("archivedAt") and not p.get("deletedAt")]
    target = data.get("target", {})
    fields = {"project_id": lambda p: p["id"],
              "workspace_root": lambda p: p.get("workspaceRoot"),
              "repository_key": lambda p: (p.get("repositoryIdentity") or {}).get("canonicalKey"),
              "title": lambda p: p.get("title")}
    unknown = set(target) - set(fields)
    if unknown:
        raise ValueError("unknown target fields: " + ", ".join(sorted(unknown)))
    if any(not isinstance(v, str) or not v.strip() for v in target.values()):
        raise ValueError("target values must be nonempty strings")
    if target:
        # All supplied selectors are constraints, never silently overridden.
        matches = [p for p in projects if all(fields[k](p) == v for k, v in target.items())]
    elif data.get("scope") == "current_project":
        matches = [p for p in projects if p["id"] == data.get("current_project_id")]
    elif data.get("scope") == "cross_project":
        return {"action": "clarify", "reason": "target_required", "candidates": []}
    else:
        raise ValueError("scope must be current_project or cross_project when target is absent")
    candidates = sorted(p["id"] for p in matches)
    if len(candidates) == 1:
        return {"action": "select", "project_id": candidates[0]}
    if not candidates and set(target) == {"workspace_root"}:
        return {"action": "verify_folder", "workspace_root": target["workspace_root"]}
    return {"action": "clarify", "reason": "ambiguous" if candidates else "no_match",
            "candidates": candidates}


def operation_key(data):
    identity = {}
    for key in ("environment_id", "controller_id", "request_id", "assignment_id", "operation"):
        value = data.get(key)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(key + " must be a nonempty string")
        identity[key] = value
    if identity["operation"] not in ("launch", "send"):
        raise ValueError("operation must be launch or send")
    revision = data.get("revision")
    if type(revision) is not int or revision < 1:
        raise ValueError("revision must be a positive integer")
    identity["revision"] = revision
    payload = data.get("payload")
    if not isinstance(payload, dict) or not payload:
        raise ValueError("payload must contain the exact tool arguments before clientRequestId")
    if "clientRequestId" in payload:
        raise ValueError("remove clientRequestId from payload")
    return {"clientRequestId": "t3-ctl-" + digest(identity), "payload_sha256": digest(payload)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("select-project", "operation-key"))
    args = parser.parse_args()
    try:
        data = json.load(sys.stdin)
        if not isinstance(data, dict):
            raise ValueError("input must be a JSON object")
        result = (select_project if args.command == "select-project" else operation_key)(data)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
