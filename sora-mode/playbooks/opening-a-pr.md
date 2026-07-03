### Opening a PR

Invoked at the end of every other playbook.

**Worktree.** Work from a git worktree off main; subagents inherit it. Multiple Agent calls on the same branch each get their own worktree (`isolation: worktree`), or `git fetch && git reset --hard origin/<branch>` between them. Dirty branch with unrelated work: patch out, fresh worktree, apply. Snarled worktree: reset from main, redo minimally.

**Commits.** Commit liberally; rebase into small, ordered commits before opening PRs. Each commit is a future PR: landable, ordered to tell the story. Amend when the fix belongs in a just-made commit; new commit when separable. Commit messages per the global rule: simplicity first, then clarity of intent.

**PRs.** Run `/simplify` over the diff before commit; write the PR description and commit bodies per **Writing the reply**. Small PRs, 5 narrow over 1 fat; stack follow-ups, branch off main only for genuinely independent work. For stacked PRs, use whatever stacking tool the team uses; the principle is small, ordered slices with the stack visible to reviewers. `gh pr view <number>` before referencing PR status. Rebase on `main` before substantial stack work. No `## Summary` / `## Test plan` boilerplate on small PRs; commit bodies don't restate the subject. After opening, **babysit** the follow-up yourself: watch `gh pr checks`, read review comments, triage fix / dismiss-with-reason / ask, and push back when feedback drifts from intent.

A subagent that opens a PR runs **interrogate** and `/simplify`, returns the URL, and does NOT babysit. Return to the parent.
