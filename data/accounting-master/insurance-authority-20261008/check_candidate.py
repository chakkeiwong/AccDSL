"""Verify the bounded document delta and preservation without rewriting prior runs."""
from datetime import datetime, timezone
import difflib
import hashlib
import json
from pathlib import Path
import re
import time

import fitz

START = time.monotonic()
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
checks = []
inputs = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_text())


def check(name, passed, details=None):
    checks.append({"check": name, "passed": bool(passed), "details": details})


def verify(name, hashes):
    bad = [n for n, h in hashes.items() if not (ROOT / n).is_file() or sha(ROOT / n) != h]
    check(name, not bad, {"count": len(hashes), "mismatches": bad})


baseline = read(OUT / "baseline.json")
OLD = ROOT / baseline["source_directory"]
NEW = ROOT / baseline["candidate_directory"]
verify("Version 2.4, prior source unit and original insurance sources preserved", baseline["protected_hashes"])
relocations = {r["historical_path"]: r["preserved_path"] for r in baseline["pointer_relocations"]}
verify("prior current-pointer bytes preserved", {r["preserved_path"]: r["sha256"] for r in baseline["pointer_relocations"]})
previous = read(ROOT / "data/accounting-master/authority-literature-20261008/run-manifest.json")
verify("previous unit manifest resolves with saved pointers", {relocations.get(n, n): h for n, h in previous["artifact_hashes"].items()})

suffixes = {".tex", ".bib", ".lark"}
old_files = {p.relative_to(OLD) for p in OLD.rglob("*") if p.suffix in suffixes}
new_files = {p.relative_to(NEW) for p in NEW.rglob("*") if p.suffix in suffixes}
check("candidate source inventory unchanged", old_files == new_files)
changed, diff, before_tex, after_tex = [], [], [], []
for rel in sorted(old_files):
    before, after = (OLD / rel).read_text(), (NEW / rel).read_text()
    inputs[str((NEW / rel).relative_to(ROOT))] = sha(NEW / rel)
    if before != after:
        changed.append(str(rel))
        diff.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                         fromfile=str((OLD / rel).relative_to(ROOT)), tofile=str((NEW / rel).relative_to(ROOT))))
    if rel.suffix == ".tex":
        before_tex.append(before)
        after_tex.append(after)
(OUT / "manuscript-delta.diff").write_text("".join(diff))
check("only planned files changed", set(changed) == {"accounting-product-proposal.tex", "chapters/08-modules.tex", "sections/insurance-methods.tex", "references.bib"}, changed)
old_tex, new_tex = "\n".join(before_tex), "\n".join(after_tex)
pattern = r"\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{\1\}"
displays = lambda t: [m.group() for m in re.finditer(pattern, t, re.S)]
check("all prior displays retained exactly", displays(old_tex) == displays(new_tex), len(displays(old_tex)))
old_ins = (OLD / "sections/insurance-methods.tex").read_text()
new_ins = (NEW / "sections/insurance-methods.tex").read_text()
left, right = new_ins.split("A one-year policy can leave claims unpaid", 1)
addition, right = right.split("Reinsurance has its own group", 1)
restored = (left + "Reinsurance has its own group" + right).replace("under AASB~17 paragraphs 60--70A.", "under 60--70A.").replace("under AASB~17 Appendix C,", "under Appendix C,")
check("earlier insurance source is intact except explicit AASB attributions", restored == old_ins)
check("addition includes dates, inputs and remaining applicability limits", all(s in addition for s in ["two years later", "not a certain", "10\\%", "risk adjustment of 5", "original issuance", "1 July 2026"]))

keys = lambda t: re.findall(r"@\w+\s*\{\s*([^,\s]+)", t)
old_bib, new_bib = (OLD / "references.bib").read_text(), (NEW / "references.bib").read_text()
check("all previous bibliography bytes preserved", new_bib.startswith(old_bib))
check("one bibliography addition with unique keys", set(keys(new_bib)) - set(keys(old_bib)) == {"mofasbe25"} and len(keys(new_bib)) == len(set(keys(new_bib))))
cites = lambda t: {k.strip() for g in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}", t) for k in g.split(",")}
check("old citations retained and all citations resolve", cites(old_tex) <= cites(new_tex) <= set(keys(new_bib)))
labels = re.findall(r"\\label\{([^}]+)\}", new_tex)
refs = re.findall(r"\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}", new_tex)
check("labels unique and literal references resolve", len(labels) == len(set(labels)) and set(refs) <= set(labels))

