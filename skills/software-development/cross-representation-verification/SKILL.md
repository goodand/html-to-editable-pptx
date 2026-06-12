---
name: cross-representation-verification
description: "Use when building or debugging format converters, parsers, or export pipelines (e.g. HTML→PPTX, DOM→IR, doc→doc): three cross-checking techniques — probe-first classification, dual-source extraction, declaration-level validation — because no single representation of the data can be trusted."
version: 1.0.0
author: Hermes Agent (distilled from goodand/html-to-editable-pptx sessions)
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [parsing, conversion, pipelines, validation, verification, cross-checking, converters]
    category: software-development
    related_skills: [systematic-debugging, test-driven-development, plan]
---

# Cross-Representation Verification

## Overview

Format converters juggle at least three representations of the same content: the
**source** (raw markup/bytes), the **processing model** (a library's box tree, DOM,
AST), and the **output declaration** (the file you write). Each one lies in a
different way. The source hides geometry. The processing model hides provenance and
inserts invisible nodes. The output renders correctly even when its declarations are
wrong, because renderers auto-correct.

**Core principle: NEVER trust a single representation. Every claim about the data
must be confirmed in a second, independent representation.**

## The Iron Law

```
NO HANDLER WITHOUT A PROBE.  NO SHIP WITHOUT A DECLARATION-LEVEL CHECK.
```

If you have not printed the real structure, you may not write code against it.
If you have only looked at a render, you have not validated the output.
Do not ship before running all four layers (Layer A through Layer D).

## When to Use

Use when writing or fixing ANY program that transforms one representation into
another:

- Document converters (HTML→PPTX, Markdown→DOCX, PDF→text)
- Parsers consuming a third-party tree/AST/box model
- Exporters/serializers writing structured file formats (OOXML, SVG, JSON schemas)
- Diff or migration tools comparing two artifacts

**Use this ESPECIALLY when:**
- The processing library's tree is undocumented or version-coupled
- An element "should obviously be there" but your handler never fires
- The output looks correct in a viewer and you are about to ship it
- A previous fix worked for one element type and silently broke another

## Data Contract

This skill operates on a **Visual Object IR** (Intermediate Representation) as
defined in `src/ir/schema.ts`. The key fields every output node must carry:

| Field | Type | Constraint | Purpose |
|---|---|---|---|
| `sourceRef` | string | non-empty | provenance: maps output back to source element |
| `bbox` | `{x,y,w,h}` | finite numbers, px | page-absolute geometry |
| `semanticType` | enum | `text\|shape\|table\|chart\|image\|group\|fallbackRegion` | closed type set |
| `zIndex` | integer | paint order | sort key for mapper |
| `dataSource` | `"attr"\|"svg-marks"` | required on chart nodes | I9 provenance for chart recovery |

A **consistent run** means:
1. Given the same HTML input, the pipeline produces byte-identical IR JSON.
2. The validator (`validateIR`) reports zero errors.
3. All three validation layers (bag-of-lines, MD5, IoU) produce the same
   pass/fail verdict.



Apply in pipeline order. Technique 1 guards input handling, Technique 2 guards
extraction, Technique 3 guards output.

---

### Technique 1: Probe-First Classification

**Recurring failure:** processing trees contain *invisible intermediaries* —
proxy wrappers that delegate attribute access, implicit nodes the spec inserts
(e.g. `tbody`), namespace-prefixed tags. Naive `type(x).__name__` or exact-tag
dispatch fails **silently**: the element is simply skipped, no error raised.

**Rule: before writing any handler against an unfamiliar tree, render a minimal
fixture and print the real structure.**

```python
def probe(node, d=0):
    real = getattr(node, "_box", node)        # unwrap known proxy attrs
    print(" " * d, type(real).__name__, getattr(real, "element_tag", ""),
          getattr(real, "position_x", ""), getattr(real, "position_y", ""))
    for c in getattr(real, "children", []):
        probe(c, d + 1)
```

Then write handlers **defensively**:

