# Architecture v0.1

This document describes the first architecture blueprint for `html-to-editable-pptx`.

The core goal is to convert rendered HTML into editable PowerPoint objects, not to export screenshots by default.

## 1. Architecture summary

```text
Rendered HTML
  -> browser measurement
  -> measured visual nodes
  -> Visual Object IR
  -> semantic candidates
  -> editable PPT object mapping
  -> PPTX generation
  -> rendered validation
```

## 2. Full pipeline

```mermaid
flowchart TD
    A[HTML / CSS / JS-rendered Page] --> B[Playwright Browser Rendering]

    B --> C[DOM Geometry Extractor]
    B --> D[Computed Style Extractor]
    B --> E[Asset Extractor]

    C --> F[Measured Visual Nodes]
    D --> F
    E --> F

    F --> G[Visual Object IR Normalizer]

    G --> H[Semantic Candidate Classifier]

    H --> H1[Text Candidate]
    H --> H2[Shape Candidate]
    H --> H3[Image / SVG / Media Candidate]
    H --> H4[Table Candidate]
    H --> H5[Chart Candidate]
    H --> H6[Group Candidate]
    H --> H7[Fallback Region Candidate]

    H1 --> I1[Text Run Collector]
    H2 --> I2[Shape Style Mapper]
    H3 --> I3[Asset Mapper]
    H4 --> I4[Table Extractor / Fake Table Detector]
    H5 --> I5[Chart Semantic Extractor]
    H6 --> I6[Group Mapper]
    H7 --> I7[Fallback Policy Engine]

    I1 --> J[Editable PPTX Object Mapper]
    I2 --> J
    I3 --> J
    I4 --> J
    I5 --> J
    I6 --> J
    I7 --> J

    J --> K[PPTX Generator]

    K --> L[Rendered PPTX]
    B --> M[Source HTML Screenshot]

    L --> N[Validation Engine]
    M --> N

    N --> O[Validation Report]
    N --> P[Fallback Decision Report]
    N --> Q[Editability Report]

    O --> R{Acceptable?}
    R -->|Yes| S[Final PPTX]
    R -->|No| T[Revise IR / Mapping / Fallback Policy]
    T --> G
```

## 3. Layered module design

```mermaid
flowchart LR
    subgraph InputLayer[Input Layer]
        A1[HTML]
        A2[CSS]
        A3[JS Runtime]
        A4[External Assets]
    end

    subgraph RenderLayer[Browser Render Layer]
        B1[Playwright]
        B2[getBoundingClientRect]
        B3[getComputedStyle]
        B4[DOM Traversal]
    end

    subgraph ExtractionLayer[Extraction Layer]
        C1[Measured Visual Node Extractor]
        C2[Text Node Extractor]
        C3[Image / SVG Extractor]
        C4[Table DOM Extractor]
        C5[Chart Region Detector]
    end

    subgraph IRLayer[Visual Object IR Layer]
        D1[Visual Object IR Schema]
        D2[Wrapper Normalizer]
        D3[Semantic Candidate Classifier]
        D4[Reading Order Resolver]
        D5[Z-order Resolver]
    end

    subgraph MappingLayer[PPT Mapping Layer]
        E1[Text Run Collector]
        E2[Shape Mapper]
        E3[Image / SVG Asset Mapper]
        E4[Native Table Mapper]
        E5[Native Chart Mapper]
        E6[Fallback Region Mapper]
    end

    subgraph OutputLayer[Output Layer]
        F1[PptxGenJS Backend]
        F2[PPTX File]
        F3[Debug JSON]
        F4[Debug HTML Overlay]
    end

    subgraph ValidationLayer[Validation Layer]
        G1[Render PPTX]
        G2[Pixel Diff]
        G3[Overflow Check]
        G4[Font Substitution Check]
        G5[Editability Score]
        G6[Validation Report]
    end

    InputLayer --> RenderLayer
    RenderLayer --> ExtractionLayer
    ExtractionLayer --> IRLayer
    IRLayer --> MappingLayer
    MappingLayer --> OutputLayer
    OutputLayer --> ValidationLayer
    ValidationLayer --> IRLayer
```

