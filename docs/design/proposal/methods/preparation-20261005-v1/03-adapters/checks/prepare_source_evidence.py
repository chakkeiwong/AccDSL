"""Build portable source anchors and a located retained-source example; no adapters run."""
from pathlib import Path
import hashlib
import json
import re

BASE = Path(__file__).resolve().parents[1]

ANCHORS = {
    "A01": [("arelle/arelle__ModelInstanceObject.py", 179, 208), ("arelle/arelle__ModelInstanceObject.py", 308, 455)],
    "A02": [("arelle/arelle__ModelInstanceObject.py", 634, 780)],
    "A03": [("arelle/arelle__ModelInstanceObject.py", 1035, 1159)],
    "A04": [("arelle/arelle__ModelObject.py", 141, 163), ("arelle/arelle__ModelInstanceObject.py", 1294, 1311)],
    "A05": [("arelle/arelle__ModelInstanceObject.py", 1239, 1259), ("arelle/arelle__ModelInstanceObject.py", 1479, 1511), ("arelle/arelle__ModelInstanceObject.py", 1359, 1410)],
    "A06": [("arelle/arelle__XmlUtil.py", 969, 1034)],
    "A07": [("arelle/arelle__ValidateDuplicateFacts.py", 45, 135), ("arelle/arelle__ValidateDuplicateFacts.py", 193, 282)],
    "A08": [("arelle/arelle__plugin__saveLoadableOIM.py", 396, 441), ("arelle/arelle__plugin__saveLoadableOIM.py", 452, 551)],
    "A09": [("arelle/arelle__ValidateXbrlCalcs.py", 704, 736)],
    "A10": [("arelle/arelle__api__Session.py", 29, 120), ("arelle/arelle__api__Session.py", 142, 162)],
    "A11": [("arelle/arelle__WebCache.py", 162, 189), ("arelle/arelle__WebCache.py", 600, 628), ("arelle/arelle__WebCache.py", 687, 748)],
    "D01": [("docling/docling__utils__utils.py", 22, 39)],
    "D02": [("docling/docling__document_converter.py", 556, 645), ("docling/docling__datamodel__document.py", 638, 717)],
    "D03": [("docling/docling__datamodel__document.py", 389, 424), ("docling/docling__datamodel__document.py", 474, 497)],
    "D04": [("docling/docling__pipeline__standard_pdf_pipeline.py", 992, 1036), ("docling/docling__pipeline__standard_pdf_pipeline.py", 1150, 1181)],
    "D05": [("docling/docling__models__stages__reading_order__readingorder_model.py", 200, 277)],
    "D06": [("docling/docling__backend__html_backend.py", 1490, 1513)],
    "D07": [("docling/docling__datamodel__pipeline_options.py", 1389, 1441), ("docling/docling__datamodel__pipeline_options.py", 2097, 2162)],
    "C01": [("docling-core/docling_core__types__doc__common__origin.py", 12, 26), ("docling-core/docling_core__types__doc__common__origin.py", 61, 75)],
    "C02": [("docling-core/docling_core__types__doc__common__reference.py", 183, 203), ("docling-core/docling_core__types__doc__base.py", 47, 70)],
    "C03": [("docling-core/docling_core__types__doc__items__text.py", 19, 43), ("docling-core/docling_core__types__doc__items__node.py", 119, 128)],
    "C04": [("docling-core/docling_core__types__doc__items__table__table_data.py", 20, 55), ("docling-core/docling_core__types__doc__items__table__table_data.py", 105, 149)],
    "C05": [("docling-core/docling_core__types__doc__common__reference.py", 32, 84)],
    "C06": [("docling-core/docling_core__types__doc__document.py", 3843, 3859), ("docling-core/docling_core__types__doc__document.py", 3926, 4006)],
    "X01": [("docling/docling__backend__xml__xbrl_backend.py", 86, 192), ("docling/docling__backend__xml__xbrl_backend.py", 194, 210)],
    "X02": [("docling/docling__backend__xml__xbrl_backend.py", 292, 320)],
    "X03": [("docling/docling__backend__xml__xbrl_backend.py", 321, 388)],
    "X04": [("docling/docling__backend__xml__xbrl_backend.py", 389, 473)],
    "P01": [("pdfplumber/pdfplumber__page.py", 353, 424), ("pdfplumber/pdfplumber__pdf.py", 149, 169)],
    "P02": [("pdfplumber/pdfplumber__page.py", 452, 497)],
    "P03": [("pdfplumber/pdfplumber__table.py", 421, 457)],
    "L01": [("arelle/LICENSE.md", 1, 18)],
    "L02": [("docling/LICENSE", 1, 21), ("docling-core/LICENSE", 1, 21)],
    "L03": [("pdfplumber/LICENSE.txt", 1, 21)],
    "V01": [("docling/pyproject.toml", 1, 54), ("docling/pyproject.toml", 169, 174)],
    "V02": [("docling-core/pyproject.toml", 1, 6), ("arelle/pyproject.toml", 1, 11)],
}

