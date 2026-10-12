"""Retain lease source pages and exact operative-attachment paragraphs."""
import hashlib
import json
import re
import time
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import fitz

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
AUTH = ROOT / "docs/design/proposal/readiness/sources-20261007"
PDF = ROOT / "data/accounting-master/pingan-2019-counterparts-20261013/sources/2464938e.pdf"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main():
    assert not (OUT / "captures.json").exists()
    start = time.monotonic()
    doc = fitz.open(PDF)
    captures = []
    for number in [88, 101, 102, 108, 109, 114, 115, 166, 167]:
        page = doc[number-1]
        folder = OUT / "pages"
        folder.mkdir(exist_ok=True)
        text, render = folder / f"page-{number}.txt", folder / f"page-{number}.png"
        text.write_text(page.get_text())
        page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False).save(render)
        captures.append({"pdf_page": number, "printed_page": number-2,
                         "text": str(text.relative_to(ROOT)), "text_sha256": sha(text),
                         "render": str(render.relative_to(ROOT)), "render_sha256": sha(render)})
    with zipfile.ZipFile(AUTH / "asbe21-issued.doc") as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = ["".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in root.findall(".//w:p", ns)]
    extracted = "\n".join(paragraphs)
    prior = (AUTH / "asbe21-issued.txt").read_text()
    assert "".join(extracted.split()) == "".join(prior.split())
    starts = list(re.finditer(r"第[一二三四五六七八九十]+条", extracted))
    wanted = {"第十四条", "第十五条", "第十六条", "第十七条", "第十八条", "第三十二条",
              "第五十三条", "第五十四条", "第六十条", "第六十一条", "第六十二条", "第六十三条",
              "第六十四条", "第六十五条", "第六十六条", "第六十七条", "第六十八条"}
    # An article reference inside a paragraph is not a new article heading.
    starts = [m for m in starts if m.start() == 0 or extracted[m.start()-1] == "\n"]
    articles = []
    for i, match in enumerate(starts):
        if match[0] in wanted:
            end = starts[i+1].start() if i+1 < len(starts) else len(extracted)
            articles.append({"article": match[0], "quote": extracted[match.start():end].strip()})
    assert {r["article"] for r in articles} == wanted
    discovery = json.loads((OUT / "lease-discovery.json").read_text())
    focused = {88: "major-contract reporting qualification", 101: "ROU carrying balance", 102: "lease liability carrying balance",
               108: "finance-leasing business cash flows; not lessee payment roll-forward", 114: "ASBE basis and adoption balances",
               115: "lessee measurement and elected simplifications", 167: "lessee liability undiscounted maturity row"}
    inventory = []
    for page in discovery["pages"]:
        n = page["pdf_page"]
        role = focused.get(n, "other source context: entity/lessor business, debt or related-party disclosure; not a lessee roll-forward")
        if n == 21:
            role = "MD&A repeats June ROU/liability balances and marks comparative percentage as not applicable"
        inventory.append({**page, "role": role, "complete_page_read": n in focused,
                          "status": "inspected scoped source" if n in focused else "search context screened; full page not semantically annotated"})
    save("captures.json", captures)
    save("authority-excerpts.json", {"source": str((AUTH / "asbe21-issued.doc").relative_to(ROOT)),
         "sha256": sha(AUTH / "asbe21-issued.doc"), "extraction": "OOXML w:p/w:t; list numbering remains in original bytes",
         "saved_text_normalized_equivalence": True, "articles": articles,
         "notice_source": str((AUTH / "lease-notice-recovery.html").relative_to(ROOT)),
         "notice_sha256": sha(AUTH / "lease-notice-recovery.html"),
         "notice_text": (AUTH / "lease-notice-recovery.txt").read_text(),
         "wall_seconds": time.monotonic() - start})
    save("lease-hit-dispositions.json", {"source": str(PDF.relative_to(ROOT)), "sha256": sha(PDF),
                                       "pages": inventory, "limits": "Exact-term discovery is not full semantic annotation"})
    print(json.dumps({"captured_pages": len(captures), "authority_articles": len(articles), "hit_pages_disposed": len(inventory)}))


if __name__ == "__main__":
    main()
