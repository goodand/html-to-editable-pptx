# Subtree Module Inventory v0.2

## Purpose

This document tracks external repositories at the module-boundary level before
adopting them through `git subtree`.

Current repository state:

- Repo-level discovery is still recorded in `third_party/repositories.toml` and
  `third_party/manifests/*.toml`.
- Subtree-level decisions are recorded in `third_party/subtrees.toml`.
- A repository must not be adopted as a subtree until its working package,
  build, test, and entrypoint boundaries are identified.

Decision values:

| Value | Meaning |
|---|---|
| `pending` | Listed but not reviewed yet |
| `needs_entrypoint_review` | Needs package/build/test/entrypoint reading |
| `adopt_subtree` | Approved for subtree adoption |
| `package_dependency` | Use upstream package manager first |
| `reference_only` | Use as design/reference material only |
| `reject` | Do not use |
| `defer` | Revisit later |

Import modes:

| Value | Meaning |
|---|---|
| `whole_repo` | Import the upstream repository root as the subtree |
| `split_subdir` | Import a specific upstream subdirectory |
| `package_dependency` | Do not vendor source; use npm/pip/maven/etc. |
| `reference_only` | Keep as a reference only |
| `pending` | Import boundary not decided |

## v0.2 Decision Summary

| ID | Upstream | Decision | Import mode | Subtree prefix | Notes |
|---|---|---|---|---|---|
| `dom_to_pptx` | `atharva9167j/dom-to-pptx` | `adopt_subtree` | `whole_repo` | `third_party/subtrees/dom-to-pptx` | Adopt whole repo, but treat runtime core + agent skill bundle as separate responsibilities |
| `pixelmatch` | `mapbox/pixelmatch` | `adopt_subtree` candidate | `whole_repo` | `third_party/subtrees/pixelmatch` | Small single-entry validation library; package dependency remains acceptable if no patching is needed |
| `looks_same` | `gemini-testing/looks-same` | `adopt_subtree` candidate | `whole_repo` | `third_party/subtrees/looks-same` | Small Node image comparison package; similar adoption shape to `pixelmatch` |
| `odiff` | `dmtrKovalenko/odiff` | `adopt_subtree` candidate | `split_subdir` | `third_party/subtrees/odiff-bin` | Root is a private monorepo; practical package boundary is `npm_packages/odiff-bin` |
| `opendataloader_pdf_core` | `opendataloader-project/opendataloader-pdf/java/opendataloader-pdf-core` | promote candidate | `split_subdir` | `third_party/subtrees/opendataloader-pdf-core` | Better subtree candidate than the Node wrapper; still needs Java module build/test verification |
| `pptxgenjs` | `gitbrent/PptxGenJS` | `package_dependency` | `package_dependency` | n/a | Large published PPTX backend; subtree only if internal generator patching becomes required |
| `backstopjs` | `garris/BackstopJS` | `package_dependency` | `package_dependency` | n/a | Large config-driven visual regression CLI/app; use package or external CLI first |
| `docling` | `docling-project/docling` | `reference_only` or package experiment | `reference_only` | n/a | Useful pipeline/object-model reference; no clean split subtree boundary yet |
| `opendataloader_pdf` | `opendataloader-project/opendataloader-pdf` | `reference_only` with core promotion path | `reference_only` | n/a | Whole repo remains a Java/Node/Python multi-SDK reference; core Java module is the subtree candidate |
| `table_transformer` | `microsoft/table-transformer` | `reference_only` | `reference_only` | n/a | Research/model pipeline with weights/config/sibling DETR code; not a small library subtree |
| `chartdetective` | `m-damien/ChartDetective` | `reference_only` | `reference_only` | n/a | Interactive React app; reusable chart logic needs deeper slicing before subtree |

## `dom_to_pptx` Adopted Boundary

`dom_to_pptx` is now promoted from a review/defer state to:

```text
decision = adopt_subtree
import_mode = whole_repo
subtree_prefix = third_party/subtrees/dom-to-pptx
```

The reason for `whole_repo` is that upstream's published package boundary is
the repository root:

- `package.json` exposes the package entrypoints and `bin`.
- `rollup.config.js` builds from `src/index.js` into `dist/*`.
- `vitest.config.js` defines the package test environment.
- `files` includes `dist`, `bin`, and `skills`.

### Runtime Core

The runtime core is the HTML-to-PPTX conversion library:

- `src/index.js` is the main export pipeline and `exportToPptx(...)`
  orchestrator.
- `src/utils.js` contains text, style, border, table, gradient, and shape
  conversion helpers.
- `src/image-processor.js` handles image loading, rounded masking,
  `object-fit`, and `object-position`.
- `src/font-embedder.js` handles font embedding and PPTX OOXML mutation.
- `src/pptx-normalizer.js` post-processes generated PPTX zip contents.

### Agent Skill Bundle

The same upstream repo also ships an AI-agent skill bundle:

- `bin/cli.js` is a skill installer, not the HTML-to-PPTX conversion CLI.
- `skills/dom-to-pptx-skill/*` contains prompt, template, validation, and
  design-reference assets.
- `skills/dom-to-pptx-skill/reference/SAFE_HTML_TEMPLATE.md` is an
  engine-aware safe-authoring template, not a generic README.

This means the subtree should preserve the whole upstream repo, while project
architecture should keep two responsibilities separate:

```text
third_party/subtrees/dom-to-pptx/
  runtime core
  + agent skill bundle
```

Operational note: the subtree import is one physical subtree, but downstream
usage should not treat the skill installer as part of the runtime conversion
path.

## Reference-Only to Subtree Promotion Notes

### `opendataloader_pdf_core`

`opendataloader-pdf` remains reference-only as a whole repository, but
`java/opendataloader-pdf-core` is a real promotion candidate because it is
closer to the semantic processor chain:

- The Node package is mainly a Java JAR subprocess wrapper.
- The Node setup script depends on Java build artifacts and root metadata.
- The Java core module has a clearer Maven module boundary and contains the
  processor/writer patterns that match this project's Semantic IR needs.

Do not promote the Node wrapper as an independent subtree unless the target is
specifically the published Node SDK wrapper. For parser/IR logic, keep reading
the Java core.

### `docling`

`docling` is still not a clean subtree target:

- The official package boundary is root `pyproject.toml` plus the `docling/`
  package and extras.
- `DocumentConverter`, CLI, pipeline, model registry, and datamodel references
  are package-wide.
- Some core types are re-exported from `docling_core`, so a small source subtree
  is not self-contained.

Use `docling` as a reference for staged pipeline, object model, and factory
registry design. Revisit subtree only if a concrete patch to upstream internals
becomes necessary.

## Current Next Steps

1. Use `third_party/subtrees.toml` as the machine-readable subtree decision
   manifest.
2. Import `dom_to_pptx` with `git subtree add` only when the project is ready to
   vendor the upstream source.
3. Before importing `opendataloader_pdf_core`, verify the Java module's direct
   build and tests.
4. Keep `docling`, `table_transformer`, and `chartdetective` reference-only
   until a smaller reusable runtime boundary is proven.
