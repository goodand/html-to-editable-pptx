# 작업 요청서 — G1: 파일명 규칙 적용 (내용 문서 rename + 내부 참조 갱신)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g1-rename |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | git 작업 (rename + content update + commit + push) |
| 산출물 | commit SHA 1개, push 완료 |
| 예상 소요 | 30분~1시간 |
| 의존성 | 없음 — 가장 먼저 실행 |

## 2. 작업의 위치

T-line 세션의 인터뷰에서 사용자가 확정한 *파일명 규칙*은 다음과 같습니다:

- **규칙**: 내용 문서는 `_vx.x.md` suffix를 사용
- **소급 적용 범위 (β)**: 모든 내용 문서에 적용. 지시서와 도구 문서(README.md)는 제외
- **사용자의 명시적 동의**: ULTIMATE_GOAL.md 이름 변경 포함 (MD-4 위반 아님 — 내용 보존)

본 작업(G1)은 *이 규칙을 실제 repository에 반영*하는 것입니다. G2/G3/G4는 G1 완료 후 진행됩니다.

## 3. 입력 자료

repo 루트에 있어야 할 파일:

```text
docs/ULTIMATE_GOAL.md
docs/GOAL_PROBLEM.md
docs/reuse_report.md
docs/architecture_v0.1.md
docs/reuse_triage_task_A.md
docs/ultimate_goal_eval_task.md
docs/TASK.md
README.md
```

T-line 세션이 이미 작성한 *부분 갱신본*이 별도로 전달됩니다 (`/mnt/user-data/outputs/`에 위치). 그러나 G1은 *codebase_analysis가 직접 sed 작업*을 수행하는 것이 더 안전합니다 — repo의 정확한 현재 상태를 기준으로.

## 4. 작업 정의

### 4.1. 분류표 — 이름 변경 대상

| 현재 파일 | 분류 | 작업 |
|---|---|---|
| `docs/ULTIMATE_GOAL.md` | 내용 문서 | → `docs/ULTIMATE_GOAL_v0.1.md` |
| `docs/GOAL_PROBLEM.md` | 내용 문서 | → `docs/GOAL_PROBLEM_v0.1.md` |
| `docs/reuse_report.md` | 내용 문서 | → `docs/reuse_report_v0.1.md` |
| `docs/architecture_v0.1.md` | 내용 문서 (이미 규칙 따름) | 변경 없음 |
| `docs/reuse_triage_task_A.md` | 지시서 | 이름 유지 (단, 내부 참조 갱신 필요) |
| `docs/ultimate_goal_eval_task.md` | 지시서 | 이름 유지 (단, 내부 참조 갱신 필요) |
| `docs/TASK.md` | 지시서 | 이름 유지 (G2가 처리) |
| `README.md` | 도구 문서 | 이름 유지 (G2가 처리) |

### 4.2. 명령 시퀀스

