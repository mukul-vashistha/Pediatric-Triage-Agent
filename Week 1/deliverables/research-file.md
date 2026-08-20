# Problem Statement

Parents often have to decide what level of medical care their child needs based on incomplete and sometimes ambiguous symptoms. The same symptom can appear in a minor illness or in a more serious condition and parents may not know which additional observations are important.

The agent observes a child's symptoms and basic observations such as age, duration of symptoms, temperature, breathing, hydration, alertness, pain, eating/drinking and changes in behavior. It must decide whether to recommend monitoring at home, contacting a nurse line, scheduling a pediatrician visit or seeking emergency care.

The key challenge is that the child's true underlying health state is hidden. The agent only observes symptoms and other evidence and must continuously update its belief about the possible states as new information becomes available.

# Project Objective

Design and test an agent that estimates the probability of a child's underlying triage state using Bayesian inference and recommends an appropriate level of care.

The goal is not to diagnose the exact disease. The goal is to make an appropriate care-level decision when information is incomplete.

The agent should start with inexpensive and high-value observations, update its probabilities as new evidence arrives, ask additional questions when uncertainty is high and escalate when evidence suggests a potentially serious condition.

The system should also recognize that some dangerous conditions may initially look low-risk and that some alarming symptoms may ultimately turn out to be non-urgent.

# Technical Terms

* **Hidden State:** The child's actual underlying health/triage condition that the agent cannot directly observe from symptoms alone.

* **Bayesian Update:** The mathematical process the agent uses to revise its belief about the child's hidden state whenever new evidence is observed.

* **Prior Probability:** The agent's belief about each possible hidden state before considering the latest evidence.

* **Likelihood:** How likely a particular observation is if a specific hidden state is actually true.

* **Posterior Probability:** The updated probability of each hidden state after combining the prior belief with new evidence.

* **Base Rate:** The historical frequency of a particular triage state within a relevant population.

* **Evidence:** Any observation that provides information about the child's hidden state, such as breathing difficulty, hydration, fever, alertness or symptom duration.

* **Red Flag:** An observation that may indicate a potentially serious condition and therefore requires immediate escalation rather than relying only on the overall probability estimate.

* **Gray Zone:** A probability range where the agent is not sufficiently confident to make a strong care-level recommendation and should ask additional questions or seek human/clinical review.

* **HITL (Human in the Loop):** A human or qualified healthcare professional is involved when the agent is uncertain or when the case requires judgment beyond the system's safe operating boundary.

* **Care Level:** The recommended action category: monitor at home, contact a nurse line, schedule a pediatrician visit, or seek emergency care.

* **Observation Sequence:** The ordered sequence of symptoms and observations collected over time.

* **State Transition:** A change in the underlying health/triage state over time, which is the reason an HMM-style framework may be useful.

* **Uncertainty:** The degree to which the agent is unsure about the child's underlying state.

# Search Queries

## Pediatric Triage & Care-Level Decisions

* "how do pediatric triage systems determine urgency"
* "how do pediatric nurse lines assess symptoms"
* "pediatric triage decision rules emergency vs non emergency"
* "how do doctors determine when a child needs emergency care"
* "pediatric symptom severity assessment frameworks"

## Bayesian & Probabilistic Triage

* "Bayesian inference for medical triage"
* "Bayesian decision making under uncertainty healthcare"
* "probabilistic models for clinical decision support"
* "Bayesian networks pediatric diagnosis triage"
* "uncertainty estimation clinical decision support systems"

## Hidden States & Time Evolution

* "hidden Markov model healthcare patient state progression"
* "HMM clinical disease progression model"
* "hidden Markov models pediatric health"
* "patient state transition probabilistic model"
* "Bayesian filtering healthcare symptoms over time"

## Hard-to-Catch Cases

* "pediatric conditions with subtle early symptoms"
* "children serious illness early symptoms nonspecific"
* "pediatric triage false negative missed red flags"
* "pediatric emergency symptoms that parents commonly miss"
* "children symptoms that look minor but are serious"

## Red Flags & Safety

* "pediatric emergency red flags breathing dehydration lethargy"
* "pediatric triage red flag symptoms"
* "when should a child go to emergency department symptoms"
* "pediatric dehydration emergency warning signs"
* "child breathing difficulty emergency signs"

# The 4 Hidden States

The agent tracks 4 mutually exclusive states representing every possible combination of how the child's symptoms appear vs. what the child's actual underlying triage state is:

State 1 (S₁): Symptoms look low-risk, actually low-risk (Minor/self-limiting condition).

State 2 (S₂): Symptoms look high-risk, actually high-risk (Genuinely urgent or emergency condition).

State 3 (S₃): Symptoms look low-risk, actually high-risk (Serious condition with subtle or early symptoms).

State 4 (S₄): Symptoms look high-risk, actually low-risk (Alarming symptoms caused by a minor or non-urgent condition).

Total Low-Risk Probability:

P(Low Risk) = P(S₁) + P(S₄)

Total High-Risk Probability:

P(High Risk) = P(S₂) + P(S₃)

The important safety state is S₃ because it represents a potentially dangerous condition that does not initially appear severe. This is the false-reassurance failure mode.

S₄ represents the opposite situation: the symptoms appear concerning, but the underlying condition is ultimately non-urgent.

# Possible Care-Level Actions

* **Monitor at Home**
* **Contact Nurse Line**
* **Schedule Pediatrician Visit**
* **Seek Emergency Care (ER)**

The hidden state and the action are different concepts.

The hidden state represents what is actually happening to the child.

The action represents what the agent recommends based on its current probability distribution and safety rules.

# Signals (Evidence the Agent Checks)

## Level 1 — Checked on Every Case

* Child's age
* Main symptom
* Symptom duration
* Symptom severity
* Breathing difficulty
* Level of alertness / responsiveness
* Hydration and ability to keep fluids down
* Urination frequency
* Fever / temperature
* Pain severity
* Ability to eat and drink
* Vomiting
* Diarrhea
* Changes in behavior
* Sudden worsening
* Parent's description of whether the child appears significantly different from normal

## Level 2 — Checked When the Initial Probability Is Unclear

* How quickly symptoms appeared
* Whether symptoms are getting better, worse, or staying the same
* Pattern of fever over time
* Frequency and severity of vomiting
* Fluid intake compared with normal
* Urination compared with normal
* Changes in activity level
* Whether the child can walk, speak, interact, or perform normal age-appropriate activities
* Recent illness or exposure
* Relevant medical history
* Medication already given
* Response to supportive care
* Additional symptom combinations that may change the estimated probability

## Level 3 — Safety / Escalation Layer

Certain observations should not be treated as ordinary Bayesian evidence alone.

Examples include:

* Significant breathing difficulty
* Severe difficulty waking or markedly reduced responsiveness
* Signs of severe dehydration
* Seizure
* Severe or rapidly worsening condition
* Other predefined emergency red flags

If a hard safety rule is triggered, the system should escalate rather than allowing a probability calculation to produce false reassurance.

# Observations

The table below is my own prediction based on the architecture's signals. These are assumptions, not confirmed medical probabilities. Testing and clinical validation would be required before using these observations in a real healthcare system.

| Observation                                                                 | What it might suggest                                         |
| --------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Mild symptoms, normal breathing, normal hydration, child alert              | Likely S₁ (low-risk, actually low-risk)                       |
| Severe breathing difficulty with worsening symptoms                         | Likely S₂ (high-risk, actually high-risk)                     |
| Child appears relatively well but symptoms are worsening rapidly            | Could shift belief toward S₃                                  |
| Mild-looking symptoms combined with unusual lethargy                        | Shifts belief strongly toward S₃                              |
| Child looks very uncomfortable but is otherwise alert, hydrated and stable | Could represent S₄                                            |
| High fever alone without other concerning observations                      | Does not automatically imply high-risk state                  |
| Poor fluid intake plus reduced urination                                    | Shifts belief toward higher-risk states                       |
| Symptoms improving over time                                                | Shifts belief toward lower-risk states                        |
| Sudden deterioration after initially mild symptoms                          | Shifts belief toward S₃ or S₂                                 |
| Significant red-flag symptom                                                | Should trigger escalation regardless of the overall posterior |

# Prior, Likelihood, Posterior

**Prior:** The agent's belief about the probability of each hidden state before considering the latest evidence.

For example:

P(S₁), P(S₂), P(S₃), P(S₄)

The prior may be informed by historical triage data, age group, season, symptom category and other relevant population-level information.

**Likelihood:** How likely a particular observation would be if a specific hidden state were actually true.

For example:

P(Breathing Difficulty | S₂)

means how likely significant breathing difficulty would be if the child were actually in State 2.

**Posterior:** The updated probability of each hidden state after incorporating new evidence.

Bayes' rule:

P(Sᵢ | Evidence) ∝ P(Evidence | Sᵢ) × P(Sᵢ)

