"""Retain exact SEC filing rows and a small set of report-context pages."""
import datetime
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def main():
    assert not (OUT / "baseline.json").exists()
    source_rel = "data/financial-report-benchmark/landing/jpmorgan/988914cd3a4a690176cd9e5a972fbb585c02d44bc74b33ce9d9fd76b90c4753d.json"
    path = ROOT / source_rel
    doc = json.loads(path.read_text())
    assert doc["cik"] == "0000019617" and doc["name"] == "JPMORGAN CHASE & CO"
    receipts = [r for r in json.loads((ROOT / "data/financial-report-benchmark/source-access.json").read_text())
                if r.get("local_path") == source_rel]
    assert len(receipts) == 1 and receipts[0]["status"] == "ok"
    assert receipts[0]["sha256"] == sha(path)
    recent = doc["filings"]["recent"]
    events = []
    for form, period, key in [("10-K", "2025-12-31", "jpmorgan-2025-annual"),
                              ("10-Q", "2025-09-30", "jpmorgan-2025-q3")]:
        indices = [i for i, f in enumerate(recent["form"]) if f == form and recent["reportDate"][i] == period]
        assert len(indices) == 1
        i = indices[0]
        events.append({"document_id": key, "row_index": i,
                       "row": {field: values[i] for field, values in recent.items()}})
    sources = json.loads((ROOT / "data/financial-report-benchmark/source-evidence.json").read_text())["documents"]
    selected = {e["document_id"]: sources[e["document_id"]] for e in events}
    coverage = {r["document_id"]: r for r in json.loads((ROOT / "data/financial-report-benchmark/coverage.json").read_text())["rows"]}
    for key, r in selected.items():
        assert r["sha256"] == coverage[key]["sha256"] == sha(ROOT / r["local_path"])
    controls = []
    for rel in ["docs/plans/accounting-master-checkpoint.md", "docs/plans/accounting-master-current.md",
                "docs/plans/accounting-continuation-requirements-20261007.md", "data/accounting-master/next-plan.md"]:
        dest = OUT / "before" / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / rel, dest)
        controls.append({"live": rel, "snapshot": str(dest.relative_to(ROOT)), "sha256": sha(dest)})
    save("baseline.json", {"started_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                           "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                           "source": source_rel, "source_sha256": sha(path), "receipt": receipts[0],
                           "controls": controls})
    save("selected-sources.json", selected)
    save("sec-events.json", {"cik": doc["cik"], "issuer_name": doc["name"], "source": source_rel,
                             "source_sha256": sha(path), "events": events,
                             "excluded_periods": ["2026-03-31", "2026-06-30"],
                             "older_shards": doc["filings"]["files"],
                             "scope": "Two active-panel events in the retained recent response; older shards not inspected"})
    pages = []
    for key, number in [("jpmorgan-2025-annual", 49), ("jpmorgan-2025-annual", 75),
                        ("jpmorgan-2025-q3", 1), ("jpmorgan-2025-q3", 207)]:
        r = selected[key]
        pdf = fitz.open(ROOT / r["local_path"])
        page = pdf[number - 1]
        folder = OUT / "pages" / key
        folder.mkdir(parents=True, exist_ok=True)
        text = folder / f"page-{number}.txt"
        render = folder / f"page-{number}.png"
        text.write_text(page.get_text())
        page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False).save(render)
        pages.append({"document_id": key, "pdf_page": number, "pdf_pages": len(pdf),
                      "pdf_sha256": r["sha256"], "text": str(text.relative_to(ROOT)), "text_sha256": sha(text),
                      "render": str(render.relative_to(ROOT)), "render_sha256": sha(render)})
    save("selected-pages.json", pages)
    print(json.dumps({"SEC_events": len(events), "page_renders": len(pages), "inspection": "pending"}))


if __name__ == "__main__":
    main()
