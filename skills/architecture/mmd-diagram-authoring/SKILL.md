---
name: mmd-diagram-authoring
description: Use when creating or revising Mermaid .mmd architecture diagrams from evolving design discussions, especially when the user wants action-item-first diagram refinement, pairwise natural-language checks, Korean/English label variants, and repository-saved Mermaid files.
metadata:
  hermes:
    tags: [architecture, diagrams, mermaid, mmd, action-items, repository]
    category: architecture
    related_skills: [consensus-recording, interview-facilitation]
---

# MMD Diagram Authoring

Create architecture diagrams as durable Mermaid `.mmd` files. Prefer a coarse-to-fine workflow: stabilize the large plot first, then decompose each accepted action into lower-level diagrams.

## When to Use

- The user asks to create, critique, or save Mermaid architecture diagrams.
- The user prefers action-item keywords over noun-only boxes.
- A diagram needs Korean and English label variants.
- A passed diagram should be stored under the repo, usually `docs/diagrams/architecture/`.

Do not use this for decorative diagrams, one-off sketches that will not be saved, or diagrams where a formal notation other than Mermaid is required.

## Core Method

1. **Start with action items.** Use verb-led labels such as `Register artifact input draft`, `Generate candidate PPTX`, or `Collect validation evidence`. Avoid noun-only system boxes until the plot is stable.

2. **Pair adjacent actions in natural language.** For every edge, read the pair as a sentence. If the sentence feels unnatural, the action names or ordering are probably wrong.

3. **Stabilize the macro plot before micro details.** First produce a small lifecycle diagram. Only after the user accepts it, create subflow diagrams for one action at a time.

4. **Name the decision owner.** Decision nodes should show who decides when it matters, e.g. `Reviewer decides: accept or request revision?`, not just `Accept?`.

5. **Preserve lineage.** If a flow creates a revised artifact, route it through an action such as `Register revised source artifact` or `Publish immutable source artifact revision`. Do not jump directly from feedback to a conversion job.

6. **Separate evidence layers.** Do not mix source analysis evidence, render evidence, validation evidence, and final reports unless the diagram is explicitly about an evidence bundle.

7. **Make outputs visible.** If an action computes a digest, binds a manifest, delivers a PPTX, or publishes a revision, show that output in the label or adjacent step.

8. **Save accepted diagrams as `.mmd`.** Store raw Mermaid only. Do not include Markdown fences in `.mmd` files.

## Diagram Layers

Use this sequence unless the user asks for a different part:

1. **Artifact session lifecycle**: register source, generate candidate, collect evidence, assess, accept or request revision.
2. **Source artifact registration**: draft input, validate, resolve, materialize, manifest, publish revision, create job.
3. **Frozen input manifest lifecycle**: collect records, attach blob refs and hashes, record provenance, canonicalize, validate closure, compute digest, bind to revision.
4. **Conversion job lifecycle**: render source, extract visual evidence, build IR, map objects, generate PPTX.
5. **Validation evidence lifecycle**: render PPTX, compare visual output, validate editability, produce final report.
6. **Revision workflow lifecycle**: bundle request, run authenticated revision, publish revised source artifact.

## Label Guidance

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

## Verification

Before finishing:

- Check each `.mmd` file starts with a Mermaid diagram declaration such as `flowchart TD`, `flowchart LR`, `sequenceDiagram`, or `stateDiagram-v2`.
- Check `.mmd` files do not contain Markdown code fences.
- Re-read every edge as a natural-language pair.
- Confirm accepted diagrams are saved under the requested path.
- If files were changed in a git-backed repo, commit and push or otherwise ensure the remote branch has the new files.

If this skill includes `scripts/check_mmd_files.py`, run it on saved `.mmd` files for a quick structural check.
