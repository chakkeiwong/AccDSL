"""Exact documentary company replay and EPS projection; no book writes."""
from copy import deepcopy
from datetime import date, timedelta
from fractions import Fraction as Q
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
P5 = ROOT / "data/accounting-master/company-composition-20261016"
EPS = ROOT / "data/accounting-master/continuation-integrity-eps-20261016/ordered-eps"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


base_facts = load_module("company_eps_base_facts", P5 / "authored_cases.py")
base_oracle = load_module("company_eps_base_oracle", P5 / "financial_checks.py")
eps_oracle = load_module("company_eps_selector", EPS / "reference_selector.py")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def file_ref(path, anchor):
    return dict(path=str(path.relative_to(ROOT)), sha256=hashlib.sha256(path.read_bytes()).hexdigest(), anchor=anchor)


def need(ok, code, status="rejected"):
    if not ok:
        raise ValueError((status, code))


def encode(value):
    if isinstance(value, Q):
        return str(value)
    if isinstance(value, dict):
        return {key: encode(v) for key, v in value.items()}
    if isinstance(value, list):
        return [encode(v) for v in value]
    return value


def replay_base():
    state = deepcopy(base_facts.OPENING)
    state["books"] = {owner: {k: str(Q(balances.get(k, 0))) for k in base_oracle.ACCOUNTS}
                      for owner, balances in state["books"].items()}
    state.update(sequence=0, flows=[])
    opening = deepcopy(state)
    journals = []
    interim = None
    for event in base_facts.EVENTS:
        state, journal, flows = base_oracle.derive(state, event["event"], need)
        journals.append(dict(id=event["id"], date=event["event"]["date"], journal=journal, flows=flows))
        if event["id"] == "tax-h1":
            interim = deepcopy(state)
    annual, legal = base_oracle.report(opening, state, "2025-01-01", "2026-01-01", need)
    return dict(opening=opening, closing=state, interim=interim, journals=journals,
                annual=annual, legal=legal)


