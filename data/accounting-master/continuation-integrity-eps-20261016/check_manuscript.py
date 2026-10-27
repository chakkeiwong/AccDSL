"""Preservation, build, cross-reference, page and rendered-boundary evidence."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil

import fitz
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "docs/design/proposal/manuscript-company-composition-20261016"
NEXT = ROOT / "docs/design/proposal/manuscript-ordered-eps-20261016"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=2) + "\n")


def main():
    lock = json.loads((OUT / "baseline-source-lock.json").read_text())
    checks = []

    def check(name, ok):
        checks.append(dict(name=name, passed=bool(ok)))

    for item in lock["files"]:
        relative = item["path"]
        check("baseline-bytes/" + relative, sha(BASE / relative) == item["sha256"])
        check("snapshot-bytes/" + relative, sha(OUT / "baseline-sources" / relative) == item["sha256"])
        text = (NEXT / relative).read_text()
        if relative == "accounting-product-proposal.tex":
            text = text.replace("Version 3.15 (proposal candidate)", "Version 3.14 (proposal candidate)")
        elif relative == "sections/eps-lifecycle.tex":
            text = text.replace("\\input{sections/ordered-eps-method}\n\n", "")
        elif relative == "chapters/17-portable-reference.tex":
            text = text.removesuffix("\n\\input{sections/ordered-eps-records}\n")
        check("inherited-content/" + relative, text == (BASE / relative).read_text())
    check("baseline-pdf", sha(BASE / "accounting-product-proposal.pdf") == lock["candidate_pdf_sha256"])
    tex_files = sorted(NEXT.rglob("*.tex"))
    all_text = "\n".join(p.read_text() for p in tex_files)
    labels = re.findall(r"\\label\{([^}]+)\}", all_text)
    refs = re.findall(r"\\(?:ref|pageref|eqref)\{([^}]+)\}", all_text)
    duplicate_labels = [k for k, count in Counter(labels).items() if count > 1]
    missing_refs = sorted(set(refs) - set(labels))
    check("unique-labels", not duplicate_labels)
    check("resolved-references", not missing_refs)
    log = (NEXT / "accounting-product-proposal.log").read_text()
    warning_lines = [line for line in log.splitlines() if any(term in line for term in
        ("Overfull", "undefined", "multiply defined", "Missing character", "Fatal error", "LaTeX Error"))]
    check("no-material-build-warning", not warning_lines)
    pdf = NEXT / "accounting-product-proposal.pdf"
    document = fitz.open(pdf)
    old = fitz.open(BASE / "accounting-product-proposal.pdf")
    full_texts = [page.get_text() for page in document]
    phrases = ("One comparison rule for a finite set of series", "Keep unresolved instruments in the report",
               "Ordered multi-series EPS report records")
    hits = {phrase: [i+1 for i, text in enumerate(full_texts) if phrase in text] for phrase in phrases}
    for phrase, pages in hits.items():
        check("rendered-heading/" + phrase, bool(pages))
    method_start = hits[phrases[0]][-1]
    method_end = next(i+1 for i, text in enumerate(full_texts) if i+1 >= method_start and
                      "Actual conversion, expiry and incomplete terms" in text)
    appendix_start = hits[phrases[2]][-1]
    appendix_end = next(i+1 for i, text in enumerate(full_texts) if i+1 > appendix_start and
                        text.startswith("Appendix B\n"))
    pages = sorted({1, *range(method_start-1, method_end+2), *range(appendix_start-1, appendix_end+1)})
    render = OUT / ("render-attempt-%02d" % (len(list(OUT.glob("render-attempt-*"))) + 1))
    render.mkdir(exist_ok=False)
    images = []
    for number in pages:
        file = render / ("page-%03d.png" % number)
        document[number-1].get_pixmap(matrix=fitz.Matrix(1.1, 1.1)).save(file)
        images.append(dict(page=number, path=str(file.relative_to(ROOT)), sha256=sha(file)))
    for start in range(0, len(images), 6):
        batch = images[start:start+6]
        sheet = Image.new("RGB", (3*400, 2*590), "#dddddd")
        draw = ImageDraw.Draw(sheet)
        for j, record in enumerate(batch):
            im = Image.open(ROOT / record["path"]).convert("RGB")
            im.thumbnail((390, 555))
            x, y = (j % 3)*400, (j // 3)*590
            sheet.paste(im, (x, y+25))
            draw.text((x+6, y+5), "Physical page %s" % record["page"], fill="black")
        sheet.save(render / ("contact-%02d.png" % (start//6+1)))
    # Text matching can identify inherited pages unaffected by repagination;
    # it is a navigation diagnostic, not a visual acceptance test.
    old_texts = {page.get_text() for page in old}
    same_text = sum(text in old_texts for text in full_texts)
    bounds = []
    for i, page in enumerate(document):
        bad = []
        for block in page.get_text("dict")["blocks"]:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    x0, y0, x1, y1 = span["bbox"]
                    if x0 < -1 or y0 < -1 or x1 > page.rect.width+1 or y1 > page.rect.height+1:
                        bad.append(span["text"][:100])
        if bad:
            bounds.append(dict(page=i+1, text=bad))
    check("all-page-text-bounds", not bounds)
    result = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), baseline_sources=len(lock["files"]),
        candidate_version="3.15", candidate_pdf=str(pdf.relative_to(ROOT)), pdf_sha256=sha(pdf),
        pages=len(document), checks=len(checks), failures=sum(not c["passed"] for c in checks),
        source_checks=checks, duplicate_labels=duplicate_labels, missing_references=missing_refs,
        material_build_warnings=warning_lines, text_bound_findings=bounds,
        pages_with_identical_baseline_text=same_text, heading_pages=hits, rendered_pages=pages,
        human_acceptance="pending", visual_review="pending")
    write("manuscript-checks.json", result)
    write("render-manifest.json", dict(pdf_sha256=sha(pdf), pages=images, review="pending"))
    shutil.copy2("/tmp/accdsl-ordered-eps-trusted-build.log", OUT / "build-trusted-stdout.log")
    print(json.dumps({k: result[k] for k in ("pages", "pdf_sha256", "checks", "failures", "heading_pages", "rendered_pages", "material_build_warnings")}))


if __name__ == "__main__":
    main()
