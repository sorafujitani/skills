# Plan

Produce a phased implementation plan grounded in the **Principles** section of the `sora-mode` skill. The plan is the deliverable. Do not implement.

Open a todolist with one item per step below.

## 0. Triage

Skip the plan when the change is one or two files with an obvious approach. Say so and stop.

Plan when the change spans three or more files, introduces architecture, has competing approaches or unclear scope, or the user asked for one.

## 1. Re-read principles

Read the **Principles** section of the `sora-mode` skill end to end, and the brain leaf files it indexes (`~/brain/principles/`). The principles govern every plan decision; cross-link them.

## 2. Scope and constraints

State your read of scope and constraints in one paragraph. Use AskUserQuestion only for genuinely ambiguous intent (the **never-block-on-the-human** principle); give concrete options with each open question.

Resolve what is in scope vs explicitly out, technical or platform constraints, patterns to preserve, and the definition of done.

## 3. Explore in subagents

Delegate codebase exploration (the **guard-the-context-window** principle).

- Use `Explore` subagents for read-only recon; `general-purpose` for broader digs. Don't rely on the built-in `Plan` agent to apply this skill; it doesn't read sora-mode.
- Omit `model` so explorers inherit the session model; a light model only for bulk mechanical scans.

Each explorer returns file pointers, conventions, dependencies, test infrastructure, and entry points. No inlined dumps.

## 4. Write the plan

Plans live in the project's `.claude/plans/` (the configured plansDirectory) unless the user says otherwise.

Single file `NN-slug.md` for small plans. For three or more phases, a directory with `overview.md` plus phase files:

```
NN-slug/
├── overview.md
├── phase-1-scaffold.md
├── phase-2-...md
└── testing.md
```

### Phase sizing

- One function or type plus tests, or one bug fix. Not "one file".
- Two to three files touched, max.
- Prefer eight to ten small phases over three to four large ones to preserve option value (the **foundational-thinking** principle).
- Split if a phase has more than five test cases or three functions.

### Overview file

- **Context.** Problem and why now.
- **Scope.** Included; explicitly excluded.
- **Constraints.** Technical, platform, dependency, pattern.
- **Alternatives.** Two or three approaches sketched, choice and rationale (the **exhaust-the-design-space** principle). Skip when constraints dictate one.
- **Applicable skills.** Domain skills the implementer should invoke, by name.
- **Phases.** Ordered standard-markdown links to phase files.
- **Verification.** Project-level commands.
- **Implementation guidance.** Per section 6.

### Phase files

- Back-link to overview.
- **Goal.** What the phase accomplishes.
- **Changes.** Files affected and the change at a high level. What and why, not how. No code snippets.
- **Data structures.** Name the key types or schemas. One-line sketch only (the **foundational-thinking** principle).
- **Verification.** Per section 5.

Order phases so infrastructure and shared types land first (the **foundational-thinking** principle). Each phase should be independently shippable.

For changes touching existing code, apply the **redesign-from-first-principles** principle: if we'd built this with the new requirement on day one, what would it look like? Redesign holistically; deliver incrementally.

If a phase creates or edits a skill, the phase instructs the implementer to use the **create-skill** skill.

## 5. Verification per phase

Each phase needs both:

**Static.** Type check, lint, project tests pass.

**Runtime.** Exercise the feature on the matching surface (**control**):

- Browser / Electron / Web UIs: the `agent-browser` skill or Chrome tools.
- CLIs, TUIs, and servers: the `run` and `verify` skills.
- Native mobile: whatever simulator-driving tooling the project has.
- No way to drive the touched surface: flag it in the plan.

For bug fixes, the loop is reproduce on the surface, fix, verify on the same surface. Unit tests show a branch behaves a certain way; they do not prove the bug is gone (the **prove-it-works** principle).

## 6. Implementation guidance

In the overview, name which sora-mode non-negotiables the implementer must apply, by name:

- **how** over each unfamiliar subsystem before changing it.
- **interrogate** for adversarial review on contested designs before shipping.
- `/simplify` over each diff before commit; every prose surface per **Writing the reply**.
- the **show-me-your-work** decision trail when the plan is large enough to need an auditable record.
- **babysit** the PR follow-up after opening it.

## 7. Hand back

Summarize phases, scope boundaries, applicable skills, and verification. Stop. The user decides when implementation starts.