The posterior becomes the new belief state before the next observation arrives.

For example, if the agent initially believes a child is probably low-risk but then observes worsening breathing, the posterior probability of the high-risk states should increase.

Real probability values are not assigned yet. Priors and likelihoods would need to be estimated from appropriate historical/clinical data and validated before being used for real-world decisions.

# Likelihood Table

This table represents architectural assumptions, not measured clinical probabilities.

High / Medium / Low are placeholders that would need to be replaced with validated probability estimates.

| Signal                              | S₁ Low-risk / Looks low-risk | S₂ High-risk / Looks high-risk | S₃ High-risk / Looks low-risk | S₄ Low-risk / Looks high-risk |
| ----------------------------------- | ---------------------------- | ------------------------------ | ----------------------------- | ----------------------------- |
| Normal breathing                    | High                         | Low                            | Medium                        | High                          |
| Significant breathing difficulty    | Low                          | High                           | Medium                        | Low                           |
| Normal hydration                    | High                         | Low                            | Medium                        | High                          |
| Poor hydration / reduced urination  | Low                          | High                           | High                          | Medium                        |
| Normal alertness                    | High                         | Low                            | Medium                        | High                          |
| Marked lethargy / difficult to wake | Low                          | High                           | High                          | Low                           |
| Mild, stable symptoms               | High                         | Low                            | Medium                        | Medium                        |
| Rapidly worsening symptoms          | Low                          | High                           | High                          | Medium                        |
| Symptoms improving                  | High                         | Low                            | Low/Medium                    | High                          |
| Severe pain                         | Low/Medium                   | High                           | Medium/High                   | Medium                        |
| Sudden deterioration                | Low                          | High                           | High                          | Low                           |

# Bayesian Updating Example

Suppose the agent begins with:

P(S₁) = 0.60
P(S₂) = 0.15
P(S₃) = 0.15
P(S₄) = 0.10

The agent then receives new evidence:

**Evidence 1:** Child is drinking normally.

This may increase the probability of lower-risk states.

The agent performs a Bayesian update.

Then:

**Evidence 2:** Parent reports that the child has become unusually difficult to wake.

This evidence has a much stronger relationship with potentially serious states.

The agent updates again.

The important point is that the system does not make its decision from one symptom alone. It continuously revises its belief as evidence arrives.

# Time / HMM-Style Component

The child's underlying state may change over time.

For example:

S₁ → S₁
S₁ → S₂
S₁ → S₃
S₂ → S₂
S₂ → S₁

The HMM-style component would model the probability of transitioning from one hidden state to another as new observations arrive.

For example:

P(Sₜ | Sₜ₋₁)

represents the probability of the child's current hidden state given the previous hidden state.

The observation model represents:

P(Eₜ | Sₜ)

which describes how likely the current evidence is given the current hidden state.

However, the HMM component should remain secondary to the Bayesian inference and safety layer unless reliable longitudinal data exists to estimate meaningful state-transition probabilities.

# Safety Layer

The most important failure mode is a missed serious condition.

Therefore, the architecture should not rely entirely on probabilistic inference.

A predefined red-flag layer should operate before or alongside the probabilistic model.

If a high-priority red flag is present, the agent should escalate immediately rather than allowing a low posterior probability to override the safety rule.

Examples of high-priority red-flag categories include:

* Breathing difficulty
* Markedly reduced responsiveness / severe lethargy
* Severe dehydration
* Seizure
* Rapid deterioration
* Other clinically validated emergency warning signs

The Bayesian model should primarily handle uncertainty and non-emergency reasoning, while the safety layer provides deterministic protection against high-cost missed red flags.

# Gray Zone

The agent should not force every case into a confident recommendation.

A gray zone can be defined where:

* The posterior probabilities are close together.
* Important information is missing.
* Evidence conflicts.
* The observation is ambiguous.
* The agent cannot safely distinguish between two care levels.

In the gray zone, the agent should ask the next highest-value question rather than guessing.

For example:

If the agent cannot distinguish between "monitor at home" and "contact nurse line," it may ask about hydration, urine output, breathing, alertness, or symptom progression.

The exact probability thresholds should not be assumed yet. They need to be tested and calibrated using appropriate data.

# Decision Rules

The posterior probability should inform the recommendation, but probability alone should not determine every action.

A simplified architecture is:

**Red flag present → Emergency escalation**

Otherwise:

**High probability of serious/urgent state → Higher level of care**

**Intermediate probability / uncertainty → Ask more questions or contact nurse line**

