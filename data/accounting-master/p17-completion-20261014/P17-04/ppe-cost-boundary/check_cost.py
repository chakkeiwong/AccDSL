"""Independent exact reconciliation of authored documentary cases; no runtime claim."""
from collections import defaultdict
from fractions import Fraction as F
import json
from pathlib import Path
import time

OUT = Path(__file__).resolve().parent


def main():
    started = time.perf_counter()
    case = json.loads((OUT / "cost-cases.json").read_text())
    checks = []

    def check(name, observed, expected=True):
        checks.append({"name": name, "passed": observed == expected,
                       "observed": str(observed), "expected": str(expected)})

    costs = case["costs"]
    check("unique_cost_resources", len({r["id"] for r in costs}), len(costs))
    totals = {k: sum((F(r["amount"]) for r in costs if r["destination"] == k), F(0))
              for k in ["ppe", "inventory", "expense"]}
    check("eligible_ppe_cost", totals["ppe"], F(120))
    check("normal_goods_cost", totals["inventory"], F(6))
    check("excluded_period_cost", totals["expense"], F(6))
    check("cost_population_exhaustive", sum(totals.values()), sum(F(r["amount"]) for r in costs))
    check("sample_sale_precedes_availability", case["sale"]["date"] < case["available_date"])
    check("no_inventory_write_down", totals["inventory"] <= F(case["sale"]["nrv"]))
    dep = (totals["ppe"] - F(case["depreciation"]["residual"])) / case["depreciation"]["life_months"] * case["depreciation"]["months"]
    check("six_available_months", case["depreciation"]["months"], 12 - int(case["available_date"][5:7]) + 1)
    check("idle_to_year_end", case["idle_through"], case["reporting_date"])

    balances = defaultdict(F, {"Cash": F(case["opening_cash"]), "Capital": -F(case["opening_equity"])})
    flows = defaultdict(F)
    for entry in case["journals"]:
        lines = entry["lines"]
        check("balanced:" + entry["id"], sum(F(v) for _, v in lines), F(0))
        for name, value in lines:
            balances[name] += F(value)
            if name == "Cash":
                flows[entry["cash_class"]] += F(value)
        check("trial_balance_after:" + entry["id"], sum(balances.values()), F(0))
    revenue = -balances["Revenue"]
    profit = revenue - sum(balances[k] for k in ["Cost of sales", "Period expense", "Depreciation expense"])
    measured = {
        "cash": balances["Cash"], "ppe_cost": balances["PPE"],
        "depreciation": -balances["Accumulated depreciation"],
        "ppe_net": balances["PPE"] + balances["Accumulated depreciation"],
        "inventory": balances["Inventory"], "profit": profit,
        "equity": F(case["opening_equity"]) + profit,
        "cfo": flows["operating"], "cfi": flows["investing"], "cff": flows["financing"]}
    for k, expected in case["expected"].items():
        check("statement:" + k, measured[k], F(expected))
    check("ledger_ppe_vs_resources", balances["PPE"], totals["ppe"])
    check("ledger_goods_vs_resources", balances["Cost of sales"], totals["inventory"])
    check("ledger_expense_vs_resources", balances["Period expense"], totals["expense"])
    check("ledger_depreciation_vs_time", measured["depreciation"], dep)
    check("independent_cash", measured["cash"], F(case["opening_cash"]) - sum(totals.values()) + F(case["sale"]["price"]))
    check("balance_sheet", measured["cash"] + measured["ppe_net"] + measured["inventory"], measured["equity"])
    check("indirect_cfo", profit + dep, measured["cfo"])
    check("cash_flow_reconciliation", measured["cash"] - F(case["opening_cash"]), sum(flows.values()))
    check("no_noncash_cash", flows["none"], F(0))

    # Derive the three wrong but balanced outcomes independently of their authored answers.
    for kind, expected in case["wrong_treatments"].items():
        cost, period, r, goods = totals["ppe"], totals["expense"], revenue, totals["inventory"]
        if kind == "net_samples_into_ppe":
            cost += goods - r
            r, goods = F(0), F(0)
        if kind == "capitalize_all_period_costs":
            cost += period
            period = F(0)
        d = F(0) if kind == "wait_for_productive_use" else cost / 60 * 6
        p = r - goods - period - d
        wrong = {"ppe_cost": cost, "depreciation": d, "ppe_net": cost-d,
                 "profit": p, "equity": F(case["opening_equity"])+p,
                 "cfo": r-goods-period, "cfi": -cost}
        for k, v in expected.items():
            check(kind+":"+k, wrong[k], F(v))
        check(kind+":still_balances", measured["cash"] + wrong["ppe_net"], wrong["equity"])
        check(kind+":same_total_cash_flow", wrong["cfo"]+wrong["cfi"], measured["cfo"]+measured["cfi"])
        check(kind+":fails_target_profit", wrong["profit"] != measured["profit"])
        check(kind+":fails_target_ppe", wrong["ppe_net"] != measured["ppe_net"])

    result = {"passed": all(c["passed"] for c in checks), "check_count": len(checks),
              "role": "exact documentary calculation; not accounting admission or runtime validation",
              "checks": checks, "wall_seconds": time.perf_counter()-started}
    (OUT/"calculation-checks.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: result[k] for k in ["passed", "check_count", "wall_seconds"]}))
    if not result["passed"]:
        print([c for c in checks if not c["passed"]])
        raise SystemExit(1)


if __name__ == "__main__":
    main()
