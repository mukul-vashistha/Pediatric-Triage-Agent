# Week 2 Decision Record and Progress Log

Running log of decisions, findings, and open items for Week 2. Updated after each substantive decision or finding. Not a record of every message, only items relevant to the paper or to resuming work later. For current project status, see README.md.

---

## 1. File index

| File | Purpose |
|---|---|
| agent_v0.py | Snapshot prior to the S5 addition and seed fix. Not modified further. |
| agent.py | Active implementation. States, priors, likelihoods, all functions. |
| run_experiment.py | Empty. Intended as a thin script to import from agent.py and run the experiment separately from the engine logic. |
| research.md (Week 1) | Problem, objective, states, actions, signals, cost. |
| experiment.md (Week 1) | Belief table, priors, likelihoods, posteriors, thresholds, 17 test cases, failures, diagrams. |
| discussion-record.md | Continuous record, updated not replaced. Contains Week 1 and Week 2 X and Reddit exchanges. |
| v0_final.md | Week 1 narrative summary. |
| decision-record.md (this file) | Running log of decisions, findings, and open items. |
| docs/paper/ | Formal write-up: IJCAI-ECAI 26 format preprint (main.tex, ijcai26.sty, named.bst, paper.pdf). |
| v1_final.md (planned) | Week 2 narrative summary, same role as v0_final.md. |

---

## 2. Key numbers (seed 42, reproducible)

| Policy | Cost before S5 | Cost after S5 |
|---|---|---|
| P0 (baseline, always Monitor) | 870 | 960 |
| P2 (fixed E-A threshold agent) | 333 | 431 |
| P3 (value of information agent) | 142 | 180 |

Derived threshold: p* = C_FP / (C_FP + C_FN) = 1 / (1+30) ≈ 3.2%
Entropy: prior 1.57 bits, posterior after TC1 evidence 0.99 bits
KL divergence (TC2 against TC1): approximately 0.35 bits under the four-state model (later recomputed under the five-state model, see Section 13). Asymmetric; direction matters.

---

## 2b. Full metrics (seed 42, post-S5, with checks_used tracking)

| Metric | P0 | P2 | P3 |
|---|---|---|---|
| Accuracy | 0.68 | 0.31 | 0.64 |
| Precision | 0 (never flags) | 0.37 | 0.49 |
| Recall | 0.0 | 0.94 | 0.91 |
| Decision cost | 960 | 431 | 180 |
| Info cost | 0 | 66 | 560 |
| Avg. questions asked | 0.0 | 0.66 | 1.64 |
| Human review rate | 0.0 | 0.81 | 0.59 |

Total cost, decision plus info: P0 = 960, P2 = 497, P3 = 740

Finding: P3 has the lowest decision cost, highest precision, and lowest human-review load, but its information-gathering cost (560) is substantially higher than P2's (66), since it escalates through up to three evidence sources on ambiguous cases. Including info cost, P3's total (740) exceeds P2's (497). This is reported as a genuine trade-off rather than a clean win, consistent with the general principle that a policy dominating on every single metric usually indicates an error rather than a real result. Whether the trade-off (higher decision quality at higher information cost) is worthwhile depends on the real-world relative cost of a check versus a wrong decision; the simulation surfaces this question without resolving it.

Additional note: P2's raw accuracy (0.31) is lower than P0's (0.68) despite P2 being the better policy on cost and recall. This illustrates why accuracy alone is a poor summary statistic in an imbalanced setting.

---

## 2c. Task 5: five candidate evidence questions

| Question | Answers | Info value | Cost | Time | Policy |
|---|---|---|---|---|---|
| E-A: Is fluid intake normal? | Normal / Reduced | 0.118 bits | 1 | Instant | Always asked. Best value per cost. |
| E-C: Is temperature normal? | Normal / Elevated | 0.244 bits | 3 | A few minutes | Asked if still uncertain after E-A |
| E-E: Video review by clinician | Reassuring / Concerning | ~0.30 bits (estimate) | 5 | A few minutes | Asked if still uncertain after E-A and E-C |
| E-B: Doctor consult | Reassuring / Concerning | 0.364 bits | 8 | 15-30 minutes | Last resort only |
| E-D: Prior similar episode? | Yes / No | ~0.015 bits (estimate) | ~0 | Instant | Excluded from automatic policy; answer does not reliably change the action regardless of cost |

