# 작업 요청서 — G1 v3: 파일명 규칙 적용 (git clone 환경 명시)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g1-rename (v3) |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | git 작업 (rename + content update + commit + push) |
| **필수 환경** | **로컬 git clone 환경** (`git mv`, `sed`, `git diff` 실행 가능) |
| 산출물 | commit SHA 1개, push 완료 |
| 예상 소요 | 30분 |
| 의존성 | 없음 — 가장 먼저 실행 |
| 대체 대상 | `docs/git_g1_rename_task.md` (v1), `docs/git_g1_rename_v2_task.md` (v2) |
| 수명 | **본 지시서는 작업 완료 후 삭제 대상** (MD-13) |

### v3 발행 이유

v2는 codebase_analysis 실행 시 멈췄다. 멈춤의 이유:

> *"docs/reuse_report.md 전체를 무손실로 재작성할 수단이 현재 세션의 원격 GitHub 도구 조합에서는 안정적으로 확보되지 않음."*

이는 **codebase_analysis가 v2를 *원격 GitHub Contents API*로 실행하려 했고, 50KB의 `reuse_report.md`를 PUT으로 다시 쓰는 과정의 손상 위험을 회피하여 멈췄음**을 의미한다. 외부 평가에 따르면 이 멈춤은 정당한 *부분 성공 commit 금지* 판단이었다.

v3의 핵심 변경:

1. **§1에 필수 환경을 명시**: 로컬 git clone 환경. Contents API 환경에서는 실행 금지.
2. **§3에 환경 사전 검증 단계 추가**: 도구 가용성을 먼저 확인하고, 부재 시 즉시 보고하고 멈춤.
3. **§4에 백업과 diff 검증 단계 추가**: 큰 파일의 손상을 *작업 중에 발견*할 수 있도록.
4. **§6에 폴백 지시 명시**: 환경이 안 맞으면 codebase_analysis가 *자체 폴백 시도 금지*. T-line에 보고하고 멈춤.

v3은 외부 평가 보고서의 7가지 안전 원칙을 모두 반영한다:
1) 큰 문서는 contents API로 재작성하지 말 것
2) "필수 존재" vs "있으면 갱신" 분리 (v2에서 이미 적용)
3) 변경 전 스냅샷
4) 치환 후 검증 규칙
5) 브랜치에서 diff 확인 후 merge
6) 라인 수 / 구조 검증
7) 부분 성공 commit 금지

## 2. 작업의 위치

T-line 세션의 인터뷰에서 사용자가 확정한 *파일명 규칙*:

- **규칙**: 내용 문서는 `_vx.x.md` suffix를 사용
- **소급 적용 범위 (β)**: 모든 내용 문서에 적용. 지시서와 도구 문서(README.md)는 제외
- **사용자의 명시적 동의**: ULTIMATE_GOAL.md 이름 변경 포함

본 작업(G1)은 이 규칙을 실제 repository에 반영한다. G2/G3/G4는 G1 v3 완료 후 진행한다.

## 3. 필수 환경 검증

### 3.1. 환경 요구사항

본 지시서는 **로컬 git clone 환경**에서 실행되어야 한다. 다음 도구가 모두 가용해야 한다:

```text
git    (clone, mv, diff, add, commit, push)
sed    (in-place 치환)
grep   (검증)
python3 + PyYAML  (YAML 파싱 검증)
wc     (라인 수 검증)
```

GitHub Contents API만 가용한 환경에서는 본 작업을 **시작하지 마라**. 이유: 50KB의 `reuse_report.md`를 PUT으로 다시 쓰는 과정에서 *전체 본문 손상 위험*. 외부 평가에서 이미 검증된 정당한 멈춤 사유.

### 3.2. 환경 사전 검증 — pre-flight check

다음 명령으로 환경을 검증한다. 하나라도 실패하면 §6 Non-goals의 환경 부재 폴백 규칙으로.

