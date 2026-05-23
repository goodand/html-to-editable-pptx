---
name: session-handoff
description: Close a session that has accumulated too much context by producing two artifacts — a one-time session summary that captures current state and immediate next actions, and a permanent methodology Skill that captures patterns for re-use. Use whenever a session reaches a logical milestone and a new session needs to resume work without re-reading the full conversation.
version: 1.0.0
metadata:
  hermes:
    tags: [handoff, context-management, session-boundary, summary]
    category: agent-collaboration
    related_skills: [consensus-recording, interview-facilitation]
---

# Session Handoff

A protocol for ending a session at a logical boundary in a way that a successor session — possibly a different agent — can resume cleanly. The protocol separates *what the session learned about itself* (durable, becomes a Skill) from *where the work stands right now* (transient, becomes a one-time summary).

## When to Use

- The current session's context window is becoming a constraint on response quality or speed.
- The work has reached a logical milestone (a phase complete, a major decision made, a delegation chain ready to execute) where stopping is cheap and resuming is meaningful.
- Future sessions on the same project are expected, and they will not have access to this session's conversation.

Do *not* use mid-decision. A handoff in the middle of an interview leaves the successor with an ambiguous restart point. Either finish the current decision first, or explicitly document the unfinished decision as the first item the successor must complete.

## Prerequisites

- The project's consensus record exists and is current (see [`consensus-recording`](../consensus-recording/SKILL.md)). The summary will reference numbered items there; if those items are not yet recorded, do that first.
- A clear sense of what the *next actions* are. If next actions are unclear, the handoff is premature — finish at least one decision before handing off.
- A target location for the two output files. By convention: the one-time summary in the project's docs directory; the methodology Skill in a `skills/<category>/` location following the project's Skills convention.

## How to Run

Write two files. The summary captures *here and now*: SHAs, commit IDs, the exact message the user is supposed to send next, the precise stop point. The Skill captures *patterns*: the anti-patterns this session encountered, the methods that worked, the decision flowchart. Wire them so each points to the other.

## Quick Reference

| Output | Lifetime | Optimized for | Reader |
|---|---|---|---|
| Session summary | One-time, deleted after handoff | Resuming this specific work | Successor session |
| Methodology Skill | Permanent, in-place patches over time | Reusing patterns in any future session | Any future session |

Naming convention recommendation:

- Summary: `docs/session_summary_v0.1.md` or `docs/handoff_v0.1.md`
- Skill: under the project's Skills tree at the appropriate category

Both files should explicitly state their lifetime in their own metadata or preamble.

## Procedure

1. **Confirm the session has reached a logical boundary.** A boundary is not just "context is getting long" — it is also a point where the next action is well-defined and does not require remembering mid-decision state. If both conditions are not met, finish or document the open decision first.

2. **List the four items that will be handed over.** These are *categories of context*, not files:
   - The work artifact itself (typically a git repository — already on disk, no transfer needed).
   - The user-agent conversation record (typically a compressed or summarized version the user transfers).
   - The session summary (this protocol produces it).
   - The methodology Skill (this protocol produces it).

   The summary and the Skill are the only two artifacts this protocol creates; the others are managed by the user.

3. **Write the session summary first.** It is the more time-sensitive artifact — its content is current state and will go stale quickly. Sections to include:
   - *Meta*: file name, lifetime ("deleted after handoff"), companion Skill name.
   - *Project overview*: one paragraph plus a pointer to the consensus record.
   - *Settled facts*: tables of numbered items (UG-N, MD-N, EX-N, conventions) — quick reference, not full prose.
   - *Current in-progress work*: the active work groups, their status, the exact SHAs and IDs.
   - *Immediate next action*: the literal message the user should send to the executing agent next, in a copy-pasteable code block.
   - *Mid-term and long-term*: the interview questions and the eventual implementation work, briefly.
   - *Stop point*: a diagram showing exactly where the handoff happens in the work flow.
   - *Successor start procedure*: numbered steps for the successor's first turn.
   - *Lifetime*: when this summary should be deleted (typically after the successor confirms they have absorbed it).

4. **Write the methodology Skill second.** Use [`consensus-recording`](../consensus-recording/SKILL.md)'s discipline for permanent documents, plus the Skill format conventions. The Skill captures:
   - When to use this approach (trigger conditions).
   - Prerequisites the user must have in place.
   - The protocol's steps as a numbered procedure.
   - Pitfalls discovered during the originating session — these are the most valuable content, because they are *learned* lessons.
   - Verification rules.
   The Skill should not contain project-specific facts (no UG-N, no MD-N from a particular project). Those belong in the project's consensus record. The Skill is reusable across projects.

5. **Cross-reference the two files.** The summary names the Skill ("see Skill X for the methodology"); the Skill is named in the summary's "successor start procedure". Bidirectional pointer ensures the successor reads both before acting.

6. **Sanity check by simulating the successor's first turn.** Read only the summary and the Skill (not the conversation). Can you state the immediate next action without ambiguity? Can you state the methodology in your own words? If either fails, the summary is incomplete or the Skill is too abstract — revise before delivering.

7. **Commit both files in the same commit if possible.** They are designed as a set. Separating them in the commit history creates risk that the successor sees one without the other.

## Pitfalls

- **Handoff mid-decision.** The successor inherits ambiguity. Either finish the current decision in the current session or write the open decision as the first explicit item in the summary's "immediate next action" — never leave it implicit.

- **Project-specific content in the methodology Skill.** Anti-patterns and procedures stay general. Specific decisions, file paths, and SHAs go in the summary. The Skill should be useful to a completely different project; the summary is project-specific by definition.

- **Skipping cross-reference.** A summary that points to its companion Skill, and a Skill that is named in the summary, ensure both are read together. Without the pointer, the successor may read only one and miss the other.

- **Forgetting to state the lifetime.** Without an explicit lifetime, the summary accumulates and clutters the project. State the deletion condition (e.g. "after successor confirms handoff complete") and name the deletion target.

- **Over-summarizing.** The summary is for the *successor*, not the user. The user has read everything already. Write at a level that someone who never saw the conversation can act on.

- **Under-summarizing the next action.** "Continue from here" is not a next action. The next action should be a literal command, message, or step the successor can execute without interpretation.

- **Letting the summary go stale before handoff.** If hours pass between writing the summary and the user starting a new session, the summary may already be wrong (a commit has landed, a finding has been processed). Verify the summary still matches reality before delivering it to the user.

## Verification

The handoff is correctly produced when:

- Two files exist: one short-lived summary and one permanent Skill.
- Each file points to the other with a working reference.
- The summary contains a literal next-action message that the user can copy-paste to a successor agent.
- The summary's "stop point" diagram unambiguously identifies where the work currently is.
- The methodology Skill is free of project-specific facts and could be applied to a different project unchanged.
- Both files state their lifetime in their own metadata.
- A reader of only the two files can reconstruct what the successor must do, in what order, without consulting the conversation that produced them.

If the successor session has to ask the user to re-supply context after reading these two files, the handoff was incomplete. The most common cause is missing SHAs or missing exact-text messages — both should be in the summary as literal blocks, not paraphrased.
