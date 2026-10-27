"""Exact documentary PPE cases; no application runtime or live books."""
from collections import defaultdict
from dataclasses import dataclass, asdict
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


def check(name, actual, expected):
    CHECKS.append({"name": name, "passed": actual == expected,
                   "actual": actual, "expected": expected})


def encode(value):
    if isinstance(value, F):
        return str(value)
    if isinstance(value, set):
        return sorted(value)
    raise TypeError(type(value).__name__)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Asset:
    gross: F
    accumulated: F
    remaining: F
    surplus: F = F(0)
    prior_loss: F = F(0)
    active: bool = True

    @property
    def carrying(self):
        return self.gross - self.accumulated

    def depreciate(self):
        assert self.active and self.remaining > 0
        amount = self.carrying / self.remaining
        self.accumulated += amount
        self.remaining -= 1
        return amount

    def revalue(self, value):
        assert self.active and value >= 0
        delta = value - self.carrying
        if delta >= 0:
            profit = min(delta, self.prior_loss)
            oci = delta - profit
            self.prior_loss -= profit
        else:
            oci = -min(-delta, self.surplus)
            profit = delta - oci
            self.prior_loss -= profit
        self.surplus += oci
        self.gross, self.accumulated = value, F(0)
        return profit, oci

    def dispose(self):
        amount = self.carrying
        self.gross, self.accumulated, self.active = F(0), F(0), False
        return amount


PL = {"depreciation", "disposal_loss", "disposal_gain",
      "revaluation_loss", "revaluation_gain", "maintenance"}


class Book:
    def __init__(self, name):
        self.name = name
        self.balances = defaultdict(F, cash=F(200), capital=F(-200))
        self.events = []
        self.states = []

    def post(self, date, event, amounts, role="noncash"):
        lines = {k: F(v) for k, v in amounts.items()}
        check(self.name+":"+event+":balance", sum(lines.values()), F(0))
        self.events.append({"date": date, "event": event, "role": role,
                            "lines_debit_positive": lines})
        for account, amount in lines.items():
            self.balances[account] += amount

    def close(self, year):
        active = {k: -self.balances[k] for k in PL if self.balances[k]}
        active["retained_earnings"] = -sum(active.values())
        self.post(f"{year}-12-31", f"close_{year}", active, "closing")

    def snapshot(self, label, assets, expected):
        b = self.balances
        for key, asset in assets.items():
            check(f"{self.name}:{label}:{key}:gross", b["ppe_"+key], asset.gross)
            check(f"{self.name}:{label}:{key}:accumulated", -b["ad_"+key], asset.accumulated)
            check(f"{self.name}:{label}:{key}:surplus", -b["surplus_"+key], asset.surplus)
        ppe = sum(a.carrying for a in assets.values())
        profit_unclosed = -sum(b[k] for k in PL)
        retained = -b["retained_earnings"] + profit_unclosed
        surplus = -sum(v for k, v in b.items() if k.startswith("surplus_"))
        state = {"cash": b["cash"], "ppe": ppe, "liabilities": F(0),
                 "capital": -b["capital"], "retained": retained,
                 "surplus": surplus, "equity": -b["capital"]+retained+surplus}
        check(f"{self.name}:{label}:trial_balance", sum(b.values()), F(0))
        check(f"{self.name}:{label}:balance_sheet", state["cash"]+ppe, state["equity"])
        for key, value in expected.items():
            check(f"{self.name}:{label}:{key}", state[key], F(value))
        self.states.append({"label": label, "statement": state,
                            "components": {k: asdict(v) for k,v in assets.items()},
                            "signed_ledger": dict(b)})
        return state

    def annual(self, year, opening, expected):
        movement = defaultdict(F)
        cfi = cfo = F(0)
        for event in self.events:
            if not event["date"].startswith(str(year)) or event["role"] == "closing":
                continue
            for k,v in event["lines_debit_positive"].items():
                movement[k] += v
            cash = event["lines_debit_positive"].get("cash", F(0))
            if event["role"] == "investing": cfi += cash
            elif event["role"] == "operating": cfo += cash
            else: check(self.name+":"+event["event"]+":noncash", cash, F(0))
        profit = -sum(movement[k] for k in PL)
        transfer = -movement["retained_earnings"]
        surplus_change = -sum(v for k,v in movement.items() if k.startswith("surplus_"))
        oci = surplus_change + transfer
        indirect = profit + sum(movement[k] for k in PL if k != "maintenance")
        closing = self.states[-1]["statement"]
        report = {"profit": profit, "oci": oci, "transfer": transfer,
                  "depreciation": movement["depreciation"],
                  "cfo_direct": cfo, "cfo_indirect": indirect, "cfi": cfi,
                  "closing_cash": closing["cash"], "closing_ppe": closing["ppe"],
                  "closing_equity": closing["equity"], "closing_retained": closing["retained"],
                  "closing_surplus": closing["surplus"]}
        check(f"{self.name}:{year}:cash_bridge", opening["cash"]+cfo+cfi, closing["cash"])
        check(f"{self.name}:{year}:equity_bridge", opening["equity"]+profit+oci, closing["equity"])
        check(f"{self.name}:{year}:retained_bridge", opening["retained"]+profit+transfer, closing["retained"])
        check(f"{self.name}:{year}:surplus_bridge", opening["surplus"]+oci-transfer, closing["surplus"])
        for key,value in expected.items(): check(f"{self.name}:{year}:{key}", report[key], F(value))
        return report


