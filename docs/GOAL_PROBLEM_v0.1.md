# Goal Problem

## Problem statement

Build an editability-first HTML to PPTX parser.

The parser must convert a rendered HTML page into native, editable PowerPoint objects wherever possible. It should not default to screenshot export.

## Priority

```text
editability > visual fidelity
validated output > unverified output
reuse existing modules > write new code
explicit fallback decision > implicit rasterization
```

## Target conversion policy

Asset-backed objects are acceptable for:

- SVG and icon assets
- PNG / JPG / GIF
- video thumbnails
- complex effects that cannot be represented as stable native PPT objects

Editable PPT objects are required where possible for:

- text
- rich text runs
- shapes
- tables
- charts

## Required reusable module slots

The project must explicitly track these reusable module slots.

| Slot | Required role | Expected source |
|---|---|---|
| 1 | getBoundingClientRect/getComputedStyle based extractor | dom-to-pptx / custom Playwright extractor |
| 2 | renderQueue-style intermediate render item queue | dom-to-pptx, then project Visual Object IR |
| 3 | text run collector | dom-to-pptx / html2pptxgenjs |
| 4 | background/border/radius/shadow mapper | dom-to-pptx / PptxGenJS mapper |
| 5 | semantic HTML table extractor | dom-to-pptx / PptxGenJS table utilities |
| 6 | image/SVG asset mapper | dom-to-pptx / PptxGenJS image utilities |
| 7 | semantic element + bbox JSON schema | opendataloader-pdf / Docling / Unstructured |
| 8 | PPTX output and validation backend | PptxGenJS / visual validation tools |

## Are all 8 slots represented in this repository?

Yes, as tracked candidate sources. But they are not yet implemented as project-native modules.

| Slot | Present as candidate? | Native implementation status |
|---|---:|---|
| getBoundingClientRect/getComputedStyle extractor | yes | not implemented |
| renderQueue intermediate queue | yes | not implemented |
| text run collector | yes | not implemented |
| background/border/radius/shadow mapper | yes | not implemented |
| semantic HTML table extractor | yes | not implemented |
| image/SVG asset mapper | yes | not implemented |
| semantic element + bbox JSON schema | yes | not implemented |
| PPTX output/validation backend | yes | not implemented |

## Core pipeline

```text
HTML / CSS / JS-rendered page
  -> Playwright browser rendering
  -> DOM geometry and computed style extraction
  -> measured visual nodes
  -> Visual Object IR
  -> semantic candidates
  -> editable PPTX object mapper
  -> PPTX generation
  -> rendered validation
```

## Visual Object IR requirements

The project must not map DOM nodes directly to PPT objects.

A DOM node should pass through these layers:

```text
DOM node
  -> measured visual node
  -> semantic candidate
  -> PPT mapping decision
  -> PPTX object
```

Minimum IR object types:

- document
- slide/page
- group
- text
- richTextRun
- shape
- image
- table
- tableRow
- tableCell
- chartCandidate
- fallbackRegion

## opendataloader-pdf modules that can be reused or studied

opendataloader-pdf is not an HTML to PPTX parser. It is still useful because it solves a similar representation problem:

```text
raw visual document
  -> semantic content elements
  -> bbox-aware JSON
  -> multiple output generators
```

### 1. JSON schema

Useful file:

```text
schema.json
```

Reusable concepts:

- document metadata
- top-level `kids`
- `contentElement`
- `baseElement`
- `bounding box`
- `paragraph`
- `heading`
- `caption`
- `table`
- `tableRow`
- `tableCell`
- `textBlock`
- `list`
- `listItem`
- `image`
- `headerFooter`

Use in this project:

```text
opendataloader contentElement
  -> html-to-editable-pptx VisualObjectIR
```

### 2. Processing pipeline

Useful file:

```text
java/opendataloader-pdf-core/src/main/java/org/opendataloader/pdf/processors/DocumentProcessor.java
```

Internal modules worth studying:

- DocumentProcessor
- TaggedDocumentProcessor
- HybridDocumentProcessor
- ContentFilterProcessor
- HiddenTextProcessor
- ClusterTableProcessor
- TableBorderProcessor
- StrikethroughProcessor
- SpecialTableProcessor
- TextLineProcessor
- HeaderFooterProcessor
- ListProcessor
- ParagraphProcessor
- HeadingProcessor
- CaptionProcessor
- LevelProcessor
- AutoTaggingProcessor
- ContentSanitizer
- ImagesUtils
- JsonWriter
- MarkdownGenerator
- HtmlGenerator
- TextGenerator
- PDFWriter

