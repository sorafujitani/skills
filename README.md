# Agent Skills

A collection of agent skills I use day-to-day across Claude Code, Codex, Cursor, and other agents that follow the [open agent skills](https://github.com/vercel-labs/skills) convention.

## Install

Use [`skills`](https://github.com/vercel-labs/skills) to install any single skill, or browse them all interactively:

```bash
# install one skill (replace <skill> with any name from the catalog below)
npx skills add sorafujitani/skills/<skill>

# pick from a list
npx skills add sorafujitani/skills

# install everything for Claude Code only
npx skills add sorafujitani/skills --skill '*' -a claude-code -g -y
```

Each skill ends up at `~/.claude/skills/<skill>/SKILL.md` (or the equivalent directory for other agents).

## Catalog

### Coding modes

Hands-on modes that hold the keyboard for you instead of writing code on your behalf.

- **guided-coding** — The agent never writes code; it tells you what to write and where, phase by phase, until the task is done.

  ```bash
  npx skills add sorafujitani/skills/guided-coding
  ```

- **print-debugging** — One step, one observation. Place a `println` / `console.log`, run, read, then decide the next probe — both to chase a bug and to learn an unfamiliar codebase.

  ```bash
  npx skills add sorafujitani/skills/print-debugging
  ```

### Planning & design

Read-only modes for thinking through a change before any code moves.

- **dry-coding** — Plan-mode wrapper for PR- to epic-sized design. Parallel Explore/Plan sub-agents, schema contracts, and a design doc plus reviewable dry-coded implementation under `.claude/plans/`. No file edits.

  ```bash
  npx skills add sorafujitani/skills/dry-coding
  ```

- **analyzing-issues** — Four-phase analysis of an OSS issue or feature request: independent parallel investigation, hypothesis/refutation cycles, evidence scoring, then a TDD-shaped implementation plan with cited sources.

  ```bash
  npx skills add sorafujitani/skills/analyzing-issues
  ```

### Pull requests

- **planning-pr-comments** — Pull the unresolved review comments on the current branch's PR, classify them (Critical / Important / Minor), and produce an ordered remediation plan.

  ```bash
  npx skills add sorafujitani/skills/planning-pr-comments
  ```

- **generating-prs** — Generate a PR from the current git state in a standard format (no Linear integration).

  ```bash
  npx skills add sorafujitani/skills/generating-prs
  ```

### Code review

- **reviewing-code** — Multi-agent code review. Four sub-agents review in parallel, each finding is checked for code existence and backed by official docs (WebSearch) to keep hallucinations out, then explained with prerequisite knowledge for the reader.

  ```bash
  npx skills add sorafujitani/skills/reviewing-code
  ```

### Testing

- **exploratory-testing** — Detect the project's interface (CLI / API / Web API / GUI) and run an exploratory test pass end-to-end: plan → implement → execute → report.

  ```bash
  npx skills add sorafujitani/skills/exploratory-testing
  ```

- **property-based-testing** — Static analysis of the target picks property patterns, composes generators, generates the test code, runs it, and reports — across whatever PBT framework is in the project.

  ```bash
  npx skills add sorafujitani/skills/property-based-testing
  ```

### Utilities

- **karin-info** — Pulls the latest news, releases, live dates and links about singer-songwriter Karin. via WebSearch / WebFetch.

  ```bash
  npx skills add sorafujitani/skills/karin-info
  ```

- **finding-local-repos** — Resolve another repository's path on the local machine, regardless of how the developer organises their workspace, using `fd`.

  ```bash
  npx skills add sorafujitani/skills/finding-local-repos
  ```

- **doc-prerequisite-knowledge** — Explain a topic from its prerequisite knowledge upward, with verified official-doc links at every step. Triggered by requests like 「〜について基本と前提知識から理解できるように教えて」 / "explain X from basics including prerequisites".

  ```bash
  npx skills add sorafujitani/skills/doc-prerequisite-knowledge
  ```

## Local development

This repository lives directly at `~/.claude/skills/` on my own machine, which is the path Claude Code already loads user skills from. Editing a skill's `SKILL.md` here means the change is picked up by the next Claude Code session — no symlinks, no `npx skills add` round-trip.

### Adding a new public skill

1. Create `<skill-name>/SKILL.md` at the repo root with YAML frontmatter (`name`, `description`).
2. `git add <skill-name>/ && git commit && git push`.

Skill names follow the [Anthropic Agent Skills naming conventions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#naming-conventions): lowercase letters, numbers, and hyphens only; gerund or short noun-phrase form; no vague labels (`helper`, `utils`, …) or reserved words (`anthropic`, `claude`).

### Keeping private skills out

Private skills stay in the same `~/.claude/skills/` directory but are listed in `.gitignore` and remain untracked. Add a directory name to `.gitignore` before its first `git add` to keep it local-only.

### Bootstrapping on a new machine

```bash
# Move any pre-existing private skills out of the way first if you have them.
git clone git@github.com:sorafujitani/skills.git ~/.claude/skills
# Drop your private skills back into ~/.claude/skills/. They remain untracked
# as long as their directory name is listed in .gitignore.
```

## License

MIT — see [LICENSE](./LICENSE).
