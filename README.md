# Pediatric Triage Agent

A small research project exploring whether a probabilistic (Bayesian) agent can help make safer, more consistent care-level decisions when a child's symptoms are ambiguous — deciding between monitoring at home, calling a nurse line, booking a pediatrician visit, or seeking emergency care.

The core idea: a child's true underlying condition is never directly observable. Only symptoms and behavior are. The agent maintains a belief over possible underlying states and updates that belief as new evidence comes in, rather than reacting to any single symptom in isolation.

## Status

Early-stage and actively evolving. Currently: problem framing, a worked Bayesian model, and an initial set of simulated test cases. Known limitations are documented openly in `docs/` rather than hidden — this is a research-in-progress project, not a finished product.

## Structure

- **`docs/`** — write-ups: problem statement, technical terms, the Bayesian model, test cases, limitations, and references.
- **`images/`** — architecture and process diagrams.
- **`data/`**, **`experiments/`**, **`results/`** — simulation inputs/outputs (populated as the project progresses).
- **`src/`** — code (to follow).
- **`paper/`** — the eventual write-up, once results are further along.

## Why this problem

The hardest case isn't the obviously mild or obviously serious one — it's the condition that looks mild early on but is quietly serious. Most of this project is really about not being falsely reassured.

See `docs/` for the full reasoning, worked examples, and current limitations.
