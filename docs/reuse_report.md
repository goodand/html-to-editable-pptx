# Reuse Report (B안 — Evidence-first)

> **Scope contract**: This document is the B안 deliverable. It evaluates P1 candidates **at code level** using a Level-2 critical-path trace, combining two complementary lenses per repo: criterion X (the library's representative path) and criterion Y (back-tracing from our slot's requirements). The shallow triage of all 27 repos is delegated to a separate session — see `docs/reuse_triage_task_A.md`.
>
> **Reading order**: Each P1 section follows a 7-part format derived from `docs/GOAL_PROBLEM.md` §8, extended with explicit X-findings and Y-findings blocks. Adopt/discard decisions stated here are evidence-backed and override the broader triage in case of conflict.

---

## P1.1 — `pixelmatch` (slot: `fallback_validation`)

| Field | Value |
|---|---|
| Repository | `mapbox/pixelmatch` |
| Commit pinned | `9faed09302aa` (v7.2.0, 2026-04-28) |
| Slot | `fallback_validation` (part of GOAL_PROBLEM §8, §9) |
| Priority | P1 |
| License | ISC (MIT-compatible, commercial use permitted) |
| Decision | **Adopt** for the pixel-comparison core of the validation backend |
| Confidence | High — X and Y converge with no contradictions |

### 1. Problem

The fallback policy engine and validation backend (GOAL_PROBLEM §8, §9) need a deterministic pixel-level comparator that produces a numeric mismatch score and an optional visual diff image. Without it, the project cannot satisfy success criteria 6 (*"rendered PPTX is validated against the source screenshot"*) and 7 (*"every lossy decision is recorded in a report"*).

### 2. Cause

PPTX rendering across PowerPoint / Keynote / LibreOffice differs in font hinting, anti-aliasing, and sub-pixel positioning. Naïve byte equality between a Playwright HTML screenshot and a LibreOffice PPTX screenshot always reports a mismatch, even when the editable objects are semantically identical. A perceptual comparator with anti-aliasing tolerance is required.

### 3. Required input (from the slot)

- Source HTML screenshot (Playwright output)
- Rendered PPTX screenshot (LibreOffice / headless PowerPoint output)
- Optional ROI bounds for fallback regions
- Threshold configuration

### 4. Expected output (from the slot)

- `mismatch_pixel_count` (integer)
- Optional diff image (PNG-shaped raw bytes)
- Per-pixel classification: identical / anti-aliasing / substantive difference / darker / brighter

### 5. Reuse candidate evaluation

#### 5.1. X-findings (library representative path)

The library exposes a **single default-export function** at `index.js:22`:

```js
pixelmatch(img1, img2, output, width, height, options)  // returns number
```

The README's representative example is the Node.js path (`README.md:69-82`): `PNG.sync.read` decodes both images, the function is called once, the diff is written back via `PNG.sync.write`. The CLI binary (`bin/pixelmatch:1-39`) mirrors this path.

What the library actually does in 314 lines (`index.js`):

| Operation | Location | Notes |
|---|---|---|
| Input validation (typed-array view, 1 byte/elem) | L32-38 | Buffers pass (Node `Buffer` extends `Uint8Array`) despite JSDoc saying only `Uint8Array` |
| Fast path for identical inputs | L46-54 | 32-bit word comparison; returns 0 without per-pixel work |
| Per-pixel YIQ color delta | L65-67, helper `colorDelta` L214 | YIQ space, not RGB — implements Kotsarenko & Ramos 2010 |
| Threshold gate | L58, L70 | `maxDelta = 35215 × threshold²`; `Math.abs(delta) > maxDelta` is the trigger |
| Anti-aliasing exclusion | L74, helper `antialiased` L120 | Vyšniauskas 2009 detector; only when `includeAA === false` (default) |
| Diff pixel rendering | L78, L82-87 | `diffColorAlt` distinguishes "darker than img1" from "brighter than img1" |
| Mismatch counting | L62, L89, L99 | `diff++` only when AA-exclusion fails |

The library's claimed scope (*"smallest, simplest, fastest pixel comparison"*, `README.md:6`) matches the code exactly. No hidden surface area, no plugin system, no I/O — raw bytes in, raw bytes out.

#### 5.2. Y-findings (back-tracing from our slot)

Y produced a 13-row responsibility split between pixelmatch and our code. The split is:

| Slot responsibility | Owner | Justification |
|---|---|---|
| Playwright screenshot capture | us | out of scope for any image-diff lib |
| PPTX → screenshot (headless rendering) | us | out of scope |
| PNG decoding → raw bytes | us | `pngjs` is a CLI/test-only dep, not a library dep |
| Dimension normalization (resize/crop/pad) | us | hard-throw at `index.js:35-38` if mismatched |
| Buffer → Uint8Array conversion | us | strictly required by JSDoc; in practice X-finding showed Buffer passes |
| ROI cropping for fallback regions | us | library compares full images only |
| **Per-pixel comparison algorithm** | **pixelmatch** | confirmed by X at L65-90 |
| **Diff image rendering** | **pixelmatch** | confirmed by X at L78-87 |
| **AA / threshold tuning** | **pixelmatch** | confirmed by X at L58, L70, L74 |
| **Per-pixel difference classification (incl. darker/brighter)** | **pixelmatch** | X-finding: `diffColorAlt` at L83-87 — *not previously listed in Y* |
| mismatch_pixels → editability_score combination | us | library returns raw count only |
| Fallback reason annotation | us | library is reason-agnostic |
| Validation report write to disk | us | GOAL_PROBLEM §9 mandate |

**X strengthened Y in one way**: the `diffColorAlt` mechanism (darker-vs-brighter distinction) is a per-pixel classification signal that feeds the future reason-aware reporter. It was not visible from the README alone.

### 6. Implementation task

#### 6.1. Bootstrap-required (immediate)

> **Single task: build an image normalization adapter** that converts `(Playwright Buffer, LibreOffice Buffer)` into `(Uint8Array, Uint8Array, width, height)` such that both arrays satisfy `len === width × height × 4` and have identical dimensions.

