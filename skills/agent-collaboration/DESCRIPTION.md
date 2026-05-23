---
description: Patterns for multi-agent collaboration where one agent handles interviews and consensus while another handles environment-bound execution.
---

# Agent Collaboration

Skills in this category cover the workflow where a *facilitating agent* (interview, consensus recording, instruction writing) hands off work to an *executing agent* (git operations, code execution, environment-bound actions).

The split is grounded in two practical constraints that recur across projects:

1. **Environment asymmetry.** The facilitating agent often does not have git, network, or filesystem access to the target repository. The executing agent does. Skills here treat that asymmetry as the design center, not as a workaround.
2. **Consensus is fragile.** Decisions made through interviews lose precision when re-stated. Skills here include patterns for recording consensus in a form that survives handoff to a different agent or to a later session.

These skills are *project-agnostic*. They do not assume any specific repository structure, file naming, or domain vocabulary. Project-specific facts (e.g. settled meta-decisions, file-naming rules) belong in the project's own consensus document, not in these skills.

## Skills in this category

- [`interview-facilitation`](./interview-facilitation/SKILL.md) — Run a structured one-decision-per-turn interview with depth-over-roundtrips bias.
- [`consensus-recording`](./consensus-recording/SKILL.md) — Record interview outcomes as a non-authoritative repository document with prose for humans and a YAML index for agents.
- [`task-delegation`](./task-delegation/SKILL.md) — Write self-contained instruction sheets that hand mechanical work to another agent with explicit environment requirements.
- [`evaluation-followup`](./evaluation-followup/SKILL.md) — Process external evaluation findings into prioritized work groups with clear dependencies.
- [`session-handoff`](./session-handoff/SKILL.md) — When context grows too large, split outputs into a one-time session summary and a permanent methodology Skill.
- [`iteration-resilience`](./iteration-resilience/SKILL.md) — Diagnose and recover when the same instruction halts repeatedly, by treating environment assumptions as falsifiable.
