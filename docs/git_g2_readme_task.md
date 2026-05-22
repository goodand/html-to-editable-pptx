# 작업 요청서 — G2: README.md 및 TASK.md 갱신 (P0 — 평가 I-01, I-02)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g2-readme-task |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | git 작업 (content update + commit + push) |
| 산출물 | commit SHA 1개 (또는 2개 — 4.4 참조), push 완료 |
| 예상 소요 | 1~2시간 |
| 의존성 | **G1 완료 후 진행** |

## 2. 작업의 위치

codebase_analysis가 ULTIMATE_GOAL.md v0.1을 외부 평가한 결과 (`ultimate_goal_eval_task.md`의 산출물에 해당), 다음 두 가지 P0 발견이 보고되었습니다:

- **I-01**: `TASK.md`가 `docs/architecture.md`를 요구하지만 실제 파일은 `docs/architecture_v0.1.md`. 경로 불일치.
- **I-02**: `README.md`가 `docs/ULTIMATE_GOAL_v0.1.md`를 안내하지 않음. 최상위 문서가 진입점에서 누락.

본 작업(G2)은 이 두 발견을 정리합니다. G1이 새 파일명을 확정한 뒤에야 가능합니다 (G1에서 생긴 `_v0.1.md` 이름들을 참조해야 하므로).

## 3. 입력 자료

G1 완료 후 repo 상태:

```text
docs/ULTIMATE_GOAL_v0.1.md       (G1으로 생성됨)
docs/GOAL_PROBLEM_v0.1.md        (G1으로 생성됨)
docs/reuse_report_v0.1.md        (G1으로 생성됨)
docs/architecture_v0.1.md        (이미 존재)
docs/reuse_triage_task_A.md      (G1으로 내부 참조 갱신됨)
docs/ultimate_goal_eval_task.md  (G1으로 내부 참조 갱신됨, 또는 G3에서 신규 생성)
docs/TASK.md                     (이번 G2에서 갱신)
README.md                        (이번 G2에서 갱신)
```

## 4. 작업 정의

### 4.1. TASK.md 갱신 — I-01 해결

**현재 상태** (T-line이 fetch한 GitHub 상태 기준):

```markdown
Then read the cloned repositories and write:

- docs/reuse_report.md
- docs/architecture.md
- docs/deletion_candidates.md
```

**갱신 후**:

```markdown
Then read the cloned repositories and write:

- docs/reuse_report_v0.1.md
- docs/architecture_v0.1.md
- docs/deletion_candidates_v0.1.md
```

**갱신 규칙**:
- `docs/reuse_report.md` → `docs/reuse_report_v0.1.md` (G1으로 이미 존재)
- `docs/architecture.md` → `docs/architecture_v0.1.md` (이미 존재. 이름 변경 없이 *참조만 갱신*)
- `docs/deletion_candidates.md` → `docs/deletion_candidates_v0.1.md` (아직 미존재. *향후 만들 때* 새 규칙 따름을 명시)

placeholder 항목 (`src/ir/schema.ts`, `src/extract/README.md` 등)은 변경 없음 — 코드 파일이므로 파일명 규칙 비대상.

### 4.2. README.md 갱신 — I-02 해결

**필요 변경 2가지**:

#### 4.2.1. 상단 intro에 ULTIMATE_GOAL 안내 추가

README.md의 *프로젝트 소개* 직후 (현재 *"For the concrete problem definition..."* 단락 *앞*에) 다음 단락 추가:

```markdown
For the top-level purpose of the project — what end the technical
work is intended to serve — read:

```text
docs/ULTIMATE_GOAL_v0.1.md
```

For the concrete problem definition...
```

#### 4.2.2. "Important files" 목록 갱신

현재 목록:

```text
README.md
docs/GOAL_PROBLEM.md
scripts/clone_repos.sh
scripts/clone_repos_from_toml.py
third_party/repositories.toml
third_party/manifests/*.toml
docs/TASK.md
```

갱신 후:

