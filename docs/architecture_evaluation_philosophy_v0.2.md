# Architecture Evaluation Philosophy v0.2

| 항목 | 값 |
|---|---|
| 문서 종류 | 내용 문서 (`_vx.x` 규칙 적용) |
| 출처 | 사용자 합의 — T-line·실행 세션에서 추출, 2026-06-10 사용자 전달 원문 보존 |
| 검토 이력 | v0.1(미커밋 초안)에 대한 외부 검토 3건(major 1: 평가 순서 drift / minor 2: 부록 이식성 과장, 분류 체계 미완결)을 반영해 승계 |
| 지위 | 평가 방법론의 합의 기록. 상호 참조 그래프의 한 노드이며 단일 권위 아님 (MD-1, MD-3 준용) |
| 관계 | `docs/architecture_eval_v0.1.md`의 평가가 따른 암묵 원칙의 명문화. mmd-diagram-authoring skill의 범용 reference는 본 문서의 **원칙 부분집합**(§6 제외)을 사용 — 부록의 예시 어휘는 본 프로젝트 산이므로 출처 주석과 함께만 이식 (§meta 하단 주 참조) |

> **부록 이식성에 대한 정직한 한정**: 부록 A/B의 *패턴*(거시 우선, action label,
> lineage 보존, decision owner 명시 등)은 범용이지만, *예시 어휘*(accept/revise,
> artifact lifecycle, source→conversion→validation, `Reviewer decides`)는 본
> 프로젝트 세션에서 추출된 것이다. 다른 프로젝트로 이식할 때 패턴은 가져가되
> 예시는 그 프로젝트의 어휘로 재도출한다. "§6만 빼면 완전히 portable"이라는
> v0.1의 주장은 과장이었으므로 본 한정으로 교체한다.

## 0. 목적

이 평가는 "아이디어가 좋아 보이는가"를 묻는 문서가 아니다.
이 평가는 현재 저장소에 기록된 시스템이 **자기 목표와 자기 문서들에 대해 구조적으로 정렬되어 있는가**를 점검하는 절차다.

핵심 원칙은 하나다:

> **미시 정렬보다 거시 정렬이 우선이다.**
> 외측의 목적, 책임, 경계, 권위가 잠기기 전에는 내측의 모듈, 필드, 스크립트, 체크 규칙을 최종 정렬로 보지 않는다.

## 1. 평가 순서

아키텍처 평가는 항상 바깥에서 안쪽으로 내려간다. v0.2의 순서는
**성과 → 산출 → 입력 → 절차 → 구조 → 경계 → 구성 → 미시**다.
산출과 입력을 독립 평가축으로 승격한 이유: 이 둘을 의도·구조·미시에 흡수해
두면 평가자가 절차 중심으로 미끄러질 여지가 남기 때문이다 (v0.1의 결함).

1. **성과 계층 (outcomes)** — 사용자가 실제로 얻는 가치가 성립하는가:
   시각·직관적 평가가 가능한가, 그 평가가 수정·재생성으로 이어지는가.
   시스템의 존재 이유(구 '의도 계층')는 이 계층에 흡수된다 — 의도는 성과의
   서술이지 별도 축이 아니다.
2. **산출 계층 (outputs)** — 성과를 떠받치는 산출물이 정의되고 소유되어
   있는가: 평가 표면(PPT), self-assessment(validation report), 증거 번들,
   리비전 산출물. 산출물 정의 없이 절차만 정교한 상태를 이 계층에서 걸러낸다.
3. **입력 계층 (inputs)** — 산출을 만들 입력이 canonical하게 고정되는가:
   무엇이 source of truth인가(HTML), 입력은 어떻게 동결·지문화되는가
   (frozen manifest), 입력의 계보(provenance)는 추적되는가.
4. **절차 계층 (procedures)** — 입력을 산출로 바꾸는 과정: pipeline, loop,
   job, 도구. 절차는 성과·산출·입력이 잠긴 뒤에만 평가할 의미가 있다.
5. **구조 계층** — 전체 lifecycle이 닫혀 있는가 / accept·revise·publish·validate
   loop가 명시적인가 / actor와 decision owner가 드러나는가
6. **경계 계층** — browser vs Node / local vs remote runtime /
   validation renderer ownership / language·subprocess·sidecar 경계
7. **구성 계층** — slot·module·category·layer가 서로 추적 가능한가 /
   reuse decision이 하나의 canonical record로 정리되어 있는가 /
   문서와 manifest가 같은 결정을 말하는가
8. **미시 계층** — schema, manifest field, digest, threshold, score /
   checker coverage / file naming, parity, hygiene / 스크립트의 실제 enforcement 범위

**횡단 게이트 — 합의 검증**: 구 '합의 계층'은 한 단계가 아니라 모든 계층에
횡단 적용된다. 각 계층을 평가할 때 가장 먼저 묻는다 — 이 계층에 대한
live intent와 documented consensus가 일치하는가, 하위 산출물(diagram·task·skill)이
상위 합의를 앞질렀는가.

