# 작업 요청서 — G3: ultimate_goal_eval_task.md 신규 commit (P0 — 평가 I-03)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g3-eval-task-commit |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | git 작업 (new file commit + push) |
| 산출물 | commit SHA 1개, push 완료 |
| 예상 소요 | 15분 |
| 의존성 | **G1 완료 후 진행** (eval_task.md 내부 참조가 새 이름을 가리켜야 함) |

## 2. 작업의 위치

codebase_analysis가 ULTIMATE_GOAL.md v0.1을 외부 평가한 결과, **I-03**이 보고되었습니다:

> `docs/ultimate_goal_eval_task.md`가 공유되었으나 GitHub repo에는 *Not Found*. 즉 T-line이 *작성한* 지시서가 *commit되지 않은* 상태.

본 작업(G3)은 이 파일을 정식으로 commit하여 repo에 등록합니다.

> **주의**: `ultimate_goal_eval_task.md`는 *codebase_analysis가 수행한 평가*의 *지시서*입니다. 즉 이 평가는 *이미 수행되었지만*, 그것을 수행하라고 *지시한 문서*는 commit이 안 된 상태입니다. 본 작업은 *과거 시점의 지시서를 사후 등록*하는 것입니다 — 향후 동일한 평가를 다시 할 때, 또는 평가의 *맥락*을 검증할 때 그 지시서가 repo에 있어야 합니다.

## 3. 입력 자료

T-line 세션이 작성한 파일이 `/mnt/user-data/outputs/ultimate_goal_eval_task.md`에 위치합니다.

G1 완료 후에는 이 파일의 *내부 참조*가 새 이름 (`ULTIMATE_GOAL_v0.1.md`, `GOAL_PROBLEM_v0.1.md`, `reuse_report_v0.1.md`)으로 갱신되어 있어야 합니다 — G1의 sed 작업이 이 파일도 포함합니다.

## 4. 작업 정의

### 4.1. 파일 등록

`docs/ultimate_goal_eval_task.md`가 repo에 이미 존재하는지 확인. 두 가지 경우가 있습니다:

**경우 A**: G1이 이 파일을 *이미 워킹 디렉터리에서 갱신*한 상태로 commit에 포함시킨 경우.
- 그러면 G1 commit에 이미 들어있음. G3는 *무작업*. 그러나 *명시적 보고*는 필요.

**경우 B**: G1이 이 파일을 *접근하지 못한* 경우 (예: 파일이 repo에 없었다면 G1의 for-loop이 `[ -f "$f" ]` 조건에서 빠뜨림).
- T-line이 전달한 파일을 `docs/ultimate_goal_eval_task.md`로 복사
- 별도 commit으로 등록

**판정 방법**:

```bash
git log --oneline -- docs/ultimate_goal_eval_task.md
```

출력이 있으면 경우 A, 없으면 경우 B.

### 4.2. 명령 시퀀스 — 경우 B (대부분의 경우)

