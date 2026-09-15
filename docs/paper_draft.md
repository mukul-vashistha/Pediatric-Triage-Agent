# Deciding When to Wait, Ask, or Escalate: A Bayesian and Information-Theoretic Approach to Pediatric Home-Triage Under Uncertainty

## 1. Abstract

When a parent has to decide whether a child's symptoms mean "wait and watch," "see a doctor," or "go to the emergency room," that decision is made without ever really knowing what is actually wrong. This paper builds a small AI system for exactly that situation, aimed at recommending an appropriate level of care rather than a diagnosis. Instead of producing a single answer, the system tracks how likely five different possibilities are (including a category for cases that do not fit a clean pattern), and updates those odds as new information arrives, similar to how a clinician's suspicion shifts with each additional question. The system decides for itself when it is worth asking one more question and when it already knows enough to act, weighing what each question costs against how much it is likely to help. A hardcoded safety rule sits in front of this entire process: a small number of unmistakably dangerous signs bypass the calculation and lead directly to a recommendation for emergency care, regardless of what the underlying math says. Three versions of the system were compared on 100 simulated cases: one that takes no evidence into account at all, one that always asks the same fixed question, and one that selects its own questions based on value for cost. The most capable version produced noticeably better decisions overall, but also spent more effort gathering information to do so, a real trade-off this paper reports directly rather than minimizing. Reviewing the system's own mistakes surfaced a genuine implementation defect, one of the five states (S5) was being silently excluded from the risk calculation, which was corrected and retested properly. The paper closes with an honest account of where the system's assumptions would break down, particularly in a resource-limited setting, along with several open questions the results raised without a clean answer.

## 2. Introduction

Whenever a parent describes a child's symptoms to anyone, what is actually being conveyed is an incomplete, sometimes unreliable picture of something that cannot be directly observed: the child's true condition. A system that returns a single confident answer from that picture discards the one thing that matters most, how certain it actually is, along with the ability to say "there is not enough information here, involve a person." This project treats that uncertainty as something worth modeling directly, rather than something to be hidden behind confident language. This is also why the agent is built to recommend an appropriate level of care rather than attempt a diagnosis.

Asking a general-purpose chatbot what to do with a list of symptoms is not sufficient here, for two reasons. First, sounding confident and being correct are not the same thing; a system can state something with complete confidence and still be wrong far more often than that confidence would suggest. Second, and more fundamentally, the real difficulty in this problem is not producing an answer at all, it is deciding what to do next: whether another question is worth asking, what it would cost, and whether the case is already clear enough that asking further would only waste time. Reasoning about this requires an explicit belief and an explicit cost model, not a fluent response.

This agent therefore tracks five possibilities at once, updates their likelihood using Bayes' rule as evidence arrives, and selects among three final actions using a threshold derived from the real cost of each type of mistake. What to ask next, and when to stop asking, are treated as decisions in their own right, weighed by value against price rather than by how much a question teaches in isolation. Section 4 describes the belief system in full, Section 6 covers how evidence is selected, Section 7 covers the decision rule, and Sections 8 through 10 cover the experiment, its results, and a real implementation defect that was identified and corrected.

## 3. Related Work

**Real-world evidence that objective signs outperform worded questions under a language barrier.** A study evaluating an early-warning tool across hospitals in lower-resource countries found that it identifies at-risk children effectively using only signs a clinician can directly observe, independent of how well a parent can describe symptoms in words. This independently confirms the argument developed in Section 11, that objective evidence should outperform worded questions when a language barrier is present, and demonstrates that a real tool is already built around that principle.

**Adapting a triage tool to local resources is a requirement, not an optional refinement.** A second study examined what determines whether an early-warning score succeeds or fails once deployed in a resource-limited hospital, finding that success depends on adapting the tool to local equipment and staffing. This elevates the local-health-worker proposal in Section 11 from a suggestion to something closer to a necessary design element.

**A named concept for a risk this design already guards against.** A third study interviewed practitioners deploying AI decision-support tools in real hospitals and found that the primary barriers are rarely the algorithm itself; they involve trust, workflow integration, and a phenomenon termed "automation bias," in which users stop scrutinizing a system's recommendations over time. This is precisely what the human-escalation rules and the hardcoded safety rule (Sections 7.3 and 7.4) are designed to prevent.

**An independently built clinical system exhibits the same trade-off reported here.** A pediatric telephone triage decision-support system, evaluated with 51 practitioners, showed the same pattern found in this project: improved decision accuracy accompanied by longer decision times. The trade-off is structurally identical, better reasoning at a higher cost, expressed in a different unit (clinician time rather than information-gathering cost). This provides independent support that the trade-off reported in Section 9 reflects a general pattern rather than an artifact specific to the cost values chosen in this project.

A public dataset, the Patient Priority Classification dataset (Kaggle), was also identified as a potential source for validating the assumed likelihood values against real symptom co-occurrence patterns. It has not yet been integrated into this project and is noted as future work in Section 13.

This project has also been discussed publicly on LinkedIn and Reddit. One Reddit post presented the finding that the more capable system in this project has lower decision cost but higher total cost once information-gathering is included, and asked whether this pattern is expected or indicates a miscalibration in the cost assumptions. No replies had been received at the time of writing, which is reported directly rather than treated as an implicit result.

