"""Preserve nominated credits pages; record actual inspection separately."""
import hashlib
import json
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
SPECS = [
    (2018, "annual", 250, "2019-02-21"), (2018, "interim_h1", 42, "2018-08-16"),
    (2019, "annual", 268, "2020-03-05"), (2019, "interim_h1", 53, "2019-08-13"),
    (2020, "annual", 298, "2021-03-04"), (2020, "interim_h1", 51, "2020-08-06"),
    (2021, "annual", 326, "2022-02-23"), (2021, "interim_h1", 54, "2021-08-12"),
    (2022, "annual", 373, "2023-03-07"), (2022, "interim_h1", 67, "2022-08-15"),
    (2023, "annual", 393, "2024-03-04"), (2023, "interim_h1", 69, "2023-08-10"),
    (2024, "annual", 395, "2025-03-11"), (2024, "interim_h1", 68, "2024-08-13"),
    (2025, "annual", 489, "2026-03-11"), (2025, "interim_h1", 70, "2025-08-07"),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assert not (OUT / "henkel-pages.json").exists()
    sources = json.loads((OUT / "selected-sources.json").read_text())
    rows = []
    for year, kind, number, date in SPECS:
        key = f"henkel-{year}-{kind}"
        source = sources[key]
        pdf = ROOT / source["local_path"]
        assert sha(pdf) == source["sha256"]
        doc = fitz.open(pdf)
        page = doc[number - 1]
        folder = OUT / "pages" / key
        folder.mkdir(parents=True, exist_ok=True)
        text = folder / f"page-{number}.txt"
        image = folder / f"page-{number}.png"
        text.write_text(page.get_text())
        scale = min(1.2, 1200 / page.rect.width)
        page.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False).save(image)
        rows.append({"document_id": key, "pdf_page": number, "pdf_sha256": source["sha256"],
                     "candidate_date": date, "text": str(text.relative_to(ROOT)), "text_sha256": sha(text),
                     "render": str(image.relative_to(ROOT)), "render_sha256": sha(image),
                     "review_status": "pending visual inspection"})
    (OUT / "henkel-pages.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(json.dumps({"retained_pages": len(rows), "inspection": "pending"}))


if __name__ == "__main__":
    main()