| Defense | Instead of | Because |
|---|---|---|
| Unwrap proxies first (`getattr(x, '_box', x)`) | `type(x).__name__ == 'BlockBox'` | Proxies delegate everything via `__getattr__`, so they *behave* real but *classify* wrong |
| Collect descendants recursively | `box.children` direct iteration | Specs insert implicit wrappers (tbody → `TableRowGroupBox`) between you and the nodes you want |
| Suffix / namespace-tolerant match (`tag.endswith('svg')`) | `tag == 'svg'` | Parsers may store `{http://www.w3.org/2000/svg}svg` |

**Evidence from the field:** an absolutely-positioned card `<div>` vanished from
output because `AbsolutePlaceholder.__getattr__` proxied every attribute to the
real box while failing the class check; a table reported 0 rows because rows sat
under an implicit row-group; an inline `<svg>` handler never fired on the
namespaced tag. All three were zero-error silent drops; all three were found in
minutes once probed.

---

### Technique 2: Dual-Source Extraction

**Recurring failure:** layout/processing engines give you *derived state*
(geometry, computed styles) but hide *source provenance* — an image object with
no URL, a chart with no data, style keys renamed between versions.

**Rule: extract geometry from the processing model and content from the raw
source with a second lightweight parser, then join the two streams by
document-order queues.**

```python
# stream 1 — raw source, stdlib parser, document order
class ImgSrcGrab(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == "img": self.srcs.append(dict(attrs).get("src"))

# stream 2 — processing model walk
# on encountering the Nth replaced image box: src = img_srcs.pop(0)
```

Join contract: **encounter order in the tree == document order in the source.**
State this assumption in a comment; it breaks under reordering (floats, CSS
`order`), and when it does you want the assumption findable, not implicit.

For version-coupled API keys, never hard-code one spelling:

```python
def get(style, key, default=None):
    try: return style[key]          # 'text_align' became 'text_align_all' in v69
    except Exception: return default
```

**Evidence from the field:** `RasterImage` exposed no URL attribute at all —
the raw-HTML queue recovered it; chart data lived only in `data-*` attributes
invisible to the box tree; a style-key rename crashed extraction until guarded.

---

### Technique 3: Declaration-Level Validation

**Recurring failure:** "**looks right, declared wrong.**" Renderers repair broken
declarations on the fly — they auto-grow a table frame whose declared height is
1 inch, they ignore a dangling content-type entry until one strict consumer
(PowerPoint) refuses the whole file. Pixel diffs and human eyes validate the
*repair*, not the *declaration*.

**Rule: validate what you wrote, not what a renderer shows. Run one independent
layer per representation:**

| Layer | Representation | Mechanism | Catches |
|---|---|---|---|
| **Layer A** — semantic | text | order-insensitive bag-of-lines, source vs output | dropped / invented content |
| **Layer B** — binary | assets | content hashing (MD5) source vs packaged media | missing / corrupted / renamed assets |
| **Layer C** — visual | pixels | rasterize both sides, pixel diff with masks | layout drift a human would see |
| **Layer D** — geometric | declarations | parse output XML geometry, IoU vs intended bbox per object | declared-vs-intended mismatch renderers hide |

Two sub-rules:

1. **Mask semantically-validated regions out of pixel diff.** Native charts
   re-render with their own engine; comparing their pixels to the source is
   noise. Validate them in layers A/D, subtract their bbox from layer C's
   denominator.
2. **Per-object, source-referenced reports.** A failing check must name the
   source object (`sourceRef`) so the fix lands at the origin, not the symptom
   (same doctrine as systematic-debugging Phase 1.5: trace upstream).

**Evidence from the field:** a table's declared frame height was 96 px against
an intended 324 px (IoU 0.296). Every renderer auto-corrected it; pixel diff
passed; visual QA passed. Only the geometric layer caught it — a one-line fix
(`h:` was never passed to the serializer).

---

## Red Flags — STOP and Cross-Check

If you catch yourself thinking:
- "The viewer shows it correctly, ship it"
- "The tree obviously has rows as direct children"
- "The API must expose the source URL somewhere"
- "Pixel diff passed, so the geometry is fine"
- "My handler just doesn't fire for this element — skip it for now"
- "Same library, the style key can't have changed"

**ALL of these mean: you are trusting one representation. Probe it, cross it,
or layer it.**

## Common Rationalizations