> **확인 필요 (제안 문구 표기)**: "성과 → 산출 → 입력 → 절차" 순서 자체는
> 합의된 원칙이다. 그러나 위 1~4 계층의 정의 문안, 의도→성과 흡수, 그리고
> '합의 계층의 횡단 게이트화'는 T-line이 제안한 해석이다. 그 합의의 원 문안과
> 다르면 **원 문안이 우선**하며 본 절을 재도출한다 (산문-우선 규칙 준용).

## 2. 최상위 판단 원칙

### P1. 거시 위반은 미시 완성으로 상쇄되지 않는다.
runtime boundary가 비어 있으면 field 정의가 정교해도 미완성이다.
acceptance metric이 없으면 validation report 형식이 좋아도 미완성이다.

### P2. 합의 문서가 다이어그램과 skill보다 상위다.
`ULTIMATE_GOAL`, `GOAL_PROBLEM` 같은 consensus 문서에 없는 핵심 구조가
diagram, task, skill에서 먼저 굳어졌다면 그것은 설계 진전이 아니라 **합의 누락**이다.

### P3. 평가 대상은 "상상된 미래 상태"가 아니라 "기록된 현재 상태"다.
아키텍처 평가는 구현 의도나 구두 합의가 아니라
현재 repo에 남아 있는 문서, diagram, manifest, script를 기준으로 한다.

### P4. loop에는 종료 조건이 있어야 한다.
accept / revise 구조가 있다면 — 누가 판단하는지 / 무엇으로 판단하는지 / threshold를 누가 소유하는지 — 가 정의되어야 한다.

### P5. boundary 없는 module map은 불완전하다.
모듈이 "무엇을 한다"뿐 아니라 — 어디서 실행되는지 / 무엇을 입력으로 받는지 / 어떤 계층에 속하는지 — 가 함께 정의되어야 한다.

### P6. reuse는 단일 canonical record를 가져야 한다.
`reuse_report`, `subtrees.toml`, architecture 문서가 서로 다른 결정을 말하면
그 상태는 "유연함"이 아니라 **판정 불능 상태**다.

### P7. 절차 중심주의를 금지한다. (v0.2 신설 — §1 순서의 원칙화)
성과·산출·입력이 정의되기 전의 절차 정교화는 진전이 아니다.
"파이프라인이 얼마나 정교한가"는 "그 파이프라인이 무엇을 누구에게
내놓는가"가 잠긴 뒤에만 의미 있는 질문이다.

## 3. 무엇을 중대한 문제로 볼 것인가

**Blocker** (v0.2 신설 정의): 평가 또는 후속 결정 자체를 진행 불능으로 만드는
상태 — 평가 대상 산출물의 부재, 합의 문서 간 정면 모순으로 어느 기준선도
선택할 수 없는 상태, 평가에 필요한 접근(저장소·문서) 불가. blocker는
"심각한 major"가 아니라 "평가가 멈추는 지점"이다.

**Major** — 다음은 기본적으로 major 이상으로 본다.

- 상위 의도와 하위 구조의 불일치
- consensus 문서와 diagram/skill의 선후 역전
- validation의 핵심 컴포넌트가 문서 어디에도 owned 되지 않음
- acceptance metric 부재
- runtime boundary 부재
- canonical reuse decision 부재
- slot/category/module/layer crosswalk 부재로 인한 traceability 붕괴
- (v0.2 추가, §1 준용) 성과·산출·입력이 정의되지 않은 채 절차만 정의된 상태

## 4. 무엇을 경미한 문제로 볼 것인가

**Minor** — 다음은 보통 minor로 본다.

- stale file/path naming
- section 이름 불일치
- 용어 순서의 사소한 drift
- checker 설명과 실제 동작 간의 제한된 불일치
- 문서 간 cross-reference 누락이 있으나 구조 해석은 가능한 경우

단, 이런 경미한 문제도 상위 구조 혼란을 누적시키면 major로 승격할 수 있다.

**Observation** (v0.2 신설 정의): 위반이 아닌 기록 — 점검했으나 위반이 아닌
정합 확인(이것도 가치 있는 결과다), 규칙상 허용된 비대칭, 프로세스 잔여물,
도구 범위의 한계 명시. observation은 수정 대상 목록이 아니라 감사 흔적이다.

분류 체계는 평가 문서들이 실제로 쓰는 4단계와 일치한다:
**blocker / major / minor / observation**.

## 5. 평가 산출물의 규칙

평가 문서는 다음만 해야 한다.

- 현재 상태를 재설계하지 않고 평가한다
- finding마다 근거를 남긴다
- finding마다 계층을 암묵적으로라도 식별한다
- "어디가 비어 있는가"를 말한다
- "무엇을 먼저 결정해야 하는가"를 남긴다

평가 문서는 구현안을 길게 쓰지 않는다. 구현안은 후속 결정 문서의 일이다.

