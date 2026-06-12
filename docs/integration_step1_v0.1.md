# Integration Step 1 — h2p source merge

Date: 2026-06-12
Branch: `main` selective merge from parser packet
Resolves: AE-01, AE-02, AE-05, AE-06 (partial evidence)
Closes D7, D8 from integration diff analysis (2026-06-12). D1 subtree import is
deferred; this merge uses the Step 2 resolver decision instead.

---

## What was done

### 1. dom-to-pptx reuse (D1 deferred, D-2-1 active)

`third_party/subtrees/dom-to-pptx` whole-repo subtree import is **not included** in
this merge. The active reuse decision is D-2-1:

```
default:  import("dom-to-pptx") as an optionalDependency
fallback: src/output/normalize-zip.js
```

The fallback preserves the normalizer reuse surface without adding the whole repo
subtree to this commit. A future subtree import, if needed, must remain a separate
single-purpose commit.

### 2. Parser source (D7 해소 — IR 계약)

`src/ir/schema.ts` v1.2.0 (불변식 I1–I9) — AE-01 해소.

```
src/
  ir/schema.ts           IR contract v1.2.0
  ir/validate.js         runtime validator
  extract/weasy_extract.py   HTML → IR (WeasyPrint, rule-based)
  map/ir_to_pptx.mjs     IR → PPTX (PptxGenJS)
  validate/
    validate_ab.py       Layer A (bag-of-lines) + Layer B (MD5)
    pixel_c.mjs          Layer C (pixelmatch, chart mask support)
    layout_d.py          Layer D (IR bbox vs OOXML xfrm IoU)
```

`src/map/ir_to_pptx.mjs` normalizer resolution:
runtime import of optional `dom-to-pptx` first, then automatic fallback to
`src/output/normalize-zip.js`.

### 3. npm deps + repositories.toml (D8 해소)

신규 `package.json` (루트). 4종 신규 의존성 `third_party/repositories.toml` 등록:
- `jszip` — OOXML re-pack (category: pptx_output_backend)
- `xmldom` — DOMParser polyfill for normalizer (category: pptx_output_backend)
- `pngjs` — PNG codec for pixelmatch (category: fallback_validation)
- `weasyprint` — CSS layout engine, pip (category: visual_object_ir_normalizer)

### 4. .gitignore + out/.gitkeep

`out/` 산출물 제외, `.gitkeep`으로 디렉토리 유지.

### 5. skills/software-development 신규 카테고리

`cross-representation-verification` 스킬 추가.
category: `software-development` (기존: agent-collaboration, architecture).

---

## AE finding responses

| Finding | Response |
|---------|----------|
| AE-01 IR contract undefined | `src/ir/schema.ts` v1.2.0, invariants I1–I9 defined |
| AE-02 renderer unowned | `scripts/run.sh` LibreOffice portable resolver owns PPTX→render |
| AE-05 Playwright boundary unanswered | WeasyPrint = deterministic extraction backend; IR abstraction isolates backend choice |
| AE-06 acceptance metrics unnamed | Layer A: missing=0 + jaccard≥1.0 per slide; Layer B: MD5 match; Layer C: diffPct<5%; Layer D: IoU>0.90, nativeObjectRatio≥0.8 (`editabilityScore` is a legacy alias, not final edit-quality scoring) |

---

## Validation pass criteria (smoke test)

```bash
npm ci
bash scripts/run.sh fixtures/deck.html
```

| Check | File | Criterion |
|-------|------|-----------|
| Layer A | `out/deck.ab.json` | `layerA_semantic.pass: true`, all slides `jaccard: 1.0` |
| Layer B | `out/deck.ab.json` | `layerB_media.pass: true` |
| Layer C | stdout stage-4 | each slide `diffPct < 5` |
| Layer D | `out/deck.d.json` | `layerD_layout.pass: true`, `worstIoU > 0.90` |
| Native object ratio | `out/deck.mapreport.json` | `nativeObjectRatio: 1`, `editabilityScore: 1` legacy alias, `fallback: 0` |

---

## Remaining (not in this step)

| Item | Note |
|------|------|
| AE-03 | reuse-decision 3계층 reconciliation |
| AE-04 | vocabulary crosswalk: map/mapper/stage naming |
| AE-08 | Python+Node mixed runtime topology formal record |
| pixelmatch / looks-same / odiff subtree | decisions exist in subtrees.toml, execution pending |
| D2 (renderer 소유 문서화) | integration_step1_v0.1.md에 기록됨 |
| D3 (언어 토폴로지) | AE-08로 추적 |
| D4 (어휘 통일) | AE-04로 추적 |
