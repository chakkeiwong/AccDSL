"""Author finite documentary cases; no product/runtime code is imported."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, re

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[3]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def encode(x):
    if isinstance(x, F):
        return str(x)
    if isinstance(x, dict):
        return {k: encode(v) for k, v in x.items()}
    if isinstance(x, list):
        return [encode(v) for v in x]
    return x

def write(name, data):
    (OUT / name).write_text(json.dumps(encode(data), indent=2) + "\n")

def event(identity, journal, components=None, cash_class=None):
    return {"id": identity, "journal": {k: str(F(v)) for k, v in journal.items()},
            "components_after": components,
            "cash_class": cash_class, "replay": "identical=no_change; changed_payload=conflict"}

def vfa_components(financial, mortality, ra, csm, loss):
    return dict(financial_benefit=str(F(financial)), mortality_pv=str(F(mortality)),
                ra=str(F(ra)), csm=str(F(csm)), loss_component=str(F(loss)))

def vfa_case(up, died):
    label = ("up" if up else "down") + ("_death" if died else "_alive")
    value, benefit, csm, loss = (120, 108, 19, 0) if up else (80, 90, 0, 3)
    jump = value - 100
    paid = 20 if died else 0
    revenue = 22 if up else 0
    events = [
        event("recognize_and_receive", {"cash": 110, "lrc": -110},
              vfa_components(99, 2, 1, 8, 0), "operating"),
        event("buy_underlying", {"underlying": 100, "cash": -100}, cash_class="investing"),
        event("pre_service_remeasurement", {
            "underlying": jump, "investment_result": -jump,
            "insurance_finance": jump, "lrc": -jump-loss, "onerous_loss": loss},
            vfa_components(benefit, 2, 1, csm, loss)),
        event("complete_service", {"lrc": 3+csm, "service_revenue": -revenue,
                                  "onerous_reversal": -loss},
              vfa_components(benefit, 0, 0, 0, 0)),
        event("incur_mortality", {"claim_expense": paid, "lic": -paid}),
        event("sell_underlying", {"cash": value, "underlying": -value}, cash_class="investing"),
        event("settle_investment_component", {"lrc": benefit, "cash": -benefit},
              vfa_components(0, 0, 0, 0, 0), "operating"),
        event("settle_mortality", {"lic": paid, "cash": -paid}, cash_class="operating"),
    ]
    profit = (22 if up else 0) - paid
    weight = F(3 if up else 1, 4) * F(1 if died else 9, 10)
    return {
        "id": label, "kind": "vfa", "group": "issued-vfa-2024",
        "contract": "coupled-life-investment", "market_state": "up" if up else "down",
        "death": died, "physical_weight": str(weight),
        "opening": {"cash": "50", "owner_capital": "-50"},
        "events": events,
        "expected": {"profit": str(profit), "cash": str(50+profit), "equity": str(50+profit),
                     "operating_cash": str(110-benefit-paid), "investing_cash": str(jump),
                     "revenue": str(revenue), "oci": "0", "liabilities": "0"}
    }

def gross_components(claim, premium, ra, loss):
    return {"claims": str(F(claim)), "future_premium": str(F(premium)),
            "ra": str(F(ra)), "csm": "0", "loss_component": str(F(loss))}

def held_components(premium, cost, loss):
    return {"recoveries": "50", "future_premium": str(F(premium)),
            "ra": "5/2", "cost_csm": str(F(cost)), "loss_recovery": str(F(loss))}

def acquisition_case(timely):
    recovery = F(15, 2) if timely else F(0)
    cost = F(5, 2)+recovery
    asset = F(55)+recovery
    zero_held = {k: "0" for k in held_components(0, 0, 0)}
    events = [
        event("pay_acquisition_before_recognition", {"acquisition_asset": 10, "cash": -10},
              cash_class="operating"),
        event("recognize_and_transfer_acquisition", {"onerous_loss": 15, "acquisition_asset": -10, "lrc": -5},
              {"issued": gross_components(100, 100, 5, 15)}),
        event("receive_issued_premium", {"cash": 100, "lrc": -100},
              {"issued": gross_components(100, 0, 5, 15)}, "operating"),
        event("recognize_held", {}, {"held": held_components(55, F(5, 2), 0)}),
        event("initial_loss_recovery", {"held_asset": recovery, "recovery_income": -recovery},
              {"held": held_components(55, cost, recovery)}),
        event("pay_held_premium", {"held_asset": 55, "cash": -55},
              {"held": held_components(0, cost, recovery)}, "operating"),
        event("complete_issued_service", {"lrc": 105, "service_revenue": -90, "onerous_reversal": -15},
              {"issued": gross_components(0, 0, 0, 0)}),
        event("present_acquisition_recovery", {"acquisition_expense": 10, "service_revenue": -10}),
        event("incur_claims", {"claim_expense": 100, "lic": -100}),
        event("release_held_coverage", {"held_asset": -asset, "held_premium_expense": 55,
                                       "loss_recovery_reversal": recovery},
              {"held": zero_held}),
        event("incur_held_recovery", {"held_receivable": 50, "recovery_income": -50}),
        event("pay_claims", {"lic": 100, "cash": -100}, cash_class="operating"),
        event("receive_held_recovery", {"cash": 50, "held_receivable": -50}, cash_class="operating")
    ]
    return {"id": "acquisition_" + ("timely" if timely else "late"), "kind": "acquisition",
            "issued_group": "issued-acquisition-2024", "held_group": "held-quota-2024",
            "treaty_entered_at_or_before_underlying_recognition": timely,
            "prior_acquisition_recoverability": {"premium": "100", "claims": "80", "ra": "5",
                                                "net_inflow": "15", "asset": "10"},
            "recognition_assumption_update": "claims80->100 at initial group recognition; no earlier onerous interval",
            "opening": {"cash": "50", "owner_capital": "-50"},
            "events": events,
            "expected": {"profit": "-15", "cash": "35", "equity": "35", "operating_cash": "-15",
                         "investing_cash": "0", "revenue": "100", "oci": "0", "liabilities": "0",
                         "initial_equity": str(F(35)+recovery), "initial_held_asset": str(asset),
                         "initial_issued_liability": "105"}}

def source_record(identity, pdf, txt, starts_ends, scope):
    text = (ROOT/txt).read_text()
    spans = []
    for label, begin, end in starts_ends:
        a = re.search(begin, text, re.M)
        assert a, (identity, label, "start")
        b = re.search(end, text[a.end():], re.M)
        assert b, (identity, label, "end")
        stop = a.end()+b.start()
        span = text[a.start():stop]
        spans.append({"id": label, "start": a.start(), "end": stop,
                      "offset_unit": "Unicode code points", "text": span,
                      "sha256": hashlib.sha256(span.encode()).hexdigest()})
    return {"id": identity, "pdf": pdf, "pdf_sha256": sha(ROOT/pdf),
            "text": txt, "text_sha256": sha(ROOT/txt), "cover": text.split("\f")[0],
            "spans": spans, "scope": scope, "current_authority_claim": False}

assert not (OUT/"cases.json").exists(), "Keep prior case bytes; revise explicitly instead of rerunning."
authorities = [
    source_record("aasb17", "docs/design/research/standards/aasb17.pdf",
                  "docs/design/research/standards/aasb17.txt", [
        ("separation", r"^10\s+An insurance", r"^14\s"),
        ("acquisition", r"^28A\s", r"^29\s"),
        ("initial_measurement", r"^32\s", r"^39\s"),
        ("vfa_losses", r"^45\s", r"^53\s"),
        ("reinsurance", r"^62\s", r"^69\s"),
        ("presentation", r"^78\s", r"^89\s"),
        ("insurance_risk", r"^B17\s", r"^B24\s"),
        ("investment_separation", r"^B31\s", r"^B33\s"),
        ("acquisition_allocation", r"^B35A\s", r"^B36\s"),
        ("market_and_nonmarket", r"^B42\s", r"^B50\s"),
        ("participation_and_loss_recovery", r"^B101\s", r"^B120\s"),
        ("revenue", r"^B120\s", r"^B126\s"),
    ], "AU for-profit calendar2024/25; historical compilation F2023C00382"),
    source_record("aasb107",
        "docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023.pdf",
        "docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023.txt",
        [("cash_classification", r"^14\s", r"^17\s")],
        "Historical calendar2024/25; principal insurance operating cash, explicitly nontrading investment")
]
write("source-support.json", {"authorities": authorities,
    "mathematics": "project derivation: solve two state payoff equations, then obtain state-price representation",
    "source_limits": "No current multi-GAAP admission, actuarial calibration or general valuation library."})
cases = [vfa_case(up, died) for up in [True, False] for died in [False, True]]
cases += [acquisition_case(True), acquisition_case(False)]
adverse = [
    {"id": "physical_pricing", "wrong": "9/2", "required": "9", "decision": "wrong_measure"},
    {"id": "guarantee_omitted", "wrong": "90", "required": "99", "decision": "wrong_financial_benefit"},
    {"id": "whole_gain_to_csm", "wrong": "28", "required": "19", "decision": "wrong_csm"},
    {"id": "vfa_loss_added_twice", "wrong": "96", "required": "93", "decision": "double_loss_component"},
    {"id": "investment_in_revenue_up", "wrong": "130", "required": "22", "decision": "investment_component_in_revenue"},
    {"id": "retain_acquisition_asset", "wrong": "10", "required": "0", "decision": "duplicate_asset"},
    {"id": "omit_acquisition_presentation", "wrong": "90", "required": "100", "decision": "wrong_gross_presentation"},
    {"id": "loss_excludes_acquisition", "wrong": "5", "required": "15", "decision": "wrong_initial_loss"},
    {"id": "late_treaty_recovery", "wrong": "15/2", "required": "0", "decision": "timing_ineligible"},
    {"id": "held_loss_added_twice", "wrong": "70", "required": "125/2", "decision": "double_loss_recovery"},
    {"id": "missing_ra", "input_patch": {"ra": None}, "decision": "measurement_unresolved"},
    {"id": "missing_vfa_admission", "input_patch": {"eligibility": None}, "decision": "admission_unresolved"},
    {"id": "missing_dependence", "input_patch": {"physical_dependence": None}, "decision": "joint_law_unresolved"},
    {"id": "service_already_supplied", "input_patch": {"service_units_supplied": "1/2"},
     "decision": "dated_allocation_required"},
    {"id": "unspanned_third_state", "input_patch": {"additional_financial_states": True},
     "decision": "valuation_model_unresolved"},
    {"id": "invalid_state_prices", "input_patch": {"S0": "130"}, "decision": "no_arbitrage_bound_failed"},
    {"id": "held_group_vfa", "input_patch": {"group_kind": "reinsurance_held", "measurement": "VFA"},
     "decision": "outside_vfa_scope"},
    {"id": "repeat_acquisition_transfer", "input_patch": {"acquisition_asset_consumed": True,
                                                       "same_event_same_payload": True},
     "decision": "replay_no_change"}
]
write("cases.json", {
    "schema": "accdsl.documentary.insurance-priced-guarantee.v1",
    "profile": "historical conditional calendar2024/25; pretax; no OCI",
    "financial_model": {"S0": "100", "Su": "120", "Sd": "80", "R": "1", "share": "9/10", "floor": "90",
                        "q_up": "1/2", "topup_up": "0", "topup_down": "18",
                        "delta": "-9/20", "bank": "54", "guarantee_price": "9", "benefit_price": "99",
                        "trading": "frictionless, unrestricted borrowing/shorting; no dividends or counterparty loss"},
    "physical_model": {"p_up": "3/4", "p_death": "1/10", "dependence": "independent, supplied",
                       "expected_guarantee": "9/2", "expected_profit": "29/2"},
    "nonfinancial_measurement": {"mortality_benefit": "20", "mortality_mean": "2", "vfa_ra": "1",
                                "issued_acquisition_ra": "5", "held_ra": "5/2",
                                "status": "supplied conditional compensation, not calibrated"},
    "admission": {"vfa": "supplied conditional finding under B101–108",
                  "insurance_risk": "supplied significant-risk finding; death adds20 and up/death cash128 exceeds premium110",
                  "non_distinct": "mutual termination under B32(b); no separately exercisable rights",
                  "no_embedded_derivative_separation": "supplied assessment under11(a)",
                  "risk_mitigation_election": False,
                  "event_order": "financial observation before any supplied coverage unit; mortality later"},
    "cases": cases, "adverse": adverse,
    "source_support_sha256": sha(OUT/"source-support.json")
})
print(json.dumps({"cases": len(cases), "events": sum(len(c["events"]) for c in cases),
                  "adverse": len(adverse), "authorities": len(authorities)}))
