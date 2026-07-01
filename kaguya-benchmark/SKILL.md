---
name: kaguya-benchmark
description: Benchmark Kaguya and WezTerm macOS builds for app size, zip size, binary size, and startup time. Use when the user asks to measure or compare Kaguya vs WezTerm, before/after Kaguya refs, macOS launch speed, package size, or startup performance after optimization work.
---

# Kaguya Benchmark

## Workflow

Use this skill for macOS benchmark work around Kaguya or WezTerm. Prefer actual build/package/run measurements over estimates.

1. Confirm the target repository and refs. For the local Kaguya fork, default to:

   ```sh
   /Users/fujitanisora/ghq/github.com/sorafujitani/kaguya
   ```

2. Keep the user worktree clean. Do not run destructive cleanup in the repo. The bundled script creates temporary detached worktrees and removes them unless `--keep-artifacts` is set.

3. Run the benchmark script:

   ```sh
   python3 /Users/fujitanisora/.agents/skills/kaguya-benchmark/scripts/benchmark_kaguya.py \
     --repo /Users/fujitanisora/ghq/github.com/sorafujitani/kaguya \
     --before-ref <old-ref> \
     --after-ref <new-ref> \
     --runs 8
   ```

4. Report:
   - exact refs
   - macOS version and cargo/rust toolchain
   - `.app`, zip, and GUI binary size deltas
   - startup timing medians and percentage deltas
   - whether runs were alternating and warmed
   - any CI/test failures separately from size/startup results

## Script Behavior

`scripts/benchmark_kaguya.py` does the repeatable work:

- creates detached git worktrees for `--before-ref` and `--after-ref`
- builds release binaries with `cargo +nightly build --release -p wezterm -p wezterm-gui -p wezterm-mux-server -p strip-ansi-escapes`
- packages with `TAG_NAME=... ci/deploy.sh target`
- reads `Info.plist` to detect bundle id and executable
- measures launch with `open -na`, `pgrep`, and System Events window detection by PID
- alternates before/current launches to reduce OS cache ordering bias
- prints per-run JSON lines and a final `SUMMARY_JSON=...`

Use `--keep-artifacts` only when the user wants to inspect the generated `.app` or zip. Otherwise let the script clean temporary worktrees.

## Caveats

- This is macOS-only. Do not run launch benchmarks on Linux.
- Unsigned local `.app` builds may differ from signed release builds.
- `open -na` and System Events measure launch/window-detection time, not terminal prompt readiness.
- If comparing against upstream WezTerm, ensure the ref can still build with the local toolchain. Prefer a known buildable ref if upstream `main` has moved.