Correction: an earlier draft listed E-C's info value as approximately 0.08-0.09 bits. Correct value, verified in Stage 4: 0.244 bits.

Design change: E-C, E-D, and E-E added to agent.py. P3 escalation chain extended to E-A, E-C, E-E, E-B, ordered by info-per-cost ratio (0.118, 0.081, ~0.06, 0.046). E-D defined but excluded from the automatic chain per the value-of-information reasoning above.

Updated metrics after adding E-C, E-D, E-E:

| Metric | P0 | P2 | P3 |
|---|---|---|---|
| Accuracy | 0.68 | 0.31 | 0.75 |
| Precision | 0 | 0.37 | 0.58 |
| Recall | 0.0 | 0.94 | 0.91 |
| Decision cost | 960 | 431 | 131 |
| Info cost | 0 | 66 | 634 |
| Avg. questions asked | 0.0 | 0.66 | 1.87 |
| Human review rate | 0.0 | 0.81 | 0.50 |

Total cost, decision plus info: P0 = 960, P2 = 497, P3 = 765

Result: additional evidence sources improved P3's decision cost, precision, and accuracy further, while widening the total-cost gap against P2 (765 versus 497). This reinforces the earlier finding that P3's decision quality comes at a real information-gathering cost.

---

## 2d. Task 6: critical thinking challenge, real cases

Naive approach: rank by raw information gain, always run E-B first (0.364 bits, the highest value).

**Case 1, most informative check would have been wasted.** True state S3, evidence matching TC10 (lethargic, normal capillary refill, normal respiration). First posterior: P(High Risk) = 59.5%, already past the 40% emergency cutoff before any additional check. Result: Emergency, zero checks used. Running E-B would have cost 8 units and changed nothing.

**Case 2, cheapest check alone was sufficient.** True state S3, evidence matching TC13 (restless, mild tachypnea, reduced feeding, prolonged fussiness). First posterior: P(High Risk) = 39.0%, at the ambiguous boundary. One E-A check (cost 1) pushed the belief past 40%, resolving to Emergency. E-C, E-E, and E-B (up to 16 additional units combined) were not needed.

Rule: information has value only if some possible answer could change the action. Case 1 shows a decided case where even the best-value question is wasted. Case 2 shows the cheapest question alone resolving a genuinely ambiguous case. Ranking by raw information gain alone, without checking cost or decision-changing potential, is incorrect in both directions.

Code change: bottom execution block of agent.py wrapped in `if __name__ == "__main__":`, allowing functions to be imported for analysis without re-running the full 100-child experiment. No behavior change; output verified identical after the edit.

---

## 3. Findings for the Reflections section

1. Nurse-line and pediatrician actions collapsed into one threshold band in Week 1. Retained as-is; documented as an open question rather than patched.
2. Initial FN:FP cost ratio estimate: 100x, unreasoned. Implied threshold (~1%) would escalate nearly all cases. Revised to 30x. Resulting threshold: 3.2%, combined with a cheap escalation step.
3. The same asymmetry principle appears in two unrelated places: KL divergence is asymmetric depending on comparison direction; the cost structure is asymmetric because missing danger costs more than a false alarm.
4. Ranking evidence sources by raw information gain gives the opposite order from ranking by value per cost. E-B has the highest raw gain but the worst value per cost; E-A is the reverse. Consistent with a known pattern in information theory.
5. P3 costs roughly 3x less than P2 and roughly 15-20x less than P0, by skipping evidence gathering on already-decided cases and escalating through cheaper sources first on ambiguous ones.
6. Adding S5 raised cost for all three policies but did not remove P3's relative advantage. A genuinely unclassifiable state makes the problem harder without breaking the value-of-information strategy.
7. The simulation and the agent share the same likelihood tables. The experiment tests whether the policy logic is sound given those likelihoods; it cannot validate whether the likelihoods themselves are accurate. Stated directly in the Limitations section.