```bash
# Required tools availability
command -v git    >/dev/null || { echo "BLOCKER: git not available"; exit 2; }
command -v sed    >/dev/null || { echo "BLOCKER: sed not available"; exit 2; }
command -v grep   >/dev/null || { echo "BLOCKER: grep not available"; exit 2; }
command -v wc     >/dev/null || { echo "BLOCKER: wc not available"; exit 2; }
python3 -c "import yaml" 2>/dev/null || { echo "BLOCKER: python3+yaml not available"; exit 2; }

# Repo is a git work tree
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
    echo "BLOCKER: not inside a git work tree. Clone the repo first."
    exit 2
}

# Network reachability for push (optional check, can be skipped if known)
git ls-remote --exit-code origin >/dev/null 2>&1 || {
    echo "WARN: cannot reach origin. push step will fail if this persists."
}

echo "Pre-flight OK"
```

### 3.3. 입력 자료 — 두 그룹 (v2와 동일)

#### 3.3.1. 존재 필수 (rename 대상)

```text
docs/ULTIMATE_GOAL.md    -> docs/ULTIMATE_GOAL_v0.1.md
docs/GOAL_PROBLEM.md     -> docs/GOAL_PROBLEM_v0.1.md
docs/reuse_report.md     -> docs/reuse_report_v0.1.md
```

#### 3.3.2. 존재 시 갱신 (참조 갱신 대상)

```text
docs/architecture_v0.1.md
docs/reuse_triage_task_A.md
docs/ultimate_goal_eval_task.md   (G3 산출물, G1 v3 시점에는 없을 수 있음)
```

부재 파일은 *skip*. 없어도 G1 v3 진행 가능.

## 4. 작업 정의

### 4.1. 백업 — 변경 전 스냅샷

외부 평가 권고: *"변경 전 스냅샷을 남기고 시작"*. 손상 시 복구 비용 최소화.

```bash
# (B1) Create a backup branch pointing at current HEAD
git branch backup/pre-g1 || git branch -f backup/pre-g1

# (B2) Save copies of the three rename targets to /tmp
cp docs/ULTIMATE_GOAL.md /tmp/ULTIMATE_GOAL.md.bak
cp docs/GOAL_PROBLEM.md  /tmp/GOAL_PROBLEM.md.bak
cp docs/reuse_report.md  /tmp/reuse_report.md.bak

# (B3) Record line counts and content hashes for post-change verification
sha256sum docs/ULTIMATE_GOAL.md docs/GOAL_PROBLEM.md docs/reuse_report.md > /tmp/g1-pre-hashes.txt
wc -l    docs/ULTIMATE_GOAL.md docs/GOAL_PROBLEM.md docs/reuse_report.md > /tmp/g1-pre-linecounts.txt
echo "=== Pre-change state ==="
cat /tmp/g1-pre-hashes.txt
cat /tmp/g1-pre-linecounts.txt
```

### 4.2. 작업 브랜치 생성 — diff 검증 가능 환경

외부 평가 권고: *"한 번에 main에 직접 쓰지 말고, 브랜치에서 diff 확인 후 merge"*.

```bash
git checkout -b chore/g1-rename-v3
```

### 4.3. Rename + 참조 갱신

```bash
# (1) Rename three content documents
git mv docs/ULTIMATE_GOAL.md docs/ULTIMATE_GOAL_v0.1.md
git mv docs/GOAL_PROBLEM.md  docs/GOAL_PROBLEM_v0.1.md
git mv docs/reuse_report.md  docs/reuse_report_v0.1.md

# (2) Update internal references via sed (in-place, byte-safe)
# The [ -f "$f" ] guard intentionally allows §3.3.2 files to be absent.
for f in docs/ULTIMATE_GOAL_v0.1.md \
         docs/GOAL_PROBLEM_v0.1.md \
         docs/reuse_report_v0.1.md \
         docs/architecture_v0.1.md \
         docs/reuse_triage_task_A.md \
         docs/ultimate_goal_eval_task.md; do
    if [ -f "$f" ]; then
        sed -i \
            -e 's/ULTIMATE_GOAL\.md/ULTIMATE_GOAL_v0.1.md/g' \
            -e 's/GOAL_PROBLEM\.md/GOAL_PROBLEM_v0.1.md/g' \
            -e 's/reuse_report\.md/reuse_report_v0.1.md/g' \
            "$f"
    else
        echo "skip (file absent): $f"
    fi
done
```

### 4.4. 검증 — 구조 보존 검사

외부 평가 권고: *"큰 문서는 라인 수 / 해시 / 구조를 같이 검증"*.