## 4. Probabilistic View

### 4.1 Problem Statement

The agent observes a child's symptoms as reported by a parent. It must select one of three actions, monitor at home, consult a doctor, or seek emergency evaluation, because the child's underlying condition is not directly observable and the information provided by the parent is incomplete.

### 4.2 Hidden States (The Five Possible Underlying Conditions)

The agent never has direct access to a child's true condition. It observes only symptoms and must infer the underlying state from them. Rather than committing to a single explanation, it maintains five possibilities simultaneously and estimates the likelihood of each:

- **S1, genuinely low risk:** the child is actually fine, and the symptoms reflect that.
- **S2, genuinely high risk, apparent:** the child is genuinely at risk, and the symptoms make this evident.
- **S3, genuinely high risk, concealed:** the child is genuinely at risk, but the symptoms appear mild or ambiguous. This is the most dangerous case, since risk is present without a clear signal.
- **S4, false alarm:** the symptoms appear concerning, but the child is actually fine.
- **S5, unclassifiable:** the case does not reliably match any of the above, either because the presentation is genuinely atypical or because the parent's description is too sparse or inconsistent to place with confidence.

S5 was not part of the original design. It was added after a realization made while working through KL divergence (Section 5): if a possibility is never included in the model, no amount of evidence can direct the agent toward it, since it is simply not an option the system recognizes. Omitting a real possibility altogether proved to be a substantially more dangerous error than leaving belief distributed across the possibilities already accounted for.

### 4.3 Prior Belief (The Starting Assumption Before Any Evidence)

Before observing any symptoms, the agent begins with the following belief about a typical case:

| State | Starting belief | Basis |
|---|---|---|
| S1, genuinely low risk | 57% | Assumed, based on the expectation that most parent-initiated queries concern non-emergencies |
| S2, genuinely high risk, apparent | 20% | Assumed |
| S3, genuinely high risk, concealed | 10% | Assumed |
| S4, false alarm | 10% | Assumed |
| S5, unclassifiable | 3% | Assumed, deliberately small since this state is intended to be rare |

These values are explicit assumptions, not measurements from real patient data, and are labeled as such throughout. They sum to 100 percent, since together they are intended to cover every real possibility.

### 4.4 Evidence (What the Agent Actually Observes)

The agent primarily works from a parent's description of symptoms. To make this usable, a library of 17 example symptom patterns was constructed (TC1 through TC17), each combining a behavioral state (normal, sleepy, irritable, or lethargic), a circulation and skin appearance, and a respiratory pattern. These categories are drawn from the Pediatric Early Warning Score, a clinical tool used in practice. For each of the 17 patterns, a likelihood value was assigned for each of the five states, representing how likely that pattern would be to occur if that state were actually true. These values reflect judgment rather than measurement and are labeled accordingly.

If the initial pattern alone does not resolve the case, the agent can request up to four additional pieces of evidence:

- **E-A:** is the child's fluid intake normal, or reduced?
- **E-C:** is temperature normal, or elevated?
- **E-E:** a short video reviewed by a clinician, assessed as reassuring or concerning?
- **E-B:** a live doctor consult, assessed as reassuring or concerning?

A fifth candidate question, whether the child has had a similar episode before that resolved without intervention, was designed but deliberately excluded from the automatic policy. Although it costs almost nothing to ask, its answer rarely changes the outcome, making it not worth asking despite its negligible cost. This reasoning is developed further in Section 6.

### 4.5 Worked Example (One Full Case, Computed by Hand)

The following shows what happens when the agent observes the TC1 symptom pattern (mild symptoms, normal breathing, normal hydration, alert child). The likelihood of this pattern under each state is 0.80 for S1, 0.20 for S2, 0.40 for S3, 0.30 for S4, and 0.25 for S5.

| State | Starting belief | Likelihood of this pattern under this state | Product | Updated belief |
|---|---|---|---|---|
| S1 | 0.57 | 0.80 | 0.456 | 0.740 |
| S2 | 0.20 | 0.20 | 0.040 | 0.065 |
| S3 | 0.10 | 0.40 | 0.040 | 0.065 |
| S4 | 0.10 | 0.30 | 0.030 | 0.049 |
| S5 | 0.03 | 0.25 | 0.0075 | 0.012 |
| Total | 1.00 | -- | 0.6165 | 1.00 |

The computation is straightforward: each state's starting belief is multiplied by the likelihood of the observed evidence under that state, the resulting column is summed to obtain 0.6165, and each product is divided by that total to yield the updated belief. This is the complete mechanism underlying every belief update in this system, applied repeatedly as new evidence arrives.

### 4.6 Measuring Uncertainty

Before any evidence is observed, the agent's uncertainty measure sits at 1.61 bits. After observing the TC1 pattern above, it falls to 1.13 bits, indicating that the evidence meaningfully increased confidence. This is consistent with expectation: mild, unremarkable symptoms should shift belief toward the low-risk state, which is exactly what occurred.

### 4.7 Deriving the Decision Threshold

Rather than selecting a threshold by intuition, the threshold was derived from the relative cost of each type of error. Sending a genuinely healthy child for unnecessary evaluation costs 1 unit in this accounting. Missing a genuinely dangerous case costs 30 units. Balancing these two costs produces a threshold of approximately 3.2 percent: below this level, monitoring is the safer choice; above it, action is warranted.