---

## 4. Concepts requiring multiple passes to resolve

- Distinguishing a likelihood question (if state X were true, how likely is this evidence) from a posterior question (given this evidence, how likely is state X). Caused a live calculation error on TC2 that required correction.
- Understanding why an evidence source's value requires a weighted average across every possible outcome, not the most dramatic-sounding one. Resolved using a spam-filter example.
- Understanding why a simulated answer (e.g., to E-A) must be drawn using the true hidden state, not the agent's current belief. Resolved using a "the coin already landed" framing.
- Nested loop structure in simulate_one_child: distinguishing the per-child loop from the loop comparing across the 17 test cases. Resolved using an analogy.
- Definition of S5: initial approach treated it as one specific unusual symptom combination, which is functionally an 18th test case. Correct framing: a case that does not fit the modeling framework at all, not a combination that was simply omitted.

---

## 5. Suggestions accepted

| # | Context | Suggestion | Outcome |
|---|---|---|---|
| 1 | Week 1 file organization | Keep research.md and experiment.md separate; merge at the end | Kept separate; merge pending |
| 2 | 4 actions vs. 3 threshold bands | Retain the collapse; document as an open question | Retained |
| 3 | Test case realism | Ground evidence in PEWS and IMCI criteria rather than sourcing a raw dataset | Adopted |
| 4 | HITL box in diagram | Remove rather than relabel or implement | Removed |
| 5 | Diagram styling | White boxes, colored borders and text | Adopted |
| 6 | FN:FP cost ratio | Revise the 100x estimate after reviewing the implied threshold | Revised to 30x; added E-A escalation step |
| 7 | Experiment sequencing | Build the matched simulator/agent version first; defer the mismatched version | Adopted |
| 8 | Code authorship | Code written directly, logic explained separately | Applied throughout Stage 8 |
| 9 | Evidence structure for simulation | Reuse the 17 hand-built test cases rather than construct ~48 new likelihood values | Adopted |
| 10 | Reusable helper functions | Single implementation of check_evidence_source and try_source, reused across E-A, E-C, E-B | Adopted |
| 11 | Random seed | Add random.seed(42), report it | Adopted |
| 12 | S5 residual state | Prior 0.03 (from S1), moderate flat likelihoods | Adopted |
| 13 | S5 definition | Broad "does not fit the framework" definition with one concrete example, rather than one specific symptom combination | Adopted |
| 14 | Real dataset (Patient Priority Classification, Kaggle) | Reference in Future Work rather than integrate now | Adopted |
| 15 | Versioning | agent_v0.py as frozen snapshot, agent.py as active file | Adopted |

## 6. Suggestions rejected or corrected

| # | Context | Issue | Resolution | Reason |
|---|---|---|---|---|
| 1 | Test case count | Miscounted as 10 | Corrected to 17 (TC1-TC17) | Factual error, corrected |
| 2 | Partial-miss cost value | No default suggested | Set to 20, between FP=1 and FN=30 | Independent judgment call |
| 3 | Baseline (P0) logic | Two options: hardcode "Monitor," or compute the max-probability state programmatically | Hardcoded | Priors are fixed for this experiment; dynamic computation adds no robustness |
| 4 | Umbrella problem cost inputs | Situation and cost scale requested | Provided directly | N/A |
| 5 | Simulation evidence model | Option A: ~48 new likelihood values across separate dimensions | Rejected in favor of reusing the 17 existing test cases | Time cost of untested new values versus reuse of verified ones |

---

## 7. Planned addition: interactive UI demo

Concept: a web interface allowing symptom entry, with live display of posterior updates, triggered checks, and the final action with its reasoning trail. A visual layer over the existing agent.py logic.

Status: planned for after the core deliverable is complete. Not part of the required write-up.

