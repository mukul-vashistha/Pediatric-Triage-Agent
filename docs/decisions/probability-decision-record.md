# Probability Decision Record

One worked case, in the required format, using the TC1 evidence example already verified by hand and in code.

| Item | Recorded information |
|---|---|
| Evidence | Parent-reported symptoms matching profile TC1: mild symptoms, normal breathing, normal hydration, alert. |
| Hidden states | S1 (true low-risk), S2 (true high-risk, obvious), S3 (true high-risk, hidden), S4 (false high-risk), S5 (atypical/unclassifiable). |
| Beliefs (prior, before this evidence) | S1 = 0.57, S2 = 0.20, S3 = 0.10, S4 = 0.10, S5 = 0.03. Sum = 1.00. |
| Event | Whether the child is in the high-risk group (S2, S3, or S5 combined) versus the low-risk group (S1 or S4). |
| Actions | Monitor at home, consult a doctor, seek emergency evaluation. |
| Costs | False positive (unnecessary escalation of a low-risk child): 1 unit. Partial miss (a high-risk child sent to a doctor rather than emergency): 20 units. False negative (a high-risk child sent home): 30 units. |
| Policy | Compute P(High Risk) = P(S2) + P(S3) + P(S5) from the posterior. Below 3.2 percent, monitor. Above 40 percent, escalate to emergency. In between, gather further evidence (fluid intake, then temperature, then a clinician video review, then a doctor consult, in that order) and recheck after each one, stopping as soon as the belief resolves out of the ambiguous band. |
| Decision | Posterior P(High Risk) for this case works out to approximately 0.065 + 0.065 + 0.012 = 0.142, or 14.2 percent (see the worked update below). This falls in the ambiguous band, so the policy proceeds to gather further evidence rather than deciding immediately. |
| Audit data | Time: this record was produced during Week 2 development, after the S5 residual state and safety-override additions. Data version: hand-assigned likelihoods, version reflecting the 5-state model (post-S5 addition). Model version: `agent.py` as of the S5-exclusion bug fix and safety override addition (see `decisions/decision-record.md`, Sections 9 and 15). Policy version: threshold 3.2 percent / 40 percent, derived from cost ratio 1:30, revised down from an initial 1:100 estimate. |

The hidden-state probabilities sum to 100 percent both before and after the update below.

## Adding one new item of evidence

**1. Prior probability:** as recorded above, S1 = 0.57, S2 = 0.20, S3 = 0.10, S4 = 0.10, S5 = 0.03.

**2. New evidence:** TC1's profile (mild symptoms, normal breathing, normal hydration, alert).

**3. Likelihood for each hidden state:** P(E|S1) = 0.80, P(E|S2) = 0.20, P(E|S3) = 0.40, P(E|S4) = 0.30, P(E|S5) = 0.25. These are hand-assigned judgments, clearly labeled as such, not measured from real data.

**4. Posterior probability, calculated in full:**

| State | Prior | Likelihood | Prior × Likelihood | Posterior |
|---|---|---|---|---|
| S1 | 0.57 | 0.80 | 0.456 | 0.740 |
| S2 | 0.20 | 0.20 | 0.040 | 0.065 |
| S3 | 0.10 | 0.40 | 0.040 | 0.065 |
| S4 | 0.10 | 0.30 | 0.030 | 0.049 |
| S5 | 0.03 | 0.25 | 0.0075 | 0.012 |
| Total | 1.00 | -- | 0.6165 | 1.00 |

**5. Compare posterior against threshold:** P(High Risk) = 0.065 + 0.065 + 0.012 = 0.142, or 14.2 percent. This is above the 3.2 percent monitor threshold and below the 40 percent emergency threshold, placing it in the ambiguous band.

**6. Recorded action:** gather further evidence, starting with the fluid-intake check (E-A), before making a final decision. This matches what `agent.py`'s `compute_action_p3` actually does for this evidence profile when run.