```text
README.md
docs/ULTIMATE_GOAL_v0.1.md
docs/GOAL_PROBLEM_v0.1.md
docs/architecture_v0.1.md
docs/reuse_report_v0.1.md
scripts/clone_repos.sh
scripts/clone_repos_from_toml.py
third_party/repositories.toml
third_party/manifests/*.toml
docs/TASK.md
```

추가된 3개: `ULTIMATE_GOAL_v0.1.md`, `architecture_v0.1.md`, `reuse_report_v0.1.md`.

`GOAL_PROBLEM.md` → `GOAL_PROBLEM_v0.1.md` 치환 1건.

### 4.3. README.md의 다른 옛 이름 참조 일괄 갱신

README.md 본문 어디든 `GOAL_PROBLEM.md` 등 옛 이름이 등장하면 새 이름으로 갱신:

```bash
sed -i \
    -e 's/GOAL_PROBLEM\.md/GOAL_PROBLEM_v0.1.md/g' \
    -e 's/reuse_report\.md/reuse_report_v0.1.md/g' \
    -e 's/ULTIMATE_GOAL\.md/ULTIMATE_GOAL_v0.1.md/g' \
    README.md
```

이전과 동일하게 `_v0.1.md`는 다시 매치되지 않으므로 안전.

### 4.4. 커밋 분리 결정

I-01 (TASK.md)과 I-02 (README.md)를 **1개 commit으로 묶을지** **2개로 분리할지** 결정 사항입니다. 

**권장**: 1개 commit. 이유:
- 두 변경 모두 *codebase_analysis 평가의 P0*에서 출발
- 두 변경 모두 *G1이 만든 새 이름을 참조*하는 것
- 단일 책임 원칙은 *결정의 출처*를 기준으로 보면 *외부 평가의 P0*라는 같은 출처
- 분리 시 commit 메시지가 거의 동일 — 중복 부담

### 4.5. 명령 시퀀스

```bash
# Pre-check: G1 이 완료되었는지 확인
[ -f docs/ULTIMATE_GOAL_v0.1.md ] || { echo "G1 not done"; exit 1; }
[ ! -f docs/ULTIMATE_GOAL.md ] || { echo "G1 rename incomplete"; exit 1; }

# (1) TASK.md 갱신
# Manual edit recommended (multi-line block). Use editor or here-doc.
# After edit, verify:
grep -E "architecture\.md|reuse_report\.md|deletion_candidates\.md" docs/TASK.md
# Should match either zero occurrences, or only _v0.1.md / _v0.1 patterns.

# (2) README.md 갱신
# 4.2.1: Add intro paragraph (manual edit)
# 4.2.2: Update Important files list (manual edit)
# 4.3:   Sed substitution
sed -i \
    -e 's/GOAL_PROBLEM\.md/GOAL_PROBLEM_v0.1.md/g' \
    -e 's/reuse_report\.md/reuse_report_v0.1.md/g' \
    -e 's/ULTIMATE_GOAL\.md/ULTIMATE_GOAL_v0.1.md/g' \
    README.md

# (3) Verify no old-name leaks
for f in README.md docs/TASK.md; do
    leaks=$(grep -cE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" "$f" || true)
    echo "$f: $leaks leak(s)"
done

# (4) Commit
git add README.md docs/TASK.md
git status
git commit -F - <<'EOF'
docs: update README and TASK to reflect new file naming and add ULTIMATE_GOAL entry

Closes two P0 findings from the codebase_analysis evaluation of
ULTIMATE_GOAL_v0.1.md:

  I-01 (TASK.md path conflict):
    TASK.md required docs/architecture.md as a deliverable, but the
    actual file is docs/architecture_v0.1.md (per the naming rule
    established in G1). Updates the path references in the task list:
      docs/reuse_report.md       -> docs/reuse_report_v0.1.md
      docs/architecture.md       -> docs/architecture_v0.1.md
      docs/deletion_candidates.md -> docs/deletion_candidates_v0.1.md
    Placeholder code files (src/*) are unchanged — code files are not
    subject to the naming rule.

  I-02 (README missing ULTIMATE_GOAL entry):
    README did not introduce ULTIMATE_GOAL_v0.1.md to readers. Adds
    a paragraph linking to the top-level purpose document immediately
    before the existing problem-definition link, and adds three
    content documents to the "Important files" list:
      docs/ULTIMATE_GOAL_v0.1.md
      docs/architecture_v0.1.md
      docs/reuse_report_v0.1.md
    Also normalizes any remaining old-name references (GOAL_PROBLEM.md,
    reuse_report.md, ULTIMATE_GOAL.md) to their _v0.1.md equivalents
    via sed.

Reasoning:
  README is the entry point for general audience (per MD-5 reader
  separation: README serves the mass audience, ULTIMATE_GOAL serves
  agents and the user during retrospection). Adding the link to
  ULTIMATE_GOAL preserves the abstraction layering while pointing
  curious readers to the top-level purpose document.

  TASK.md is an instruction document (exempt from the _v0.1.md naming
  rule), but its *references* to content documents must use the new
  names per the naming rule. The instruction itself remains under
  the name TASK.md.

Out of scope:
  G3: ultimate_goal_eval_task.md commit (separate task)
  G4: reuse_triage_task_A.md scope clarification, architecture_v0.1.md
      Media Candidate note, GOAL_PROBLEM_v0.1.md self-assessment link
EOF

# (5) Push
git push origin main

# (6) Report
echo "=== G2 done ==="
git rev-parse HEAD
git log -1 --stat
```

