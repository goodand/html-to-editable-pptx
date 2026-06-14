# External Renderer Guards

Use this reference when a fixture matrix needs a viewer, office suite, browser,
PDF renderer, image rasterizer, or any other external renderer to produce visual
evidence.

## Guard Rules

1. **Renderer gates are opt-in.** Do not run renderer/pixel checks for every
   fixture by default. Enable them only when the fixture declares a render gate.

2. **Run renderers sequentially unless proven safe.** Many renderers use global
   process state, profile directories, app locks, display services, or shared
   output filenames. Parallel runs can produce crashes or false failures.

3. **Isolate output directories.** Each fixture should render into an output
   directory keyed by fixture id. Shared output names make retries and parallel
   experiments unreliable.

4. **Fail on absent render artifacts.** If a fixture declares rendered PNGs,
   PDFs, screenshots, or diff images, a missing file is a failure. Do not treat
   an empty glob as a skipped success.

5. **Separate visual gates from declaration gates.** Renderers may auto-repair
   invalid declarations. Passing pixels do not prove the output declaration is
   correct when declaration-level evidence is available.

6. **Record renderer environment.** Include renderer name/version when it affects
   reproducibility or thresholds. If the environment is unstable, keep the render
   gate looser or out of the primary gate.

## Report Fields

Renderer-backed fixture reports should include:

```text
renderer: <name/version or unknown>
render_gate: enabled | disabled
output_dir: <fixture-specific directory>
expected_artifacts: <list>
missing_artifacts: <list>
visual_metric: <value or n/a>
declaration_metric: <value or n/a>
primary_gate: <gate name>
```

## Stop Conditions

Stop and classify the run as environment-blocked or unexpected failure when:

- the renderer crashes before producing declared artifacts;
- the renderer writes to a different output path than expected;
- a declared render artifact is missing;
- a renderer-specific failure would be mistaken for parser correctness;
- running the renderer requires changing the fixture contract.