Suggested module location: `src/validate/normalize.ts`. Suggested dependencies: one of `sharp` / `jimp` / `pngjs` for decoding (no strong preference — pngjs is already a transitive dep so it's the lowest-cost choice).

Calling pattern:

```text
normalize(htmlPng, pptxPng) → { a: Uint8Array, b: Uint8Array, width, height }
  → pixelmatch(a, b, diff, width, height, { threshold }) → mismatch_count
```

#### 6.2. Deferred (post-bootstrap)

| Task | Trigger to start |
|---|---|
| ROI-based comparison wrapper | when fallback policy engine produces region bounds |
| Score combiner (`mismatch_ratio + editability_score`) | when IR emits editability scores |
| Reason-aware reporter (uses `diffColorAlt` channel) | when fallback policy assigns reasons to regions |

Each deferred task has a single specific trigger — none should be built speculatively.

### 7. Validation

The adopt decision is verified by re-checking these invariants when `src/validate/normalize.ts` lands:

1. `pixelmatch(a, a, null, w, h)` returns `0` for identical inputs (covered by upstream test `1emptydiffmask` at `test/test.js:14`).
2. The normalize adapter never passes mismatched-dimension arrays to pixelmatch — verified by a unit test that asserts on dimension equality before the call.
3. The full validation path (`HTML.png + PPTX.png → mismatch_count + diff.png`) executes end-to-end on the first validated example slide.
4. License notice (ISC, Mapbox 2025) is preserved in any vendored or redistributed form.

### 8. Non-goals

Following GOAL_PROBLEM.md's non-goal categorization:

- **Case: Type** — Do not build a perceptual similarity metric beyond what pixelmatch provides. Do not extend pixelmatch internals (the library is small enough to fork, but forking creates a maintenance burden that violates *"reuse existing modules > write new code"*).
- **Case: State** — Adopt does not mean "no replacement ever". If LibreOffice rendering introduces systematic anti-aliasing differences that pixelmatch's detector cannot tolerate, we evaluate `looks-same` (P2, same slot) before forking.
- **Case: Performance: Null** — Do not optimize pixelmatch invocation latency in bootstrap. The fast path (`index.js:46-54`) already makes identical-slide comparisons free; that is the only optimization we rely on for now.
- **Case: Performance: Over** — Do not wrap pixelmatch behind an abstraction layer that supports multiple diff backends in bootstrap. A direct call site with a single backend is the correct primitive until the second backend becomes necessary.

### 9. Open questions for downstream sessions

These questions are intentionally **not** answered here. They are recorded for `docs/architecture.md` or `docs/reuse_triage_task_A.md` to resolve:

- Q-pm-1: Which PNG decoder do we adopt project-wide — `sharp` (fast, native binary), `jimp` (pure JS, slower), or `pngjs` (already transitive)? This is a project-wide infrastructure choice, not a fallback_validation decision.
- Q-pm-2: How are HTML and PPTX screenshots brought to identical dimensions when slide aspect ratios may differ — letterbox, crop, or scale? This is a fallback_policy_engine decision, not pixelmatch's.
- Q-pm-3: Should the diff PNG be persisted per slide, per region, or both? This is a report-format decision belonging to `docs/architecture.md` §validation.

---

## P1.2 — `pptxgenjs` (slot: `pptx_output_backend`)

| Field | Value |
|---|---|
| Repository | `gitbrent/PptxGenJS` |
| Commit pinned | `3c9ec1b687c1` (v4.0.1, 2025-06-25) |
| Slot | Slot 8 — PPTX output backend (also referenced by Slots 3, 4, 5a, 6, 7c as the target API) |
| Priority | P1 |
| License | MIT (Brent Ely, 2015-2022) |
| Decision | **Adopt** as the sole PPTX serialization backend |
| Confidence | High — no realistic alternative in the JS ecosystem |

### 1. Problem

The IR must become an actual `.pptx` file that PowerPoint, Keynote, and LibreOffice will open and present as editable objects. Without a backend, the IR is unobservable and success criteria 1-5 of GOAL_PROBLEM.md cannot be validated.

### 2. Cause

The OOXML/PresentationML format is large and fragile: it requires correct `[Content_Types].xml`, relationship parts (`_rels/*.rels`), slide masters, theme XML, EMU-based coordinates (`914400 EMU = 1 inch`), and dozens of element-specific XML schemas (shape types, chart series, table grids). Hand-writing this is feasible but reconstructive — it directly violates *"implementation is cheap; reconstruction is expensive"*.

### 3. Required input (from the slot)

- Visual Object IR with PPT mapping decisions
- Slide size and layout
- Resolved assets (PNG / SVG → embedded media)
- Text runs with resolved font, color, size, weight
- Shape options (fill, border, radius, shadow)
- Table rows and cells
- Chart data when recoverable

### 4. Expected output (from the slot)

- A `.pptx` file on disk that opens in PowerPoint without errors
- Text objects that are editable (selectable, re-typable)
- Shapes that are editable (re-sizable, re-styleable in PowerPoint UI)
- Tables that are editable (row insertion, cell edit)
- Charts that are editable (data table accessible)

### 5. Reuse candidate evaluation

#### 5.1. X-findings (library representative path)

pptxgenjs exposes a fluent API rooted at `class PptxGen` (`src/pptxgen.ts`). The representative path from `README.md` and `demos/`:

```js
const pres = new PptxGen()
const slide = pres.addSlide()
slide.addText("Hello", { x: 1, y: 1, w: 4, h: 1, fontSize: 18 })
slide.addShape(pres.ShapeType.roundRect, { x: 1, y: 3, w: 4, h: 2, fill: { color: "0088CC" } })
await pres.writeFile({ fileName: "out.pptx" })
```

Key surface points relevant to our slot:

| API method | Source | Maps to our IR type |
|---|---|---|
| `addText(text, opts)` | `src/slide.ts:?` (referenced in `gen-objects.ts`) | `text` + `richTextRun` |
| `addShape(shapeName, opts)` | `src/slide.ts:213` | `shape` |
| `addImage(opts)` | `src/slide.ts:181` | `image` |
| `addTable(rows, opts)` | `src/slide.ts:229` | `table` + `tableRow` + `tableCell` |
| `addChart(type, data, opts)` | `src/slide.ts:167` | `chartCandidate` |
| `addMedia(opts)` | `src/slide.ts:191` | video / audio asset |

Internal generation modules (`gen-charts.ts`, `gen-media.ts`, `gen-objects.ts`, `gen-tables.ts`, `gen-utils.ts`, `gen-xml.ts`) are private — we are not expected to extend them. The XML emission and ZIP packaging via `jszip` is a closed pipeline.

The unit system is fixed: EMU at 914400 per inch (`core-enums.ts:9`). Our extractor produces `getBoundingClientRect` outputs in CSS pixels at 96 DPI, so the conversion is `px × (914400 / 96)` to EMU — a constant multiplier, not an algorithm. pptxgenjs accepts inches as float (`x: 1.5`) which makes the conversion ergonomic.

#### 5.2. Y-findings (back-tracing from our slot)

The IR-to-PPT mapping decisions from §5-§6 of GOAL_PROBLEM.md determine which pptxgenjs surface we use. Our 12 IR types map to pptxgenjs as follows:

| IR type | pptxgenjs API | Editability preserved? |
|---|---|---|
| `document` | `new PptxGen()` | n/a |
| `slide` | `pres.addSlide()` | n/a |
| `group` | **no native group API** | partial — sequential `slide.add*` calls; group selection in PowerPoint is manual |
| `text` | `slide.addText()` with array of runs | yes |
| `richTextRun` | text array element with `{ text, options }` | yes |
| `shape` | `slide.addShape()` | yes |
| `image` | `slide.addImage()` | asset-backed |
| `table` | `slide.addTable()` | yes |
| `tableRow` / `tableCell` | nested rows[][] structure | yes |
| `chartCandidate` | `slide.addChart()` when data recoverable | yes for data; asset fallback otherwise |
| `fallbackRegion` | `slide.addImage()` with rasterized content | asset-backed (by definition) |

**Critical Y-finding — no group object**: pptxgenjs has no `addGroup()` method. CSS visual hierarchy (a card with header + body + footer that the user expects to move as one unit in PowerPoint) cannot be preserved. Each child element becomes an independent slide object. This is a documented limitation, not an oversight.

> Mitigation: GOAL_PROBLEM.md §2 already accepts that "layout-only wrappers should not become unnecessary PPT objects." The IR normalizer flattens groups before reaching pptxgenjs; group identity is recorded in IR metadata only.

**Second Y-finding — shape type vocabulary is fixed**: `ShapeType` enum (`core-enums.ts`) defines a closed set of PowerPoint-native shape names (`rect`, `roundRect`, `ellipse`, etc.). Arbitrary CSS shapes (e.g. `border-radius: 30% 70% 70% 30% / 60% 40% 60% 40%`) cannot be expressed natively — they fall back to either an SVG asset or a `customGeometry` if pptxgenjs supports it. Quick check at `core-interfaces.ts:611` shows `ShapeProps` does not expose custom path geometry → **custom CSS clip-paths must fall back to SVG asset**.

**Third Y-finding — Buffer/ArrayBuffer dual environment**: package main is `dist/pptxgen.cjs.js` and module is `dist/pptxgen.mjs`. CJS and ESM both ship, but the writer is async and works in Node (`writeFile`) and browser (`write(...)`) with different output types. Our pipeline runs in Node — `writeFile({ fileName, outputType: "nodebuffer" })` is the call.

### 6. Implementation task

#### 6.1. Bootstrap-required (immediate)

> **Single task: build an IR → pptxgenjs translator** at `src/mapper/pptxgen.ts` that accepts a slide-scoped IR subtree and produces the sequence of `slide.add*` calls.

The translator is a deterministic dispatch table — given an IR node, look up its type, call the matching pptxgenjs method. No reasoning, no semantic decisions. All semantic decisions happen earlier in the pipeline (extractor, IR normalizer, fallback policy).

#### 6.2. Deferred (post-bootstrap)

| Task | Trigger to start |
|---|---|
| Custom shape geometry via SVG asset emission | when first non-native CSS shape is encountered |
| Group metadata preservation (slide-level comments or layout) | when downstream user feedback requests grouping |
| Font embedding via pptxgenjs font options | when validation reveals font substitution issues |
| Chart authoring path for recovered chart data | when ChartDetective (or alternative) actually yields source data |

### 7. Validation

1. The translator's output, when run against an empty IR, produces a valid empty PPTX (opens in PowerPoint).
2. A round-trip test: IR with one text run + one rectangle + one table → generated PPTX → opened and inspected → text editable, rect resizable, table cell editable.
3. EMU conversion correctness: a 96px × 96px CSS box becomes 1.0in × 1.0in in PowerPoint (verified by ruler).
4. License notice (MIT) preserved.

### 8. Non-goals

- **Case: Type** — Do not fork pptxgenjs to add a group API. CSS group semantics are an IR concern, not a PPT concern.
- **Case: Type** — Do not implement custom geometry XML emission. SVG asset fallback is the supported path.
- **Case: State** — Do not pin to v4.x indefinitely. Track major version changes via the deletion candidate document.
- **Case: Performance: Null** — Do not stream-write PPTX in bootstrap. `writeFile` to disk is sufficient.
- **Case: Performance: Over** — Do not build an abstraction layer over pptxgenjs to allow swapping backends. There is no realistic alternative backend; the abstraction would be premature.

### 9. Open questions

- Q-pg-1: How are font files embedded for non-system fonts? pptxgenjs has font options but font embedding into the PPTX itself may require post-processing (see `dom_to_pptx`'s `PPTXEmbedFonts` for a working precedent — P1.3).
- Q-pg-2: What is the maximum slide count beyond which pptxgenjs becomes slow? Out of scope until batch throughput becomes a concern.
- Q-pg-3: Does pptxgenjs's chart API support the chart types we recover from SVG? Resolved in P1.4 (ChartDetective).

---

## P1.3 — `dom_to_pptx` (slots: extractor, renderQueue, text runs, style mapper, table extractor, image mapper)

| Field | Value |
|---|---|
| Repository | `atharva9167j/dom-to-pptx` |
| Commit pinned | `e1f8a7ab953f` (v1.1.9, 2026-05-16) |
| Slots | 1, 2, 3, 4, 5a, 6 (six slots — the highest single-dep concentration in the project) |
| Priority | P1 |
| License | MIT (2025, Atharva Dharmendra Jagtap) |
| Decision | **Adopt as reference, vendor selected functions** — *not* `import dom-to-pptx` as a runtime dep |
| Confidence | Medium-high — code is real and working, but transplantation is required |

### 1. Problem

Six of the eight required reusable module slots are nominally filled by this one repository (per `GOAL_PROBLEM.md` §"Required reusable module slots"). If `dom_to_pptx` is adopted naively as a runtime dependency, the entire pipeline becomes a thin wrapper around it — and we inherit its architectural decisions wholesale, including `html2canvas`-based rasterization. If it is rejected, six slots need new implementations. The correct posture lies between these extremes.

### 2. Cause

`dom_to_pptx` is structured as a **monolithic browser-side converter**: `exportToPptx(target, options)` accepts a live HTMLElement, runs `getBoundingClientRect` / `getComputedStyle` on the live DOM, calls `html2canvas` for icon/image rasterization, and emits a `Blob` via embedded `pptxgenjs`. Three structural facts force a transplantation strategy:

1. **It runs in a browser, not Node.** All `window` / `document` references are real-DOM; Playwright provides the DOM, but `dom_to_pptx` is not packaged as a Playwright-injectable module.
2. **It bundles `pptxgenjs ^3.12.0`** as a runtime dep, while we adopt v4.0.1 directly in P1.2. Importing `dom_to_pptx` pulls a second pptxgenjs major version into the dependency tree.
3. **It includes `html2canvas`** — a rasterization tool. Adopting wholesale means accepting rasterization as a primary path, in direct conflict with our editability-first priority (GOAL_PROBLEM.md headline).

### 3. Required input (per slot it touches)

- Slot 1 (extractor): rendered viewport, DOM root, `getBoundingClientRect`, `getComputedStyle`, device pixel ratio, target slide size
- Slot 2 (renderQueue): measured nodes, parent/child links, z-order
- Slot 3 (text runs): text subtree, inline styles, hyperlinks
- Slot 4 (style mapper): computed background, border, radius, shadow, opacity, transform
- Slot 5a (table extractor): semantic `<table>` subtree
- Slot 6 (image mapper): image src, SVG source, CSS background-image, object-fit

### 4. Expected output (per slot it produces)

- Slot 1: measured visual nodes (slide-space coordinates)
- Slot 2: `renderItem` queue with z-order and DOM order
- Slot 3: pptxgenjs text-run array `[{ text, options }]`
- Slot 4: pptxgenjs shape options object (fill, line, shadow, etc.)
- Slot 5a: pptxgenjs table-rows nested array
- Slot 6: pptxgenjs image options (path or data URI, x/y/w/h, cropping)

### 5. Reuse candidate evaluation

#### 5.1. X-findings (library representative path)

The library's representative path is `exportToPptx(htmlElement)` at `src/index.js:51`. Following it down:

```text
exportToPptx(target)
  → walk DOM
  → for each node: prepareRenderItem(node, ...)     [src/index.js:522, 845 lines]
    → text path: collectTextParts()                  [src/utils.js:1041, 95 lines]
    → table path: extractTableData()                  [src/utils.js:37, 119 lines]
    → style path: getTextStyle() + getBorderInfo() + getVisibleShadow() + generateGradientSVG()
                                                       [src/utils.js:434/223/708/742]
    → image path: getProcessedImage()                  [src/image-processor.js]
    → icon path: elementToCanvasImage()                [src/index.js:336, falls back to html2canvas]
  → emit pptxgenjs calls
  → font embedding via PPTXEmbedFonts()                [src/font-embedder.js]
  → ZIP normalization via normalizePptxZip()           [src/pptx-normalizer.js]
  → return Blob
```

**`prepareRenderItem` is exactly the renderQueue pattern** GOAL_PROBLEM.md cites for Slot 2 — it takes a DOM node + computed style + z-index and returns an array of typed render items (`{ type: 'text', zIndex, domOrder, ... }`). This is the strongest single reuse signal in the entire repo.

**`collectTextParts` (95 lines)** handles: hyperlink inheritance (`<a>` ancestors), `::before` CSS content (icon fonts), whitespace normalization, child recursion. This is exactly Slot 3's deliverable.

**`extractTableData` (119 lines)** walks `<table>/<tr>/<td>` and emits pptxgenjs's nested row array directly. Slot 5a's deliverable.

**`getTextStyle` (78 lines)** maps `font-size` / `font-weight` / `font-style` / `text-decoration` / `color` / `text-align` / `line-height` / `letter-spacing` to pptxgenjs text options. Includes opacity inheritance handling.

#### 5.2. Y-findings (back-tracing from our slot)

Mapping the 6 slots to `dom_to_pptx`'s code units:

| Our slot | dom_to_pptx unit | Status |
|---|---|---|
| 1 (extractor) | `getBoundingClientRect` + `getComputedStyle` calls scattered through `prepareRenderItem` | **Reusable as pattern, not as module** — the calls are inlined, not extracted |
| 2 (renderQueue) | `prepareRenderItem` returns `{ items: [...] }` keyed by type | **Highly reusable**, needs transplant to Node/Playwright `page.evaluate` |
| 3 (text runs) | `collectTextParts` in `utils.js` | **Directly reusable** as a function (no Node-only deps inside it) |
| 4 (style mapper) | `getTextStyle`, `getBorderInfo`, `getVisibleShadow`, `generateGradientSVG`, `getRotation` | **Directly reusable** — pure functions over computed-style values |
| 5a (table extractor) | `extractTableData` | **Directly reusable** |
| 6 (image mapper) | `getProcessedImage` + `image-processor.js` | **Partially reusable** — image loading is browser-API based, needs Node equivalent |

**Critical Y-finding — html2canvas is gated**: `html2canvas` is called inside `elementToCanvasImage` at `src/index.js:336`, which is used for *icon detection* (`isIconElement` at L475) and rasterization fallback when an element cannot be represented natively. It is **not the primary path** — most DOM nodes go through `prepareRenderItem` and become native pptxgenjs calls. The rasterization concern is real but bounded.

**Second Y-finding — font infrastructure is a bonus**: `font-embedder.js` + `font-utils.js` solve a problem we haven't addressed yet: embedding non-system fonts into the PPTX so it renders identically on other machines. This is a free win — see P1.2 Q-pg-1.

**Third Y-finding — `pptx-normalizer.js` solves a known PowerPoint bug**: per the docstring at `src/index.js:46`, pptxgenjs's raw output sometimes includes "dangling [Content_Types].xml Overrides" that PowerPoint rejects. The normalizer re-zips with DEFLATE and strips these. This is concrete evidence the author has hit real PowerPoint validation issues and patched them — knowledge we'd otherwise rediscover painfully.

### 6. Implementation task

#### 6.1. Bootstrap-required (immediate)

> **Single task: transplant six pure functions into our `src/extract/` and `src/mapper/` modules** with clear attribution to `dom_to_pptx` (license, commit SHA, file/line in this report).

Functions to transplant (in order of priority):

1. `collectTextParts` → `src/extract/text-runs.ts`
2. `getTextStyle` → `src/mapper/text-style.ts`
3. `extractTableData` → `src/extract/table.ts`
4. `getBorderInfo` + `getVisibleShadow` + `generateGradientSVG` → `src/mapper/visual-style.ts`
5. The `prepareRenderItem` dispatch skeleton → `src/extract/render-queue.ts` (heavily refactored — this is the IR boundary)
6. `pptx-normalizer.js` → `src/output/normalize-zip.ts` (run after pptxgenjs writeFile)

Each transplanted function carries a comment header:

```ts
// Adapted from dom-to-pptx (MIT, Atharva Dharmendra Jagtap 2025)
// Original: src/utils.js:1041, commit e1f8a7ab953f
```

#### 6.2. Deferred (post-bootstrap)

| Task | Trigger to start |
|---|---|
| Font embedding via `font-embedder.js` pattern | when first non-system-font test case is reported |
| Image processing pipeline transplant | when first complex image (SVG with embedded raster, cropped background-image) is encountered |
| html2canvas icon fallback | when iconography (Font Awesome, Material Icons) is needed; consider SVG-only path first |

### 7. Validation

1. Transplanted functions pass their original tests (port `src/__tests__/pptx-normalizer.test.js` first as smallest unit).
2. The transplanted `collectTextParts` produces identical run arrays for a fixed HTML fixture compared to `dom_to_pptx`'s output.
3. License attribution headers present in all transplanted files.
4. No `html2canvas` import in our `src/` tree (verifies the editability-first commitment).
5. The original `dom_to_pptx` package is **not** listed in our `package.json` dependencies.

### 8. Non-goals

- **Case: State** — Do not import `dom_to_pptx` as a runtime dep. This locks pptxgenjs major version and pulls html2canvas — two conflicts with our architecture.
- **Case: Type** — Do not transplant `html2canvas`-dependent functions in the base pipeline (`elementToCanvasImage`, `isIconElement`'s rasterization branch). Pure functions only in bootstrap.
- **Case: Type** — Do not extract logic involving `window.document.createRange()` or other live-DOM APIs without first wrapping in a Playwright `page.evaluate` boundary.
- **Case: Performance: Over** — Do not refactor `prepareRenderItem`'s 845-line function structure as our IR boundary. Use it as a pattern reference; our IR is its own design (see `docs/architecture.md` when written).
- **Case: Performance: Under** — It is acceptable that the transplanted code is slower than `dom_to_pptx`'s original because we add a Playwright boundary.

### 9. Open questions

- Q-d2p-1: Where is the Playwright boundary? Two options: (a) ship transplanted functions as a string into `page.evaluate`, (b) keep them in Node and pass computed-style snapshots through. (a) is closer to the original, (b) is cleaner — decision belongs to `docs/architecture.md`.
- Q-d2p-2: How do we keep the transplanted code in sync with upstream fixes? `dom_to_pptx` is actively maintained (HEAD 2026-05). Set a quarterly upstream-diff review in `docs/deletion_candidates.md`.
- Q-d2p-3: The transplant strategy implies `dom_to_pptx` shifts from "P1 adopt" to "permanent reference + attribution." Update slot tracking table accordingly when this is committed.

---

## P1.4 — `chartdetective` (slot: `chart_semantic_extractor`)

| Field | Value |
|---|---|
| Repository | `m-damien/ChartDetective` |
| Commit pinned | `d6d411632574` (2024-03-03) |
| Slot | Slot 7c — chart semantic extraction |
| Priority | P1 |
| License | BSD 2-Clause (Damien Masson, 2023) |
| Decision | **Reference only, not runtime** — adopt the *interaction model and data structures*, not the application |
| Confidence | High that it cannot be a runtime dep; medium that its model is the right reference |

### 1. Problem

Charts in HTML are rendered as SVG, canvas, or images. Native PPT charts require structured data (categories, series, axes). The slot needs a path from "chart visible on screen" to "chart data that pptxgenjs `addChart` can consume" — when recovery is possible.

### 2. Cause

Most chart libraries (D3, Chart.js, ECharts, Plotly) emit SVG marks or canvas rasters without exposing the source data series in the DOM. ChartDetective is the most cited tool for **vector chart extraction** because it parses SVG path commands and clusters them into series. The chart_semantic_extractor slot in GOAL_PROBLEM.md §7 lists ChartDetective as one of several candidates.

### 3. Required input

- Chart DOM region (SVG preferred; canvas requires rasterization first)
- Chart library hints if available (data attributes, ARIA labels)
- Axis label DOM nodes

### 4. Expected output

- Chart type (line / bar / scatter / boxplot)
- Categories (x values)
- Series data (y values per series)
- Axis metadata (units, scale type)
- Confidence score
- Or: explicit "recovery failed" so the chart falls back to image asset

### 5. Reuse candidate evaluation

#### 5.1. X-findings (library representative path)

**ChartDetective is a React + TypeScript desktop application**, not a library. Per `README.md:14-25`:

> "The tool was created using TypeScript and React. To run it, you can use npm. ... `npm start`."

> "Drag-and-drop interactions: (1) select the chart ... (2) select the X axis and then drag and drop it ... (3) Select a mark ... (4) check the extraction by hovering."

The data extraction is **human-in-the-loop by design**. Files of interest:

- `src/view/HookedCanvasFactory.tsx` — PDF/SVG parsing entry, per README's "reporting issues" pointer
- `src/datastructure/ShapeCommand.tsx` — internal data structures
- `public/animations/elements.gif` — UI demonstration

There is no headless API. There is no `extractChartData(svg)` function. The drag-and-drop UI is the extraction mechanism.

#### 5.2. Y-findings (back-tracing from our slot)

The slot requires a programmatic call: `extractChart(domNode) → { type, categories, series, confidence }`. ChartDetective cannot provide this directly.

What can be reused:

| ChartDetective asset | Reusable? | How |
|---|---|---|
| Drag-and-drop UI | **No** | Wrong interaction model for headless conversion |
| Application bootstrap | **No** | We are a Node CLI, not a React app |
| SVG path → ShapeCommand parser | **Possibly** | If `ShapeCommand.tsx` exposes a pure function over SVG path data |
| Clustering of shape commands into series | **Possibly** | The published algorithm is in the CHI'23 paper |
| Data structure (mark / axis / series typing) | **Yes** | TypeScript interfaces are pure types |
| The CHI'23 paper itself | **Yes** | Algorithm description, citable as a reference |

**Critical Y-finding — the slot's success criterion is met by the asset-backed fallback path.** GOAL_PROBLEM.md §7's non-goals state:

> "Do not solve arbitrary canvas chart reconstruction without source data."
> "Do not guarantee native PPT chart recovery for all SVG charts."

A correct interpretation: **failing to recover chart data is not failure of the slot.** The slot is satisfied when the converter (a) recovers data when possible, (b) marks the chart as `chartCandidate` with low confidence and falls back to image asset when not. ChartDetective informs the "when possible" path but cannot be the engine of it.

### 6. Implementation task

#### 6.1. Bootstrap-required (immediate)

> **None.** The bootstrap pipeline treats every chart as `chartCandidate` with confidence=0, falling back to image asset. This satisfies success criterion 5 (*"complex assets are explicitly marked as fallback regions"*).

#### 6.2. Deferred (post-bootstrap)

| Task | Trigger to start |
|---|---|
| Library-specific source data adapters (Chart.js, ECharts, D3 with attached data) | when a target deck uses a known library and data extraction would unlock editability |
| SVG path command parsing for simple line charts | when ChartDetective's `ShapeCommand` parsing can be ported as a pure function |
| Reference implementation of the CHI'23 algorithm | when SVG-only recovery becomes a priority |

### 7. Validation

When deferred work is taken on:

1. A chart with known underlying data (e.g. a fixture deck) is recovered to within 1% of true values, or marked as low-confidence and rasterized.
2. The decision (recovered vs rasterized) is logged in the validation report.
3. No false-positive "recovered" charts with wrong data — better to rasterize than to lie.

### 8. Non-goals

- **Case: Type** — Do not depend on the React UI. Do not run `npm start`.
- **Case: Type** — Do not OCR axis labels. DOM text is available for SVG charts.
- **Case: Performance: Null** — Do not deliver chart recovery in bootstrap.
- **Case: Performance: Over** — Do not embed ChartDetective via iframe or sub-process to "use it headlessly" — the user-interaction is essential to its algorithm.

### 9. Open questions

- Q-cd-1: Is the CHI'23 algorithm self-contained enough to reimplement from the paper, or does it rely on the UI's iterative refinement? Read paper before scheduling deferred work.
- Q-cd-2: For the asset-backed fallback, what minimum chart metadata should we still extract (axis labels, legend) to power validation reports? This is a `chart_semantic_extractor` decision, not a ChartDetective decision.
- Q-cd-3: Does a P2 candidate (`extract-line-chart-data`, `LineFormer`) offer a more directly reusable headless API? Defer evaluation to A-session (`docs/reuse_triage_task_A.md`).

---

## P1.5 — `backstopjs` (slot: `fallback_policy_engine_validation`)

| Field | Value |
|---|---|
| Repository | `garris/BackstopJS` |
| Commit pinned | `930b3c863d39` (v6.3.25, 2024-09-07) |
| Slot | Slot 8 — fallback policy engine + visual validation |
| Priority | P1 |
| License | MIT (Garris Shipon, 2014) |
| Decision | **Reference, not adopt as runtime dep** — borrow workflow patterns, not the binary |
| Confidence | High — overlap with our pipeline is partial but valuable |

### 1. Problem

Visual validation needs more than pixel comparison (pixelmatch, P1.1): it needs orchestration — capturing screenshots in a reproducible way, organizing reference vs current snapshots, tracking diff history over time, and reporting in a developer-readable form. The slot requires both the algorithm (pixelmatch) and the workflow around it.

### 2. Cause

BackstopJS is a mature (since 2014) visual regression testing framework. It already solves: Playwright/Puppeteer integration, reference snapshot lifecycle (`reference` / `test` / `approve` commands), JUnit and HTML reporting, parallelization. Two slots in our manifest fall under it: `fallback_policy_engine_validation` (P1) and the looks-same / VRT alternates.

### 3. Required input

- Source HTML URL or static file
- Rendered PPTX screenshot pipeline output
- Scenario configuration (which pages, which viewports, which interactive states)
- Threshold and AA tolerance configuration

### 4. Expected output

- Reference + test + diff PNG triples per scenario
- A report (HTML or JUnit) listing passes/fails with diff visualization
- Persistence of approved baselines

### 5. Reuse candidate evaluation

#### 5.1. X-findings (library representative path)

BackstopJS's representative workflow is a CLI:

```bash
backstop init        # scaffold config
backstop reference   # capture baseline screenshots
backstop test        # capture current + diff against baseline
backstop approve     # promote current to baseline
```

The `core/runner.js` (`package.json:main`) orchestrates. Dependencies signal the architecture:

- `playwright ^1.40.1` — uses Playwright (same as us; no version conflict if we choose a recent Playwright)
- `puppeteer ^22.1.0` — also bundles Puppeteer as alternative engine
- `@mirzazeyrek/node-resemble-js` — its pixel comparator (a fork of `resemble.js`, **not pixelmatch**)
- `junit-report-builder` — test report emission
- `super-simple-web-server` — local server for static content

Key directories: `capture/` (screenshot logic), `compare/` (diff orchestration around node-resemble-js), `core/` (runner glue), `cli/` (CLI binary).

#### 5.2. Y-findings (back-tracing from our slot)

The slot needs orchestration + reporting around our pixelmatch calls. BackstopJS provides this, but:

| Slot need | BackstopJS provides | Adopt as runtime? |
|---|---|---|
| Playwright screenshot capture | yes | partial — we capture inside our pipeline already |
| Reference vs current snapshot lifecycle | yes | useful pattern, but BackstopJS expects URLs, not generated PPTX files |
| Diff visualization | yes (via node-resemble-js) | **conflicts with P1.1** — we already chose pixelmatch |
| HTML report | yes | adoptable separately |
| JUnit XML report | yes (via `junit-report-builder`) | adoptable separately |
| Threshold per-scenario configuration | yes | inspire our config schema |
| Approve baseline workflow | yes | strong pattern to copy |

**Critical Y-finding — comparator conflict**: BackstopJS uses `node-resemble-js`, not pixelmatch. Adopting BackstopJS as a runtime dep gives us *two* visual diff algorithms in the project — pixelmatch (from P1.1) and node-resemble-js (transitively via BackstopJS). This violates the *"explicit fallback decision > implicit rasterization"* principle by adding a second hidden comparator.

**Second Y-finding — the validation domain is "screenshot vs screenshot of generated PPTX," not "URL vs URL."** BackstopJS scenarios assume URLs (the thing under test is a web page). Our scenarios are: render PPTX → screenshot it → diff against HTML screenshot. We'd be misusing BackstopJS's scenario model.

**Third Y-finding — the workflow patterns are gold even without the binary**: the `reference / test / approve` triad and the directory layout (`backstop_data/{bitmaps_reference,bitmaps_test,html_report,ci_report}/`) are battle-tested conventions. Copying them costs nothing.

### 6. Implementation task

#### 6.1. Bootstrap-required (immediate)

> **Adopt BackstopJS's directory and lifecycle conventions for our own validation tool, without depending on its code.**

Concretely, our `src/validate/` should produce output under:

```text
validation_data/
  reference/   # HTML screenshots (the "truth")
  test/        # PPTX screenshots (the candidate)
  diff/        # pixelmatch outputs (per region or per slide)
  report.html  # human-readable summary
  report.json  # machine-readable, for CI
```

And our CLI should expose at least: `validate reference`, `validate test`, `validate approve` semantically — even if implemented as flags on a single command.

#### 6.2. Deferred (post-bootstrap)

| Task | Trigger to start |
|---|---|
| HTML report template (inspired by BackstopJS's report) | when first multi-slide validation needs human review |
| JUnit XML emission | when CI integration is requested |
| Per-scenario threshold config schema | when single global threshold becomes insufficient |

### 7. Validation

1. Our validation tool produces the directory structure described in §6.1.
2. The `approve` semantics work: re-running `test` after `approve` reports zero diffs (modulo intentional changes).
3. No `backstopjs` import in `package.json`.

### 8. Non-goals

- **Case: State** — Do not commit to BackstopJS's full feature set. We borrow workflow, not framework.
- **Case: Type** — Do not adopt `node-resemble-js`. The comparator decision is closed (pixelmatch, P1.1).
- **Case: Type** — Do not implement multi-engine support (BackstopJS supports both Playwright and Puppeteer; we use Playwright only).
- **Case: Performance: Over** — Do not build a full visual regression platform (GOAL_PROBLEM.md §8 explicit non-goal).

### 9. Open questions

- Q-bs-1: Is JUnit XML report worth implementing in bootstrap if CI integration is on a deferred roadmap? Probably not — JSON report suffices.
- Q-bs-2: Should the `approve` workflow be an explicit subcommand or a flag? Defer to `docs/architecture.md`.

---

## P1.6 — `table_transformer` (slot: `fake_table_detector`)

| Field | Value |
|---|---|
| Repository | `microsoft/table-transformer` |
| Commit pinned | `16d124f61610` (2023-09-06) |
| Slot | Slot 5b — fake table detector (div/grid layouts that look like tables) |
| Priority | P1 |
| License | MIT (Microsoft Corporation) |
| Decision | **Reference only, defer adoption** — Python/PyTorch model, not viable for bootstrap Node pipeline |
| Confidence | High — clear language and runtime mismatch |

### 1. Problem

HTML pages frequently use `<div>` + CSS Grid or Flexbox to render visually table-like content without semantic `<table>` markup. The slot needs detection logic that promotes such layouts into PPT table objects (when confidence is high), or leaves them as individual shapes (when confidence is low).

### 2. Cause

Semantic `<table>` detection is handled by `dom_to_pptx`'s `extractTableData` (Slot 5a, P1.3). Fake tables — visually aligned grids without table semantics — are a separate problem. GOAL_PROBLEM.md §5 lists deterministic bbox clustering as the primary approach for bootstrap, with ML detection as a later option. Table Transformer is the ML option.

### 3. Required input

- Measured visual nodes with bbox in slide coordinates
- Visible borders / backgrounds / text alignment signals
- Or, as fallback: a rasterized image of the candidate region (for image-based detectors like TATR)

### 4. Expected output

- Table candidate IR node with confidence score
- Row and column boundaries
- Cell membership for each child node

### 5. Reuse candidate evaluation

#### 5.1. X-findings (library representative path)

Table Transformer is a **PyTorch deep-learning model** based on DETR. README quote:

> "A deep learning model based on object detection for extracting tables from PDFs and images."

> "TATR is an object detection model that recognizes tables from image input. The inference code built on TATR needs text extraction (from OCR or directly from PDF) as a separate input."

Layout: `src/inference.py` (Python), `detr/` (model code), `environment.yml` (conda environment with PyTorch 1.13.1, Torchvision 0.14.1). Pre-trained weights are downloaded separately (not in the repo).

Representative path:

```bash
conda env create -f environment.yml
python src/inference.py --image_dir <dir> --out_dir <out>
```

Output is a structure detection on rasterized images. Not callable from Node without subprocess invocation.

#### 5.2. Y-findings (back-tracing from our slot)

The slot can be served by two distinct approaches:

| Approach | Source | Fit for bootstrap |
|---|---|---|
| Deterministic bbox clustering | our own code, inspired by `opendataloader-pdf` table processors | **Yes** — explicit recommendation in GOAL_PROBLEM.md §5 non-goal *"start with deterministic bbox clustering before ML-based detection"* |
| ML-based image detection | Table Transformer (Python) | No for bootstrap |

The non-goal text is decisive: **deterministic bbox clustering is the bootstrap path; ML is deferred.** Table Transformer cannot meaningfully participate in bootstrap.

If/when ML-based detection is needed, the integration shape is one of:

1. **Sidecar microservice**: TATR runs as a Python HTTP service; Node pipeline calls it. High operational complexity.
2. **CLI subprocess**: invoke `python src/inference.py` per-page via `child_process`. Slow, brittle.
3. **ONNX export**: export TATR weights to ONNX and run via `onnxruntime-node`. Highest engineering effort, lowest runtime cost.

None of these are bootstrap-scale work.

**Critical Y-finding — measured DOM has signals TATR's image-only path discards.** We have `getBoundingClientRect` outputs and `getComputedStyle` text-align values. TATR works on image pixels and reconstructs what we already know. For our domain (HTML, not PDFs of unknown provenance), deterministic clustering on measured bboxes is likely *more accurate*, not less.

### 6. Implementation task

#### 6.1. Bootstrap-required (immediate)

> **None for `table_transformer`.** Build deterministic bbox clustering in `src/extract/fake-table.ts` based on measured node geometry. TATR is unused in bootstrap.

The clustering algorithm draws from:

- `opendataloader-pdf`'s `ClusterTableProcessor` (Java, design reference)
- bbox alignment: nodes share a column if their `x` and `width` cluster within a tolerance
- text alignment consistency, consistent gap detection, border/background pattern repetition (signals from GOAL_PROBLEM.md §5)

#### 6.2. Deferred (post-bootstrap)

| Task | Trigger to start |
|---|---|
| TATR integration as sidecar | when deterministic clustering fails on a real-world fixture and no algorithmic fix is feasible |
| ONNX export evaluation | when sidecar overhead exceeds bootstrap pipeline cost |
| Alternative ML models from P2 manifests (`surya`, `mineru`) | concurrent with TATR evaluation, delegate to A-session |

### 7. Validation

When deterministic clustering lands:

1. A fixture with both semantic `<table>` and div/grid fake table is processed; both become PPT tables.
2. A fixture with a non-table grid layout (e.g. a CSS grid of distinct cards) does not become a table.
3. Confidence scores are logged for every detected candidate.

### 8. Non-goals

- **Case: Type** — Do not run Python in the bootstrap pipeline. Node-only.
- **Case: Type** — Do not OCR text. DOM text is available.
- **Case: Performance: Null** — Do not optimize fake table detection speed in bootstrap.
- **Case: Performance: Over** — Do not build a Python sidecar before deterministic clustering is shown to be insufficient. *"Implementation is cheap; reconstruction is expensive"* — but only when reconstruction is actually needed.

### 9. Open questions

- Q-tt-1: Is the deterministic clustering implementation a fresh design or a port of opendataloader-pdf's Java code? Decide in `docs/architecture.md`.
- Q-tt-2: What confidence threshold separates "promote to table" from "leave as shapes"? Empirical, decide after first fixtures.
- Q-tt-3: Should fake table detection have its own non-table-but-aligned IR type (`gridRegion`)? Schema decision for `src/ir/schema.ts`.

---

## Summary — six P1 decisions and their pipeline shape

| P1 | Slot(s) | Decision | Bootstrap action |
|---|---|---|---|
| pixelmatch | fallback_validation | Adopt as dep | Build image normalization adapter |
| pptxgenjs | pptx_output_backend | Adopt as dep | Build IR → pptxgen translator |
| dom_to_pptx | 1, 2, 3, 4, 5a, 6 | Transplant pure functions | Vendor 6 functions with attribution |
| chartdetective | chart_semantic_extractor | Reference only | None — chart=asset fallback |
| backstopjs | fallback_policy_engine_validation | Workflow reference | Adopt directory layout + lifecycle commands |
| table_transformer | fake_table_detector | Reference only, deferred | Build deterministic bbox clustering |

**The bootstrap pipeline depends on exactly two npm packages from the P1 set**: `pixelmatch` and `pptxgenjs`. All other reuse takes the form of code transplantation (with attribution) or pattern adoption. This is consistent with *"reuse existing modules > write new code"* read as *"reuse existing engineering, not necessarily existing packages."*

**The dom_to_pptx finding is the most significant**: its six-slot concentration translates into six pure-function transplants, not a single dependency. The transplantation strategy avoids both extremes (don't depend on the whole thing, don't reinvent six wheels).

**Two slots are intentionally underserved in bootstrap**: `chart_semantic_extractor` and `fake_table_detector`. Their P1 candidates are not viable for Node bootstrap, and GOAL_PROBLEM.md's non-goals explicitly accept this state (Performance: Null, Performance: Under).

---

## Cross-cutting open questions for downstream sessions

- **CQ-1** (architecture.md): What is the exact boundary between Playwright `page.evaluate` (browser-side) and Node-side processing? The dom_to_pptx transplant decision (P1.3 Q-d2p-1) is the forcing function.
- **CQ-2** (architecture.md): IR schema must accommodate all 12 minimum types (GOAL_PROBLEM.md §"Visual Object IR requirements") *and* the confidence/fallback metadata implied by P1.1, P1.4, P1.6.
- **CQ-3** (deletion_candidates.md): Should `dom_to_pptx` be removed from `third_party/repositories.toml` after the transplant lands, given it shifts from "P1 adopt" to "reference + attribution"? Manifest semantics decision.
- **CQ-4** (reuse_triage_task_A.md): P2/P3 candidates (`html2pptxgenjs`, `surya`, `extract-line-chart-data`, `looks-same`, etc.) need shallow triage to confirm none of them invalidate a P1 adopt decision above.
