# 작업 요청서 — G1 v4: 파일명 규칙 적용 (GitHub git plumbing API 기반)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g1-rename (v4) |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | GitHub REST API 작업 (plumbing — blobs / trees / commits / refs) |
| **필수 환경** | **`api.github.com` 접근 + write 권한** (codebase_analysis 환경에서 이미 증명됨) |
| 산출물 | commit SHA 1개 (atomic) |
| 예상 소요 | 20분 |
| 의존성 | 없음 — 가장 먼저 실행 |
| 대체 대상 | v1, v2, v3 모두 |
| 수명 | **본 지시서는 작업 완료 후 삭제 대상** (MD-13) |

### v4 발행 이유

v1·v2·v3 모두 codebase_analysis 환경에서 실행 불가했다. 분석 결과:

- **v1**: §3 순환 의존성 (지시서 결함)
- **v2**: Contents API로 50KB `reuse_report.md` 손상 위험 → 정당한 멈춤
- **v3**: 로컬 git clone 요구 → `github.com` DNS 차단으로 불가

그러나 같은 codebase_analysis 환경에서 *지시서 commit 자체*는 *수차례 성공*했다 (`a9dc75cf`, `e3bab8a0`, `70f84b63` 등). 이는 `api.github.com` 접근이 *증명*되었음을 의미한다.

**v4의 결정적 통찰**: GitHub REST API의 *git plumbing 엔드포인트*는:

- `api.github.com`을 통해 호출됨 (codebase_analysis 환경 가용)
- `github.com` DNS나 git protocol 불필요 (v3 차단 회피)
- rename은 *이전 blob SHA를 새 path에 매핑* — **50KB 본문 다시 전송 안 함** (v2 손상 위험 회피)
- 9개 파일 변경을 *하나의 tree + 하나의 commit*으로 묶음 — 부분 적용 *수학적으로 불가능* (v2 외부 평가 권고 #7 *"부분 성공 commit 금지"* 충족)

v4는 *codebase_analysis의 능력*과 *환경 제약*과 *외부 평가 권고* 모두를 만족하는 **유일한 경로**다.

## 2. 작업의 위치

T-line 세션의 인터뷰에서 사용자가 확정한 파일명 규칙:

- **규칙**: 내용 문서는 `_vx.x.md` suffix를 사용
- **소급 적용 범위 (β)**: 모든 내용 문서에 적용. 지시서와 도구 문서(README.md)는 제외
- **사용자의 명시적 동의**: ULTIMATE_GOAL.md 이름 변경 포함

본 작업(G1)은 이 규칙을 GitHub 저장소에 적용한다. G2/G3 v2/G4는 G1 v4 완료 후 진행한다.

## 3. 필수 환경 검증

### 3.1. 환경 요구사항

본 지시서는 **GitHub REST API의 git plumbing 엔드포인트**를 호출할 수 있는 환경에서 실행한다. 다음 능력이 필요하다:

| 능력 | 검증 방법 |
|---|---|
| `api.github.com` HTTPS 호출 | 이전 commit 성공이 이미 증명 |
| `goodand/html-to-editable-pptx` repo write 권한 | 이전 commit 성공이 이미 증명 |
| `GET /repos/{owner}/{repo}/git/trees/{ref}?recursive=1` | 표준 endpoint |
| `POST /repos/{owner}/{repo}/git/blobs` | 표준 endpoint |
| `POST /repos/{owner}/{repo}/git/trees` | 표준 endpoint |
| `POST /repos/{owner}/{repo}/git/commits` | 표준 endpoint |
| `PATCH /repos/{owner}/{repo}/git/refs/heads/main` | 표준 endpoint |

로컬 `git clone`, `git mv`, `sed`, `git push`는 **사용하지 않는다**. v4는 *원격 plumbing API only*.

### 3.2. 환경 사전 검증

```text
1. GET /repos/goodand/html-to-editable-pptx → 200 응답 확인
2. GET .../git/refs/heads/main → 현재 main의 commit SHA 획득 (이하 BASE_COMMIT)
3. GET .../git/commits/{BASE_COMMIT} → BASE_COMMIT의 tree SHA 획득 (이하 BASE_TREE)
4. GET .../git/trees/{BASE_TREE}?recursive=1 → 모든 파일의 path와 blob SHA 매핑 획득
```

이 4단계가 모두 200 응답이면 환경 OK. 어느 하나라도 실패하면 §6 Non-goals 환경 부재 폴백 규칙으로.

## 4. 작업 정의

### 4.1. 작업의 atomic 단위

전체 G1은 **하나의 commit**으로 처리한다. 이는 v4의 핵심 안전장치다:

- 부분 적용 *수학적으로 불가능* (하나의 tree object에 9개 변경 모두 포함)
- 실패 시 main의 ref가 *원래 위치 그대로* — 롤백 불필요
- 성공 시 단 한 번의 `PATCH refs/heads/main`이 모든 변경을 한꺼번에 publish

### 4.2. 처리 단계

#### Step 1 — 현재 상태 획득

```text
GET /repos/goodand/html-to-editable-pptx/git/refs/heads/main
  → BASE_COMMIT_SHA

GET /repos/goodand/html-to-editable-pptx/git/commits/{BASE_COMMIT_SHA}
  → BASE_TREE_SHA, parent_commits

GET /repos/goodand/html-to-editable-pptx/git/trees/{BASE_TREE_SHA}?recursive=1
  → tree entries [{path, mode, type, sha}, ...]
```

이 응답에서 다음을 추출:

| 변수 | 값의 의미 |
|---|---|
| `OLD_UG_SHA` | `docs/ULTIMATE_GOAL.md`의 현재 blob SHA |
| `OLD_GP_SHA` | `docs/GOAL_PROBLEM.md`의 현재 blob SHA |
| `OLD_RR_SHA` | `docs/reuse_report.md`의 현재 blob SHA |
| `OLD_ARCH_SHA` | `docs/architecture_v0.1.md`의 현재 blob SHA (있다면) |
| `OLD_TRIAGE_SHA` | `docs/reuse_triage_task_A.md`의 현재 blob SHA |
| `OLD_EVAL_SHA` | `docs/ultimate_goal_eval_task.md`의 현재 blob SHA (없으면 null) |

#### Step 2 — 변경되는 파일의 *새 blob* 생성

6개 파일에 대해 *새 본문*을 만들어 blob으로 생성한다.

처리 방법:

```text
for each file in [
  docs/ULTIMATE_GOAL.md, docs/GOAL_PROBLEM.md, docs/reuse_report.md,
  docs/architecture_v0.1.md, docs/reuse_triage_task_A.md,
  docs/ultimate_goal_eval_task.md
]:
    if file exists in BASE_TREE:
        GET /repos/.../git/blobs/{OLD_SHA} → base64 content
        decode to text
        apply three sed-equivalent substitutions:
            "ULTIMATE_GOAL.md" → "ULTIMATE_GOAL_v0.1.md"
            "GOAL_PROBLEM.md"  → "GOAL_PROBLEM_v0.1.md"
            "reuse_report.md"  → "reuse_report_v0.1.md"
        if any substitution actually changed text:
            POST /repos/.../git/blobs with {content: <new_text>, encoding: "utf-8"}
            → NEW_SHA for this file
        else:
            NEW_SHA = OLD_SHA  (no change, reuse the blob)
    else:
        skip (file not present, e.g., ultimate_goal_eval_task.md if G3 not yet)
```

`OLD_SHA = NEW_SHA`인 경우 (치환 결과가 원본과 동일) blob을 새로 만들 필요 없음. plumbing API의 이점.

#### Step 3 — 새 tree 생성

새 tree는 BASE_TREE에서 다음 9개 변경을 적용한 결과:

| 변경 | path 처리 | mode | sha |
|---|---|---|---|
| docs/ULTIMATE_GOAL.md 제거 + ULTIMATE_GOAL_v0.1.md 추가 | path: `docs/ULTIMATE_GOAL.md` → 항목 자체 제외; path: `docs/ULTIMATE_GOAL_v0.1.md` → 새 항목 추가 | `100644` | (Step 2에서 얻은 NEW_UG_SHA) |
| docs/GOAL_PROBLEM.md 제거 + GOAL_PROBLEM_v0.1.md 추가 | 동일 패턴 | `100644` | NEW_GP_SHA |
| docs/reuse_report.md 제거 + reuse_report_v0.1.md 추가 | 동일 패턴 | `100644` | NEW_RR_SHA |
| docs/architecture_v0.1.md 갱신 (참조만) | path 동일, blob만 새 SHA | `100644` | NEW_ARCH_SHA (또는 변경 없으면 OLD_ARCH_SHA) |
| docs/reuse_triage_task_A.md 갱신 (참조만) | path 동일, blob만 새 SHA | `100644` | NEW_TRIAGE_SHA |
| docs/ultimate_goal_eval_task.md 갱신 (있다면) | path 동일, blob만 새 SHA | `100644` | NEW_EVAL_SHA |

GitHub의 tree 생성 API는 두 가지 패턴을 지원한다:

```text
POST /repos/.../git/trees
  body:
    base_tree: <BASE_TREE_SHA>  # 시작점
    tree: [
      {path: "docs/ULTIMATE_GOAL.md",      sha: null},                 # remove
      {path: "docs/ULTIMATE_GOAL_v0.1.md", sha: NEW_UG_SHA, mode: "100644", type: "blob"},  # add
      {path: "docs/GOAL_PROBLEM.md",       sha: null},                 # remove
      {path: "docs/GOAL_PROBLEM_v0.1.md",  sha: NEW_GP_SHA, mode: "100644", type: "blob"},  # add
      {path: "docs/reuse_report.md",       sha: null},                 # remove
      {path: "docs/reuse_report_v0.1.md",  sha: NEW_RR_SHA, mode: "100644", type: "blob"},  # add
      {path: "docs/architecture_v0.1.md",  sha: NEW_ARCH_SHA, mode: "100644", type: "blob"},  # update (only if changed)
      {path: "docs/reuse_triage_task_A.md", sha: NEW_TRIAGE_SHA, mode: "100644", type: "blob"},
      {path: "docs/ultimate_goal_eval_task.md", sha: NEW_EVAL_SHA, mode: "100644", type: "blob"},  # only if exists
    ]
  → NEW_TREE_SHA
```

`sha: null` 항목은 *그 path를 tree에서 제거*함을 의미한다. 이것이 rename의 *delete* 반쪽.
변경되지 않은 모든 파일(README.md, TASK.md, scripts/, third_party/ 등)은 base_tree에서 자동 상속된다 — 명시할 필요 없음.

#### Step 4 — 새 commit 생성

```text
POST /repos/.../git/commits
  body:
    message: <see §4.3 below>
    tree: NEW_TREE_SHA
    parents: [BASE_COMMIT_SHA]
  → NEW_COMMIT_SHA
```

이 시점까지는 *어떤 ref도 갱신되지 않았다*. NEW_COMMIT_SHA는 *떠다니는 commit object*. 사용자/codebase_analysis가 이 commit을 *조회만* 할 수 있고, main은 여전히 BASE_COMMIT를 가리킴.

#### Step 5 — 사전 검증 (commit 객체 inspection)

NEW_COMMIT_SHA를 ref에 연결하기 *전에* 검증:

```text
GET /repos/.../git/commits/{NEW_COMMIT_SHA} → 200, tree=NEW_TREE_SHA 확인
GET /repos/.../git/trees/{NEW_TREE_SHA}?recursive=1 → tree 내용 확인:
  - docs/ULTIMATE_GOAL.md, docs/GOAL_PROBLEM.md, docs/reuse_report.md 는 없어야 함
  - docs/ULTIMATE_GOAL_v0.1.md, docs/GOAL_PROBLEM_v0.1.md, docs/reuse_report_v0.1.md 는 있어야 함
  - 다른 모든 파일은 BASE_TREE와 동일 path로 존재

GET /repos/.../git/blobs/{NEW_UG_SHA} → 본문 받아 leak 검사:
  grep "ULTIMATE_GOAL.md" → 0건 (단, "ULTIMATE_GOAL_v0.1.md"는 매칭되지 않게 정밀 regex)
  grep "GOAL_PROBLEM.md"  → 0건
  grep "reuse_report.md"  → 0건

(reuse_report_v0.1.md, GOAL_PROBLEM_v0.1.md도 동일 검사)

YAML parse 검증 (ULTIMATE_GOAL_v0.1.md):
  추출 후 yaml.safe_load
  document.name == "ULTIMATE_GOAL_v0.1.md" 확인
  related_documents 키 5개 모두 새 이름 확인
```

검증 실패 시 — *ref를 갱신하지 마라*. NEW_COMMIT_SHA는 *그대로 떠다니게* 두고 T-line에 보고. main은 영향 없음.

#### Step 6 — Ref 갱신 (atomic publish)

검증 모두 통과 시:

```text
PATCH /repos/.../git/refs/heads/main
  body:
    sha: NEW_COMMIT_SHA
    force: false  # main이 BASE_COMMIT 그대로일 때만 성공 (race condition 안전)
  → 200 응답이면 commit이 main에 land
```

`force: false`는 *fast-forward only*에 해당. 만약 그 사이 main이 다른 commit으로 진행되었다면 이 호출은 실패 — codebase_analysis는 *멈추고 보고*. T-line이 상황 검토.

### 4.3. Commit message

```text
docs: apply file-naming rule _v0.1.md to content documents (G1 v4, plumbing API)

Per the T-line interview decision (file-naming convention: content
documents use _vx.x.md suffix; instruction and tool documents are
exempt), rename three content documents and update internal
references — performed as a single atomic git tree change via
GitHub plumbing API.

Renames (blob SHA preserved — no content transmission for the move):
  docs/ULTIMATE_GOAL.md  -> docs/ULTIMATE_GOAL_v0.1.md
  docs/GOAL_PROBLEM.md   -> docs/GOAL_PROBLEM_v0.1.md
  docs/reuse_report.md   -> docs/reuse_report_v0.1.md

Internal-reference updates (new blob created only where text changed):
  docs/ULTIMATE_GOAL_v0.1.md (after rename, references updated)
  docs/GOAL_PROBLEM_v0.1.md
  docs/reuse_report_v0.1.md
  docs/architecture_v0.1.md
  docs/reuse_triage_task_A.md
  docs/ultimate_goal_eval_task.md (if present at execution time)

Method (v4 vs prior versions):
  v1 halted on circular dependency in input list.
  v2 halted on Contents API risk of damaging the 50KB reuse_report.md
     during full-body PUT.
  v3 required local git clone but github.com DNS was blocked in the
     codebase_analysis environment.
  v4 uses GitHub git plumbing API (api.github.com) which the
     codebase_analysis environment can reach (proven by prior commits
     in this repository). Rename does not transmit blob content;
     reused blob SHA. Internal reference updates create new blobs only
     for files whose text actually changes. All nine changes are
     packed into one tree and one commit; atomic, no partial
     application possible.

Pre-publish verification (performed before PATCH refs):
  - Tree contents inspected (old names removed, new names present)
  - Each updated blob downloaded and re-checked for old-name leaks
  - YAML in ULTIMATE_GOAL_v0.1.md parsed; document.name and
    related_documents reflect new names
  - Commit object inspected for tree/parent integrity

If any verification step failed, the commit object remained as a
floating object and main was not advanced. This commit was
published only after all checks passed.

Exempt from this commit:
  README.md, docs/TASK.md (tool/instruction documents — G2 handles)
  *_task.md instruction files (names kept; references updated)

MD-4 (user-consent for ULTIMATE_GOAL modification):
  User explicitly approved the rename via T-line interview answer
  to "(β) — apply rule including ULTIMATE_GOAL.md". Content is
  preserved byte-for-byte except for the three reference substitutions.

Supersedes:
  docs/git_g1_rename_task.md     (v1)
  docs/git_g1_rename_v2_task.md  (v2)
  docs/git_g1_rename_v3_task.md  (v3)
```

### 4.4. 보고

작업 완료 후 T-line에 보고:

```text
G1 v4 결과:
  환경 검증:        OK / FAILED
  BASE_COMMIT_SHA:  <SHA>
  BASE_TREE_SHA:    <SHA>
  새 blob 생성:    N개 (어느 파일이 새 blob을 받았는지)
  blob SHA 재사용: N개 (변경 없음으로 OLD_SHA 그대로 쓴 파일)
  skipped 파일:    N개 (BASE_TREE에 없어서 처리 안 한 파일)
  NEW_TREE_SHA:    <SHA>
  NEW_COMMIT_SHA:  <SHA>
  사전 검증:
    tree 구조:     OK / FAILED
    blob leak:     0건 / N건
    YAML parse:    OK / FAILED
  ref PATCH:       OK / FAILED (force-with-lease: BASE_COMMIT 그대로일 때만 성공)
  최종 commit SHA: <SHA, ref 갱신 성공 시>
```

## 5. 산출물 형식

위 §4.4 보고를 T-line 세션에 전달.

## 6. 비목표 (Non-goals)

### Case: Type

- **Contents API를 사용하지 마라.** v2의 손상 위험. plumbing API만 사용.
- **로컬 git clone을 시도하지 마라.** v3에서 차단 확인. plumbing API로 완결.
- **여러 commit으로 쪼개지 마라.** v4의 *원자성*이 핵심 안전장치. 9개 변경은 *하나의 tree, 하나의 commit*.
- **G2/G3/G4의 작업을 G1 v4에 포함하지 마라.**

### Case: State

- **사전 검증 실패 시 ref 갱신 금지.** NEW_COMMIT_SHA는 *떠다니게* 두고 T-line에 보고. main은 BASE_COMMIT 그대로 유지 (자동 롤백 효과).
- **force-with-lease (`force: false`)로만 PATCH.** main이 그 사이 진행되었으면 실패해야 정상.
- **환경 부재 시 폴백을 *자체 결정하지 마라*.** §3.2 환경 검증 실패 시 T-line 보고.

### Case: Performance: Over

- **변경 없는 파일에 새 blob을 만들지 마라.** Step 2의 *변경 검사*가 통과한 파일은 OLD_SHA 재사용.
- **여러 commit으로 안전성을 *시뮬레이션*하지 마라.** atomic tree change 자체가 안전성. 추가 단계 불필요.

## 7. 검증 규칙 (산출물 완료 기준)

1. 환경 검증 통과 (§3.2)
2. BASE_TREE에서 §3.3.1 파일 3개 SHA 추출 성공
3. NEW_TREE에서 §3.3.1 옛 path 3개 부재, 새 path 3개 존재
4. 새 blob의 leak 검사 0건
5. ULTIMATE_GOAL_v0.1.md YAML 파싱 성공
6. ref PATCH 성공 (force: false)
7. T-line에 최종 commit SHA 보고

## 8. 시작 지시

1. §3.2 환경 사전 검증
2. §4.2 Step 1 — 현재 상태 획득
3. §4.2 Step 2 — 변경되는 blob 생성
4. §4.2 Step 3 — 새 tree 생성
5. §4.2 Step 4 — 새 commit 생성 (이 시점에는 ref 갱신 없음)
6. §4.2 Step 5 — 사전 검증
7. §4.2 Step 6 — ref PATCH (atomic publish)
8. §4.4 보고

## 9. 작업 완료 후 정리

본 지시서는 일회성 (MD-13). 작업 완료 후 다음 파일들이 삭제 대상:

```text
docs/git_g1_rename_task.md      (v1)
docs/git_g1_rename_v2_task.md   (v2)
docs/git_g1_rename_v3_task.md   (v3)
docs/git_g1_rename_v4_task.md   (v4, this file)
```

삭제 시점은 G4 완료 후 일괄 cleanup commit에서 처리.

---

**요청자 노트**: v4는 *codebase_analysis 환경에서 *증명된 능력*을 사용하는 유일한 G1 버전*이다. 모든 이전 버전의 멈춤 원인이 v4에서 *구조적으로* 회피된다:

- v1의 순환 의존성 → v4도 §3.3.2의 "존재 시 갱신" 분리 유지
- v2의 50KB 손상 위험 → plumbing API rename은 *본문 전송 안 함*
- v3의 git clone 차단 → plumbing API는 `api.github.com`만 사용

v4 실행 후에도 멈추면, 그것은 *완전히 새로운 원인*이며 *코드베이스 환경이 GitHub API 자체를 잃은 경우* — 이 시나리오는 이전 commit들이 *증거*로 부인한다.