The 30-to-1 ratio was not the initial estimate. An initial estimate of 100-to-1 was based on intuition about how much worse a missed diagnosis is than an unnecessary referral. Working through the implication of that ratio (a threshold near 1 percent, which would escalate nearly every case) revealed that the estimate reflected an emotional response to the stakes rather than a reasoned judgment, and it was revised down to 30-to-1. Even at this ratio, a simple two-outcome policy (monitor or escalate) still appeared overly aggressive, since many cases fall just above 3.2 percent without being genuinely concerning. This motivated the addition of one inexpensive intermediate question before committing to a larger decision, rather than escalating immediately at the threshold.

The resulting rule: below 3.2 percent, monitor at home. Between 3.2 and 40 percent, gather additional evidence before deciding (Section 6). Above 40 percent, proceed directly to a recommendation for emergency care without further evidence-gathering, since no additional information at that point could plausibly change the outcome.

A hardcoded rule sits above this entire calculation. If the reported symptoms include any of three unmistakable danger signs, the child being unresponsive, mottled skin, or severe respiratory distress, the agent recommends emergency care immediately, bypassing the probabilistic calculation entirely. The rationale is direct: for a small set of genuinely unambiguous signs, waiting for a probability calculation to concur adds delay without any offsetting benefit.

## 5. Information-Theoretic View

This section draws on several ideas from information theory, the branch of mathematics concerned with measuring what is actually known. Only the concepts used directly in this project are covered, each explained in plain terms before the corresponding value from this project is given.

**Entropy, a measure of present uncertainty.** This is a single number describing how spread out or uncertain a belief is. A confident belief produces a low value; a belief genuinely divided among several possibilities produces a higher one. Before any symptoms are observed, this value is 1.61. After observing the TC1 pattern (mild symptoms, normal breathing), it falls to 1.13, indicating the evidence increased confidence (see Section 4.6 for the full calculation).

**Information gain, the expected value of a question.** This measures how much a piece of evidence is expected to reduce uncertainty, averaged across every answer it could return, not only the answer one might anticipate. For the fluid-intake question, this comes to 0.118. The calculation: 68 percent of the time the answer returns "Normal," leaving 1.34 bits of remaining uncertainty; 32 percent of the time it returns "Reduced," leaving 1.69 bits. Averaging these outcomes and comparing to the starting value produces the 0.118 figure.

**Conditional entropy, the expected uncertainty that remains.** This is the complementary quantity to information gain: rather than measuring how much uncertainty is expected to decrease, it measures how much is expected to remain. For the fluid-intake question, this is the 1.45 weighted average described above, the value obtained before subtracting from the starting uncertainty.

**Mutual information, whether one variable reveals anything about another.** This measures whether knowing one quantity provides any information about a second, including non-linear relationships that ordinary correlation would fail to detect. It is mathematically identical to information gain, expressed in the vocabulary of a different field. No separate example was constructed for it in this project, since it reduces to the same calculation already in use.

**KL divergence, the cost of trusting the wrong belief.** This measures how different two beliefs are from one another, with the notable property that it is not a symmetric measure, unlike a physical distance. Treating the TC1-derived belief as the expectation and the TC2-derived belief as the outcome yields a divergence of 1.06; reversing the comparison yields 0.91. The same two beliefs produce different values depending on which is taken as the starting point. This asymmetry is not incidental: it mirrors a design choice already made elsewhere in this project, where missing genuine danger is treated as 30 times more costly than a false alarm. Both are expressions of the same underlying principle, that the two directions of error are not equally costly.

**Calibration, whether stated confidence matches outcomes.** This is not a property of any single decision, but of whether stated confidence levels are trustworthy across many cases. This project does not implement an empirical calibration check, primarily because doing so requires a confirmed real-world outcome for every case, and such confirmation is only available for cases that were actually escalated. Sections 11 and 13 describe the method that would be used: group predictions by stated confidence and compare against confirmed outcomes across many cases, rather than evaluating calibration from any single case.

Jensen-Shannon divergence, a symmetric and bounded alternative to KL divergence that never produces an unbounded value, was reviewed conceptually but is not used numerically in this project.

## 6. Information Selection

Five candidate questions were designed and compared not only on how much information each would provide, but on how much it would provide relative to its cost. The governing principle throughout: a question is worth asking only if some possible answer could change the resulting action. A question can carry substantial information and still have no practical value if no outcome would alter the decision.

| Question | Possible answers | Information value | Cost | Time | Policy |
|---|---|---|---|---|---|
| E-A: Is fluid intake normal? | Normal / Reduced | 0.118 | 1 | Instant | Always asked; best value for cost. |
| E-C: Is temperature normal? | Normal / Elevated | 0.244 | 3 | A few minutes | Asked if still uncertain after E-A. |
| E-E: Clinician video review | Reassuring / Concerning | approximately 0.30 | 5 | A few minutes | Asked if still uncertain after E-A and E-C. |
| E-B: Live doctor consult | Reassuring / Concerning | 0.364 | 8 | 15-30 minutes | Reserved as a last resort. |
| E-D: Prior similar episode? | Yes / No | approximately 0.015 | negligible | Instant | Excluded from the automatic policy; the answer rarely changes the outcome regardless of its low cost. |

