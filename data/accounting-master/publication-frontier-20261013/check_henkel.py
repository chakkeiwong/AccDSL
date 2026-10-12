"""Check the inspected date assertions and preserve the discovery limitations."""
import datetime
import hashlib
import json
import re
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "completion.json").exists()
    start = time.monotonic()
    sources = json.loads((OUT / "selected-sources.json").read_text())
    pages = json.loads((OUT / "henkel-pages.json").read_text())
    review = json.loads((OUT / "henkel-visual-review.json").read_text())
    baseline = json.loads((OUT / "baseline.json").read_text())
    checks = []

    def ck(name, passed):
        checks.append({"name": name, "passed": bool(passed)})

    ck("120 active unverified non-Munich reports", len(sources) == 120
       and not any(r["issuer_id"] in {"allianz", "unilever", "munich_re"} for r in sources.values()))
    for rel, digest in baseline["input_hashes"].items():
        ck("frozen input " + rel, sha(ROOT / rel) == digest)
    ck("all sixteen renders inspected", len(pages) == 16 and
       {(p["document_id"], p["pdf_page"], p["render_sha256"]) for p in pages} ==
       {(p["document_id"], p["pdf_page"], p["render_sha256"]) for p in review["pages"] if p["inspected"]})
    rows = []
    for page in pages:
        key = page["document_id"]
        source = sources[key]
        year = int(key.split("-")[1])
        kind = key.split("-", 2)[2]
        raw = (ROOT / page["text"]).read_text()
        normalized = " ".join(raw.split())
        match = re.search(r"(Date of publication of this [Rr]eport):?\s+"
                          r"((?:Wednesday, )?[A-Z][a-z]+ \d{1,2}, \d{4})", normalized)
        ck("PDF identity " + key, sha(ROOT / source["local_path"]) == source["sha256"] == page["pdf_sha256"])
        ck("text/render identity " + key, sha(ROOT / page["text"]) == page["text_sha256"]
           and sha(ROOT / page["render"]) == page["render_sha256"])
        ck("issuer/report context " + key, "Henkel AG & Co. KGaA" in normalized
           and str(year) in normalized and "translation" in normalized.lower())
        ck("explicit date " + key, match is not None)
        if match is None:
            continue
        label, date_text = match.groups()
        parsed = datetime.datetime.strptime(date_text.removeprefix("Wednesday, "), "%B %d, %Y").date()
        ck("transcribed date " + key, parsed.isoformat() == page["candidate_date"])
        if date_text.startswith("Wednesday"):
            ck("stated weekday " + key, parsed.weekday() == 2)
        pr = re.search(r"PR [Nn]o\.:\s*([0-9 ]+)", normalized)
        printed = page["pdf_page"] - (1 if kind == "annual" and year <= 2022 else
                                      2 if kind == "annual" else 1 if year >= 2022 else 0)
        rows.append({"document_id": key, "report_year": year, "report_class": kind,
                     "pdf": source["local_path"], "pdf_sha256": source["sha256"],
                     "source_url": source["source_url"], "pdf_page": page["pdf_page"],
                     "printed_page": printed, "source_label": label, "quote": match.group(),
                     "declared_date": parsed.isoformat(), "date_precision": "day",
                     "time_of_day": None, "timezone": None, "publication_channel": "unspecified",
                     "separate_pr_code": pr.group(1).strip() if pr else None,
                     "source_language": "English; translation credited on page; German comparison not performed",
                     "evidence_class": "issuer-declared publication statement in exact retained report",
                     "historical_unchanged_byte_availability": "not independently established",
                     "frozen_corpus_date_status": source["source_metadata"]["publication_date_status"],
                     "text_sha256": page["text_sha256"], "render_sha256": page["render_sha256"],
                     "visual_review": "author inspected"})
    ck("complete issuer series", {r["document_id"] for r in rows} ==
       {key for key in sources if key.startswith("henkel-")} and len(rows) == 16)
    latest = next(r for r in rows if r["document_id"] == "henkel-2025-interim_h1")
    ck("2025 date and printed 08 24 0 PR code retained separately",
       latest["declared_date"] == "2025-08-07" and latest["separate_pr_code"] == "08 24 0")
    save("henkel-date-evidence.json", {"primary": rows, "historical_byte_admissions": 0,
                                      "scope": "All sixteen Henkel selected reports; attributed dates only"})
    lines = ["# Henkel declared publication dates", "", "| Report | Declared date | PDF / printed page |",
             "| --- | --- | --- |"]
    lines.extend(f"| {r['document_id']} | {r['declared_date']} | {r['pdf_page']} / {r['printed_page']} |" for r in rows)
    (OUT / "henkel-date-register.md").write_text("\n".join(lines) + "\n")
    failed = [r["name"] for r in checks if not r["passed"]]
    save("henkel-checks.json", {"checks": checks, "passed": len(checks) - len(failed), "failed": failed,
                                "wall_seconds": time.monotonic() - start})
    print(json.dumps({"passed": len(checks) - len(failed), "failed": failed, "reports": len(rows)}))
    raise SystemExit(bool(failed))


if __name__ == "__main__":
    main()