```bash
# Pre-check: G1 완료 확인
[ -f docs/ULTIMATE_GOAL_v0.1.md ] || { echo "G1 not done"; exit 1; }

# (1) Check if file already exists in repo
if git log --oneline -- docs/ultimate_goal_eval_task.md | head -1; then
    echo "File already tracked — case A. Report and exit."
    exit 0
fi

# (2) Copy from T-line's output to repo
cp /mnt/user-data/outputs/ultimate_goal_eval_task.md docs/ultimate_goal_eval_task.md

# (3) Apply naming-rule reference updates (in case T-line's copy is pre-G1)
sed -i \
    -e 's/ULTIMATE_GOAL\.md/ULTIMATE_GOAL_v0.1.md/g' \
    -e 's/GOAL_PROBLEM\.md/GOAL_PROBLEM_v0.1.md/g' \
    -e 's/reuse_report\.md/reuse_report_v0.1.md/g' \
    docs/ultimate_goal_eval_task.md

# (4) Verify no leaks
leaks=$(grep -cE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" docs/ultimate_goal_eval_task.md || true)
[ "$leaks" != "0" ] && { echo "leaks: $leaks"; exit 1; }

# (5) Commit
git add docs/ultimate_goal_eval_task.md
git status
git commit -F - <<'EOF'
docs: add ultimate_goal_eval_task.md (closes I-03 from evaluation)

Adds the instruction sheet that drove the external evaluation of
ULTIMATE_GOAL_v0.1.md. The evaluation was performed (its findings
were reported as I-01 through I-05, with P0/P1 priority), but the
instruction document itself was never committed to the repo.

This commit registers the instruction document so that:
  - the evaluation's context can be audited later
  - the same evaluation procedure can be re-run if ULTIMATE_GOAL
    advances to v0.2 or beyond
  - the boundary between T-line (writes instructions) and
    codebase_analysis (executes them) is preserved in repo history

The file follows the instruction-document naming pattern (no _v0.1
suffix, per the naming rule established in G1).

Internal references in this file have been updated to use the new
content-document names from G1.

Closes: I-03 (P0) from the codebase_analysis evaluation of
        ULTIMATE_GOAL_v0.1.md
EOF

# (6) Push
git push origin main

# (7) Report
echo "=== G3 done ==="
git rev-parse HEAD
git log -1 --stat
```

### 4.3. 명령 시퀀스 — 경우 A (드문 경우)

만약 G1이 이미 파일을 포함시켰다면 G3는 *별도 commit이 필요 없습니다*. 단, T-line에 *상태 보고*가 필요합니다:

```bash
echo "G3 case A: file already tracked"
git log --oneline -- docs/ultimate_goal_eval_task.md
echo "No new commit needed."
```

## 5. 산출물 형식

T-line 세션에 다음을 보고:

```text
G3 결과:
  경우:              A (G1에 포함됨) / B (별도 commit)
  commit SHA:        <full SHA, 경우 B인 경우만>
  push 상태:         OK / FAILED / N/A
  내부 참조 갱신:    OK (옛 이름 0건 잔존)
  파일 크기:         약 N줄
```

## 6. 비목표 (Non-goals)

### Case: Type

- **`ultimate_goal_eval_task.md`의 *내용을 수정하지 마라*.** T-line이 작성한 그대로 등록.
- **G1의 작업을 다시 하지 마라.** 내부 참조 sed는 *G1이 이 파일을 접근하지 못한 경우의 백업*일 뿐.
- **`ultimate_goal_eval.md`(평가 *결과* 보고서)를 commit하지 마라.** 그건 별도 작업(evaluation 그 자체). G3는 *지시서*만 다룸.

### Case: State

- **G1 미완료 상태에서 시작하지 마라.** Pre-check 통과 필수.
- **이미 등록된 파일을 *덮어쓰지 마라*.** 경우 A에서는 변경 없이 보고만.

### Case: Performance: Over

- **이 commit에 다른 변경을 포함하지 마라.** *단일 파일 신규 등록* 또는 *상태 보고*만.

## 7. 검증 규칙

산출물이 완료로 간주되려면:

1. **`docs/ultimate_goal_eval_task.md`가 repo에 존재** (경우 A 또는 B 모두)
2. **파일 내부 참조에 옛 이름 0건 잔존**
3. **commit + push 완료** (경우 B) 또는 *경우 A 명시적 보고* (경우 A)
4. **GitHub fetch 결과 `Not Found`가 아님**

## 8. 시작 지시

1. G1 완료 확인
2. 경우 A/B 판정
3. 경우 B면 명령 시퀀스 4.2 실행
4. 경우 A면 4.3 실행
5. T-line에 결과 통보

---

**요청자 노트**: G3는 *가장 단순한 작업*입니다. 위험 거의 없음 — 새 파일 추가는 다른 파일에 영향 없음. 경우 A로 끝날 가능성도 있으므로 *상태 확인*이 본 작업의 핵심.