Ranking these sources by raw information value produces the order E-B, E-E, E-C, E-A. Ranking by value per unit of cost inverts this almost entirely: E-A, E-C, E-E, E-B. The agent follows the second ordering, asking the inexpensive fluid-intake question first, proceeding to temperature and video review only if the case remains unresolved, and reserving the doctor consult, the most informative but also most expensive option, for cases that persist through the cheaper checks.

E-D illustrates why cost alone is not a sufficient criterion. Despite costing almost nothing, its answer is nearly identical regardless of the true state, meaning it provides little practical value regardless of price.

### 6.1 Value Versus Raw Information

A natural but incorrect assumption is that the most informative question is always the correct one to ask first, which by raw value would be E-B. Two real cases from the experiment illustrate why this assumption fails.

**A case in which the most informative question would have been wasted.** One simulated child was genuinely at risk (S3), and matched a symptom pattern that produced a first-pass belief of 59.5 percent, already past the 40 percent threshold for emergency care before any additional question was asked. The agent correctly proceeded directly to a recommendation for emergency evaluation without asking further questions. Running the doctor consult regardless would have cost 8 units and changed nothing, since the case was already conclusively decided.

**A case in which the least expensive question alone was sufficient.** A second child, also genuinely at risk, produced a first-pass belief of 39.0 percent, just below the threshold. A single fluid-intake question, at a cost of 1 unit, pushed the belief past 40 percent and correctly resolved the case. The three more expensive questions, which together would have cost up to 16 units, were never required.

The principle drawn from both cases: information has value only if some possible answer could change the resulting action. Ranking questions by raw information value alone, without accounting for whether a case is already resolved or whether a cheaper question would suffice, produces incorrect conclusions in both directions.

## 7. Decision Policy

### 7.1 Action Set

The agent selects one of three final outcomes: monitor at home, consult a doctor, or seek emergency care. Requesting additional evidence is not itself a final outcome; it is an intermediate step taken on the way to one of the three.

### 7.2 Deriving the Threshold from Cost

The threshold used by the agent is derived from cost rather than chosen for plausibility. With an unnecessary escalation costed at 1 unit and a missed dangerous case costed at 30 units, the break-even point is:

threshold = 1 / (1 + 30) ≈ 3.2%

This ratio underwent one substantive revision. An initial estimate of 100-to-1, based on intuition regarding the relative severity of the two error types, produced a threshold near 1 percent, which would have escalated nearly every case. Recognizing this as an emotionally driven rather than reasoned estimate, the ratio was revised to 30-to-1. Even at this revised ratio, a plain two-outcome threshold still appeared overly aggressive, since a substantial share of cases fall just above 3.2 percent without being genuinely concerning. This motivated the addition of an inexpensive intermediate question rather than escalating immediately upon crossing the threshold.

### 7.3 The Stop Rule

Given the current belief about a case, the agent follows this sequence:

1. If the estimated risk is below 3.2 percent, monitor at home immediately, with no further questions.
2. If the estimated risk exceeds 40 percent, proceed directly to a recommendation for emergency care. No remaining question at this point could plausibly reduce the belief below this threshold, so asking further would only add delay.
3. Otherwise, questions are asked in order of value for cost, fluid intake, then temperature, then video review, then doctor consult, with the belief re-evaluated after each answer. The agent stops as soon as the case resolves, never proceeding to a more expensive question than necessary.

This procedure follows directly from the principle established in Section 6: continuing to spend on evidence once a case is already resolved adds cost without adding value.

The hardcoded safety rule sits above this entire procedure. If the reported symptoms include any of three unmistakable warning signs, unresponsiveness, mottled skin, or severe respiratory distress, the agent proceeds directly to a recommendation for emergency care, bypassing the belief calculation and threshold logic entirely. This rule was added after recognizing that while every actual error identified in this project traced to either a genuinely difficult case or a since-corrected calculation defect, nothing in the design protected against the simple possibility of a coding or modeling error overlooking an unmistakable danger sign. A small set of signs is treated as sufficiently dangerous, on its own, that waiting for a probabilistic calculation to concur introduces risk without any corresponding benefit. Any one of the three signs alone is sufficient to trigger the rule; co-occurrence is not required.

### 7.4 Human Escalation Rules

Beyond the belief-driven procedure above, five conditions warrant human involvement, in some cases independent of the calculated probability.

1. **The case remains unresolved after all affordable questions have been asked.** This occurs automatically: a case that survives the full sequence of questions without resolving is directed to a doctor consult, which itself places a person in the decision loop.
2. **The evidence itself cannot be trusted, regardless of the calculated result.** For infants below a threshold age, for example three months, a parent's ability to accurately judge signs such as breathing effort or activity level is limited. This is a limitation of the evidence rather than the calculation, and cases involving infants below this age are proposed for mandatory human review regardless of the computed probability.
3. **Two pieces of evidence point in clearly different directions.** This is an acknowledged, currently unaddressed limitation. Each answer is incorporated sequentially into the next calculation without any check for contradiction with the previous result. A future version could compare consecutive belief updates and flag a case for review if a new answer shifts belief in the opposite direction from the prior one, rather than silently combining conflicting signals.
4. **The case resembles nothing the system has previously encountered.** This is precisely the role of S5. A belief that leans substantially toward S5 is the system's own indication that it lacks a confident interpretation of the case, functioning as a built-in signal for human review.
5. **The system's confidence appears to be drifting from reality.** This is not a per-case signal but one observed only across many cases over time: grouping predictions by stated confidence and checking whether outcomes actually match that confidence. A persistent, systematic gap is the relevant warning sign, not any single incorrect case.

