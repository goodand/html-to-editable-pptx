# Integration Step 2 — Consensus Record

Date: 2026-06-12
Scope: OQ-3 (AE-03 reuse 정식화), OQ-4 (AE-04 crosswalk), AE-08 (런타임 토폴로지)
Method: 사용자와 1결정/1턴 인터뷰

---

## Decision D-2-1: OQ-3 — dom_to_pptx reuse 방식 (AE-03 해소)

**결정 (최종, 2026-06-12):** runtime import 기본 + transplant 자동 폴백.

```
기본 경로  : import("dom-to-pptx")            ← npm optionalDependency
폴백 경로  : src/output/normalize-zip.js      ← 이식본 (MIT attribution 유지)
폴백 트리거: ① 패키지 부재  ② normalizePptxZip export 부재
            ③ 로드 오류    ④ pptxgenjs 버전 충돌이 우리 해석 트리에 실체화
```

**결정 이력:**

| 차수 | 내용 | 비고 |
|---|---|---|
| v1 | 호환 해석 — subtree=이식 소스, runtime import 금지 | 인터뷰 1차 답변 |
| v2 (최종) | runtime import 기본 + 폴백 | 사용자 지시로 동일자 개정. 사유: "현재 환경이 나의 local 환경이 아니기 때문" — npm 설치가 로컬 재현에 단순 |
| 절차 기록 | v1 합의 직후 동의 없이 실행 1회 발생 → 사용자 교정 → 이후 명시 동의 후 실행으로 절차 복구 | 워크플로 규칙 재확인 |

**reuse_report_v0.1 §6.1 supersede 기록:**

superseded 조항: validation #5 "package.json에 dom-to-pptx 없음" 및
"naive runtime dependency 금지" 경고.

수용 근거:
1. `optionalDependencies` 한정 — 일반 dependencies가 아니며, 설치 실패가 빌드를 깨지 않음
2. 소비 표면은 순수 함수 `normalizePptxZip` 1개 — `exportToPptx`(브라우저 DOM 필요)는 호출 경로 없음
3. html2canvas / pptxgenjs@3은 번들 로드만 되고 비호출(contained); 우리 트리의
   pptxgenjs는 4.0.1로 해석됨을 실측 확인 (2026-06-12, /tmp/rtest)
4. 폴백이 transplant 경로를 보존 — reuse_report의 원래 의도(브라우저 의존 차단)는
   폴백 트리거 ④와 이식본 유지로 계승

**실증 결과 (2026-06-12, npm v1.1.10):**

| 검증 | 결과 |
|---|---|
| root `import("dom-to-pptx")` | Node 로드 성공 |
| `normalizePptxZip` export | **부재** — root export는 `exportToPptx`뿐 |
| deep import (`/src/pptx-normalizer.js`) | `ERR_PACKAGE_PATH_NOT_EXPORTED` 차단 |
| 우리 pptxgenjs 해석 | 4.0.1 격리 유지 |

따라서 **현행 npm 버전에서 resolver는 항상 폴백으로 동작**하며 사유가 mapreport에
자동 기록된다(`normalizer`, `normalizerNote` 필드). 업스트림이 export를 추가하는
시점에 코드 무변경으로 runtime-import로 전환된다.

**구현 (3파일):**
- `package.json` — `optionalDependencies: { "dom-to-pptx": "^1.1.10" }`
- `src/map/ir_to_pptx.mjs` — resolver (`resolveNormalizer()`, 트리거 4종)
- `src/output/normalize-zip.js` — 폴백 역할 명시 (attribution 유지)

**이식 함수 현황 (원 reuse_report 6종):**

| 함수 | 상태 |
|---|---|
| pptx-normalizer.js → normalize-zip.js | ✅ 이식 완료 (폴백 역할) |
| collectTextParts / extractTableData / prepareRenderItem / getTextStyle / getBorderInfo+getVisibleShadow+generateGradientSVG | ⏸ 보류 — WeasyPrint 추출 경로가 동등 기능 수행, 현 아키텍처에서 불필요 (S3-7) |

---

## Decision D-2-2: OQ-4 — 어휘 통일 crosswalk (AE-04 해소)

**결정 (최종, 2026-06-12):** crosswalk 소유 문서 = `docs/vocabulary_v0.1.md` (B안 — 어휘 전담 신규 문서). 아래 테이블은 결정 시점 기록이며 canonical 버전은 vocabulary_v0.1.md.

**Crosswalk 테이블:**

