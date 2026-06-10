# Architecture Evaluation v0.1

| Field | Value |
|---|---|
| Evaluated state | `goodand/html-to-editable-pptx` remote `main`, fetched 2026-06-10 (two independent tarball fetches, byte-identical; 43 files, 6,867 lines). Commit SHA: `68b5d43b5012c14829de67d30080a2ec5d5a0df3` |
| Evaluation target | Union of (a) `docs/architecture_v0.1.md` (conversion-pipeline blueprint, 5 embedded mermaid diagrams) and (b) `docs/diagrams/architecture/*.mmd` (session/lifecycle layer, 5 files) |
| Method | R1–R4 full read of all 43 repository files (read 43 / excluded 0 — see Appendix A), then evaluation against the repository's own stated goals and invariants only |
| Rules applied | Evaluate, do not redesign. Findings only. Every finding carries evidence (file:line or diagram node), severity (blocker / major / minor / observation), and one classification: internal-inconsistency \| goal-misalignment \| coverage-gap \| undefined-boundary \| feasibility-risk \| open-question |
| Scope qualifier | This is a **conversion-architecture evaluation of the documented state**. The current-session, revision-centric intent (multimodal, Codex-authenticated revision, artifact/scope sessions as first-class constructs) is only partially documented in the repository — see AE-14. It is not a final evaluation of the full intended system. |
| Evaluator | T-line session (direct read; no delegation), 2026-06-10 |
| Relation to prior evaluations | Complementary to the external evaluation of `ULTIMATE_GOAL_v0.1.md` (findings I-01…I-05, processed via G1–G4). This document evaluates the architecture layer, which that round did not cover. |

---

## 0. Intent reconstruction (requires user confirmation)

The system exists so that a user can **evaluate, visually and intuitively, an artifact an LLM generated in HTML**, by receiving it in a familiar, **directly operable** PPT form (ULTIMATE_GOAL_v0.1.md §1 L13, §3 L38-46). Editability is the *means* of evaluation, not the end; PPTX is an MVP container, not a target (§2 L23-28, C5 L64-65). The architecture must therefore deliver: editable native objects over visual fidelity, explicit (never silent) fallback marking (C3 L58-59), and an agent-side self-assessment — concretely, the validation report (GOAL_PROBLEM_v0.1.md §9 Terminology link L818-824) — produced before the user evaluates. The bootstrap scope is deliberately minimal: a single-page, Node-only, validated conversion path with exactly two npm dependencies (`pixelmatch`, `pptxgenjs`) plus six functions transplanted from `dom_to_pptx` (reuse_report_v0.1.md Summary L773-790), with charts, ML fake-table detection, batch throughput, and PPTX richness all deferred through explicit non-goals.

**Confirmation result (2026-06-10 review):** confirmed correct **for the documented state** of `main`. However, the user's *current* intent has moved one step beyond the documents: the revision loop is being elevated to a first-class, **multimodal, Codex-authenticated** workflow operating on **artifact sessions / scope sessions**, with HTML as the source of truth and PPT strictly as the evaluation surface. Of these, "PPT as evaluation vehicle" and "revisions flow through a new HTML artifact" are already in ULTIMATE_GOAL_v0.1.md (§2 L28; §6 L101-108); "multimodal", "Codex-authenticated revision", and "artifact/scope session as system constructs" are absent from every consensus document and surface only as traces in diagrams 01–03 and the mmd-authoring skill (layer 6, "run authenticated revision"). This gap is recorded as finding AE-14; the intent baseline of this evaluation is therefore the documented v0.1 consensus, one step behind the live intent.

---

## 1. Summary

| Severity | Count | IDs |
|---|---:|---|
| Blocker | 0 | — |
| Major | 8 | AE-01 … AE-06, AE-08 (elevated), AE-14 (added) |
| Minor | 3 | AE-07, AE-09, AE-10 |
| Observation | 3 | AE-11 … AE-13 |

