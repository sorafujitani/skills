# Skills

A collection of custom skills for Claude Code, distributed as a plugin marketplace.

## Installation

### From the marketplace

Add this repository as a plugin marketplace in Claude Code:

```
/plugin marketplace add sorafujitani/skills
```

Then install individual plugins:

```
/plugin install karin-info@sorafujitani-skills
```

### Manual installation

Alternatively, copy a skill directory directly into your Claude Code skills folder:

```bash
git clone https://github.com/sorafujitani/skills.git
cp -r skills/plugins/karin-info/skills/karin-info ~/.claude/skills/
```

## Available Plugins

| Plugin | Description |
|--------|-------------|
| [karin-info](./plugins/karin-info/skills/karin-info/SKILL.md) | Fetches and organizes the latest information about singer-songwriter Karin. via web search |

### karin-info

Collects the latest information about Karin. via WebSearch / WebFetch and organizes it into:

- News
- Releases (singles / albums / EPs)
- Live events & concerts
- Related links

Example usage:

```
Tell me the latest news about Karin.
Look up Karin.'s upcoming live events
```

See [SKILL.md](./plugins/karin-info/skills/karin-info/SKILL.md) for details.