Use in this project:

```text
DocumentProcessor-style stages
  -> Extract
  -> Normalize
  -> Enrich
  -> Assign IDs
  -> Detect structure
  -> Generate outputs
  -> Validate
```

### 3. Table processors

Useful concepts:

- border-based table detection
- cluster table detection
- special table detection
- neighboring table linking
- row/column/cell model
- row span / column span
- nested content inside cells

Use in this project:

```text
HTML fake table region
  -> bbox cluster detection
  -> row/column grouping
  -> tableCell candidate
  -> PPT native table
```

### 4. Reading order and structure

Useful concepts:

- XY-Cut style reading order
- heading hierarchy detection
- list detection
- header/footer filtering
- caption linking
- level detection

Use in this project:

```text
DOM order + visual order + z-order
  -> reading order
  -> PPT object insertion order
  -> accessibility-friendly order
```

### 5. Output generator pattern

Useful files/classes:

- JsonWriter
- MarkdownGenerator
- HtmlGenerator
- TextGenerator
- PDFWriter

Use in this project:

```text
Visual Object IR
  -> PPTX generator
  -> debug HTML generator
  -> JSON dump
  -> validation report
```

### 6. HtmlGenerator semantic mapping

Useful file:

```text
java/opendataloader-pdf-core/src/main/java/org/opendataloader/pdf/html/HtmlGenerator.java
```

Reusable mapping pattern:

- SemanticHeading -> heading tag
- SemanticParagraph -> paragraph tag
- PDFList -> list tags
- TableBorder -> table/tr/th/td
- ImageChunk -> img
- SemanticPicture -> figure/img
- SemanticTextNode -> figcaption
- SemanticFormula -> math block

Use in this project:

```text
Visual Object IR element
  -> PPT native object
```

The target generator is different, but the dispatch pattern is reusable.

### 7. Options and policy surface

Useful file:

```text
options.json
```

Reusable option ideas:

- output format selection
- keep line breaks
- table method selection
- reading order selection
- image output mode
- page range selection
- include header/footer
- hybrid fallback
- thread count

Use in this project:

```text
conversion policy options
  -> editability-first / visual-first / hybrid
  -> table detection mode
  -> chart extraction mode
  -> fallback threshold
  -> validation threshold
```

## What must still be built here

Existing repositories reduce the cost, but these project-native modules are still required:

1. HTML/PPTX-specific Visual Object IR schema
2. measured DOM node extractor
3. wrapper vs visual object normalizer
4. DOM text subtree to rich text runs
5. fake table detector for div/grid layouts
6. chart library source-data adapters
7. SVG chart semantic parser
8. fallback policy engine
9. PPTX renderer/validator integration
10. deletion candidate tracking

## Success criteria

A conversion is acceptable when:

1. important text remains editable;
2. shapes remain editable where CSS can be mapped to PPT safely;
3. semantic HTML tables become native PPT tables;
4. chart data becomes native PPT chart data when source data is recoverable;
5. complex assets are explicitly marked as fallback regions;
6. rendered PPTX is validated against the source screenshot;
7. every lossy decision is recorded in a report.

## Non-goals

Non-goals exist to keep the work inside the correct responsibility boundary.

> **Core concept**: A non-goal is not an unimportant thing. It is a boundary-setting device that defines what this decision or task is not responsible for.

### Why non-goals matter here

Non-goals should reduce scope drift in Codex or agent handoff work.

Expected effect:

- reduce the chance that Codex edits unrelated areas;
- make handoff quality higher;
- separate current task responsibility from future optimization;
- make side effects visible without forcing the current task to solve all of them.

### What is not a non-goal

- A non-goal is not a failed state.
- A non-goal is not a trivial issue that can be ignored.
- A non-goal is not permission to produce unvalidated or unusable output.

### Side-effect caution

Some side effects may harm the system, but not every side effect is the responsibility of the current task.

Use a non-goal when:

```text
we recognize the side effect
but this task does not own the optimization or full remediation
```

### Non-goal categories

| Case | Meaning | Example |
|---|---|---|
| State | Defines a state transition that is not guaranteed | Improve A state, but do not guarantee transition into B state |
| Type | Excludes specific error types or exception classes from this task | Handle semantic HTML tables, but not arbitrary canvas chart recovery |
| Performance: Null | No performance improvement target in this task | Build validated prototype first; no speed target |
| Performance: Over | Avoid unnecessary high-spec or over-engineered work | Do not build a full browser engine or full CSS renderer |
| Performance: Under | A known performance limit is not treated as a defect in this decision | Slow validation is acceptable in bootstrap phase |

