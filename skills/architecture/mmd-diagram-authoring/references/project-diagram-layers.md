## Project Layer Map (`html-to-editable-pptx`)

This file records the current diagram-layer decomposition used in this repository.
It is a project-local map, not a generic authoring template.

1. **Artifact session lifecycle**: register source, generate candidate, collect evidence, assess, accept or request revision.
2. **Source artifact registration**: draft input, validate, resolve, materialize, manifest, publish revision, create job.
3. **Frozen input manifest lifecycle**: records, blob refs and hashes, provenance, rendering environment metadata, canonicalization, closure validation, digest, revision binding.
4. **Conversion job lifecycle**: render source, extract visual evidence, build IR, map objects, generate PPTX.
5. **Validation evidence lifecycle**: render generated PPTX, compare visual output, validate editability, produce final report.
6. **Revision workflow lifecycle**: create revision request bundle, run authenticated revision, register or publish revised source artifact.

> **Consensus note**: layers 1–3 correspond to accepted diagrams in `docs/diagrams/architecture/`. Layers 4–6 record a design *direction* that is not yet reflected in the project's consensus documents (ULTIMATE_GOAL / GOAL_PROBLEM). Until that consensus lands, treat layers 4–6 as proposals, not as a fixed standard — per the principle that consensus documents rank above diagrams and skills.
