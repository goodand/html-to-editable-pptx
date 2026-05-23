---
name: task-delegation
description: Write a self-contained instruction sheet that hands a mechanical task to another agent or session with explicit environment requirements, explicit input partitions, explicit failure modes, and explicit lifetime. Use whenever the writing agent cannot execute the work itself due to environment, authority, or role separation, and the receiving agent will execute without further interview.
version: 1.0.0
metadata:
  hermes:
    tags: [delegation, instruction, agent-handoff, environment]
    category: agent-collaboration
    related_skills: [interview-facilitation, iteration-resilience, evaluation-followup]
---

# Task Delegation

A protocol for writing an instruction sheet that another agent will execute as a single self-contained job. The instruction sheet must carry every fact the receiving agent needs, because once execution starts there is no opportunity for clarification mid-task. This skill assumes the *what* of the task has been decided (in [`interview-facilitation`](../interview-facilitation/SKILL.md)); it covers the *how to hand it over*.

## When to Use

- A decision has been taken that requires execution in an environment the current agent cannot reach (git operations on a repository, code execution, filesystem changes outside this session).
- The receiving agent does not share the current session's context and will read only the instruction sheet plus the repository state.
- The task is mechanical enough that the receiving agent should not be making new decisions during execution. Genuine new decisions belong back in interview, not in the instruction.

Do *not* use for collaborative work where the other agent participates in deciding what to do. Use it only when the deciding and executing are separated.

## Prerequisites

- The decision that produced this task is already recorded (typically per [`consensus-recording`](../consensus-recording/SKILL.md)). The instruction sheet should cite the recorded decision, not re-litigate it.
- The receiving agent's *environment* is known well enough to specify required tools. If unknown, prefer to ask the receiving agent to self-report capability before writing — see [`iteration-resilience`](../iteration-resilience/SKILL.md) Pitfalls for why guessed environments produce repeated halts.
- A target path for the instruction file in the repository, following the project's conventions (often `docs/<descriptive_task>_task.md`).

## How to Run

Write a Markdown file with nine fixed sections in the order below. Each section is self-contained — a reader should not need to scroll up and down to act on it.

## Quick Reference

| Section | Purpose | Typical length |
|---|---|---|
| 1. Meta | Task ID, recipient, output, lifetime | ~10 lines |
| 2. Position | Where this task sits in the larger plan | ~5 lines |
| 3. Inputs | Required-to-exist vs update-if-present | varies |
| 4. Definition | Concrete command sequence or steps | bulk of file |
| 5. Output format | Exact shape the receiver should report back | ~15 lines |
| 6. Non-goals | What is explicitly out of scope | ~20 lines |
| 7. Verification | What "done" looks like | ~10 lines |
| 8. Start | Numbered ordered steps to begin | ~10 lines |
| 9. Lifetime | When the instruction itself should be deleted | ~5 lines |

Two non-negotiable invariants:

- **Inputs are partitioned.** Distinguish files that must exist for the task to start from files that should be updated if they happen to be present. Mixing them causes circular-dependency halts when the optional files are produced by a sibling task.
- **Environment is explicit.** State which tools and which network surface the receiving agent must have, with verification steps the agent runs *before* starting work. Implicit environment assumptions are the most common cause of halt-and-redesign cycles. See [`iteration-resilience`](../iteration-resilience/SKILL.md).

## Procedure

1. **Write the Meta header first.** A small table: task ID, recipient role, output (e.g. commit SHA, file path, report), expected duration, dependencies on other tasks, and lifetime (`one-time, delete after execution`). If lifetime is one-time, repeat that fact in section 9.

2. **Position the task in section 2.** One short paragraph: what larger plan this is part of, which sibling tasks exist, and what depends on this task completing. The receiving agent reads this to know whether to halt on edge cases or push through.

3. **Partition inputs in section 3 — non-negotiable.** Two sub-lists:
   - *Required to exist.* Without these, the task halts before work begins.
   - *Update if present.* These may not exist (typically because they are outputs of a sibling task). Their absence is not an error; the task skips them.
   This partition prevents the most common halt cause: a task that references its own siblings as prerequisites.

