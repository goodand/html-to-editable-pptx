# 작업 요청서 — G3 v2: ultimate_goal_eval_task.md 신규 등록 (P0 — 평가 I-03)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g3-eval-task-register (v2) |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | git 작업 (new file commit + push) |
| 산출물 | commit SHA 1개, push 완료 |
| 예상 소요 | 15~30분 |
| 의존성 | **G1 v2 완료 후 진행** |
| 대체 대상 | `docs/git_g3_register_eval_task.md` (v1) |
| 수명 | **본 지시서는 작업 완료 후 삭제 대상** (MD-13: 지시서는 일회성 문서) |

### v2 발행 이유

v1은 G1과의 *책임 분담*이 명시되지 않았다. v1 §4.2에는 sed 갱신이 있었지만, G1도 같은 sed를 적용하려 시도하여 *책임 중복*. 또한 G1 v2가 §3 분리 fix를 적용하면서 *eval_task.md가 G1 시점에 없을 수 있음*을 명시했는데, 그 경우 *eval_task.md의 내부 참조 갱신은 누가 책임지는가*가 v1에서는 모호했다.

v2는 책임을 명시한다: **eval_task.md의 내부 참조 갱신은 G3의 책임**. G1 v2는 *eval_task.md가 이미 있으면 갱신하고, 없으면 skip*. G3 v2는 *eval_task.md를 등록할 때 *처음부터 새 이름으로* 작성*. 어느 시나리오에서도 최종 결과는 *eval_task.md가 새 이름으로 참조함*.

## 2. 작업의 위치

codebase_analysis 평가에서 보고된 **I-03**:

> `docs/ultimate_goal_eval_task.md`가 공유되었으나 GitHub repo에는 *Not Found*. 즉 T-line이 *작성한* 지시서가 *commit되지 않은* 상태.

본 작업(G3 v2)은 이 파일을 정식으로 commit하여 repo에 등록한다.

> **주의**: `ultimate_goal_eval_task.md`는 *codebase_analysis가 수행한 평가*의 *지시서*. 즉 이 평가는 *이미 수행되었지만*, 그것을 수행하라고 *지시한 문서*는 commit이 안 된 상태. 본 작업은 *과거 시점의 지시서를 사후 등록*하는 것 — 향후 동일한 평가를 다시 할 때, 또는 평가의 *맥락*을 검증할 때 그 지시서가 repo에 있어야 함.

## 3. 입력 자료

G1 v2 완료 후 repo 상태:

```text
docs/ULTIMATE_GOAL_v0.1.md       (G1 v2으로 생성됨)
docs/GOAL_PROBLEM_v0.1.md        (G1 v2으로 생성됨)
docs/reuse_report_v0.1.md        (G1 v2으로 생성됨)
docs/architecture_v0.1.md        (이미 존재)
docs/reuse_triage_task_A.md      (G1 v2으로 내부 참조 갱신됨)
docs/ultimate_goal_eval_task.md  (이번 G3 v2에서 등록)
docs/TASK.md                     (아직 갱신 전 — G2 담당)
README.md                        (아직 갱신 전 — G2 담당)
```

T-line 세션이 작성한 `ultimate_goal_eval_task.md` 원본이 별도로 전달된다 (사용자가 `/mnt/user-data/outputs/` 또는 다른 경로로). 이 원본의 *내부 참조 상태*는 G1 시점 이전이므로 *옛 이름을 가리키고 있을 수 있다*.

## 4. 작업 정의

### 4.1. G1 v2와 G3 v2의 책임 분담 — 명시

| 측면 | G1 v2 책임 | G3 v2 책임 |
|---|---|---|
| eval_task.md의 *repo 등록* | 책임 없음 | **책임** — 본 작업의 핵심 |
| eval_task.md의 *내부 참조 갱신* | *존재 시* skip 가능 — `[ -f ]` 가드 | **책임** — 등록 시점에 새 이름으로 작성 |
| eval_task.md가 G1 시점에 *이미 있는 경우* | G1이 sed로 갱신 (선제 적용) | G3는 *case A* 처리 — 등록 확인만 |
| eval_task.md가 G1 시점에 *없는 경우* | G1 skip | G3는 *case B* 처리 — 새로 작성하며 새 이름 적용 |

이 두 시나리오 모두 *최종 상태가 동일*함을 보장한다 — eval_task.md가 repo에 있고 내부 참조가 새 이름.

### 4.2. 파일 등록 — case 판정

```bash
git log --oneline -- docs/ultimate_goal_eval_task.md
```

출력이 있으면 **case A** (G1 v2이 이미 처리), 없으면 **case B** (G3가 신규 등록).

### 4.3. 명령 시퀀스 — case B (대부분의 경우)

