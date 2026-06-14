---
name: probe-first-regression-matrix
description: Build converter/parser fixture matrices by probing third-party trees before handlers, adding regression fixtures before feature fixtures, declaring expected behavior and primary gates, isolating outputs, and making renderer checks opt-in.
version: 0.1.0
metadata:
  hermes:
    tags: [fixtures, regression, probes, parsers, converters, validation, matrix]
    category: software-development
    related_skills: [cross-representation-verification]
---

# Probe-First Regression Matrix

A protocol for growing fixture coverage in parsers, converters, exporters, and
layout pipelines. It starts after a representation problem has been identified
by [`cross-representation-verification`](../cross-representation-verification/SKILL.md)
and turns that knowledge into repeatable fixtures, gates, and reports.

The core rule:

> Probe before handler. Regression before feature. Fixture gates before claims.

## When to Use

- A parser/converter needs more fixtures and the processing model is
  library-owned, undocumented, version-coupled, or renderer-coupled.
- A bug came from an internal tree shape, wrapper, implicit node, namespace,
  style-key drift, or output declaration that a renderer repaired.
- New fixture categories need a manifest, expected behavior states, primary
  gates, and isolated outputs.
- A fixture should prove a known regression does not return before new feature
  breadth is added.

Do not use this for one-off examples whose output is inspected manually and not
kept as an executable contract.

## Modes

- **Probe-before-handler** — create a minimal input and record the library's
  real tree or model before writing or changing extraction logic.
- **Regression fixture** — encode a previously observed bug as the first fixture
  in a category.
- **Feature fixture** — explore new supported breadth after regressions are
  covered.
- **Renderer-gated fixture** — opt into render or pixel checks only when that
  layer is meaningful for the fixture. See `references/external-renderer-guards.md`.

## Quick Reference

| Need | Action |
|---|---|
| Start a fixture family | Probe a minimal input and save the probe output |
| Lock a past bug | Add a regression fixture before feature fixtures |
| Avoid overclaiming | Set `expectedBehavior` to `pass`, `degraded`, `known-limit`, or `unsupported` |
| Identify the decisive check | Set `primaryGate` for the fixture |
| Avoid output collisions | Run each fixture under an isolated output directory |
| Avoid renderer flakiness | Make renderer/pixel gates opt-in per fixture |
| Prevent silent skips | Fail when a declared gate cannot produce evidence |

## Manifest Contract

Each fixture entry should carry the following fields or equivalents:

```json
{
  "id": "category_00_regression_name",
  "category": "table",
  "input": "fixtures/matrix/category_00_regression_name.html",
  "intent": "The specific risk this fixture locks.",
  "expectedBehavior": "pass",
  "primaryGate": "layerD",
  "probeRequired": true,
  "gates": {
    "layerA": true,
    "minLayerDWorstIoU": 0.9,
    "maxFallback": 0,
    "mustReportFallback": false,
    "expectedExitCode": 0
  }
}
```

Expected behavior states:

| State | Meaning |
|---|---|
| `pass` | Supported path; declared gates must pass without fallback |
| `degraded` | Output is native or usable but has a documented quality loss |
| `known-limit` | Boundary is documented; it must not masquerade as full support |
| `unsupported` | Outside scope; must fail explicitly or report fallback by contract |

`primaryGate` names the layer that decides the fixture. A fixture may collect
other evidence, but not all layers are equally meaningful for every fixture.
Use `expectedExitCode` when an `unsupported` or `known-limit` fixture should fail
explicitly instead of producing a fallback. Use `mustReportFallback` when the
expected result is a reported fallback rather than a crash.

## Procedure

1. **Name the fixture family by risk, not by visual content.** A fixture family
   should answer "what class of bug are we locking?" rather than "what example
   looks nice?"

2. **Probe first.** Create the smallest input that exercises the library surface
   and run a probe that records real node classes, tags, wrappers, positions,
   span metadata, or equivalent structure. Do not write a handler from memory.

3. **Record the probe as evidence.** Store probe output in the fixture's isolated
   output directory or attach it to the report. A future regression should be
   able to compare implementation assumptions against observed structure. If
   probe output lives under ignored generated directories, the matrix runner
   must regenerate it and report the path; commit probe output only when the
   project treats it as a durable baseline.

4. **Add regression fixtures before breadth fixtures.** The first fixtures in a
   category should reproduce bugs already observed. Feature exploration comes
   after known regressions are executable.

5. **Choose an honest expected behavior.** Use `degraded`, `known-limit`, or
   `unsupported` when the output is partial or outside scope. Do not force every
   useful fixture into `pass`.

6. **Set the primary gate.** If a bug lives in output declarations, a pixel gate
   may be noise and the geometry/declaration gate should be primary. If the bug
   is visible drift, render/pixel may be primary.

7. **Isolate outputs per fixture.** Use an output directory keyed by fixture id.
   Do not let parallel or repeated runs collide on shared filenames.

8. **Make renderer gates opt-in.** External renderers often carry global process
   state, file locks, display assumptions, or auto-repair behavior. Enable them
   only when the fixture declares a render gate. A full shipping suite may still
   require representative render gates even when individual matrix fixtures keep
   render checks disabled.

9. **Fail on missing declared evidence.** If a fixture declares rendered PNGs,
   reports, or probe output, absence is a failure. Silent "no files matched"
   skips create false-green runs.

10. **Write a matrix report.** Each fixture result should include fixture id,
    expected behavior, primary gate, check results, output directory, and final
    status. Status should distinguish expected states from `unexpected_fail` and
    renderer/environment failures such as `environment_blocked`.

## Pitfalls

- **Fixture-only confidence.** More examples do not expose library internals if
  none of them record the tree/model representation.
- **Feature-first matrix growth.** New breadth hides old regressions when the
  known bug was never made executable.
- **One gate for every fixture.** A uniform gate set overstates weak layers and
  understates decisive layers.
- **Renderer by default.** Headless renderers can fail for environmental reasons
  unrelated to the fixture's contract.
- **Shared output directory.** Repeated fixtures overwrite each other's reports
  and make evidence untrustworthy.
- **Unsupported as crash.** Unsupported input still needs an explicit failure or
  fallback contract; it should not crash by accident.

## Verification

The matrix is correctly designed when:

- every new fixture family starts with probe evidence;
- each category begins with regression fixtures for known bugs;
- every fixture declares `expectedBehavior` and `primaryGate`;
- output directories are isolated by fixture id;
- renderer/pixel gates are enabled only by fixture declaration;
- a missing declared artifact fails the fixture;
- the matrix report distinguishes `pass`, `degraded`, `known-limit`,
  `unsupported`, `unexpected_fail`, and `environment_blocked`;
- unsupported fixtures declare either an expected exit code or a fallback report
  gate, so unsupported does not mean accidental crash.