**Low probability of serious state + stable/improving symptoms → Lower level of care**

The final decision should also account for the cost of errors.

A false negative — incorrectly reassuring a parent when the child needs urgent care — can be substantially more harmful than a false positive that sends a low-risk child for additional evaluation.

# Error Types

## False Negative

The agent recommends a low level of care when the child actually has a serious condition.

This corresponds closely to State 3:

S₃ = Looks low-risk, actually high-risk.

This is the most important error to minimize.

## False Positive

The agent recommends a high level of care when the underlying condition is actually low-risk.

This corresponds closely to State 4:

S₄ = Looks high-risk, actually low-risk.

False positives can create unnecessary anxiety, cost and healthcare utilization.

## Uncertainty Error

The agent is not sufficiently certain but gives a confident recommendation instead of asking for more information or escalating.

This is why the system needs a gray zone and explicit uncertainty handling.

# Signal Costs

**Age check = Cost: Low** because the age is directly provided.

**Symptom duration = Cost: Low** because it can be obtained directly from the parent.

**Temperature = Cost: Low** when the parent already has a thermometer reading.

**Breathing assessment = Cost: Low to Medium** because it requires asking specific questions and may be difficult to assess remotely.

**Hydration assessment = Cost: Low to Medium** because several observations may be required, such as fluid intake and urination.

**Alertness assessment = Cost: Low** because the parent can generally describe whether the child is awake, responsive and behaving normally.

**Additional symptom questions = Cost: Low to Medium** because they increase conversation length but generally do not require external computation.

**Historical/contextual information = Cost: Medium** because more questions and information retrieval may be required.

**Bayesian update = Cost: Low** computationally once the probability model has been established.

**HMM/state-transition update = Cost: Low to Medium** computationally, but the difficult part is obtaining reliable transition probabilities.

**Human/clinical review = Cost: High** because it requires qualified human attention and is slower than automated assessment.

# Target Communities & Research Outreach

## Target Reddit Communities

| Community                  | Focus & Project Relevance                                                     | Status   |
| -------------------------- | ----------------------------------------------------------------------------- | -------- |
| **r/AskDocs**              | Understanding how medical professionals reason about symptoms and uncertainty | Research |
| **r/pediatrics**           | Pediatric symptom assessment, triage reasoning and clinical context          | Research |
| **r/healthIT**             | Clinical decision-support systems, healthcare technology and implementation  | Research |
| **r/MachineLearning**      | Bayesian models, uncertainty estimation, ML system design                     | Research |
| **r/learnmachinelearning** | Probabilistic modeling, Bayesian inference, HMM concepts                      | Research |
| **r/medtech**              | Medical technology, safety, validation and product considerations            | Research |
| **r/softwarearchitecture** | Agent architecture, safety layers, escalation and fallback systems            | Research |

# Research Objectives by Community

## 1. r/pediatrics

* **Focus:** Pediatric symptom assessment and triage reasoning.
* **Key Insight Sought:** Which observations are most useful for distinguishing low-risk cases from cases requiring urgent evaluation.

## 2. r/AskDocs

* **Focus:** Real-world clinical reasoning.
* **Key Insight Sought:** How clinicians handle incomplete information and which follow-up questions provide the most decision value.

## 3. r/healthIT

* **Focus:** Clinical decision-support systems.
* **Key Insight Sought:** How probabilistic recommendations should be combined with deterministic safety rules and human escalation.

## 4. r/learnmachinelearning

* **Focus:** Bayesian inference, HMMs, uncertainty and sparse data.
* **Key Insight Sought:** How to estimate priors and likelihoods when reliable training data is limited.

## 5. r/softwarearchitecture

* **Focus:** Safety-oriented agent architecture.
* **Key Insight Sought:** How to structure a fast safety gate, probabilistic reasoning layer, question-selection layer and escalation mechanism.

## 6. r/medtech

* **Focus:** Healthcare technology and safety.
* **Key Insight Sought:** Validation, risk management, human oversight and practical limitations of AI systems in healthcare.

# Key Questions to Research

1. What should the actual hidden states represent?
2. Is "looks low-risk vs. looks high-risk" the best decomposition for the four states?
3. Which observations provide the strongest likelihood ratios?
4. Which symptoms should be treated as hard red flags instead of ordinary Bayesian evidence?
5. How should the agent handle conflicting observations?
6. How should priors vary by age and symptom category?
7. How can Bayesian probabilities be calibrated?
8. How should the agent behave when evidence is insufficient?
9. What probability threshold should trigger escalation?
10. What is the appropriate definition of the gray zone?
11. Does an HMM add meaningful value if longitudinal pediatric data is unavailable?
12. How should state transitions be estimated?
13. How should false negatives and false positives be weighted?
14. How should the system communicate uncertainty to parents?
15. When should the agent stop asking questions and recommend human/clinical assessment?

