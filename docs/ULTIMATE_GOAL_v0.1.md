# Ultimate Goal

This document describes the reason this project exists, at the highest abstraction layer in the project. All other project documents — describing the problem decomposition, the architecture, the reuse strategy, and future decisions — describe **means**. This document records the **end** that those means are intended to serve.

This document is one node in a cross-reference graph of project documents, not a fixed top-level authority. When decisions across documents appear to conflict, the resolution is determined by a fresh interview with the user, not by any single document overriding another. This document records the consensus that prior interviews produced; it is the *artifact* of consensus, not its *source*.

Modification rule: an agent may not modify this document without explicit user consent. To change anything here, the agent must first request permission, surface the proposed change, and obtain agreement. Other project documents do not carry this restriction.

---

## 1. The ultimate goal — one sentence

> **Let the user evaluate, visually and intuitively, an artifact that an LLM generated in HTML — by delivering it in a familiar visual form (PPT proportions and PPT-style image conventions) that the user can directly operate.**

## 2. The longer form

The system exists so that:

- An LLM generates an artifact in HTML, because HTML is the medium the LLM is most fluent in.
- The user receives that artifact in PPT form, because PPT proportions and PPT-style images are formats that the general public is already familiar with, so the cognitive cost of looking at the result is near zero.
- The user can *operate* the result — manipulate text, shapes, tables — because direct operation is the only channel through which **visual and intuitive evaluation** is possible.

The PPTX file format itself is not the point. PPTX is chosen as **the MVP container** for two reasons:

1. its directory structure (OOXML zip) is simple enough to author without re-implementing a presentation engine, and
2. the PPT visual conventions (16:9, slide style, image-on-canvas layout) are already in the user's eye, so no new visual literacy is required.

The system does *not* aim to use PPTX's full feature set (animations, master slides, transitions, etc.). PPTX is a *vehicle for evaluation*, not an end in itself.

## 3. Why evaluation is the goal, and not "editing" or "fidelity"

A user who receives an LLM-generated artifact may want to do one of three things:

| Action | Description |
|---|---|
| (1) Direct modification | The user is dissatisfied with the artifact and wants to fix it themselves |
| (2) Textual feedback | The user wants to describe a change but finds the requirements hard to express in text |
| (3) Visual/intuitive evaluation | The user wants to judge the artifact by looking and operating, not by reading |

These three actions are **not equal**. They have a dependency structure:

- **(1) depends on (3).** A user cannot decide to modify what they have not first evaluated. Evaluation precedes modification logically and temporally.
- **(2) and (3) overlap.** Touching the artifact is itself a form of expressing what the user wants, especially when text cannot capture it.
- **(3) has no substitute.** Modification (1) can be handled by interviews with the agent. Textual feedback (2) can be improved by rule-based accuracy and by the LLM teaching the user better expression. But visual and intuitive evaluation — *"I need to see and touch this to know what I think"* — cannot be replaced by any text channel.

Therefore (3) is the system's **first responsibility**. Without it, (1) cannot start because there is nothing to modify; (2) is still possible but limited in accuracy or specificity. With it, (1) and (2) can be handled through other channels (interviews, rules, LLM teaching).

## 4. What this goal commits the system to

Five concrete commitments follow from the ultimate goal:

1. **Familiar visual form**
   The output must look like something the user already recognizes — a PPT slide. New visual conventions raise the evaluation cost and defeat the goal.

2. **Operable surface**
   The artifact's visible elements must be directly modifiable through the standard UI actions of the user's familiar tool. Without operation, evaluation degrades to mere viewing — closer to reading text than to direct evaluation. The specific scope of which elements must be operable, and at what granularity, is the responsibility of `GOAL_PROBLEM_v0.1.md` and `reuse_report_v0.1.md`, not this document.

3. **Honest fallback marking**
   When part of the artifact cannot be made operable, it must be **explicitly marked** as such. A surface that *looks* operable but is not is worse than no operability at all, because it breaks evaluation in a hidden way.

4. **Agent-side pre-evaluation**
   The system must produce some form of self-assessment **before** the user evaluates. This is not a substitute for user evaluation; it is a courtesy that lets the user know what is worth their attention. The specific content of this self-assessment — what is measured, what is reported — is defined in `GOAL_PROBLEM_v0.1.md`, not this document.

5. **No commitment to PPTX richness**
   The system does not commit to supporting PPTX animations, masters, transitions, or other advanced features. PPTX is a container, not a target.

## 5. What this goal does *not* commit the system to

The ultimate goal explicitly does not include:

- **Pixel-perfect visual fidelity to the source HTML.** Fidelity helps evaluation but is not the goal. If the artifact is operable and recognizable, the goal is met even if pixels differ.
- **Round-trip editing back to HTML.** The user's modifications in PPTX do not need to flow back to the original HTML.
- **High-throughput batch conversion.** A single artifact for a single user's evaluation is the unit of value.
- **Multi-tool consistency (PowerPoint vs Keynote vs LibreOffice rendering equality).** The artifact must be evaluable in *one* tool the user has.
- **Replacing the user's judgment.** The self-assessment is a courtesy, not a verdict. The user decides.
- **Maximizing PPTX feature usage.** Animations, transitions, master slides, and embedded media beyond simple images are out of scope.

## 6. The user-agent loop, in one diagram

