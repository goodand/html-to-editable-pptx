---
name: consensus-recording
description: Record decisions reached through interview as a non-authoritative repository document that preserves consensus across sessions and across agents. Use whenever interview outcomes need to outlive the conversation in a form that future readers — both human users and other agents — can act on without re-deriving the reasoning.
version: 1.0.0
metadata:
  hermes:
    tags: [documentation, consensus, repository, two-readers, yaml-index]
    category: agent-collaboration
    related_skills: [interview-facilitation, session-handoff]
---

# Consensus Recording

A protocol for writing the document that holds the durable outcomes of a series of interviews. The document is treated as a *record* of consensus rather than as a *source* of authority. This skill assumes the decisions have already been taken; it covers how to write them down.

## When to Use

- An interview run with [`interview-facilitation`](../interview-facilitation/SKILL.md) has produced one or more durable decisions that need to be preserved.
- Two or more readers will use the resulting document for different purposes (a human reviewing past decisions, an agent generating new interview questions).
- The decisions are likely to be referenced by other project documents, and those references should remain stable as the consensus evolves.

Do *not* use for transient notes, single-session task lists, or pre-decision exploratory writing. The protocol's structure is wasted on content that will not be referenced later.

## Prerequisites

- A clear list of items to record (settled goals, meta-decisions, expression rules, conventions). If the items are still being negotiated, run the interview first.
- Agreement on whether this document requires explicit user consent for modifications, or whether any agent may edit it. This affects the modification-rule line in the preamble.
- A target file path in the project. Repositories typically place this document at the top of a `docs/` tree.

## How to Run

Write the document in two parts: prose for the human reader, a YAML index for the agent reader. Keep the prose authoritative and treat the YAML as derivative. Update the YAML whenever the prose changes.

## Quick Reference

| Layer | Reader | Optimized for | Authority |
|---|---|---|---|
| Preamble (3 short paragraphs) | Both | Self-positioning | — |
| Numbered sections | Human (retrospection) | Read-ease, concrete examples | Authoritative |
| YAML index block | Agent (question-generation) | Boundary clarity, keys | Derivative |

The preamble has exactly three jobs: identify the document, position it in the cross-reference graph, and state the modification rule. Anything beyond that belongs in a numbered section.

## Procedure

1. **Open with a non-authority self-positioning preamble.** Three short paragraphs:
   - *What this document is.* "This document describes the reason this project exists, at the highest abstraction layer in the project." Avoid words like "single", "top-level", or "primary authority" — they make the document harder to reposition later when new documents enter the graph.
   - *How it relates to other documents.* "One node in a cross-reference graph, not a fixed top authority. Conflicts are resolved by fresh interview, not by document precedence." This makes the document a *record* of consensus rather than its source.
   - *Modification rule.* If consent is required, state it. If not, state explicitly that this document may be modified freely by any agent. Implicit modification rules are interpreted differently by different agents.

2. **Use numbered sections for the body.** One section per coherent topic (e.g. one-sentence goal, longer-form expansion, commitments, non-commitments). Do not nest beyond two levels — deep hierarchy hides the audit trail.

3. **Prefer concrete examples over compact abstraction.** The human reader is using this document for retrospection, not first-time learning. Concrete tokens ("PPT slide", "16:9") help retrospection even when they reduce abstraction. Move highly abstract framings to the agent-facing YAML index.

4. **Number every durable item.** Goals as `UG-N`, meta-decisions as `MD-N`, expression rules as `EX-N`. Whatever the scheme, use it consistently. Numbered items are how other documents reference back, and they survive renames of section titles.

5. **Add a YAML index block at the end of a "how to use" section, not at the top.** Top-of-document YAML reads as authority. Mid-document YAML reads as supporting material. The YAML's first comment line should state explicitly: prose is authoritative; if YAML conflicts, prose wins and YAML must be re-derived.

6. **Exclude open questions from the YAML index.** Indexing unresolved items risks freezing them into apparent consensus. Open questions stay in prose only, and only get an index entry once they become settled items.

7. **When recording from an interview, copy the user's exact wording for one-sentence goals.** Paraphrases lose precision. Wider sections may rephrase, but the canonical one-sentence statement of the goal is verbatim.

8. **Re-derive the YAML whenever the prose changes.** Treat the YAML the way a compiled artifact is treated relative to source code. Manual divergence between prose and YAML is the most common drift mode.

See [`session-handoff`](../session-handoff/SKILL.md) for how this document gets summarized when a session ends and a new session needs to resume.

## Pitfalls

- **Authority-claim phrasing in the preamble.** Words like "single", "top-level", "primary", "is wrong" make the document harder to revise later when the graph of project documents shifts. Use relational phrasing ("at the highest abstraction layer in the project", "the reason this project exists") instead.

- **Enumerating sibling document names in the preamble.** Listing "see `X.md`, `Y.md`, `Z.md`" couples this document to the lifecycle of those files. When files are renamed or split, the preamble drifts. Use abstract reference ("all other project documents") and put concrete file names in a dedicated "how to use" section that is easier to maintain.

- **Putting the YAML index at the top.** Position implies precedence. Top-of-document YAML reads as the *source* of truth; mid-document or end-of-document YAML reads as *supporting material*. Match position to the actual authority relationship.

- **Letting YAML and prose drift.** The agent reader will trust the YAML; the human reader will trust the prose. When they disagree, both readers misread. Prose-wins is enforceable only if YAML is regenerated whenever prose changes — not as a separate human task, but as a step in every edit.

- **Recording one-off preferences as durable consensus.** Not every user remark is an `MD-N`. Promote only when the user signals durability ("from now on", "as a rule") — see [`interview-facilitation`](../interview-facilitation/SKILL.md) for the same warning on the interview side.

- **Numbered-item resets.** Never restart numbering when a section grows. `MD-12` should remain `MD-12` even if `MD-3` and `MD-7` are later superseded. Other documents that reference `MD-12` should not break because the count was renormalized.

## Verification

The document is correctly recorded when:

- A new reader (human) can scan the numbered sections in order and reconstruct the project's consensus without going back to original conversations.
- A new agent reading the YAML can produce a list of project commitments, non-commitments, and related-document delegations that matches the prose.
- The preamble does not use authority-claim phrasing; the document positions itself in a graph rather than at a top.
- Every cross-reference to another document either uses an abstract phrase or appears in the dedicated "how to use" section, never scattered through the body.
- Open questions exist only in prose, not in the YAML index.
- The YAML's first line of comments explicitly states the prose-wins rule.

A document that passes all six checks survives handoff to a different agent or a later session without re-derivation of the underlying decisions. See [`session-handoff`](../session-handoff/SKILL.md) for what that handoff process requires from this document.