In a resource-limited setting, a sixth form of human involvement is proposed: a local health worker positioned between the system's recommendation and an actual hospital visit. This is not equivalent to a simple review of the system's output; it introduces a genuine additional source of evidence, a physical examination the system cannot perform, and a judgment on whether further travel is warranted. This is developed further in Section 11.

## 8. Experiment

### 8.1 Experimental Setup

100 simulated cases were generated. For each case, a true underlying state was drawn according to the starting beliefs in Section 4.3, and a symptom pattern consistent with that state was drawn from the 17 example patterns. The system under evaluation was never given the true state, only the symptoms, and the true state was consulted only after a decision had already been made, to score the outcome. The random seed was fixed at 42 and is reported here so that the experiment can be exactly reproduced. All three systems below were evaluated on the identical set of 100 cases, so any difference in outcome reflects a difference in policy rather than in the random cases each system happened to receive.

### 8.2 Policies Compared

- **P0, a baseline that ignores all evidence:** always recommends monitoring at home. This exists specifically to establish whether the more sophisticated policies provide real benefit, since a policy this simple can appear misleadingly strong on raw accuracy alone if most cases are genuinely benign.
- **P2, a fixed-question policy:** evaluates the initial symptoms and, if still uncertain, always asks the same single inexpensive question (fluid intake) before making a final decision.
- **P3, a value-of-information policy:** evaluates the initial symptoms and, if still uncertain, works through up to four questions in order of value for cost, stopping as soon as the case resolves.

Both P2 and P3 operate behind the hardcoded safety rule described in Section 7.3. P0 does not, by design, since it is intended to represent the absence of any intelligent evaluation, and adding a safety layer to it would undermine its function as a baseline.

### 8.3 Evaluation Metrics

A case is classified as positive (genuinely high-risk) if the true state was S2, S3, or S5, and negative otherwise. Accuracy measures how often the final decision was correct. Decision cost sums the cost of every incorrect outcome (1 for an unnecessary escalation, 20 for directing a genuinely high-risk child to a doctor rather than emergency care, 30 for sending a genuinely high-risk child home). Information cost sums the cost of every question actually asked. Questions asked reports the average number of additional questions per case. Human-review rate reports how often the final recommendation was anything other than monitoring at home, since both a doctor consult and an emergency recommendation involve a person.

## 9. Results

| Metric | P0 (no evidence) | P2 (fixed question) | P3 (value-of-information) |
|---|---|---|---|
| Accuracy | 0.68 | 0.27 | 0.66 |
| Precision | 0 | 0.34 | 0.49 |
| Recall | 0.0 | 0.94 | 0.84 |
| Decision cost | 960 | 397 | 198 |
| Information cost | 0 | 73 | 736 |
| Average questions asked | 0.0 | 0.73 | 2.13 |
| Human-review rate | 0.0 | 0.87 | 0.55 |

Total cost, decision cost plus information cost: P0 = 960, P2 = 470, P3 = 934.

Three observations from this table warrant direct attention.

**Accuracy alone is misleading in this setting.** P2's raw accuracy (0.27) is lower than that of the baseline that ignores all evidence (0.68), despite P2 being the clearly more useful policy by cost and recall. This occurs because most simulated cases are genuinely benign, so a policy that never escalates accumulates a large number of accidentally correct outcomes, while a more cautious policy that flags genuine concerns also accumulates unnecessary flags that count against it on this single measure.

**P3 produces clearly superior decisions.** Its decision cost (198) is substantially lower than either alternative, and it improves both recall and precision relative to P2.

**P3 achieves this at substantially higher information cost.** Once the cost of its additional questions is included, P3's total cost (934) approaches, and slightly exceeds, that of the baseline, and is well above P2's. P3 is willing to ask up to four questions per unresolved case, which accumulates. Whether this trade, improved decisions at the cost of more questions asked, is worthwhile depends entirely on the real-world relative cost of a question versus an incorrect decision, a judgment this experiment surfaces but does not resolve.

## 10. Failure Analysis

Five real cases in which the system produced an incorrect outcome (either missing a genuinely dangerous child or under-escalating one) were examined individually.

**Four of the five shared a common cause, and it was a genuine defect rather than four independent difficult cases.** All four involved children whose true state was S5. Examination of the underlying calculation revealed that the risk value used to determine escalation summed only the S2 and S3 probabilities, never including S5, even though the separate scoring function used to evaluate outcomes correctly treated S5 as high-risk. S5's probability was being tracked correctly throughout; it was simply not included where it mattered for the decision. The belief itself was not wrong; the rule connecting belief to action was.

**The fifth case was a genuine miss, not a defect.** This child was genuinely at risk, but the observed symptoms appeared reassuring enough that the estimated risk was only 5.5 percent, well below the threshold for further action. No reasonable correction to the decision logic would have caught this case; it reflects an honest limitation of the available information.

