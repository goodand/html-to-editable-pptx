---
name: mmd-diagram-authoring
description: Use when creating, critiquing, refining, or saving Mermaid .mmd architecture diagrams from design discussions, especially when macro-first plot tuning, action-item labels, pairwise natural-language checks, Korean/English variants, and repository-saved Mermaid files are required.
version: 0.1.0
author: html-to-editable-pptx project
license: MIT
metadata:
  hermes:
    tags: [architecture, diagrams, mermaid, mmd, action-items, repository]
    related_skills: [consensus-recording, interview-facilitation]
---

# MMD Diagram Authoring

## Overview

Author durable Mermaid `.mmd` architecture diagrams from evolving design conversations.
This skill preserves the project method: choose action-item keywords first, test adjacent action pairs in natural language, stabilize the macro plot, then decompose accepted actions into lower-level diagrams.

This is a skill, not a core tool. The fragile part is diagram judgment and authoring discipline. The only bundled tool is a lightweight `.mmd` structural checker.

## When to Use

- The user asks to create, critique, revise, or save Mermaid/MMD diagrams.
- The user wants macro-first architecture alignment before micro-level detail.
- The diagram needs action-item labels, reviewer decisions, artifact lineage, or evidence/report boundaries.
- Accepted diagrams should be stored as repository `.mmd` files.
- Korean and English label variants need to stay structurally aligned.

Do not use this for decorative diagrams, one-off unsaved sketches, or diagrams that require a notation other than Mermaid.

## Quick Reference

| Need | Action |
|---|---|
| Start a new architecture diagram | Pick 5-7 action items, not nouns |
| Check flow naturalness | Read each adjacent pair as a sentence |
| Refine a crowded diagram | Split into macro lifecycle and one subflow at a time |
| Save accepted diagram | Write raw Mermaid to `docs/diagrams/architecture/*.mmd` |
| Validate saved files | Run `scripts/check_mmd_files.py` on the target directory |

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

## Diagram Layers

Use this sequence unless the user asks for a different part:

1. **Artifact session lifecycle**: register source, generate candidate, collect evidence, assess, accept or request revision.
2. **Source artifact registration**: draft input, validate, resolve, materialize, manifest, publish revision, create job.
3. **Frozen input manifest lifecycle**: records, blob refs and hashes, provenance, rendering environment metadata, canonicalization, closure validation, digest, revision binding.
4. **Conversion job lifecycle**: render source, extract visual evidence, build IR, map objects, generate PPTX.
5. **Validation evidence lifecycle**: render generated PPTX, compare visual output, validate editability, produce final report.
6. **Revision workflow lifecycle**: create revision request bundle, run authenticated revision, register or publish revised source artifact.

## Label Vocabulary

Prefer:

- `Register artifact input draft`
- `Validate bundle shape and entrypoint`
- `Resolve local and external references`
- `Materialize and fingerprint resolved inputs`
- `Write frozen input manifest`
- `Publish immutable source artifact revision`
- `Create conversion job for published revision`

Avoid:

- `Create v1` / `Create v2` labels in architecture diagrams. Use parameterized or role-based language instead.
- `Run conversion` when the purpose is clearer as `Generate candidate PPTX`.
- `Gather evidence` when the intended evidence is validation-specific; use `Collect validation evidence`.
- `Record environment assumptions`; use `Record rendering environment metadata`.
- `Seal manifest` when the real outputs are digest computation and revision binding.

## Korean Labeling

When producing Korean variants, keep the structure identical to the English file and translate labels consistently.

Preferred translations:

| English | Korean |
|---|---|
| Artifact revision session | 아티팩트 리비전 세션 |
| Register artifact input draft | 아티팩트 입력 초안 등록 |
| Validate bundle shape and entrypoint | 번들 구조와 진입점 검증 |
| Resolve local and external references | 로컬 및 외부 참조 해석 |
| Materialize and fingerprint resolved inputs | 해석된 입력을 실체화하고 지문 생성 |
| Write frozen input manifest | 고정 입력 매니페스트 작성 |
| Publish immutable source artifact revision | 불변 소스 아티팩트 리비전 발행 |
| Create conversion job for published revision | 발행된 리비전에 대한 변환 작업 생성 |

## File Naming

Use stable numeric prefixes and language suffixes:

```text
docs/diagrams/architecture/01_artifact_session_lifecycle.en.mmd
docs/diagrams/architecture/02_source_artifact_registration.en.mmd
docs/diagrams/architecture/02_source_artifact_registration.ko.mmd
```

Use lowercase snake case after the numeric prefix. Use `.en.mmd` and `.ko.mmd` when maintaining parallel language variants.

## Hermes Placement and Management

- Keep bundled project skills under `skills/`, organized by category.
- Use `optional-skills/` only for skills that should ship with the repo but not load by default.
- External or community skills should be managed outside this folder and installed through Hermes skill management.
- Hermes exposes skills through `skills_list`, `skill_view`, and `skill_manage`; keep `name`, `description`, tags, and related skills clear enough for discovery.

## Bundled Script

Use the lightweight checker after saving `.mmd` files:

```bash
python skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py docs/diagrams/architecture
```

The checker validates repository hygiene only: Mermaid declaration, no Markdown fences, and no tabs. It does not replace human diagram review.

## Pitfalls

- **Noun-first diagrams.** They hide system motion. Convert nouns into action items before drawing.
- **Instance labels.** `v1` and `v2` make architecture diagrams look like one execution trace. Use `initial`, `revised`, or parameterized terms.
- **Implicit actors.** `Accept?` is ambiguous. Write `Reviewer decides` when user/reviewer judgment is part of the design.
- **Hidden lineage.** Do not route feedback directly into a conversion job; register or publish the revised artifact first.
- **Evidence mixing.** Do not collapse source analysis, render evidence, validation evidence, and reports into one box unless that is the explicit subject.
- **Overloaded diagrams.** If a graph has too many concerns, split it into a lifecycle diagram and subflow diagrams.

## Verification

A diagram pass is complete when:

- The user accepts the macro plot or targeted subflow.
- Every edge reads naturally as an action-to-action sentence.
- Decision nodes name the decision owner when required.
- Artifact revision and provenance boundaries remain explicit.
- Accepted diagrams are saved as raw `.mmd` files under the requested path.
- Korean and English variants have matching structure when both exist.
- `check_mmd_files.py` passes for saved `.mmd` files.
