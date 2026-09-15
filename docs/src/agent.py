import random

random.seed(42)

states = ["S1","S2","S3","S4","S5"]
priors = [0.57,0.20,0.10,0.10,0.03]
priors_dict = {
    "S1": 0.57,
    "S2": 0.20,
    "S3": 0.10,
    "S4": 0.10,
    "S5": 0.03
}

CHECK_COSTS = {"EA": 1, "EC": 3, "EE": 5, "EB": 8, "ED": 0}

# Safety override layer. These are signs I consider unambiguous enough that
# waiting for the Bayesian pipeline to agree adds delay for no real benefit.
# Any single one present triggers immediate Emergency, skipping belief
# updates and thresholds entirely. Checked before any other reasoning runs.
RED_FLAG_KEYWORDS = ["unresponsive", "mottled", "severe respiratory distress"]

def check_red_flags(evidence_text):
    evidence_lower = evidence_text.lower()
    for flag in RED_FLAG_KEYWORDS:
        if flag in evidence_lower:
            return True
    return False

ea_likelihoods = {
    "Normal": {"S1": 0.80, "S2": 0.30, "S3": 0.70, "S4": 0.70, "S5": 0.50},
    "Reduced": {"S1": 0.20, "S2": 0.70, "S3": 0.30, "S4": 0.30, "S5": 0.50}
}
ec_likelihoods = {
    "Normal": {"S1": 0.85, "S2": 0.15, "S3": 0.55, "S4": 0.60, "S5": 0.50},
    "Elevated": {"S1": 0.15, "S2": 0.85, "S3": 0.45, "S4": 0.40, "S5": 0.50}
}
eb_likelihoods = {
    "Reassuring": {"S1": 0.90, "S2": 0.10, "S3": 0.35, "S4": 0.75, "S5": 0.50},
    "Concerning": {"S1": 0.10, "S2": 0.90, "S3": 0.65, "S4": 0.25, "S5": 0.50}
}
ed_likelihoods = {
    "Yes": {"S1": 0.55, "S2": 0.40, "S3": 0.45, "S4": 0.50, "S5": 0.50},
    "No":  {"S1": 0.45, "S2": 0.60, "S3": 0.55, "S4": 0.50, "S5": 0.50}
}
ee_likelihoods = {
    "Reassuring": {"S1": 0.85, "S2": 0.10, "S3": 0.40, "S4": 0.70, "S5": 0.50},
    "Concerning": {"S1": 0.15, "S2": 0.90, "S3": 0.60, "S4": 0.30, "S5": 0.50}
}

test_cases = {
    "TC1": {"evidence": "Mild symptoms, normal breathing/hydration, alert",
             "likelihoods": {"S1": 0.80, "S2": 0.20, "S3": 0.40, "S4": 0.30, "S5": 0.25}},
    "TC2": {"evidence": "Lethargic, pink cap refill, mild tachypnea",
             "likelihoods": {"S1": 0.10, "S2": 0.40, "S3": 0.55, "S4": 0.10, "S5": 0.25}},
    "TC3": {"evidence": "Normal behavior, pale/3-4s cap refill, normal respiration",
             "likelihoods": {"S1": 0.85, "S2": 0.01, "S3": 0.09, "S4": 0.10, "S5": 0.25}},
    "TC4": {"evidence": "Irritable, pale/3-4s cap refill, mild tachypnea",
             "likelihoods": {"S1": 0.25, "S2": 0.30, "S3": 0.45, "S4": 0.35, "S5": 0.25}},
    "TC5": {"evidence": "Sleepy but consolable, pink/normal, normal respiration",
             "likelihoods": {"S1": 0.70, "S2": 0.05, "S3": 0.15, "S4": 0.20, "S5": 0.25}},
    "TC6": {"evidence": "Lethargic, gray/mottled >5s, severe tachypnea",
             "likelihoods": {"S1": 0.02, "S2": 0.85, "S3": 0.30, "S4": 0.05, "S5": 0.25}},
    "TC7": {"evidence": "Playing normally, pink/normal, moderate tachypnea/retractions",
             "likelihoods": {"S1": 0.30, "S2": 0.25, "S3": 0.50, "S4": 0.35, "S5": 0.25}},
    "TC8": {"evidence": "Irritable, gray/4-5s cap refill, moderate tachypnea/retractions",
             "likelihoods": {"S1": 0.05, "S2": 0.55, "S3": 0.40, "S4": 0.15, "S5": 0.25}},
    "TC9": {"evidence": "Sleepy but consolable, pale/3-4s cap refill, mild tachypnea",
             "likelihoods": {"S1": 0.45, "S2": 0.15, "S3": 0.35, "S4": 0.30, "S5": 0.25}},
    "TC10": {"evidence": "Lethargic, pink/normal cap refill, normal respiration",
              "likelihoods": {"S1": 0.08, "S2": 0.25, "S3": 0.50, "S4": 0.15, "S5": 0.25}},
    "TC11": {"evidence": "Mild fussiness, normal breathing, good hydration, brief consolable crying",
              "likelihoods": {"S1": 0.75, "S2": 0.10, "S3": 0.20, "S4": 0.15, "S5": 0.25}},
    "TC12": {"evidence": "Slightly reduced activity, normal breathing, adequate hydration, low-grade fever",
              "likelihoods": {"S1": 0.70, "S2": 0.12, "S3": 0.22, "S4": 0.15, "S5": 0.25}},
    "TC13": {"evidence": "Restless, mild tachypnea, reduced feeding, prolonged fussiness",
              "likelihoods": {"S1": 0.25, "S2": 0.30, "S3": 0.55, "S4": 0.30, "S5": 0.25}},
    "TC14": {"evidence": "Restless, moderate tachypnea, poor feeding, delayed capillary refill",
              "likelihoods": {"S1": 0.22, "S2": 0.32, "S3": 0.58, "S4": 0.28, "S5": 0.25}},
    "TC15": {"evidence": "Playful, normal breathing, excellent hydration, no fever",
              "likelihoods": {"S1": 0.90, "S2": 0.02, "S3": 0.05, "S4": 0.05, "S5": 0.25}},
    "TC16": {"evidence": "Unresponsive to stimulation, mottled skin, severe respiratory distress",
              "likelihoods": {"S1": 0.03, "S2": 0.90, "S3": 0.35, "S4": 0.05, "S5": 0.25}},
    "TC17": {"evidence": "Clingy, less playful than usual, mild fever, slightly reduced fluid intake",
              "likelihoods": {"S1": 0.45, "S2": 0.20, "S3": 0.40, "S4": 0.30, "S5": 0.25}},
}