## 4. Reuse blueprint

```mermaid
flowchart TD
    subgraph ExistingRepos[Reusable Existing Repositories]
        R1[dom-to-pptx]
        R2[html2pptxgenjs]
        R3[PptxGenJS]
        R4[opendataloader-pdf]
        R5[Docling / Unstructured]
        R6[table-transformer]
        R7[ChartDetective / LineFormer]
        R8[pixelmatch / odiff / looks-same]
    end

    subgraph ProjectModules[Project Native Modules]
        M1[Measured DOM Extractor]
        M2[Visual Object IR]
        M3[Text Run Collector]
        M4[Shape Style Mapper]
        M5[Table Detector]
        M6[Chart Semantic Extractor]
        M7[Fallback Policy Engine]
        M8[PPTX Compiler]
        M9[Validation Runner]
    end

    R1 --> M1
    R1 --> M2
    R1 --> M4

    R2 --> M3

    R3 --> M8

    R4 --> M2
    R4 --> M5
    R4 --> M9

    R5 --> M2

    R6 --> M5

    R7 --> M6

    R8 --> M9

    M1 --> M2
    M2 --> M3
    M2 --> M4
    M2 --> M5
    M2 --> M6
    M3 --> M8
    M4 --> M8
    M5 --> M8
    M6 --> M8
    M7 --> M8
    M8 --> M9
    M9 --> M7
```

## 5. Native object versus fallback decision flow

```mermaid
flowchart TD
    A[Visual Object Candidate] --> B{Can be native editable PPT object?}

    B -->|Yes| C[Map to Native PPT Object]
    B -->|Partially| D[Split Object]

    D --> D1[Editable Text / Shape Layer]
    D --> D2[Asset-backed Visual Layer]

    B -->|No| E[Create Fallback Region]

    C --> F[PPTX Output]
    D1 --> F
    D2 --> F
    E --> F

    F --> G[Render Validation]
    G --> H{Pass validation?}

    H -->|Yes| I[Keep Mapping]
    H -->|No| J[Record Failure Reason]

    J --> K{Can adjust mapping?}
    K -->|Yes| L[Revise IR / Mapper]
    K -->|No| M[Explicit Fallback Decision]

    L --> B
    M --> F
```

## 6. Minimal v0.1 path

For the first implementation, the shortest useful path is:

```mermaid
flowchart TD
    A[Rendered HTML] --> B[Extract DOM Rect + Computed Style]
    B --> C[Measured Visual Nodes]
    C --> D[Visual Object IR]
    D --> E[Semantic Candidates]
    E --> F[Editable PPT Object Mapping]
    E --> G[Fallback Region Mapping]
    F --> H[PPTX Generation]
    G --> H
    H --> I[Render PPTX]
    I --> J[Validation Report]
    J --> K{Accept?}
    K -->|Yes| L[Final PPTX]
    K -->|No| M[Revise IR / Mapping / Fallback]
    M --> D
```

## 7. v0.1 implementation order

1. Define `src/ir/schema.ts`.
2. Create measured DOM extraction prototype.
3. Convert simple text, shape, image, and semantic table objects.
4. Generate PPTX through PptxGenJS.
5. Render PPTX and compare against the source screenshot.
6. Write validation and fallback reports.
7. Add fake table and chart recovery only after the base path is validated.

## 8. Explicit non-goals for v0.1

- Do not build a custom CSS layout engine.
- Do not guarantee pixel-perfect visual equality.
- Do not solve arbitrary canvas chart reconstruction.
- Do not solve arbitrary SVG chart semantic recovery.
- Do not create a full visual regression platform.
- Do not optimize for batch throughput before the single-page path is stable.