## 6. 이 프로젝트에 대한 적용 해석

이 프로젝트에서 아키텍처 평가는 특히 다음 질문을 우선한다.
(v0.2 주: 질문 1~4는 §1의 성과·산출·입력 계층에, 5~6은 경계 계층에,
7은 구성 계층에, 8은 횡단 게이트에 대응한다.)

1. HTML과 PPT 중 무엇이 canonical한가
2. PPT는 output인가, evaluation surface인가
3. revision loop는 부가 기능인가, 시스템 본체인가
4. validation은 실제로 무엇을 보장하는가
5. Playwright/Node 경계는 어디인가
6. PPTX renderer는 누가 소유하는가
7. reuse decision의 canonical source는 무엇인가
8. live intent가 consensus 문서까지 반영되었는가

이 질문들이 잠기기 전에는 manifest, checker, schema, adapter, subtree 배치 같은
미시 결정은 잠정 상태로 본다.

## 7. 한 줄 요약

> **이 프로젝트의 아키텍처 평가는 "안쪽 구현이 정교한가"보다 먼저 "바깥 목적과 구조가 잠겼는가"를 본다.**
> 성과·산출·입력이 잠긴 뒤에 절차를, 거시 정렬이 끝난 뒤에만 미시 정렬을 안정된 결정으로 인정한다.

---

## 부록 A — 다이어그램 원칙 12 (본 프로젝트 세션에서 추출 — 패턴은 범용, 예시 라벨은 출처 프로젝트의 것)

1. 거시 플로우를 먼저 잠근다 — Level 0(accept/revise, artifact lifecycle, source→conversion→validation)를 잠근 뒤 하위로 분해한다.
2. action label이 noun label보다 낫다 — `Register source artifact`, `Collect validation evidence`처럼 행위 중심으로.
3. 인접한 두 노드는 자연어 문장으로 읽혀야 한다 — 부자연스러우면 중간 실행 단계가 빠진 것이다.
4. revision lineage는 생략하면 안 된다 — 피드백 뒤 바로 conversion job으로 가지 말고 `Register/Publish revised source artifact` 계보 경계를 지난다.
5. 상위 다이어그램에는 인스턴스 표기(v1, v2)를 넣지 않는다 — role-based 표현(initial, revised, published revision)을 쓴다.
6. acceptance/revision 분기는 시스템 중심축이다 — 작은 `Accept?`가 아니라 중심 decision node로 둔다.
7. decision owner를 드러낸다 — `Reviewer decides: …`는 문구 수정이 아니라 권위 구조 명시다.
8. evidence와 report는 구분한다 — source analysis / render / validation evidence / final report를 분리한다.
9. 한 장의 다이어그램에는 한 레벨의 책임만 둔다 — layer mixing이 가장 큰 적이다.
10. session은 박스보다 컨텍스트로 다룬다 — action node가 아니라 subgraph/scope/container.
11. checker가 보장하는 것과 사람이 판단해야 하는 것을 분리한다 — hygiene은 기계, macro plot·actor·lineage·번역 품질은 사람.
12. 다이어그램은 미합의 설계를 드러내는 장치다 — 그리기가 아니라 합의 누락 탐지가 본질이다.

> 좋은 mmd는 많은 것을 담는 그림이 아니라, 한 레벨의 책임을 명확히 잠그고 다음 레벨로 내려갈 수 있게 만드는 그림이다.

## 부록 B — Before / After (출처: 본 프로젝트의 mmd 조정 세션)

| Before | After |
|---|---|
| 처음부터 모든 내부 단계를 한 장에 넣음 | 먼저 Level 0 거시 플로우를 잠그고, 그 다음 하위 다이어그램으로 분해 |
| 명사 중심 라벨 (Validation, Revision, Artifact) | 행위 중심 라벨 (Register source artifact, Collect validation evidence) |
| 노드 연결이 "그냥 이어짐" | 인접 노드가 자연어 문장으로 읽히는지 검증 |
| 피드백 후 바로 conversion job으로 점프 | 반드시 revised artifact 등록/발행 단계를 거쳐 lineage 명시 |
| 상위 다이어그램에 v1, v2 표기 | role-based 표현 (initial, revised, published revision) |
| `Accept?` 같은 익명 decision | decision owner 명시 (`Reviewer decides: accept or request revision?`) |
| conversion 중심, revision은 꼬리 기능 | accept / revise loop를 시스템 중심축으로 승격 |
| evidence·diagnostics·report를 한 박스에 혼합 | source analysis / render / validation evidence / final report 분리 |
| lifecycle·registration·manifest를 한 그림에 혼합 | 한 다이어그램 = 한 레벨의 책임 |
| session을 일반 action node로 그림 | session은 container / subgraph / context |
| "검증 완료" = checker 통과 | checker는 hygiene만, 구조 정합성은 사람 검토 |
| diagram을 표현 수단으로만 봄 | diagram을 합의 누락·경계 공백을 드러내는 도구로 사용 |
