# Fixture Matrix v0.1

This matrix is probe-first and regression-first.

## Purpose

Fixtures are not examples that happen to render well. They are executable
contracts for supported behavior, degraded behavior, known limits, and
unsupported input.

The parser has already hit failures caused by library-internal representation:
WeasyPrint wrappers, implicit table row groups, namespaced SVG tags, style-key
drift, and OOXML declarations that renderers auto-repair. Those failures are
not reliably discovered by adding more HTML examples. Each new fixture family
therefore starts with a WeasyPrint probe and with regression fixtures for bugs
already observed.

## Expected behavior states

| State | Meaning |
|---|---|
| `pass` | Supported path; gates must pass without fallback. |
| `degraded` | Native output exists but has a known quality loss. |
| `known-limit` | A documented boundary; must not crash or silently pass as full support. |
| `unsupported` | Outside v0.1 scope; must fail explicitly or report fallback according to the fixture gates. |

## Gates

Each fixture declares a `primaryGate` because not every validation layer is
equally meaningful for every fixture. Table geometry regressions primarily
depend on Layer D. Pixel similarity can remain acceptable even when OOXML
geometry is wrong because renderers may auto-repair declarations.

The runner records all available layers, but the manifest states which gates
define acceptance for that fixture.

Layer C rendering is opt-in per fixture. The table regression set uses Layer A,
Layer B, and Layer D without invoking LibreOffice because its primary purpose is
semantic and OOXML-geometry regression. Visual fixtures can add
`maxLayerCDiffPct` or `renderedPngs` to enable render/pixel gates.

## Files

| File | Role |
|---|---|
| `fixtures/matrix/manifest.json` | Fixture contract: intent, expected behavior, primary gate, and gates. |
| `scripts/probe_weasy.py` | Observes WeasyPrint box-tree structure before parser changes. |
| `scripts/run_matrix.py` | Runs fixtures sequentially in isolated output directories. |
| `out/matrix/<fixture_id>/probe.json` | Probe evidence for that fixture. |
| `out/matrix/<fixture_id>/run.stdout` | Full conversion/validation stdout. |
| `out/matrix_report.json` | Summary report; generated and ignored. |

## Current table regression fixtures

| Fixture | Locked risk |
|---|---|
| `table_00_regression_tbody_rows.html` | Implicit `TableRowGroupBox` wrappers must not produce zero rows. |
| `table_00_regression_h_declaration.html` | Table `h` must reach PPTX geometry; Layer D catches renderer auto-repair. |
| `table_01_never_single_column.html` | Columns that only appear in colspan cells must receive nonzero widths. |

## Commands

```bash
npm run probe:weasy -- fixtures/matrix/table_00_regression_tbody_rows.html
npm run test:matrix
```

The matrix runner is sequential by design. LibreOffice headless rendering uses
global process state and file outputs; parallel execution is not part of v0.1.
Fixtures that do not declare a render gate run with `RUN_RENDER=0`.