Verdict in one paragraph: the conversion-pipeline architecture (`architecture_v0.1.md`) is internally coherent at the macro level and well aligned with the stated intent — the pipeline invariant, the 12-type IR, the explicit-fallback path, and the minimal v0.1 scope all mutually reinforce (AE-11). The risk is concentrated not in the pipeline shape but in three places around it: (1) a second architecture layer (the lifecycle `.mmd` diagrams) that no document binds to the pipeline and whose infrastructure has no slot, candidate, or module (AE-01); (2) load-bearing validation components — the PPTX renderer and the editability metric — that every document assumes and no document owns (AE-02, AE-06); and (3) three reuse-decision records (`reuse_report_v0.1.md`, `third_party/subtrees.toml` + inventory, `architecture_v0.1.md` §4) that have diverged without reconciliation (AE-03), on top of four parallel slot/category/module vocabularies that break traceability between them (AE-04). The single most consequential undecided design question — the Playwright execution boundary — is explicitly delegated to the architecture document and is not answered there (AE-05). **Review cycle (2026-06-10):** an independent re-verification against remote `main` confirmed all findings valid; AE-08 was elevated to major (the revision/lifecycle direction makes runtime topology load-bearing) and AE-14 (consensus-layer intent gap) was appended. The same review revealed that the local working checkout lacks files present on remote (see AE-12 (d)).

---

## 2. What holds (checked, no violation found)

Per the project's own evaluation culture (ultimate_goal_eval_task.md §7 Case: State — "점검했으나 위반 아님도 가치 있는 결과"), the following were checked and found consistent:

1. **Pipeline invariant is uniform.** `DOM node → measured visual node → semantic candidate → PPT mapping decision → PPTX object` appears identically in README.md L188-193, GOAL_PROBLEM_v0.1.md L85-91, and architecture_v0.1.md §1/§2/§6.
2. **The 12 minimum IR types match.** GOAL_PROBLEM_v0.1.md L93-106 ↔ reuse_report_v0.1.md P1.2 §5.2 mapping table (12 rows, same names).
3. **Editability-first is structural, not declarative.** Fallback is a first-class pipeline path (architecture §2 H7/I7, §5 entire decision flow; GOAL_PROBLEM §8), `html2canvas` is excluded with a verifiable rule (reuse_report P1.3 §7 validation #4: "No html2canvas import in our src/ tree"), and fallback decisions emit dedicated reports (architecture §2 nodes P, Q) — which gives ULTIMATE_GOAL C3 (honest fallback marking) an enforcing mechanism.
4. **Architecture §8 non-goals mirror GOAL_PROBLEM non-goals and ULTIMATE_GOAL §5**, including the G4-added Scope note (architecture §3, "per ULTIMATE_GOAL_v0.1.md §5") that closed external finding I-05.
5. **The minimal v0.1 path (§6, §7) is correctly scoped to the bootstrap decision** of two npm dependencies + transplants (reuse_report Summary L780-783); §7 step 7 defers fake-table/chart recovery exactly as P1.4 §6.1 and P1.6 §6.1 decided.
6. **The lifecycle diagram 01 aligns with the ULTIMATE_GOAL §6 user-agent loop** (generate → assess → accept/revise → re-register → regenerate), operationalizing the loop the goal document drew in text — with one actor ambiguity noted in AE-06.
7. **en/ko `.mmd` pairs (02, 03) are structurally identical** node-for-node; 01 existing in `en` only is permitted by the authoring skill's rule ("when both exist", mmd-diagram-authoring SKILL.md §Verification).

---

## 3. Findings (ordered by severity at initial issue; AE-08 elevated and AE-14 appended in the 2026-06-10 review — IDs are stable, never renumbered)

### AE-01 — Two architecture representations exist with no defined relationship, and the lifecycle layer's infrastructure has no implementation grounding
**Severity:** major. **Class:** undefined-boundary (+ coverage-gap).

Evidence:
- `docs/architecture_v0.1.md` describes the conversion pipeline. `docs/diagrams/architecture/01–03.mmd` describe a different layer: artifact session lifecycle, source artifact registration, frozen input manifest lifecycle.
- No document in the repository references `docs/diagrams/` or any `.mmd` file (verified: repository-wide grep for `diagrams/` and `.mmd` over all `*.md` returns zero hits). ULTIMATE_GOAL_v0.1.md §7 (L117-121) and its YAML `related_documents` (L191-196) enumerate the document graph; the lifecycle diagrams are absent from it.
- The bridge is *known* but recorded only inside a skill: mmd-diagram-authoring SKILL.md §Diagram Layers plans six diagrams, of which 4 (*conversion job lifecycle*: render source → extract → build IR → map objects → generate PPTX) and 5 (*validation evidence lifecycle*) are precisely the missing joints between the lifecycle layer and the pipeline — and they do not exist yet.
- The lifecycle layer commits to substantial infrastructure: immutable source artifact revisions, frozen input manifests with blob references, content hashes, source/resolution provenance, rendering environment metadata, canonicalization, manifest digests, revision binding (02 nodes A–G; 03 nodes A–H). None of this appears in GOAL_PROBLEM's "What must still be built here" list (L322-335, 10 items), in the 8-slot table (L39-48), in any third_party manifest category, or in architecture §3/§4 modules. It has no reuse candidate among the 27.

Why it matters: the repository currently contains two architectures of one system that cannot disagree only because they never meet. Any implementation that starts from `architecture_v0.1.md` §7 will build a converter with no registration/manifest surface; any implementation that starts from the lifecycle diagrams will need storage, hashing, and a revision registry that no slot or reuse analysis covers. The interface is the architecture decision that determines both.

### AE-02 — The PPTX→screenshot renderer is load-bearing for validation and is owned by no slot, no candidate, no decision
**Severity:** major. **Class:** coverage-gap + feasibility-risk.

Evidence:
- architecture_v0.1.md §2 nodes K→L ("Rendered PPTX") and §3 ValidationLayer G1 ("Render PPTX"); §6 node I ("Render PPTX") — the validation loop's first step in all three diagrams.
- GOAL_PROBLEM_v0.1.md §9 expected output includes "rendered PPTX screenshot" (L843) with reuse candidate only "existing slide rendering and validation tools" (L849) — unnamed.
- reuse_report_v0.1.md P1.1 §3 takes "Rendered PPTX screenshot (LibreOffice / headless PowerPoint output)" as a *given input* (L31-32); P1.1 Y-table assigns "PPTX → screenshot (headless rendering)" to "us" (L75) with no further analysis anywhere.
- None of the 27 manifest candidates is a PPTX renderer (verified across `third_party/repositories.toml` and all six manifests).
- Success criterion 6 (GOAL_PROBLEM L346, "rendered PPTX is validated against the source screenshot") and ULTIMATE_GOAL C4 (agent-side pre-evaluation) both depend on this component existing.

Why it matters: the architecture's defining differentiator — "validated output > unverified output" — rests on a component that has received zero of the project's otherwise rigorous reuse analysis. Renderer choice (LibreOffice headless vs PowerPoint automation vs other) also has fidelity characteristics that directly shape pixelmatch thresholds (P1.1 §2 anticipates exactly this) and may constrain OS/runtime — i.e., it back-propagates into the boundaries of AE-05/AE-08.

### AE-03 — The reuse-decision record has forked into three unreconciled layers
**Severity:** major. **Class:** internal-inconsistency.

Evidence (three records, pairwise divergent, no cross-references):
- **(a) reuse_report_v0.1.md (evidence-based, v0.1):** `dom_to_pptx` = "Adopt as reference, vendor selected functions — *not* `import dom-to-pptx` as a runtime dep" (P1.3 meta L285); transplant six pure functions (§6.1); validation #5: "The original dom_to_pptx package is **not** listed in our package.json" (L409). `pixelmatch` = "Adopt as dep" (npm dependency; P1.1 L18, Summary L775). `looks-same` = evaluated only *if* pixelmatch's AA detector fails (P1.1 §8 Case: State L129). Explicit prohibition: "Do not wrap pixelmatch behind an abstraction layer that supports multiple diff backends in bootstrap" (P1.1 §8 Performance: Over L131).
- **(b) third_party/subtrees.toml + docs/subtree_module_inventory_v0.2.md (decision fields, v0.2):** `dom_to_pptx` `decision = "adopt_subtree"`, `import_mode = "whole_repo"` (subtrees.toml; inventory L42; handoff L19: "no longer a reference-only/defer item"). `pixelmatch` `decision = "adopt_subtree"` whole_repo with `adapter = "src/validate/pixelmatchAdapter.ts"`. `looks_same` `decision = "adopt_subtree"` as "secondary validation backend candidate". Three validation adapters are planned (`pixelmatchAdapter.ts`, `looksSameAdapter.ts`, `odiffAdapter.ts`) — structurally the multi-backend abstraction layer that (a) forbids in bootstrap.
- **(c) architecture_v0.1.md §4 reuse blueprint:** edges `R1(dom-to-pptx) → M1, M2, M4` only — omitting text runs and semantic tables; `M3 (Text Run Collector)` is sourced from `R2(html2pptxgenjs)`, a P2 repository never code-analyzed — contradicting reuse_report P1.3, which assigns slots 1, 2, **3**, 4, **5a**, 6 to `dom_to_pptx` with file:line evidence (`collectTextParts` at utils.js:1041, `extractTableData` at utils.js:37).
- Neither subtree document cites reuse_report; reuse_report's own pointer for this reclassification (Q-d2p-3, CQ-3) was queued for `deletion_candidates.md`, which does not exist (AE-10).

Compatible readings exist — a whole-repo subtree can serve as the in-repo *source* from which the six functions are transplanted, keeping `package.json` clean; adapters can be post-bootstrap — but no document states either reconciliation, and the machine-readable `decision` fields contradict the evidence-based decisions as written.

Why it matters: "reuse existing modules > write new code" is a core priority, and the project currently has three different answers to "what did we decide about reuse," with the timeline (v0.2 after v0.1) implying supersession that was never declared. An implementing agent obeying subtrees.toml violates reuse_report's validation rules and vice versa.

### AE-04 — Slot taxonomy fragmentation: four parallel vocabularies, no crosswalk
**Severity:** major. **Class:** internal-inconsistency.

Evidence:
- **GOAL_PROBLEM_v0.1.md L39-48:** eight *numbered* slots. Note: chart extraction is not one of the eight (it appears only as Technical Problem #7, L720); slot 8 fuses "PPTX output **and** validation backend".
- **reuse_report_v0.1.md:** *named* slots (`fallback_validation`, `pptx_output_backend`, `chart_semantic_extractor`, `fallback_policy_engine_validation`, `fake_table_detector`) plus sub-slot identifiers **5a / 5b / 7c** defined nowhere (P1.2 L149: "Slots 3, 4, 5a, 6, 7c"; P1.4 L427: "Slot 7c"; P1.6 L662: "Slot 5b"). P1.2 (L149) and P1.5 (L539) both claim "Slot 8" with *different* role descriptions for *different* repositories.
- **third_party manifests:** a third vocabulary of `category` strings, including compounds (`visual_object_ir_normalizer_fake_table_detector` for `surya`/`mineru`) and reference categories (`semantic_ir_reference`, `rich_text_reference`, …) that map to no numbered slot exactly.
- **architecture_v0.1.md:** §3 = seven layers (~30 nodes); §4 = nine project modules M1–M9; README L81-86 = six "Main modules". No table anywhere maps slots ↔ categories ↔ modules ↔ layers.

Why it matters: traceability — "which slot does this module satisfy, with which candidate, validated how" — is the spine connecting GOAL_PROBLEM → reuse decisions → architecture → validation. With four vocabularies, completeness checks become unevaluable: reuse_triage_task_A.md §7 requires "8개 슬롯 각각에 최소 1개의 adopt", which cannot be verified when the executing agent must privately invent a slot mapping. AE-03's divergence is partly a *product* of this finding: each record was written in its own vocabulary.

### AE-05 — The Playwright execution boundary is the pipeline's forcing decision, was explicitly delegated to the architecture document, and is unanswered there
**Severity:** major. **Class:** undefined-boundary.

Evidence:
- reuse_report_v0.1.md CQ-1 (L792-793): "What is the exact boundary between Playwright `page.evaluate` (browser-side) and Node-side processing? The dom_to_pptx transplant decision (P1.3 Q-d2p-1) is the forcing function." P1.3 Q-d2p-1 (L416-417) names the two options — (a) ship transplanted functions into `page.evaluate`, (b) keep them in Node over computed-style snapshots — and states "decision belongs to `docs/architecture.md`."
- architecture_v0.1.md mentions Playwright (§2 node B; §3 RenderLayer B1–B4) but takes no position on the boundary, and the document contains no open-questions section acknowledging the delegation.
- Further delegations to the architecture document, all unfulfilled there: Q-pm-2 (screenshot dimension normalization policy, L138), Q-pm-3 (diff persistence granularity, L139), Q-bs-2 (`approve` subcommand shape, L654), Q-tt-1 (clustering fresh design vs Java port, L767), CQ-2 (IR schema accommodating 12 types + confidence/fallback metadata, L794-795).

Why it matters: the boundary decides where the six transplanted functions execute, what the extraction layer's input contract is (live DOM vs serialized snapshots), where the IR is constructed, and it conditions AE-08. Every step of architecture §7's implementation order from step 2 onward inherits this undecided choice. This is a *delegation-unfulfilled* finding in the repository's own evaluation typology (ultimate_goal_eval_task.md §4, "위임-미실현 발견이 가장 가치 있습니다").

### AE-06 — The acceptance metrics the architecture pivots on are named but never defined
**Severity:** major. **Class:** coverage-gap + open-question.

Evidence:
- **Editability score:** appears as architecture §3 node G5, §2 report node Q; GOAL_PROBLEM §8 expected output (L789) and §9; reuse_report P1.1 Y-table row "mismatch_pixels → editability_score combination | us" (L84). No document defines how editability is measured (per object? PPTX XML inspection? interactive probe?). ULTIMATE_GOAL C2 delegates the operable-surface scope to GOAL_PROBLEM/reuse_report (L56); GOAL_PROBLEM enumerates *which* object types must be editable (L27-33) but not how editability is *verified*; reuse_report P1.2 §4 lists expectations ("re-typable", "row insertion", L175-179) with no measurement method.
- **"Important text"**: success criterion 1, "important text remains editable" (GOAL_PROBLEM L341) — "important" is undefined anywhere.
- **Thresholds:** architecture §2 decision node R ("Acceptable?") and GOAL_PROBLEM policy options "fallback threshold / validation threshold" (L318-319) have no owner and no defaults; Q-tt-2 (L768) acknowledges the fake-table threshold as empirical but assigns no decision point.
- **Reviewer authority:** ULTIMATE_GOAL UQ-4 (L206) asks which is authoritative when self-assessment and user evaluation disagree — open. Lifecycle diagram 01 has a single node "Reviewer decides: accept or request revision?" that does not distinguish the agent's pre-evaluation (C4) from the user's evaluation ((3)) — embedding UQ-4's ambiguity into the architecture as one undifferentiated actor.

Why it matters: "validated output > unverified output" and the §2/§6 accept/revise loops are only as real as the metrics at node R. As written, the loop's terminating condition is undefined; the agent's self-assessment cannot be implemented, and ULTIMATE_GOAL C4 has no concrete landing point beyond the report's *container* (GOAL_PROBLEM §9 defines the report's fields, not the fields' computation).

### AE-07 — Core priority order differs between README and GOAL_PROBLEM
**Severity:** minor. **Class:** internal-inconsistency.

Evidence: README.md L25-28 orders `editable > fidelity / reuse > new / validated > unverified / explicit fallback`, while GOAL_PROBLEM_v0.1.md L12-15 orders `editability > fidelity / validated > unverified / reuse > new / explicit fallback` — positions 2 and 3 swapped. architecture_v0.1.md does not restate the order.

Why it matters: the order is the project's declared tie-breaker. The two orderings answer differently when reuse and validation conflict — e.g., "adopt an existing unvalidated module now, or write new code on the validated path" (the exact shape of the AE-03 subtree-vs-transplant tension). Likely a transcription divergence, but it sits in the project's most-quoted four lines.

### AE-08 — Runtime/language topology is decided only inside a per-repo non-goal, and the architecture document says nothing about it
**Severity:** major (elevated from minor in the 2026-06-10 review: the project's confirmed direction toward a session/lifecycle/revision runner makes execution topology load-bearing — a revision runner must know where conversion, validation, and authenticated revision each execute). **Class:** undefined-boundary.

Evidence: the real decision exists — "Do not run Python in the bootstrap pipeline. Node-only." (reuse_report P1.6 §8 Case: Type, L759) — but lives in table_transformer's non-goals, not in the architecture. Post-bootstrap integration shapes (Python sidecar / CLI subprocess / ONNX, P1.6 §5.2 L737-744) are enumerated and undecided. `opendataloader_pdf_core` is a Java split-subtree candidate with `validation_command = "mvn test"` (subtrees.toml) — a Java build entering the tree with no consuming boundary defined anywhere. architecture_v0.1.md contains no statement about runtimes or languages in any layer.

Why it matters: combined with AE-05, the architecture currently specifies *what* the modules are but not *where anything executes* — browser vs Node vs subprocess vs JVM. The candidate pool spans three languages; the architecture's silence defers exactly the boundary the candidate analyses keep colliding with.

### AE-09 — Stale-name and path residue across documents
**Severity:** minor. **Class:** internal-inconsistency.

Evidence:
- README.md L166-167 ("Codex Web first task" expected outputs) still instructs producing `docs/architecture.md` and `docs/deletion_candidates.md`, while TASK.md L12-13 (G2-updated) says `docs/architecture_v0.1.md` / `docs/deletion_candidates_v0.1.md`. The G2 sed patterns covered only `ULTIMATE_GOAL|GOAL_PROBLEM|reuse_report` (git_g2_readme_task.md §4.3), so these two names were never in scope of the leak check.
- reuse_report_v0.1.md L135 and L139 ("recorded for `docs/architecture.md` … belonging to `docs/architecture.md` §validation"), P1.3 §8 ("see `docs/architecture.md` when written") reference the pre-rename file name; `architecture_v0.1.md` also has no "§validation" section for L139 to land on.
- GOAL_PROBLEM_v0.1.md L882 expects `docs/deletion_candidates.md` (unversioned) — three documents now name that future file three ways.
- Future `src/` layout vocabulary split: subtrees.toml adapters use `src/pptx/` (pptxgenjsAdapter) while reuse_report P1.3 §6.1 uses `src/output/` (normalize-zip), alongside TASK.md's `src/ir|extract|mapper|validate` placeholders.

Why it matters: individually trivial; collectively these are the seeds of the next "I-01-class" external finding, and L139 currently delegates open questions to a section that does not exist.

### AE-10 — Deletion-candidate tracking is a defined system module with no artifact, and reconciliation questions are queued to it
**Severity:** minor. **Class:** coverage-gap.

Evidence: GOAL_PROBLEM Technical Problem #10 (L866-905) defines deletion-candidate tracking as a built component with inputs/outputs/validation; TASK.md L13 and README L167 mandate the document; it does not exist. reuse_report CQ-3 (L796) and Q-d2p-2 (L418, quarterly upstream-diff review) queue the dom_to_pptx reclassification and sync policy specifically to this absent file — which is part of why AE-03's fork has no recorded reconciliation point.

### AE-11 — Verified-consistent set (positive observation)
**Severity:** observation. **Class:** (none — conformance record). See §2 items 1–7.

### AE-12 — Process residue affecting auditability (recorded, not for fixing here)
**Severity:** observation. **Class:** open-question (process).

Evidence: (a) the Cleanup commit (session_summary_v0.1.md §4.2, per MD-13/MD-14) is recorded as "남은 첫 작업" and not executed — all ten one-time files remain on `main`; (b) the external evaluation *report* (`docs/ultimate_goal_eval.md`, deliverable of ultimate_goal_eval_task.md §1) was never committed — only its five findings survive, summarized in session_summary §3.1; G4 §6 notes the evaluation had five P1 items of which three were processed, so two P1 findings are now unrecorded in the repository; (c) no `.gitignore` exists, while `scripts/clone_repos_from_toml.py` writes `third_party/repos/` and three clone-results files into the work tree (L20, L87-95) — a standing risk of accidental vendoring noted previously in this project's sessions; (d) **reverse local↔remote skew confirmed during the 2026-06-10 review**: the local working checkout lacks `docs/diagrams/architecture/`, `third_party/subtrees.toml`, and the `docs/subtree_*_v0.2.md` documents, all of which exist on remote `main`. Remote is the source of truth — the local checkout must be synced (`git pull`) before any further local work, including the commit of this document.

### AE-13 — Diagram governance scope (observation)
**Severity:** observation. **Class:** coverage-gap (tooling).

Evidence: `check_mmd_files.py` validates only standalone `.mmd` files (declaration prefix, no fences, no tabs); the five mermaid diagrams embedded in architecture_v0.1.md are outside any checker's scope. Diagram 01 exists in `en` only — permitted by the authoring skill's parity rule, recorded here for completeness.

### AE-14 — The live, revision-centric intent has entered the repository through the diagram layer while skipping the consensus layer
**Severity:** major. **Class:** open-question (+ coverage-gap at the consensus layer; the repository's own evaluation typology calls this 합의 누락 — consensus present in interviews but absent from documents, ultimate_goal_eval_task.md §4).

Evidence:
- Confirmed in the 2026-06-10 review: the user's current intent elevates the revision loop to a first-class, **multimodal, Codex-authenticated** workflow operating on **artifact sessions / scope sessions**, with HTML as the source of truth and PPT strictly as the evaluation surface.
- Already documented (no gap): "PPTX is a *vehicle for evaluation*" (ULTIMATE_GOAL_v0.1.md §2 L28); revisions flow through "new HTML artifact (loop)" (§6 L101-108).
- Partially documented (traces only): artifact sessions and the revision loop appear in diagrams 01–02 ("Artifact revision session", "Run revision workflow") and in the mmd-authoring skill's planned layer 6 — "create revision request bundle, **run authenticated revision**, register or publish revised source artifact" (mmd-diagram-authoring SKILL.md §Diagram Layers).
- Absent entirely from consensus documents: "multimodal", Codex authentication, and "artifact/scope session" as defined system constructs appear nowhere in ULTIMATE_GOAL_v0.1.md (incl. its YAML index) or GOAL_PROBLEM_v0.1.md.
- Governing rules: ULTIMATE_GOAL is the consensus repository and may not be modified without explicit user consent via interview (L7, MD-4); document-level conflicts resolve by fresh interview, not precedence (MD-2). session_summary_v0.1.md §4.3 already queues the 본질 인터뷰 (Q2/Q3/Q4) toward ULTIMATE_GOAL v0.2 — this finding adds the revision-centric elements to that interview's agenda.

Why it matters: this is AE-01 repeated one layer up. The new intent shaped the lifecycle diagrams and skill before touching the goal documents, so every evaluation, triage, or implementation grounded in the documented consensus — including this one — runs one step behind the live intent. Until ULTIMATE_GOAL advances to v0.2 by consented interview, the gap will silently widen with each diagram or task authored from the live intent.

---

## 4. Open questions for the user (one decision each; derived from findings)

- **OQ-1 (← AE-05, CQ-1/Q-d2p-1):** Playwright boundary — (a) transplanted functions execute inside `page.evaluate`, or (b) Node-side processing over computed-style snapshots?
- **OQ-2 (← AE-02):** Which PPTX→screenshot renderer becomes a tracked slot with its own candidate analysis (e.g., LibreOffice headless, PowerPoint automation, other)?
- **OQ-3 (← AE-03):** Which record is canonical for reuse decisions — `reuse_report` (evidence-based) or `subtrees.toml` (machine-readable) — and is `adopt_subtree(dom_to_pptx, whole_repo)` to be read as "vendor source *for transplant*" (compatible) or as superseding the no-runtime-dep decision (conflict)?
- **OQ-4 (← AE-04):** Adopt one canonical slot↔category↔module mapping (a single crosswalk table owned by one document)? (Yes/No; which document owns it is a follow-up.)
- **OQ-5 (← AE-06):** Who defines, and in which document, the editability-score computation, the meaning of "important text", and the acceptance thresholds at node R — and (UQ-4) which evaluator is authoritative on disagreement?
- **OQ-6 (← AE-07):** Which priority order is canonical: `validated` before `reuse` (GOAL_PROBLEM) or `reuse` before `validated` (README)?
- **OQ-7 (← AE-01):** Proceed with lifecycle diagrams 04 (conversion job) and 05 (validation evidence) — already planned in the mmd-authoring skill — as the binding layer between the lifecycle architecture and the pipeline architecture? (Yes/No; commissioning is a separate task.)
- **OQ-8 (← AE-14):** Conduct the consent-gated interview (MD-4) to advance ULTIMATE_GOAL to v0.2, with an agenda of: the pending Q2/Q3/Q4 (session_summary §4.3) plus the revision-centric elements — multimodal evaluation, Codex-authenticated revision, and artifact/scope sessions as system constructs? (Yes/No)

Per project protocol, answering these is interview work (one decision per turn); none is resolved in this document.

---

## Appendix A — Read audit (R1–R4; 43 / 43 files read, 0 excluded)

| Area | Files | Lines |
|---|---:|---:|
| Root: README.md | 1 | 236 |
| docs/ content documents (ULTIMATE_GOAL, GOAL_PROBLEM, architecture, reuse_report, session_summary, subtree_adoption_handoff, subtree_module_inventory — all `_vx.x`) | 7 | 2,962 |
| docs/ instruction documents (TASK, reuse_triage_task_A, ultimate_goal_eval_task, git_g1 v1/v3/v4, git_g2, git_g3 v1/v2, git_g4) | 10 | 1,889 |
| docs/diagrams/architecture/*.mmd (01.en, 02.en, 02.ko, 03.en, 03.ko) | 5 | 47 |
| third_party (repositories.toml, subtrees.toml, 6 manifests) | 8 | 375 |
| scripts (clone_repos.sh, clone_repos_from_toml.py) | 2 | 125 |
| skills/agent-collaboration (DESCRIPTION + 6 SKILL.md + 1 reference) | 8 | 818 |
| skills/architecture/mmd-diagram-authoring (SKILL.md + checker script) | 2 | 235 |
| **Total** | **43** | **6,867** |

State pinned by two independent `codeload` tarball fetches of `main` on 2026-06-10, byte-identical (drift check passed). Line evidence in this document refers to that state.
