---
name: interview-facilitation
description: Run a structured interview where one decision is taken per turn, automatic inferences from prior consensus are surfaced before manual questions, and depth on each decision is preferred over interview round-trips. Use whenever a user needs to make a sequence of related decisions whose record will outlive the conversation.
version: 1.0.0
metadata:
  hermes:
    tags: [interview, consensus, decision-making, facilitation]
    category: agent-collaboration
    related_skills: [consensus-recording, task-delegation, evaluation-followup, session-handoff]
---

# Interview Facilitation

A protocol for running interviews that produce durable, auditable decisions. The protocol biases toward depth on each decision and against unnecessary round-trips. It does not cover *recording* the resulting decisions — that belongs to [`consensus-recording`](../consensus-recording/SKILL.md).

## When to Use

- The user is making a sequence of decisions whose outcome will be recorded in a document or specification.
- Two or more decisions in the sequence are coupled, so taking them in the wrong order would force re-work.
- The user has indicated a preference for thoroughness ("the option that takes more time", "do the more detailed one") rather than speed.
- A new decision might already be settled by an earlier one in the same project; the user should not have to re-decide what they already decided.

Do *not* use when the user is asking for a single factual answer, a simple yes/no, or a quick tool action. The protocol's overhead is wasted there.

## Prerequisites

- A list of accumulated consensus items the user has established earlier — settled goals, meta-decisions, expression rules, file conventions, anything stable enough to derive from. Without this, "automatic inference" reduces to guessing.
- A clear scope for the current interview round (e.g. "review section 4 of the goal document", "decide how to handle external-eval findings"). Open-ended scope drifts.
- Permission to write Markdown notes or to edit a target document. If the interview's outputs cannot be recorded anywhere, the protocol is producing throw-away decisions.

## How to Run

For each new question the user surfaces:

1. Check whether prior consensus settles it. If yes, apply and report.
2. If not, present 2–4 labeled options with trade-offs.
3. Wait for one choice (one decision per turn).
4. Record the decision and any auto-derived consequences before moving on.

## Quick Reference

| Situation | Move |
|---|---|
| New question, fully derivable from prior consensus | Apply silently, report what was applied and why |
| New question, partially derivable | Apply the derived part, ask only about the residual |
| New question, not derivable | Present 2–4 options with trade-offs, ask once |
| User answer reveals a new decision pattern | Promote it to a numbered consensus item (e.g. MD-N, EX-N) |
| User answer changes scope | Stop the current question, confirm the new scope, then re-enter the protocol |
| User answer is ambiguous | Restate what you heard and ask a single yes/no confirmation |

Common label families for options:
- Coverage: full / partial / minimal
- Position: keep / abstract / move / remove
- Timing: now / next round / deferred
- Subject: user / agent / both

## Procedure

1. **Frame the decision in one sentence.** "We need to decide X." Anything longer is usually two decisions stacked. If you find yourself writing "and", split.

2. **Run the auto-derivation check before writing options.** Walk the consensus list and ask: does any prior decision narrow this? If a prior decision *directly* answers it, the right move is to apply and report — not to ask. Asking what was already decided erodes the user's trust in the consensus record. See `references/auto-derivation-checklist.md` for the checks worth running.

3. **Write 2–4 options, no more.** Each option must lead to a *different concrete outcome*, not the same outcome with different wording. If two options collapse on inspection, drop one. If you cannot get to four meaningfully different options, three or even two is fine — manufactured options are worse than fewer real ones.

4. **For each option, list trade-offs in the same dimensions.** Compare options on the same axes (e.g. coverage, cost, reversibility) so the user can scan a table. Mixed-axis option descriptions force re-reading.

5. **Make a recommendation, but separate it from the options.** State which option you would pick and why in one short paragraph after the option list. The user can disagree without re-reading the options.

6. **Take exactly one answer, then stop adding new questions.** If new questions come up during the answer, queue them; do not chain a second question into the same response. One-decision-per-turn is the only mechanism that keeps the audit trail clean.

7. **Apply the decision before moving on.** Update the target document or note the new consensus item *now*. Latency between decision and recording is where the user starts re-deciding.

8. **Surface auto-derived consequences.** When a decision settles other questions automatically, name them. The user should see "this also decides X and Y" before the next turn, so they can challenge the chain if it overreaches.

## Pitfalls

- **Asking what was already decided.** If you find yourself listing options that the user established in MD-2 or UG-3, stop drafting and apply. The auto-derivation check exists precisely to prevent this.

- **Bundling two decisions into one question.** "Should we do A in form B or form C?" is two decisions: whether A, and which form. Ask the upper one first. The user's answer to the upper question often makes the lower question moot.

- **Manufacturing options to reach four.** Real decisions sometimes have only two genuine paths. Inflating to four with near-duplicates dilutes the trade-off table and signals false precision.

- **Treating depth-bias as round-trip-bias.** "Take the option that takes more time" applies to *the analysis depth on one decision*, not to *adding more interview rounds*. A single deep round beats four shallow ones.

- **Recommending without separating.** When the recommendation is mixed into the option list, the user reads it as a fait accompli. Keep the recommendation in its own paragraph so dissent is easy.

- **Auto-applying a decision that touches a protected document.** Some documents (consensus repositories, signed specs) require explicit user consent for changes even when the change is "obviously" derived. Check the project's modification rules before silent application.

- **Promoting a one-off preference to a consensus item.** Not every user answer is a durable rule. If the user says "this time, let's go with B", that is a local decision, not a new MD-N. Promote only when the user signals durability ("from now on", "as a rule", "make this the convention").

## Verification

After each interview turn the protocol should produce:

- One recorded decision, written in the same shape as prior decisions (same numbering scheme, same vocabulary, same level of abstraction).
- A short note of any auto-derived consequences, with a pointer to which prior consensus item produced them.
- No new question chained into the same response.

After a full interview session the protocol should produce:

- A consensus record that a new reader can scan in the order it was created and understand each decision without going back to the original conversation.
- Zero decisions that re-decide an earlier one. If two decisions conflict, the later one supersedes and the earlier one is annotated as superseded; both are kept for audit.

If either property fails, the protocol was not actually followed. Common failure mode: the recommendation was buried in the option list and the user picked it without realizing it was the recommendation — the audit trail then looks like the user "chose" what the agent suggested. Fix by separating recommendation in subsequent turns.
