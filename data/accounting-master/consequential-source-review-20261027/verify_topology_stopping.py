"""One-shot exact diagnostic of the printed Lemma 7.5 construction."""
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import platform
import time

started = time.monotonic()
root = Path(__file__).resolve().parents[3]
out = Path(__file__).with_name("topology-stopping-verification.json")
if out.exists():
    raise SystemExit("Preserve successful one-shot result; do not overwrite")
source = root / "docs/papers/All adapted topologies are equal Backhoff-Veraguas (2020).pdf"
digest = sha256(source.read_bytes()).hexdigest()
assert digest == "72040d8c94c9a2b123946789cc9dc2c438e658c997417c458b8b8d347188f5a7"
f = F(3)
h = [F(3), F(-6, 5)]
weights = [F(1, 2), F(1, 2)]
assert sum(weights) == 1
terminal = [f * value for value in h]
two_date = min(f, sum(w * value for w, value in zip(weights, terminal)))

def backward(unwanted_cost):
    # The branches become observable at date2. The source's unwanted cost
    # remains an available stopping action there.
    date2 = [min(unwanted_cost, value) for value in terminal]
    date1_continue = sum(w * value for w, value in zip(weights, date2))
    return min(f, date1_continue), date2

printed, printed_date2 = backward(F(4))
repaired, repaired_date2 = backward(F(10))
assert max(abs(f), *(abs(value) for value in h)) <= 3
assert printed == F(1, 5) and two_date == F(27, 10)
assert printed != two_date
assert max(abs(f), *(abs(value) for value in terminal)) <= 9
assert repaired == two_date
result = {
    "date": "2026-10-27",
    "status": "literal_construction_fails_repaired_construction_passes",
    "arithmetic": "exact fractions; exhaustive two-branch tree; no sampling",
    "source": {"path": str(source.relative_to(root)), "sha256": digest, "anchor": "Lemma7.5, physical45/printed1169"},
    "inputs": {"f": str(f), "h": list(map(str, h)), "weights": list(map(str, weights)), "terminal": list(map(str, terminal))},
    "printed": {"m": "3", "unwanted_cost": "4", "date2_values": list(map(str, printed_date2)), "actual_value": str(printed), "displayed_two_date_value": str(two_date), "equal": printed == two_date},
    "repaired": {"M": "9", "unwanted_cost": "10", "date2_values": list(map(str, repaired_date2)), "actual_value": str(repaired), "displayed_two_date_value": str(two_date), "equal": repaired == two_date},
    "not_concluded": ["topology theorem false", "full external proof certified", "any empirical or issuer-policy result"],
    "manifest": {
        "git_commit": "N/A: existing .git marker is unusable; no repository initialized",
        "command": "python3 data/accounting-master/consequential-source-review-20261027/verify_topology_stopping.py",
        "environment": platform.python_version(),
        "cpu_gpu": "Python standard library exact rational arithmetic; no GPU framework imported",
        "data_version": digest,
        "random_seeds": "N/A: exhaustive deterministic calculation",
        "wall_seconds": time.monotonic() - started,
        "plan": "docs/plans/accounting-consequential-source-review-20261027.md",
        "evidence_contract": str(Path(__file__).with_name("adapted-topology-review.md").relative_to(root)),
        "output": str(out.relative_to(root)),
        "script_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
    },
}
with out.open("x") as handle:
    json.dump(result, handle, indent=2)
    handle.write("\n")
print(result["status"])
print("printed value", printed, "two-date value", two_date, "repaired value", repaired)
