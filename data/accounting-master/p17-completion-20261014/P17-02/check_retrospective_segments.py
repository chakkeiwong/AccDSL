"""Source-bound retrospective disclosure comparison; no accounting engine."""

from datetime import datetime, timezone
import hashlib
import html
import json
from pathlib import Path
import re
import subprocess
import time

from bs4 import BeautifulSoup
import fitz


ROOT = Path(__file__).resolve().parents[4]
UNIT = Path(__file__).resolve().parent
SOURCE = ROOT / "data/financial-report-benchmark/documents/apple/apple-2025-annual/original.html"
TEXT = ROOT / "data/financial-report-benchmark/documents/apple/apple-2025-annual/extracted-f74097ba716245f42bb316f7e7ac00ed6d74a574381f39c3ce3ff5deff03ac52.txt"
PRIOR = ROOT / "data/accounting-master/apple-segments-20261009/source-claim-supplement.json"
STATEMENTS = ROOT / "data/accounting-master/apple-statement-network-20261013/statement-readings.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (UNIT / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def relative(path):
    return str(path.relative_to(ROOT))


def render_view(name, body, landscape=False):
    view = UNIT / "source-views" / (name + ".html")
    view.write_text(body)
    pdf = view.with_suffix(".pdf")
    story = fitz.Story(html=body, user_css=(
        "body {font-family:sans-serif; font-size:9pt;} h1 {font-size:13pt;} "
        "table {width:100%;font-size:8pt;} td,th {padding:4pt;border-bottom:0.5pt solid #aaa;}"
    ))
    writer = fitz.DocumentWriter(str(pdf))
    page = fitz.Rect(0, 0, 842, 595) if landscape else fitz.paper_rect("a4")
    more = True
    count = 0
    while more:
        count += 1
        if count > 4:
            raise RuntimeError("Source view exceeds bounded page count")
        device = writer.begin_page(page)
        more, _ = story.place(page + (30, 30, -30, -30))
        story.draw(device)
        writer.end_page()
    writer.close()
    images = []
    with fitz.open(pdf) as document:
        for i, page in enumerate(document):
            target = pdf.with_name(f"{name}-{i + 1}.png")
            page.get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(target)
            images.append({"path": relative(target), "sha256": sha(target)})
    return {"view": relative(view), "pdf": relative(pdf), "images": images,
            "kind": "Derived exact-text/column view, not an original browser screenshot"}