Requirement: a visible disclaimer ("Educational simulation only. Not medical advice. Always consult a real doctor or emergency service for actual symptoms."), since the interface produces triage-style output even in demo form.

Input design decision: present the 17 test case profiles as a single selectable list rather than three independent dropdowns. Rationale: guarantees every selectable input maps to a case with real likelihood values. Alternative considered and rejected: free combination of dropdowns with nearest-case matching for undefined combinations, rejected because it could present a result based on symptoms not actually selected by the user, even with disclosure.

Implementation plan: HTML/JavaScript reimplementation of the belief update logic, the 17-profile picker in place of free text, live posterior and entropy display, final action with a reasoning trail (checks asked, order, results).

---

## 8. Task 7: generalization challenge

**Environment shift:** baseline (urban, easy ER access, clear communication) versus a rural, resource-limited setting with a language or communication barrier.

**Scope note:** this section is written analysis only; agent.py, priors, thresholds, and evidence sources are unchanged. Purpose: demonstrate understanding of the design's limits, not rebuild it for a new setting.

### The 8 questions

**1. Which assumptions break?**
Both core assumptions fail together: that evidence questions can be reliably asked and understood, and that emergency evaluation means a short, low-friction trip.

**2. Which probabilities change, and in which direction?**
Initial estimate: P(S1) increases. Corrected on review: parents facing a real access barrier are more likely to seek care specifically for concerning cases, not mild ones. Conclusion: P(S1) decreases, P(S2) and P(S3) increase, since the population reaching the agent skews toward higher risk. This is selection bias in who seeks care, not a change in the underlying disease rate.

**3. Which costs change?**
Both C_FP and C_FN increase. C_FN increases because delay allows a condition to worsen. C_FP increases because an unnecessary trip becomes a substantive burden of travel time, cost, and lost work rather than a minor inconvenience.

Derived observation: since the threshold is p* = C_FP / (C_FP + C_FN), if both costs scale by a similar factor, the threshold changes only modestly despite both absolute costs rising. If C_FN grows faster than C_FP, which is plausible given how delay compounds risk, the threshold would still shift lower. No principled estimate of the relative growth rates is available; this is recorded as an open question rather than an assumed number.

**4. Which hidden states were missing?**
Not a new medical state. The model implicitly assumes that once an action (e.g., "go to Emergency") is recommended, it is executed without independent risk. In a resource-limited setting, travel itself introduces risk (accident, cost, symptom progression during transit). This is not specific to this model; most decision-support systems share the same assumption. More precisely described as an unmodeled cost attached to the action, not a missing state about the child.

**5. Which evidence becomes more important?**
Neither the worded questions (E-A, E-C) nor the video check (E-E) remain reliable by default under a language barrier. The video check has an independent failure mode (poor recording or lighting) unrelated to language. Proposed mitigation: convert worded questions into selectable options (yes/no, icons) rather than free text or spoken language, which would improve all worded evidence sources simultaneously.

**6. Which evidence becomes less important or unavailable?**
E-B (doctor consult) does not become less reliable; it becomes less available, since a doctor's judgment accuracy is unaffected if a connection is established, but establishing that connection is the real constraint. E-E (video) has a hard ceiling regardless of connection quality, since no video permits a pulse check or auscultation.

**7. Does the threshold stay the same?**
Addressed with question 3: if both costs move similarly, the threshold remains close to its current value, but could shift lower if C_FN grows faster.

**8. Does the human review policy stay the same?**
No. A local health worker positioned between the agent's recommendation and a hospital trip is proposed as a necessary addition. This differs from standard human-in-the-loop review, which approves or overrides an existing recommendation: the health worker adds a new evidence source (physical exam) and acts as a gatekeeper for further travel, a role broader than a simple approval checkpoint.

### Three variable-change prompts

**Prompt 1: C_FN increases 100x (30 to 3000).**

New threshold: p* = 1 / (1 + 3000) ≈ 0.033%.