## 5. 산출물 형식

T-line 세션에 다음을 보고:

```text
G2 결과:
  commit SHA:        <full SHA>
  push 상태:         OK / FAILED
  TASK.md 갱신:      OK (옛 이름 0건 잔존)
  README.md 갱신:    OK (intro 단락 추가, Important files 3개 추가)
  옛 이름 잔존:      0건 / N건
```

## 6. 비목표 (Non-goals)

### Case: Type

- **G1, G3, G4의 작업을 G2에 포함하지 마라.**
- **README.md의 *다른 부분*을 손대지 마라.** 예: 프로젝트 설명 톤, 예시 명령, third-party 매니페스트 안내 등은 *현재 형태 유지*. I-02가 요구한 *두 가지 변경*만 적용.
- **TASK.md의 placeholder 코드 파일 항목을 손대지 마라.** `src/ir/schema.ts` 등은 *코드 파일*. 파일명 규칙 비대상.

### Case: State

- **G1이 완료되지 않은 상태에서 G2를 시작하지 마라.** 명령 시퀀스의 pre-check를 반드시 통과.
- **README.md의 *intro 단락 추가*가 실패하면 commit하지 마라.** 잘못된 위치에 단락이 들어가면 *진입점이 더 혼란*해짐.

### Case: Performance: Over

- **README.md를 *전면 재작성하지 마라*.** I-02의 두 가지 명시적 요구사항만 적용.
- **TASK.md의 *내용을 확장하지 마라*.** 경로 갱신만.

## 7. 검증 규칙

산출물이 완료로 간주되려면:

1. **TASK.md에 `architecture.md`, `reuse_report.md`, `deletion_candidates.md` (옛 이름) 0건 잔존**
2. **README.md에 `ULTIMATE_GOAL_v0.1.md` 링크가 *intro 위치에* 등장**
3. **README.md의 "Important files" 목록에 3개 새 항목 등장**: `ULTIMATE_GOAL_v0.1.md`, `architecture_v0.1.md`, `reuse_report_v0.1.md`
4. **README.md에 옛 이름 0건 잔존**
5. **commit + push 완료**

## 8. 시작 지시

1. G1 완료 확인 (pre-check)
2. TASK.md 수동 편집 (4.1)
3. README.md 수동 편집 (4.2.1, 4.2.2)
4. README.md sed 일괄 갱신 (4.3)
5. 검증 step 실행
6. commit + push
7. T-line에 SHA 통보

---

**요청자 노트**: G2는 *기계적 + 약간의 편집 판단*을 요합니다. 4.2.1의 intro 단락 위치, 4.2.2의 Important files 순서는 *기존 README의 흐름과 어울리도록* codebase_analysis가 판단. 단, *I-02가 요구한 두 가지 변경* 외의 *재구성*은 비목표.