### Project non-goals

#### Case: State

- Do not guarantee pixel-perfect visual equality in the first implementation.
- Do not guarantee that every rendered HTML node becomes a native PPT object.
- Do not guarantee that every fallback region can later be automatically reconstructed into editable objects.
- Do not guarantee that a generated PPTX will look identical across PowerPoint, Keynote, LibreOffice, and PowerPoint Online.

#### Case: Type

- Do not solve arbitrary canvas-to-native-PPT-chart reconstruction without source data.
- Do not solve arbitrary SVG chart-to-native-PPT-chart reconstruction in the base pipeline.
- Do not convert video into editable timeline objects; video may be represented as an asset or thumbnail.
- Do not require GIF frame-level editing.
- Do not require full CSS feature parity for `filter`, `backdrop-filter`, `mix-blend-mode`, `mask`, and complex `clip-path`.
- Do not treat every div/grid layout as a semantic table unless table-like structure is detected by explicit rules.
- Do not treat image OCR as the primary path for text extraction when DOM text is available.

#### Case: Performance: Null

- Do not optimize conversion speed before the Visual Object IR and validation reports exist.
- Do not target batch-scale throughput before a single-page validated path is working.
- Do not optimize memory usage before repository reuse and module boundaries are clear.

#### Case: Performance: Over

- Do not implement a custom CSS layout engine.
- Do not reimplement browser rendering when Playwright can provide computed layout.
- Do not build a full PDF parser for this project; use document parser references only for schema and processor design.
- Do not build a full visual regression platform when existing diff tools can be used.
- Do not create a large agent framework before concrete extraction, IR, mapping, and validation modules exist.

#### Case: Performance: Under

- It is acceptable for the first validated prototype to be slow.
- It is acceptable for visual validation to run as a separate post-processing step.
- It is acceptable for chart semantic extraction to be partial and library-specific.
- It is acceptable for fake table detection to start with deterministic bbox clustering before ML-based detection.

### Non-goal review rule

When a new task is created, include a short non-goal block if the task could drift into neighboring work.

Recommended format:

```text
Goal:
- ...

Non-goals:
- Case: State: ...
- Case: Type: ...
- Case: Performance: ...

Validation:
- ...
```

## Technical Problems and Tasks

This section turns the goal into implementation work. Each technical problem must have an explicit cause, required input, expected output, reuse candidate, implementation task, validation rule, and non-goal boundary.

### 1. Browser layout to PPT coordinate mapping

**Problem:** HTML/CSS layout does not directly provide PPT coordinates.

**Cause:** CSS layout is resolved by the browser after applying cascade, inheritance, layout algorithms, font metrics, transforms, and viewport rules.

**Required input:**

- rendered page viewport size
- DOM node identity
- `getBoundingClientRect()` output
- `getComputedStyle()` output
- device pixel ratio
- target slide size

**Expected output:**

- measured visual node with normalized bbox
- slide-space coordinates
- source DOM path
- computed style snapshot

**Reuse candidate:**

- `dom-to-pptx`
- custom Playwright extractor

**Implementation task:**

Create `src/extract` module that returns measured visual nodes from a rendered page.

**Validation:**

- bbox values must map to slide coordinates deterministically;
- source screenshot and debug overlay must align within a configured tolerance;
- every extracted node must preserve source DOM identity.

**Non-goal:**

- Do not implement a custom CSS layout engine.
- Do not support multiple responsive breakpoints in the first validated path.

### 2. DOM tree to Visual Object IR normalization

**Problem:** DOM nodes do not map 1:1 to PowerPoint objects.

**Cause:** HTML contains layout wrappers, framework containers, pseudo-visual nodes, semantic tags, and nested structures that may not correspond to editable PPT objects.

**Required input:**

- measured visual nodes
- DOM parent/child relationships
- computed visual styles
- visibility and opacity
- z-order hints
- text/image/table/chart candidates

**Expected output:**

- Visual Object IR nodes
- stable object IDs
- parent/child grouping
- semantic candidate type
- mapping confidence

**Reuse candidate:**

- `dom-to-pptx` renderQueue pattern
- `opendataloader-pdf` contentElement schema pattern
- Docling / Unstructured element models

**Implementation task:**

Create `src/ir/schema.ts` and a normalizer that converts measured DOM nodes into typed IR objects.

**Validation:**

- layout-only wrappers should not become unnecessary PPT objects;
- visible backgrounds/borders/text/images/tables should become explicit IR candidates;
- the IR must be serializable to JSON.