```bash
# Pre-check: G1 v2 완료 확인
[ -f docs/ULTIMATE_GOAL_v0.1.md ] || { echo "G1 v2 not done"; exit 1; }
[ ! -f docs/ULTIMATE_GOAL.md ] || { echo "G1 v2 rename incomplete"; exit 1; }

# (1) Check if file already exists in repo
if git log --oneline -- docs/ultimate_goal_eval_task.md | head -1 | grep -q .; then
    echo "File already tracked — case A. Skipping to step (7)."
    git rev-parse HEAD
    echo "G3 v2 case A: no new commit needed."
    exit 0
fi

# (2) Copy from T-line's output to repo
# T-line transmits the file via a known path (user provides)
SOURCE_PATH="${ULTIMATE_GOAL_EVAL_TASK_SOURCE:-/mnt/user-data/outputs/ultimate_goal_eval_task.md}"
if [ ! -f "$SOURCE_PATH" ]; then
    echo "BLOCKER: source file not found at $SOURCE_PATH"
    echo "Set ULTIMATE_GOAL_EVAL_TASK_SOURCE env var or place file at default path."
    exit 1
fi
cp "$SOURCE_PATH" docs/ultimate_goal_eval_task.md

# (3) Apply naming-rule reference updates to the newly placed file.
#     This is G3's explicit responsibility (per §4.1). Even if the source
#     happens to already have new names (because T-line pre-updated it),
#     running sed is idempotent — no harm.
sed -i \
    -e 's/ULTIMATE_GOAL\.md/ULTIMATE_GOAL_v0.1.md/g' \
    -e 's/GOAL_PROBLEM\.md/GOAL_PROBLEM_v0.1.md/g' \
    -e 's/reuse_report\.md/reuse_report_v0.1.md/g' \
    docs/ultimate_goal_eval_task.md

# (4) Verify no leaks
leaks=$(grep -cE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" docs/ultimate_goal_eval_task.md || true)
if [ "$leaks" != "0" ]; then
    echo "leaks: $leaks"
    grep -nE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" docs/ultimate_goal_eval_task.md
    exit 1
fi

# (5) Commit
git add docs/ultimate_goal_eval_task.md
git status
git commit -F - <<'EOF'
docs: add ultimate_goal_eval_task.md (G3 v2, closes I-03)

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
suffix, per the naming rule established in G1 v2).

Internal references use the new content-document names from G1 v2.
This is G3's explicit responsibility per the v2 division of labor
between G1 and G3: G1 v2 handles reference updates in files present
at its execution time; G3 v2 handles them at the registration time
of this file. Either way, the final state has the file in the repo
with new-name references.

Closes: I-03 (P0) from the codebase_analysis evaluation of
        ULTIMATE_GOAL_v0.1.md

Supersedes: docs/git_g3_register_eval_task.md (v1, responsibility
            split with G1 was implicit)
EOF

# (6) Push
git push origin main

# (7) Report
echo "=== G3 v2 done ==="
git rev-parse HEAD
git log -1 --stat
```

### 4.4. 명령 시퀀스 — case A (드문 경우)

만약 G1 v2가 *이미 파일을 포함시켰다면* G3 v2는 별도 commit이 필요 없다:

```bash
echo "G3 v2 case A: file already tracked by G1 v2"
git log --oneline -- docs/ultimate_goal_eval_task.md
echo "No new commit needed."
```

그러나 case A에서도 *T-line에 명시적 보고*는 필수.

## 5. 산출물 형식

T-line 세션에 다음을 보고:

```text
G3 v2 결과:
  경우:              A (G1 v2에 포함됨) / B (별도 commit)
  commit SHA:        <full SHA, 경우 B인 경우만>
  push 상태:         OK / FAILED / N/A
  내부 참조 갱신:    OK (옛 이름 0건 잔존)
  파일 크기:         약 N줄
```

## 6. 비목표 (Non-goals)

### Case: Type

- **`ultimate_goal_eval_task.md`의 *내용을 수정하지 마라*.** T-line이 작성한 그대로 등록. *내부 참조 갱신* 외의 변경 금지.
- **G1 v2의 작업을 다시 하지 마라.** 다른 파일(ULTIMATE_GOAL_v0.1.md 등)의 참조는 *G1 v2의 책임*.
- **`ultimate_goal_eval.md`(평가 *결과* 보고서)를 commit하지 마라.** 그건 별도 작업.

### Case: State

- **G1 v2 미완료 상태에서 시작하지 마라.** Pre-check 통과 필수.
- **이미 등록된 파일을 *덮어쓰지 마라*.** Case A에서는 변경 없이 보고만.
- **소스 파일 경로 부재 시 BLOCKER.** Case B에서 *T-line이 전달한 원본*이 지정된 경로에 없으면 멈춤 + 보고.

### Case: Performance: Over

- **이 commit에 다른 변경을 포함하지 마라.** *단일 파일 신규 등록* 또는 *상태 보고*만.

## 7. 검증 규칙

산출물이 완료로 간주되려면:

1. **`docs/ultimate_goal_eval_task.md`가 repo에 존재** (case A 또는 B 모두)
2. **파일 내부 참조에 옛 이름 0건 잔존**
3. **commit + push 완료** (case B) 또는 *case A 명시적 보고* (case A)
4. **GitHub fetch 결과 `Not Found`가 아님**

## 8. 시작 지시

1. G1 v2 완료 확인 (pre-check)
2. case A/B 판정 (§4.2)
3. case B면 명령 시퀀스 §4.3 실행
4. case A면 §4.4 실행
5. T-line에 결과 통보

## 9. 작업 완료 후 정리

본 지시서는 **일회성 문서** (MD-13). 작업 완료 후 다음 두 파일이 삭제 대상:

```text
docs/git_g3_register_eval_task.md     (v1, superseded)
docs/git_g3_register_eval_v2_task.md  (v2, this file, executed)
```

삭제 시점은 G4 완료 후 일괄 cleanup commit에서 처리.

---

**요청자 노트**: G3 v2는 *책임 분담 명시*가 v1 대비 핵심 차이. 명령 시퀀스 자체는 v1과 거의 동일하지만, §4.1의 *G1과의 책임 분담표*가 추가되어 *어느 시나리오에서도 안전한 진행*이 보장된다. case A로 끝날 가능성도 있으므로 *상태 확인*이 본 작업의 첫 번째 책임.
