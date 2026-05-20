# html-to-editable-pptx

Editability-first HTML to PPTX parser project.

The goal is to convert rendered HTML into **editable PowerPoint objects** by combining browser layout extraction, a Visual Object IR, semantic object detection, and PPTX object mapping.

For the concrete problem definition, reusable module slots, and `opendataloader-pdf` module mapping, read:

```text
docs/GOAL_PROBLEM.md
```

This is not a screenshot-first exporter. Visual fidelity matters, but the primary target is editability.

## Core priority

```text
editable PPT objects > visual fidelity
reuse existing modules > write new code
validated output > unverified output
explicit fallback policy > implicit rasterization
```

Working rule:

```text
implementation is cheap; reconstruction is expensive
```

Therefore, the project should read and reuse existing modules before writing new code, and every generated PPTX should be validated by rendering.

## Target editable objects

The following should become editable PPT objects where possible:

- text
- rich text runs
- shapes
- tables
- charts

The following may remain asset-backed objects:

- PNG / JPG / GIF
- SVG and icon assets
- video thumbnails
- complex visual effects that cannot be represented as stable native PPT objects

## Planned pipeline

```text
HTML / CSS / JS-rendered page
  -> Playwright browser rendering
  -> DOM geometry and computed style extraction
  -> measured visual nodes
  -> Visual Object IR
  -> semantic candidates
     - text
     - shape
     - image
     - table
     - chartCandidate
     - group
     - fallbackRegion
  -> editable PPTX object mapper
  -> PPTX generation
  -> rendered validation
```

## Main modules

The project currently tracks candidate repositories for these modules:

1. Visual Object IR normalizer
2. fake table detector
3. chart semantic extractor
4. fallback policy / visual validation engine
5. PPTX output backend
6. reference parsers and IR designs

## Repository manifests

Third-party candidates are listed in TOML manifests.

```text
third_party/repositories.toml
third_party/manifests/visual_ir.toml
third_party/manifests/table_detection.toml
third_party/manifests/chart_extraction.toml
third_party/manifests/visual_validation.toml
third_party/manifests/reference_repos.toml
third_party/manifests/agent_skills.toml
```

The default manifest contains the highest-priority seed repositories:

| module | repository |
|---|---|
| HTML measurement / PPT mapping | `atharva9167j/dom-to-pptx` |
| table detection | `microsoft/table-transformer` |
| chart extraction | `m-damien/ChartDetective` |
| visual diff | `mapbox/pixelmatch` |
| PPTX backend | `gitbrent/PptxGenJS` |

Additional manifests add document layout, table recognition, chart extraction, visual validation, reference parser candidates, and agent skill references.

## Clone third-party repositories

Use:

```bash
./scripts/clone_repos.sh
```

The script reads:

```text
third_party/repositories.toml
third_party/manifests/*.toml
```

and clones all configured repositories into:

```text
third_party/repos/
```

The clone helper uses shallow clones by default:

```text
git clone --depth 1 --single-branch --filter=blob:none
```

If partial clone fails, it retries with a normal shallow clone.

## Important files

```text
README.md
docs/GOAL_PROBLEM.md
scripts/clone_repos.sh
scripts/clone_repos_from_toml.py
third_party/repositories.toml
third_party/manifests/*.toml
docs/TASK.md
```

## Codex Web first task

After cloning third-party repositories, write a reuse report before implementing new code.

Expected first outputs:

```text
docs/reuse_report.md
docs/architecture.md
docs/deletion_candidates.md
```

Recommended placeholders:

```text
src/ir/schema.ts
src/extract/README.md
src/mapper/README.md
src/validate/README.md
```

## Design notes

### Visual Object IR

Do not map DOM nodes directly to PPT objects.

Preferred structure:

```text
DOM node
  -> measured visual node
  -> semantic candidate
  -> PPT mapping decision
  -> PPTX object
```

This avoids over-creating PPT objects from layout wrappers such as `div`, `section`, and framework-generated containers.

### Fake table detection

Native HTML tables can be mapped directly to PPT tables. Div/grid-based visual tables need separate detection.

Useful signals:

- repeated aligned bounding boxes
- row and column clusters
- text alignment consistency
- consistent cell spacing
- border/background pattern repetition

### Chart extraction

Chart recovery is the hardest area. Prefer source data adapters when possible.

Recommended order:

1. Extract source data from known chart libraries.
2. Parse SVG marks, axes, labels, and legends where possible.
3. Use image/vector chart extraction tools only as a fallback reference.
4. If semantic recovery fails, preserve the chart as an asset-backed object.

### Validation

Generated PPTX should be rendered and compared against source HTML screenshots.

Validation should produce:

- visual mismatch score
- object editability score
- overflow report
- missing font report
- fallback region report

## Current status

This repository is in bootstrap phase.

The immediate goal is not full conversion. The immediate goal is to read existing repositories, identify reusable modules, define the Visual Object IR, and build a minimal validated conversion path.
