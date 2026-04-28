# 設計ドキュメントテンプレート

出力先: `.claude/plans/design-{YYYY-MM-DD}-{short-desc}.md`

## テンプレート

```markdown
# System Design: {title}

## Meta
- **Source**: {issue-url | requirements text}
- **Repository**: {owner/repo}
- **Date**: {YYYY-MM-DD}
- **Language/Framework**: {detected}
- **Granularity**: {PR | epic}
- **Evaluation Score**: {N}/35 ({classification})

## Requirements
### Functional
- {FR-1}: {description}
### Non-Functional
- {NFR-1}: {description}
### Constraints
- {C-1}: {description}

## Architecture Overview

### Component Diagram
{mermaid or ASCII diagram}

### Design Pattern
**Pattern**: {name}
**WHY**: {rationale with codebase evidence}
**Prerequisite**: {concept explanation}
**Reference**: [{doc}]({url})

## Component Design

### {Component Name}
- **Responsibility**: {single responsibility description}
- **Interface**:
  ```{lang}
  {key function signatures / type definitions}
  ```
- **Dependencies**: {list}
- **Test Strategy**: {unit/integration approach}

## Data Flow
### Happy Path
{sequence description or diagram}
### Error Path
{error propagation and recovery}

## Design Evaluation
| Dimension | Score | Evidence |
|-----------|-------|----------|
| D1: Testability | /5 | {cite code} |
| D2: Changeability | /5 | |
| D3: Pattern Fit | /5 | |
| D4: Lang/Runtime Fit | /5 | |
| D5: Dependency Mgmt | /5 | |
| D6: Error Handling | /5 | |
| D7: Performance | /5 | |
| **Total** | **/35** | **{class}** |

## Design Decisions
### DD-{N}: {title}
- **Choice**: {what was chosen}
- **WHY**: {rationale}
- **Rejected**: {alternatives and why rejected}
- **Prerequisite Knowledge**: {concept}
- **Reference**: [{doc}]({url})

## Implementation Roadmap
<!-- PR granularity -->
### Step {N}: {description}
- **Files**: {list}
- **Depends on**: {prior steps}
- **Test**: {what to verify}

## PR Split Plan
<!-- Epic granularity only -->
### PR-{N}: {title}
- **Scope**: {description}
- **Files**: {list}
- **Depends on**: {prior PRs}
- **Merge strategy**: {note}

## Risk Assessment
| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| {desc} | H/M/L | H/M/L | {approach} |

## Prerequisite Knowledge
| Concept | Reference | Relevance |
|---------|-----------|-----------|
| {name} | [{doc}]({url}) | {why it matters} |
```

## 粒度別セクション選択

| セクション | PR | Epic |
|-----------|:---:|:----:|
| Implementation Roadmap | o | - |
| PR Split Plan | - | o |
| 他のセクション | o | o |
