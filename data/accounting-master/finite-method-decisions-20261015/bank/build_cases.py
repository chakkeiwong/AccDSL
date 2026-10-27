"""Finite bank specification cases; no production execution or calibration."""
from pathlib import Path
from fractions import Fraction as F
import hashlib, json, re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def event(name,journal,attrs=None,cash=None):
    return {"id":name,"journal":{k:str(F(v)) for k,v in journal.items()},
            "attributes_after":attrs or {},"cash_class":cash}
def amounts(**kw):return {k:str(F(v)) for k,v in kw.items()}

def modified(cured):
    events=[
        event("modify_continuing_rights",{"gross_loan":-10,"modification_expense":10},
              {"contractual_claim":"110","original_risk_ref":"origination-2023","rights":"continue"}),
        event("measure_modified_ecl",{"allowance":35,"impairment_expense":-35},
              {"expected_receipt":"88","sicr":True,"credit_impaired":True}),
        event("dated_credit_assessment",{"allowance":10,"impairment_expense":-10},
              {"expected_receipt":"99","sicr":True,"credit_impaired":not cured,
               "objective_improvement":cured,"original_risk_ref":"origination-2023"}),
    ]
    if cured:
        events += [
            event("subsequent_gross_interest",{"gross_loan":10,"interest_income":-10}),
            event("subsequent_allowance_roll",{"allowance":-1,"impairment_expense":1})
        ]
    else:
        events += [event("subsequent_net_interest",{"gross_loan":10,"interest_income":-9,"allowance":-1})]
    events += [event("full_settlement_and_allowance_release",
                     {"cash":110,"gross_loan":-110,"allowance":11,"impairment_expense":-11},
                     {"contractual_claim":"0","rights":"expired_by_full_payment"},"operating")]
    return {
        "id":"modified_"+("cured" if cured else "still_impaired"),"kind":"modified","cured":cured,
        "opening":amounts(cash=100,gross_loan=110,allowance=-55,deposits=-180,opening_equity=25),
        "rate":{"period":"one year","rate":"1/10"},
        "law_after_modification":[{"weight":"4/5","payment":"110"},{"weight":"1/5","payment":"0"}],
        "law_after_credit_review":[{"weight":"9/10","payment":"110"},{"weight":"1/10","payment":"0"}],
        "events":events,
        "expected":amounts(cash=210,gross=0,allowance=0,liabilities=180,equity=30,profit=55,
                           interest=10 if cured else 9,operating_cash=110,financing_cash=0,
                           contractual_claim=0,oci=0)
    }

settled={
    "id":"full_legal_release","kind":"release",
    "opening":amounts(cash=100,gross_loan=100,allowance=-20,deposits=-180,opening_equity=0),
    "events":[event("settle_and_release",{"cash":85,"allowance":20,"gross_loan":-100,"derecognition_gain":-5},
                    {"contractual_claim":"0","release_evidence":"synthetic-enforceable-full-release","rights":"expired"},"operating")],
    "expected":amounts(cash=185,gross=0,allowance=0,liabilities=180,equity=5,profit=5,interest=0,
                       operating_cash=85,financing_cash=0,contractual_claim=0,oci=0)
}
collateral={
    "id":"delayed_collateral","kind":"collateral",
    "opening":amounts(cash=200,deposits=-180,opening_equity=-20),
    "rate":{"period":"contractual half-year","rate":"1/10","annual_effective":"21/100"},
    "schedule":["2024-01-01","2024-07-01","2025-01-01","2025-07-01"],
    "law":[{"weight":"3/5","payments":[{"period":2,"receipt":"121"}]},
           {"weight":"2/5","payments":[{"period":3,"gross_agent_proceeds":"3993/50",
                                       "agent_costs":"1331/100","receipt":"1331/20"}]}],
    "events":[
        event("advance",{"gross_loan":100,"cash":-100},{"contractual_claim":"121"},"operating"),
        event("initial_ecl",{"impairment_expense":20,"allowance":-20}),
        event("first_half_year_gross_interest",{"gross_loan":10,"interest_income":-10}),
        event("pre_observation_allowance",{"allowance":-2,"impairment_expense":2}),
        event("observed_default",{"allowance":-33,"impairment_expense":33},
              {"credit_impaired":True,"expected_receipt":"1331/20","receipt_period":3}),
        event("maturity_net_interest",{"gross_loan":11,"interest_income":F(-11,2),"allowance":F(-11,2)}),
        event("post_maturity_net_interest",{"allowance":F(121,20),"interest_income":F(-121,20)},
              {"contractual_claim":"121","post_maturity_contractual_interest":"0"}),
        event("agent_remits_net_receipt",{"cash":F(1331,20),"gross_loan":F(-1331,20)},
              {"contractual_claim":"1089/20"},"operating"),
        event("supported_accounting_writeoff",{"allowance":F(1089,20),"gross_loan":F(-1089,20)},
              {"contractual_claim":"1089/20","rights":"not_legally_released",
               "no_reasonable_recovery_finding":True})
    ],
    "expected":amounts(cash=F(3331,20),gross=0,allowance=0,liabilities=180,equity=F(-269,20),
                       profit=F(-669,20),interest=F(431,20),operating_cash=F(-669,20),
                       financing_cash=0,contractual_claim=F(1089,20),oci=0)
}
def funding(fill):
    paid=20+fill
    return {
        "id":"funding_"+str(fill),"kind":"funding","confirmed_fill":str(fill),
        "opening":amounts(cash=20,securities=50,gross_loan=80,allowance=-10,deposits=-120,opening_equity=-20),
        "facility":{"limit":"10","eligible_lot":"security-A","eligible_market_value":"10","haircut":"1/5",
                    "other_securities_ineligible":"40","existing_draw":"0","requested":"8",
                    "receipt_evidence":"confirmed_settlement" if fill else "independently_confirmed_no_receipt_by_deadline",
                    "request_status":"filled" if fill==8 else "partially_filled" if fill else "pending"},
        "events":[
            event("request_funding",{},{"capacity":"8","requested":"8","unpaid_due":"30"}),
            event("confirm_receipt",{"cash":fill,"funding_liability":-fill},
                  {"confirmed_funding":str(fill),"remaining_capacity":str(8-fill),
                   "pledged_lot":"security-A" if fill else None},"financing"),
            event("partial_withdrawal",{"deposits":paid,"cash":-paid},
                  {"unpaid_due":str(30-paid),"status":"liquidity_default_at_deadline"},"operating")
        ],
        "expected":amounts(cash=0,gross=80,allowance=10,liabilities=100,equity=20,profit=0,interest=0,
                           operating_cash=-paid,financing_cash=fill,unpaid_due=30-paid,oci=0)
    }