**Non-goal:**

- Do not guarantee every DOM node is preserved as a PPT object.
- Do not infer full authoring intent from arbitrary class names.

### 3. HTML text subtree to PPT rich text runs

**Problem:** Browser text and PPT text use different layout and rich text models.

**Cause:** HTML text may be split across text nodes, spans, inline styles, links, strong/em tags, nested elements, and CSS inheritance. PPT expects text boxes and runs with explicit options.

**Required input:**

- text DOM subtree
- text node order
- inherited computed style
- inline formatting
- hyperlinks
- line-height / letter-spacing / white-space signals

**Expected output:**

- editable text IR node
- ordered rich text runs
- paragraph boundaries
- optional line boxes
- text fallback risk score

**Reuse candidate:**

- `dom-to-pptx` text part collection
- `html2pptxgenjs`
- PptxGenJS rich text API

**Implementation task:**

Create a text run collector that converts DOM text subtrees into editable PPT text runs.

**Validation:**

- bold/italic/underline/color/font-size changes must survive in run output;
- text order must match rendered reading order;
- text must remain editable in generated PPTX.

**Non-goal:**

- Do not guarantee browser-identical automatic line wrapping in the first version.
- Do not use OCR when DOM text is available.

### 4. CSS visual style to PPT shape mapping

**Problem:** CSS visual styles and PPT shape options are not the same model.

**Cause:** CSS supports backgrounds, borders, radii, shadows, gradients, filters, masks, blend modes, and clipping. PPT supports only a subset as stable native objects.

**Required input:**

- computed background
- border properties
- border radius
- box shadow
- opacity
- transform
- clipping and overflow signals

**Expected output:**

- shape IR node
- PPT shape mapping options
- unsupported-style flags
- fallback risk score

**Reuse candidate:**

- `dom-to-pptx` background/border/radius/shadow mapping
- PptxGenJS shape API

**Implementation task:**

Create a style mapper that converts safe CSS visual styles into PPT shape options and marks unsupported effects explicitly.

**Validation:**

- simple backgrounds, borders, radii, and outer shadows must map to native PPT shapes;
- unsupported effects must be recorded in the validation report;
- complex effects must not silently disappear.

**Non-goal:**

- Do not implement full CSS feature parity.
- Do not require native PPT reconstruction for `backdrop-filter`, complex masks, or blend modes.

### 5. Semantic HTML table and fake table detection

**Problem:** HTML tables and visually table-like layouts need different extraction paths.

**Cause:** Semantic tables use `table`, `tr`, `td`, and `th`, while fake tables are often `div` or CSS grid layouts with aligned cells but no table semantics.

**Required input:**

- semantic table DOM subtree
- measured bbox clusters
- row/column alignment data
- cell text and styles
- span information if available

**Expected output:**

- table IR node
- row and cell IR nodes
- rowSpan / colSpan where known
- cell text and style mapping
- table confidence score

**Reuse candidate:**

- `dom-to-pptx` semantic table extractor
- PptxGenJS table utilities
- `opendataloader-pdf` table row/cell/span model
- `table-transformer` and deterministic bbox clustering for fake tables

**Implementation task:**

Create a semantic table extractor first, then add fake table detection using bbox clustering.

**Validation:**

- semantic HTML tables must become native PPT tables;
- fake table candidates must include a confidence score;
- low-confidence fake tables must not be forced into invalid PPT tables.

**Non-goal:**

- Do not treat every grid layout as a table.
- Do not require ML-based fake table detection in the first implementation.

### 6. Image, SVG, icon, GIF, and video asset mapping

**Problem:** Non-text media must be preserved without blocking editability of surrounding objects.

**Cause:** Images and media are already asset-like, while SVGs may contain editable vector structure, chart semantics, icons, or complex styling.

**Required input:**

- image source URL or data URI
- SVG source
- CSS background-image
- object-fit / object-position
- media bbox
- alt text or accessible name
- z-order

**Expected output:**

- image asset IR node
- SVG asset IR node
- video thumbnail or asset reference
- crop and placement metadata
- alt text metadata

**Reuse candidate:**

- `dom-to-pptx` image/SVG asset mapper
- PptxGenJS image utilities
- `opendataloader-pdf` image metadata pattern

**Implementation task:**

Create an asset mapper that preserves media placement and metadata while keeping nearby text/shapes editable.

**Validation:**

- images must be placed with correct bbox;
- crop behavior must be explicit;
- alt text should be preserved when available;
- media fallback must be recorded.