| Slot# | named slot (reuse_report) | manifest category | module (arch_v0.1) | IR semanticType (h2p v1.2.0) | 구현 상태 |
|---|---|---|---|---|---|
| 1 | extractor | `visual_object_ir_normalizer` | M1 Measured DOM Extractor | — | ✅ `src/extract/weasy_extract.py` |
| 2 | renderQueue | `visual_object_ir_normalizer` | M2 Visual Object IR | — | ✅ `src/ir/schema.ts` (I1–I9) |
| 3 | text run collector | `visual_object_ir_normalizer` | M3 Text Run Collector | `text` | ✅ weasy_extract TextBox 처리 |
| 4 | style mapper | `visual_object_ir_normalizer` | M4 Shape Style Mapper | `shape` | ✅ weasy_extract + ir_to_pptx |
| 5a | table extractor | `fake_table_detector` | M5 Table Detector | `table` | ✅ colspan/rowspan 포함 |
| 5b | fake table detector | `fake_table_detector` | M5 Table Detector | `table` | ⬜ rule-based only (ML 불사용) |
| 6 | image/SVG asset mapper | `visual_object_ir_normalizer` | — | `image` | ✅ MD5 추적 포함 |
| 7 | IR/bbox JSON schema | `semantic_ir_reference` | M2 Visual Object IR | — | ✅ `src/ir/schema.ts` |
| 7c | chart semantic extractor | `chart_semantic_extractor` | M6 Chart Semantic Extractor | `chart` | ✅ tier1(attr)+tier2(svg-marks) |
| 8a | PPTX output | `pptx_output_backend` | M8 PPTX Compiler | — | ✅ PptxGenJS |
| 8b | validation runner | `fallback_validation` `fallback_policy_engine_validation` | M9 Validation Runner | `fallbackRegion` | ✅ Layer A-D |
| — | group mapper | — | — | `group` | ⬜ 미구현 |

**어휘 매핑 규칙 (이후 문서 작성 시 준수):**
- 신규 코드 파일 설명 시: `Slot N (named slot) = M? = category` 3개 동시 기재
- IR semanticType은 이 테이블의 "구현체 레이블"로 취급 (5번째 어휘, 공식 편입)
- crosswalk 테이블 소유 문서: `docs/vocabulary_v0.1.md` (확정, D-2-2 final)

---

## Decision D-2-3: AE-08 — 런타임 언어 토폴로지 공식화

**결정:** Python + Node 혼합 공식화 — architecture 문서에 명시.

**공식 토폴로지:**

```
[입력 HTML]
      │
      ▼ Python (WeasyPrint)
src/extract/weasy_extract.py   → IR JSON
      │
      ▼ Node.js (PptxGenJS)
src/map/ir_to_pptx.mjs         → .pptx
      │
      ├── Python
      │   src/validate/validate_ab.py  (Layer A: bag-of-lines, Layer B: MD5)
      │   src/validate/layout_d.py     (Layer D: IoU)
      │
      └── Node.js
          src/validate/pixel_c.mjs     (Layer C: pixelmatch)
```

**경계 규칙:**
- Python: 레이아웃 엔진(WeasyPrint), 텍스트 기반 검증(A/B/D), 픽셀 외 분석
- Node.js: PPTX 직렬화(PptxGenJS), 픽셀 diff(pixelmatch), normalizer(jszip)
- 두 런타임은 **파일 시스템(JSON/pptx)으로만 통신** — 직접 호출 없음
- run.sh가 단일 진입점으로 두 런타임을 조율

**reuse_report 비공식 결정("Node-only") 처리:**
- 해당 결정은 `table_transformer` non-goal 섹션 안에 기록된 scope-limited 결정
- bootstrap 단계에서 Python 사용이 실증됨 → 공식 토폴로지로 승격
- architecture_v0.1.md에 Language Topology 섹션 추가로 기록

---

## 다음 단계 (Step 3)

| 작업 | 근거 | 내용 |
|---|---|---|
| S3-1 | D-2-1 | ✅ 완료 — `normalize-zip.js` 이식(폴백 역할) + attribution |
| S3-2 | D-2-1 | ✅ 완료 — `ir_to_pptx.mjs` resolver가 runtime-import ↔ 폴백 자동 전환 |
| S3-3 | D-2-2 | ✅ 완료 — `docs/vocabulary_v0.1.md` 신규 (crosswalk canonical) |
| S3-4 | D-2-3 | ✅ 완료 — `docs/architecture_v0.1.md` §9 Language Topology |
| S3-5 | D-2-1 | reuse_report_v0.1 §6.1 validation #5에 supersede 각주 추가 (다음 패킷) |
| S3-6 | — | pixelmatch / looks-same / odiff subtree 실행 (subtrees.toml 결정 보유) |
| S3-7 | D-2-1 | 잔여 5개 함수 이식 보류 — WeasyPrint 경로에서 불필요 판정 기록 |