```text
        LLM
         │
         │  generates
         ▼
    HTML artifact
         │
         │  this project converts
         ▼
    PPT artifact  ────────► self-assessment
         │                    (agent's pre-evaluation)
         │
         │  user opens in a familiar tool
         ▼
   user evaluates ◄─────── (3) The first responsibility
         │
         ├──── satisfied ─────► done
         │
         ├──── (1) direct modification in PPT
         │        (user fixes it themselves)
         │
         └──── (2) textual feedback
                  │
                  │  agent improves via:
                  │   - rule-based accuracy
                  │   - LLM-led expression teaching
                  │   - structured interview
                  ▼
              new HTML artifact (loop)
```

The loop closes only because (3) is in place. Remove (3) and the user has nothing to feed back from.

## 7. How to use this document

When reading other project documents:

- `GOAL_PROBLEM_v0.1.md` defines the **problem statement and slot structure** — the technical decomposition of the work needed to reach this ultimate goal.
- `architecture_v0.1.md` defines the **pipeline shape** — the modules and their connections.
- `reuse_report_v0.1.md` defines **which external code helps reach the goal** with the least new construction.
- `reuse_triage_task_A.md` defines **the parallel shallow triage** for non-P1 candidates.
- `TASK.md` defines **the next concrete actions** — what is to be done now to make progress on the means above.

All of these are *means*. This document records the *end* that those means are intended to serve. When a decision in any of those documents appears not to serve the user's visual and intuitive evaluation, the resolution is not for this document to override that decision — it is for a fresh interview with the user to reconcile them. This document is updated only as a result of such an interview, and only with explicit user consent.

This document has two readers, who use it differently:

- The **user** reads this document to *retrospect* — to recall what was previously agreed, in a form that is easy to read. For this reader, prose clarity and concrete familiar examples take precedence over compact abstraction.
- An **agent** reads this document to *generate interview questions* — to find conflicts, inconsistencies, or contradictions between this document and other project documents, and surface them to the user for resolution. For this reader, the boundaries of what this document does and does not commit to must be unambiguous.

These two reading modes are not in conflict; they are addressed by complementary parts of the document. Prose passages serve the user's retrospection. Where boundary clarity matters more than narrative flow, structured representations (such as YAML index blocks; see below) may supplement the prose without replacing it.

### Agent index (YAML)

The following YAML block is a derivative index of the prose above, intended for agent consumption. **The prose is authoritative.** If this YAML conflicts with the prose, the prose wins and this block must be re-derived. The block is added in this v0.1 round; future rounds may extend it as new consensus accumulates.

```yaml
# Agent index — derivative of the prose above. Prose is authoritative.
# If this YAML conflicts with the prose, the prose wins and this block must be re-derived.

document:
  name: ULTIMATE_GOAL_v0.1.md
  authority: consensus_repository  # not authority document
  modification_rule: user_consent_required
  graph_position: highest_abstraction_node  # not single top authority

ultimate_goal:
  one_sentence: >
    Let the user evaluate, visually and intuitively, an artifact that an LLM
    generated in HTML — by delivering it in a familiar visual form (PPT
    proportions and PPT-style image conventions) that the user can directly
    operate.

user_actions:
  - id: "1"
    name: direct_modification
    depends_on: ["3"]
    handled_when_absent: cannot_start
    alternative_channel: interview_with_agent
  - id: "2"
    name: textual_feedback
    overlaps_with: ["3"]
    handled_when_absent: possible_but_limited_in_accuracy_or_specificity
    alternative_channel: rule_based_accuracy_or_llm_teaching
  - id: "3"
    name: visual_intuitive_evaluation
    role: first_responsibility
    substitute: none

commitments:
  - id: C1
    name: familiar_visual_form
  - id: C2
    name: operable_surface
    scope_delegated_to: [GOAL_PROBLEM_v0.1.md, reuse_report_v0.1.md]
  - id: C3
    name: honest_fallback_marking
  - id: C4
    name: agent_side_pre_evaluation
    content_delegated_to: [GOAL_PROBLEM_v0.1.md]
  - id: C5
    name: no_commitment_to_pptx_richness

non_commitments:
  - pixel_perfect_visual_fidelity
  - round_trip_editing_back_to_html
  - high_throughput_batch_conversion
  - multi_tool_consistency
  - replacing_user_judgment
  - maximizing_pptx_feature_usage

related_documents:
  GOAL_PROBLEM_v0.1.md: problem_statement_and_slot_structure
  architecture_v0.1.md: pipeline_shape
  reuse_report_v0.1.md: external_code_selection
  reuse_triage_task_A.md: shallow_triage_for_non_p1
  TASK.md: next_concrete_actions
```

## 8. Open questions about the ultimate goal itself

This document is a v0.1 statement of the ultimate goal. The following questions remain open and should be resolved by future interviews, then reflected in this document:

- **UQ-1**: Of the operations available to the user, which are *essential* for (3) evaluation to function as an enabler? Are all operations equivalent for evaluation, or are some (e.g., text editing) more essential than others (e.g., color change)? The concrete enumeration of operations is the responsibility of `GOAL_PROBLEM_v0.1.md`; this question concerns only the *upper principle* of which operation classes the ultimate goal depends on.
- **UQ-2**: Is there a class of LLM-generated content where evaluation is *not* the goal (e.g., the user wants a one-shot delivery without evaluation)? If so, is that out of scope, or a different mode?
- **UQ-3**: Does "familiar visual form" extend beyond PPT proportions and style? Would other familiar forms (A4 document, mobile screen) qualify in future versions?
- **UQ-4**: When the self-assessment and the user's evaluation disagree, which is treated as authoritative?