**Non-goal:**

- Do not convert video into editable timeline objects.
- Do not require GIF frame-level editing.
- Do not treat every SVG as a chart.

### 7. Chart semantic extraction and native PPT chart mapping

**Problem:** Charts are visually rendered objects, but native PPT charts require structured data.

**Cause:** Chart libraries may render as SVG, canvas, HTML, or images. The visual output often does not expose the original data series, axes, scales, or legend mappings in a consistent way.

**Required input:**

- chart DOM region
- chart library hints
- SVG nodes if present
- canvas source hooks if available
- axis labels
- legend labels
- extracted data series when recoverable

**Expected output:**

- chartCandidate IR node
- chart type
- categories / x values
- series data
- axis metadata
- confidence score
- fallback reason if semantic recovery fails

**Reuse candidate:**

- ChartDetective
- extract-line-chart-data
- LineFormer
- ChartReader
- svgdigitizer
- PptxGenJS chart API

**Implementation task:**

Start with chart library source-data adapters, then add SVG chart parsing for selected chart types.

**Validation:**

- recovered chart data must round-trip into a native PPT chart;
- chart confidence must be recorded;
- low-confidence charts must remain asset-backed rather than producing misleading editable charts.

**Non-goal:**

- Do not solve arbitrary canvas chart reconstruction without source data.
- Do not guarantee native PPT chart recovery for all SVG charts.

### 8. Native object versus fallback policy

**Problem:** The converter must decide when to preserve editability and when to use fallback assets.

**Cause:** Some CSS effects, media, charts, and complex containers cannot be represented faithfully as stable native PPT objects.

**Required input:**

- Visual Object IR
- unsupported-style flags
- semantic confidence scores
- rendered HTML screenshot
- rendered PPTX screenshot
- diff results

**Expected output:**

- fallback decision per object or region
- fallback reason
- editability score
- visual mismatch score
- validation report

**Reuse candidate:**

- pixelmatch
- looks-same
- odiff
- BackstopJS
- Visual Regression Tracker

**Implementation task:**

Create a fallback policy engine that records native-object, partial-native, and asset-backed decisions explicitly.

**Validation:**

- every fallback must have a reason;
- generated PPTX must be rendered and compared against the source screenshot;
- validation report must include mismatch and editability scores.

**Non-goal:**

- Do not build a full visual regression platform before a local validator works.
- Do not let fallback decisions happen silently.

### 9. Output generation and validation backend

> **Terminology link**: The "validation report" defined in this
> section is the concrete form of what ULTIMATE_GOAL_v0.1.md §4-C4
> calls "agent-side pre-evaluation" or "self-assessment". The two
> documents use different terms at different abstraction levels:
> ULTIMATE_GOAL describes the *act* of producing a self-assessment
> before user evaluation; this document defines its *content*
> (mismatch score, editability score, fallback reasons, etc.).

**Problem:** The IR must become a PPTX file that can be inspected and validated.

**Cause:** Mapping IR to PPTX is only useful if the resulting file is renderable, editable, and testable.

**Required input:**

- Visual Object IR
- PPT mapping decisions
- assets
- target slide size
- validation configuration

**Expected output:**

- PPTX file
- debug JSON
- optional debug HTML overlay
- rendered PPTX screenshot
- validation report

**Reuse candidate:**

- PptxGenJS
- existing slide rendering and validation tools
- visual diff tools

**Implementation task:**

Create a PPTX compiler and validation wrapper that can be run in CI or Codex Web.

**Validation:**

- output PPTX must open and render;
- important text objects must remain editable;
- validation artifacts must be written to disk.

**Non-goal:**

- Do not optimize for batch throughput until the single-page path is stable.

### 10. Deletion candidate tracking

**Problem:** Removing code or dependencies is risky because reconstruction is expensive.

**Cause:** A module may look unused before the IR, mapper, or validator has enough context to prove it is unnecessary.

**Required input:**

- reuse report
- module ownership map
- dependency graph
- failed validation records
- duplicate functionality records

**Expected output:**

- `docs/deletion_candidates.md`
- reason for deletion candidate status
- evidence required before deletion
- owner module affected by deletion

**Reuse candidate:**

- agent skill references
- repository reuse report
- validation reports

**Implementation task:**

Create a deletion candidate document before deleting or replacing modules.

**Validation:**

- every deletion candidate must include evidence;
- no project dependency should be removed without a documented replacement or non-use proof.

**Non-goal:**

- Do not delete uncertain modules during bootstrap.
- Do not optimize dependency count before reuse analysis is complete.
