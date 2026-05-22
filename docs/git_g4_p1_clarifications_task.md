# 작업 요청서 — G4: P1 보강 (평가 I-04, I-05, P1 항목)

## 1. Meta

| 항목 | 값 |
|---|---|
| 작업 ID | git-g4-p1-clarifications |
| 수신 | codebase_analysis 세션 |
| 요청자 | T-line 세션 |
| 작업 종류 | git 작업 (content addition + commit + push) |
| 산출물 | commit SHA 1~3개 (4.4 참조), push 완료 |
| 예상 소요 | 1~2시간 |
| 의존성 | **G1, G2, G3 모두 완료 후 진행** |

## 2. 작업의 위치

codebase_analysis 평가의 **P1 (낮은 심각도, 다음 정리 때 보강)** 항목 3건:

- **I-04**: `reuse_triage_task_A.md`의 *"B안 우선"* 문구가 *reuse analysis 범위 한정*임이 명시되지 않음. 외부에서 보면 *ULTIMATE_GOAL의 "single document override 없음"* 원칙과 모순처럼 보일 수 있음.
- **I-05**: `architecture_v0.1.md`의 *"Image / SVG / Media Candidate"* 섹션과 *"Asset Mapper"*가 ULTIMATE_GOAL의 *"PPTX richness 비목표"*와 모순 가능성. 명시적 연결 부족.
- **P1-#6** (평가의 P1 권장사항): `GOAL_PROBLEM_v0.1.md`에 *"validation report is the concrete form of agent-side self-assessment"* 연결 문장 추가. ULTIMATE_GOAL의 `self-assessment` 용어와 GOAL_PROBLEM의 `validation report` 용어를 잇기.

본 작업(G4)은 이 3건을 적용합니다.

## 3. 입력 자료

G1, G2, G3 완료 후 repo 상태:

```text
docs/ULTIMATE_GOAL_v0.1.md        (G1으로 생성됨)
docs/GOAL_PROBLEM_v0.1.md         (G1으로 생성됨) — I-05의 자매 대상
docs/reuse_report_v0.1.md         (G1으로 생성됨)
docs/architecture_v0.1.md         (이미 존재) — I-05 대상
docs/reuse_triage_task_A.md       (G1으로 내부 참조 갱신됨) — I-04 대상
docs/ultimate_goal_eval_task.md   (G3로 등록됨)
docs/TASK.md                      (G2로 갱신됨)
README.md                         (G2로 갱신됨)
```

## 4. 작업 정의

### 4.1. I-04 — reuse_triage_task_A.md 범위 명시

**문제**: 현재 reuse_triage_task_A.md §8에 다음 문장이 있음:

> *"만약 두 세션의 결론이 충돌하면 **B안(코드 검증 기반)이 우선**합니다 — A안은 README 기반의 1차 분류이므로."*

이 문장은 *reuse analysis 범위 내*에서는 정확하지만, ULTIMATE_GOAL.md §7의 *"문서 간 충돌은 fresh interview로 해결"* 원칙과 *겉보기 모순*. 외부 평가자가 *"single document override 없음"*과 충돌로 해석.

**해결**: §8의 해당 문장 *바로 뒤*에 범위 한정 문장 추가:

```markdown
이 우선순위는 *reuse analysis decision의 범위 안에서만* 적용됩니다.
프로젝트의 ultimate goal 또는 다른 추상도 층위의 결정에서 두 세션의
의견이 갈리는 경우, ULTIMATE_GOAL_v0.1.md §7의 원칙에 따라 fresh
interview로 해결됩니다 — 어느 한 세션의 결론이 자동으로 우선하지
않습니다.
```

### 4.2. I-05 — architecture_v0.1.md Media Candidate 범위 명시

**문제**: codebase_analysis 평가에서 다음을 발견:

> *"`ULTIMATE_GOAL.md`는 PPTX rich feature와 embedded media beyond simple images를 비목표로 둡니다. 그러나 `architecture_v0.1.md`에는 `Image / SVG / Media Candidate`, `Asset Mapper`가 있습니다. 판정: 현재는 모순 아님. 권장 조치: architecture 문서에 'Media Candidate means asset reference or thumbnail, not editable timeline/media authoring' 추가."*

**해결**: `architecture_v0.1.md`의 *Media Candidate*가 처음 언급되는 위치 또는 §3 *Layered module design* 섹션 내 *Asset Mapper* 부근에 다음 명시 추가:

```markdown
> **Scope note** (per ULTIMATE_GOAL_v0.1.md §5 non-commitment to
> PPTX richness): "Media Candidate" means a reference to an asset
> (image, SVG, video thumbnail) or a placeholder, not an editable
> timeline, animation, or media authoring object. Video is
> represented as a thumbnail or asset reference; GIFs do not support
> frame-level editing. This boundary mirrors GOAL_PROBLEM_v0.1.md
> §"Target conversion policy" non-goals.
```

정확한 삽입 위치는 codebase_analysis가 *architecture_v0.1.md의 구조에 맞게* 판단. 단일 *Scope note* 블록으로.

### 4.3. P1-#6 — GOAL_PROBLEM_v0.1.md self-assessment 연결

**문제**: ULTIMATE_GOAL §4-C4는 *self-assessment*라는 추상 용어를 사용하고, GOAL_PROBLEM은 *validation report*, *fallback report*, *editability score* 등 구체 용어를 사용. 두 용어가 *같은 것을 가리킨다는 명시*가 없음.

**해결**: `GOAL_PROBLEM_v0.1.md`의 *validation report* 또는 *§9 Output generation and validation backend* 섹션 내, 첫 언급 부근에 연결 문장 추가:

```markdown
> **Terminology link**: The "validation report" defined in this
> section is the concrete form of what ULTIMATE_GOAL_v0.1.md §4-C4
> calls "agent-side pre-evaluation" or "self-assessment". The two
> documents use different terms at different abstraction levels:
> ULTIMATE_GOAL describes the *act* of producing a self-assessment
> before user evaluation; this document defines its *content*
> (mismatch score, editability score, fallback reasons, etc.).
```

정확한 삽입 위치는 codebase_analysis가 *GOAL_PROBLEM의 흐름에 맞게* 판단.

### 4.4. 커밋 분리 결정

3건의 변경을 **1개 commit으로 묶을지** **분리할지** 결정 사항.

**권장**: 1개 commit. 이유:
- 세 변경 모두 *codebase_analysis 평가의 P1*에서 출발
- 세 변경 모두 *경계 명시 보강* 성격 — 같은 작업 유형
- 각 변경이 *짧음* (3~5줄 추가)
- 분리 시 commit 메시지의 80%가 중복

다만 *역사 추적*을 중시한다면 3개 분리도 가능. 결정은 codebase_analysis에 위임.

### 4.5. 명령 시퀀스 (1 commit 가정)

```bash
# Pre-check: G1, G2, G3 완료 확인
[ -f docs/ULTIMATE_GOAL_v0.1.md ] || { echo "G1 not done"; exit 1; }
grep -q "ULTIMATE_GOAL_v0.1.md" README.md || { echo "G2 not done"; exit 1; }
[ -f docs/ultimate_goal_eval_task.md ] || { echo "G3 not done"; exit 1; }

# (1) I-04: reuse_triage_task_A.md 갱신
# Manual edit — find the "B안 우선" sentence in §8 and append the
# scope-limitation paragraph as defined in 4.1.

# (2) I-05: architecture_v0.1.md 갱신
# Manual edit — add the Scope note block as defined in 4.2.

# (3) P1-#6: GOAL_PROBLEM_v0.1.md 갱신
# Manual edit — add the Terminology link block as defined in 4.3.

# (4) Verify additions exist
grep -q "reuse analysis decision의 범위 안에서만" docs/reuse_triage_task_A.md
grep -q "Scope note" docs/architecture_v0.1.md
grep -q "Terminology link" docs/GOAL_PROBLEM_v0.1.md

# (5) Commit
git add docs/reuse_triage_task_A.md docs/architecture_v0.1.md docs/GOAL_PROBLEM_v0.1.md
git status
git commit -F - <<'EOF'
docs: apply P1 boundary clarifications (closes I-04, I-05, P1-#6)

Closes three P1 findings from the codebase_analysis evaluation of
ULTIMATE_GOAL_v0.1.md, each adding an explicit boundary statement
without changing existing content.

I-04 (reuse_triage_task_A.md): scope clarification for "B안 우선"
  The "B안 (code-level reuse report) takes precedence over A안
  (README-based shallow triage)" rule could be misread as a
  general document-override rule, conflicting with
  ULTIMATE_GOAL §7's "no single document override" principle.
  Added an explicit paragraph stating the precedence applies only
  within reuse-analysis decisions; ultimate-goal-level conflicts
  are still resolved by fresh interview.

I-05 (architecture_v0.1.md): Media Candidate scope note
  The Media Candidate / Asset Mapper modules could be misread as
  contradicting ULTIMATE_GOAL §5's non-commitment to PPTX media
  richness (video timeline, animation, etc.). Added a Scope note
  near the Media Candidate definition stating that this module
  handles asset references and thumbnails, not editable timeline
  or media authoring — mirroring the non-goals in
  GOAL_PROBLEM_v0.1.md.

P1-#6 (GOAL_PROBLEM_v0.1.md): terminology link to ULTIMATE_GOAL
  ULTIMATE_GOAL §4-C4 uses the abstract term "self-assessment"
  and delegates content definition to GOAL_PROBLEM. GOAL_PROBLEM
  uses concrete terms (validation report, fallback report,
  editability score). The link between the two terminologies
  was implicit. Added a Terminology link block stating that
  "validation report" is the concrete form of what ULTIMATE_GOAL
  calls "self-assessment", with the two documents addressing
  different abstraction levels (act vs content) of the same
  responsibility.

Reasoning:
  All three additions are scope or terminology clarifications.
  No existing decision is reversed. The additions explicitly
  state boundaries that were previously implicit, reducing the
  surface area for future misreading or evaluator-style
  rediscovery of these same questions.

This commit completes the P0/P1 follow-up sequence (G1, G2, G3, G4)
that originated from the codebase_analysis evaluation of
ULTIMATE_GOAL_v0.1.md.
EOF

# (6) Push
git push origin main

# (7) Report
echo "=== G4 done ==="
git rev-parse HEAD
git log -1 --stat
```