rows = []
for anchor_id, parts in ANCHORS.items():
    segments = []
    for filename, start, end in parts:
        path = Path("sources/upstream") / filename
        raw = (BASE / path).read_bytes()
        lines = raw.decode().splitlines(keepends=True)
        assert 1 <= start <= end <= len(lines), (anchor_id, len(lines), start, end)
        excerpt = "".join(lines[start - 1:end])
        segments.append({"path": str(path), "line_start": start, "line_end": end,
                         "source_sha256": hashlib.sha256(raw).hexdigest(),
                         "excerpt_sha256": hashlib.sha256(excerpt.encode()).hexdigest()})
    rows.append({"id": anchor_id, "segments": segments, "inspection": "read source; runtime not executed"})
(BASE / "source-anchors.json").write_text(json.dumps(rows, indent=2) + "\n")

source = BASE / "sources/retained/apple-2025-q1-original.html"
raw = source.read_bytes()
text = raw.decode()
parts = {}
for name, element_id, pattern in [
    ("fact", "f-134", r'<ix:nonFraction\b[^>]*id="f-134"[^>]*>.*?</ix:nonFraction>'),
    ("context", "c-17", r'<xbrli:context\b[^>]*id="c-17"[^>]*>.*?</xbrli:context>'),
    ("unit", "usd", r'<xbrli:unit\b[^>]*id="usd"[^>]*>.*?</xbrli:unit>'),
]:
    match = re.search(pattern, text, re.I | re.S)
    assert match, name
    parts[name] = {"byte_start": len(text[:match.start()].encode()),
                   "byte_end_exclusive": len(text[:match.end()].encode()),
                   "excerpt": match.group(), "element_id": element_id}
case = {
    "id": "APPLE-INSTANT-01", "report_id": "apple-2025-q1",
    "original_repo_path": "data/financial-report-benchmark/documents/apple/apple-2025-q1/original.html",
    "source_path": str(source.relative_to(BASE)), "source_sha256": hashlib.sha256(raw).hexdigest(),
    "locator_convention": "UTF-8 original bytes; start inclusive/end exclusive; IDs within same source version",
    "parts": parts,
    "expected": {"literal": "344,085", "normalized_decimal": "344085000000", "currency": "USD",
                 "scale": "6", "decimals": "-6", "reported_instant": "2024-12-28",
                 "normalized_xbrl_boundary": "2024-12-29T00:00:00",
                 "entity_identifier": {"scheme": "http://www.sec.gov/CIK", "value": "0000320193"},
                 "publication": {"state": "not_assessed_in_this_packet"},
                 "acceptance": "provisional source reading, no accounting admission"},
    "comparison_limit": "No Arelle or Docling executed. Docling XBRL backend accepts native instance only; date-format counterexample concerns equivalent instance context.",
}
(BASE / "apple-instant-case.json").write_text(json.dumps(case, indent=2) + "\n")
print(f"Prepared {len(rows)} claim anchor groups and {len(parts)} located Apple excerpts.")
