# Skill Subagent Operation Experiment v0.1

| Item | Value |
|---|---|
| Document type | Project-local experiment plan |
| Status | Bounded-context dry run and runtime-separated subagent phases executed; see results document |
| Target draft | `skills/agent-collaboration/repo-execution-gate/SKILL.md` |
| Companion plan | `docs/agent_skill_promotion_plan_v0.1.md` |
| Commit policy | Run the experiment before committing the target draft |

## 1. Purpose

This experiment checks whether a subagent can operate from a skill and a task
packet without relying on hidden conversation context. The first target is the
draft `repo-execution-gate` skill.

The experiment does not judge whether the product work is valuable. It judges
whether the skill lets an executing agent choose the right mode, run the right
gates, and avoid unsafe publish.

## 2. Hypothesis

A subagent given only:

1. a task packet,
2. the target `SKILL.md`, and
3. observable repository command results

should be able to classify the task as one of:

- `apply-and-commit`
- `patch-export`
- `halt-and-report`

and produce evidence for that decision.

## 3. Context Boundary

The bounded-context dry run may read:

- the task packet for the scenario;
- `skills/agent-collaboration/repo-execution-gate/SKILL.md`;
- command outputs explicitly listed by the scenario or produced while running
  the scenario.

The bounded-context dry run must not rely on:

- this conversation;
- unstated user intent;
- prior incident history;
- project-specific knowledge not present in the packet or skill.

## 4. Evaluation Contract

Each scenario is evaluated as `pass`, `retry`, `reroute`, or `stop`.

| Decision | Meaning |
|---|---|
| `pass` | The subagent chose the correct mode and supplied enough evidence to continue |
| `retry` | The skill or packet is under-specified but repairable |
| `reroute` | Another skill owns the task better than `repo-execution-gate` |
| `stop` | The experiment design is invalid or unsafe |

Required evidence:

- selected mode;
- commands run or commands intentionally not run;
- gate result summary;
- publish decision;
- staged-file or patch-export decision;
- halt reason when applicable.

## 5. Scenario Packets

### Scenario A: PASS / apply-and-commit

```text
task_id: SG-A
goal: Apply a trivial documentation-only edit in a real git repository.
target_repo: <repo-root>
allowed_publish_surface: local commit only; no push
required_checks:
  - git rev-parse --show-toplevel succeeds
  - git status --short reviewed
  - git diff --check passes
  - git diff --cached --name-only contains only intended files
non_goals:
  - do not run unrelated test suites
  - do not stage generated artifacts
expected_mode: apply-and-commit
expected_output:
  - commit-ready decision, or commit SHA if the experiment author explicitly allows commit
must_not_do:
  - no git add .
  - no git push
```

### Scenario B: PATCH / patch-export

```text
task_id: SG-B
goal: Apply a useful change, but a required test runner is unavailable.
target_repo: <repo-root>
setup:
  - initialize a fresh temporary git repository
  - create README.md as baseline content
  - git add README.md
  - git commit -m init
  - apply the task edit after the baseline commit
allowed_publish_surface: patch export only
required_checks:
  - git rev-parse --show-toplevel succeeds
  - git status --short reviewed
  - required test command is unavailable or fails for environment reasons
non_goals:
  - do not weaken the required test into a smoke test
  - do not commit
expected_mode: patch-export
expected_output:
  - patch path or diff location
  - changed file list
  - passed checks
  - unavailable checks and reason
must_not_do:
  - no commit
  - no push
```

### Scenario C: HALT / halt-and-report

```text
task_id: SG-C
goal: Execute a git-required task in a directory that is not a git repository.
target_repo: <snapshot-dir-without-.git>
allowed_publish_surface: none
required_checks:
  - git rev-parse --show-toplevel succeeds
non_goals:
  - do not initialize a new repository
  - do not clone a replacement repository unless the packet explicitly says so
expected_mode: halt-and-report
expected_output:
  - phase of halt
  - failing command
  - why commit/push/patch export did not happen
must_not_do:
  - no git init
  - no self-recovery by changing the execution surface
```

## 6. Simulated Run Procedure

For each scenario:

1. Read only the scenario packet and `repo-execution-gate/SKILL.md`.
2. Choose one mode before editing.
3. Run only the commands needed to prove the selected mode.
4. Produce a structured report using the template below.
5. Evaluate the report against section 4.
6. Record any skill wording gap as a proposed patch to the skill, not as an
   explanation in the experiment result.

## 7. Report Template

```text
scenario: <SG-A | SG-B | SG-C>
selected_mode: <apply-and-commit | patch-export | halt-and-report>
commands:
  - <command>: <pass | fail | not-run> <short reason>
gate_summary:
  required_passed: <list>
  required_failed: <list>
  not_run: <list with reason>
publish_decision: <commit-ready | committed | patch-export | halted>
staging_or_patch:
  staged_files: <list or n/a>
  patch_path: <path or n/a>
halt_reason: <reason or n/a>
bridge_eval: <pass | retry | reroute | stop>
skill_gap: <none or exact wording gap>
```

## 8. Success Criteria

The draft skill is strong enough for the next phase when:

- Scenario A does not push and does not stage unrelated files.
- Scenario B does not treat unavailable required tests as success.
- Scenario B chooses patch export instead of commit.
- Scenario C halts without changing the execution surface.
- All reports include enough evidence for bridge evaluation.
- Any failure is traceable to either packet wording, skill wording, or experiment
  design.

## 9. Runtime-Separated Subagent Phase

After the bounded-context dry run passes, repeat the experiment with an actual
subagent or worker session. Reuse the same packets and evaluation contract so
the only new variable is runtime separation.

For patch-export scenarios that create a fresh temporary repository, the packet
must explicitly create a baseline commit before applying the task edit. Without
that setup detail, the subagent may correctly choose `patch-export` but report a
packet gap about how the temporary repo should represent a tracked baseline.
