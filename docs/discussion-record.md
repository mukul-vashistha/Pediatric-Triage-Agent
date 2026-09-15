# Community Contributions

Public discussion connected to this project, organized by platform.

---

## X (Twitter)

**Reply to [@zakkohane](https://x.com/zakkohane)**
https://x.com/MukulVashistha/status/2088223929295065219
Contribution: Could the same apply to pediatric triage, where the problem isn't just predicting the final recommendation but correctly inferring the child's underlying state from incomplete and ever-changing symptoms, so the child can be guided to the right level of care.
Response: No response.
Outcome: No change. Confirmed the core framing already chosen: the agent needs to infer a hidden state, not just predict a final action directly.

**Reply to [@DrDevSK](https://x.com/DrDevSK)**
https://x.com/MukulVashistha/status/2088293003538714870
Contribution: Are current AI solutions more focused on optimizing the final outcome rather than identifying the underlying patient status from incomplete observations?
Response: No response.
Outcome: No change. Reinforced the same design choice as above, that identifying the underlying state matters more than optimizing the final label alone.

**Original post**
https://x.com/MukulVashistha/status/2088316337114562833
Contribution: When an AI system is uncertain about a child's symptoms, should uncertainty itself be treated as a reason to escalate to a doctor?
Response: No response.
Outcome: No change. Confirmed the escalation-on-uncertainty policy already built into the threshold-based decision logic (Decision Policy, Section 7).

**Reply to [@DocPriyamMD](https://x.com/DocPriyamMD)**
https://x.com/MukulVashistha/status/2088330315635024289
Contribution: Should we continue looking at current symptoms to determine what disease a child is suffering from, instead of observing hidden symptoms, given that symptoms are ever-evolving?
Response: No response.
Outcome: No change. Reinforced the rationale for S3 (hidden high-risk), the state specifically meant to represent danger that doesn't show clearly in current symptoms.

**Reply to [@AmineKorchiMD](https://x.com/AmineKorchiMD)**
https://x.com/MukulVashistha/status/2088490831187779949
Contribution: My point was that AI should delegate to human intervention in case of uncertainty, and should focus on the underlying state of a situation instead of ignoring uncertainty and unknown conditions.
Response: No response.
Outcome: No change. Reinforced the human escalation trigger design (Section 7.4, Trigger 1: belief remains ambiguous after all affordable checks).

**Cross-post of the original LinkedIn article**
https://x.com/MukulVashistha/status/2088713785959940440
Contribution: "Check out my latest article: Exploring AI for Pediatric Care: Making Decisions With Incomplete Information," linking to the original article.
Response: No response.
Outcome: Original post, not reply-driven. Extended the reach of the initial problem-statement introduction to a second platform.

**Announcing the safety override**
https://x.com/MukulVashistha/status/2099420127452377467
Contribution: "Building an AI triage agent taught me one thing: safety should come before intelligence. Before Bayesian reasoning or uncertainty, a simple hard-rule layer handles critical red flags and escalates immediately."
Response: No response.
Outcome: Original post, not reply-driven. Announced the hardcoded safety override added following the failure analysis (Section 7.3).

**Announcing the finished paper**
https://x.com/MukulVashistha/status/2099775420434653373
Contribution: "Published the full write-up on my Bayesian pediatric triage agent: tracks 5 hidden conditions, decides when to ask one more question vs. act now, and caught a real bug through its own failure analysis." Links to the LinkedIn paper announcement.
Response: No response.
Outcome: Original post, not reply-driven. Cross-posted the paper announcement to a second platform.

---

## Reddit

**r/learnmachinelearning**
https://www.reddit.com/r/learnmachinelearning/comments/1vohmmp/missing_information_and_next_step/
Contribution: If a parent doesn't know an important detail about their child's symptoms, should an AI system make its best recommendation with the available information, or ask additional questions before deciding the appropriate level of care?
Response: Could depend on how the data will be used. Will it be looked at per child? If so, guessing information on a single-person basis wouldn't seem reasonable, especially if the parents didn't answer the same question.
My follow-up: Agreed that for one child, the AI shouldn't just guess an important symptom and treat it as true.
Outcome: No structural change. Confirmed a principle already held: the agent should ask for more evidence rather than assume an unknown symptom, matching the evidence-gathering chain rather than a single-shot guess.

**r/HealthTech**
https://www.reddit.com/r/HealthTech/
Contribution: Discussed pediatric AI triage and asked for feedback on uncertainty and human intervention.
Response: No response captured from this thread.
Outcome: No design change recorded from this thread specifically.

**r/EmergencyRoom**
https://www.reddit.com/r/EmergencyRoom/comments/1vp9b09/how_do_you_decide_between_going_straight_to_the/
Contribution: Asked how practitioners decide between going straight to the ER or a non-ER option.
Response: Anxious parents never give proper information, which solidifies the belief that AI needs to know more and should ask follow-up questions to reduce uncertainty.
My follow-up: Continuing to build the agent whose aim is to suggest an appropriate level of care, not a diagnosis.
Outcome: Confirmed the value-of-information evidence-gathering approach (E-A through E-B) rather than trying to diagnose the underlying disease outright.

**r/LLMDevs — question selection and decision-layer design**
https://www.reddit.com/r/LLMDevs/comments/1vqo2bz/how_should_an_llm_agent_decide_what_to_ask_next/
Contribution: Discussed LLM-based question selection and decision-layer design.
Response: You don't currently have enough validated pediatric symptom-transition data to claim that a Bayesian/HMM model can reliably determine real clinical states.
My follow-up: In real-world implementation, a safety layer would be put in place as a first step, and if that isn't sufficient, other probabilistic models could handle the remainder.
Outcome: This exchange directly anticipated the hardcoded safety override built later in the project, well before any failure analysis had suggested it was needed. See `agent.py`, `check_red_flags`, and the paper's Section 7.3.

**r/LLMDevs — decision cost vs. information cost finding**
https://www.reddit.com/r/LLMDevs/comments/1wbezui/my_smarter_bayesian_agent_has_lower_decision_cost/
Contribution: Posted about the Bayesian triage agent — the value-of-information policy cuts decision cost roughly 3x, but total cost (including information-gathering) is actually higher than the simpler policy. Asked whether this is expected or a sign of miscalibrated check-costs.
Response: Three separate replies converged on similar advice. One pointed out that value-of-information is meant to maximize expected utility, not minimize total cost outright, and that if the cost structure penalizes evidence-gathering more heavily than mistakes, a simpler fixed-threshold policy will look artificially cheaper; suggested tuning the cost weights or capping the information budget per case. A second suggested converting both decision errors and evidence costs into the same unit (for example, dollars), so the stopping rule has a real anchor instead of comparing two different currencies. A third suggested capping information-gathering spend at some fraction of the decision cost being avoided, forcing a decision once that cap is hit.
My follow-up: Agreed with the first reply, given the project's own cost setup (a missed dangerous case costs far more than a false alarm, so spending more upfront to avoid it is justified). Agreed with the third reply that a spending cap is a reasonable approach.
Outcome: Confirms and sharpens the hybrid stop-rule idea already reasoned through in the paper's Generalization section (Section 11, Prompt 2): a value-based stop rule plus a hard spending cap as backstop. The "same currency" suggestion, pricing decision cost and information cost in one shared unit, is a genuinely new, concrete refinement not yet implemented in `agent.py`, and a strong candidate for a future version.

**r/AIQuality — same finding, second community**
https://www.reddit.com/r/AIQuality/comments/1wbf07c/my_smarter_bayesian_agent_has_lower_decision_cost/
Contribution: Same finding as above, posted separately to a second relevant community: the value-of-information policy cuts decision cost but raises total cost once information-gathering is counted. Asked whether this is an expected pattern.
Response: Awaiting reply.
Outcome: Confirms this and the r/LLMDevs post above are two distinct posts to two different communities, not a duplicate link, resolving an earlier open question about identical post titles.

---

## LinkedIn

**Original problem statement**
https://www.linkedin.com/posts/activity-7494479362956685314-uBiZ
Contribution: Introduced the original problem: an agent that must decide whether a child needs to be monitored at home, seen by a doctor, or taken to emergency care, when the parent's description of symptoms is incomplete and the true condition is never directly observable.
Outcome: Original post, not reply-driven.

**Adaptive evidence-gathering**
https://www.linkedin.com/posts/activity-7500148338743410688-ZFpM
Contribution: Introduced the idea of sequential evidence-gathering and belief updating, rather than making one fixed decision from the first piece of information available.
Outcome: Original post, not reply-driven.

**Why more data isn't always better**
https://www.linkedin.com/posts/activity-7500560318205722624-L45R
Contribution: Introduced the value-of-information idea: more evidence isn't automatically better once the cost of gathering it is actually counted.
Outcome: Original post, not reply-driven.

**Full paper published**
https://lnkd.in/p/dX-fxnKV
Contribution: Published the full paper with the PDF attached, summarizing the five hidden states, the value-of-information result (roughly 3x fewer wrong decisions at a higher information-gathering cost), and the real bug caught through failure analysis.
Outcome: Original post, not reply-driven. Closes the arc from the original problem statement through to the finished, compiled paper.