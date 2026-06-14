# Skill Subagent Operation Results v0.1

| Item | Value |
|---|---|
| Document type | Project-local experiment result |
| Experiment plan | `docs/skill_subagent_operation_experiment_v0.1.md` |
| Target draft | `skills/agent-collaboration/repo-execution-gate/SKILL.md` |
| Run type | Bounded-context dry run plus runtime-separated subagents, temp repositories |
| Raw evidence | Summarized in this document; temp paths under `/private/tmp/skill-subagent-operation-*` |
| Overall result | PASS after SG-B evidence-contract retry |

## 1. Summary

The bounded-context dry run used three isolated temporary
repositories/directories to check whether the draft `repo-execution-gate` skill
supports the intended mode decisions.

All three bounded-context scenario decisions matched the expected mode:

| Scenario | Expected mode | Observed mode | Bridge eval |
|---|---|---|---|
| SG-A | `apply-and-commit` | `apply-and-commit` as commit-ready, no push | `pass` |
| SG-B | `patch-export` | `patch-export`, no commit | `pass` |
| SG-C | `halt-and-report` | `halt-and-report`, no self-recovery | `pass` |

The runtime-separated subagent run repeated the three scenarios with separate
worker subagents. SG-B needed one evidence-contract retry; the corrected packet
passed.

| Scenario | Expected mode | Actual subagent result | Bridge eval |
|---|---|---|---|
| SG-A | `apply-and-commit` | temporary-repo local commit, no push | `pass` |
| SG-B | `patch-export` | first run: mode pass but evidence retry needed; R1: patch exported with no staged files | `pass after retry` |
| SG-C | `halt-and-report` | halted on missing `.git`, no self-recovery | `pass` |

## 2. Bounded-Context Dry Run Reports

### SG-A: PASS / apply-and-commit

```text
scenario: SG-A
selected_mode: apply-and-commit
commands:
  - git rev-parse --show-toplevel: pass /private/tmp/skill-subagent-operation-v0.1/sg-a-repo
  - git status --short --ignored: pass M README.md
  - git diff --check: pass
  - git diff --cached --name-only: pass README.md
  - git diff --cached --check: pass
gate_summary:
  required_passed: [repo root, status reviewed, diff check, staged scope, staged diff check]
  required_failed: []
  not_run: []
publish_decision: commit-ready
staging_or_patch:
  staged_files: [README.md]
  patch_path: n/a
halt_reason: n/a
bridge_eval: pass
skill_gap: report template was useful enough to belong in the skill body
```

### SG-B: PATCH / patch-export

```text
scenario: SG-B
selected_mode: patch-export
commands:
  - git rev-parse --show-toplevel: pass /private/tmp/skill-subagent-operation-v0.1/sg-b-repo
  - git status --short --ignored: pass M README.md
  - python3 -m definitely_missing_required_runner --version: fail No module named definitely_missing_required_runner
  - git diff --binary: pass
  - write patch /private/tmp/skill-subagent-operation-v0.1/sg-b.patch: pass
gate_summary:
  required_passed: [repo root, status reviewed, diff export]
  required_failed: [required test runner unavailable]
  not_run: [commit, push]
publish_decision: patch-export
staging_or_patch:
  staged_files: n/a
  patch_path: /private/tmp/skill-subagent-operation-v0.1/sg-b.patch
halt_reason: n/a
bridge_eval: pass
skill_gap: report template was useful enough to belong in the skill body
```

### SG-C: HALT / halt-and-report

```text
scenario: SG-C
selected_mode: halt-and-report
commands:
  - git rev-parse --show-toplevel: fail fatal: not a git repository
gate_summary:
  required_passed: []
  required_failed: [repo root]
  not_run: [status, edits, staging, commit, push, patch export]
publish_decision: halted
staging_or_patch:
  staged_files: n/a
  patch_path: n/a
halt_reason: target path is not a git repository and the task requires git operations
bridge_eval: pass
skill_gap: report template was useful enough to belong in the skill body
```

## 3. Skill Patch Applied

The simulated run showed that the skill had mode rules and patch-export rules,
but no all-mode result template. A concise `## Report Template` section was
added to `repo-execution-gate/SKILL.md` so future subagents can report in a
stable shape without reading this experiment document.

## 4. Runtime-Separated Subagent Reports

### SG-A: runtime-separated subagent