| Excuse | Reality |
|--------|---------|
| "Probing wastes time, the docs show the tree" | Docs show the *spec* tree. Proxies and implicit nodes are implementation details that only a probe reveals. |
| "A silent skip is harmless" | A silent skip is content loss with no error trail — the most expensive bug class in converters. |
| "Renderer X opens it, so the file is valid" | Renderers repair declarations. The next consumer may refuse the file outright. |
| "One validation pass is enough" | Each layer is blind to the other layers' failure modes. The geometric defect above passed three other layers. |
| "I'll join the two parsers by matching attributes" | Attribute matching breaks on duplicates. Document-order queues are deterministic — just state the ordering assumption. |

## Quick Reference

| Technique | Trigger | Action | Success criterion |
|---|---|---|---|
| 1. Probe-first | New tree/AST, handler not firing | Minimal fixture → print real structure → defensive match | Handler dispatch explained by printed structure, not assumed |
| 2. Dual-source | Engine hides provenance / version drift | Second stdlib parse of raw source, join by order queue | Every emitted object carries provenance from the source stream |
| 3. Declaration layers | Before shipping any output file | Run layers A–D; mask semantic regions from C | All layers pass on declarations, not renders |

## Verification

The skill was applied correctly when:

1. Every handler in the extraction walk can cite a probe output justifying its
   match condition.
2. Every emitted object carries a `sourceRef` joining it back to the raw source.
3. The validation report shows one independent result per representation layer,
   and failing entries name source objects.
4. No check in the report validates a *render* where a *declaration* was
   available.

## Hermes Agent Integration

### Investigation tools

- **`terminal`** — run probe scripts on minimal fixtures; unzip output packages
  (`unzip -p out.pptx [Content_Types].xml`) to read declarations directly
- **`read_file` / `search_files`** — locate version-coupled keys, trace where a
  silently-skipped element should have been handled
- **`execute_code`** — quick IoU / hash / bag-of-lines comparisons without
  scaffolding

### With delegate_task

Probing is an ideal subagent task — bounded, read-only, evidence-producing:

```python
delegate_task(
    goal="Probe the real box-tree structure for fixture X",
    context="""
    Follow cross-representation-verification Technique 1:
    1. Render the minimal fixture with <library>
    2. Print every node: class name, tag, position, unwrapping any proxy attrs
    3. Report structure verbatim — do NOT write handlers yet
    """,
    toolsets=['terminal', 'file']
)
```

### Verification script

Run the full four-layer check with the bundled helper:

```bash
# from the project root (generates out/<name>.ab.json, .d.json, diff-N.png)
bash scripts/run.sh fixtures/<slide>.html

# inspect Layer A (semantic)
python3 src/validate/validate_ab.py fixtures/<slide>.html out/<slide>.pptx

# inspect Layer D (geometric / declaration-level IoU)
python3 src/validate/layout_d.py out/<slide>.ir.json out/<slide>.pptx
```

A passing run produces:
- `layerA_semantic.pass: true` with `jaccard: 1.0` per slide
- `layerB_media.pass: true` with `matched == sourceAssets`
- `layerC_visual.diffPct < 5` (chart regions masked)
- `layerD_layout.pass: true` with `worstIoU > 0.90`

### Usage counter and result storage

Hermes tracks this skill via the **sidecar** `~/.hermes/skills/.usage.json`
(keyed by skill `name`). The counter fields are:

| Field | Bumped by |
|---|---|
| `use_count` + `last_used_at` | `skill_usage.bump_use("cross-representation-verification")` |
| `view_count` + `last_viewed_at` | automatic on `skill_view()` |
| `patch_count` + `last_patched_at` | `skill_manage(action="patch", ...)` |

Skill results (IR JSON, validation reports, diff PNGs) are persisted by
`tool_result_storage` when they exceed the per-turn context budget
(`MAX_TURN_BUDGET_CHARS = 200k`). The full output is written to
`/tmp/hermes-results/<tool_use_id>.txt` and replaced in-context with a
preview + `read_file` pointer. To access a spilled report:

```bash
read_file /tmp/hermes-results/<tool_use_id>.txt
```



### With systematic-debugging

When a converter bug surfaces, systematic-debugging Phase 1 (root cause) is the
outer loop; this skill supplies the converter-specific evidence moves: probe the
tree (1.4 gather evidence), join source provenance (1.5 trace data flow), and
check declarations before trusting any render.
