# Reading List: Pediatric Triage Agent Project

A note before reading: these are starting points I found through search, not sources I have personally read and verified in depth. Read each one yourself, and only cite the ones you actually open and understand well enough to explain in your own words. If a paper is too long or dense, it's fine to have an AI assistant summarize it for you first, but verify the summary against the actual paper before trusting or citing it, per the "never cite something you didn't read" rule.

---

## Most directly connected to this project (read these first)

### 1. Provisional Validation of a Pediatric Early Warning Score for Resource-Limited Settings
A PEWS variant built specifically for resource-limited hospital settings, validated in Rwanda. Closely mirrors the generalization scenario worked through in this project (rural, resource-limited deployment).
https://pubmed.ncbi.nlm.nih.gov/30992308/

### 2. Validation of the Emergency Department-Paediatric Early Warning Score (ED-PEWS) for use in low- and middle-income countries
Validates a PEWS variant across several low- and middle-income country settings, and explicitly discusses why objective, structured parameters are an advantage in places where patients speak different local languages. Directly connects to the language-barrier reasoning in this project's generalization section.
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10956749/

---

## Foundational PEWS background

### 3. The Pediatric Early Warning System score: a severity of illness score to predict urgent medical need in hospitalized children
One of the original PEWS validation studies, useful background for where the evidence-category structure in this project's design (behavior, circulation, respiratory pattern) originally comes from.
https://pubmed.ncbi.nlm.nih.gov/16990097/

### 4. Accuracy and Monitoring of Pediatric Early Warning Score (PEWS)
A study on how often real PEWS scores get recorded incorrectly in practice. Relevant to this project's Limitations section, specifically the point that evidence reliability is a real, separate problem from the reasoning built on top of it.
https://pediatrics.jmir.org/2021/1/e25991/PDF

### 5. A qualitative study of barriers and facilitators to pediatric early warning score (PEWS) implementation in a resource-limited setting
Studies real-world implementation friction for PEWS in a resource-limited hospital. Supports the local-health-worker-as-intermediary idea developed in this project's generalization section.
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10050749/

---

## Articles connecting the broader idea (AI reasoning under uncertainty in healthcare, not just triage scoring mechanics)

### 6. Risk and Uncertainty Communication in Deployed AI-based Clinical Decision Support Systems: A scoping review
A review of how deployed clinical AI systems actually communicate uncertainty to their users. Closely related to this project's core idea of holding and reporting a belief distribution rather than a single confident answer.
https://doi.org/10.1145/3830235

### 7. Problems and Barriers Related to the Use of AI-Based Clinical Decision Support Systems: Interview Study
Covers "automation bias," where clinicians over-trust an AI system's recommendation even when it is wrong or contradicted by other information. Directly relevant to why this project's human-escalation rules and safety override exist.
https://www.jmir.org/2025/1/e63377

### 8. Do as AI Say: Susceptibility in Deployment of Clinical Decision-Aids
A study finding that physicians rate identical advice differently depending on whether it is labeled as coming from a human or an AI system. Relevant background for thinking about how a system like this one would actually be trusted and used in practice.
https://pmc.ncbi.nlm.nih.gov/articles/PMC7896064/

### 9. Explainable AI for Clinical Decision Support Systems: Literature Review, Key Gaps, and Research Synthesis
Covers the broader challenge of making an AI system's reasoning understandable to the people using it, including how to visually and practically communicate low-confidence predictions. Connects to this project's emphasis on the agent's decisions being inspectable rather than opaque.
https://www.mdpi.com/2227-9709/12/4/119

### 10. PED-IA, a CDSS to support decision in pediatrics telephone triage: a crossover evaluation
A real pediatric telephone triage clinical decision support system, evaluated with 51 practitioners. Its central finding, better decision accuracy at the cost of significantly longer decision time, closely mirrors this project's own decision-cost versus information-cost trade-off finding. Read in full and cited in the paper's Related Work section.
https://doi.org/10.1016/j.compbiomed.2025.110645

---

## Dataset noted for future work (not yet integrated into this project)

### Patient Priority Classification dataset
A real dataset of patient records including symptoms, vital signs, and human-assigned triage priority labels. Identified as a potential source for validating this project's hand-assigned likelihoods against real symptom co-occurrence rates, but not yet integrated.
https://www.kaggle.com/datasets/hossamahmedaly/patient-priority-classification
