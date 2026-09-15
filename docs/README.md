# Pediatric Triage Agent Project

A small Bayesian and information-theoretic agent for deciding whether a child's reported symptoms warrant home monitoring, a doctor consult, or emergency evaluation, under incomplete parental reporting.

## What's in this repository

- `agent.py` — the current, active implementation. States, priors, likelihoods, evidence sources, the Bayesian update, the decision policy, the safety override, and the experiment runner all live here.
- `agent_v0.py` — a frozen snapshot of the agent before the S5 residual state and the random seed fix were added. Kept for reference, not edited further.
- `run_experiment.py` — reserved for a thin script that imports from `agent.py` and runs the experiment separately from the engine logic. Currently empty.
- `research.md`, `experiment.md` — Week 1 material: problem statement, hidden states, priors, the original 17 test cases, and the belief-update work.
- `discussion-record.md` — ongoing record of public discussion on Reddit and LinkedIn connected to this project.
- `decisions/decision-record.md` — the running log of every real decision, finding, and challenge across Week 2, including accepted and rejected suggestions and why.
- `decisions/probability-decision-record.md` — a single worked probability decision record in the required format, including audit metadata.
- `review-record.md` — three review passes (practitioner, probability, preprint) with accept/reject decisions and what changed as a result.
- `paper/` — the formal write-up: `main.tex`, `ijcai26.sty`, `named.bst`, and the compiled `paper.pdf` (official IJCAI-ECAI 26 format). `paper_draft.md` is the editable Markdown source.
- `v0_final.md` — a narrative recap of the Week 1 work.
- `social/` — saved copies of LinkedIn and Reddit post content.

## How to reproduce the experiment

1. Make sure Python 3 is installed. No external packages are required; the agent only uses the standard library (`random`).
2. Run the agent directly:
   ```
   python3 agent.py
   ```
3. This will generate 100 simulated children using a fixed random seed (42), run all three policies (P0, P2, P3), and print a metrics dictionary for each: accuracy, precision, recall, decision cost, info cost, average questions asked, and human-review rate.
4. Because the random seed is fixed, running this command again should produce identical output. If it doesn't, something in the code path has changed in a way that consumes a different number of random draws per case; see the failure analysis section of `decisions/decision-record.md` for a worked example of exactly this happening during a bug fix.

## Reproducing a specific finding

To reproduce the failure analysis findings (Section 10 of the paper), or to inspect individual simulated children rather than just the aggregate metrics, import the functions from `agent.py` into a separate script rather than editing `agent.py` directly:

```python
from agent import *
children = generate_children(100)
results = run_p3(children)
failures = [r for r in results if r["label"] in ["false negative", "partial miss"]]
```