Analysis: the most reassuring realistic evidence pattern across the 17 test cases reduces P(High Risk) to approximately 1-2% at best, still far above 0.033%. No evidence pattern can realistically bring a case below this threshold, meaning "Monitor" stops being a reachable outcome. The single-question fix used at the 30x ratio does not scale here: the threshold dropped roughly 100x, but the evidence sources' capacity to move belief did not change, since it remains bounded by the same likelihood values. Conclusion: beyond some cost ratio, threshold tuning is insufficient and the action set itself requires redesign.

**Prompt 2: evidence cost increases 10x (E-A=10, E-C=30, E-E=50, E-B=80).**

E-A's value-per-cost drops from 0.118 to 0.0118, a direct 10x reduction.

A fixed spending cap was proposed as a stopping rule. Limitation identified: a cap cannot distinguish a low-value question taken just before the limit from a high-value question skipped just after it. Resolution: a hybrid rule combining the existing stop rule with a cap as backstop. Note: expected information gain is computed from the likelihood tables before any question is asked, so the hybrid is not blind spending; it is rule-based stopping with a backstop.

Final rule:
1. Stop if nothing remaining could change the action.
2. Stop if the best remaining check now costs more than its known expected value.
3. Hard cost ceiling as backstop, rarely triggered if rules 1 and 2 function correctly.

Purpose of rule 3: protection against the possibility that rules 1 and 2's value estimates are themselves incorrect, for example if evidence sources are more correlated than assumed. Rule 3 bounds the resulting damage rather than preventing it. Suggested ceiling: cost of running all four sources at the new prices, plus margin.

**Prompt 3: priors become unreliable (population no longer matches the assumed S1-S5 distribution).**

Initial approach: count observed true-state frequencies directly. Rejected: the true hidden state is never observable in real deployment, only in simulation.

Working approach: for escalated cases, the pairing of stated confidence and eventual confirmed outcome is available. Bucketing predictions by stated probability and comparing against confirmed outcome rates within each bucket isolates a genuine calibration problem from an ordinary change in case volume (e.g., a seasonal increase in illness), which a raw case-count trend cannot distinguish.

**Task 7 status:** complete. All 8 questions and 3 prompts documented, ready for the paper's Generalization section.

---

## 9. Task 8: human escalation rules

Five standard escalation triggers mapped to the current design.

**Trigger 1, belief remains ambiguous after all affordable checks.** Already implemented: a case surviving the full E-A through E-B chain without resolving returns "Consult doctor," a human-in-the-loop outcome.

**Trigger 2, decision cost is high enough to matter regardless of confidence.** For infants under a threshold age (e.g., three months), a parent's ability to judge signs such as breathing effort or activity level is unreliable, affecting evidence quality rather than the calculation. Proposed rule: mandatory human review for cases below this age threshold, independent of the computed probability.

**Trigger 3, two evidence sources disagree strongly.** Not currently implemented. Each evidence source's result is fed sequentially into the next Bayesian update without checking for contradiction with the prior result. This is a known limitation: Bayesian combination assumes conditional independence between sources, and correlated or contradictory sources could have their disagreement silently absorbed. Proposed future implementation: compare consecutive posteriors and flag a case if belief moves in the opposite direction from the previous check.

**Trigger 4, case resembles nothing in the historical data.** Addressed by S5. A posterior leaning meaningfully toward S5 is a direct signal that the case does not fit the modeling framework, functioning as a human-review trigger without additional implementation.

**Trigger 5, calibration is drifting.** Connects to Prompt 3 above. A single incorrect case is not informative on its own; the relevant signal is a persistent, systematic gap across many cases (e.g., a "60-70% confident" bucket that is actually correct 90% of the time). This is a monitoring rule applied periodically across the case population, not a per-case check.

**Task 8 status:** complete. Four of five triggers map to existing design elements (thresholds, S5, calibration monitoring). Trigger 3 (source disagreement) is documented as an unresolved limitation.

---

## 10. Task 9: failure analysis

100-case run through P3; 6 cases labeled false negative or partial miss identified. 5 of 6 involved true state S5, indicating a code defect rather than independent hard cases.

### Failures 1-4: common root cause