def derive_company(world, premises, base):
    """Replay every base journal plus independently derived financing journals.

    The base financial oracle supplies its original event calculations. The
    extension recalculates actual annual tax from the merged legal ledger and
    consolidates the resulting complete books; expected results are not read.
    """
    need(world in ("conversion", "redemption"), "unsupported_world", "unsupported")
    instrument = premises["new_instrument"]
    proceeds, coupon, principal, rate, shares = map(Q, [instrument[k] for k in
        ("proceeds", "coupon", "principal", "period_rate", "conversion_shares")])
    debt = (coupon + principal) / (1 + rate)
    original_equity = proceeds-debt
    need(debt == principal, "different_maturity_schedule", "unsupported")
    keys = [*base_oracle.ACCOUNTS, "new_debt", "new_conversion_equity"]
    books = {owner: {key: Q(balances.get(key, 0)) for key in keys}
             for owner, balances in base["opening"]["books"].items()}
    schedule = [dict(item, order=0) for item in base["journals"]]
    issue = dict(cash=proceeds, new_debt=-debt, new_conversion_equity=-original_equity)
    interest = debt*rate
    additions = [
        dict(id="new.issue", date=instrument["issue_date"], order=1, journal={"P": issue},
             flows=[dict(entity="P", activity="financing", amount=proceeds, origin="new_instrument_proceeds")]),
        dict(id="new.accrue", date=instrument["maturity_date"], order=1,
             journal={"P": dict(finance_expense=interest, new_debt=-interest)}, flows=[]),
        dict(id="new.coupon", date=instrument["maturity_date"], order=2,
             journal={"P": dict(new_debt=coupon, cash=-coupon)},
             flows=[dict(entity="P", activity="operating", amount=-coupon, origin="interest")]),
    ]
    before_settle = debt+interest-coupon
    if world == "conversion":
        additions.append(dict(id="new.conversion", date=instrument["maturity_date"], order=3,
            journal={"P": dict(new_debt=before_settle, capital=-before_settle)}, flows=[]))
    else:
        additions.append(dict(id="new.redemption", date=instrument["maturity_date"], order=3,
            journal={"P": dict(new_debt=before_settle, cash=-before_settle)},
            flows=[dict(entity="P", activity="financing", amount=-before_settle, origin="new_principal")]))
    schedule += additions
    timeline, flows, equity_changes = [], [], Q(0)
    h1_sub_profit = None
    for event in sorted(schedule, key=lambda e: (e["date"], e["order"])):
        journal = {owner: {key: Q(event["journal"].get(owner, {}).get(key, 0)) for key in keys} for owner in books}
        event_flows = deepcopy(event["flows"])
        if event["id"] == "tax-h2":
            # Taxable income = actual parent pretax income plus the inherited
            # returns timing adjustment (-40+16), before current-period tax.
            prior = books["P"]["current_tax"]
            r = base["opening"]["returns"]
            return_timing = -Q(r["expected_units"])*Q(r["unit_refund"])+Q(r["recovery"])
            taxable = base_oracle.pretax(books["P"])+return_timing
            payment = taxable*Q(instrument["tax"]["rate"])-prior
            need(payment >= 0, "tax_refund_not_in_subset", "unsupported")
            journal["P"]["current_tax"], journal["P"]["cash"] = payment, -payment
            for flow in event_flows:
                if flow["entity"] == "P" and flow["origin"] == "income_tax":
                    flow["amount"] = -payment
        for owner in books:
            need(sum(journal[owner].values()) == 0, "unbalanced_journal")
            need(journal[owner]["cash"] == sum(Q(f["amount"]) for f in event_flows if f["entity"] == owner), "cash_origin_mismatch")
            for key in keys:
                books[owner][key] += journal[owner][key]
            need(sum(books[owner].values()) == 0, "unbalanced_legal_book")
            need(books[owner]["cash"] >= 0, "cash_shortfall")
        if event["id"] == "tax-h1":
            h1_sub_profit = base_oracle.profit(books["S"])
        if event["id"] == "new.issue":
            equity_changes += original_equity
        if event["id"] == "new.conversion":
            equity_changes += before_settle
        flows += [dict(flow, date=event["date"]) for flow in event_flows]
        timeline.append(dict(id=event["id"], date=event["date"], journal=journal,
            new_debt_after=-books["P"]["new_debt"], parent_cash=books["P"]["cash"]))
    p, s = books["P"], books["S"]
    # All inventory is sold outside the group before this annual close.
    need(p["inventory"] == s["inventory"] == 0, "unsold_inventory_requires_elimination", "unsupported")
    need(p["receivable"] == s["payable"] == 0, "internal_balance_remaining", "unsupported")
    group_profit = base_oracle.profit(p)+base_oracle.profit(s)
    nci = Q(1,5)*h1_sub_profit+Q(1,10)*(base_oracle.profit(s)-h1_sub_profit)
    assets = sum(sum(book[key] for key in base_oracle.ASSETS) for book in books.values())-p["investment"]
    liabilities = -sum(sum(book[key] for key in [*base_oracle.LIABS, "new_debt"]) for book in books.values())
    equity = assets-liabilities
    purchase = base["closing"]["ownership_purchase"]
    nci_equity = Q(20)+nci-Q(purchase["carrying_reduction"])
    need(equity == Q(642)+group_profit-Q(purchase["consideration"])+equity_changes, "group_equity_bridge")
    out = dict(group_profit=group_profit, parent_profit=group_profit-nci, nci_profit=nci,
        cash=p["cash"]+s["cash"], assets=assets, liabilities=liabilities, equity=equity,
        parent_equity=equity-nci_equity, nci_equity=nci_equity,
        current_tax=p["current_tax"]+s["current_tax"], deferred_tax=p["deferred_tax"]+s["deferred_tax"],
        pretax=base_oracle.pretax(p)+base_oracle.pretax(s), parent_legal_cash=p["cash"],
        parent_legal_profit=base_oracle.profit(p),
        parent_legal_equity=base_oracle.equity(p)-p["new_conversion_equity"])
    for activity in ("operating", "investing", "financing"):
        out[activity+"_receipts"] = Q(0)
        out[activity+"_payments"] = Q(0)
    out.update(interest_paid=Q(0), tax_paid=Q(0))
    internal = []
    for flow in flows:
        amount = Q(flow["amount"])
        if flow["origin"] == "internal":
            internal.append(amount)
            continue
        activity = "financing" if flow["origin"] == "nci_purchase" else flow["activity"]
        out[activity+("_receipts" if amount >= 0 else "_payments")] += abs(amount)
        if flow["origin"] == "interest":
            out["interest_paid"] -= amount
        if flow["origin"] == "income_tax":
            out["tax_paid"] -= amount
    need(len(internal) == 2 and sum(internal) == 0, "gross_internal_elimination")
    out["net_cash"] = sum(out[a+"_receipts"]-out[a+"_payments"] for a in ("operating", "investing", "financing"))
    need(out["cash"]-Q(600) == out["net_cash"], "cash_bridge")
    # Day-by-day independent share replay, not a copied weighted-average formula.
    start, end, issue_date, maturity = [date.fromisoformat(v) for v in (
        premises["report_start"], premises["report_end_exclusive"], instrument["issue_date"], instrument["maturity_date"])]
    actual_days, potential_days, trace = Q(0), Q(0), []
    day = start
    while day < end:
        actual = Q(premises["ordinary_opening_shares"])+(shares if world == "conversion" and day >= maturity else 0)
        potential = shares if issue_date <= day < maturity else Q(0)
        actual_days += actual
        potential_days += potential
        trace.append(dict(date=day.isoformat(), actual=str(actual), potential=str(potential)))
        day += timedelta(days=1)
    days = (end-start).days
    out.update(actual_ending_shares=Q(premises["ordinary_opening_shares"])+(shares if world == "conversion" else 0),
        basic_numerator=out["parent_profit"], basic_denominator=actual_days/days,
        potential_numerator_increment=interest*(1-Q(instrument["tax"]["rate"])),
        potential_share_increment=potential_days/days)
    out["basic_eps"] = out["basic_numerator"]/out["basic_denominator"]
    return encode(dict(world=world, financials=out, closing_books=books, timeline=timeline,
        flows=flows, daily_shares=trace, issue_debt=debt, issue_equity=original_equity,
        liability_after_coupon=before_settle, external_equity_additions=equity_changes))


