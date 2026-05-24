# Session Summary — T-line v0.1 → 새 세션 인계 문서

## Meta

| 항목 | 값 |
|---|---|
| 문서 종류 | Handoff (세션 인계 문서) |
| 생성 시점 | T-line 세션 v0.1 종료 시점 |
| 수명 | **인계 완료 후 삭제 대상** (MD-14: 인계 문서 일회성 정책) |
| 대상 독자 | 새 T-line 세션 (또는 인계받을 다른 Agent) |
| 보조 산출물 | `skills/agent-collaboration/` (T-line 방법론 6-Skill 카테고리, GitHub commit `8fc1605`) |

이 문서는 새 세션이 *T-line v0.1이 멈춘 지점에서 정확히 이어 진행*할 수 있도록 만든 인계 문서입니다. 산출물 B (Skill)와 함께 읽어야 *방법론*과 *현재 상태*가 모두 이해됩니다.

---

## 1. 프로젝트 개요

### 1.1. Repository

```text
goodand/html-to-editable-pptx
branch: main
```

### 1.2. 핵심 미션

LLM이 HTML로 생성한 artifact를 사용자가 PPT 형식(익숙한 시각 형식)으로 직접 조작하면서 시각·직관적으로 평가하게 하는 것.

자세한 정의: `docs/ULTIMATE_GOAL_v0.1.md` (작업 진행 후 새 이름)

### 1.3. 현재 단계

bootstrap. 합의 보존소(ULTIMATE_GOAL_v0.1.md)와 슬롯 구조(GOAL_PROBLEM_v0.1.md), 재사용 분석(reuse_report_v0.1.md), 외부 평가 보고 완료.

코드 자체는 *아직 작성 전*. 첫 코드 작성은 새 세션의 후속 작업.

---

## 2. 합의된 사실 — 빠른 참조

### 2.1. Ultimate Goal (UG-1 ~ UG-5)

| ID | 내용 |
|---|---|
| UG-1 | (3) 시각·직관적 평가가 시스템의 1차 책임 |
| UG-2 | (1) 수정과 (2) 텍스트 표현은 (3)의 후속이며 대체 채널 존재 |
| UG-3 | LLM은 HTML 생성에 친화적, 사용자는 PPT 형식에 익숙함 |
| UG-4 | PPTX 자체는 목적이 아닌 evaluation 매체 (단순한 디렉토리 구조의 MVP) |
| UG-5 | "reconstruction is expensive"는 Agent의 working rule이며 ultimate goal 아님 |

### 2.2. Meta-Decisions (MD-1 ~ MD-14)

| ID | 내용 |
|---|---|
| MD-1 | 상호 참조 그래프, 단일 최상위 권위 없음 |
| MD-2 | 우선순위는 인터뷰가 결정, 문서가 결정하지 않음 |
| MD-3 | ULTIMATE_GOAL은 합의 보존소, 권위 문서 아님 |
| MD-4 | ULTIMATE_GOAL은 사용자 동의 없이 수정 금지 (다른 문서는 자유) |
| MD-5 | 독자별 추상도 분리: README(대중·구체) / GOAL_PROBLEM(Agent·중간) / ULTIMATE_GOAL(Agent·추상) |
| MD-6 | Claude 산출물은 .md, 실제 구현은 codebase_analysis |
| MD-7 | ULTIMATE_GOAL은 두 독자: 사용자(복기) / Agent(인터뷰 질문 생성) |
| MD-8 | 사용자 독자를 위해 *읽기 쉬움*이 추상도보다 우선 |
| MD-9 | Agent 독자를 위해 *경계 명확성*이 우선 |
| MD-10 | YAML 인덱스는 *Agent를 위한 derivative*. 산문이 권위 |
| MD-11 | YAML과 산문 충돌 시 산문 우선. YAML은 자동 갱신 대상 |
| MD-12 | YAML은 점진적 도입 |
| MD-13 | 지시서(`*_task.md`)는 일회성. 작업 완료 후 삭제 |
| MD-14 | 인계 문서(`session_summary_*.md`, `handoff_*.md`)는 인계 완료 후 삭제 |