Example: true_state S5, case TC11. First posterior: S1=0.87, S2=0.04, S3=0.04, S4=0.03, S5=0.015. The risk calculation (p_high = S2 + S3) computes 0.08, while score_case treats any state other than S1/S4 as high-risk, including S5. S5's probability mass is correctly computed but never included in the decision calculation.

Same pattern confirmed across all four cases: real S5 probability present in each posterior, never counted, because compute_action and compute_action_p3 define p_high as S2+S3 only, while score_case defines high-risk as anything other than S1/S4.

**Root cause:** inconsistency between the risk definition used for scoring (S2, S3, S5 = high-risk) and the risk definition used for the decision calculation (S2, S3 only).

**Classification:** wrong action policy. Belief tracking is correct; the mapping from belief to action is incorrect. Not a missing hidden state, since S5 exists and is tracked.

**Why this bug disproportionately affects S5:** S5 is designed as a low-probability catch-all across most evidence patterns, meaning it rarely dominates a posterior and is therefore easily dropped by an incomplete p_high calculation without producing an obviously wrong result in most cases.

### Failure 5: genuine miss, not a bug

True_state S3, case TC5. First posterior: P(High Risk) = 5.5%, S5 = 1.7%. Even with S5 correctly included (7.2% combined), the case remains within or near the low-risk band. This reflects genuinely reassuring-looking evidence for a case that was actually dangerous.

**Classification:** insufficient information. No correction to the decision logic would change this outcome.

### Summary table

| # | True state | Case | Classification | Cause |
|---|---|---|---|---|
| 1 | S5 | TC11 | Wrong action policy | Bug: S5 excluded from p_high |
| 2 | S5 | TC9 | Wrong action policy | Bug: S5 excluded from p_high |
| 3 | S5 | TC15 | Wrong action policy | Bug: S5 excluded from p_high |
| 4 | S5 | TC12 | Wrong action policy | Bug: S5 excluded from p_high |
| 5 | S3 | TC5 | Insufficient information | Genuine miss, not a bug |

### Design change and retest

Fix: p_high in try_source, compute_action_p3's initial check, and compute_action (P2) updated to S2 + S3 + S5, consistent with score_case.

Initial single-seed comparison (seed 42, matched children) showed the fix producing apparently worse results: accuracy 0.77 to 0.63, decision cost 129 to 210, recall 0.906 to 0.875.

Cause identified: random draws are sequential; changing decision logic changes how many random draws occur per child, shifting the draw sequence for subsequent children even under a fixed seed. A single-run comparison of old versus new logic is therefore not a controlled comparison unless run on identical, unmodified draw sequences.

Resolution: comparison repeated across 10 seeds. Average decision cost: old 135.3, new 111.2 (improvement). Average accuracy: old 0.733, new 0.695 (slight decrease). Direction of effect on any single seed is variable, since shifting a small amount of probability mass across the 3.2% threshold changes which children enter the evidence-gathering chain, which reshuffles each affected child's subsequent random draws rather than producing a uniform directional shift.

**Conclusion:** the fix is retained as logically correct, consistent with the risk definition used elsewhere in the code. A single-seed comparison would have produced a misleading conclusion; multi-seed comparison is required for any future design change of this kind.

**Task 9 status:** complete. Five failures identified and classified from real data. One code defect identified, fixed, and retested across multiple seeds, constituting the second required design-change-and-retest alongside the S5 addition.

---

## 11. Safety override layer (added following Task 9)

Gap identified: no mechanism existed to guarantee an immediate response to an unmistakably severe presentation independent of the Bayesian calculation. All decisions passed through priors, likelihoods, posteriors, and thresholds with no override path.

Decision: implement a hardcoded override rather than document this only as a limitation, consistent with standard practice in real triage tools (e.g., PEWS red-flag overrides: a small set of signs triggering immediate escalation regardless of the calculated score).

Override criteria: unresponsive to stimulation, mottled skin, severe respiratory distress. Any single sign is sufficient to trigger the override; co-occurrence is not required, since each sign independently justifies immediate escalation without waiting for probabilistic confirmation.