## 5. 산출물 형식

T-line 세션에 다음을 보고:

```text
G4 결과:
  commit SHA:           <full SHA>
  push 상태:            OK / FAILED
  I-04 추가:            OK (reuse_triage_task_A.md)
  I-05 추가:            OK (architecture_v0.1.md, 삽입 위치: §N)
  P1-#6 추가:           OK (GOAL_PROBLEM_v0.1.md, 삽입 위치: §N)
  분리 commit 여부:     1 commit / 3 commits
```

## 6. 비목표 (Non-goals)

### Case: Type

- **새로운 결정을 만들지 마라.** 세 추가는 *이미 합의된 사실의 명시화*. 새 commitment, 새 non-commitment, 새 책임 분담은 추가하지 말 것.
- **기존 문장을 *수정하지 마라*.** 세 변경은 *추가*만. 기존 문장을 *반박*하거나 *교체*하는 형태가 되어선 안 됨.
- **다른 P1 항목 처리하지 마라.** 평가 보고서의 P1은 *5번 항목까지* 있으나, T-line이 *3건*만 본 작업에 포함시켰음.

### Case: State

- **G1/G2/G3 미완료 상태에서 시작하지 마라.** Pre-check 모두 통과해야 함.
- **삽입 위치가 모호하면 *추가하지 말고 보고*.** 잘못된 위치에 들어가면 *문서 흐름이 깨짐*.

### Case: Performance: Over

- **세 변경 외의 보강을 하지 마라.** *발견되는 다른 모순*은 별도 작업 또는 다음 평가 라운드.
- **다른 P2 변경(예: 새 슬롯 정의, 새 모듈 정의)을 묶지 마라.** G4는 P1 한정.

### Case: Performance: Under

- **codebase_analysis가 *삽입 위치 판단*을 망설이면 보고만 하고 멈춤이 정상.** T-line이 추가 인터뷰로 위치를 명시.

## 7. 검증 규칙

산출물이 완료로 간주되려면:

1. **세 파일에 추가된 텍스트가 grep으로 확인 가능** (4.5의 step 4)
2. **기존 문장이 *수정되지 않음*** (git diff에서 *추가 라인*만 보여야 함, *수정 라인*은 없어야 함)
3. **YAML 등 구조적 요소가 손상되지 않음**
4. **commit + push 완료**

## 8. 시작 지시

1. G1, G2, G3 완료 확인 (pre-check 3건)
2. I-04 적용 (4.1)
3. I-05 적용 (4.2) — 삽입 위치 모호 시 보고
4. P1-#6 적용 (4.3) — 삽입 위치 모호 시 보고
5. 검증 step 실행
6. commit + push
7. T-line에 SHA 통보

---

**요청자 노트**: G4는 *판단 비중이 가장 큰 작업*입니다 — 세 *Scope note* / *Terminology link* 블록의 *삽입 위치*가 codebase_analysis의 판단. 위치가 모호하면 *추가하지 말고 보고*하는 것이 정상 동작. T-line은 그 보고를 받아 인터뷰를 통해 위치를 명시할 수 있음.

본 작업이 완료되면 P0/P1 후속 작업 시퀀스(G1~G4)가 모두 마무리됩니다. 다음 단계는 *Q2/Q3/Q4 본질 질문* 인터뷰이며, 이는 별도 T-line 세션의 책임입니다.
