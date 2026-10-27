"""Exact documentary examples, not an installed accounting runtime package."""
from collections import defaultdict
from datetime import datetime, timezone
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import subprocess
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[4]
CHECKS = []


def exact(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {k: exact(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [exact(v) for v in value]
    return value


def check(name, actual, expected=True):
    CHECKS.append({"name": name, "passed": actual == expected,
                   "actual": exact(actual), "expected": exact(expected)})


class Book:
    """Debit-positive exact ledgers for the stated proposed entries only."""

    def __init__(self, name):
        self.name = name
        self.balances = defaultdict(F)
        self.entries = []
        self.snapshots = []

    def post(self, event, date, **deltas):
        amounts = {k: F(v) for k, v in deltas.items()}
        if any(row["event"] == event for row in self.entries):
            raise ValueError("duplicate documentary event")
        if sum(amounts.values()) != 0:
            raise ValueError("unbalanced proposed entry")
        proposed = self.balances.copy()
        for account, amount in amounts.items():
            proposed[account] += amount
        if any(proposed[a] < 0 for a in ("cash", "inventory")):
            raise ValueError("insufficient cash or owned stock")
        self.balances = proposed
        self.entries.append({"event": event, "date": date,
                             "debit_positive_deltas": amounts})
        check(f"{self.name}:{event}:trial_balance", sum(self.balances.values()), 0)

    def state(self):
        b = self.balances
        revenue = -b["revenue"]
        expense = b["cogs"] + b["service_expense"]
        profit = revenue - expense
        return {"cash": b["cash"], "inventory": b["inventory"],
                "contract_liability": -b["contract_liability"],
                "supplier_payable": -b["supplier_payable"],
                "revenue": revenue, "expense": expense, "profit": profit,
                "equity": -b["opening_equity"] + profit}

    def snapshot(self, label, **expected):
        actual = self.state()
        for key, value in expected.items():
            check(f"{self.name}:{label}:{key}", actual[key], F(value))
        check(f"{self.name}:{label}:balance_sheet",
              actual["cash"] + actual["inventory"],
              actual["contract_liability"] + actual["supplier_payable"]
              + actual["equity"])
        self.snapshots.append({"label": label, **actual})
        return actual

    def serial(self):
        return {"entries": self.entries, "snapshots": self.snapshots}


def unchanged_on_rejection(book, event, date, deltas):
    before = dict(book.balances), list(book.entries)
    try:
        book.post(event, date, **deltas)
    except ValueError:
        check(f"{book.name}:{event}:rejection_no_mutation",
              before == (dict(book.balances), list(book.entries)))
    else:
        check(f"{book.name}:{event}:should_reject", False)


def modification_route(approved, enforceable, added_distinct, reflects_ssp,
                       remaining, price_known=True):
    """Bounded routing from already admitted facts; no legal inference."""
    if approved is False:
        return "existing_contract"
    if approved is None or enforceable is None:
        return "unresolved"
    if not enforceable:
        return "existing_contract"
    if not price_known:
        return "requires_variable_price_assessment"
    if added_distinct is None or reflects_ssp is None:
        return "unresolved"
    if added_distinct and reflects_ssp:
        return "separate_contract"
    return {"distinct": "prospective_remaining", "integrated": "catch_up",
            "mixed": "requires_component_allocation"}.get(remaining, "unresolved")


def warranty_route(separate_option, extra_service, can_separate=True):
    if separate_option:
        return "service_obligation"
    if separate_option is None or extra_service is None:
        return "unresolved"
    if extra_service:
        return "service_obligation" if can_separate else "combined_warranty_obligation"
    return "requires_assurance_method"


def main():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.perf_counter()
    cases = {}

    # Relative-price derivation and independent allocation conservation.
    product, service = (F(108)*100/120, F(108)*20/120)
    check("warranty:product_allocation", product, 90)
    check("warranty:service_allocation", service, 18)
    check("warranty:allocation_total", product+service, 108)
    w = Book("warranty")
    w.post("opening", "2024-07-01", inventory=60, opening_equity=-60)
    w.post("receipt", "2024-07-01", cash=108, contract_liability=-108)
    w.post("product_control", "2024-07-01", contract_liability=product,
           revenue=-product, cogs=60, inventory=-60)
    w.snapshot("delivery", cash=108, inventory=0, contract_liability=18,
               revenue=90, expense=60, profit=30, equity=90)
    w.post("half_service", "2024-12-31", contract_liability=service/2,
           revenue=-service/2)
    w.post("first_cost", "2024-12-31", service_expense=3, cash=-3)
    ws1 = w.snapshot("2024_close", cash=105, contract_liability=9,
                      revenue=99, expense=63, profit=36, equity=96)
    w.post("remaining_service", "2025-06-30", contract_liability=service-service/2,
           revenue=-(service-service/2))
    w.post("second_cost", "2025-06-30", service_expense=3, cash=-3)
    ws2 = w.snapshot("2025_close", cash=102, contract_liability=0,
                      revenue=108, expense=66, profit=42, equity=102)
    check("warranty:2024_cash_bridge", ws1["profit"]+60+ws1["contract_liability"],
          ws1["cash"])
    check("warranty:2025_cash_bridge", ws2["profit"]-ws1["profit"]-9,
          ws2["cash"]-ws1["cash"])
    check("warranty:immediate_full_revenue_exceeds_earned", F(108)-product, 18)
    unchanged_on_rejection(w, "product_control", "2024-07-01",
                           {"contract_liability":90,"revenue":-90})
    cases["service_warranty"] = w.serial()

    # Distinct-goods history, full costs and two annual statement bridges.
    d = Book("distinct")
    d.post("opening", "2024-01-01", inventory=96, opening_equity=-96)
    d.post("original_prepayment", "2024-01-02", cash=100, contract_liability=-100)
    d.post("first_four", "2024-03-31", contract_liability=40, revenue=-40,
           cogs=24, inventory=-24)
    d.snapshot("before_modification", cash=100, inventory=72,
               contract_liability=60, revenue=40, expense=24, profit=16, equity=112)
    remaining_price = F(100)-40+48
    unit_price = remaining_price/12
    check("distinct:remaining_consideration", remaining_price, 108)
    check("distinct:remaining_unit_price", unit_price, 9)
    d.post("modification_receipt", "2024-07-01", cash=48, contract_liability=-48)
    d.snapshot("amendment", cash=148, inventory=72, contract_liability=108,
               revenue=40, profit=16, equity=112)
    d.post("next_six", "2024-12-31", contract_liability=6*unit_price,
           revenue=-6*unit_price, cogs=36, inventory=-36)
    ds1 = d.snapshot("2024_close", cash=148, inventory=36, contract_liability=54,
                      revenue=94, expense=60, profit=34, equity=130)
    d.post("last_six", "2025-03-31", contract_liability=6*unit_price,
           revenue=-6*unit_price, cogs=36, inventory=-36)
    ds2 = d.snapshot("2025_close", cash=148, inventory=0, contract_liability=0,
                      revenue=148, expense=96, profit=52, equity=148)
    check("distinct:2024_cash_bridge", ds1["profit"]+96-ds1["inventory"]
          +ds1["contract_liability"], ds1["cash"])
    check("distinct:2025_cash_bridge", ds2["profit"]-ds1["profit"]
          +ds1["inventory"]-ds2["inventory"]+ds2["contract_liability"]
          -ds1["contract_liability"], ds2["cash"]-ds1["cash"])
    check("distinct:retroactive_shortcut_wrong_first_revenue", F(148,16)*4, 37)
    check("distinct:retroactive_shortcut_omits_prior_earned", 40-F(148,16)*4, 3)
    unchanged_on_rejection(d, "oversell", "2025-04-01", {"inventory":-6,"cogs":6})
    cases["remaining_distinct_goods"] = d.serial()

    # Separate-contract comparator retains independent allocation totals.
    original = {"total_units":10,"delivered_before":4,"price":F(100),
                "earned_before":F(40),"remaining_earned":F(60)}
    addition = {"total_units":6,"price":F(60),"earned":F(60)}
    check("separate:original_allocation", original["earned_before"]+original["remaining_earned"], original["price"])
    check("separate:additional_unit_price", addition["price"]/6, 10)
    check("separate:lifetime_revenue", original["price"]+addition["price"], 160)
    check("separate:lifetime_profit", original["price"]+addition["price"]-96, 64)
    cases["separate_contract_comparator"] = {"original":original,"addition":addition}

    i = Book("integrated")
    i.post("opening", "2024-01-01", cash=50, opening_equity=-50)
    i.post("original_prepayment", "2024-01-02", cash=100, contract_liability=-100)
    i.post("first_service_cost", "2024-06-30", service_expense=30, cash=-30)
    earned_before = F(100)*F(2,5)
    i.post("original_progress", "2024-06-30", contract_liability=earned_before,
           revenue=-earned_before)
    i.snapshot("before_modification", cash=120, contract_liability=60,
               revenue=40, expense=30, profit=10, equity=60)
    i.post("modification_receipt", "2024-12-31", cash=30, contract_liability=-30)
    revised = F(130)*F(3,10)
    catch_up = revised-earned_before
    check("integrated:revised_cumulative", revised, 39)
    check("integrated:catch_up", catch_up, -1)
    i.post("modification_catch_up", "2024-12-31", revenue=-catch_up,
           contract_liability=catch_up)
    ins1 = i.snapshot("2024_close", cash=150, contract_liability=91,
                       revenue=39, expense=30, profit=9, equity=59)
    i.post("remaining_service_cost", "2025-06-30", service_expense=60, cash=-60)
    i.post("completion", "2025-06-30", contract_liability=130-revised,
           revenue=-(130-revised))
    ins2 = i.snapshot("2025_close", cash=90, contract_liability=0,
                       revenue=130, expense=90, profit=40, equity=90)
    check("integrated:2024_cash_bridge", ins1["profit"]+ins1["contract_liability"],
          ins1["cash"]-50)
    check("integrated:2025_cash_bridge", ins2["profit"]-ins1["profit"]-91,
          ins2["cash"]-ins1["cash"])
    check("integrated:no_catch_up_overstates_revenue", earned_before-revised, 1)
    cases["integrated_promise"] = i.serial()

    p = Book("principal")
    p.post("owned_purchase", "2024-07-01", inventory=100, supplier_payable=-100)
    p.post("transfer_and_receipt", "2024-07-02", cash=120, revenue=-120,
           cogs=100, inventory=-100)
    ps1 = p.snapshot("received", cash=120, supplier_payable=100,
                     revenue=120, expense=100, profit=20, equity=20)
    p.post("supplier_payment", "2024-07-03", supplier_payable=100, cash=-100)
    ps2 = p.snapshot("complete", cash=20, inventory=0, supplier_payable=0,
                     revenue=120, expense=100, profit=20, equity=20)
    a = Book("agent")
    a.post("arrangement_completed_and_cash_received", "2024-07-02", cash=120,
           supplier_payable=-100, revenue=-20)
    as1 = a.snapshot("received", cash=120, supplier_payable=100,
                     revenue=20, expense=0, profit=20, equity=20)
    a.post("supplier_remittance", "2024-07-03", supplier_payable=100, cash=-100)
    as2 = a.snapshot("complete", cash=20, inventory=0, supplier_payable=0,
                     revenue=20, expense=0, profit=20, equity=20)
    for field in ["cash","supplier_payable","profit","equity"]:
        check(f"principal_agent:matched_interim_{field}", ps1[field], as1[field])
        check(f"principal_agent:matched_final_{field}", ps2[field], as2[field])
    check("principal_agent:different_revenue", ps2["revenue"]-as2["revenue"], 100)
    check("principal_agent:cash_conservation", F(120)-100, ps2["cash"])
    cases["principal"] = p.serial()
    cases["agent"] = a.serial()
    cases["agency_presentation_limit"] = "Cash ledger legs +120/-100 retained; cash-flow statement gross/net presentation not decided from revenue role."

    routes = [
        ("not_approved", (False, True, True, False, "distinct"), "existing_contract"),
        ("unknown_approval", (None, True, True, False, "distinct"), "unresolved"),
        ("unknown_enforceability", (True, None, True, False, "distinct"), "unresolved"),
        ("not_enforceable", (True, False, True, False, "distinct"), "existing_contract"),
        ("separate", (True, True, True, True, "distinct"), "separate_contract"),
        ("remaining", (True, True, True, False, "distinct"), "prospective_remaining"),
        ("integrated", (True, True, False, False, "integrated"), "catch_up"),
        ("mixed", (True, True, False, False, "mixed"), "requires_component_allocation"),
        ("unknown_price", (True, True, True, False, "distinct", False), "requires_variable_price_assessment"),
        ("unknown_ssp", (True, True, True, None, "distinct"), "unresolved"),
    ]
    for label, inputs, expected in routes:
        check("modification_route:"+label, modification_route(*inputs), expected)
    for label, inputs, expected in [
        ("purchased", (True, True), "service_obligation"),
        ("assurance", (False, False), "requires_assurance_method"),
        ("unresolved", (False, None), "unresolved"),
        ("inseparable", (False, True, False), "combined_warranty_obligation"),
    ]:
        check("warranty_route:"+label, warranty_route(*inputs), expected)
    cases["classification_scope"] = "Routes operate on stipulated admitted facts; they do not determine legal enforceability, standalone prices, progress, control or accounting validity."

    payload = {"cases": exact(cases), "scope": "exact synthetic documentary calculation",
               "tax": "uncomputed, not zero", "runtime_conformance": "not evaluated"}
    (OUT/"customer-obligation-cases.json").write_text(json.dumps(payload,indent=2)+"\n")
    result = {"passed": all(c["passed"] for c in CHECKS), "check_count":len(CHECKS),
              "checks":CHECKS,"wall_seconds":time.perf_counter()-timer}
    (OUT/"calculation-checks.json").write_text(json.dumps(result,indent=2)+"\n")
    manifest = {"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT).decode().strip(),
                "started_utc":started,"wall_seconds":result["wall_seconds"],
                "command":["python3",str(Path(__file__).relative_to(ROOT))],
                "environment":"system Python standard library; fractions.Fraction",
                "gpu":"N/A; no GPU or numerical framework imported", "random_seeds":"N/A; deterministic rational arithmetic",
                "plan":"docs/plans/accounting-customer-obligations-20261014.md",
                "result":str((OUT/"result.md").relative_to(ROOT)),
                "data_version":"Synthetic inputs in checked method and this script; source bytes in source-manifest.json",
                "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                "outputs":[str((OUT/name).relative_to(ROOT)) for name in ["customer-obligation-cases.json","calculation-checks.json"]]}
    (OUT/"calculation-run.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps({"passed":result["passed"],"checks":len(CHECKS),
                      "failures":[c for c in CHECKS if not c["passed"]]}))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