**Correcting the defect and verifying the correction.** The risk calculation was updated in every location where it appeared to correctly include S5 alongside S2 and S3. An initial comparison of the original and corrected logic on a single set of 100 cases appeared to show the correction making outcomes worse (lower accuracy, higher cost), which was unexpected given that the correction was clearly appropriate. Repeating the comparison across 10 different random starting points resolved this: on average, the correction genuinely reduces cost, but it also introduces variability in how it plays out on any individual run, because shifting a small amount of probability across the decision threshold changes which children require additional questions, which in turn reshuffles the subsequent random outcomes for those children. A comparison based on a single run would have produced an incorrect conclusion; only the comparison across many runs produced a reliable result.

**A further addition made in response to this analysis.** Reviewing these failures identified a separate concern: nothing in the design guaranteed an immediate response to an unmistakably severe case if the probabilistic calculation were incorrect for any reason, whether due to a defect or otherwise. This directly motivated the hardcoded safety rule described in Section 7.3. None of the five analyzed failures involved a missed obvious warning sign; the rule was added because nothing in the design protected against that possibility at all, not because it had already occurred.

## 11. Generalization

The design was stress-tested against a deliberately difficult shift in deployment context: from a setting with reliable access to care and clear communication, to a resource-limited setting with a language barrier between the parent and the system.

**Two core assumptions fail simultaneously.** The design assumes that questions can always be asked and understood clearly, and that emergency care involves a short, low-friction visit. Neither holds in this harder setting.

**The population reaching the system changes, even if the true rate of illness does not.** The population is expected to skew toward higher-risk cases in this setting, not because illness becomes more common, but because a parent facing real barriers to care is more likely to make the effort specifically for cases that already concern them; mild cases are comparatively less likely to reach the system at all. This is a selection effect concerning who seeks care, not a change in the underlying rate of illness.

**Both categories of error become more costly, for different reasons.** Missing genuine danger becomes more costly because delay allows a condition to worsen. An unnecessary visit becomes more costly as well, since it is no longer a minor inconvenience but a substantial burden of travel time, cost, and lost work. Because the threshold is fundamentally a ratio between these two costs, if both increase by a similar factor, the threshold itself may shift only modestly, even though both absolute costs have grown considerably. If the cost of missing genuine danger grows faster, which seems plausible given how delay compounds risk, the threshold would still shift lower. This project does not have a principled basis for estimating the relative growth rates of the two costs in this hypothetical setting, and this is reported as an open question rather than resolved with an assumed figure.

**A cost this model does not account for: the action itself is not free.** The model assumes that once an action is recommended, carrying it out introduces no independent risk. This is a reasonable simplification where resources are readily available, but it is a genuine blind spot in a resource-limited setting, where the act of traveling for care can itself introduce delay, cost, or harm. This is better described as an unmodeled cost attached to the action itself, rather than a missing hidden state concerning the child.

**A language barrier affects some evidence sources more than others.** Worded questions cannot be assumed reliable if the parent and the system do not share a language. The video review has an independent weakness: a poorly recorded or poorly lit video is uninformative regardless of language. A structured alternative, converting worded questions into selectable options, would improve every worded evidence source at once rather than favoring one over another. The doctor consult does not become less accurate in this setting; it becomes harder to reach, since the judgment itself should be unaffected if a connection can be established. The video review retains a hard limit regardless of connection quality, since no video permits a pulse check or auscultation.

**A local health worker would need to be part of the design.** A health worker positioned between the system's recommendation and an actual hospital visit is proposed as a genuine requirement in this setting, not an optional addition. This differs from a simple human review of the system's output; it introduces a real physical examination the system cannot perform, and a judgment on whether the visit is actually warranted.

**Sensitivity to an extreme cost ratio.** If the cost of missing genuine danger rises to 100 times the cost of a false alarm, rather than 30, the derived threshold falls to approximately 0.033 percent. No symptom pattern currently in the model can realistically bring a case's belief below this level, since even the most reassuring pattern only reaches roughly 1 to 2 percent. At this point, monitoring at home effectively ceases to be a reachable outcome regardless of the evidence, and the appropriate response is not a lower threshold but a reconsideration of the action set itself.

**Sensitivity to a higher cost of gathering evidence.** If the cost of every question increases by a factor of ten, a simple fixed spending limit becomes an inadequate stopping rule, since it cannot distinguish a low-value question skipped just before the limit from a high-value question skipped just after it. A more defensible rule combines the existing stop condition with a spending cap retained only as a safeguard against the possibility that the underlying value estimates are themselves incorrect, for example if two evidence sources turn out to be more correlated than assumed.

**Detecting that starting assumptions have become outdated.** In actual deployment, the true condition of a child is never directly observable, which is the defining property of a hidden state. What is available, for cases that are escalated, is the pairing of the system's stated confidence and an eventual confirmed outcome. Grouping predictions by stated confidence and comparing against confirmed outcomes across many cases is a genuine method for detecting outdated assumptions, in a way that simply observing the raw number of escalated cases over time cannot, since that figure could rise for an entirely unrelated reason, such as a seasonal increase in genuine illness.

## 12. Human Discussions

This project has been discussed publicly since early in its development, and two exchanges are directly relevant here.

