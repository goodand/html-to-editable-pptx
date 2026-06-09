# Subtree Adoption Handoff v0.2

## Scope

This handoff is for the next Agent continuing the subtree-adoption work in
`goodand/html-to-editable-pptx`.

The current task added the first subtree-level inventory and manifest:

- `docs/subtree_module_inventory_v0.2.md`
- `third_party/subtrees.toml`
- `docs/subtree_adoption_handoff_v0.2.md`

This handoff does not mean the actual upstream code has already been imported.
It records the decisions needed before running `git subtree add`.

## Critical Decision

`dom_to_pptx` is no longer a reference-only/defer item.

Use this exact decision state:

```toml
id = "dom_to_pptx"
decision = "adopt_subtree"
import_mode = "whole_repo"
source_path = "."
subtree_prefix = "third_party/subtrees/dom-to-pptx"
```

Do not change `dom_to_pptx` to `split_subdir = "src"` without a new explicit
review. Upstream's package, build, test, CLI, dist, and skill assets are tied to
the repo root.

## Why `dom_to_pptx` Is Whole Repo

The upstream repo has two responsibilities in one published package boundary:

```text
runtime core + agent skill bundle
```

Runtime core:

- `src/index.js`
- `src/utils.js`
- `src/image-processor.js`
- `src/font-embedder.js`
- `src/pptx-normalizer.js`
- root build/test/package metadata

Agent skill bundle:

- `bin/cli.js`
- `skills/dom-to-pptx-skill/*`
- skill reference/template/validation files

Important caveat: `bin/cli.js` is a skill installer, not the HTML-to-PPTX
conversion CLI. The subtree should keep it because upstream publishes it, but
project architecture should not treat it as part of the runtime conversion
path.

## Other Current Classifications

Validation candidates:

- `pixelmatch`: `adopt_subtree`, `whole_repo`
- `looks_same`: `adopt_subtree`, `whole_repo`
- `odiff_bin`: `adopt_subtree`, `split_subdir`, source path
  `npm_packages/odiff-bin`

Package dependency candidates:

- `pptxgenjs`: use package dependency first
- `backstopjs`: use package/external CLI first

Reference-only / delayed candidates:

- `docling`: reference-only or package experiment; no clean split subtree yet
- `opendataloader_pdf`: whole repo remains reference-only
- `opendataloader_pdf_core`: promotable split-subdir candidate, but still needs
  direct Java module build/test verification
- `table_transformer`: reference-only unless a separate model execution unit is
  created
- `chartdetective`: reference-only until reusable chart logic is isolated

## Suggested Next Agent Steps

1. Read `third_party/subtrees.toml`.
2. Confirm `dom_to_pptx` still has `decision = "adopt_subtree"` and
   `import_mode = "whole_repo"`.
3. If the user asks to execute the actual subtree import, run:

```bash
git subtree add \
  --prefix=third_party/subtrees/dom-to-pptx \
  https://github.com/atharva9167j/dom-to-pptx.git \
  master \
  --squash
```

4. After import, run a minimal verification pass:

```bash
git status --short
test -d third_party/subtrees/dom-to-pptx
test -f third_party/subtrees/dom-to-pptx/package.json
test -f third_party/subtrees/dom-to-pptx/bin/cli.js
test -d third_party/subtrees/dom-to-pptx/skills/dom-to-pptx-skill
```

5. Commit the subtree import separately from documentation updates.

## Do Not Do Yet

- Do not import `docling` as a subtree without a new explicit boundary review.
- Do not import the whole `opendataloader-pdf` repo as a subtree just because
  `opendataloader_pdf_core` is promotable.
- Do not replace `pptxgenjs` package dependency with a subtree unless the
  project needs to patch upstream internals.
- Do not treat `dom-to-pptx`'s agent skill bundle as runtime conversion code.

## Current Stopping Point

The repository now has a subtree decision layer, but no actual subtree source
has been vendored yet in this step. The next meaningful work is either:

1. execute `dom_to_pptx` subtree import, or
2. finish the Java-module verification for `opendataloader_pdf_core`.
