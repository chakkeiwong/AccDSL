"""Check the bounded document delta, provenance and preserved historical evidence."""
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
NEW = ROOT / "docs/design/proposal/manuscript-authority-20261008"
checks = []
inputs = {}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    inputs[str(path.relative_to(ROOT))] = sha(path)
    return json.loads(path.read_text())


def check(label, passed, details=None):
    checks.append({"check": label, "passed": bool(passed), "details": details})


def verify_hashes(label, mapping):
    bad = [name for name, expected in mapping.items()
           if not (ROOT / name).is_file() or sha(ROOT / name) != expected]
    check(label, not bad, {"count": len(mapping), "mismatches": bad})


baseline = read(OUT / "baseline.json")
OLD = ROOT / baseline["source_directory"]
verify_hashes("Version 2.3, completed E14 and old method/research evidence preserved", baseline["protected_hashes"])
sources = sorted(p for p in OLD.rglob("*") if p.suffix in {".tex", ".bib", ".lark"})
check("candidate source inventory matches baseline", {p.relative_to(OLD) for p in sources} ==
      {p.relative_to(NEW) for p in NEW.rglob("*") if p.suffix in {".tex", ".bib", ".lark"}})
changed, deltas, old_tex, new_tex = [], [], [], []
for old in sources:
    rel = old.relative_to(OLD)
    new = NEW / rel
    before, after = old.read_text(), new.read_text()
    inputs[str(new.relative_to(ROOT))] = sha(new)
    if before != after:
        changed.append(str(rel))
        deltas.extend(difflib.unified_diff(before.splitlines(True), after.splitlines(True),
                                         fromfile=str(old.relative_to(ROOT)), tofile=str(new.relative_to(ROOT))))
    if old.suffix == ".tex":
        old_tex.append(before)
        new_tex.append(after)
check("exact planned source delta", set(changed) == {
    "accounting-product-proposal.tex", "chapters/08-modules.tex", "sections/bank-methods.tex", "references.bib"}, changed)
(OUT / "manuscript-delta.diff").write_text("".join(deltas))
before, after = "\n".join(old_tex), "\n".join(new_tex)
pattern = r"\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|displaymath)\}.*?\\end\{\1\}"
displays = lambda text: [match.group() for match in re.finditer(pattern, text, re.S)]
check("all displayed mathematics preserved exactly", displays(before) == displays(after), len(displays(before)))
labels = re.findall(r"\\label\{([^}]+)\}", after)
refs = re.findall(r"\\(?:ref|eqref|pageref|autoref|cref)\{([^}]+)\}", after)
check("labels unique and literal references resolve", len(labels) == len(set(labels)) and set(refs) <= set(labels))
old_bib, new_bib = (OLD / "references.bib").read_text(), (NEW / "references.bib").read_text()
keys = lambda text: re.findall(r"@\w+\s*\{\s*([^,\s]+)", text)
check("all prior bibliography entry bytes retained", new_bib.startswith(old_bib))
check("one intended bibliography addition", set(keys(new_bib)) - set(keys(old_bib)) == {"mofasbe22"})
check("bibliography keys unique", len(keys(new_bib)) == len(set(keys(new_bib))))
cites = lambda text: {key.strip() for group in re.findall(r"\\cite\w*\*?(?:\[[^\]]*\])*\{([^}]+)\}", text) for key in group.split(",")}
check("all old citations retained and all new citations resolve", cites(before) <= cites(after) <= set(keys(new_bib)))
old_bank, new_bank = (OLD / "sections/bank-methods.tex").read_text(), (NEW / "sections/bank-methods.tex").read_text()
table = lambda text: re.search(r"\\begin\{longtable\}.*?\\end\{longtable\}", text, re.S).group()
check("complete loan balance-sheet table preserved", table(old_bank) == table(new_bank))
check("earlier deterministic recovery wording repaired", "establishes that only 60.5 will be collected" not in new_bank
      and "forecast mean, not a guaranteed or maximum recovery" in new_bank
      and "would require the corresponding earlier write-off" in new_bank)
check("one-year equal-horizon limitation stated", "twelve-month and lifetime ECL both equal 11" in new_bank)
check("source-date and applicability limits stated", "its issuance schedule, subsequent amendments and adoption facts" in new_bank)

pdf = NEW / "accounting-product-proposal.pdf"
with fitz.open(pdf) as document:
    pages = len(document)
    pdf_text = " ".join(" ".join(page.get_text().split()) for page in document)
