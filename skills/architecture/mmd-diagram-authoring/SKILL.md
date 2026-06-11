---
name: mmd-diagram-authoring
description: Author and validate Mermaid architecture diagrams.
version: 0.1.0
author: html-to-editable-pptx project
license: MIT
metadata:
  hermes:
    tags: [architecture, diagrams, mermaid, mmd, action-items, repository]
    category: architecture
    related_skills: [consensus-recording, interview-facilitation]
---

# MMD Diagram Authoring Skill

Author durable Mermaid `.mmd` architecture diagrams from evolving design conversations. This skill preserves the project method: choose action-item keywords first, test adjacent action pairs in natural language, stabilize the macro plot, then decompose accepted actions into lower-level diagrams. This is a skill, not a core tool: the fragile part is diagram judgment and authoring discipline, and the only bundled tool is a lightweight `.mmd` checker.

Good MMD diagrams are not dense drawings: they lock one responsibility level, expose missing consensus, and create a stable path to the next lower level.

When asked to *critique or review* architecture diagrams — or when macro alignment is unstable — read `references/architecture-diagram-evaluation.md` first and evaluate against it: consensus-layer checks precede `.mmd` authoring.

## When to Use

- The user asks to create, critique, revise, or save Mermaid/MMD diagrams.
- The diagram needs action-item labels, reviewer decisions, artifact lineage, or evidence/report boundaries.
- Accepted diagrams should be stored as repository `.mmd` files.
- Korean and English label variants need to stay structurally aligned.
- The user asks to lock macro alignment before micro details, preserve artifact lineage, expose decision ownership, or detect consensus gaps in diagrams.

Do not use this for decorative diagrams, one-off unsaved sketches, or diagrams that require a notation other than Mermaid.

## Modes

- **Interactive authoring** — exploratory work with the user: pick the layer, draft action labels, tune pairs, iterate until the user accepts. Reviewer-only checks live here; these map to the Human-judged items in Verification.
- **Batch validation** — mechanical upkeep of accepted diagrams: save raw `.mmd`, run the checker, keep en/ko variants aligned. Checker-backed checks live here; these map to the Machine-verified items in Verification, and no design decisions are made in this mode.

## Prerequisites

- Python 3 (stdlib only) for the bundled checker.
- Target diagrams live under a repository path such as `docs/diagrams/architecture/`; the directory must exist before saving.
- Familiarity with the project's consensus record is assumed when diagrams encode agreed decisions (see related skills).

## How to Run

Interactive authoring: pick the diagram layer with the user, draft action-item labels, tune adjacent pairs in natural language, iterate until accepted.

Batch validation: save raw Mermaid under the target path and run `python scripts/check_mmd_files.py <target-directory>` from the skill directory (from repo root, prefix the skill path).

## Quick Reference

| Need | Action |
|---|---|
| Start a new architecture diagram | Pick 5-7 action items, not nouns |
| Check flow naturalness | Read each adjacent pair as a sentence |
| Refine a crowded diagram | Split into macro lifecycle and one subflow at a time |
| Save accepted diagram | Write raw Mermaid to `docs/diagrams/architecture/*.mmd` |
| Validate saved files | Run `python scripts/check_mmd_files.py <target-directory>` |

## Procedure

1. **Clarify the layer.** Ask whether the user wants the macro lifecycle or a subflow. Do not mix all layers in one diagram.

2. **Draft action-item keywords.** Prefer action labels over nouns. Use labels such as `Register artifact input draft`, `Generate candidate PPTX`, or `Collect validation evidence`.

3. **Tune pairs in natural language.** For every edge, read the pair as a sentence. If the sentence feels unnatural, rename or reorder the action items before adding detail.

4. **Stabilize the macro plot before micro details.** First produce a small lifecycle diagram. Only after the user accepts it, create subflow diagrams for one action at a time.

5. **Name decision owners.** Decision nodes should show the actor when it matters, e.g. `Reviewer decides: accept or request revision?`, not just `Accept?`.

6. **Preserve lineage.** If a flow creates a revised artifact, route it through an explicit action such as `Register revised source artifact` or `Publish immutable source artifact revision`. Do not jump directly from feedback to a conversion job.

7. **Separate evidence and reports.** Keep source analysis evidence, render evidence, validation evidence, and final reports distinct unless the diagram is explicitly about an evidence bundle.

8. **Show concrete outputs.** If an action computes a digest, binds a manifest, delivers a PPTX, or publishes a revision, make that output visible in the label or adjacent step.

9. **Save only accepted diagrams.** Store raw Mermaid only. Do not include Markdown fences in `.mmd` files.

10. **Validate `.mmd` files.** Run the bundled checker when available.

## Project-local references

This skill stays portable by keeping project decomposition and glossary material in separate references. When you are working inside `html-to-editable-pptx`, consult:

- `references/project-diagram-layers.md` for this repository's current layer map.
- `references/project-label-vocabulary.md` for current action-label examples and the English/Korean glossary.

Treat both references as project-local aids, not as generic authoring rules.

## Labeling Principles

Prefer action labels over nouns, and treat any concrete labels as examples rather than as portable standards. If a project maintains a glossary, keep the glossary below the consensus layer and update the skill only when the *principle* changes.

When producing Korean variants, keep the structure identical to the English file and translate labels consistently. Project-specific translations belong in a glossary or reference file, not in the portable skill body.

## File Naming

Use stable numeric prefixes and language suffixes:

```text
docs/diagrams/architecture/01_artifact_session_lifecycle.en.mmd
docs/diagrams/architecture/02_source_artifact_registration.en.mmd
docs/diagrams/architecture/02_source_artifact_registration.ko.mmd
```

Use lowercase snake case after the numeric prefix. Use `.en.mmd` and `.ko.mmd` when maintaining parallel language variants.

## Hermes Placement and Management

Bundled project skills live under `skills/<category>/<name>/`; Hermes exposes
them via `skills_list` / `skill_view` / `skill_manage`. Keep frontmatter
discoverable; details belong to the Hermes documentation, not this skill.

## Bundled Script

Use the lightweight checker after saving `.mmd` files:

```bash
python scripts/check_mmd_files.py docs/diagrams/architecture
```

The checker validates machine-checkable structure only: Mermaid declaration, no Markdown fences, no tabs, non-empty targets, and en/ko structural parity when both variants exist. It does not replace human diagram review.

## Pitfalls

- **Noun-first diagrams.** They hide system motion. Convert nouns into action items before drawing.
- **Instance labels.** `v1` and `v2` make architecture diagrams look like one execution trace. Use `initial`, `revised`, or parameterized terms.
- **Implicit actors.** `Accept?` is ambiguous. Write `Reviewer decides` when user/reviewer judgment is part of the design.
- **Hidden lineage.** Do not route feedback directly into a conversion job; register or publish the revised artifact first.
- **Evidence mixing.** Do not collapse source analysis, render evidence, validation evidence, and reports into one box unless that is the explicit subject.
- **Overloaded diagrams.** If a graph has too many concerns, split it into a lifecycle diagram and subflow diagrams.

## Verification

### Machine-verified (run the checker)

- saved `.mmd` files pass `scripts/check_mmd_files.py`: declaration, no fences, no tabs, en/ko structural parity when both variants exist, non-empty target

### Human-judged (cannot be delegated to the checker)

- the user accepts the macro plot or targeted subflow
- every edge reads naturally as an action-to-action sentence
- decision nodes name the decision owner when required
- artifact revision and provenance boundaries remain explicit
- Korean labels translate the English labels consistently (translation quality)
