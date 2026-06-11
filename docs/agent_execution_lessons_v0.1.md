# Agent Execution Lessons v0.1

| 항목 | 값 |
|---|---|
| 문서 종류 | 내용 문서 (`_vx.x` 규칙 적용) |
| 출처 | 2026-06-10~2026-06-11의 실제 실행 세션들에서 반복적으로 드러난 운영 교훈을 정리한 기록 |
| 지위 | 운영 규율 문서. 아키텍처 권위 문서가 아니라, task packet 실행과 handoff를 안정화하기 위한 규율의 집합 |
| 관계 | `skills/agent-collaboration/task-delegation`, `iteration-resilience`, `session-handoff`가 다루는 원칙을 본 저장소의 실제 incident에 맞게 구체화한 후속 기록 |

## 0. 목적

이 문서는 아키텍처나 기능 요구를 정의하지 않는다.
이 문서는 **다른 agent가 task packet을 실제로 실행할 때 반복해서 부딪힌 운영 문제**를
재발 방지 규율로 고정한다.

핵심 구분은 다음과 같다.

- `mmd-diagram-authoring` 같은 skill은 **무엇을 만들고 어떻게 검토할지**를 다룬다.
- 이 문서는 **어떤 환경에서 실행할 수 있는지, 언제 멈춰야 하는지, 무엇을 handoff로 남겨야 하는지**를 다룬다.

즉 이 문서의 관심사는 설계가 아니라 **execution discipline**이다.

## 1. 적용 범위

이 문서는 다음과 같은 작업에 적용한다.

1. 한 agent가 지시서를 쓰고 다른 agent가 실행하는 작업
2. git clone, 테스트 실행, commit, push, patch export 같은 실제 실행이 포함된 작업
3. 로컬 clone / snapshot / 제한된 sandbox / 네트워크 불가 환경처럼 실행 표면이 서로 다른 환경을 오가는 작업

다음은 이 문서의 범위가 아니다.

- 아키텍처 목표, 기능 우선순위, 합의 문서의 내용 자체
- checker가 어떤 의미론까지 검사해야 하는지에 대한 제품/정책 결정
- task packet 하나의 구체 절차를 대체하는 것

## 2. 핵심 운영 규율

### EL-1. 실행 표면은 시작 전에 증명되어야 한다.

실행 agent가 실제로 가진 표면이 무엇인지 먼저 확인한다. 가정하지 않는다.

- git 작업을 요구하는 packet은 **실제 git clone**이 필요하다.
- `.git`이 없는 snapshot은 읽기나 제한적 수정에는 쓸 수 있어도, `git status`, `commit`, `push`를 요구하는 packet의 실행 환경으로 간주하지 않는다.
- packet이 전제하는 네트워크 표면(`origin main` pull, `git push`, 패키지 설치, remote API)이 실제로 열려 있는지 preflight에서 확인한다.

핵심 원칙:

> **환경 가정은 사실이 아니라 가설이다. preflight가 그 가설을 깨면, 실행이 아니라 보고가 정답이다.**

### EL-2. dirty worktree는 보호 대상이다.

실행 전 `git status --short`로 현재 작업트리를 읽고, 기존 변경을 보호한다.

- 사용자 또는 다른 흐름의 변경은 되돌리지 않는다.
- dirty worktree에서는 **명시 파일만 stage**한다.
- 디렉터리 단위 `git add skills/`, `git add docs/` 같은 광범위 staging은 금지한다.
- 실행 중 생성된 캐시나 로그가 tracked 변경과 섞이지 않도록 분리한다.

핵심 원칙:

> **작업 범위는 설명으로가 아니라 staging set으로 증명된다.**

### EL-3. 검증 gate 실패는 publish 금지다.

packet이 요구한 검증 중 하나라도 실패하면 commit/push를 하지 않는다.

- `pytest`가 required gate면, smoke나 직접 호출 테스트가 일부 통과해도 대체로 간주하지 않는다.
- checker 통과, lint 통과, diff 검토 같은 gate는 "참고"가 아니라 **출시 전제**다.
- 부분 성공 상태를 commit으로 남기지 않는다.

핵심 원칙:

> **"거의 됨"은 publish 조건이 아니다.**

### EL-4. 환경이 publish를 막으면 patch export로 전환한다.

작업 자체는 진행됐지만 현재 환경이 최종 검증 또는 publish를 막으면, patch export가 표준 fallback이다.

대표 사례:

- `pytest` 설치/조회 불가
- 실제 clone은 있지만 push 불가
- 수정은 끝났지만 최종 gate를 현재 세션이 충족할 수 없음
- 접근 가능한 환경과 publish 가능한 환경이 서로 다름

이 경우의 표준 산출물:

1. unified diff 또는 patch 파일
2. 변경된 파일 목록
3. 수행된 검증과 실패한 검증의 구분
4. commit/push를 하지 않은 이유

핵심 원칙:

> **publish 권한이 없는 환경에서는 결과를 숨기지 말고 이동 가능한 형태로 동결한다.**

### EL-5. `git push`와 remote API commit은 다른 publish surface다.

이 둘은 같은 "게시"가 아니다.

- atomicity가 다르다
- 파일 크기/전송 비용 특성이 다르다
- auth surface가 다르다
- 실패 모드가 다르다
- audit trail이 다르다

따라서 packet은 어느 publish surface를 쓸지 **하나를 고른 상태**여야 한다.
실행 agent는 임의로 `git push`를 remote API commit으로, 또는 그 반대로 바꾸지 않는다.

핵심 원칙:

