#!/usr/bin/env python3
"""Check the Version 2.27 manuscript delta and its retained evidence."""

from __future__ import annotations

import hashlib
import json
import difflib
import re
import time
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASELINE_TREE = Path("/tmp/accdsl-manuscript-model-paths-20261010-baseline")
CANDIDATE = ROOT / "docs/design/proposal/manuscript-jpmorgan-guarantees-20261011"
start = time.monotonic()
checks: list[dict] = []


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(label: str, ok: bool, details=None) -> None:
    row = {"check": label, "passed": bool(ok)}
    if details is not None:
        row["details"] = details
    checks.append(row)


def subsequence(before: str, after: str) -> bool:
    before_lines = before.rstrip().splitlines()
    after_lines = after.rstrip().splitlines()
    opcodes = difflib.SequenceMatcher(None, before_lines, after_lines).get_opcodes()
    return all(tag in {"equal", "insert"} for tag, *_ in opcodes)


def token_subsequence(before: str, after: str) -> bool:
    before_tokens = re.findall(r"\S+", before)
    after_tokens = re.findall(r"\S+", after)
    opcodes = difflib.SequenceMatcher(None, before_tokens, after_tokens).get_opcodes()
    return all(tag in {"equal", "insert"} for tag, *_ in opcodes)


def source_files(tree: Path) -> set[Path]:
    return {
        p.relative_to(tree)
        for p in tree.rglob("*")
        if p.is_file() and p.suffix in {".tex", ".bib", ".lark"}
    }


def read_source(tree: Path, rel: Path) -> str:
    return (tree / rel).read_text(encoding="utf-8")


def displays(text: str) -> list[str]:
    pattern = re.compile(
        r"\\\[.*?\\\]|"
        r"\\begin\{(equation\*?|align\*?|gather\*?|multline\*?|displaymath)\}.*?"
        r"\\end\{\1\}",
        re.S,
    )
    return [match.group(0) for match in pattern.finditer(text)]


base = json.loads((OUT / "baseline.json").read_text(encoding="utf-8"))
baseline_pdf = ROOT / base["baseline_pdf"]["path"]
candidate_pdf = ROOT / base["candidate_pdf"]["path"]
check("protected baseline PDF identity", sha(baseline_pdf) == base["baseline_pdf"]["sha256"])
check("protected baseline PDF has 168 pages", len(fitz.open(baseline_pdf)) == 168)
check("candidate PDF identity", sha(candidate_pdf) == base["candidate_pdf"]["sha256"])

old_files = source_files(BASELINE_TREE)
new_files = source_files(CANDIDATE)
check("candidate source inventory matches baseline", old_files == new_files)
changed: list[str] = []
all_before: list[str] = []
all_after: list[str] = []
for rel in sorted(old_files):
    before = read_source(BASELINE_TREE, rel)
    after = read_source(CANDIDATE, rel)
    if before != after:
        changed.append(rel.as_posix())
    if rel.suffix == ".tex":
        all_before.append(before)
        all_after.append(after)
    if rel.as_posix() == "accounting-product-proposal.tex":
        expected = before.replace(
            "Version 2.26 (proposal candidate) \\quad 10 October 2026",
            "Version 2.27 (proposal candidate) \\quad 11 October 2026",
        )
        check("main TeX has only the Version 2.27 title change", after == expected)
    elif rel.as_posix() == "references.bib":
        check("bibliography retains all prior bytes", before.rstrip() in after)
    elif rel.as_posix() == "chapters/10-validation.tex":
        adjusted = before.replace(
            "The retained panel contains all 192 target annual/interim reports for",
            "The retained panel contains all 192 target annual/interim report slots for",
        ).replace(
            "eight consecutive complete years per issuer.",
            "eight consecutive reporting years per issuer.",
        )
        check("original validation text retained apart from declared qualification", token_subsequence(adjusted, after))
    else:
        check("original TeX/Lark lines retained: " + rel.as_posix(), subsequence(before, after))

expected_changed = {
    "accounting-product-proposal.tex",
    "chapters/10-validation.tex",
    "chapters/15-banking.tex",
    "references.bib",
}
check("only intended source files changed", set(changed) == expected_changed, changed)
before_tex = "\n".join(all_before)
after_tex = "\n".join(all_after)
flat_tex = " ".join(after_tex.split())
check("actual TeX delta is nonempty", before_tex != after_tex)
before_displays = displays(before_tex)
after_displays = displays(after_tex)
check("all 48 displayed equations remain", len(before_displays) == len(after_displays) == 48)
check("displayed equations are byte-for-byte unchanged", before_displays == after_displays)

labels = re.findall(r"\\label\{([^{}]+)\}", after_tex)
refs = re.findall(r"\\(?:ref|eqref|pageref|autoref|cref)\{([^{}]+)\}", after_tex)
check("labels remain unique", len(labels) == len(set(labels)))
check("all literal references resolve", set(refs) <= set(labels), sorted(set(refs) - set(labels)))