def cost_case():
    book = Book("cost")
    assets = {"shell": Asset(F(80), F(0), F(8)), "old": Asset(F(20), F(0), F(2))}
    opening = {"cash": F(200), "equity": F(200), "retained": F(0), "surplus": F(0)}
    book.post("2024-01-01", "purchase", {"ppe_shell":80,"ppe_old":20,"cash":-100}, "investing")
    check("cost:2024:independent_depreciation", sum(a.depreciate() for a in assets.values()), F(20))
    book.post("2024-12-31", "depreciate_2024", {"depreciation":20,"ad_shell":-10,"ad_old":-10})
    book.close(2024)
    end24 = book.snapshot("end_2024", assets, {"cash":100,"ppe":80,"equity":180,"retained":-20})
    reports = {"2024":book.annual(2024,opening,{"profit":-20,"oci":0,"cfi":-100,"cfo_direct":0,"cfo_indirect":0})}
    old_amount = assets["old"].dispose()
    check("cost:replacement:old_carrying", old_amount, F(10))
    book.post("2025-01-01", "remove_old", {"ad_old":10,"disposal_loss":10,"ppe_old":-20})
    assets["new"] = Asset(F(30),F(0),F(3))
    book.post("2025-01-01", "buy_new", {"ppe_new":30,"cash":-30}, "investing")
    book.snapshot("after_replacement", assets, {"cash":70,"ppe":100,"equity":170})
    check("cost:2025:independent_depreciation", sum(a.depreciate() for a in assets.values() if a.active), F(20))
    book.post("2025-12-31", "depreciate_2025", {"depreciation":20,"ad_shell":-10,"ad_new":-10})
    book.snapshot("before_sale", assets, {"cash":70,"ppe":80,"equity":150})
    disposed = sum(a.dispose() for a in assets.values() if a.active)
    check("cost:sale:independent_gain", F(90)-disposed, F(10))
    book.post("2025-12-31", "sell", {"cash":90,"ad_shell":20,"ad_new":10,"ppe_shell":-80,"ppe_new":-30,"disposal_gain":-10}, "investing")
    book.close(2025)
    book.snapshot("end_2025", assets, {"cash":160,"ppe":0,"equity":160,"retained":-40})
    reports["2025"] = book.annual(2025,end24,{"profit":-20,"oci":0,"cfi":60,"cfo_direct":0,"cfo_indirect":0})
    check("cost:lifetime:cash_vs_equity", reports["2024"]["cfi"]+reports["2025"]["cfi"], F(160)-200)
    check("cost:all_identities_disposed", all(not a.active for a in assets.values()), True)
    return {"events":book.events,"states":book.states,"reports":reports}