```bash
# (V1) Post-change line counts
wc -l docs/ULTIMATE_GOAL_v0.1.md docs/GOAL_PROBLEM_v0.1.md docs/reuse_report_v0.1.md > /tmp/g1-post-linecounts.txt
echo "=== Line count change ==="
paste /tmp/g1-pre-linecounts.txt /tmp/g1-post-linecounts.txt
# Sanity: line counts must be identical (rename + sed of single-line refs ≠ structural change)
# If sed altered line count, that signals damage.

# (V2) Markdown heading structure preserved
echo "=== Heading structure: reuse_report_v0.1.md ==="
grep -c "^## " docs/reuse_report_v0.1.md
grep "^## P1\." docs/reuse_report_v0.1.md  # 6 P1 sections expected
echo "=== Heading structure: ULTIMATE_GOAL_v0.1.md ==="
grep -n "^##" docs/ULTIMATE_GOAL_v0.1.md  # 8 sections + YAML subsection expected
echo "=== Heading structure: GOAL_PROBLEM_v0.1.md ==="
grep -c "^## " docs/GOAL_PROBLEM_v0.1.md

# (V3) Old-name leaks check
echo "=== Leak check ==="
for f in docs/ULTIMATE_GOAL_v0.1.md \
         docs/GOAL_PROBLEM_v0.1.md \
         docs/reuse_report_v0.1.md \
         docs/architecture_v0.1.md \
         docs/reuse_triage_task_A.md \
         docs/ultimate_goal_eval_task.md; do
    if [ -f "$f" ]; then
        leaks=$(grep -cE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" "$f" 2>/dev/null || true)
        if [ "$leaks" != "0" ]; then
            echo "FAIL: $f has $leaks leak(s)"
            grep -nE "(^|[^v0-9.])(ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report)\.md" "$f"
            echo "Roll back and abort:"
            echo "  git checkout main && git branch -D chore/g1-rename-v3"
            exit 1
        fi
    fi
done

# (V4) YAML parses
python3 -c "
import yaml, re, sys
content = open('docs/ULTIMATE_GOAL_v0.1.md').read()
m = re.search(r'\`\`\`yaml\n(.+?)\n\`\`\`', content, re.DOTALL)
if not m: sys.exit('FAIL: YAML block missing')
data = yaml.safe_load(m.group(1))
assert data['document']['name'] == 'ULTIMATE_GOAL_v0.1.md', f'document.name mismatch: {data["document"]["name"]}'
expected = {'GOAL_PROBLEM_v0.1.md', 'architecture_v0.1.md', 'reuse_report_v0.1.md', 'reuse_triage_task_A.md', 'TASK.md'}
actual = set(data['related_documents'].keys())
assert expected == actual, f'related_documents mismatch: expected {expected}, got {actual}'
print('YAML OK')
"
```

### 4.5. 수동 diff 검토

외부 평가 권고: *"git diff --word-diff도 좋습니다"*. 큰 파일의 의도 외 변경을 사람의 눈으로 확인.

```bash
echo "=== Summary of changes ==="
git diff --stat
echo ""
echo "=== Word-level diff (will be long for reuse_report — scroll through) ==="
git diff --word-diff=color docs/reuse_report_v0.1.md | head -100
echo "..."
# Manual inspection: confirm only references changed, not surrounding prose.
```

자동 검증이 통과해도 **이 diff를 사람의 눈으로 빠르게 훑어보는 것이 권장된다**. 의심스러운 변경 (예: 코드 블록 내부의 의도하지 않은 sed 매칭, 인용문 안의 옛 이름 치환)이 없는지.

만약 의심 변경이 보이면 § 7 롤백 절차.

### 4.6. Commit + push + merge

