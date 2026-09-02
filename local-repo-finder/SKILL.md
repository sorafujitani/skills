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

`fd` is preferred; fall back to `find` when it is missing. In a ghq-managed environment `ghq list -p <name>` also resolves the path.
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

Use `find` if `fd` is not installed:
```bash
find ~/ -type d -name ".git" 2>/dev/null | xargs -I {} dirname {} | grep "<REPO_NAME>$" | head -1
```


## Boundaries

- Search under `~/` only (searching from `/` is slow).
- When multiple repositories match, show the candidates and ask which one to use.

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
