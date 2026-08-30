# Skill management

- This checkout owns standalone personal skills. Edit the real package here;
  `~/.agents/skills`, `~/.codex/skills`, and `~/.claude/skills` are discovery paths.
- When using skill-creator or another skill-authoring workflow, explicitly set
  its output directory to this checkout for standalone personal skills. Validate
  the completed package, register it with `manage_skills.py register`, then run
  `check`; generating files alone does not complete local registration.
- Resolve an existing skill through the local manifest before updating it.
  Repository-scoped skills, plugin skills, and app-managed artifact templates
  keep their owner's prescribed location. Do not patch the bundled creator or
  plugin cache to impose personal placement rules.
- Do not copy a package between host directories or run `atlantis skills sync`
  to replicate this library. Run `python3 scripts/manage_skills.py check` and
  `python3 scripts/manage_skills.py link` to inspect or create references.
- External packages stay outside this repository. Use the Codex skill installer
  through `scripts/manage_skills.py install`; preserve source, ref, and license.
  Never overwrite a locally modified install during an update.
- Skills owned by another project stay in that project, or in that project's
  managed install location. Do not vendor them into this standalone library.
- Do not stage all files or publish untracked personal skills automatically.
  Review publication scope and local paths before an explicitly requested push.
- Validate changes with `atlantis skills check .`, `git diff --check`, and
  `python3 scripts/manage_skills.py check`. Plugin caches and `.system` belong to
  their respective installers and are outside this library's scope.
