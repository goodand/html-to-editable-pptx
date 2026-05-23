---
name: iteration-resilience
description: Diagnose and recover when the same delegated instruction halts repeatedly, by treating environment assumptions as falsifiable and revising the instruction rather than the receiving agent. Use whenever two or more attempts at the same task have failed in a way that suggests the writing agent's model of the executing environment is wrong, not that the executing agent is misbehaving.
version: 1.0.0
metadata:
  hermes:
    tags: [resilience, environment, halt-recovery, instruction-versioning]
    category: agent-collaboration
    related_skills: [task-delegation]
---

# Iteration Resilience

A protocol for recovering when a delegated task halts more than once. The protocol's central commitment: each halt is *evidence about the environment*, not evidence about the receiving agent. The instruction is the thing that gets revised, not the agent. This skill assumes you are using [`task-delegation`](../task-delegation/SKILL.md) to write the instruction sheets; this skill covers what to do when the receiving agent reports back "halted."

## When to Use

- A delegated instruction has halted, and the same instruction (or a minor revision of it) has halted again.
- The halt reasons are *different each time* — first time circular dependency, second time content size, third time network — suggesting the writing agent's environment model is incomplete rather than that there is a single specific bug.
- The receiving agent is reporting the halts honestly and not silently working around them. (Silent workarounds produce a different problem and require a different fix.)

Do *not* use after a single halt with a clear cause. One halt with a clear cause gets a minor revision and a retry. The protocol's overhead applies once a *pattern* of halts emerges.

## Prerequisites

- The previous instructions and their halt reports are preserved in the project (typically by following the no-edit-in-place rule from [`task-delegation`](../task-delegation/SKILL.md) — each version is its own file). Without the audit trail of why each version halted, the protocol has nothing to learn from.
- The receiving agent's halt reports are detailed enough to identify which assumption failed. "Could not run" is not detailed enough; "could not resolve host" is.
- The writing agent has the capacity to verify environment facts directly when needed — typically by reading public documentation or asking the receiving agent to self-report.

## How to Run

Read all prior halt reports together. Identify which assumption broke each time. Look for *one underlying environment property* that, if explicitly verified, would have prevented all halts. Use the receiving agent's *prior successes* as the source of truth for what the environment can do, not your model of what it should be able to do.

## Quick Reference

| Halt cause pattern | Likely root | Next-version move |
|---|---|---|
| Halts on different surface each time (filesystem, network, API) | Environment surface area is misjudged | Re-derive surface from prior successful actions |
| Halts on different file size each time | Operation has implicit cost ceiling | Switch to lower-cost operation (e.g. metadata rewrite instead of full PUT) |
| Halts cite an explicit policy each time | Instruction violated a constraint the agent self-enforces | Read the constraint, redesign so it does not apply |
| Halts say "no permission" | Authority misjudged | Use a different authority surface that prior actions proved available |
| Halt reasons contradict each other | Two different agents responded, with different environments | Pin the environment in the instruction's Meta section |

Anti-pattern recognition table:

| Symptom | Anti-pattern label |
|---|---|
| Each version's halt blames the instruction's environment assumption | environment-assumption non-verification |
| Two tasks blame each other for missing prerequisites | implicit responsibility split |
| Halt produces a partially modified state | non-atomic application |
| Receiving agent runs successfully but the result is wrong | over-application of consensus |
| Halt mid-batch, but no file says what should happen next | absent halt-handling rule |
| Instruction lifecycle expectations diverge across versions | instruction-permanence assumption |

## Procedure

1. **Read all prior halt reports as one record.** Halts examined individually look like distinct bugs. Read in sequence to find the through-line. The through-line is almost always a single environment property that was never made explicit.

2. **Make the implicit environment property explicit.** Write one sentence: *"The executing environment can do X, cannot do Y, and we don't yet know whether it can do Z."* This sentence becomes the basis for the next version. If you cannot write the sentence with confidence, ask the receiving agent to self-report.

3. **Use prior successes as evidence, not just prior failures.** If the receiving agent has *successfully* committed to the repository in the past, it has at least the surface that those commits required. Listing what *did* work narrows the search space faster than listing what *did not*.