### 2.3. 표현 규칙 (EX-1 ~ EX-4)

| ID | 내용 |
|---|---|
| EX-1 | `touchable` 어휘는 `operate*` 계열로 치환 (비유적 인용은 보존) |
| EX-2 | 권위 단정형 회피, 관계형 표현 사용 |
| EX-3 | 다른 문서 *구체 이름 열거* 회피, 추상 표현 사용 |
| EX-4 | Skill 간 연결은 frontmatter `metadata.hermes.related_skills`에 *양방향* 명시. 본문에서 다른 Skill 언급은 *Markdown 상대 경로 링크*. `## Related Skills` 별도 섹션은 추가하지 않음 |

### 2.4. 파일명 규칙

- **내용 문서**: `_vx.x.md` suffix 사용 (예: `ULTIMATE_GOAL_v0.1.md`)
- **지시서**: `_task.md` suffix, versioning은 `_vN_task.md` (예: `git_g1_rename_v4_task.md`)
- **도구 문서**: `README.md` 등 변경 없음
- **소급 적용 범위 (β)**: 모든 내용 문서에 적용. 지시서와 도구 문서는 제외
- **린터 강제**: 향후 도입 예정 (D3, 미작성)

---

## 3. 현재 진행 중 작업

### 3.1. 외부 평가 후속 작업 (G1~G4)

codebase_analysis가 ULTIMATE_GOAL_v0.1.md를 외부 평가하여 5개 발견 보고:

- **I-01**: TASK.md의 `architecture.md` 경로가 실제 파일(`architecture_v0.1.md`)과 불일치
- **I-02**: README가 ULTIMATE_GOAL_v0.1.md를 안내하지 않음
- **I-03**: `ultimate_goal_eval_task.md`가 GitHub에 없음 (commit 누락)
- **I-04**: reuse_triage_task_A.md의 *"B안 우선"* 범위가 *reuse analysis 한정*임이 명시 안 됨
- **I-05**: architecture의 *Media Candidate* 범위와 ULTIMATE_GOAL의 *PPTX richness 비목표*의 연결 부족

이 발견들을 처리하기 위해 4개의 git 작업 그룹으로 분리:

