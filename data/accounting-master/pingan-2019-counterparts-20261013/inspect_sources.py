"""Capture issuer candidates and compare their text with the selected mirror."""
import hashlib
import json
import time
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def compare(a, b, pairs):
    rows = []
    for i, j in pairs:
        x, y = a[i - 1].get_text(), b[j - 1].get_text()
        rows.append({"left_pdf_page": i, "right_pdf_page": j,
                     "left_text_sha256": hashlib.sha256(x.encode()).hexdigest(),
                     "right_text_sha256": hashlib.sha256(y.encode()).hexdigest(),
                     "left_characters": len(x), "right_characters": len(y),
                     "exact_text_equal": x == y,
                     "whitespace_normalized_equal": "".join(x.split()) == "".join(y.split())})
    return {"pairs": rows, "raw_equal": sum(r["exact_text_equal"] for r in rows),
            "whitespace_normalized_equal": sum(r["whitespace_normalized_equal"] for r in rows),
            "empty_equal_pairs": sum(r["exact_text_equal"] and r["left_characters"] == 0 for r in rows)}


def main():
    assert not (OUT / "captures.json").exists()
    start = time.monotonic()
    selected = json.loads((ROOT / "data/financial-report-benchmark/source-evidence.json").read_text())["documents"]["ping_an-2019-interim_h1"]
    paths = {"full": OUT / "sources/2464938e.pdf", "extract": OUT / "sources/073a50e0.pdf", "mirror": ROOT / selected["local_path"]}
    docs = {k: fitz.open(v) for k, v in paths.items()}
    sources = {k: {"pdf": str(p.relative_to(ROOT)), "sha256": sha(p), "pdf_pages": len(docs[k])} for k, p in paths.items()}
    captures = []
    selections = {"full": [1, 3, 100, 114, 180], "extract": [1, 9], "mirror": [1, 115]}
    for kind, numbers in selections.items():
        folder = OUT / "pages" / kind
        folder.mkdir(parents=True, exist_ok=True)
        for number in numbers:
            page = docs[kind][number - 1]
            text = folder / f"page-{number}.txt"
            render = folder / f"page-{number}.png"
            text.write_text(page.get_text())
            page.get_pixmap(matrix=fitz.Matrix(1.2, 1.2), alpha=False).save(render)
            captures.append({"source": kind, "pdf_page": number, "pdf_sha256": sources[kind]["sha256"],
                             "text": str(text.relative_to(ROOT)), "text_sha256": sha(text),
                             "render": str(render.relative_to(ROOT)), "render_sha256": sha(render)})
    assert len(docs["mirror"]) == len(docs["full"]) + 1
    full_comparison = compare(docs["full"], docs["mirror"], [(i, i+1) for i in range(1, len(docs["full"])+1)])
    extract_comparison = compare(docs["extract"], docs["full"], [(i, i+100) for i in range(1, len(docs["extract"])+1)])
    save("captures.json", captures)
    save("source-inventory.json", sources)
    save("text-comparisons.json", {"sources": sources, "full_vs_mirror": full_comparison,
                                   "extract_vs_full": extract_comparison, "wall_seconds": time.monotonic() - start,
                                   "scope": "Exact extracted text and whitespace-normalized comparison; not visual or historical-byte equivalence"})
    print(json.dumps({"sources": {k: v["pdf_pages"] for k, v in sources.items()}, "captures": len(captures),
                      "full_vs_mirror": {k: v for k, v in full_comparison.items() if k != "pairs"},
                      "extract_vs_full": {k: v for k, v in extract_comparison.items() if k != "pairs"}}))


if __name__ == "__main__":
    main()
