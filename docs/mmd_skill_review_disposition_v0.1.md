# MMD Skill Review Disposition v0.1

| 항목 | 값 |
|---|---|
| 문서 종류 | 내용 문서 (`_vx.x` 규칙 적용) |
| 범위 | `mmd-diagram-authoring` skill, its checker, and the directly related references/tests |
| 지위 | 리뷰 후속 기록. 평가 문서가 아니라, **실제로 수정되어 main에 반영된 finding만** 남기는 disposition register |
| 포함 기준 | 외부/다른 세션 리뷰에서 제기된 finding 중, 실제 커밋으로 처리 완료된 항목만 포함 |
| 제외 기준 | 기각, 보류, 미해결 scope decision, 후속 인터뷰 필요 항목은 의도적으로 제외 |

## 0. 목적

이 문서는 `mmd-diagram-authoring` review cycle에서 무엇이 실제로 고쳐졌는지 기록한다.

핵심 제약은 다음과 같다.

- **채택 + 수정 완료된 finding만** 적는다.
- 기각/보류 항목은 이 문서의 범위가 아니다.
- "왜 안 고쳤는가"보다 **"무엇을 어느 커밋에서 닫았는가"**를 빠르게 찾게 하는 것이 목적이다.

즉 이 문서는 full review archive가 아니라 **fixed-findings register**다.

## 1. 대상 커밋

이 review cycle에서 `mmd-diagram-authoring` 관련으로 반영된 핵심 커밋은 다음과 같다.

| SHA | 메시지 | 역할 |
|---|---|---|
| `f0ed2fb` | `skills: harden mmd-diagram-authoring (HARDLINE, EX-4, false-green fix, philosophy alignment)` | hardening baseline |
| `715a632` | `fix: handle multi-directory mmd checker logging` | checker multi-directory crash hotfix |
| `1315283` | `docs: tighten mmd authoring skill boundaries` | project-local content extraction, boundary tightening |
| `40e36bc` | `fix: tighten mmd skill portability and checker discipline` | residue cleanup, checker discipline, logging default change |
| `9f01091` | `docs: clarify mmd checker parity contract` | parity 보장 범위 명문화 |

이 문서는 위 다섯 커밋 안에서 **실제로 닫힌 finding만** 다룬다.

## 2. 수정 완료된 Finding Register

### D-01. checker zero-file false green 제거

- **출처 finding 계열:** SK-8, "0개 `.mmd` / 잘못된 경로에서도 성공 종료"
- **처리 커밋:** `f0ed2fb`
- **현재 상태:**
  - 존재하지 않는 경로는 `exit 2`
  - `.mmd`가 하나도 없으면 `exit 1`
  - 정상 대상만 `exit 0`
- **근거:**
  - [check_mmd_files.py:157-195](/Users/jaehyuntak/Desktop/Project_____현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py:157)
  - [Verification](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:132)

### D-02. checker multi-directory logging crash 제거

- **출처 finding 계열:** "복수 디렉터리 입력에서 `relative_to()` ValueError로 crash"
- **처리 커밋:** `715a632`
- **현재 상태:**
  - 첫 번째 target 기준 상대경로가 안 되면 cwd 기준 relpath
  - 그것도 안 되면 absolute path로 fallback
  - 복수 디렉터리 입력에서도 logging 때문에 crash하지 않음
- **근거:**
  - [write_log](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py:129)

### D-03. project-specific layer map를 portable skill 본문에서 분리

- **출처 finding 계열:** F1, "Diagram Layers가 generic authoring skill 안에 project policy로 섞임"
- **처리 커밋:** `1315283`
- **현재 상태:**
  - skill 본문에는 portable discipline만 남김
  - project layer map은 별도 project-local reference로 분리
- **근거:**
  - [Project-local references](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:81)
  - [project-diagram-layers.md](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/references/project-diagram-layers.md)

### D-04. label vocabulary / Korean glossary를 portable skill 본문에서 분리

- **출처 finding 계열:** F2, "Label Vocabulary / Korean Labeling이 project glossary 역할을 함"
- **처리 커밋:** `1315283`
- **현재 상태:**
  - 본문에는 labeling principle만 남김
  - 프로젝트 어휘와 번역 예시는 project-local reference로 분리
- **근거:**
  - [Labeling Principles](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:90)
  - [project-label-vocabulary.md](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/references/project-label-vocabulary.md)

### D-05. Modes와 Verification의 연결 명시

- **출처 finding 계열:** F5, "Modes 개념이 문서 전체에 충분히 thread되지 않음"
- **처리 커밋:** `1315283`
- **현재 상태:**
  - Interactive authoring ↔ Human-judged
  - Batch validation ↔ Machine-verified
  를 skill 본문에 직접 연결