def report_request(world, derived, premises, support):
    f = derived["financials"]
    context = dict(entity="P", book="P-and-S-group-USD", head=digest(derived["closing_books"]),
        view=digest(premises), population="P-controls-S-80-then-90-percent",
        period=dict(start=premises["report_start"], end_exclusive=premises["report_end_exclusive"]),
        ordinary_class=premises["ordinary_class"], share_basis=premises["share_basis"], currency="USD", currency_scale="1",
        rule_version="EU2023/1803-original-IAS33-historical")
    context_ref = eps_oracle.digest(context)
    instrument = premises["new_instrument"]
    request = dict(wire="OrderedEPS/1", operation="report", context=context, context_ref=context_ref,
        inventory=dict(status="complete", ids=[instrument["id"]], support=support),
        scope=dict(nonparticipating_rights=True, independent_additive_effects=True, fixed_effects=True, support=support),
        basic=dict(status="ready", context_ref=context_ref, support=support,
            continuing_numerator=f["parent_profit"], total_numerator=f["parent_profit"], denominator=f["basic_denominator"],
            attribution_complete=True, chronology_complete=True),
        series=[dict(id=instrument["id"], resolution="candidate", context_ref=context_ref, support=support,
            continuing_increment=f["potential_numerator_increment"], total_increment=f["potential_numerator_increment"],
            share_increment=f["potential_share_increment"], earnings_complete=True, time_weighting_complete=True,
            potential_windows=[dict(start=instrument["issue_date"], end_exclusive=instrument["maturity_date"])],
            actual_windows=[dict(start=instrument["maturity_date"], end_exclusive=premises["report_end_exclusive"])] if world == "conversion" else [],
            end_kind="converted" if world == "conversion" else "lapsed", actual_in_basic=world == "conversion")])
    return request