def revaluation_case():
    book=Book("revaluation")
    assets={"A":Asset(F(100),F(0),F(5)),"B":Asset(F(40),F(0),F(4))}
    book.post("2023-01-01","purchase",{"ppe_A":100,"ppe_B":40,"cash":-140},"historical_opening")
    valuations = []
    def revalue(year, values, expected_routes):
        routes={key:asset.revalue(F(values[key])) for key,asset in assets.items()}
        check(f"revaluation:{year}:complete_class",set(values),set(assets))
        for key,expected in expected_routes.items():
            check(f"revaluation:{year}:{key}:profit_oci",routes[key],tuple(map(F,expected)))
        valuations.append({"date":f"{year}-12-31","class_members":["A","B"],"fair_values":values,"routes_profit_oci":routes,"reliable":"synthetic admitted assumption"})
    check("revaluation:2023:depreciation",sum(a.depreciate() for a in assets.values()),F(30))
    book.post("2023-12-31","depreciate_2023",{"depreciation":30,"ad_A":-20,"ad_B":-10})
    book.post("2023-12-31","eliminate_ad_2023",{"ad_A":20,"ppe_A":-20,"ad_B":10,"ppe_B":-10})
    revalue(2023,{"A":120,"B":24},{"A":(0,40),"B":(-6,0)})
    book.post("2023-12-31","revalue_2023",{"ppe_A":40,"surplus_A":-40,"ppe_B":-6,"revaluation_loss":6})
    book.close(2023)
    start24=book.snapshot("opening_2024",assets,{"cash":60,"ppe":144,"retained":-36,"surplus":40,"equity":204})
    check("revaluation:opening:B_prior_loss",assets["B"].prior_loss,F(6))
    check("revaluation:2024:depreciation",sum(a.depreciate() for a in assets.values()),F(38))
    book.post("2024-12-31","depreciate_2024",{"depreciation":38,"ad_A":-30,"ad_B":-8})
    book.post("2024-12-31","eliminate_ad_2024",{"ad_A":30,"ppe_A":-30,"ad_B":8,"ppe_B":-8})
    revalue(2024,{"A":45,"B":22},{"A":(-5,-40),"B":(6,0)})
    book.post("2024-12-31","revalue_2024",{"ppe_A":-45,"surplus_A":40,"revaluation_loss":5,"ppe_B":6,"revaluation_gain":-6})
    book.close(2024)
    end24=book.snapshot("end_2024",assets,{"cash":60,"ppe":67,"retained":-73,"surplus":0,"equity":127})
    reports={"2024":book.annual(2024,start24,{"profit":-37,"oci":-40,"cfo_direct":0,"cfo_indirect":0,"cfi":0})}
    check("revaluation:2024:A_prior_loss",assets["A"].prior_loss,F(5))
    check("revaluation:2024:B_prior_loss",assets["B"].prior_loss,F(0))
    check("revaluation:2025:depreciation",sum(a.depreciate() for a in assets.values()),F(26))
    book.post("2025-12-31","depreciate_2025",{"depreciation":26,"ad_A":-15,"ad_B":-11})
    book.post("2025-12-31","eliminate_ad_2025",{"ad_A":15,"ppe_A":-15,"ad_B":11,"ppe_B":-11})
    revalue(2025,{"A":50,"B":11},{"A":(5,15),"B":(0,0)})
    book.post("2025-12-31","revalue_2025",{"ppe_A":20,"revaluation_gain":-5,"surplus_A":-15})
    book.snapshot("before_sale",assets,{"cash":60,"ppe":61,"retained":-94,"surplus":15,"equity":121})
    proceeds={"A":F(50),"B":F(11)}
    check("revaluation:sale:gain",sum(proceeds[k]-v.dispose() for k,v in assets.items()),F(0))
    book.post("2025-12-31","sell",{"cash":61,"ppe_A":-50,"ppe_B":-11},"investing")
    transfer=sum(v.surplus for v in assets.values())
    check("revaluation:transfer:available",transfer,F(15))
    for asset in assets.values(): asset.surplus=F(0)
    book.post("2025-12-31","transfer_surplus",{"surplus_A":15,"retained_earnings":-15})
    book.close(2025)
    book.snapshot("end_2025",assets,{"cash":121,"ppe":0,"retained":-79,"surplus":0,"equity":121})
    reports["2025"]=book.annual(2025,end24,{"profit":-21,"oci":15,"transfer":15,"cfo_direct":0,"cfo_indirect":0,"cfi":61})
    check("revaluation:all_identities_disposed",all(not a.active for a in assets.values()),True)
    return {"events":book.events,"states":book.states,"reports":reports,"valuations":valuations,
            "2023_cash_flow_presentation":"not assessed; historical opening derivation only"}


