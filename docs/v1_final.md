# Week 2 Final Summary

This document summarizes the Week 2 work: what was built, what was found, and what changed along the way. The formal write-up is in `docs/paper/paper.pdf`. The complete decision-by-decision record is in `decisions/decision-record.md`. This file is a condensed overview of both.

## Objective

Week 1 established a belief system: five hidden states representing a child's possible underlying condition, a set of priors, a Bayesian update mechanism, and a threshold for choosing between monitoring at home, consulting a doctor, or seeking emergency care. Week 2 extended this system to reason about evidence itself: when additional information is worth gathering, when to stop gathering it, and what that information should cost.

## Information-Theoretic Foundation

Entropy and information gain were calculated by hand before being implemented in code, allowing each coded value to be verified against an independently worked example. Information gain was computed as an expected value across all possible outcomes of a question, not the outcome of a single imagined answer, which is a common source of error in this type of calculation.

## Deriving the Decision Threshold

The threshold separating "monitor" from "escalate" was derived from the relative cost of two error types rather than assumed. An initial cost ratio of 100-to-1 (missed danger versus a false alarm) implied a threshold near 1 percent, which would have escalated nearly every case. This ratio was identified as an unreasoned, emotionally driven estimate and revised to 30-to-1, producing a threshold of approximately 3.2 percent. This revision is documented directly in the decision record and the paper as an example of correcting an assumption after examining its implications, rather than defending an initial guess.

## Experiment and Results

Three policies were built and compared on 100 simulated cases: a baseline that ignores all evidence, a policy that always asks one fixed question, and a policy that selects its own questions based on value relative to cost. All code was written independently, with logic explained prior to implementation.

The value-of-information policy reduced decision cost by approximately 3x relative to the fixed-question policy. However, once the cost of the additional questions it asks is included, its total cost exceeded the fixed-question policy's in several runs. This trade-off, improved decisions at a higher information-gathering cost, is reported directly in the results rather than omitted in favor of the more favorable decision-cost figure alone.

## Failure Analysis and Correction

Reviewing individual failure cases, rather than only aggregate metrics, identified that nearly all failures involved the same hidden state, S5. Investigation revealed a defect: S5's probability was computed correctly but excluded from the calculation used to determine the recommended action. The defect was corrected in three locations.

An initial single-run comparison of the corrected and uncorrected logic suggested the correction made results worse. Repeating the comparison across ten random seeds showed the correction genuinely reduces cost on average; the single-run result had been misleading. This is documented as a methodological finding in its own right: design changes involving a decision threshold require multi-seed comparison, since altering the threshold changes which cases require additional evidence, which in turn reshuffles subsequent random outcomes even under a fixed seed.

## Safety Override

Reviewing the failure analysis identified a separate gap: no mechanism guaranteed an immediate response to an unmistakably severe case if the probabilistic calculation were incorrect for any reason. A hardcoded override was added: if a case presents with unresponsiveness, mottled skin, or severe respiratory distress, the system recommends emergency care immediately, bypassing the belief calculation entirely. This was added proactively, not in response to an actual missed case.

## Generalization Analysis

The design was evaluated against a deliberately difficult deployment scenario: a resource-limited setting with a language barrier between the parent and the system. Analysis showed that the population reaching the system would likely skew toward higher-risk cases, since parents facing access barriers are more likely to seek care specifically for concerning presentations rather than mild ones, a selection effect distinct from any change in the underlying rate of illness. The analysis also identified that the model assumes the recommended action can be carried out without independent risk, an assumption that does not hold when travel to care is itself difficult.

Sensitivity analysis showed that if the cost ratio were increased to 100-to-1, the resulting threshold (approximately 0.033 percent) would be lower than any evidence pattern in the model can realistically achieve, meaning monitoring would cease to be a reachable outcome. This was identified as a case requiring redesign of the action set rather than further threshold tuning.

## External Feedback

The project was discussed publicly on Reddit, LinkedIn, and X throughout its development. One exchange, predating the safety override's implementation by a substantial margin, involved a commitment to a safety-layer-first approach in response to a concern about insufficient validated data; this exchange is documented as public discussion anticipating a design decision made independently later.

A subsequent post presenting the decision-cost-versus-information-cost finding received three replies converging on similar advice: pricing decision errors and evidence costs in a shared unit would give the stopping rule a more defensible anchor. This is recorded as a concrete, unimplemented refinement for a future version.

A published study on a real pediatric telephone triage system (PED-IA) was identified and read in full. Its principal finding, improved decision accuracy at the cost of increased decision time, matches the shape of this project's own trade-off, providing independent support that the finding is not specific to the cost values assumed in this project.

## Limitations

The primary limitation, stated directly rather than left implicit: the simulation and the agent share the same underlying likelihood values. The experiment can establish whether the decision-making logic is sound given those values; it cannot establish whether the values themselves reflect how real children present. No real patient data was used in this project.

## Deliverable

The final paper is written in the official IJCAI-ECAI 26 format, compiled using the genuine style file. It is 10 pages and covers the belief system, the information-theoretic framework, the experiment and results, the failure analysis, the generalization analysis, limitations, and an appendix of required questions. The AI-use statement documents that Claude was used to explain concepts prior to independent calculation, to identify specific errors during implementation, and to assist in structuring the written material, while all hidden states, likelihood values, cost assumptions, code, and experimental runs were produced independently.