---
name: handoff
description: Use when pausing work, crossing a context boundary, waiting for an external event, resuming a prior session, or delivering an in-progress change; preserve verified state and make the next action unambiguous.
---

# Handoff

Use this skill to transfer verified state between sessions or agents. It records state; it does not own execution or authorize external changes.

## Procedure

1. Finish and verify the current atomic step. Stop nested writers before pausing. Do not start a new scope near a context boundary, and do not leave a known-broken edit without recording the reason and recovery step.
2. Preserve uncommitted work explicitly. Commit, push, or open a pull request only when the user or repository policy authorizes it.
3. Write exactly one resume note with these sections, in this order:
   - Goal
   - Decisions
   - Changed files
   - Evidence
   - Session
   - Next step
4. Collect changed files with `git status --short --untracked-files=all -z -- .`. Parse Porcelain v1 records as NUL-delimited UTF-8, preserve ordinary paths verbatim, consume the extra source field for rename/copy records, and record only the destination. Reject missing fields, invalid statuses, and output without a trailing NUL.
5. Represent `Changed files` as a JSON string array, for example `- Changed files: ["src/app.ts", "日本語,comma.txt"]`; use `none` when there are no files. Do not use a lossy comma-separated string.
6. Store the note at the configured resume-note destination. If no destination is configured, use `~/.codex/handoff-resume.md`. Report the exact location. Do not claim that another agent or harness consumed the note unless that consumption was observed.
7. For a wait, state the event that ends the wait and use a bounded watcher. For a pickup, inspect the changed artifacts and verify the captured evidence before repeating discovery.

## Reply

Report the completed state, evidence, resume-note location, and exact next step. Separate completed work from pending work and state the remaining risk when verification is incomplete.