def adverse_cases():
    rows=[]
    # These independently expose balanced wrong results; they do not exercise a runtime.
    wrong={"ppe_new":F(30),"cash":F(-30)}
    check("adverse:omit_old_removal:still_balances",sum(wrong.values()),F(0))
    check("adverse:omit_old_removal:overstatement",F(80)+30-F(100),F(10))
    rows.append({"case":"old component retained","balanced":True,"ppe_equity_overstatement":F(10),"disposition":"reject; AASB116.13/70"})
    maintenance={"ppe":F(4),"cash":F(-4)}
    check("adverse:capitalized_maintenance:balance",sum(maintenance.values()),F(0))
    check("adverse:capitalized_maintenance:profit_overstatement",F(0)-F(-4),F(4))
    rows.append({"case":"ordinary servicing capitalized","balanced":True,"profit_ppe_overstatement":F(4),"correct_entry":{"maintenance":F(4),"cash":F(-4)},"cash_class":"operating","disposition":"reject; AASB116.12 and AASB107.16 asset eligibility"})
    check("adverse:class_net:net_increase",F(120)+24-80-30,F(34))
    check("adverse:class_net:missed_profit_loss",F(0)-F(-6),F(6))
    check("adverse:class_net:understated_oci",F(40)-34,F(6))
    rows.append({"case":"all net class increase put in OCI","balanced":True,"wrong_oci":F(34),"correct_oci":F(40),"correct_profit_change":F(-6),"disposition":"reject for these for-profit assets; 39/40"})
    check("adverse:recycling:false_profit",F(-21)+15,F(-6))
    rows.append({"case":"surplus recycled through income","balanced":True,"profit_overstatement":F(15),"disposition":"reject; 41 direct equity transfer"})
    # Closed documented admission examples, not an implementation conformance claim.
    for case,disposition,anchor in [
        ("missing old carrying amount","unresolved_component_measurement","13/70; no zero default"),
        ("replacement old ID already disposed","invalid_component_state","67/70 and event identity"),
        ("missing control-transfer evidence","unresolved_disposal_date","69"),
        ("ordinary disposal gain labeled revenue","invalid_presentation","68; 68A exception excluded"),
        ("partial revaluation class","incomplete_class","36/38"),
        ("missing reliable B valuation","unresolved_valuation","31"),
        ("not-for-profit entity on this profile","unsupported_entity_regime","Aus39.1/Aus40.1–2 differ"),
        ("annual start 2026-01-01 cash-flow profile","unsupported_source_period","AASB107 retained HTML exclusive limit"),
    ]: rows.append({"case":case,"disposition":disposition,"anchor":anchor})
    check("adverse:partial_class",{"A"}=={"A","B"},False)
    check("adverse:missing_value",all(v is not None for v in [F(45),None]),False)
    check("authority:2025_cashflow_admissible","2024-01-01" <= "2025-01-01" < "2026-01-01",True)
    check("authority:2026_cashflow_rejected","2024-01-01" <= "2026-01-01" < "2026-01-01",False)
    check("authority:2023_ppe_admissible","2023-01-01" <= "2023-01-01" < "2027-01-01",True)
    return rows


def main():
    started=datetime.now(timezone.utc).isoformat(); timer=time.perf_counter()
    result={"schema":"documentary-ppe-cases.v1","numbers":"exact rational strings; journal debit positive",
            "facts":"authored synthetic; separate companies; pretax",
            "runtime_implemented":False,"cost":cost_case(),"revaluation":revaluation_case(),"adverse":adverse_cases()}
    elapsed=time.perf_counter()-timer
    (OUT/"ppe-cases.json").write_text(json.dumps(result,indent=2,default=encode)+"\n")
    report={"passed":all(c["passed"] for c in CHECKS),"check_count":len(CHECKS),"checks":CHECKS,"wall_seconds":elapsed}
    (OUT/"calculation-checks.json").write_text(json.dumps(report,indent=2,default=encode)+"\n")
    run={"git_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
         "started_utc":started,"wall_seconds":elapsed,"command":["python3",str(Path(__file__).resolve().relative_to(ROOT))],
         "environment":"system Python; fractions, standard library; no installed dependencies",
         "cpu_gpu_status":"CPU exact arithmetic; no numerical framework or GPU initialized","random_seeds":"N/A; deterministic",
         "plan":"docs/plans/accounting-ppe-operations-20261014.md","result":str((OUT/"result.md").relative_to(ROOT)),
         "data_version":"synthetic ppe-cases.v1, pinned historical standards in source-manifest.json",
         "script_sha256":sha(Path(__file__)),"outputs":{p.name:sha(p) for p in [OUT/"ppe-cases.json",OUT/"calculation-checks.json"]}}
    (OUT/"calculation-run.json").write_text(json.dumps(run,indent=2)+"\n")
    print(json.dumps({"passed":report["passed"],"checks":len(CHECKS),"failed":[c["name"] for c in CHECKS if not c["passed"]]}))
    if not report["passed"]: raise SystemExit(1)


if __name__ == "__main__": main()