- **근거:**
  - [Modes](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:32)
  - [Verification](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:132)

### D-06. When to Use trigger 중복 제거

- **출처 finding 계열:** F7, "macro alignment trigger가 중복됨"
- **처리 커밋:** `1315283`
- **현재 상태:**
  - broader trigger만 남기고 중복된 narrower trigger 제거
- **근거:**
  - [When to Use](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:22)

### D-07. portable reference에서 빠진 §6에 대한 omission note 추가

- **출처 finding 계열:** F4, "`§5 -> §7` 점프가 standalone reference에서는 결손처럼 보임"
- **처리 커밋:** `1315283`
- **현재 상태:**
  - portable subset 안에 §6 omission note를 둬서 source numbering과 reference numbering의 관계를 보이게 함
- **근거:**
  - [architecture-diagram-evaluation.md §6 note](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/references/architecture-diagram-evaluation.md:131)

### D-08. portable skill 본문에 남아 있던 project vocabulary residue 제거

- **출처 finding 계열:** R1, R2
- **처리 커밋:** `40e36bc`
- **현재 상태:**
  - Procedure는 pattern-based wording으로 일반화
  - Pitfalls는 project term이 아니라 generic form으로 표현
  - project-local examples는 reference로 유도
- **근거:**
  - [Procedure](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:59)
  - [Pitfalls](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:123)

### D-09. Bundled Script 예시를 실제 실행 가능한 명령으로 수정

- **출처 finding 계열:** R3 / N2
- **처리 커밋:** `40e36bc`
- **현재 상태:**
  - repo root 기준 실행 명령으로 정리
  - skill dir / repo root 어디에서도 동시에 깨지는 hardcoded form 제거
- **근거:**
  - [How to Run](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:43)
  - [Bundled Script](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:113)

### D-10. checker labeled-edge parity false green 제거

- **출처 finding 계열:** N1
- **처리 커밋:** `40e36bc`
- **현재 상태:**
  - `-->|label|` 형태의 labeled edge도 parity signature에 반영
  - en/ko 구조 mismatch가 silent green으로 통과하지 않음
- **근거:**
  - [EDGE_RE](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py:31)
  - [check_parity](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py:72)

### D-11. audit log가 기본 검증 때 tracked dirty change를 만드는 구조 제거

- **출처 finding 계열:** N3
- **처리 커밋:** `40e36bc`
- **현재 상태:**
  - checker logging은 `--log` opt-in
  - `.mmd_check_log.jsonl`은 ignore 대상
  - `__pycache__`도 ignore 대상
- **근거:**
  - [check_mmd_files.py main](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py:157)
  - [.gitignore](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/.gitignore:1)

### D-12. architecture evaluation 문서의 stale evidence link 갱신

- **출처 finding 계열:** F1의 후속 side effect
- **처리 커밋:** `40e36bc`
- **현재 상태:**
  - `SKILL.md §Diagram Layers`를 가리키던 포인터를 새 project-local reference 경로로 갱신
- **근거:**
  - [architecture_eval_v0.1.md:58](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/docs/architecture_eval_v0.1.md:58)
  - [architecture_eval_v0.1.md:169](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/docs/architecture_eval_v0.1.md:169)

### D-13. parity 보장 범위를 출력과 문서에 계약으로 명시

- **출처 finding 계열:** "checker가 보장하는 것과 보장하지 않는 것을 출력과 문서가 말하지 않는다"
- **처리 커밋:** `9f01091`
- **현재 상태:**
  - CLI 출력이 `parity: ok`만이 아니라, 무엇을 보는지와 무엇을 보지 않는지를 같이 말함
  - SKILL.md도 동일 범위를 문서화
  - unpaired language variants skip semantics를 출력에 포함
- **근거:**
  - [parity summary construction](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/scripts/check_mmd_files.py:111)
  - [Bundled Script contract](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:121)
  - [Machine-verified note](/Users/jaehyuntak/Desktop/Project_____현재_현재_진행중인/html-to-editable-pptx/skills/architecture/mmd-diagram-authoring/SKILL.md:136)

## 3. 의도적으로 다루지 않는 것

이 문서는 다음을 의도적으로 다루지 않는다.

- 기각된 finding
- 아직 보류 중인 finding
- checker scope를 더 넓힐지에 대한 새 결정
  - duplicate edge count 검사
  - edge label equality 검사
  - 더 넓은 Mermaid edge grammar 지원
- `mmd-diagram-authoring` 바깥의 일반 운영 규율

위 항목들은 필요하면 별도 disposition 또는 별도 decision 문서의 범위다.

## 4. 한 줄 요약

> **이 review cycle에서 실제로 main에 반영된 것은 boundary tightening, checker false-green 제거, logging discipline 정리, parity contract 명문화다. 이 문서는 그 완료분만 기록한다.**