One Reddit post presented the finding described in Section 9, that the more capable, question-asking system has lower decision cost but higher total cost once the questions themselves are counted, and asked whether this reflects a normal pattern for this type of system or indicates a problem with the assumed cost values. No replies had been received at the time of writing, which is reported directly.

A second Reddit post shares identical title text with the first, posted several days apart. Confirmation that these are genuinely two distinct posts, rather than the same link submitted twice, is still pending.

Five LinkedIn posts connected to this project have been published: one introducing the original problem, two addressing the ideas of adaptive evidence-gathering and the limits of additional data, one describing the overall system architecture, and one describing the hardcoded safety rule added following the failure analysis.

## 13. Limitations

**The experiment does not independently validate the underlying assumptions.** The same likelihood values used to construct the agent's reasoning were also used to generate the simulated cases it was tested against. This means the 100-case experiment can establish whether the decision-making logic is sound given its assumptions, but it cannot establish whether those assumptions actually match how real children present. This is stated directly rather than left implicit.

**Every parameter in this project is an assumption, clearly labeled as such.** Every starting belief, likelihood, and cost figure was assumed rather than measured. No real patient data was used in this project.

**Additional categories beyond S5 may exist.** S5 serves as a catch-all for cases that do not fit the other four states, but its own likelihood values are a flat assumption applied uniformly across all 17 symptom patterns, rather than derived from any real information about how atypical cases actually present. It is plausible that more specific categories remain unidentified.

**The system does not detect disagreement between evidence sources.** As noted in Section 7.4, each new answer is incorporated directly into the running belief with no check for whether it contradicts the previous result. This could obscure a genuinely useful signal.

**Calibration has not been empirically tested.** Section 5 describes the method that would be used to evaluate calibration, but doing so requires confirmed real-world outcomes that this project does not currently have access to.

**The safety rule relies on simple keyword matching.** It scans the reported symptoms for three specific terms. Any operational version of this rule would require a more structured representation than free text.

**Small changes early in the process can affect outcomes throughout, even with a fixed random seed.** The failure analysis in Section 10 demonstrated that a small adjustment to the risk calculation changes which children require additional questions, which reshuffles the subsequent random outcomes for those children even under an identical seed. As a result, comparisons across multiple random seeds, rather than a single run, are treated as a requirement for evaluating any future design change.

**This system is not a substitute for clinical judgment.** It is intended to support a decision and to make its reasoning inspectable, not to act autonomously without human review at the points identified in Section 7.4.

**Real-world data has not yet been used.** A real dataset (the Patient Priority Classification dataset on Kaggle) was identified as a potential source for validating the assumed values against real symptom patterns, but it has not yet been incorporated into this project.

## 14. New Questions

1. Is there a way to test directly whether two evidence sources are measuring substantially the same underlying signal, rather than discovering this only after the fact, so that sequential belief updates do not overstate the combined information of correlated sources?
2. Should the decision threshold vary by individual case characteristics, such as age, rather than remaining a single fixed value, and if so, on what basis should that variation be derived rather than assumed?
3. Given that the true underlying condition is never observable outside simulation, what is a realistic method for validating the system's confidence values when confirmed outcomes are only available for cases that were actually escalated?
4. Could a system detect, from the pattern of its own predictions over time, that its hidden-state list is incomplete, beyond simply observing how frequently its catch-all category is used?
5. What is a defensible method for assigning a real cost to something like a clinician's time, so that a value-of-information calculation reflects genuine opportunity cost rather than an assumed placeholder value?

## AI-Use Statement

Claude was used throughout this project as an explainer and a collaborator on implementation, not as a system that produced the project independently. It explained concepts including Bayesian updates, entropy, information gain, KL divergence, and calibration prior to each corresponding calculation being performed directly, and it identified specific errors during that process, including a likelihood-versus-probability calculation error on one test case, and an initial cost-ratio estimate of 100-to-1 later recognized as an emotionally driven rather than reasoned figure and revised to 30-to-1. All hidden states, starting beliefs, likelihood values, and cost figures were authored independently. All code was written independently, with the intended logic explained prior to implementation and reviewed afterward, a process that led directly to identifying and correcting a genuine defect (a hidden state silently excluded from the risk calculation in three locations). Every simulation reported in this paper was run independently, using a fixed random seed of 42, reported here to allow exact reproduction of these results. Claude assisted in drafting this paper's text and in structuring the failure analysis and generalization sections, while the underlying reasoning, corrections, and conclusions throughout were developed through direct engagement and are the author's own.

## References

Kemps, N., Holband, N., Boeddha, N.P., Faal, A., Juliana, A.E., Kavishe, G.A., Keitel, K., van 't Kruys, K.H., Ledger, E.V., Moll, H.A., Prentice, A.M., Secka, F., Tan, R., Usuf, E., Unger, S.A., Zachariasse, J.M. Validation of the Emergency Department-Paediatric Early Warning Score (ED-PEWS) for use in low- and middle-income countries: A multicentre observational study. PLOS Global Public Health, 4 (2024), e0002716. https://doi.org/10.1371/journal.pgph.0002716

Reuland, C., Shi, G., Deatras, M., Ang, M., Evangelista, P.P.G., Shilkofski, N. A qualitative study of barriers and facilitators to pediatric early warning score (PEWS) implementation in a resource-limited setting. Frontiers in Pediatrics, 11 (2023), 1127752. https://doi.org/10.3389/fped.2023.1127752