```bash
git add docs/
git status
git commit -F - <<'EOF'
docs: apply file-naming rule _v0.1.md to content documents (G1 v3)

Per the T-line interview decision (file-naming convention: content
documents use _vx.x.md suffix; instruction and tool documents are
exempt), rename and update internal references.

This is v3 of G1. v1 had a circular dependency in §3 input list;
v2 fixed that but ran into an environment constraint when the
codebase_analysis session attempted execution via remote Contents
API. v3 explicitly requires a local git-clone environment with
git mv / sed / git diff available, mirroring the external
evaluator's recommendation that long documents not be rewritten
through remote API calls.

Renames:
  docs/ULTIMATE_GOAL.md  -> docs/ULTIMATE_GOAL_v0.1.md
  docs/GOAL_PROBLEM.md   -> docs/GOAL_PROBLEM_v0.1.md
  docs/reuse_report.md   -> docs/reuse_report_v0.1.md

Internal-reference updates applied via sed across:
  the three renamed files
  docs/architecture_v0.1.md (if present)
  docs/reuse_triage_task_A.md (if present)
  docs/ultimate_goal_eval_task.md (if present — G3 may not have run yet)

Exempt from this commit:
  README.md (tool document; G2 handles)
  docs/TASK.md (instruction document; G2 handles)
  *_task.md files (instruction; refs updated, names kept)

Safeguards applied (per external evaluation recommendation):
  - backup branch backup/pre-g1 created
  - /tmp/g1-pre-hashes.txt and /tmp/g1-pre-linecounts.txt recorded
  - work performed on branch chore/g1-rename-v3, not directly on main
  - line-count, heading-structure, leak, and YAML validation all
    passed before commit
  - git diff --word-diff inspected manually for unintended changes

YAML validity preserved:
  ULTIMATE_GOAL_v0.1.md YAML re-parsed cleanly. document.name and
  related_documents keys reflect the new names.

MD-4 (user-consent for ULTIMATE_GOAL modification):
  User explicitly approved the rename via T-line interview answer
  to "(β) — apply rule including ULTIMATE_GOAL.md". Content is
  preserved; only the filename and internal references changed.

Supersedes:
  docs/git_g1_rename_task.md     (v1, circular dependency)
  docs/git_g1_rename_v2_task.md  (v2, halted at environment check)
EOF

# Push the branch
git push -u origin chore/g1-rename-v3

# Merge to main (fast-forward if possible)
git checkout main
git merge --ff-only chore/g1-rename-v3
git push origin main

# Optionally delete the working branch
git branch -d chore/g1-rename-v3
git push origin --delete chore/g1-rename-v3
```

만약 `--ff-only` merge가 실패하면, 즉 main이 그 사이 다른 commit으로 진행되었으면 *PR을 생성하고 사용자에게 알림*. 자동 merge 하지 말 것.

### 4.7. 결과 보고

```bash
echo "=== G1 v3 done ==="
git rev-parse HEAD
git log -1 --stat
echo ""
echo "=== Pre/post line counts ==="
cat /tmp/g1-pre-linecounts.txt
cat /tmp/g1-post-linecounts.txt
```

## 5. 산출물 형식

T-line 세션에 다음을 보고:

```text
G1 v3 결과:
  환경 검증:        OK / FAILED (어느 도구가 부재인지)
  백업:             OK (/tmp 백업 N개, backup branch backup/pre-g1)
  rename 3건:       OK
  내부 참조 갱신:   N건 (몇 곳이 바뀌었는지)
  skipped 파일:     N개 (어느 파일이 skip되었는지)
  라인 수 보존:     OK / FAILED (rename 후 라인 수 차이)
  Heading 구조:     OK (reuse_report 6 P1 sections, ULTIMATE_GOAL 8 sections)
  leak 검사:        0건 / N건
  YAML 검증:        OK / FAILED
  수동 diff 검토:   OK / suspect (의심 변경 있다면 어느 것)
  commit SHA:       <full SHA>
  branch merge:     OK (chore/g1-rename-v3 -> main)
  push 상태:        OK / FAILED
```

## 6. 비목표 (Non-goals)

### Case: Type

- **Contents API로 큰 파일을 다시 쓰지 마라.** 환경 사전 검증(§3.2)에서 git/sed 부재 발견 시 *작업 시작하지 말고 즉시 멈춤*.
- **§3.3.2의 부재 파일을 *오류로 처리하지 마라*.** v2의 fix를 유지.
- **G2/G3/G4의 작업을 G1 v3에 포함하지 마라.**
- **새 .md 파일을 만들지 마라.** rename + 참조 갱신만.

### Case: State

