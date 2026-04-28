---
name: local-repo-finder
description: |
  Quickly detect Git repository paths in local environments.
  Use when referencing another repository or absorbing directory layout differences across developers.
  Triggered by requests like "find repository", "locate repo", "repository location", "search path", "reference another repository".
---

# Local Repository Finder

A skill that quickly detects the path of a specified Git repository in local environments.
Absorbs different directory structures across developers and enables shareable Workflows.

## When to Use

- Reference another repository in SlashCommands or AgentSkills
- Reference local-specific paths from team-shared resources
- Automate cross-repository tasks

## Prerequisites

`fd` command is required (approximately 30x faster than `find`).
```bash
# macOS
brew install fd

# Ubuntu/Debian
apt install fd-find

# Arch Linux
pacman -S fd
```

## Instructions

### Step 1: Identify Repository Name

Confirm the repository name the user wants to reference.

### Step 2: Detect Path

Search for `.git` directories using the following command to get the repository root path.
```bash
fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "<REPO_NAME>$" | head -1
```

Replace `<REPO_NAME>` with the actual repository name and execute.

### Step 3: Store as Variable

Save the detected path to a variable for use in subsequent operations.
```bash
REPO_ROOT="$(fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "<REPO_NAME>$" | head -1)"
```

## Command Reference

| Option | Description |
|--------|-------------|
| `fd` | Fast alternative to find command |
| `-H` | Include hidden files/directories in search |
| `"^\.git$"` | Exact match for `.git` name (regex) |
| `~/` | Start search from home directory |
| `-t d` | Search directories only |
| `2>/dev/null` | Suppress error output |

## Examples

### Basic Usage
```bash
# Detect hogerepo repository
fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "hogerepo$" | head -1
# => /Users/username/dev/work/hogerepo

# Work with detected path
REPO_ROOT="/Users/username/dev/work/hogerepo"
cat "${REPO_ROOT}/package.json"
ls "${REPO_ROOT}/src/"
```

### Usage in SlashCommands
```markdown
## Phase 1: Repository Detection

Identify the target repository with the following command:

fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "target-repo$" | head -1

Use the detected path as `TARGET_ROOT` in subsequent operations.

## Phase 2: File Reference

- Entry point: `${TARGET_ROOT}/src/main.ts`
- Config file: `${TARGET_ROOT}/config/default.json`
```

### Detecting Multiple Repositories
```bash
# Show all matches when multiple exist
fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "api$"

# Narrow down with more specific pattern
fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "project-a/api$" | head -1
```

## Fallback

Use `find` if `fd` is not installed (approximately 30x slower):
```bash
find ~/ -type d -name ".git" 2>/dev/null | xargs -I {} dirname {} | grep "<REPO_NAME>$" | head -1
```

## Performance

| Command | Execution Time | Notes |
|---------|----------------|-------|
| `fd` | ~2.4 sec | Fastest, recommended |
| `find` | ~1 min 19 sec | ~32x slower than fd |
| `ghq list` | ~1 min 50 sec | Environment dependent, slowest |

## Boundaries

### DO NOT

- Do not search from outside home directory (e.g., `/`)
- Do not modify files in detected paths without permission
- Do not output authentication credentials or `.env` file contents

### ASK FIRST

- When multiple repositories match, ask which one to use
- Confirm before modifying files in detected repositories

## Troubleshooting

### fd: command not found
```bash
# Check installation
which fd || which fdfind

# On Ubuntu, it may be named fdfind
alias fd=fdfind
```

### Repository Not Found
```bash
# Search with partial match
fd -H "^\.git$" ~/ -t d 2>/dev/null | xargs -I {} dirname {} | grep "<PARTIAL_NAME>"
```

## References

- [fd - GitHub](https://github.com/sharkdp/fd)
- [Original Article (Zenn)](https://zenn.dev/soramarjr/articles/e0de39a73bfbcd)