# Relevant Domain Experts & Researchers

## Pediatric Medicine & Clinical Reasoning

* Pediatric clinicians and emergency physicians who publish research on pediatric triage and emergency warning signs.

* Researchers studying pediatric emergency medicine and clinical decision rules.

* Organizations publishing evidence-based pediatric emergency guidance.

## Bayesian & Probabilistic Machine Learning

* **David Blei** — Bayesian statistics, probabilistic modeling and machine learning.

* **David Duvenaud** — probabilistic machine learning and uncertainty.

* **Shakir Mohamed** — probabilistic machine learning and statistical AI.

## Healthcare AI & Clinical Decision Support

* Researchers working on clinical decision-support systems, uncertainty quantification, medical AI evaluation and safe deployment.

* Healthcare AI researchers studying calibration, human oversight and high-stakes decision-making.

# Key Research Resources & Technical References

| Resource / Reference                           | Type & Source          | Core Focus & Data Provided                                       | Project Relevance & Use Case                                        |
| ---------------------------------------------- | ---------------------- | ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| Pediatric emergency/triage clinical guidelines | Clinical Guidance      | Emergency warning signs and care-level assessment                | Used to identify safety-critical red flags                          |
| Pediatric triage decision rules                | Clinical Research      | Structured symptom and severity assessment                       | Used to define evidence signals and possible care levels            |
| Bayesian decision theory                       | Statistical Framework  | Updating beliefs under uncertainty                               | Provides mathematical foundation for the agent                      |
| Hidden Markov Models                           | Probabilistic Model    | Modeling hidden states evolving over time                        | Used to investigate whether symptom/state transitions add value     |
| Clinical decision-support research             | Healthcare AI Research | Human-AI decision making and uncertainty                         | Used to design escalation and HITL behavior                         |
| Calibration research                           | ML Evaluation          | Whether predicted probabilities correspond to actual frequencies | Used to determine whether P(High Risk) can be trusted               |
| Pediatric longitudinal datasets                | Clinical Dataset       | Symptoms and outcomes over time                                  | Potential source for estimating priors and transition probabilities |

# Core Architecture

The proposed architecture is:

**Parent Input**

↓

**Level 1 — Safety / Red-Flag Check**

↓

**Level 2 — Evidence Extraction**

↓

**Bayesian Probability Update**

↓

**Current Hidden-State Probability Distribution**

↓

**Uncertainty / Gray-Zone Check**

↓

**Ask Next Highest-Value Question if Needed**

↓

**Bayesian Update Again**

↓

**Care-Level Recommendation**

↓

**Human / Clinical Escalation When Required**

# Final Decision Categories

### 1. Monitor at Home

Used when the available evidence strongly supports a low-risk situation and no emergency red flags are present.

### 2. Contact Nurse Line

Used when the situation does not clearly require emergency care but the parent needs professional guidance or the evidence is uncertain.

### 3. Schedule Pediatrician Visit

Used when symptoms are persistent, recurrent, concerning, or require clinical assessment but do not appear to require immediate emergency care.

### 4. Seek Emergency Care

Used when a serious condition is suspected or a predefined emergency red flag is detected.

# Important Design Principle

The agent should not attempt to diagnose every possible pediatric disease.

Its primary task is:

**Given incomplete observations, estimate the probability of the child's underlying triage state and choose the safest appropriate level of care.**

The Bayesian model handles uncertainty.

The observation layer gathers evidence.

The HMM-style component can model changes over time if sufficient longitudinal data exists.

The red-flag layer protects against catastrophic false negatives.

The gray-zone mechanism prevents the agent from pretending to know when the evidence is insufficient.

The human-in-the-loop layer provides a final safety mechanism for cases that fall outside the system's confidence or capability.

# Main Research Hypothesis

A pediatric triage agent can make better care-level decisions under incomplete information by continuously updating probabilities from new observations rather than making a single static classification from the initial symptoms.

However, the system should not rely exclusively on probabilistic inference.

A combination of:

**Bayesian inference + explicit red-flag safety rules + uncertainty handling + optional time/state modeling + human escalation**

is the proposed architecture to investigate.