> **publish surface 변경은 구현 detail이 아니라 execution contract 변경이다.**

### EL-6. 생성 부산물은 의도적으로 처리한다.

실행 중 생기는 부산물은 세 가지로 분리한다.

1. **영구 산출물** — commit 대상 문서/코드
2. **opt-in audit artifact** — 필요할 때만 남기는 로그
3. **ephemeral cache** — 남기지 않거나 ignore할 캐시

대표 예:

- `tests/skills/__pycache__/`는 ephemeral cache다
- `.mmd_check_log.jsonl` 같은 로그는 기본 tracked 산출물이 아니라 opt-in audit artifact다

도구가 실행될 때마다 tracked file을 더럽히는 구조라면, 그것은 문서화하거나 수정해야 한다.

핵심 원칙:

> **검증 도구는 기본적으로 증거를 만들 수는 있어도, 예고 없이 작업트리를 더럽혀서는 안 된다.**

### EL-7. 도구의 보장 범위는 계약으로 적어야 한다.

checker, smoke script, direct invocation test는 각자 보장 범위가 다르다.
이 범위는 사람의 머릿속이 아니라 문서와 출력에 명시되어야 한다.

예:

- checker가 node IDs와 edge endpoints만 본다면 그렇게 적는다
- edge labels, display labels, duplicate counts를 보지 않는다면 그렇게 적는다
- human review를 대체하지 않는다면 그렇게 적는다

핵심 원칙:

> **부분 보장은 "ok"라는 한 단어로 끝내지 않는다.**

### EL-8. halt report는 다음 실행의 입력이어야 한다.

중단 보고는 변명이 아니라 다음 실행을 위한 구조화된 입력이어야 한다.

최소 포함 항목:

- 어느 phase에서 멈췄는가
- 어떤 명령이 실패했는가
- 실패 원인이 artifact 문제인지, 환경 문제인지
- 무엇을 실행했고 무엇은 실행하지 않았는가
- 어떤 파일이 바뀌었는가
- patch export가 가능한가
- commit/push를 했는가

핵심 원칙:

> **좋은 halt report는 "왜 멈췄는가"뿐 아니라 "다음 환경에서 무엇을 재사용할 수 있는가"까지 남긴다.**

## 3. Preflight Checklist

task packet 실행 전 최소한 다음을 확인한다.

| 항목 | 예시 확인 방법 | 실패 시 처리 |
|---|---|---|
| 실제 git clone 여부 | `git rev-parse --is-inside-work-tree` | git-required packet이면 중단 |
| 원격 동기화 가능 여부 | `git pull --ff-only origin main` | publish surface 재판정 또는 중단 |
| 현재 worktree 상태 | `git status --short` | dirty set 보호 계획 수립 |
| 필수 입력 존재 | packet의 required-to-exist 목록 확인 | 중단 |
| 테스트 도구 존재 | `python3 -m pytest --version` 등 | required gate면 중단 또는 patch export 경로 준비 |
| 선택된 publish surface 사용 가능 여부 | `git push`, remote API, auth 상태 확인 | surface 임의 변경 금지, 중단 후 보고 |

이 preflight는 "대충 시작해 보고 안 되면 생각한다"를 금지하기 위한 단계다.

## 4. Fallback Ladder

문제가 생겼을 때의 기본 순서는 다음과 같다.

1. **환경 사실 확인** — 현재 환경이 packet을 충족하는지 다시 판정
2. **검증 대체 가능성 판정** — packet이 허용한 범위 안에서만 대체
3. **publish 중단 여부 판정** — required gate 미충족이면 publish 금지
4. **patch export 여부 판정** — 변경 재사용이 가능하면 patch/diff로 동결
5. **halt report 작성** — 다음 실행 환경이 바로 이어받을 수 있게 보고

다음은 명시적으로 금지한다.

- required gate를 임의로 optional로 낮추는 것
- publish surface를 packet 밖에서 바꾸는 것
- dirty worktree에서 광범위 staging으로 "일단 commit"하는 것
- 실패 원인을 숨기고 부분 성공 commit을 남기는 것

## 5. Report Contract

실행 세션의 결과 보고는 최소한 아래 형식을 만족해야 한다.

```text
execution result:
  Phase 0:            OK / FAILED
  environment:        real clone / snapshot / restricted sandbox / other
  worktree status:    clean / dirty (preserved paths: ...)
  required inputs:    OK / FAILED (missing: ...)
  validation:         each required gate -> OK / FAILED / NOT RUN
  changed files:      <explicit list>
  generated artifacts:<explicit list or none>
  patch export:       path / none
  commit SHA:         <sha> / none
  push:               OK / FAILED / NOT RUN
  stop reason:        <one sentence>
```

이 형식의 목적은 간단하다.
다음 agent가 "무엇을 다시 해야 하는지"가 아니라 **"무엇은 이미 끝났는지"**를 즉시 알게 하는 것이다.

## 6. Non-goals

이 문서는 다음을 하지 않는다.

- 아키텍처나 제품 목표를 결정하지 않는다
- 개별 checker나 script의 세부 scope를 여기서 확정하지 않는다
- task packet의 구체 절차를 대체하지 않는다
- destructive cleanup, rollback, force-push를 일반 해법으로 정당화하지 않는다
- 검증 실패를 "이번만 예외"로 통과시키는 근거를 제공하지 않는다

## 7. 한 줄 요약

> **실행 작업의 품질은 수정 내용만으로 결정되지 않는다. 올바른 환경에서, 올바른 검증을 통과하고, publish 가능한 surface에서, 재사용 가능한 halt report까지 남겨야 비로소 완료다.**
