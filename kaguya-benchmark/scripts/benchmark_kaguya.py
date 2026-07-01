#!/usr/bin/env python3
"""Benchmark Kaguya/WezTerm macOS package size and startup time."""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT_BINARIES = [
    "wezterm",
    "wezterm-gui",
    "kaguya",
    "kaguya-gui",
    "wezterm-mux-server",
    "strip-ansi-escapes",
]


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    print("+ " + " ".join(cmd), file=sys.stderr, flush=True)
    return subprocess.run(cmd, cwd=cwd, env=env, text=True, check=True)


def capture(cmd: list[str], cwd: Path | None = None) -> str:
    return subprocess.check_output(cmd, cwd=cwd, text=True).strip()


def tree_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def make_worktree(repo: Path, ref: str, parent: Path, label: str) -> Path:
    worktree = parent / label
    run(["git", "-C", str(repo), "worktree", "add", "--detach", str(worktree), ref])
    return worktree


def remove_worktree(repo: Path, worktree: Path) -> None:
    subprocess.run(["git", "-C", str(repo), "worktree", "remove", "--force", str(worktree)], text=True)


def package_app(worktree: Path, label: str) -> tuple[Path, Path]:
    env = os.environ.copy()
    env["TAG_NAME"] = f"skill-bench-{label}"
    env.setdefault("LANG", "en_US.UTF-8")
    env.setdefault("LC_ALL", "en_US.UTF-8")
    run(["cargo", "+nightly", "build", "--release", "-p", "wezterm", "-p", "wezterm-gui", "-p", "wezterm-mux-server", "-p", "strip-ansi-escapes"], cwd=worktree, env=env)
    run(["bash", "ci/deploy.sh", "target"], cwd=worktree, env=env)

    zip_path = worktree / f"Kaguya-macos-skill-bench-{label}.zip"
    if not zip_path.exists():
        zip_path = worktree / f"WezTerm-macos-skill-bench-{label}.zip"
    if not zip_path.exists():
        candidates = sorted(worktree.glob(f"*-macos-skill-bench-{label}.zip"))
        if not candidates:
            raise FileNotFoundError(f"package zip not found for {label}")
        zip_path = candidates[0]

    zipdir = zip_path.with_suffix("")
    apps = sorted(zipdir.glob("*.app"))
    if not apps:
        raise FileNotFoundError(f".app not found under {zipdir}")
    return apps[0], zip_path


def app_info(app: Path) -> dict[str, str]:
    plist_path = app / "Contents" / "Info.plist"
    with plist_path.open("rb") as fh:
        plist = plistlib.load(fh)
    executable = plist.get("CFBundleExecutable")
    bundle_id = plist.get("CFBundleIdentifier")
    if not executable:
        macos_dir = app / "Contents" / "MacOS"
        candidates = [p.name for p in macos_dir.iterdir() if p.is_file() and os.access(p, os.X_OK)]
        if not candidates:
            raise RuntimeError(f"no executable found in {macos_dir}")
        executable = candidates[0]
    return {
        "app_name": app.stem,
        "bundle_id": bundle_id or "",
        "executable": executable,
        "gui_binary": str(app / "Contents" / "MacOS" / executable),
    }


