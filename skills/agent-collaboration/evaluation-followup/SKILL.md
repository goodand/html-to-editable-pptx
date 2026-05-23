---
name: evaluation-followup
description: Process an external evaluation report into prioritized work groups with clear dependencies, separating procedural fixes from substantive interview questions and keeping each group small enough for a single self-contained delegation. Use whenever an external agent or reviewer has produced a list of findings that the project needs to act on without re-litigating each finding.
version: 1.0.0
metadata:
  hermes:
    tags: [evaluation, follow-up, prioritization, work-grouping]
    category: agent-collaboration
    related_skills: [task-delegation, interview-facilitation]
---

# Evaluation Followup

A protocol for translating an external evaluation's list of findings into a small set of actionable work groups, each delegatable as a single instruction. The protocol prevents two failure modes: treating all findings as equal priority (which floods the work queue), and re-running the evaluation discussion in interview (which wastes the external work).

## When to Use

- An external agent, reviewer, or automated tool has returned a list of findings about an artifact (a document, a codebase, a design).
- The findings have implicit or explicit priorities (e.g. P0/P1/P2, severity high/medium/low, or just "things to fix first" vs "things to consider later").
- Some findings are *procedural* (rename this, update that link) and some are *substantive* (re-examine this decision, clarify this commitment). The two types should not be mixed in execution.

Do *not* use for an evaluation that is just a single comment or a single question. The protocol's grouping overhead is wasted there — handle directly in interview.

## Prerequisites

- The evaluation report itself, in a stable form (committed to the repository, or pasted in a record). Do not start grouping while the evaluation is still being revised.
- The original artifact the evaluation refers to. The receiving agent for each work group needs both the evaluation and the artifact.
- The current project's modification rules — particularly whether any artifact requires explicit user consent for changes. This determines which work groups can be delegated and which require an interview turn first.

## How to Run

Split findings into procedural vs substantive. Group procedural findings by *what document they touch* and by *what depends on what*, producing 3–5 work groups with explicit dependencies. Convert substantive findings into interview question candidates for a later round.

## Quick Reference

| Finding kind | Disposition | Where it goes |
|---|---|---|
| Procedural, no decision needed | Direct delegation | Becomes a work group with [`task-delegation`](../task-delegation/SKILL.md) |
| Substantive, decision needed | Interview question | Queued for an [`interview-facilitation`](../interview-facilitation/SKILL.md) round |
| Procedural but touches a protected document | Interview question + then delegation | One short interview turn for consent, then delegation |
| Consequence of another finding | Folded into that finding | Not a separate item |
| Already settled by prior consensus | Annotated as already-done | Documented for audit, no work |

Group sizing rules:

- A work group should be one delegation, one commit (atomic when possible).
- Dependencies between groups should form a graph with a unique starting node, not a cycle.
- More than 5 work groups suggests over-decomposition. Fewer than 2 suggests under-decomposition (one giant group hides parallel opportunities).

## Procedure

1. **Read the evaluation end-to-end before classifying anything.** Findings late in the report often reference findings early in the report. Classifying as you read produces inconsistent dispositions.

2. **Annotate each finding with a kind label.** *Procedural*, *substantive*, *consequence-of-another*, or *already-settled*. Be willing to revise these as the rest of the report clarifies relationships.

3. **Separate procedural from substantive immediately.** They have different downstream paths: procedural findings become delegations (this skill plus [`task-delegation`](../task-delegation/SKILL.md)); substantive findings become interview questions (back to [`interview-facilitation`](../interview-facilitation/SKILL.md)). Mixing them in the same work group forces the receiving agent to decide which findings to act on, which is the writing agent's job.

4. **Group procedural findings by document and dependency.** Findings that touch the same document and have no dependencies on each other can typically be one work group. Findings that depend on others' completion (e.g. "rename the file" before "update references to it") form a chain of work groups.

5. **Assign work group IDs.** A simple letter or number (G1, G2, …) is enough. The ID will be referenced in the delegation instruction, in commit messages, and in the dependency diagram. Stable IDs help when work groups are renamed or re-versioned.

6. **Draw the dependency graph.** Even if it is just three boxes and arrows. The graph is the artifact that explains the order to the receiving agent and to future readers. Cycles in the graph are bugs in the grouping — break them by splitting a node.

7. **Write a short note for each substantive finding.** What the question is, what's at stake, and whether it touches a protected document. This becomes the input to a later interview round. Do not draft answers here; the point is to capture the question accurately.

8. **For each procedural work group, write a [`task-delegation`](../task-delegation/SKILL.md) instruction.** Cite the evaluation by reference (e.g. "closes finding I-02 from the external evaluation"). The instruction's section 2 (position) is the natural place for the dependency graph.

9. **Handle protected-document findings with a single short interview turn.** If a procedural finding touches a document that requires user consent for modification, do not delegate without first getting that consent. One interview turn — present the finding, get consent — is enough.

## Pitfalls

- **Treating all findings as equal priority.** Even when the evaluation does not assign priorities explicitly, some findings block others. Render the implicit dependencies as an explicit graph; otherwise the delegated work happens in the wrong order and produces broken intermediate states.

- **Doing the substantive work in this protocol.** This skill stops at *capturing* substantive findings as interview question candidates. Actually answering them is the next interview round. Mixing the two collapses what should be two careful steps.

- **Over-decomposition.** Splitting every finding into its own work group produces a long chain of tiny commits and a lot of orchestration overhead. Group by document and dependency, not by finding count. Most evaluations of 5–10 findings produce 2–4 work groups.

- **Under-decomposition.** Putting all findings in one work group makes the resulting commit hard to review and turns one halt into a global rollback. If two findings have *no* dependency between them, they belong in separate work groups so they can be done in parallel and committed separately.

- **Inflating consequences into separate findings.** Findings that are downstream effects of other findings (e.g. "stale link" caused by "renamed file") fold into the upstream finding. Treating them as independent findings inflates the work group count and produces duplicated work.

- **Skipping the already-settled annotation.** A finding that prior consensus already addresses should be marked *already-settled* with a pointer to where it was settled. Otherwise the next reviewer files it again. The annotation is for audit, not for action.

- **Editing the evaluation report.** The evaluation is a stable artifact. Adding kind labels and group IDs belongs in a separate follow-up document, not in the evaluation file. Editing the source loses the externality that made it valuable.

## Verification

The followup is correctly processed when:

- Every finding has exactly one disposition: a work-group ID, an interview-question entry, an already-settled annotation, or a consequence-of pointer.
- The dependency graph between work groups is acyclic, with at least one starting node.
- Each procedural work group corresponds to one delegatable instruction written via [`task-delegation`](../task-delegation/SKILL.md).
- Each substantive finding has a captured question that the next interview round can pick up — not an attempted answer.
- Findings touching protected documents have been flagged for interview-first handling, not silently delegated.
- The evaluation source file is unmodified; all annotations live in a separate follow-up document.

If after this protocol there are findings the receiving agent cannot act on without further decisions, those decisions should be in the substantive queue. If they are not, the classification step was rushed — re-run step 2.