pdf = NEW / "accounting-product-proposal.pdf"
with fitz.open(pdf) as doc:
    pages = len(doc)
    text = " ".join(" ".join(p.get_text().split()) for p in doc)
check("candidate version and expected page count", "Version 2.5" in text and pages == 129)
check("substantive addition is rendered", all(s in text for s in ["A one-year policy", "liability is 50 + 5 = 55", "overstate the required liability by 10.5", "before 1 July 2026", "No. 25: Insurance Contracts"]))
log = (NEW / "accounting-product-proposal.log").read_text()
warnings = [line for line in log.splitlines() if any(s in line for s in ["Warning", "Overfull", "Underfull", "! "])]
check("LuaLaTeX final log clean", "LuaHBTeX" in log and not warnings, warnings)
check("bibliography log clean", not re.search(r"Warning--|error message|I couldn.t open", (NEW / "accounting-product-proposal.blg").read_text()))
build = read(OUT / "build-receipt.json")
check("build binds final PDF", build["exit_code"] == 0 and build["pdf_sha256"] == sha(pdf))
render = read(OUT / "render-manifest.json")
review = read(OUT / "render-review.json")
check("render binds final PDF before and after", render["pdf_sha256_before"] == render["pdf_sha256_after"] == sha(pdf))
check("author review binds actual inspected pages", review["render_manifest_sha256"] == sha(OUT / "render-manifest.json") and review["author_review_sha256"] == sha(OUT / "author-review.md") and review["page_numbers"] == render["page_numbers"])
verify("rendered bytes preserved", {r["path"]: r["sha256"] for r in render["rendered_pages"].values()})
check("independent and human acceptance still pending", review["independent_reader"] == review["human_acceptance"] == "pending")
authority = read(OUT / "authority-checks.json")
check("authority checker and source evidence current", authority["failed"] == 0 and all(r["passed"] for r in authority["checks"]) and authority["checker_sha256"] == sha(OUT / "check_authority.py") and authority["source_sha256"] == sha(OUT / "sources/asbe25-http.body"))
verify("authority inputs preserved", authority["inputs"])
acquisition = read(OUT / "acquisition-receipts.json")
check("retrieval bounded by distinct URLs and attempts", acquisition["distinct_requested_urls"] == 8 and acquisition["attempts"] == 9)
for row in acquisition["requests"]:
    verify("transport evidence: " + row["attempt"], row["files"])

entry = read(ROOT / "data/accounting-master/direct-p19-20261007/recovery-entry-v1.json")
counts = {}
for key in ["protected_hashes", "upstream_reference_hashes", "controller_hashes"]:
    verify("historical " + key, entry[key])
    counts[key] = len(entry[key])
continuation = read(ROOT / "data/accounting-master/continuation-20261007/baseline-manifest.json")
old_relocations = {r["historical_path"]: r["preserved_path"] for r in continuation["relocations"]}
verify("P19 historical hashes resolve through preserved pointer copies", {old_relocations.get(n, n): h for n, h in continuation["p19_historical_artifact_hashes"].items()})
readiness = read(ROOT / "data/accounting-master/deliverables/P19/readiness.json")
check("whole proposal remains negative with the same five wider blockers", readiness["status"] == "not_ready" and readiness["ready"] is False and set(readiness["remaining_blockers"]) == {"P15-" + e for e in ["E01", "E05", "E07", "E08", "E14"]})

report = {"recorded_at": datetime.now(timezone.utc).isoformat(), "checker_sha256": sha(Path(__file__)),
          "inputs": inputs, "pdf": {"path": str(pdf.relative_to(ROOT)), "sha256": sha(pdf), "pages": pages},
          "changed_sources": changed, "display_count": len(displays(old_tex)), "baseline_bibliography_keys": len(keys(old_bib)),
          "candidate_bibliography_keys": len(keys(new_bib)), "preservation_counts": counts,
          "checks": checks, "passed": sum(c["passed"] for c in checks), "failed": sum(not c["passed"] for c in checks),
          "wall_seconds": time.monotonic() - START,
          "scope": "Bounded source/candidate/preservation evidence; not full-domain or human acceptance"}
(OUT / "candidate-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ["passed", "failed", "display_count", "baseline_bibliography_keys", "candidate_bibliography_keys", "preservation_counts"]}))
if report["failed"]:
    print(json.dumps([c for c in checks if not c["passed"]], ensure_ascii=False))
raise SystemExit(bool(report["failed"]))