| Group | 책임 | 최종 상태 |
|---|---|---|
| **G1** | 파일명 규칙 적용 (3개 내용 문서 rename + 6개 파일 참조 갱신) | **v4 실행 완료** (plumbing API single commit) |
| **G2** | TASK.md와 README.md 갱신 (I-01, I-02) | **v1 실행 완료** |
| **G3** | `ultimate_goal_eval_task.md` 등록 (I-03) | **v2 실행 완료** |
| **G4** | reuse_triage / architecture / GOAL_PROBLEM 보강 (I-04, I-05, P1-#6) | **v1 실행 완료** (3 commit: `bf108a0d`, `cecabd26`, `bc8f3f68`) |
| **(추가) Skills 카테고리** | `skills/agent-collaboration/` 6 skill + DESCRIPTION 추가 | **commit `8fc1605`** |

### 3.2. G1 시도 이력 — 새 세션이 알아야 할 패턴

G1 v1~v3은 모두 *멈춤*. v4가 *성공*. iteration-resilience SKILL에서 *정확히 이 패턴*을 anti-pattern으로 정리.

| 버전 | 멈춤 원인 |
|---|---|
| v1 | §3 순환 의존성 (지시서 결함) |
| v2 | 50KB의 `reuse_report.md`를 Contents API로 PUT하면 손상 위험 (codebase_analysis 자체 판단으로 안전 멈춤) |
| v3 | 로컬 git clone 요구했으나 `github.com` DNS 차단 |
| v4 — *1차 시도* | plumbing endpoint가 codebase_analysis connector에 *미활성* (`create_blob` 등 부재) |
| **v4 — *2차 시도*** | **사용자가 connector 설정 수정 → plumbing API 활성 → atomic single commit 성공** |

이 패턴이 *반복 이슈*. 자세한 분석은 `skills/agent-collaboration/iteration-resilience/SKILL.md`에 있음. 핵심 교훈: *환경 가정은 falsifiable로 다룸. codebase_analysis의 prior successes를 *증거*로 활용. 동일 task 4회 시도 후 escalation*.

### 3.3. Commit SHA 추적 (시간순)

| 파일 / 작업 | SHA |
|---|---|
| `docs/ULTIMATE_GOAL.md` 최초 commit (당시 이름) | `a9dc75cf` |
| G1~G4 v1 지시서 4개 commit | `b7f4e3f1`, `9ad93d03`, `de2fd873`, `fa537de1` |
| G1 v3 지시서 | `e3bab8a0` |
| G3 v2 지시서 | `70f84b63` |
| G1 v4 지시서 | `a83c4c8b` |
| **G4 실행** (3 commit) | **`bf108a0d`, `cecabd26`, `bc8f3f68`** |
| **Skills 카테고리 추가** | **`8fc1605`** |

---

## 4. 즉시 다음 행동 — 새 세션이 할 일

### 4.1. 단기 — *상태*: G1~G4 + Skills 모두 *완료*

T-line v0.1 종료 시점 기준으로 *이미 완료된 작업*:

| 작업 | 완료 commit |
|---|---|
| G1 v4 (3 파일 rename + 6 파일 참조 갱신) | atomic single commit (codebase_analysis 보고) |
| G2 v1 (TASK.md + README.md 갱신, I-01·I-02 처리) | 완료 보고 |
| G3 v2 (`ultimate_goal_eval_task.md` 등록, I-03 처리) | 완료 보고 |
| G4 v1 (I-04, I-05, P1-#6) | 3 commit: `bf108a0d`, `cecabd26`, `bc8f3f68` |
| Skills 카테고리 (`skills/agent-collaboration/` 6 skill + DESCRIPTION) | commit `8fc1605` |

새 세션은 G1~G4 위임 메시지를 *전달하지 않음*. 그 단계는 *지났음*.

### 4.2. 단기 — Cleanup commit (남은 첫 작업)

`*_task.md` 지시서들과 본 인계 문서는 MD-13, MD-14에 따라 삭제 대상. Cleanup commit으로 일괄 처리:

```text
docs/git_g1_rename_task.md         (v1)
docs/git_g1_rename_v2_task.md      (v2, 만약 commit되어 있다면)
docs/git_g1_rename_v3_task.md      (v3)
docs/git_g1_rename_v4_task.md      (v4, 활성 버전이었음)
docs/git_g2_readme_task.md         (v1)
docs/git_g3_register_eval_task.md  (v1)
docs/git_g3_register_eval_v2_task.md (v2, 활성 버전이었음)
docs/git_g4_p1_clarifications_task.md (v1)
docs/ultimate_goal_eval_task.md    (v1, G3에서 등록된 평가 지시서)
docs/session_summary_v0.1.md       (이 문서, MD-14에 따라)
```

**삭제 대상에 *포함되지 않는 것* (영구 보존)**:

```text
skills/agent-collaboration/                       (방법론 Skill, 영구)
docs/ULTIMATE_GOAL_v0.1.md                        (합의 보존소)
docs/GOAL_PROBLEM_v0.1.md                         (슬롯 구조)
docs/architecture_v0.1.md                         (아키텍처)
docs/reuse_report_v0.1.md                         (재사용 분석)
docs/reuse_triage_task_A.md                       (G4의 I-04 결과; 작업 파일이 아닌 분석 결과로 보존)
README.md, docs/TASK.md, scripts/, third_party/   (도구 문서 + 인프라)
```

Cleanup도 *atomic single commit* (plumbing API 권장)으로 처리. 또는 codebase_analysis의 환경에 맞춰 Contents API의 *파일별 DELETE*도 가능 (파일이 작아서 손상 위험 없음).

### 4.3. 중기 (본질 인터뷰)

Cleanup 완료 후, 외부 평가가 제시한 5개 인터뷰 질문 후보를 사용자와 인터뷰:

| Q | 내용 | ULTIMATE_GOAL 영향 |
|---|---|---|
| Q1 | architecture 파일명 결정 | **답 정해짐** (`architecture_v0.1.md`, 파일명 규칙 (β) 결정에 포함) |
| Q2 | chart는 평가 필수인가 vs asset fallback 충분 | 영향 있음 (§4-C1, §4-C3 또는 §8 UQ) |
| Q3 | 사용자가 가진 도구 = PowerPoint만인가 | 영향 있음 (§1 한 문장의 *familiar visual form* 정의) |
| Q4 | self-assessment 최소 단위는 slide/object/region | 부분 영향 (§4-C4 또는 GOAL_PROBLEM) |
| Q5 | eval_task.md 별도 작성 여부 | **답 정해짐** (G3 v2로 commit 결정) |

Q1과 Q5는 이미 답이 정해짐. **Q2, Q3, Q4가 본질 인터뷰의 핵심**.

이 인터뷰 후 ULTIMATE_GOAL_v0.1.md → v0.2 갱신 가능 (MD-4: 사용자 동의 필요).

### 4.4. 장기 (실제 코드 작성)

GOAL_PROBLEM_v0.1.md의 슬롯 8개에 따른 실제 코드 작성. 첫 단계는 reuse_report_v0.1.md의 P1 후보들 (`pixelmatch`, `pptxgenjs` 등) 통합.

이는 새 세션의 *훨씬 후속* 작업.

---

## 5. 컨텍스트가 비대해진 원인 — 새 세션이 피해야 할 패턴

T-line v0.1 세션이 길어진 주된 원인:

1. **G1 시도 4회 반복** — v1~v4 + v4 재시도. 매번 *새 환경 정보*를 얻고 지시서를 재작성. 새 세션은 *환경 정보를 먼저 확인*하는 패턴 적용 (`skills/agent-collaboration/iteration-resilience/SKILL.md`에 명시).

2. **인터뷰의 *깊이 우선* 원칙** — 사용자께서 *"시간이 더 많이 드는 것을 선택한다"*고 명시. 각 결정마다 여러 옵션 분석. 이는 *방법론 자체*이지 비효율 아님. 다만 *컨텍스트 누적*은 불가피.

3. **외부 평가 처리** — 평가 보고서 자체가 길고, P0/P1로 분리되어 *후속 작업이 많음*.

새 세션 권고:
- 이 문서를 먼저 읽고 *현재 상태*만 파악
- `skills/agent-collaboration/` 6 skill을 *방법론 참고*로 사용
- 사용자의 *깊이 우선* 원칙은 유지하되, *과거 결정의 재논의는 회피*

---

## 6. 사용자가 새 세션에 전달할 것 — 4가지 인계 항목 매핑

| 항목 | 어디서 받는가 | 새 세션의 역할 |
|---|---|---|
| 1. 코드 자체 | GitHub repo | 필요 시 fetch / 읽음. *지금은 코드 없음 — bootstrap 상태*. |
| 2. 사용자↔Agent 첨삭 | 사용자가 *압축본*을 새 세션에 전달 | 사용자의 인터뷰 스타일, 결정 패턴 이해 |
| 3. 세션 요약 | **이 문서 (`docs/session_summary_v0.1.md`)** | 현재 상태 파악 |
| 4. 반복 이슈 → Skill | **`skills/agent-collaboration/` 카테고리 (6 skill)** — commit `8fc1605` | 방법론 적용. 6 skill 각각의 frontmatter `related_skills`로 양방향 그래프 형성됨 (EX-4) |

---

## 7. 멈춤 지점 표시 — 정확한 위치

T-line v0.1 세션이 종료되는 정확한 작업 위치 (이 인계 문서 commit 시점 기준):

```
[완료]
  - ULTIMATE_GOAL.md v0.1 합의 (commit a9dc75cf)
  - 외부 평가 (codebase_analysis가 수행, 5개 발견 I-01~I-05)
  - G1~G4 지시서 v1 commit (b7f4e3f1, 9ad93d03, de2fd873, fa537de1)
  - G1 v1~v3 시도 → 환경 차이로 멈춤
  - G1 v4 + G3 v2 작성 + commit (a83c4c8b, 70f84b63)
  - G1 v4 실행 (plumbing API atomic single commit)
  - G2 v1, G3 v2 실행 완료
  - G4 v1 실행 완료 (3 commit: bf108a0d, cecabd26, bc8f3f68)
  - Skills 카테고리 commit (skills/agent-collaboration/, commit 8fc1605)
  - 본 인계 문서 commit (이번 commit)

[현재 위치 ← T-line v0.1 종료 지점]
  - 인계 산출물 둘 다 GitHub에 land:
      docs/session_summary_v0.1.md (이 문서)
      skills/agent-collaboration/ (6 skill + DESCRIPTION)
  - 새 세션 시작 대기

[다음 — 새 세션의 작업]
  - 이 문서와 6 skill 정독
  - Cleanup commit (위 §4.2에 명시된 일회성 파일들 삭제)
  - Q2, Q3, Q4 본질 인터뷰 (위 §4.3)
  - ULTIMATE_GOAL v0.2 갱신 가능성 (MD-4: 사용자 동의 필요)
  - 실제 코드 작성 시작 (위 §4.4)
```

---

## 8. 새 세션 시작 절차

1. **이 문서를 정독** (5-10분) — 현재 상태와 다음 행동 파악
2. **`skills/agent-collaboration/DESCRIPTION.md`로 카테고리 개요 파악** 후 **6 skill의 SKILL.md를 각각 정독** (15-20분) — 방법론 흡수. 6 skill의 frontmatter `related_skills`로 양방향 그래프 형성되어 있음 (EX-4)
3. **GitHub repo의 최신 상태 확인** — 특히 `docs/ULTIMATE_GOAL_v0.1.md`, `docs/GOAL_PROBLEM_v0.1.md`, `docs/architecture_v0.1.md`, `docs/reuse_report_v0.1.md`, `skills/agent-collaboration/` 존재 확인
4. **첫 작업은 Cleanup commit** — §4.2에 명시된 일회성 파일들 일괄 삭제. 본 문서도 삭제 대상 (MD-14)
5. **그 다음 본질 인터뷰** — §4.3의 Q2, Q3, Q4. 사용자의 *깊이 우선* 원칙 유지. 한 턴 한 결정. 자동 추론으로 풀 수 있는 것은 추론, 새 결정은 수동 인터뷰

---

## 9. 인계 완료 후 처리

본 문서는 MD-14에 따라 **인계 완료 후 삭제** 대상.

삭제 시점: 새 세션이 *이 문서와 6 skill의 정보를 모두 흡수*하고 *Cleanup commit을 실행한 시점*. 본 파일은 §4.2의 Cleanup commit에 *함께 포함*되어 삭제.

`skills/agent-collaboration/` 카테고리 (6 skill + DESCRIPTION + auto-derivation-checklist) 는 *영구 보존* — 방법론은 *재사용 가능*하므로 삭제 대상 아님. 새 세션이 적용 중 *새 anti-pattern 발견* 시 해당 skill의 SKILL.md를 *직접 patch*하는 것이 Hermes 패턴 (`skill_manage(action='patch')`)에 부합.