```bash
# (1) Rename three content documents using git mv (preserves history)
git mv docs/ULTIMATE_GOAL.md docs/ULTIMATE_GOAL_v0.1.md
git mv docs/GOAL_PROBLEM.md  docs/GOAL_PROBLEM_v0.1.md
git mv docs/reuse_report.md  docs/reuse_report_v0.1.md

# (2) Update internal references inside renamed files and other affected docs
#     The substitution pattern is safe because new names contain "_v0.1.md"
#     which does NOT match the old ".md" pattern.
for f in docs/ULTIMATE_GOAL_v0.1.md \
         docs/GOAL_PROBLEM_v0.1.md \
         docs/reuse_report_v0.1.md \
         docs/architecture_v0.1.md \
         docs/reuse_triage_task_A.md \
         docs/ultimate_goal_eval_task.md; do
    [ -f "$f" ] && sed -i \
        -e 's/ULTIMATE_GOAL\.md/ULTIMATE_GOAL_v0.1.md/g' \
        -e 's/GOAL_PROBLEM\.md/GOAL_PROBLEM_v0.1.md/g' \
        -e 's/reuse_report\.md/reuse_report_v0.1.md/g' \
        "$f"
done

# (3) Verify no old name leaks remain in the touched files
for f in docs/ULTIMATE_GOAL_v0.1.md \
         docs/GOAL_PROBLEM_v0.1.md \
         docs/reuse_report_v0.1.md \
         docs/architecture_v0.1.md \
         docs/reuse_triage_task_A.md \
         docs/ultimate_goal_eval_task.md; do
    leaks=$(grep -cE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" "$f" || true)
    [ "$leaks" != "0" ] && echo "WARN: $f has $leaks leak(s)" && grep -nE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" "$f"
done

# (4) Verify YAML in ULTIMATE_GOAL_v0.1.md still parses
python3 -c "
import yaml, re, sys
content = open('docs/ULTIMATE_GOAL_v0.1.md').read()
m = re.search(r'\`\`\`yaml\n(.+?)\n\`\`\`', content, re.DOTALL)
if not m: sys.exit('YAML block missing')
data = yaml.safe_load(m.group(1))
assert data['document']['name'] == 'ULTIMATE_GOAL_v0.1.md', data['document']['name']
expected_keys = {'GOAL_PROBLEM_v0.1.md', 'architecture_v0.1.md', 'reuse_report_v0.1.md', 'reuse_triage_task_A.md', 'TASK.md'}
actual_keys = set(data['related_documents'].keys())
assert expected_keys == actual_keys, f'Expected {expected_keys}, got {actual_keys}'
print('YAML OK')
"

# (5) Stage and commit
git add docs/
git status  # human-readable check
git commit -F - <<'EOF'
docs: apply file-naming rule _v0.1.md to content documents

Per the T-line interview decision (file-naming convention: content
documents use _vx.x.md suffix; instruction documents and tool
documents are exempt), rename and update internal references across
content documents.

Renames:
  docs/ULTIMATE_GOAL.md  -> docs/ULTIMATE_GOAL_v0.1.md
  docs/GOAL_PROBLEM.md   -> docs/GOAL_PROBLEM_v0.1.md
  docs/reuse_report.md   -> docs/reuse_report_v0.1.md

Internal-reference updates applied via sed across:
  docs/ULTIMATE_GOAL_v0.1.md
  docs/GOAL_PROBLEM_v0.1.md
  docs/reuse_report_v0.1.md
  docs/architecture_v0.1.md  (if any old-name refs were present)
  docs/reuse_triage_task_A.md
  docs/ultimate_goal_eval_task.md

Exempt from this commit (per the rule):
  README.md                       (tool document — mass audience)
  docs/TASK.md                    (instruction document)
  docs/reuse_triage_task_A.md     (instruction; name kept; refs updated)
  docs/ultimate_goal_eval_task.md (instruction; name kept; refs updated)

Reasoning for the rule:
  - MD-1 (cross-reference graph): consistent naming makes the graph
    of inter-document references stable and auditable.
  - MD-9 (boundary clarity for agents): a reference unambiguously
    tells the reader which version of a document is being cited.

Future enforcement: the rule is intended to be enforced by a
linter-like automated tool. The linter spec is a separate
follow-up deliverable (per MD-6, actual implementation belongs to
codebase_analysis, not T-line).

YAML validity preserved:
  ULTIMATE_GOAL_v0.1.md YAML re-parsed cleanly. document.name and
  related_documents keys reflect the new names.

Out of scope for this commit (handled by G2/G3/G4):
  G2: README.md and TASK.md content updates
      (codebase_analysis evaluation I-01, I-02 / P0)
  G3: ultimate_goal_eval_task.md initial commit if not already present
      (evaluation I-03 / P0)
  G4: reuse_triage_task_A.md scope clarification, architecture_v0.1.md
      Media Candidate note, GOAL_PROBLEM_v0.1.md self-assessment link
      (evaluation I-04, I-05, P1)

MD-4 (user-consent-required for ULTIMATE_GOAL modification):
  User explicitly approved the rename via interview answer (a)
  to the "(β) — apply rule to content documents, including
  ULTIMATE_GOAL.md" question. Content is preserved; no semantic
  modification was made.
EOF

# (6) Push
git push origin main  # or whichever branch is canonical

# (7) Report
echo "=== G1 done ==="
git rev-parse HEAD
git log -1 --stat
```

## 5. 산출물 형식

T-line 세션에 다음을 보고:

```text
G1 결과:
  commit SHA:      <full SHA>
  push 상태:       OK / FAILED
  rename 3건:      OK
  내부 참조 갱신:   N건 (몇 곳이 바뀌었는지)
  YAML 검증:       OK / FAILED
  옛 이름 잔존:    0건 / N건 (있다면 어디인지)
```

## 6. 비목표 (Non-goals)

### Case: Type

- **G2/G3/G4의 작업을 G1에 포함하지 마라.** README.md, TASK.md는 본 작업 범위 밖.
- **새로운 .md 파일을 만들지 마라.** 본 작업은 *기존 파일의 rename + 참조 갱신*만.
- **콘텐츠 의미를 바꾸지 마라.** sed 패턴은 *파일 경로 참조*만 갱신. 산문의 *의미 변경*은 없어야 함.

### Case: State

- **rename 실패 시 *부분 적용된 상태로 commit하지 마라*.** rollback (`git restore --staged .`, `git checkout -- docs/`) 후 보고.
- **YAML 검증 실패 시 commit 금지.** YAML이 깨지면 *ULTIMATE_GOAL_v0.1.md의 합의 보존* 기능이 손상됨.

### Case: Performance: Over

- **추가 정리 작업을 하지 마라.** 발견되는 *다른 불일치*(예: 오타, 포맷 차이)는 G2/G3/G4 또는 별도 작업으로 미룸.

## 7. 검증 규칙

산출물이 완료로 간주되려면:

1. **3개 파일이 새 이름으로 존재**: `docs/ULTIMATE_GOAL_v0.1.md`, `docs/GOAL_PROBLEM_v0.1.md`, `docs/reuse_report_v0.1.md`
2. **옛 이름 3개가 더 이상 존재하지 않음**: `docs/ULTIMATE_GOAL.md`, `docs/GOAL_PROBLEM.md`, `docs/reuse_report.md`
3. **6개 touched 파일에 옛 이름 0건 잔존** (위 명령 시퀀스의 step 3에서 검증)
4. **`ULTIMATE_GOAL_v0.1.md`의 YAML 블록이 파싱 가능** (step 4에서 검증)
5. **commit + push 완료**: GitHub에서 새 commit 확인 가능

## 8. 시작 지시

1. 위 명령 시퀀스를 *순서대로* 실행
2. 각 step의 출력을 기록
3. 실패 시 *어느 step에서 실패했는지* 보고
4. 성공 시 commit SHA를 T-line에 통보

---

**요청자 노트**: G1은 *기계적 작업*입니다. 의사결정이 필요한 부분은 *없음* — 모든 결정이 이미 T-line 인터뷰에서 확정되었습니다. codebase_analysis는 *명령 시퀀스를 정확히 실행하고 결과를 보고*하면 됩니다.