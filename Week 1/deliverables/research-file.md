# Problem Statement

Parents often have to decide what level of medical care their child needs based on incomplete and sometimes ambiguous symptoms. The same symptom can appear in a minor illness or in a more serious condition and parents may not know which additional observations are important.

The agent observes a child's symptoms and basic observations such as age, duration of symptoms, temperature, breathing, hydration, alertness, pain, eating/drinking and changes in behavior. It must decide whether to recommend monitoring at home, contacting a nurse line, scheduling a pediatrician visit or seeking emergency care.

The key challenge is that the child's true underlying health state is hidden. The agent only observes symptoms and other evidence and must continuously update its belief about the possible states as new information becomes available.

# Project Objective

Design and test an agent that estimates the probability of a child's underlying triage state using Bayesian inference and recommends an appropriate level of care.

The goal is not to diagnose the exact disease and replace the clinician. The goal is to make an appropriate care-level decision when information is incomplete.

The agent should start with high-value observations, update its probabilities as new evidence arrives, ask additional questions when uncertainty is high and escalate when evidence suggests a potentially serious condition.

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

* **State Transition:** A change in the underlying health/triage state over time.

* **Uncertainty/Entropy:** The degree to which the agent is unsure about the child's underlying state.

# Search Queries

## Pediatric Triage & Care-Level Decisions

* "How do validated pediatric triage systems determine urgency?"
* "What information is required to safely triage a child?"
* "How do pediatric telephone triage systems decide which follow-up questions to ask?"
* "How do clinical decision systems handle missing information and uncertainty?"
* "How can AI combine structured clinical decision rules with LLMs for safe pediatric triage?"



# The 4 Hidden States

The agent tracks 4 mutually exclusive states representing every possible combination of how the child's symptoms appear vs. what the child's actual underlying triage state is:
State 1 (S1): Symptoms look low-risk, actually low-risk (Minor/self-limiting condition).
State 2 (S2): Symptoms look high-risk, actually high-risk (Genuinely urgent or emergency condition).
State 3 (S3): Symptoms look low-risk, actually high-risk (Serious condition with subtle or early symptoms).
State 4 (S4): Symptoms look high-risk, actually low-risk (Alarming symptoms caused by a minor or non-urgent condition).

* Total Low-Risk Probability:
P(Low Risk) = P(S1) + P(S4)

* Total High-Risk Probability:
P(High Risk) = P(S2) + P(S3)

The important safety state is S3 because it represents a potentially dangerous condition that does not initially appear severe. This is the false-reassurance failure mode.
S4 represents the opposite situation: the symptoms appear concerning, but the underlying condition is ultimately non-urgent.

# Possible Actions

* **Monitor at Home**
* **Contact Nurse Line**
* **Schedule Pediatrician Visit**
* **Seek Emergency Care (ER)**

The hidden state and the action are different concepts.

The hidden state represents what is actually happening to the child.

The action represents what the agent recommends based on its current probability distribution and safety rules.

# Signals (Evidences the Agent Checks)

## Level 1 - Safety / Escalation Layer

Certain observations should not be treated as ordinary Bayesian evidence alone.

Examples include:
* Significant breathing difficulty
* Signs of severe dehydration
* Seizure
* Severe or rapidly worsening condition
* Other predefined emergency red flags

If a hard safety rule is triggered, the system should escalate rather than allowing a probability calculation to produce false reassurance.


## Level 2 - Checked on Every Case if Safety layer yields a false result

* Breathing difficulty
* Level of alertness / responsiveness
* Hydration and ability to keep fluids down
* Urination frequency
* Fever / temperature
* Vomiting/Diarrhea

# Observations

The table below is my own prediction based on the architecture's signals. These are assumptions, not confirmed medical probabilities. Testing and clinical validation would be required before using these observations in a real healthcare system.

| Observation                                                                 | What it might suggest                                         |
| --------------------------------------------------------------------------- | ------------------------------------------------------------- |
| Mild symptoms, normal breathing, normal hydration, child alert              | Likely S1 (low-risk, actually low-risk)                       |
| Severe breathing difficulty with worsening symptoms                         | Likely S2 (high-risk, actually high-risk)                     |
| Child appears relatively well but symptoms are worsening rapidly            | Could shift belief toward S3                                  |
| Child looks very uncomfortable but is otherwise alert, hydrated and stable  | Could represent S4                                            |
| High fever alone without other concerning observations                      | Does not automatically imply high-risk state                  |
| Symptoms improving over time                                                | Shifts belief toward lower-risk states                        |
| Sudden deterioration after initially mild symptoms                          | Shifts belief toward S3 or S2                                 |
| Significant red-flag symptom                                                | Should trigger escalation regardless of the overall posterior |

# Rough cost of a wrong decision in each direction

Wrong decision for S1/S4: These are the cases where the condition was not critical but the agent determined it serious. In such cases , there are financial cost involved , anxiety and also use of emrgency resources.

Wrong decision for S2: Serious situation because the obvious high risk signs were missed.

Wrong decision for S3: This is the most tricky situation because the signs observed looked low-risk and it is easier for the agent to inccorectly assure the parents.

Both S2 and S3 have serious clinical implications because the child's health is at risk but S3 is an important failure mode because it is harder to detect as the signs point towards normalcy.




