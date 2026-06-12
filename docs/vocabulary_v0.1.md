# Vocabulary Crosswalk v0.1

Owner: 이 문서 (D-2-2 final, 2026-06-12 — `docs/integration_step2_consensus_v0.1.md`)
Purpose: 프로젝트 내 5개 병행 어휘를 단일 대조표로 고정한다 (AE-04 해소).

5개 어휘 체계:
① 번호 슬롯 — `GOAL_PROBLEM_v0.1.md`
② named slot — `reuse_report_v0.1.md`
③ manifest category — `third_party/repositories.toml`, `third_party/manifests/*.toml`
④ 모듈 M1–M9 — `docs/architecture_v0.1.md`
⑤ IR semanticType — `src/ir/schema.ts` v1.2.0 (구현체 레이블, 공식 편입)

---

## Crosswalk 테이블 (canonical)

| Slot# | named slot (reuse_report) | manifest category | module (arch_v0.1) | IR semanticType | 구현 상태 |
|---|---|---|---|---|---|
| 1 | extractor | `visual_object_ir_normalizer` | M1 Measured DOM Extractor | — | ✅ `src/extract/weasy_extract.py` |
| 2 | renderQueue | `visual_object_ir_normalizer` | M2 Visual Object IR | — | ✅ `src/ir/schema.ts` (I1–I9) |
| 3 | text run collector | `visual_object_ir_normalizer` | M3 Text Run Collector | `text` | ✅ weasy_extract TextBox 처리 |
| 4 | style mapper | `visual_object_ir_normalizer` | M4 Shape Style Mapper | `shape` | ✅ weasy_extract + ir_to_pptx |
| 5a | table extractor | `fake_table_detector` | M5 Table Detector | `table` | ✅ colspan/rowspan 포함 |
| 5b | fake table detector | `fake_table_detector` | M5 Table Detector | `table` | ⬜ rule-based only (ML 불사용) |
| 6 | image/SVG asset mapper | `visual_object_ir_normalizer` | — | `image` | ✅ MD5 추적 포함 |
| 7 | IR/bbox JSON schema | `semantic_ir_reference` | M2 Visual Object IR | — | ✅ `src/ir/schema.ts` |
| 7c | chart semantic extractor | `chart_semantic_extractor` | M6 Chart Semantic Extractor | `chart` | ✅ tier1(attr) + tier2(svg-marks) |
| 8a | PPTX output | `pptx_output_backend` | M8 PPTX Compiler | — | ✅ PptxGenJS + normalizer resolver |
| 8b | validation runner | `fallback_validation`, `fallback_policy_engine_validation` | M9 Validation Runner | `fallbackRegion` | ✅ Layer A–D |
| — | group mapper | — | — | `group` | ⬜ 미구현 |

---

## 어휘 매핑 규칙

1. 신규 코드 파일/문서 작성 시: `Slot N (named slot) = M? = category` 3개를 동시 기재한다.
2. IR `semanticType`은 이 테이블의 "구현체 레이블"로 취급한다 — 5번째 어휘로 공식 편입.
3. 이 테이블이 canonical이다. `docs/integration_step2_consensus_v0.1.md` §D-2-2의 사본은
   결정 시점 기록이며, 갱신은 이 문서에서만 수행한다.
4. 테이블 변경은 이 문서의 버전 증가(v0.2, …)와 함께 기록한다.

## 참조

- 결정 기록: `docs/integration_step2_consensus_v0.1.md` §D-2-2
- 아키텍처 참조: `docs/architecture_v0.1.md` §4 blockquote → 이 문서
- IR 계약: `src/ir/schema.ts` (irVersion 1.2.0)
