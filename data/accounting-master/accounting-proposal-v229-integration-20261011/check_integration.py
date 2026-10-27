#!/usr/bin/env python3
"""Validate the bounded Version 2.29 callable-note manuscript delta."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "docs/design/proposal/manuscript-jpmorgan-terms-20261011"
CANDIDATE = ROOT / "docs/design/proposal/manuscript-jpmorgan-balance-20261011"
SOURCE = ROOT / "data/accounting-master/jpmorgan-callable-indentures-20261011"
checks: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ck(label: str, ok: bool, details=None) -> None:
    row = {"check": label, "passed": bool(ok)}
    if details is not None:
        row["details"] = details
    checks.append(row)


def source_files(tree: Path) -> set[Path]:
    return {p.relative_to(tree) for p in tree.rglob("*") if p.is_file() and p.suffix in {".tex", ".bib", ".lark"}}


def displays(text: str) -> list[str]:
    pattern = re.compile(r"\\\[.*?\\\]|\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?\\end\{\1\}", re.S)
    return [m.group(0) for m in pattern.finditer(text)]


base_pdf = BASE / "accounting-product-proposal.pdf"
candidate_pdf = CANDIDATE / "accounting-product-proposal.pdf"
ck("protected Version 2.28 PDF identity", sha(base_pdf) == "23c4e9dd0df82a62cdfa4dcf76716f19cee7b8f47d3c50d588c66cc61791f6ab")
ck("candidate PDF exists and has 169 pages", candidate_pdf.is_file() and len(fitz.open(candidate_pdf)) == 169)
old_files, new_files = source_files(BASE), source_files(CANDIDATE)
ck("candidate source inventory matches Version 2.28", old_files == new_files)
changed = []
for rel in sorted(old_files):
    before, after = (BASE / rel).read_text(encoding="utf-8"), (CANDIDATE / rel).read_text(encoding="utf-8")
    if before != after:
        changed.append(rel.as_posix())
    if rel.as_posix() == "accounting-product-proposal.tex":
        ck("main TeX has only Version 2.29 title delta", after == before.replace("Version 2.28 (proposal candidate) \\quad 11 October 2026", "Version 2.29 (proposal candidate) \\quad 11 October 2026"))
    elif rel.as_posix() == "chapters/15-banking.tex":
        old_needle = "Loan origination can debit loans"
        insertion_marker = "The complete Form~10-Ks"
        after_cmp = after.replace("\\newpage\n", "")
        old_segment = before[before.index(insertion_marker):before.index(old_needle)]
        ck("all Version 2.28 bank prose retained", after_cmp[:after_cmp.index(insertion_marker)] == before[:before.index(insertion_marker)] and old_segment in after_cmp and after_cmp[after_cmp.index(old_needle):] == before[before.index(old_needle):])
        required = [
            "US\\$5,000,000", "31 December 2022", "31 December 2023", "31 December 2024",
            "2025 year-end balance", "10 June 2021", "2.60\\%", "10 June 2031",
            "US\\$1,000", "JPM/32", "DTC global", "reopening", "not carrying or fair value",
            "Exhibit~4.4", "333-209682", "Exhibit~4(a)(7)", "24 February 2016",
        ]
        for phrase in required:
            ck("bank balance/terms phrase: " + phrase, phrase in after)
    else:
        ck("unchanged source file: " + rel.as_posix(), before == after)
ck("only title and bank chapter changed", set(changed) == {"accounting-product-proposal.tex", "chapters/15-banking.tex"}, changed)
old_text = "\n".join((BASE / rel).read_text(encoding="utf-8") for rel in sorted(old_files) if rel.suffix == ".tex")
new_text = "\n".join((CANDIDATE / rel).read_text(encoding="utf-8") for rel in sorted(new_files) if rel.suffix == ".tex")
ck("48 displayed equations retained", len(displays(old_text)) == len(displays(new_text)) == 48)
ck("displayed equations unchanged", displays(old_text) == displays(new_text))
labels = re.findall(r"\\label\{([^{}]+)\}", new_text)
refs = re.findall(r"\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}", new_text)
ck("labels remain unique", len(labels) == len(set(labels)))
ck("literal references resolve", set(refs) <= set(labels), sorted(set(refs) - set(labels)))
bib = (CANDIDATE / "references.bib").read_text(encoding="utf-8")
ck("bibliography unchanged", bib == (BASE / "references.bib").read_text(encoding="utf-8"))
keys = set(re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib))
cited = {k.strip() for group in re.findall(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}", new_text) for k in group.split(",")}
ck("all citations resolve", cited <= keys, sorted(cited - keys))
ck("four JPMorgan citations retained", {"jpmorgan2022tenk", "jpmorgan2023tenk", "jpmorgan2024tenk", "jpmorgan2025tenk"} <= cited)
with fitz.open(candidate_pdf) as doc:
    pdf_text = " ".join(page.get_text() for page in doc)
pdf_text = re.sub(r"\s+", " ", pdf_text)
for phrase in ["5,000,000", "2025 year-end balance", "2.60%", "JPM/32", "333-209682", "not carrying or fair value"]:
    ck("candidate PDF renders: " + phrase, phrase in pdf_text)
log = (CANDIDATE / "accounting-product-proposal.log").read_text(encoding="utf-8")
bad = [line for line in log.splitlines() if re.search(r"^! |Overfull|Underfull|LaTeX Warning|Package .* Warning|undefined citation|undefined reference", line, re.I) and "Package: infwarerr" not in line]
ck("final TeX log has no fatal/warning/box diagnostics", not bad, bad[:12])
blg = (CANDIDATE / "accounting-product-proposal.blg").read_text(encoding="utf-8")
ck("BibTeX log has no errors", not re.search(r"Warning--|error message|I couldn.t open", blg, re.I))
ledger = json.loads((SOURCE / "source-ledger.json").read_text(encoding="utf-8"))
ck("callable source ledger passes 70/0", ledger.get("passed") == 70 and ledger.get("failed") == 0)
ck("four dated balance rows retained", [(r["filing_year"], r["reported_balance_as_of"]) for r in ledger["rows"]] == [(2022, "2022-12-31"), (2023, "2023-12-31"), (2024, "2024-12-31"), (2025, "2024-12-31")])
ck("S-3 metadata event bound", ledger.get("official_s3_event", {}).get("accessionNumber") == "0000950103-16-011338" and ledger["official_s3_event"].get("fileNumber") == "333-209682")
ck("underlying indenture access limitation recorded", "HTTP 403" in ledger.get("official_s3_route_status", "") and not (SOURCE / "sources/2016-indentures-ex4a7.htm").exists())
report = {
    "recorded_at": "2026-10-11", "unit": "Version 2.29 callable-note manuscript integration",
    "baseline_pdf": {"path": str(base_pdf.relative_to(ROOT)), "sha256": sha(base_pdf), "pages": len(fitz.open(base_pdf))},
    "candidate_pdf": {"path": str(candidate_pdf.relative_to(ROOT)), "sha256": sha(candidate_pdf), "pages": len(fitz.open(candidate_pdf))},
    "plan": "docs/plans/accounting-jpmorgan-callable-manuscript-integration-20261011.md",
    "source_plan": "docs/plans/accounting-jpmorgan-callable-balance-indentures-20261011.md",
    "source_ledger": str((SOURCE / "source-ledger.json").relative_to(ROOT)), "render_manifest": str((OUT / "render-manifest.json").relative_to(ROOT)),
    "changed_sources": changed, "checks": checks,
    "passed": sum(x["passed"] for x in checks), "failed": sum(not x["passed"] for x in checks),
    "readiness": "not_ready", "independent_reader": "pending", "domain_acceptance": "pending", "legal_acceptance": "pending",
}
(OUT / "manuscript-checks.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({k: report[k] for k in ("passed", "failed", "changed_sources", "candidate_pdf")}))
if report["failed"]:
    raise SystemExit(1)
