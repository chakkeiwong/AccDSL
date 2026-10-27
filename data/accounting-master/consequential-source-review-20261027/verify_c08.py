"""Bound source identities and independently recompute C08/C24 finite amounts.

Read-only inputs; result is written once to a new file. This is not a source
theorem verifier or a rerun of any accepted financial evidence writer.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import platform
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
started = time.time()
checks = []


def check(label, actual, expected):
    checks.append({"label": label, "actual": str(actual),
                   "expected": str(expected), "passed": actual == expected})


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


locks = json.loads((OUT / "source-lock.json").read_text())
for path, digest in locks.items():
    check("locked " + path, sha(ROOT / path), digest)

candidate = ROOT / "docs/design/proposal/manuscript-debt-reading-v553-20261027"
ledger = json.loads((OUT / "current-claim-ledger.json").read_text())
check("claim population", len(ledger["rows"]), 27)
locations = []
for row in ledger["rows"]:
    for loc in row["current_locations"]:
        check(row["id"] + " " + loc["file"],
              sha(candidate / loc["file"]), loc["sha256"])
        locations.append(loc)
check("location population", len(locations), 43)

source_expected = {
    "docs/papers/Debt dynamics with fixed issuance costs Benzoni (2023).pdf":
        "42cd37f8ffeba1c88c97042412b925f2195469de6cd7de82dd1522b503d135e1",
    "docs/papers/Moral Hazard and Capital Structure Dynamics Dewatripont (2003).pdf":
        "e708e32d6ccc0b3626a3f6b38bc6b31cb4210dddcdc041bae40d75a0c4c4dff9",
    "docs/papers/The Dynamics of Investment Payout and Debt Lambrecht (2017).pdf":
        "9487a76d78397891ae57906990bfbd4fa73fb66ee5ba86e7b5af42124260210b",
}
source_manifest = []
for path, digest in source_expected.items():
    p = ROOT / path
    check("source " + path, sha(p), digest)
    source_manifest.append({"path": path, "sha256": sha(p),
                            "bytes": p.stat().st_size})
for name, digest in {
    "milgrom-segal.pdf":
        "0c31ba565c69fa6f8d10b589b12ab8c191ec9b04d2bf49e7a70faa3946f06eb1",
    "lamberton-zervos-preprint.pdf":
        "073c3f1397ae74ebb2f053306815cc64ac25676735bf608efa30e4c8b40b2c42",
    "benzoni-code.zip":
        "908cef3b26ed8e16c0b6771404002030e8355ca00dc67afcdbda80e85006f75d",
}.items():
    p = OUT / "sources" / name
    check("download " + name, sha(p), digest)
    source_manifest.append({"path": str(p.relative_to(ROOT)), "sha256": sha(p),
                            "bytes": p.stat().st_size})
for row in json.loads((OUT / "author-code-manifest.json").read_text())["files"]:
    check("author code " + row["member"], sha(ROOT / row["destination"]),
          row["sha256"])

# Allocate each estate by subtracting each senior payment from the remaining
# resources. This computes the outputs independently of the manuscript formula.
allocation = {}
for estate, expected in {100: (40, 60, 0), 20: (20, 0, 0),
                         220: (40, 80, 100)}.items():
    remaining = F(estate)
    receipts = []
    for face in (40, 80):
        payment = min(F(face), remaining)
        remaining -= payment
        receipts.append(payment)
    receipts.append(remaining)
    allocation[estate] = tuple(receipts)
    check("estate " + str(estate), tuple(receipts), expected)
    check("estate conservation " + str(estate), sum(receipts), F(estate))
discount = F(20, 21)
safe_quote = allocation[100][1] * discount
risky_quote = (allocation[20][1] + allocation[220][1]) / 2 * discount
risky_equity_pv = (allocation[20][2] + allocation[220][2]) / 2 * discount
check("safe junior proceeds", safe_quote, F(400, 7))
check("risky junior proceeds", risky_quote, F(800, 21))
check("inconsistent quote shortfall", safe_quote - risky_quote, F(400, 21))
check("risky cash requirement", F(60) - risky_quote, F(460, 21))
check("risky cash exceeds owner cash 20", F(60) - risky_quote > 20, True)
for quote in (safe_quote, risky_quote):
    subscription = F(60) - quote
    safe_value = -subscription
    risk_value = risky_equity_pv - subscription
    check("risk preference at quote " + str(quote), risk_value > safe_value, True)
check("safe commitment shareholder participation",
      -(F(60) - safe_quote) < 0, True)
check("45/25 senior refusal", F(45) < 50 and F(25) >= 20, True)
check("50/20 participation and conservation",
      F(50) >= 50 and F(20) >= 20 and F(50) + F(20) == 70, True)
check("fee 1 makes joint participation impossible", F(70) - 1 < 50 + 20, True)

result = {
    "date": "2026-10-27",
    "question": "Exact current source identities and finite C08/C24 arithmetic",
    "plan": "docs/plans/accounting-consequential-source-review-20261027.md",
    "script_sha256": sha(Path(__file__)),
    "command": "python3 data/accounting-master/consequential-source-review-20261027/verify_c08.py",
    "environment": {"python": platform.python_version(), "cpu": "stdlib only",
                    "gpu": "not imported or queried", "random_seeds": "N/A: exact rational arithmetic",
                    "git": "Unavailable: existing .git marker is unusable; no repository initialized"},
    "source_manifest": source_manifest,
    "checks": checks,
    "passed": all(x["passed"] for x in checks),
    "wall_seconds": time.time() - started,
    "limits": "File equality and exact finite arithmetic only; no theorem, edition, accounting or release acceptance",
}
with (OUT / "c08-verification.json").open("x") as f:
    json.dump(result, f, indent=2)
    f.write("\n")
print(json.dumps({"passed": result["passed"], "checks": len(checks),
                  "artifact": str((OUT / "c08-verification.json").relative_to(ROOT))}))
raise SystemExit(0 if result["passed"] else 1)