def main():
    started = datetime.now(timezone.utc).isoformat()
    timer = time.monotonic()
    for name in ("source-fragments", "source-views"):
        (UNIT / name).mkdir(exist_ok=True)
    checks = {}

    def check(name, condition):
        checks[name] = bool(condition)
        if not condition:
            raise AssertionError(name)

    check("retained_2025_body", sha(SOURCE) == "eb08113db1fa3b847936c68ddf7bd9c31b5d708c14794c94355fd38ac3846850")
    check("retained_2025_text", sha(TEXT) == "f74097ba716245f42bb316f7e7ac00ed6d74a574381f39c3ce3ff5deff03ac52")
    raw = SOURCE.read_text()
    soup = BeautifulSoup(raw, "html.parser")
    tables = soup.find_all("table")
    fragments = list(re.finditer(r"<table\b[^>]*>.*?</table>", raw, re.S | re.I))
    check("table_fragment_alignment", len(tables) == len(fragments) == 67)
    text = TEXT.read_text()
    bounds = {
        "adoption": (text.index("Recently Adopted Accounting Pronouncements"),
                     text.index("Revenue\nThe Company records", text.index("Recently Adopted Accounting Pronouncements"))),
        "note13": (text.index("Note 13 – Segment Information"),
                   text.index("Report of Independent Registered Public Accounting Firm", text.index("Note 13 – Segment Information"))),
    }
    spans = {}
    for name, (a, b) in bounds.items():
        quote = text[a:b]
        dest = UNIT / "source-fragments" / (name + ".txt")
        dest.write_text(quote)
        spans[name] = {"source_text": relative(TEXT), "start": a, "end": b,
                       "offset_unit": "Unicode code points", "path": relative(dest),
                       "sha256": sha(dest), "text": quote}
    check("actual_adoption_statement", "The Company adopted ASU 2023-07 using a retrospective transition method." in spans["adoption"]["text"])
    check("source_period", "for the fiscal year ended" in text.lower() and "September 27, 2025" in text[:5000])
    segments = ["Americas", "Europe", "Greater China", "Japan", "Rest of Asia Pacific", "Corporate", "Total"]
    expected_labels = ["Net sales", "Cost of sales", "Research and development",
                       "Selling and marketing", "General and administrative", "Operating income/(loss)"]
    readings = []
    views = []
    source_tables = []
    matrices = {}
    for index, year in [(48, "2025"), (49, "2024"), (50, "2023")]:
        table = tables[index]
        fragment = fragments[index]
        check(f"fragment:{year}", BeautifulSoup(fragment.group(), "html.parser").get_text(" ", strip=True) == table.get_text(" ", strip=True))
        check(f"flat_table:{year}", table.find("table") is None)
        target = UNIT / "source-fragments" / f"segment-{year}.html"
        target.write_text(fragment.group())
        rows = table.find_all("tr")
        merged = [[" ".join(c.stripped_strings) for c in row.find_all(["td", "th"], recursive=False)] for row in rows]
        values = [[x for x in cells if x and x != "$"] for cells in merged]
        check(f"year:{year}", values[1] == [year])
        check(f"columns:{year}", values[2] == segments)
        check(f"labels:{year}", [v[0] for v in values[3:]] == expected_labels)
        matrix = {}
        view_rows = ["<tr><th>Item</th>" + "".join("<th>" + html.escape(s) + "</th>" for s in segments) + "</tr>"]
        for row_number, (label, *cells) in enumerate(values[3:], start=3):
            check(f"width:{year}:{label}", len(cells) == 7)
            parsed = []
            for segment, literal in zip(segments, cells):
                if literal == "—":
                    value = None
                else:
                    check(f"number:{year}:{label}:{segment}", re.fullmatch(r"\(?[0-9,]+\)?", literal) is not None)
                    value = int(literal.replace(",", "").strip("()")) * (-1 if literal.startswith("(") else 1)
                parsed.append(value)
                readings.append({"fiscal_year": year, "segment": segment, "label": label,
                    "literal": literal, "value": value, "value_kind": "reported dash" if value is None else "displayed integer",
                    "unit": "USD million", "entity": "Apple Inc. consolidated reportable-segment presentation",
                    "information_source": "FY2025 Form 10-K", "html_table_index": index,
                    "source_row": row_number, "source": relative(SOURCE), "source_sha256": sha(SOURCE),
                    "printed_page": 47, "raw_row_cells": merged[row_number]})
            matrix[label] = parsed
            view_rows.append("<tr><td>" + html.escape(label) + "</td>" + "".join("<td>" + html.escape(v) + "</td>" for v in cells) + "</tr>")
        matrices[year] = matrix
        body = f"<h1>FY2025 Note 13: {year} comparative table</h1><p>USD millions. Derived view from retained HTML table {index}; exact cell text and column order preserved. Dashes remain dashes.</p><table>" + "".join(view_rows) + "</table>"
        view_text = " ".join(BeautifulSoup(body, "html.parser").stripped_strings)
        check(f"view_text:{year}", all(" ".join(v) in view_text for v in values[2:]))
        views.append(render_view("segment-" + year, body, landscape=True))
        source_tables.append({"year": year, "table_index": index, "fragment": relative(target),
                              "sha256": sha(target), "raw_start": fragment.start(), "raw_end": fragment.end()})
        # All operands below are explicitly reported numerical cells, not dash-to-zero conversions.
        for col, segment in enumerate(segments[:5]):
            check(f"operating_bridge:{year}:{segment}", matrix["Net sales"][col] + matrix["Cost of sales"][col] + matrix["Selling and marketing"][col] == matrix["Operating income/(loss)"][col])
        for label in ["Net sales", "Cost of sales", "Selling and marketing"]:
            check(f"reported_region_sum:{year}:{label}", sum(matrix[label][:5]) == matrix[label][6])
        check(f"corporate_bridge:{year}", matrix["Research and development"][5] + matrix["General and administrative"][5] == matrix["Operating income/(loss)"][5])
        check(f"company_income:{year}", sum(matrix["Operating income/(loss)"][:6]) == matrix["Operating income/(loss)"][6])

    prior = json.loads(PRIOR.read_text())["tables"]
    comparisons = []
    for prior_col, year in enumerate(["2024", "2023"]):
        for label, key in [("Net sales", "annual.sales"), ("Operating income/(loss)", "annual.income")]:
            for col, segment in enumerate(segments[:5]):
                old = prior[key]["rows"][segment][prior_col]
                new = matrices[year][label][col]
                check(f"unchanged_comparative:{year}:{segment}:{label}", old == new)
                comparisons.append({"fiscal_year": year, "segment": segment, "label": label,
                                    "old": old, "new": new, "disposition": "same displayed amount; preserve both source assertions"})
        bridge = prior["annual.bridge"]
        check(f"same_total_income:{year}", bridge["consolidated"][prior_col] == matrices[year]["Operating income/(loss)"][6])
        check(f"same_rd:{year}", bridge["rd"][prior_col] == -matrices[year]["Research and development"][5])
        check(f"same_corporate_number:{year}", bridge["other"][prior_col] == -matrices[year]["General and administrative"][5])
    old_text = (ROOT / "docs/design/cases/apple/annual-2024.txt").read_text()
    a = old_text.index("Note 13 – Segment")
    b = old_text.index("Report of Independent Registered Public Accounting Firm", a)
    old_note = old_text[a:b]
    # This is a note-scoped absence; no assertion about every earlier public source.
    check("old_note_has_no_separate_selling_marketing_row", "Selling and marketing" not in old_note)
    check("old_corporate_qualification_preserved", "various nonrecurring charges" in old_note)
    old_pdf = ROOT / "docs/design/cases/apple/annual-2024.pdf"
    with fitz.open(old_pdf) as document:
        for page_number in (49, 50):
            target = UNIT / "source-views" / f"annual2024-p{page_number}.png"
            document[page_number - 1].get_pixmap(matrix=fitz.Matrix(1.35, 1.35)).save(target)
            views.append({"original_pdf": relative(old_pdf), "pdf_page": page_number,
                          "images": [{"path": relative(target), "sha256": sha(target)}]})

    definitions = spans["note13"]["text"].split("The following tables show information by reportable segment")[0]
    country = spans["note13"]["text"].split("The following tables show net sales for 2025")[1]
    body = "<h1>FY2025 Note 1 adoption and Note 13 definitions</h1><p>Derived text view, not a browser screenshot.</p>"
    for passage in [spans["adoption"]["text"], definitions, "The following tables show net sales for 2025" + country]:
        body += "<pre>" + html.escape(passage) + "</pre>" if "Net sales:" in passage else "<p>" + html.escape(passage).replace("\n", "<br>") + "</p>"
    views.append(render_view("adoption-and-definitions", body))
    statement_rows = {x["id"]: x for x in json.loads(STATEMENTS.read_text())["rows"]}
    for key in [k for k in statement_rows if k.startswith("operations.")]:
        if "selling" in statement_rows[key]["label"].lower():
            value = int(statement_rows[key]["value"])
            check("2024_sga_decomposition", value == -matrices["2024"]["Selling and marketing"][6] - matrices["2024"]["General and administrative"][6])
            sga_comparison = {"prior_row": key, "prior_value": value,
                              "later_selling_marketing": 18639, "later_general_administrative": 7458}
            break
    else:
        raise AssertionError("Prior SG&A row not found")
    save("retrospective-segment-readings.json", {"source": relative(SOURCE), "sha256": sha(SOURCE),
        "text_source": relative(TEXT), "text_sha256": sha(TEXT), "spans": spans,
        "tables": source_tables, "rows": readings, "comparisons": comparisons,
        "sg_and_a": sga_comparison,
        "corporate_label_limit": "Other corporate expenses, net in FY2024 and General and administrative in FY2025 have matching displayed amounts for these years; amount equality alone does not establish identical scope or a general concept mapping.",
        "geographic_wording_limit": "FY2025 Rest of Asia Pacific explicitly names New Zealand; FY2024 wording did not. Do not infer a perimeter change from wording alone.",
        "information_time_limit": "Later reported comparative detail, not an accounting-error correction or historical-byte admission."})
    save("source-view-manifest.json", {"source": relative(SOURCE), "sha256": sha(SOURCE), "views": views,
                                      "inspection_status": "rendered; manual visual inspection required"})
    save("source-checks.json", {"passed": sum(checks.values()), "failed": [k for k,v in checks.items() if not v], "checks": checks})
    inputs = [SOURCE, TEXT, PRIOR, STATEMENTS, old_pdf, ROOT / "docs/design/cases/apple/annual-2024.txt", Path(__file__)]
    save("source-run.json", {"started_utc": started, "wall_seconds": time.monotonic() - timer,
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "command": "python3 data/accounting-master/p17-completion-20261014/P17-02/check_retrospective_segments.py",
        "environment": "system Python; BeautifulSoup and PyMuPDF; document parsing and integer arithmetic",
        "cpu_gpu": "CPU document processing; no GPU detection or numerical framework imported",
        "random_seeds": "N/A: deterministic source comparison", "data_version": "retained FY2024 and FY2025 filings, hashes below",
        "plan": "docs/plans/accounting-apple-retrospective-segments-20261014.md",
        "result": relative(UNIT / "result.md"),
        "inputs": [{"path": relative(p), "sha256": sha(p)} for p in inputs],
        "outputs": ["retrospective-segment-readings.json", "source-view-manifest.json", "source-checks.json"],
        "readiness": "not_ready"})
    print(json.dumps({"passed": sum(checks.values()), "failed": 0, "cells": len(readings),
                      "same_period_matches": len(comparisons), "source_views": len(views)}))


if __name__ == "__main__":
    main()