- **환경 부재 시 폴백을 *자체 결정하지 마라*.** Contents API 사용으로 우회하지 말 것. *T-line에 보고하고 멈춤*. 폴백 옵션은 T-line/사용자가 결정 (예: 옵션 X — 사용자가 직접 실행, 옵션 Z — Claude Code).
- **검증 단계 중 하나라도 실패하면 commit 금지.** §4.4의 V1~V4 모두 통과해야 §4.6 진행. 실패 시 §7 롤백.
- **수동 diff 검토에서 *의심 변경* 발견 시 commit 금지.** 사람의 눈에 이상해 보이는 변경이 있으면 자동 검증이 통과해도 멈춤.
- **`--ff-only` merge 실패 시 자동 merge 강행 금지.** PR 생성 후 사용자 알림.

### Case: Performance: Over

- **추가 정리 작업을 하지 마라.** 발견되는 다른 불일치는 G2/G3/G4 또는 별도 작업.
- **백업을 *추가로 외부에 push하지 마라*.** `/tmp` + backup branch면 충분.

## 7. 롤백 절차

검증 실패 또는 수동 diff에서 의심 변경 발견 시:

```bash
# (R1) Discard working changes
git checkout main
git branch -D chore/g1-rename-v3

# (R2) Restore from /tmp backups if necessary
cp /tmp/ULTIMATE_GOAL.md.bak docs/ULTIMATE_GOAL.md
cp /tmp/GOAL_PROBLEM.md.bak  docs/GOAL_PROBLEM.md
cp /tmp/reuse_report.md.bak  docs/reuse_report.md

# (R3) Verify hashes match pre-state
sha256sum docs/ULTIMATE_GOAL.md docs/GOAL_PROBLEM.md docs/reuse_report.md
diff - /tmp/g1-pre-hashes.txt <<EOF
$(sha256sum docs/ULTIMATE_GOAL.md docs/GOAL_PROBLEM.md docs/reuse_report.md)
EOF
# Hashes must match. If not, restore from backup branch:
#   git restore --source backup/pre-g1 -- docs/

# (R4) Report failure to T-line with the specific verification step that failed
```

## 8. 검증 규칙 (산출물 완료 기준)

1. **환경 사전 검증 통과** (§3.2)
2. **§3.3.1 파일 3개가 새 이름으로 존재**
3. **옛 이름 3개가 더 이상 존재하지 않음**
4. **§3.3.2 파일 중 존재했던 파일에 leak 0건** (부재 파일은 검증 대상 아님)
5. **YAML 파싱 성공 + document.name 및 related_documents 새 이름 반영**
6. **라인 수 보존** (rename + sed로는 라인 수 변화 없어야 함)
7. **Heading 구조 보존** (reuse_report 6개 P1 섹션, ULTIMATE_GOAL 8개 섹션 등)
8. **수동 diff 검토 통과**
9. **`chore/g1-rename-v3` 브랜치가 main에 ff-merge되고 push 완료**

## 9. 작업 완료 후 정리

본 지시서는 일회성 (MD-13). 작업 완료 후 다음 commit 또는 후속 cleanup commit에서 삭제 대상:

```text
docs/git_g1_rename_task.md      (v1, superseded)
docs/git_g1_rename_v2_task.md   (v2, superseded)
docs/git_g1_rename_v3_task.md   (v3, this file, executed)
```

삭제 시점은 G4 완료 후 일괄 cleanup commit에서 처리.

## 10. 시작 지시

1. **§3.2 환경 사전 검증을 *먼저* 실행**. 실패 시 즉시 멈춤 + 보고 (자체 폴백 금지).
2. §4.1 백업 생성
3. §4.2 작업 브랜치 생성
4. §4.3 rename + sed 실행
5. §4.4 자동 검증 (V1~V4)
6. §4.5 수동 diff 검토
7. §4.6 commit + push + merge
8. §4.7 결과 보고
9. 실패 시 §7 롤백

---

**요청자 노트**: v3은 *환경 명시*가 v2 대비 가장 큰 차이다. v2의 §3 분리 fix는 그대로 유지하면서, *어디서 어떻게 실행하는가*에 대한 가정을 명시적으로 만들었다. codebase_analysis가 본 환경 요건을 만족하지 못한다면, *재시도가 아니라 보고 후 멈춤*이 본 지시서의 정상 동작이다. 이는 외부 평가 보고서의 *"부분 성공 commit 금지"* 원칙과 정렬한다.