assert not (OUT/"cases.json").exists(),"Preserve generated evidence; do not rerun this builder."
authorities=[]
for identity,pdf,txt,ranges in [
    ("aasb9","docs/design/research/p08-v1/aasb9.pdf","docs/design/research/p08-v1/aasb9.txt",[
        ("derecognition_scope",r"^3\.2\.2\s",r"^3\.2\.8\s"),
        ("full_transfer_measurement",r"^3\.2\.11\s",r"^3\.2\.14\s"),
        ("interest_modification_writeoff",r"^5\.4\.1\s",r"^5\.4\.5\s"),
        ("credit_risk_and_modified_assets",r"^5\.5\.3\s",r"^5\.5\.15\s"),
        ("modified_asset_and_expected_losses",r"^B5\.5\.25\s",r"^B5\.5\.29\s"),
        ("collateral",r"^B5\.5\.55\s",r"^B5\.6\.1\s")]),
    ("aasb107",
     "docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023.pdf",
     "docs/design/proposal/methods/preparation-20261005-v1/01-accounting/sources/aasb107-compiled-jun2023.txt",
     [("cash_classification",r"^14\s",r"^18\s")])
]:
    text=(ROOT/txt).read_text();spans=[]
    for label,begin,end in ranges:
        a=re.search(begin,text,re.M);assert a,label
        b=re.search(end,text[a.end():],re.M);assert b,label
        stop=a.end()+b.start();span=text[a.start():stop]
        spans.append({"id":label,"start":a.start(),"end":stop,"text":span,
                      "sha256":hashlib.sha256(span.encode()).hexdigest(),"offset_unit":"Unicode code points"})
    authorities.append({"id":identity,"pdf":pdf,"pdf_sha256":sha(ROOT/pdf),"text":txt,
                        "text_sha256":sha(ROOT/txt),"cover":text.split("\f")[0],"spans":spans,
                        "scope":"Historical AU for-profit calendar2024/25; conditional cases",
                        "current_authority_claim":False})
(OUT/"source-support.json").write_text(json.dumps({"authorities":authorities,
    "facility_terms":"authored synthetic agreement; no actual venue, entitlement or regulatory rule"},
    indent=2)+"\n")
cases=[modified(True),modified(False),settled,collateral]+[funding(x) for x in [8,6,0]]
adverse=[
    {"id":"asset_ten_percent_shortcut","decision":"asset_rights_assessment_required"},
    {"id":"modification_cures_credit","decision":"credit_assessment_unresolved"},
    {"id":"reset_original_risk","decision":"wrong_sicr_comparator"},
    {"id":"use_net_interest_after_cure","wrong":"9","required":"10"},
    {"id":"use_gross_interest_still_impaired","wrong":"10","required":"9"},
    {"id":"omit_late_collateral","wrong":"40","required":"20"},
    {"id":"invent_post_maturity_claim","wrong":"1331/10","required":"121"},
    {"id":"writeoff_erases_legal_right","wrong":"0","required":"1089/20"},
    {"id":"post_capacity_as_cash","wrong":"28","required":"20"},
    {"id":"post_request_instead_of_partial_fill","wrong":"28","required":"26"},
    {"id":"duplicate_unpaid_liability","wrong":"102","required":"100"},
    {"id":"timeout_means_zero_receipt","decision":"observation_unresolved"},
    {"id":"recycled_collateral_lot","decision":"encumbrance_conflict"},
    {"id":"proposed_over_capacity_draw","requested":"9","capacity":"8","decision":"request_rejected"},
    {"id":"evidenced_unexpected_receipt","received":"9","capacity":"8","decision":"record_receipt_and_control_violation"},
    {"id":"new_distressed_asset_is_stage1","decision":"new_asset_poci_assessment_required"}
]
(OUT/"cases.json").write_text(json.dumps({"schema":"accdsl.documentary.bank-restructuring.v1",
    "profile":"historical synthetic pretax cases; no stochastic sampling or calibrated defaults",
    "cases":cases,"adverse":adverse,"source_support_sha256":sha(OUT/"source-support.json")},
    indent=2)+"\n")
print(json.dumps({"cases":len(cases),"events":sum(len(c["events"]) for c in cases),
                  "adverse":len(adverse),"authorities":len(authorities)}))