def run_p0(children):
    results = []
    for child in children:
        result = run_baseline(child["true_state"])
        results.append({
            "true_state": child["true_state"],
            "action": "Monitor",
            "cost": result["cost"],
            "label": result["label"],
            "checks_used": 0
        })
    return results

def run_p2(children):
    results = []
    for child in children:
        evidence_text = test_cases[child["chosen_case"]]["evidence"]
        if check_red_flags(evidence_text):
            action = "Emergency evaluation"
            checks_used = 0
        else:
            posterior = bayes_update(priors_dict, test_cases[child["chosen_case"]]["likelihoods"])
            action_result = compute_action(posterior, child["true_state"])
            action = action_result["action"]
            checks_used = action_result["checks_used"]
        result = score_case(action, child["true_state"])
        results.append({
            "true_state": child["true_state"],
            "action": action,
            "cost": result["cost"],
            "label": result["label"],
            "checks_used": checks_used
        })
    return results

def run_p3(children):
    results = []
    for child in children:
        evidence_text = test_cases[child["chosen_case"]]["evidence"]
        if check_red_flags(evidence_text):
            action = "Emergency evaluation"
            checks_used = 0
        else:
            posterior = bayes_update(priors_dict, test_cases[child["chosen_case"]]["likelihoods"])
            action_result = compute_action_p3(posterior, child["true_state"])
            action = action_result["action"]
            checks_used = action_result["checks_used"]
        result = score_case(action, child["true_state"])
        results.append({
            "true_state": child["true_state"],
            "action": action,
            "cost": result["cost"],
            "label": result["label"],
            "checks_used": checks_used
        })
    return results

# P3 escalation chain, ordered by info-per-cost: EA (0.118) > EC (0.081) > EE (~0.06) > EB (0.046)
# ED intentionally excluded from the automatic chain: it's free, but per the
# value-of-information rule (Section 14), a check whose answer can't reliably
# change the action has ~zero value regardless of cost. Kept defined for
# reference / possible future use, not wired into the default policy.
def compute_action_p3(posterior, true_state):
    initial_action = classify_p_high(posterior['S2'] + posterior['S3'] + posterior['S5'])
    if initial_action != "Consult doctor":
        return {"action": initial_action, "checks_used": 0}

    result = try_source(posterior, true_state, ea_likelihoods)
    if result["action"] != "Consult doctor":
        return {"action": result["action"], "checks_used": 1}

    result = try_source(result["posterior"], true_state, ec_likelihoods)
    if result["action"] != "Consult doctor":
        return {"action": result["action"], "checks_used": 2}

    result = try_source(result["posterior"], true_state, ee_likelihoods)
    if result["action"] != "Consult doctor":
        return {"action": result["action"], "checks_used": 3}

    result = try_source(result["posterior"], true_state, eb_likelihoods)
    return {"action": result["action"], "checks_used": 4}

def try_source(posterior, true_state, likelihood_table):
    new_posterior = check_evidence_source(posterior, true_state, likelihood_table)
    p_high = new_posterior['S2'] + new_posterior['S3'] + new_posterior['S5']
    result_classify = classify_p_high(p_high)
    return {"posterior": new_posterior, "action": result_classify}


def classify_p_high(p_high):
    if p_high < 0.032:
        return "Monitor"
    elif p_high > 0.40:
        return "Emergency evaluation"
    else:
        return "Consult doctor"