old_bib = read_source(BASELINE_TREE, Path("references.bib"))
new_bib = read_source(CANDIDATE, Path("references.bib"))
key_re = re.compile(r"@\w+\s*\{\s*([^,\s]+)")
old_keys = key_re.findall(old_bib)
new_keys = key_re.findall(new_bib)
check("baseline bibliography has 67 entries", len(old_keys) == 67)
check("candidate bibliography has 71 entries", len(new_keys) == 71)
check("bibliography keys are unique", len(new_keys) == len(set(new_keys)))
check("all prior bibliography keys remain", set(old_keys) <= set(new_keys))
jpmorgan_keys = {"jpmorgan2022tenk", "jpmorgan2023tenk", "jpmorgan2024tenk", "jpmorgan2025tenk"}
check("exactly four JPMorgan bibliography keys were added", set(new_keys) - set(old_keys) == jpmorgan_keys)
citation_groups = re.findall(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])*\{([^{}]+)\}", after_tex)
cited = {key.strip() for group in citation_groups for key in group.split(",")}
check("all citations resolve", cited <= set(new_keys), sorted(cited - set(new_keys)))
check("all four JPMorgan sources are cited", jpmorgan_keys <= cited)

check("source qualification for Exhibit 21 is present", "not a complete legal-entity graph" in flat_tex)
check("source qualification for ownership and transfer is present", "does not supply ownership percentages" in flat_tex)
check("guarantee wording remains source-attributed", "fully and unconditionally guaranteed" in flat_tex)
check("guarantee amount and recognition remain open", "no outstanding principal, guarantee valuation or accounting recognition" in flat_tex)
check("panel acquisition/semantic distinction is present", "source-acquisition panel" in flat_tex and "does not mean that each selected document contains every related filing section" in flat_tex)

with fitz.open(candidate_pdf) as document:
    candidate_pages = len(document)
    candidate_text = "\n".join(page.get_text() for page in document)
check("candidate PDF has 168 pages", candidate_pages == 168)
check("candidate PDF renders the Version 2.27 title", "Version 2.27" in candidate_text)
check("candidate PDF renders the JPMorgan repair", "A reported group boundary" in candidate_text and "JPMorgan Chase Financial Company" in candidate_text)

log = (CANDIDATE / "accounting-product-proposal.log").read_text(encoding="utf-8")
bad_log = [
    line for line in log.splitlines()
    if re.search(r"^! |Overfull|Underfull|LaTeX Warning|Package .* Warning|undefined citation|undefined reference", line, re.I)
]
check("final TeX log has no fatal/warning/box diagnostics", not bad_log, bad_log[:12])
blg = (CANDIDATE / "accounting-product-proposal.blg").read_text(encoding="utf-8")
check("BibTeX log has no errors", not re.search(r"Warning--|error message|I couldn.t open", blg, re.I))

semantic_dir = ROOT / base["source_units"]["semantic"]
exhibit_dir = ROOT / base["source_units"]["exhibits"]
for label, directory, expected in [
    ("semantic source checks", semantic_dir, 108),
    ("Exhibit 21/22.2 source checks", exhibit_dir, 147),
]:
    report = json.loads((directory / "checks.json").read_text(encoding="utf-8"))
    passed = report.get("passed")
    failed = report.get("failed", 0)
    rows_ok = all(row.get("passed") is True for row in report.get("checks", []))
    check(label + " remain passing", passed == expected and failed == 0 and rows_ok, {"passed": passed, "failed": failed})

render = json.loads((OUT / "render-manifest.json").read_text(encoding="utf-8"))
check("render manifest binds candidate PDF", render.get("pdf_sha256") == sha(candidate_pdf) and render.get("pages") == 168)
for row in render["images"]:
    image = ROOT / row["path"]
    check("render image hash: page " + str(row["page"]), image.is_file() and sha(image) == row["sha256"])

report = {
    "recorded_at": "2026-10-11",
    "command": ["python3", str(Path(__file__).relative_to(ROOT))],
    "checker_sha256": sha(Path(__file__)),
    "baseline": base,
    "candidate_pdf": {"path": str(candidate_pdf.relative_to(ROOT)), "sha256": sha(candidate_pdf), "pages": candidate_pages},
    "changed_sources": changed,
    "display_count": len(after_displays),
    "bibliography": {"before": len(old_keys), "after": len(new_keys), "added": sorted(jpmorgan_keys)},
    "source_check_counts": {"semantic": 108, "exhibits": 147},
    "checks": checks,
    "passed": sum(row["passed"] for row in checks),
    "failed": sum(not row["passed"] for row in checks),
    "wall_seconds": time.monotonic() - start,
    "scope": "Version 2.27 source preservation, citation/equation integrity, source-unit and rendered-image binding; independent reader and domain acceptance remain pending.",
}
(OUT / "manuscript-checks.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps({key: report[key] for key in ["passed", "failed", "display_count", "bibliography", "wall_seconds"]}, indent=2))
if report["failed"]:
    raise SystemExit(1)