Giebel, G.D., Raszke, P., Nowak, H., Palmowski, L., Adamzik, M., Heinz, P., Tokic, M., Timmesfeld, N., Brunkhorst, F., Wasem, J., Blase, N. Problems and Barriers Related to the Use of AI-Based Clinical Decision Support Systems: Interview Study. Journal of Medical Internet Research, 27 (2025), e63377. https://doi.org/10.2196/63377

Manns, A., Millet, A., Mougin, F., Campeotto, F., Vivien, B., Dupic, L., Burgun, A., Jais, J.-P., Tsopra, R. PED-IA, a CDSS to support decision in pediatrics telephone triage: a crossover evaluation. Computers in Biology and Medicine, 195 (2025), 110645. https://doi.org/10.1016/j.compbiomed.2025.110645

Patient Priority Classification dataset (Kaggle), identified as a possible future source for validating assumed values against real data; not yet incorporated into this project. https://www.kaggle.com/datasets/hossamahmedaly/patient-priority-classification

## Appendix A: Required Questions

1. **What is a hidden state, and what are yours?** Something true about a situation that cannot be directly observed, only inferred from evidence. The five used here are S1 (genuinely low risk), S2 (genuinely high risk, apparent), S3 (genuinely high risk, concealed), S4 (false alarm), and S5 (unclassifiable).

2. **Why is directly predicting an answer sometimes insufficient?** A single prediction discards how confident the system actually is. Without tracking confidence, there is no way to indicate uncertainty or to know when human involvement is warranted.

3. **What is a belief distribution, and why must it sum to one?** It is the probability assigned to each possibility simultaneously. It must sum to one because these possibilities are intended to be exhaustive; a sum below one would indicate a real possibility is missing from the model.

4. **What is the difference between a starting belief and an updated belief?** The starting belief is held before any case-specific evidence is observed; the updated belief follows evidence. The starting point here is always S1=0.57, S2=0.20, S3=0.10, S4=0.10, S5=0.03.

5. **What is a likelihood, and how does it differ from a probability?** A likelihood asks how often given evidence would occur if a particular state were true; an updated probability asks the reverse, how likely the state is given the evidence. Reversing this direction was the most frequent calculation error made throughout this project.

6. **What does it mean for a system to be uncertain?** Its belief is distributed across more than one possibility rather than concentrated on one, a property measured directly using entropy.

7. **What is entropy, and why does it represent uncertainty?** A single number describing how distributed a belief is. The starting value here is 1.61, falling to 1.13 after the TC1 symptom example.

8. **What is a "bit," in plain terms?** Approximately the amount of uncertainty resolved by one well-chosen yes-or-no question.

9. **What is information gain, and how does it relate to entropy?** The expected reduction in uncertainty from a piece of evidence, averaged across every answer it could return. The fluid-intake question is worth 0.118 by this measure.

10. **What is conditional entropy?** The uncertainty expected to remain after an answer is known, averaged across every possible answer. Entropy minus this value equals information gain.

11. **What is mutual information, and how does it differ from correlation?** It measures whether knowing one variable reduces uncertainty about another in any way, including relationships correlation would fail to detect. It is mathematically identical to information gain, expressed in a different field's terminology.

12. **What is KL divergence, and why is it not a true distance?** It measures how much is lost by trusting one belief when another is correct. It is not a true distance because measuring it in one direction produces a different value than measuring it in the reverse direction.

13. **Why is it asymmetric? Provide an example.** Comparing the TC2-derived belief against the TC1-derived belief yields 1.06; the reverse comparison yields 0.91. This mirrors a deliberate design choice elsewhere in this project, where missing genuine danger is treated as 30 times more costly than a false alarm.

14. **What is Jensen-Shannon divergence, and why does it exist?** A symmetric, bounded alternative to KL divergence that never produces an unbounded value. It is understood conceptually but not used numerically in this project.

15. **What is calibration, and why does it matter?** Whether stated confidence actually matches observed outcomes across many cases. It matters here because the entire threshold and cost framework takes the system's stated probabilities at face value.

16. **What is expected cost, and how was the threshold derived from it?** The average loss from a decision rule applied repeatedly. The threshold here (approximately 3.2 percent) was derived by comparing the cost of a false alarm against the cost of missing genuine danger, after revising an initial, emotionally driven estimate (100 times worse) to a more reasoned figure (30 times worse).

17. **What is value of information, and when is additional information not worth obtaining?** How much better a decision-maker is for having asked, minus what asking cost. Information has no value, regardless of how much it teaches, if no possible answer could change the outcome, demonstrated concretely in Section 6.1.

18. **Can a question be highly informative and still not worth asking? Provide an example.** Yes. The doctor consult provides the most information of any option in this project, but for a case that is already conclusively decided, asking it would cost 8 units and change nothing.

19. **What is distribution shift, and how would it be detected?** A mismatch between the population a model's assumptions were built from and the population it currently encounters. This would be detected by monitoring whether stated confidence continues to match observed outcomes over time, treating a persistent, systematic gap as the relevant signal.

20. **When should the system stop gathering information and act? State the rule.** Act immediately if the belief already falls clearly outside the uncertain range. Otherwise, ask the next highest-value question, re-evaluate, and continue until the case resolves or no further questions remain.
