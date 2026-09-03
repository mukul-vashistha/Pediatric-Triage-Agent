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


# Belief Table :

## State names:

* S1 = True Low-risk
* S2 = True High-risk
* S3 = Hidden High-risk
* S4 = False High-risk

## Assigning Prior Probabilities (Before seeing evidences the follwing are what we believe how likely each state is)

* S1 = 0.60
* S2 = 0.20
* S3 = 0.10
* S4 = 0.10

S1+S2+S3+S4 = 1.00

## Defining the evidence

E = Mild symptoms + normal breathing + normal hydration + child alert.

This is the observed evidence.

## Assigning likelihoods (Asking if this state is true then how likely this particular evidence is supposed to occur)

* P(E | S1)= 0.80
* P(E | S2)= 0.20
* P(E | S3)= 0.40
* P(E | S4)= 0.30

## Calculating un-normalized posteriors : P(E | Si) X P(Si)
* S1 => 0.8*0.6 = 0.48
* S2 => 0.2*0.2 = 0.04
* S3 => 0.4*0.1 = 0.04
* S4 => 0.3*0.1 = 0.03

P(E) = 0.48 + 0.04 + 0.04 + 0.03 = 0.59

Given our four possible states and the priors/likelihoods we assigned, the overall probability of observing evidence E is 0.59.

## Calculating posterior probabilities for each state 

P(Si | E) = (P(E | Si)*P(Si))/P(E)

So after observing evidences we get the following updated beliefs:

* S1 = 0.8136 => 81.36%
* S2 = 0.0678 => 6.78%
* S3 = 0.0678 => 6.78%
* S4 = 0.0508 => 5.08%

0.8136 + 0.0678 + 0.0678 + 0.0508 => 1.00 (Sum of Posterior belief should also add to 1)


| State | Prior | Posterior | Change |
|---|---:|---:|:---:|
| S1 — True Low-Risk | 0.60 | 0.8136 | ↑ |
| S2 — True High-Risk | 0.20 | 0.0678 | ↓ |
| S3 — Hidden High-Risk | 0.10 | 0.0678 | ↓ |
| S4 — False High-Risk | 0.10 | 0.0508 | ↓ |


## Action thresholds (based on updated probabilities of each state)

