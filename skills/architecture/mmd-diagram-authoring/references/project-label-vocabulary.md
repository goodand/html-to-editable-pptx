## Project Label Vocabulary (`html-to-editable-pptx`)

This file records project-local examples for action labels and the English/Korean glossary used in this repository.
It is reference material, not a portable authoring rule.

### Preferred Examples

- `Register artifact input draft`
- `Validate bundle shape and entrypoint`
- `Resolve local and external references`
- `Materialize and fingerprint resolved inputs`
- `Write frozen input manifest`
- `Publish immutable source artifact revision`
- `Create conversion job for published revision`

### Avoid

- `Create v1` / `Create v2` labels in architecture diagrams. Use parameterized or role-based language instead.
- `Run conversion` when the purpose is clearer as `Generate candidate PPTX`.
- `Gather evidence` when the intended evidence is validation-specific; use `Collect validation evidence`.
- `Record environment assumptions`; use `Record rendering environment metadata`.
- `Seal manifest` when the real outputs are digest computation and revision binding.

### English/Korean Glossary

| English | Korean |
|---|---|
| Artifact revision session | 아티팩트 리비전 세션 |
| Register artifact input draft | 아티팩트 입력 초안 등록 |
| Validate bundle shape and entrypoint | 번들 구조와 진입점 검증 |
| Resolve local and external references | 로컬 및 외부 참조 해석 |
| Materialize and fingerprint resolved inputs | 해석된 입력을 실체화하고 지문 생성 |
| Write frozen input manifest | 고정 입력 매니페스트 작성 |
| Publish immutable source artifact revision | 불변 소스 아티팩트 리비전 발행 |
| Create conversion job for published revision | 발행된 리비전에 대한 변환 작업 생성 |
