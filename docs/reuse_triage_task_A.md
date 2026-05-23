# 작업 요청서 — Decision-first reuse triage (A안)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | reuse-triage-A |
| 요청자 세션 | B안 세션 (Level 2, 기준 c 혼합, P1 6개 심층) |
| 위임 사유 | 본 세션은 P1 6개의 코드 레벨 검증(B안)에 집중. A안은 다른 책임 영역 |
| 산출물 위치 | `docs/reuse_triage.md` |
| 산출물 형식 | 결정 테이블 (Markdown) |
| 예상 분량 | 1~2일, 전체 문서 5~10페이지 |
| 본 세션 산출물 | `docs/reuse_report_v0.1.md` (B안, 별도) — 본 세션의 책임 |

## 2. 작업의 위치 (where this fits)

`html-to-editable-pptx` 프로젝트는 bootstrap 단계이며, `docs/TASK.md`가 지시한 첫 산출물은 세 개입니다:

```text
docs/reuse_report_v0.1.md
docs/architecture.md
docs/deletion_candidates.md
```

`docs/reuse_report_v0.1.md`는 두 가지 접근이 가능합니다:

- **B안 (Evidence-first, 좁고 깊게)**: P1 후보 6개에만 집중, 코드 인용과 함께 재사용 가능성 검증
- **A안 (Decision-first, 얕고 넓게)**: 27개 저장소 전부에 대해 *채택 / 참고 / 폐기* 분류

본 요청서는 A안을 다른 Agent에게 위임하는 것이며, 산출물은 충돌을 피하기 위해 `docs/reuse_triage.md`라는 별도 파일로 작성합니다.

## 3. 입력 자료

작업을 시작하기 전에 반드시 읽어야 할 파일:

```text
docs/GOAL_PROBLEM_v0.1.md
README.md
third_party/repositories.toml
third_party/manifests/*.toml
third_party/clone_results.json
third_party/repos/<repo_id>/
```

`third_party/clone_results.json`은 27개 저장소가 모두 clone되었음을 확인하는 기준 자료입니다. 모든 항목이 `cloned` 또는 `already_cloned` 상태여야 작업을 시작할 수 있습니다.

## 4. 작업 정의 — 무엇을 한다

각 저장소에 대해 **README와 디렉터리 구조만으로** 다음 4개 결정을 내립니다:

| 결정 항목 | 가능한 값 | 정의 |
|---|---|---|
| **decision** | adopt / reference / discard / defer | 그 슬롯에서 이 저장소를 어떻게 다룰지 |
| **slot_fit** | strong / partial / weak / none | `GOAL_PROBLEM_v0.1.md`의 슬롯 요구사항과 일치도 |
| **integration_cost** | low / medium / high / unknown | 통합 비용 추정 (언어/라이선스/의존성 기준) |
| **risk** | low / medium / high | 채택 시 단일 의존성 리스크 |

### 4.1. 결정 값의 정의

- **adopt**: 이 슬롯의 primary candidate로 채택. B안 세션이 코드 레벨까지 검증해야 함
- **reference**: 코드를 직접 import하지 않지만, 설계/스키마/패턴을 참고함
- **discard**: 슬롯과 맞지 않거나, 더 나은 대안에 의해 대체됨. `docs/deletion_candidates.md` 후보로 등재
- **defer**: 현재 bootstrap 단계에서 결정하지 않음. 이유와 결정 시점 명시

### 4.2. 결정의 근거 (evidence)

각 결정은 다음 항목으로 뒷받침되어야 합니다:

- 저장소의 README 인용 (1~3 문장, 출처 명시: `repo/README.md:L<line>`)
- 디렉터리 구조에서 관찰된 사실
- 라이선스 (LICENSE 파일에서 확인)
- 주 언어 (저장소 최상위 파일 확장자 기준)
- 마지막 commit 날짜 (선택사항)

**코드를 읽지 않습니다.** 코드 레벨 분석은 B안(`docs/reuse_report_v0.1.md`)의 책임입니다. README + 디렉터리 구조 + 라이선스 + 언어만으로 결정하지 못하면 `defer`로 분류합니다.

## 5. 산출물 형식

`docs/reuse_triage.md`는 다음 구조여야 합니다:

