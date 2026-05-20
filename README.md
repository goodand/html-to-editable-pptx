# html-to-editable-pptx

Editability-first HTML to PPTX parser project.

Goal: convert rendered HTML into editable PowerPoint objects using browser layout extraction, a Visual Object IR, and PPTX object mapping.

## Priority

- Editable PPT objects first
- Reuse existing modules before writing new code
- Validate generated PPTX output by rendering
- Keep fallback decisions explicit

## Target objects

Editable where possible:

- Text and rich text runs
- Shapes
- Tables
- Charts

Asset-backed where acceptable:

- Images
- SVG/icon assets
- Video thumbnails

## Planned pipeline

1. Render HTML with Playwright
2. Extract DOM geometry and computed styles
3. Build measured visual nodes
4. Normalize into Visual Object IR
5. Map IR to PPTX objects
6. Render and validate output

## Important files

- third_party/html_to_pptx_parser_repos.toml
- scripts/clone_repos_from_toml.py
- docs/CODEX_WEB_TASK.md
