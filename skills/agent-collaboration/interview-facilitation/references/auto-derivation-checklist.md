# Auto-Derivation Checklist

This checklist supports Step 2 of `interview-facilitation`'s Procedure. Run it *before* writing options for a new decision. If any check fires, the decision is at least partially derivable from prior consensus, and the corresponding part should be applied without asking.

## What to check against

A typical project that uses interview-facilitation accumulates four kinds of stable items:

- **Goal items** — the project's settled top-level purposes (often numbered UG-N).
- **Meta-decisions** — settled rules about how decisions and documents work (often numbered MD-N).
- **Expression rules** — settled rules about vocabulary, abstraction level, or representation form (often numbered EX-N).
- **Conventions** — settled rules about file naming, directory layout, branch policy, commit format.

The list and the numbering scheme vary by project. The checklist below is written in abstract terms so it works regardless.

## Per-check questions

### 1. Does any goal item directly imply an answer?

Read the decision and the goal items side by side. If a goal item names the same subject the decision is about and gives it a definite property (priority, position, responsibility), the decision inherits that property.

Example:
- Goal: "Editability is the primary responsibility; fidelity is secondary."
- Decision: "When two layout options trade fidelity for editability, which do we pick?"
- Apply: editability. No interview needed.

### 2. Does any meta-decision settle the procedure?

Meta-decisions often answer *how* the decision should be made, even if not *what*. Examples:

- "Document-level conflicts are resolved by fresh interview, not by document precedence."
- "User consent is required for modifications to document X; other documents are free."
- "Outputs of role A are .md only; role B handles execution."

If a meta-decision constrains the procedure, those constraints flow into the option set. Options that violate them should not be presented.

### 3. Does any expression rule narrow the form?

Expression rules look small but propagate widely. Examples:

- "Avoid authority-claim phrasing; use relational phrasing."
- "Do not enumerate sibling document names in this document; use abstract reference."
- "Replace term X with term Y; preserve metaphorical uses."

If the decision is about wording, check these first. The form is often fully determined before the substance.

### 4. Does any convention settle filesystem or version metadata?

For decisions that produce files or commits, conventions usually settle:

- File naming (suffix, version segment, allowed characters)
- Directory layout (which subtree the new file belongs in)
- Commit-message shape, branch naming
- Lifetime policy (one-time, permanent, deletable after handoff)

If a convention applies, the option set should not include violations.

### 5. Does an external evaluation already pre-decide part of this?

If the project has accepted an external evaluation report with prioritized findings (P0/P1/P2), those findings may pre-decide parts of the current decision. The recommendation in the evaluation does not override the user, but it should be surfaced as the *default* option.

## Reporting an auto-derivation

When a check fires, do not silently apply without saying so. Report in this shape:

> "From [consensus item N], this decision's [aspect] is determined: [outcome]. I applied that. The remaining open part is [residual]."

This gives the user one turn to dissent before the decision becomes part of the audit trail. If the user dissents, treat the dissent itself as evidence that the consensus item needs to be revisited — not as evidence that the auto-derivation logic is wrong.

## When the checks disagree

Two consensus items can imply different outcomes for the same decision. This is a *real* conflict, not an inference failure. The correct move:

1. Stop drafting options.
2. Surface the conflict to the user with both supporting items.
3. Ask which item should govern the current decision.
4. If the user resolves by ordering one item above the other, record that ordering as a *new* meta-decision; do not let it stay implicit.

A consensus graph with implicit precedences is more fragile than one with explicit conflicts, because future agents will infer different orderings.