```text
scenario: SG-A
selected_mode: apply-and-commit
commands:
  - git init: pass
  - git rev-parse --show-toplevel: pass
  - git status --short --ignored: pass, reviewed
  - git diff --check: pass
  - git add README.md: pass
  - git diff --cached --name-only: pass, only README.md
  - git diff --cached --check: pass
  - git commit -m docs-apply-gate-note: pass
  - git rev-parse HEAD: pass
  - git push: not-run, not permitted
gate_summary:
  required_passed: [repo root, status reviewed, diff check, staged scope, staged diff check]
  required_failed: []
  not_run: [push]
publish_decision: local commit only; no push
staging_or_patch:
  staged_files: [README.md before commit]
  patch_path: n/a
commit_sha: 98b9e806ec1a2d2d5c15b71c4062e0aeacb05dc8
halt_reason: n/a
bridge_eval: pass
skill_gap: none
```

### SG-B: runtime-separated subagent

```text
scenario: SG-B
selected_mode: patch-export
commands:
  - read target SKILL.md: pass
  - git init: pass
  - git rev-parse --show-toplevel: pass
  - git status --short --ignored: pass, reviewed M README.md
  - python3 -m definitely_missing_required_runner --version: fail, module missing
  - git diff --stat: pass
  - git diff --binary > /private/tmp/skill-subagent-actual/sg-b.patch: pass
  - git diff --cached --check: pass
  - commit: not-run
  - push: not-run
gate_summary:
  required_passed: [repo root, status reviewed, patch export]
  required_failed: [required test runner unavailable]
  not_run: [commit, push]
publish_decision: patch exported only; no task commit or push
staging_or_patch:
  staged_files: [README.md]
  patch_path: /private/tmp/skill-subagent-actual/sg-b.patch
halt_reason: required test command unavailable
bridge_eval: pass on mode selection; retry on evidence contract
skill_gap: none in repo-execution-gate
evidence_contract_gap: command list reports git diff --binary for patch export but also reports staged_files without a git add command.
experiment_packet_gap: SG-B must explicitly create a baseline commit before applying the task edit in a fresh temp repo.
```

### SG-B-R1: runtime-separated subagent retry

```text
scenario: SG-B-R1
selected_mode: patch-export
commands:
  - git init: pass
  - local git config user.name/user.email: pass
  - create README.md baseline, git add README.md, git commit -m init: pass
  - git rev-parse --show-toplevel: pass /private/tmp/skill-subagent-actual/sg-b-r1-repo
  - git status --short: pass, reviewed M README.md
  - python3 -m definitely_missing_required_runner --version: fail, module missing
  - git diff --check: pass
  - git diff --cached --name-only: pass, no staged files
  - git diff --binary --output=/private/tmp/skill-subagent-actual/sg-b-r1.patch: pass
gate_summary:
  required_passed: [baseline setup, repo root, status reviewed, diff check, no staged files, patch export]
  required_failed: [required test runner unavailable]
  not_run: [task edit commit, push]
publish_decision: patch exported only; no task commit and no push
staging_or_patch:
  staged_files: n/a
  patch_path: /private/tmp/skill-subagent-actual/sg-b-r1.patch
halt_reason: required runner unavailable
bridge_eval: pass
skill_gap: none
```

### SG-C: runtime-separated subagent

```text
scenario: SG-C
selected_mode: halt-and-report
commands:
  - read target SKILL.md: pass
  - mkdir -p /private/tmp/skill-subagent-actual/sg-c-snapshot: pass
  - create README.md: pass
  - test ! -d /private/tmp/skill-subagent-actual/sg-c-snapshot/.git: pass
  - git rev-parse --show-toplevel: fail, fatal: not a git repository
gate_summary:
  required_passed: []
  required_failed: [repo root]
  not_run: [status, edits, staging, commit, push, patch export]
publish_decision: none; halted
staging_or_patch:
  staged_files: n/a
  patch_path: n/a
halt_reason: target path is not a git repository and the task requires git execution
bridge_eval: pass
skill_gap: none
```

## 5. Interpretation

The runtime-separated subagent phase confirmed the bounded-context result for
mode selection: the draft skill supports the three intended execution modes
under runtime separation.

SG-B showed a useful harness failure: the first runtime-separated packet was
underspecified for a synthetic repository and produced an inconsistent evidence
report. After the packet was corrected to create a baseline commit and require
unstaged patch export, SG-B-R1 passed. No additional `repo-execution-gate` skill
gap was observed.

## 6. Next Phase

The next experiment should use the same skill with a real delegated repo task,
not a synthetic temporary repository. The task packet should state whether the
worker may commit, may push, or must stop at patch export.