```markdown
# Reuse Triage Report (A안)

## Summary

- 총 저장소: 27
- adopt: N
- reference: N
- discard: N
- defer: N

## Decision table

| repo_id | slot (category) | priority | decision | slot_fit | integration_cost | risk | language | license | evidence_brief |
|---|---|---:|---|---|---|---|---|---|---|
| dom_to_pptx | visual_object_ir_normalizer | P1 | ... | ... | ... | ... | ... | ... | ... |

## Per-repo evidence

### dom_to_pptx

- **Decision**: ...
- **Slot fit**: ...
- **Integration cost**: ...
- **Risk**: ...
- **License**: ...
- **Evidence**:
  - README.md L12: "..."
  - 디렉터리: src/ 부재, examples/만 존재
- **Open questions**:
  - ...
```

## 6. 비목표 (non-goals)

GOAL_PROBLEM_v0.1.md의 non-goal 카테고리 형식을 따릅니다.

### Case: Type

- **코드를 읽지 않는다.** 함수 시그니처 확인이나 import 추적은 B안의 책임이다.
- **실행하지 않는다.** Minimal example 실행, 의존성 설치, smoke test는 다른 세션의 책임이다.
- **벤치마크 측정을 하지 않는다.** "이 라이브러리는 빠른가?" 류의 질문은 답하지 않는다.
- **architecture.md 또는 IR 스키마를 정의하지 않는다.** Triage 결정만 한다.

### Case: State

- **adopt 결정은 최종이 아니다.** B안 세션이 코드 검증 후 뒤집을 수 있다. Triage는 *후보 선정*이지 *확정*이 아니다.
- **defer는 실패가 아니다.** 정보 부족을 솔직히 표시하는 것이 잘못된 채택보다 낫다.

### Case: Performance: Over

- **각 저장소당 30분 이상 쓰지 않는다.** 27 × 30분 = 13.5시간이 상한. 그 이상이면 작업 정의가 잘못된 것이므로 요청자에게 알린다.
- **GitHub URL을 통한 외부 자료 검색을 하지 않는다.** clone된 파일만 본다.

### Case: Performance: Under

- **README가 부실하거나 영어가 아니어도 defer로 분류 가능하다.** 무리해서 결정하지 않는다.

## 7. 검증 규칙

산출물이 다음을 만족해야 완료로 간주합니다:

1. **27개 저장소 전부**가 결정 테이블에 포함되어 있다 (누락 없음).
2. **8개 슬롯 각각에 최소 1개의 `adopt`**가 있다. 또는 그 슬롯이 비어있는 이유가 명시된다.
3. **모든 P1 저장소의 결정이 명시되어 있다**. P1은 defer 금지.
4. **각 결정에 evidence_brief가 첨부되어 있다**. 빈 evidence는 누락으로 간주.
5. **라이선스 호환성 충돌이 있다면 별도 섹션에 모아서 보고한다**.

## 8. 본 세션(B안)과의 인터페이스

A안의 결정이 B안에 미치는 영향:

- B안은 **adopt로 분류된 P1 저장소만 심층 분석**합니다.
- A안이 P1 저장소를 `discard`로 분류하면 B안은 해당 슬롯의 다음 priority 후보로 이동합니다.
- A안의 `Open questions` 섹션은 B안의 분석 항목으로 직접 이전됩니다.

만약 두 세션의 결론이 충돌하면 **B안(코드 검증 기반)이 우선**합니다. A안은 README 기반의 1차 분류입니다.

## 9. 시작 지시

1. `third_party/clone_results.json`을 확인하여 27개가 모두 cloned 상태인지 검증
2. `docs/GOAL_PROBLEM_v0.1.md`의 8개 슬롯 정의와 non-goal 섹션을 정독
3. P1 저장소 6개부터 시작
4. P2 → P3 순서로 진행
5. 마지막에 Summary 섹션과 8개 슬롯 커버리지 검증
6. `docs/reuse_triage.md`로 저장

## 요청자 노트

이 문서는 B안 세션과 병렬로 실행 가능합니다. 두 산출물(`reuse_report_v0.1.md`, `reuse_triage.md`)이 모두 작성된 뒤, 다음 단계 작업(`architecture.md`, `deletion_candidates.md`)에서 두 문서를 함께 입력으로 사용합니다.