Implementation: check_red_flags(evidence_text), a keyword match against the raw evidence string, executed before any Bayesian reasoning. A match sets the action to Emergency evaluation with zero checks used, bypassing the belief update and threshold logic.

Scope: applied to P2 and P3 only. P0 is excluded by design, since it represents a no-intervention baseline and a safety layer would undermine its function as a comparison point.

Verification: TC6 (lethargic, gray/mottled >5s, severe tachypnea) and TC16 (unresponsive to stimulation, mottled skin, severe respiratory distress) are the only test cases triggering the override. Both cases already typically resolved to Emergency based on their likelihood values, so the override does not change typical behavior; it removes the residual possibility that the probabilistic calculation alone could produce an incorrect result for these specific presentations.

---

## 12. AI-use statement

Claude was used to explain concepts (Bayesian updates, entropy, information gain, KL divergence, calibration) prior to each corresponding hand calculation, and to identify specific errors (the TC2 likelihood/probability mix-up, the unreasoned 100x cost-ratio estimate). All hidden states, priors, likelihoods, and cost assumptions were authored independently. All code in agent.py was written independently, with logic explained before implementation and reviewed afterward, which is how the S5-exclusion bug was identified. All simulations were run independently using a fixed seed (42). Drafting assistance was used for structuring the paper and this decision record; the underlying reasoning, corrections, and conclusions were developed independently.

---

## 13. Paper writing: a correction caught mid-draft

Correction identified while drafting the Information-Theoretic View section: the KL divergence value (0.35 bits, TC2 vs. TC1) had been computed under the four-state model, prior to the S5 addition. Recomputed under the current five-state model.

Updated values: KL(TC2 || TC1) = 1.06 bits, KL(TC1 || TC2) = 0.91 bits. Both higher than the original 0.35-bit figure, consistent with the change in both posteriors following the S5 addition. Asymmetry direction unchanged; the connection to the FN/FP cost asymmetry remains valid with the corrected values.

---

## 14. Reading list and Related Work

Four sources read in full and incorporated into the paper's Related Work section:

1. ED-PEWS validation in low- and middle-income countries (PMC10956749): confirms that objective, non-verbal evidence performs better under language barriers, supporting the generalization analysis (Section 8).
2. PEWS implementation barriers in a resource-limited setting (PMC10050749): establishes that adapting escalation steps to local resource constraints is a requirement rather than an optional refinement, sharpening the local-health-worker proposal (Section 8).
3. Barriers to AI clinical decision support systems (JMIR 2025/1/e63377): introduces "automation bias" as the specific failure mode addressed by the human escalation rules and the safety override.
4. PED-IA (a pediatric telephone triage decision support system tested with 51 practitioners, Computers in Biology and Medicine, 195:110645): its principal finding, decision accuracy improved significantly with system use at the cost of significantly increased decision time, matches the shape of this project's own decision-cost-versus-information-cost trade-off.

Author names for the first three sources are not confirmed against the published versions and are flagged as pending verification rather than stated with confidence.

A separate finding worth recording: reviewing discussion-record.md turned up a Reddit exchange (the "question selection and decision-layer design" post, r/LLMDevs) about insufficient validated data for a probabilistic model, in which a response had already committed to a safety-layer-first approach, predating the actual implementation of the hardcoded safety override by a substantial margin. Public discussion anticipated a design decision made later, independent of that discussion.

---

## 15. Choosing the paper's format

The official IJCAI-ECAI 26 author kit was used (ijcai26.sty, named.bst), replacing an earlier hand-built substitute style, since the genuine style file produces standard conference formatting rather than an approximation.

Page count: the compiled paper is 10 pages. The IJCAI conference submission limit (7 pages plus 2 for references) applies to competitive conference review, which is not the context of this deliverable; the applicable target for this project is 8-14 pages, which explicitly includes content (the 20-question appendix, full failure analysis) not found in an actual conference submission. No content was cut to match the IJCAI limit, since doing so would remove material required by the actual project scope rather than by IJCAI's own submission rules.