# Agent Skill Promotion Plan v0.1

| Item | Value |
|---|---|
| Document type | Project-local planning note |
| Status | Drafted from repeated execution incidents and parser hardening work |
| Source records | `docs/agent_execution_lessons_v0.1.md`, `docs/fixture_matrix_v0.1.md`, MMD skill hardening reviews |
| Scope | Decide which repeated patterns become new skills, existing skill references, or project-local docs |

## 1. Purpose

This plan converts repeated incidents into reusable agent-skill material.
It is not a new architecture decision and it does not replace the existing
execution lessons document. Its job is to classify each repeated pattern by the
right durable home.

The conversion rule is:

> Do not copy "what happened to us" into a skill. Rewrite it as the next
> agent's mode choice, gate commands, halt conditions, and verification contract.

## 2. Classification Rules

Promote a pattern to a **new skill** when it:

- applies across repositories or tasks;
- requires an agent to choose a mode before acting;
- has an ordered read -> decide -> act -> verify workflow;
- can cause harmful publish, staging, deletion, or false verification if missed;
- has a clear frontmatter trigger.

Add a pattern to an **existing skill or reference** when it:

- belongs to an already-owned workflow;
- is a checklist, edge-case set, or judgment aid rather than a standalone mode;
- would make skill selection ambiguous if split out.

Keep a pattern as a **project-local doc** when it:

- names specific commits, files, products, fixtures, or incidents;
- describes current project state rather than reusable procedure;
- would mislead another repository if copied unchanged.

## 3. Candidate Disposition

| Candidate | Home | Rationale |
|---|---|---|
| Agent Execution Gate / Handoff Discipline | New skill: `skills/agent-collaboration/repo-execution-gate/` | Independent mode choice and publish safety gate for delegated repo execution |
| Probe-First Regression Matrix | New skill or `cross-representation-verification` follow-up | Independent workflow for parser/layout/converter fixture growth |
| False-Green Verification Hardening | Existing verification skill reference | Edge-case checklist for narrowing checker guarantees |
| Doc-Code Contract Sync / Disposition Recording | Existing `doc-code-sync-checker` reference | Review finding disposition is part of document/code consistency |
| Skill Boundary Hardening | Existing skill-creation reference | Portable vs project-local boundary is a skill-authoring rule |
| External Renderer Crash Guard | Reference under probe-first matrix | Renderer instability is a conditional guard, not a standalone workflow |
| Specific MMD/parser incident history | Project-local docs | Repo-specific facts and evidence belong in docs, not portable skills |

## 4. Work Order

1. Add `repo-execution-gate` as the first new skill.
2. Add or fold in `probe-first-regression-matrix`.
3. Add reference-level hardening for false-green checks, review disposition,
   and skill-boundary rules.
4. Keep project-specific logs, SHAs, fixture inventories, and crash reports in
   docs rather than skill bodies.

## 5. Done Criteria

- New skill bodies contain no project-specific commit IDs, product decisions, or
  local incident narratives.
- Each new skill has a Hermes-discoverable frontmatter description.
- Existing category indexes mention any new skill.
- Reference candidates are not duplicated in both SKILL.md and references.
- `git diff --check` passes before any commit.