check("candidate version and page count", "Version 2.4" in pdf_text and pages == 128)
check("ASBE source and key findings rendered", all(marker in pdf_text for marker in [
    "Article 48 limits twelve-month", "forecast mean", "twelve-month and lifetime ECL both equal 11", "No. 22:"]))
log = (NEW / "accounting-product-proposal.log").read_text()
diagnostics = [line for line in log.splitlines() if any(term in line for term in ["Warning", "Overfull", "Underfull", "! "])]
check("correct engine and clean final build log", "LuaHBTeX" in log and not diagnostics, diagnostics)
check("bibliography build clean", not re.search(r"Warning--|error message|I couldn.t open", (NEW / "accounting-product-proposal.blg").read_text()))
build = read(OUT / "build-receipt.json")
check("build receipt binds final PDF", build["exit_code"] == 0 and build["pdf_sha256"] == sha(pdf))
render = read(OUT / "render-manifest.json")
review = read(OUT / "render-review.json")
check("render binds final PDF before and after", render["pdf_sha256_before"] == render["pdf_sha256_after"] == sha(pdf))
check("author review binds complete selected render", review["render_manifest_sha256"] == sha(OUT / "render-manifest.json")
      and review["author_review_sha256"] == sha(OUT / "author-review.md")
      and review["page_numbers"] == render["page_numbers"])
for page, row in render["rendered_pages"].items():
    check("render bytes preserved: " + page, sha(ROOT / row["path"]) == row["sha256"])
check("human and independent reader acceptance remain pending", review["independent_reader"] == review["human_acceptance"] == "pending")
authority = read(OUT / "authority-checks.json")
check("source/arithmetic checks pass with current source/checker", authority["failed"] == 0
      and all(c["passed"] for c in authority["checks"])
      and authority["checker_sha256"] == sha(OUT / "check_authority.py")
      and authority["source_sha256"] == sha(OUT / "sources/asbe22-trusted.body"))
receipts = read(OUT / "acquisition-receipts.json")
check("acquisition resource bound respected", receipts["distinct_requested_urls"] <= 12)
for receipt in receipts["requests"]:
    verify_hashes("transport evidence: " + receipt["attempt"], receipt["files"])
supplement = read(OUT / "source-claim-supplement.json")
verify_hashes("research supplement baseline inputs preserved", supplement["baseline_inputs"])
check("Caiani remains blocked without technical claims", supplement["source_support"][1]["classification"] == "SOURCE_BLOCKED"
      and not supplement["source_support"][1]["technical_sections_inspected"])

entry = read(ROOT / "data/accounting-master/direct-p19-20261007/recovery-entry-v1.json")
counts = {}
for group in ["protected_hashes", "upstream_reference_hashes", "controller_hashes"]:
    verify_hashes("historical " + group + " unchanged", entry[group])
    counts[group] = len(entry[group])
continuation = read(ROOT / "data/accounting-master/continuation-20261007/baseline-manifest.json")
relocations = {r["historical_path"]: r["preserved_path"] for r in continuation["relocations"]}
verify_hashes("historical P19 bytes resolve through their preserved pointers", {
    relocations.get(name, name): expected for name, expected in continuation["p19_historical_artifact_hashes"].items()})
readiness = read(ROOT / "data/accounting-master/deliverables/P19/readiness.json")
check("frozen full-proposal assessment remains negative", readiness["ready"] is False and readiness["status"] == "not_ready")

report = {"recorded_at": datetime.now(timezone.utc).isoformat(), "checker_sha256": sha(Path(__file__)),
          "command": ["python", str(Path(__file__).relative_to(ROOT))], "inputs": inputs,
          "pdf": {"path": str(pdf.relative_to(ROOT)), "sha256": sha(pdf), "pages": pages},
          "changed_sources": changed, "display_count": len(displays(before)),
          "baseline_bibliography_keys": len(keys(old_bib)), "candidate_bibliography_keys": len(keys(new_bib)),
          "preservation_counts": counts, "checks": checks,
          "passed": sum(c["passed"] for c in checks), "failed": sum(not c["passed"] for c in checks),
          "wall_seconds": time.monotonic() - START,
          "scope": "Bounded source/artifact checks and author-render evidence; no independent acceptance or full proposal readiness."}
(OUT / "candidate-checks.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
print(json.dumps({key: report[key] for key in ["passed", "failed", "display_count", "baseline_bibliography_keys", "candidate_bibliography_keys", "preservation_counts"]}))
raise SystemExit(bool(report["failed"]))