4. **Write the work as a concrete command sequence in section 4.** Prefer exact commands over prose descriptions. If the receiving agent has multiple equivalent ways to do something, pick one and write the chosen commands; leave alternatives out. Multi-choice instructions force decisions during execution.

5. **Specify the report shape in section 5.** A literal template the receiving agent fills in. Include both success values and failure-mode values (`commit SHA: <SHA> | FAILED (reason)`). This is what the writing agent reads to know what happened.

6. **List non-goals in section 6 by category.** At minimum: Type (kinds of work that don't belong here), State (what halt conditions should not be self-recovered from), Performance: Over (extra work the receiver should not do). Non-goals catch scope creep before it starts.

7. **State verification in section 7 as observable checks.** "Three files exist with new names", "old name has zero occurrences in the touched files", "YAML still parses". Not "looks correct", not "well-formed" — observable checks the receiving agent can run.

8. **Section 8 is the numbered start sequence.** Even if section 4 already has commands, give a `1. do this, 2. then this` order at the end so the receiving agent has an unambiguous entry point.

9. **Section 9 states lifetime.** If the instruction is one-time, the file should be deleted after execution. Name the file paths to delete, including this instruction itself. Without an explicit lifetime, instruction files accumulate and obscure the repository.

When the task fails repeatedly, do *not* edit this instruction in place — write a `_v2_task.md` instruction that supersedes it, document why v1 halted, and let the receiver execute v2. See [`iteration-resilience`](../iteration-resilience/SKILL.md). When the task is one of a batch of follow-ups to an external evaluation, group it under one work-group ID and link to siblings — see [`evaluation-followup`](../evaluation-followup/SKILL.md).

## Pitfalls

- **Flat input list with required and optional mixed.** This produces circular dependency halts. The receiving agent sees an "input" missing, treats it as required, and halts even though the missing input is the output of a sibling task. Always partition into required-to-exist and update-if-present.

- **Implicit environment.** If the instruction says "run `git mv`" without stating that a local git work-tree is required, the receiving agent will try to satisfy the command via whatever surface it has — and if that surface is unsuitable (e.g. remote API on a 50 KB file), the result is corruption or a halt. State environment requirements as explicit pre-flight checks the receiver runs first.

- **Multi-choice instructions.** "Either use `git mv` or PUT via Contents API" forces the receiver to decide mid-task. Pick one path and write it.

- **Missing report shape.** Without a literal template for the report, different receiving agents return differently structured responses, breaking the writing agent's verification step. Always provide the report template.

- **Edit-in-place after halt.** When v1 halts, editing it in place destroys the record of why the original failed. The audit trail loses the iteration. Always write a new versioned instruction (`_v2_task.md`) that explicitly supersedes the prior version, with a brief note of why.

- **Missing lifetime.** Instruction files accumulate. After several rounds of delegation, the repository contains a graveyard of one-time instructions that are no longer relevant. Section 9 prevents this — but only if it actually names which files to delete, including itself.

- **Embedding decisions in the instruction.** If the receiving agent has to *decide* something (which file to overwrite, which option to pick, whether to retry on failure), the decision was not actually taken in interview. Send the task back to interview, or write multiple instructions for the alternative branches.

## Verification

The instruction sheet is correctly delegated when:

- A receiving agent reading only the instruction sheet (no shared session context) can execute it to completion without asking for clarification.
- Halts during execution are due to environment unavailability or genuine new information, not to ambiguity in the instruction.
- The report the receiving agent produces matches the template in section 5, including in failure modes.
- The instruction has an explicit lifetime that names this file among the deletion targets.
- No instruction step asks the receiving agent to make a decision that was not pre-decided in interview.

If a halt occurs that is *not* an environment unavailability and *not* genuine new information, the instruction had ambiguity. Treat that as a defect and write the next version with the ambiguity resolved — do not edit in place.
