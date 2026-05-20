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