def generate_children(n):
    children = []
    for i in range(n):
        children.append(simulate_one_child())
    return children

def simulate_one_child():
    weights=[]
    case_names=[]
    true_state = random.choices(states,weights=priors,k=1)[0]
    for case in test_cases:
        weights.append(test_cases[case]['likelihoods'][true_state])
        case_names.append(case)

    chosen_case = random.choices(case_names,weights=weights,k=1)[0]

    return({"true_state": true_state,
            "chosen_case": chosen_case,})

def bayes_update(priors,likelihoods):
    posterior = {}
    pe = 0
    for state,likelihood in likelihoods.items():
        unnormalized = priors[state]*likelihood
        pe += unnormalized
        posterior[state]=unnormalized

    for state in posterior:
        posterior[state] /= pe

    return posterior

def compute_action(posterior,true_state):
    p_high = posterior['S2'] + posterior['S3'] + posterior['S5']

    if p_high<0.032:
        return {"action": "Monitor", "checks_used": 0}
    elif p_high>0.40:
        return {"action": "Emergency evaluation", "checks_used": 0}
    else:
        drawn_outcome = draw_outcome_ea(true_state)
        ea_likelihood_row = ea_likelihoods[drawn_outcome]

        posterior_ea = bayes_update(posterior,ea_likelihood_row)
        p_high_ea = posterior_ea['S2'] + posterior_ea['S3'] + posterior_ea['S5']
        if p_high_ea < 0.032:
            return {"action": "Monitor", "checks_used": 1}
        elif p_high_ea > 0.40:
            return {"action": "Emergency evaluation", "checks_used": 1}
        else:
            return {"action": "Consult doctor", "checks_used": 1}

def draw_outcome_ea(true_state):
    drawn_outcome = random.choices(["Normal","Reduced"],weights=[ea_likelihoods["Normal"][true_state], ea_likelihoods["Reduced"][true_state]] ,k=1)[0]
    return drawn_outcome

def score_case(action, true_state):
    is_low_risk = true_state in ["S1", "S4"]

    if is_low_risk:
        if action == "Monitor":
            return {"cost": 0, "label": "true negative"}
        else:
            return {"cost": 1, "label": "false positive"}
    else:
        if action == "Emergency evaluation":
            return {"cost": 0, "label": "true positive"}
        elif action == "Consult doctor":
            return {"cost": 20, "label": "partial miss"}
        else:
            return {"cost": 30, "label": "false negative"}

def check_evidence_source(posterior, true_state, likelihood_table):
    outcomes = list(likelihood_table.keys())
    weights = [likelihood_table[outcome][true_state] for outcome in outcomes]

    drawn_outcome = random.choices(outcomes, weights=weights, k=1)[0]

    outcome_likelihoods = likelihood_table[drawn_outcome]
    new_posterior = bayes_update(posterior, outcome_likelihoods)

    return new_posterior

def run_baseline(true_state):
    action = "Monitor"
    result = score_case(action, true_state)
    return result

# Cumulative info cost for P3's fixed chain order: EA -> EC -> EE -> EB
def info_cost_for_checks(n):
    if n == 0:
        return 0
    elif n == 1:
        return CHECK_COSTS["EA"]
    elif n == 2:
        return CHECK_COSTS["EA"] + CHECK_COSTS["EC"]
    elif n == 3:
        return CHECK_COSTS["EA"] + CHECK_COSTS["EC"] + CHECK_COSTS["EE"]
    else:
        return CHECK_COSTS["EA"] + CHECK_COSTS["EC"] + CHECK_COSTS["EE"] + CHECK_COSTS["EB"]

def compute_metrics(results):
    n = len(results)
    total_decision_cost = sum(r["cost"] for r in results)

    correct = sum(1 for r in results if r["label"] in ["true negative", "true positive"])
    accuracy = correct / n

    flagged = [r for r in results if r["action"] != "Monitor"]
    true_high_risk = [r for r in results if r["true_state"] not in ["S1", "S4"]]

    true_positives_flagged = sum(1 for r in flagged if r["true_state"] not in ["S1", "S4"])

    precision = true_positives_flagged / len(flagged) if flagged else 0
    recall = true_positives_flagged / len(true_high_risk) if true_high_risk else 0

    human_review_rate = len(flagged) / n

    total_info_cost = sum(info_cost_for_checks(r["checks_used"]) for r in results)
    avg_questions_asked = sum(r["checks_used"] for r in results) / n

    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "decision_cost": total_decision_cost,
        "info_cost": total_info_cost,
        "questions_asked": avg_questions_asked,
        "human_review_rate": human_review_rate
    }


if __name__ == "__main__":
    children = generate_children(100)

    p0_results = run_p0(children)
    p2_results = run_p2(children)
    p3_results = run_p3(children)

    p0_metrics = compute_metrics(p0_results)
    p2_metrics = compute_metrics(p2_results)
    p3_metrics = compute_metrics(p3_results)

    print("P0:", p0_metrics)
    print("P2:", p2_metrics)
    print("P3:", p3_metrics)