4. **Diagnose against the anti-pattern table above.** Match the failure pattern to a labeled anti-pattern. Naming the failure makes the fix routine instead of creative.

5. **Re-design the operation around the explicit environment.** Often the next version of the instruction looks structurally different from the prior versions — a different operation entirely, on the same goal. Renaming via git work-tree is not the same operation as renaming via remote tree mutation, even though both produce "the file is renamed".

6. **Prefer operations whose cost is mathematically zero where possible.** If an operation can be expressed as a reference change rather than a content transfer (a pointer update, a metadata edit, a tree rewrite that reuses existing blobs), choose that. It eliminates a whole class of size-based and corruption-based failures.

7. **Make the new version atomic.** Multiple changes that depend on each other should land in a single commit, single transaction, or single API call. Atomic application means partial-state halts are not even *possible*, which removes them from the failure surface — see also [`task-delegation`](../task-delegation/SKILL.md)'s atomicity guidance.

8. **Add a verification step *before* the publishing step.** Whatever the operation, build a moment where the proposed result exists in a checkable form before it becomes visible to the rest of the world. Failed verification at this point produces *no change*, not a partial change.

9. **Write the new version as a successor, not an edit.** Versioned instruction files (`<task>_v2_task.md`, `<task>_v3_task.md`) preserve the audit trail of which environment assumptions failed. The next person to read this project gets the iteration history for free.

10. **Stop after 4 attempts and escalate.** If four versions of the same task have all halted, the environment is fundamentally different from what the writing agent has visibility into. Escalate to the user: ask them to identify which execution surface is actually available, or move execution to a different agent or to the user directly. Continuing past 4 attempts is the writing agent's failure mode, not the receiving agent's.

## Pitfalls

- **Treating each halt as a fresh problem.** Each halt examined alone looks legitimate, and each next version feels reasonable. The through-line is only visible when the halts are read together. Always re-read prior reports before drafting the next version.

- **Blaming the receiving agent.** "It should have known to do X" is rarely the right diagnosis. The receiving agent is following its instruction sheet. If the sheet did not say X, the sheet is the bug.

- **Editing the failed instruction in place.** Loses the audit trail. The next reader cannot see what was tried and what failed, so the same failure recurs at the next person. Always write a new version.

- **Adding more safety steps without removing the failure surface.** Layering verification on top of an operation that has a fundamental cost ceiling does not help — the operation still hits the ceiling. The fix is a different operation, not more guards.

- **Skipping the "what did work" inventory.** Without the list of operations the receiving agent has proven it can do, the next version's environment assumption is guesswork. The receiving agent's history is the most reliable source for its capabilities.

- **Forcing atomicity through ad-hoc rollback.** "If something fails, we will undo the prior steps" is fragile and depends on the receiving agent's ability to undo cleanly. Real atomicity comes from operations whose underlying mechanism is single-step (a tree rewrite, a transaction, a single API call that contains all changes), not from compensating actions.

- **Continuing past four attempts.** The fifth version is the writing agent stuck in a local minimum. Escalation is not failure — it is recognition that the environment information needed to write the right instruction is not in the writing agent's reach.

- **Confusing the halt with a refusal.** If the receiving agent's halt is *correct* — the instruction asked for something that would have caused damage — the halt is a feature, not a bug. Treat such halts as confirmations of safety, and revise the instruction to take a different operation, not to override the halt.

## Verification

The recovery is correctly handled when:

- A new version of the instruction exists as a separate file, citing the prior versions and the reason each halted.
- The new version's Meta section names the environment property that was implicit before and is now explicit.
- The operation in the new version is structurally different from the prior versions where the failure mode was structural, not just parameterized differently.
- Atomic application is provided by the operation itself, not by a compensating-action rollback plan.
- A pre-publish verification step exists where a failed check produces *no* observable change, not a partial change.
- If four versions have halted, escalation has happened; no fifth version is in progress.

When all six conditions hold and the new version succeeds, fold the lesson into the project: the explicit environment property goes into the project's consensus record (see [`consensus-recording`](../consensus-recording/SKILL.md)), so that future delegations (see [`task-delegation`](../task-delegation/SKILL.md)) start from the now-explicit environment rather than re-discovering it.
