---
name: repo-execution-gate
description: Safely execute a delegated repository task by proving the git environment, protecting dirty worktrees, running required gates, choosing commit/push or patch export, and halting instead of publishing when verification fails.
version: 0.1.0
metadata:
  hermes:
    tags: [git, execution, validation, handoff, commit, patch-export]
    category: agent-collaboration
    related_skills: [task-delegation, iteration-resilience, session-handoff]
---

# Repo Execution Gate

A protocol for the executing agent that receives a task packet and must decide
whether it is safe to apply changes, commit, push, export a patch, or halt. This
skill starts after [`task-delegation`](../task-delegation/SKILL.md) has produced
the instruction sheet. It covers the execution surface, not the product design.

## When to Use

- A task packet asks an agent to change files in a git repository.
- The work may end in a commit, push, patch export, or halt report.
- Required verification gates can fail because of missing tools, network limits,
  sandbox limits, dirty worktrees, or generated artifacts.
- The agent must prove that publish is allowed before publishing.

Do not use this to decide what the task should accomplish. Use it only after the
task's intended changes and required checks are already specified.

## Modes

- **Apply and commit** — the repository is real, required gates pass, the staged
  set is explicit and clean, and the task packet permits commit or push.
- **Patch export** — useful changes exist, but the current environment cannot
  satisfy a required gate or publish surface. Export a portable diff and report
  what was and was not verified.
- **Halt and report** — preflight fails before safe work can begin, or continuing
  would require changing the task contract.

## Prerequisites

- A task packet or instruction with required inputs, non-goals, verification
  gates, and publish expectations.
- A target repository path.
- Authority to read the worktree and run the specified checks.

## Quick Reference

| Need | Command |
|---|---|
| Prove this is a git worktree | `git rev-parse --show-toplevel` |
| Prove worktree status | `git status --short --ignored` |
| Sync only by fast-forward | `git pull --ff-only origin main` |
| Inspect intended edits | `git diff --stat` and `git diff` |
| Stage only intended files | `git add <file> <file> ...` |
| Prove staged scope | `git diff --cached --name-only` |
| Check staged whitespace | `git diff --cached --check` |
| Export unstaged patch | `git diff --binary > <name>.patch` |
| Export staged patch | `git diff --cached --binary > <name>.patch` |
| Record final commit | `git rev-parse HEAD` |

## Procedure

1. **Prove the repository surface.** Run `git rev-parse --show-toplevel`. If the
   task requires git history, commit, or push and this fails, halt. A copied
   snapshot is not a repository execution environment.

2. **Read the task packet before editing.** Identify required inputs, required
   checks, publish surface, non-goals, and halt conditions. Do not replace a
   required check with a weaker smoke test unless the packet permits it.

3. **Inspect the worktree.** Run `git status --short --ignored`. Treat existing
   changes as user-owned unless the task explicitly says otherwise. Dirty
   worktrees are allowed only when the staged set can be kept explicit.

4. **Synchronize conservatively.** If the packet requires current `main`, run
   `git pull --ff-only origin main`. If fast-forward pull fails, halt and report.
   Do not merge, rebase, or rewrite history unless the packet explicitly says so.

5. **Apply the task with narrow file ownership.** Edit only the files required by
   the packet. Leave unrelated dirty files and generated caches alone unless they
   block the task.

6. **Run the required gates.** A missing required tool, unavailable package
   registry, or failed test is a failed gate. If the gate is required, do not
   commit or push. Decide between patch export and halt based on whether the
   changes are reusable without the missing gate.

7. **Classify generated artifacts.** Separate permanent outputs, opt-in audit
   logs, and ephemeral caches. Generated artifacts must be ignored, left
   unstaged, or explicitly documented as intended outputs. Do not stage a
   directory to "catch everything."

8. **Stage explicit files only.** Use `git add <file> ...`, not broad directory
   adds, unless the task's intended output is the whole directory and the
   staged list is reviewed afterward.

9. **Verify the staged set.** Run `git diff --cached --name-only` and
   `git diff --cached --check`. If the staged list contains unrelated files,
   unstage by explicit path and review again.

10. **Publish only after gates pass.** Commit only when required gates pass and
    the staged set is correct. Push only when the packet or user explicitly
    requests push and the selected publish surface is available.

## Patch Export Contract

Use patch export when useful changes exist but publish is unsafe or impossible.
The report must include:

- patch path or exact diff location;
- changed file list;
- checks that passed;
- checks that failed or could not run;
- reason commit and push were not performed;
- any generated files intentionally excluded.

Patch export is not a success claim. It is a portable handoff state.

## Halt Conditions

Halt instead of editing or publishing when:

- the target path is not a git repository and the task requires git operations;
- required inputs are missing;
- fast-forward pull fails when required;
- a required verification gate fails or cannot run;
- the task requires a different publish surface than the environment provides;
- continuing would require a new product, architecture, or scope decision.

## Report Template

Use this shape for all three modes:

```text
repo-execution-gate result:
  selected mode:       apply-and-commit | patch-export | halt-and-report
  repo root:           <path> | FAILED
  dirty state:         <summary>
  required gates:      pass <n> / fail <n> / not-run <n>
  staged files:        <list> | n/a
  patch export:        <path> | n/a
  commit SHA:          <sha> | not committed
  push:                pushed | not pushed
  halt reason:         <reason> | n/a
  excluded artifacts:  <list> | n/a
```

## Pitfalls

- **Snapshot execution.** A directory with files but no `.git` can support
  reading or patch export, but not git-required execution.
- **Implicit staging.** `git add .` and directory-level staging hide unrelated
  edits, generated files, and user work.
- **Smoke-test substitution.** Direct invocation is evidence, not a replacement
  for a required test runner unless the packet says it is acceptable.
- **Generated artifact drift.** Verification tools that dirty tracked files need
  either opt-in logging, `.gitignore` coverage, or explicit staging policy.
- **Publish surface substitution.** `git push`, remote API commit, and patch
  export are different execution contracts. Do not swap them silently.
- **Partial success commit.** A commit after a failed required gate turns an
  unsafe intermediate state into shared history.

## Verification

Execution is correctly gated when:

- the repo root was proven before edits;
- dirty worktree state was read and unrelated changes were protected;
- every required gate is reported as pass, fail, or not run with reason;
- commit/push happened only after required gates passed;
- patch export or halt report was used when gates could not be satisfied;
- `git diff --cached --name-only` was reviewed before commit;
- generated artifacts were excluded or intentionally staged by explicit path.