There is no universally validated probability threshold for pediatric medical decision-making. Real triage systems (as recommended by WHO) uses red / yellow / green acuity categories based on clinical signs (not Bayesian probability), with red requiring immediate care, yellow urgent care, and green non-urgent care. The thresholds are being adopted as illustrative thresholds for this simulation, inspired by the study (https://pmc.ncbi.nlm.nih.gov/articles/PMC9723221/):

| Risk Probability        | Action                                             |
|-------------------------|----------------------------------------------------|
| Low (<=8%)              | Monitor                                            |
| Medium (>8% and <=40%)  | Consult doctor (nurse line / pediatrician)         |
| High (>40%)             | Emergency evaluation                               |

Our calculations yielded the following results after update:

* P(Low Risk | E ) = P(S1) + P(S4) = 0.8136 + 0.0508 = 0.8644 (86.44%)

* P(High Risk | E )= P(S2) + P(S3) = 0.0678 + 0.0678 = 0.1356 (13.56%)

Although we have both the probabilities available but here for decision making we ar choosing the P(High Risk | E ) because the primary decision concern is the high risk underlying state. 

So now based on that we see that P(High Risk | E)= 13.56% and it falls under the Medium category so that agent would suggest the action as "Consult doctor".

Thus, in this simulated example, the reassuring evidence reduces the estimated high-risk probability from the prior level, but does not reduce it enough to cross the model's lowest-risk threshold.

## Test Cases (values and symptoms are simulated)

* TC1 is calculated in detail before this section. For rest of the Test Cases the necesaary final results have been displayed.

| TC# | Evidence | P(E\|S1) | P(E\|S2) | P(E\|S3) | P(E\|S4) | P(High Risk\|E) | Action |
|---:|---|---:|---:|---:|---:|---:|---|
| 1 | Mild symptoms, normal breathing/hydration, alert | 0.80 | 0.20 | 0.40 | 0.30 | 13.56% | Consult doctor |
| 2 | Lethargic, pink cap refill, mild tachypnea | 0.10 | 0.40 | 0.55 | 0.10 | 65.85% | Emergency evaluation |
| 3 | Normal behavior, pale/3–4s cap refill, normal respiration | 0.85 | 0.01 | 0.09 | 0.10 | 2.07% | Monitor |
| 4 | Irritable, pale/3–4s cap refill, mild tachypnea | 0.25 | 0.30 | 0.45 | 0.35 | 36.21% | Consult doctor |
| 5 | Sleepy but consolable, pink/normal, normal respiration | 0.70 | 0.05 | 0.15 | 0.20 | 5.38% | Monitor |
| 6 | Lethargic, gray/mottled >5s, severe tachypnea | 0.02 | 0.85 | 0.30 | 0.05 | 92.17% | Emergency evaluation |
| 7 | Playing normally, pink/normal, moderate tachypnea/retractions | 0.30 | 0.25 | 0.50 | 0.35 | 31.75% | Consult doctor |
| 8 | Irritable, gray/4–5s cap refill, moderate tachypnea/retractions | 0.05 | 0.55 | 0.40 | 0.15 | 76.92% | Emergency evaluation |
| 9 | Sleepy but consolable, pale/3–4s cap refill, mild tachypnea | 0.45 | 0.15 | 0.35 | 0.30 | 17.81% | Consult doctor |
| 10 | Lethargic, pink/normal cap refill, normal respiration | 0.08 | 0.25 | 0.50 | 0.15 | 61.35% | Emergency evaluation |
| 11 | Mild fussiness, normal breathing, good hydration, brief consolable crying | 0.75 | 0.10 | 0.20 | 0.15 | 7.92% | Monitor *(boundary, just below 8%)* |
| 12 | Slightly reduced activity, normal breathing, adequate hydration, low-grade fever | 0.70 | 0.12 | 0.22 | 0.15 | 9.56% | Consult doctor *(boundary, just above 8%)* |
| 13 | Restless, mild tachypnea, reduced feeding, prolonged fussiness | 0.25 | 0.30 | 0.55 | 0.30 | 38.98% | Consult doctor *(boundary, just below 40%)* |
| 14 | Restless, moderate tachypnea, poor feeding, delayed capillary refill | 0.22 | 0.32 | 0.58 | 0.28 | 43.26% | Emergency evaluation *(boundary, just above 40%)* |
| 15 | Playful, normal breathing, excellent hydration, no fever | 0.90 | 0.02 | 0.05 | 0.05 | 1.62% | Monitor |
| 16 | Unresponsive to stimulation, mottled skin, severe respiratory distress | 0.03 | 0.90 | 0.35 | 0.05 | 90.34% | Emergency evaluation |
| 17 | Clingy, less playful than usual, mild fever, slightly reduced fluid intake | 0.45 | 0.20 | 0.40 | 0.30 | 21.05% | Consult doctor |

## Failures/Limitations

* Two actions got merged into one
I planned for 4 actions (monitor, nurse line, pediatrician, ER), but my threshold rule only has 3 bands. "Nurse line" and "pediatrician visit" both landed under "Consult doctor" because risk probability alone can't tell them apart and that would need something like how urgent not just how risky.

2. My numbers are for illustration and not real data
Every likelihood number in this file came from reasoning it out, not from actual pediatric cases. In Test Case 2, changing just one sign (lethargy) flipped the result from "consult a doctor" to "go to the ER." That shows how much a single guessed number can swing the outcome.

3. The trickiest state is also the most important one
S3 (Hidden High-risk) means "actually dangerous, but doesn't look dangerous yet." That's really hard to tell apart from S1 (actually fine) using symptoms alone and that is basically the whole real-world problem this project is trying to help with.

4. One evidence snapshot isn't the full picture
Right now, each test case is a single moment in time. A real child's symptoms change over hours and a kid who looks mildly sick now might look much worse in 2 hours. This model doesn't yet capture that a symptom getting worse might matter more than the symptom itself.

5. Human in the loop was initial part of the idea but isn't implemented at the current threshold rule.

## Architecture diagrams

* Agent Flow
<div align="center">
<img src="images/agent_flow.png" width="1000">
</div>

* Hidden State Grid
<div align="center">
<img src="images/state_grid.png" width="1000">
</div>

* Bayesian Update Steps
<div align="center">
<img src="images/bayes_steps.png" width="1000">
</div>



## References and Resources

The following papers and repository were used to understand Bayesian reasoning,pediatric risk stratification, emergency triage and approaches for reasoning under uncertainty. These papers helped me understand how to design the model, but the specific probabilities and thresholds I used are assumptions for this simulation, not established medical rules.

| Link | Why Relevant |
|---|---|
| [Bayesian Application in Clinical AI](https://pmc.ncbi.nlm.nih.gov/articles/PMC10497324/) | Discusses the application of Bayesian reasoning in clinical AI and provides background for probabilistic reasoning in healthcare. |
| [Bayesian Belief Network](https://pmc.ncbi.nlm.nih.gov/articles/PMC9748028/) | Discusses Bayesian Belief Networks and their use for reasoning under uncertainty. |
| [Pediatric Risk Stratification](https://pmc.ncbi.nlm.nih.gov/articles/PMC9723221/) | Provides risk-stratification thresholds that inspired the illustrative action thresholds used in this Week 1 simulation. |
| [Pediatric Emergency Triage and Vital Signs](https://pmc.ncbi.nlm.nih.gov/articles/PMC7872278/) | Examines whether objective vital signs can improve pediatric emergency triage. This is relevant to the S3 state: **looks low-risk but is actually high-risk**. |
| [ED Triage ML — Children](https://github.com/HasegawaLab/ED_triage_ML_children) | Repository containing a summary script for the study *"Machine learning-based prediction of clinical outcomes for children during emergency department triage."* |