def quit_app(info: dict[str, str]) -> None:
    bundle_id = info.get("bundle_id")
    executable = info["executable"]
    if bundle_id:
        subprocess.run(["osascript", "-e", f'tell application id "{bundle_id}" to quit'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.30)
    subprocess.run(["pkill", "-x", executable], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    subprocess.run(["pkill", "-x", "wezterm-mux-server"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(0.50)


def pgrep_exact(name: str) -> str | None:
    result = subprocess.run(["pgrep", "-x", name], text=True, capture_output=True)
    if result.returncode == 0:
        return result.stdout.strip().splitlines()[0]
    return None


def window_count_for_pid(pid: str) -> int | None:
    script = f'''
tell application "System Events"
  set matches to processes whose unix id is {pid}
  if (count of matches) is 0 then return -1
  return count windows of item 1 of matches
end tell
'''
    result = subprocess.run(["osascript", "-e", script], text=True, capture_output=True)
    if result.returncode != 0:
        return None
    try:
        return int(result.stdout.strip())
    except ValueError:
        return None


def measure_launch(app: Path, info: dict[str, str], timeout_s: float) -> dict[str, float | int | str | None]:
    quit_app(info)
    t0 = time.perf_counter()
    opened = subprocess.run(["open", "-na", str(app)], text=True, capture_output=True)
    open_return = time.perf_counter() - t0
    process_s = None
    window_s = None
    pid = None
    deadline = t0 + timeout_s

    while time.perf_counter() < deadline:
        now = time.perf_counter()
        if pid is None:
            pid = pgrep_exact(info["executable"])
            if pid is not None:
                process_s = now - t0
        if pid is not None:
            count = window_count_for_pid(pid)
            if count is not None and count > 0:
                window_s = now - t0
                break
        time.sleep(0.05)

    row = {
        "open_return_s": open_return,
        "process_s": process_s,
        "window_s": window_s,
        "pid": pid,
        "open_rc": opened.returncode,
        "open_stderr": opened.stderr.strip(),
    }
    quit_app(info)
    return row


def summarize(rows: list[dict[str, object]], key: str) -> dict[str, float | int | None]:
    vals = [r.get(key) for r in rows]
    nums = [float(v) for v in vals if isinstance(v, (int, float))]
    if not nums:
        return {"n": 0, "min": None, "median": None, "mean": None, "max": None}
    return {
        "n": len(nums),
        "min": min(nums),
        "median": statistics.median(nums),
        "mean": statistics.mean(nums),
        "max": max(nums),
    }


def build_case(repo: Path, ref: str, parent: Path, label: str) -> dict[str, object]:
    worktree = make_worktree(repo, ref, parent, label)
    commit = capture(["git", "rev-parse", "HEAD"], cwd=worktree)
    app, zip_path = package_app(worktree, label)
    info = app_info(app)
    gui_binary = Path(str(info["gui_binary"]))
    return {
        "label": label,
        "ref": ref,
        "commit": commit,
        "worktree": str(worktree),
        "app": str(app),
        "zip": str(zip_path),
        "info": info,
        "sizes": {
            "app_bytes": tree_size(app),
            "zip_bytes": zip_path.stat().st_size,
            "gui_binary_bytes": gui_binary.stat().st_size if gui_binary.exists() else None,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Kaguya/WezTerm macOS package size and startup time.")
    parser.add_argument("--repo", required=True, type=Path, help="Git repository path.")
    parser.add_argument("--before-ref", required=True, help="Older ref to compare.")
    parser.add_argument("--after-ref", required=True, help="Newer ref to compare.")
    parser.add_argument("--runs", type=int, default=8, help="Alternating launch runs per ref.")
    parser.add_argument("--timeout", type=float, default=12.0, help="Launch detection timeout in seconds.")
    parser.add_argument("--keep-artifacts", action="store_true", help="Keep temporary worktrees and packages.")
    args = parser.parse_args()

    repo = args.repo.expanduser().resolve()
    if sys.platform != "darwin":
        raise SystemExit("startup launch benchmark requires macOS")
    if args.runs < 1:
        raise SystemExit("--runs must be >= 1")

    temp_parent = Path(tempfile.mkdtemp(prefix="kaguya-bench-"))
    cases: dict[str, dict[str, object]] = {}
    try:
        cases["before"] = build_case(repo, args.before_ref, temp_parent, "before")
        cases["after"] = build_case(repo, args.after_ref, temp_parent, "after")

        rows: dict[str, list[dict[str, object]]] = {"before": [], "after": []}
        order = ["after", "before"] * args.runs
        for seq, label in enumerate(order, 1):
            case = cases[label]
            info = case["info"]
            assert isinstance(info, dict)
            app = Path(str(case["app"]))
            row = measure_launch(app, info, args.timeout)
            row["seq"] = seq
            row["label"] = label
            rows[label].append(row)
            print("RUN_JSON=" + json.dumps(row, sort_keys=True), flush=True)

        summary = {
            "repo": str(repo),
            "before": {k: v for k, v in cases["before"].items() if k not in {"worktree"}},
            "after": {k: v for k, v in cases["after"].items() if k not in {"worktree"}},
            "size_delta": {
                key: cases["after"]["sizes"][key] - cases["before"]["sizes"][key]
                for key in ["app_bytes", "zip_bytes", "gui_binary_bytes"]
                if cases["after"]["sizes"].get(key) is not None and cases["before"]["sizes"].get(key) is not None
            },
            "launch": {
                label: {key: summarize(label_rows, key) for key in ["open_return_s", "process_s", "window_s"]}
                for label, label_rows in rows.items()
            },
            "environment": {
                "sw_vers": capture(["sw_vers"]),
                "rustc": capture(["rustc", "--version"]),
                "cargo_nightly": capture(["cargo", "+nightly", "--version"]),
            },
        }
        print("SUMMARY_JSON=" + json.dumps(summary, sort_keys=True), flush=True)
    finally:
        if args.keep_artifacts:
            print(f"ARTIFACTS_DIR={temp_parent}")
        else:
            for case in cases.values():
                worktree = Path(str(case["worktree"]))
                remove_worktree(repo, worktree)
            shutil.rmtree(temp_parent, ignore_errors=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
