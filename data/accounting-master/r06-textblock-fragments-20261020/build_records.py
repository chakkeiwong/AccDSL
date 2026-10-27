"""One-time construction of finite text-block structure records."""
import importlib.util
import json
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def write(name, value):
    path = U / name
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, indent=2)
        f.write("\n")


def main():
    assert not (U / "source-ledger.json").exists(), "one-time construction"
    spec = importlib.util.spec_from_file_location("local_fragments", U / "compare.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rows, structures = m.derive()
    write("occurrences.json", rows)
    for ident, structure in structures.items():
        write("structures/" + ident + ".json", structure)
    acquisitions = []
    for name in ("01-xml", "02-xhtml", "02-xhtml-trusted"):
        acquisitions.append({"id": name, **{
            suffix: m.bind(U / "sources" / (name + "." + suffix))
            for suffix in ("receipt.json", "headers", "body", "visible.txt")
            if (U / "sources" / (name + "." + suffix)).is_file()
        }})
    write("acquisitions.json", acquisitions)
    sections = [
        ("xml_edition", "01-xml", 1, 67),
        ("xml_document", "01-xml", 259, 285),
        ("xml_characters_comments_pi_cdata", "01-xml", 409, 515),
        ("xml_line_endings", "01-xml", 761, 773),
        ("xml_content", "01-xml", 885, 947),
        ("xml_attributes", "01-xml", 1228, 1264),
        ("xml_references", "01-xml", 1373, 1430),
        ("xml_parsed_entities", "01-xml", 1607, 1624),
        ("xml_predefined_entities", "01-xml", 1914, 1946),
        ("xml_processor_scope", "01-xml", 1985, 2039),
        ("xhtml_edition", "02-xhtml-trusted", 1, 44),
        ("xhtml_document_conformance", "02-xhtml-trusted", 202, 240),
        ("xhtml_xml_differences", "02-xhtml-trusted", 301, 351),
        ("xhtml_ampersands", "02-xhtml-trusted", 481, 486),
    ]
    anchors = []
    for ident, name, first, last in sections:
        path = U / "sources" / (name + ".visible.txt")
        anchors.append({"id": ident, "source": m.bind(path), "first_line": first,
                        "last_line": last,
                        "excerpt": "\n".join(path.read_text().splitlines()[first-1:last])})
    for name in ("import-05-trusted.body", "import-06-trusted.body"):
        path = B / "taxonomy-reuse-20261007/sources" / name
        anchors.append({"id": "dtr_" + name, "source": m.bind(path), "first_line": 31,
                        "last_line": 106,
                        "excerpt": "\n".join(path.read_text().splitlines()[30:106])})
    inputs = {m.COVERAGE, m.TEXT, m.INSTANCE,
              B / "r06-text-semantics-20261020/completion.json",
              B / "r06-enumeration-domain-20261020/extract_visible.py"}
    inputs.update(R / a["source"]["path"] for a in anchors)
    for acquisition in acquisitions:
        inputs.update(R / value["path"] for key, value in acquisition.items() if key != "id")
    write("source-ledger.json", {
        "date": "2026-10-20", "primary_documents": 2, "request_attempts": 3,
        "bindings": [m.bind(path) for path in sorted(inputs)], "anchors": anchors,
        "scope": "DTR 2020/2022 annotations; selected XML 1.0 Fifth Edition and conditional XHTML 1.0 Second Edition rules",
        "extraction": "Visible class from bound predecessor; original HTML retained; inline hidden subtrees omitted from separate readable views",
        "edition_limit": "XML Fifth Edition diagnostic does not replace historical XML Schema dependencies; no XHTML edition is selected for DTR conformance",
    })
    accepted = "accepted_local_XML"
    rejected = "rejected_local_XML"
    outside = "outside_local_profile"
    fixtures = [
        {"id": "empty", "input": "", "expected_status": accepted, "expected_text": "", "expected_tags": {}},
        {"id": "plain", "input": "Plain text", "expected_status": accepted, "expected_text": "Plain text"},
        {"id": "mixed_roots", "input": "a<div>b</div>c<span>d</span>e", "expected_status": accepted,
         "expected_text": "abcde", "expected_tags": {"div": 1, "span": 1},
         "expected_counts": {"elements": 2, "nonempty_tail_slots": 2}},
        {"id": "nested_tail", "input": "<p>a<b>b</b>c<i>d</i>e</p>f", "expected_status": accepted,
         "expected_text": "abcdef", "expected_counts": {"elements": 3, "nonempty_tail_slots": 3}},
        {"id": "nested_escape", "input": "<p>&amp;lt;b&amp;gt;literal&amp;lt;/b&amp;gt;</p>",
         "expected_status": accepted, "expected_text": "&lt;b&gt;literal&lt;/b&gt;", "expected_tags": {"p": 1}},
        {"id": "escaped_markup", "input": "<p>&lt;b&gt;literal&lt;/b&gt;</p>",
         "expected_status": accepted, "expected_text": "<b>literal</b>", "expected_tags": {"p": 1}},
        {"id": "ampersand", "input": "<p>A &amp; B</p>", "expected_status": accepted, "expected_text": "A & B"},
        {"id": "line_endings", "input": "<p>a\r\nb\rc&#13;d</p>", "expected_status": accepted, "expected_text": "a\nb\nc\rd"},
        {"id": "attribute_whitespace", "input": '<p a="x\t y&#9;z&#13;w\nq"/>',
         "expected_status": accepted, "expected_text": "", "expected_attrs": [["a", "x  y\tz\rw q"]]},
        {"id": "comments_pi", "input": "a<!--keep--><?target value?>b<p>c</p>d",
         "expected_status": accepted, "expected_text": "abcd",
         "expected_counts": {"comments": 1, "processing_instructions": 1, "elements": 1}},
        {"id": "cdata", "input": "<p><![CDATA[<b>&raw</b>]]></p>", "expected_status": accepted,
         "expected_text": "<b>&raw</b>", "expected_tags": {"p": 1}},
        {"id": "default_namespace", "input": '<div xmlns="http://www.w3.org/1999/xhtml"><span>x</span></div>',
         "expected_status": accepted, "expected_text": "x",
         "expected_tags": {"{http://www.w3.org/1999/xhtml}div": 1, "{http://www.w3.org/1999/xhtml}span": 1}},
        {"id": "prefix_scope", "input": '<p:x xmlns:p="urn:test" p:a="1"><p:y xmlns:p="urn:other"/></p:x>',
         "expected_status": accepted, "expected_text": "",
         "expected_tags": {"{urn:test}x": 1, "{urn:other}y": 1}, "expected_attrs": [["{urn:test}a", "1"]]},
        {"id": "numeric_reference", "input": "<p>&#160;&#x1F600;</p>", "expected_status": accepted, "expected_text": "\u00a0\U0001F600"},
        {"id": "non_xhtml_tag", "input": "<financialMystery a='1'>x</financialMystery>",
         "expected_status": accepted, "expected_text": "x", "expected_tags": {"financialMystery": 1}},
        {"id": "xml_stylesheet_pi", "input": '<?xml-stylesheet href="not-fetched"?>',
         "expected_status": accepted, "expected_text": "", "expected_counts": {"processing_instructions": 1}},
        *[{"id": ident, "input": value, "expected_status": rejected} for ident, value in [
            ("mismatched", "<p>x</div>"), ("overlap", "<p><b>x</p></b>"),
            ("bare_ampersand", "<p>A & B</p>"), ("undeclared_html_entity", "<p>&nbsp;</p>"),
            ("unbound_prefix", "<h:p>x</h:p>"), ("duplicate_attribute", '<p a="1" a="2"/>'),
            ("illegal_character", "<p>&#0;</p>"), ("unquoted_attribute", "<p a=1/>"),
            ("wrapper_breakout", "</_accdsl_fragment><p/>"),
        ]],
        *[{"id": ident, "input": value, "expected_status": outside} for ident, value in [
            ("doctype", "<!DOCTYPE p><p/>"), ("external_entity", '<!DOCTYPE p [<!ENTITY e SYSTEM "file:///no-read">]><p>&e;</p>'),
            ("xml_declaration", '<?xml version="1.0"?><p/>'),
            ("conservative_comment_refusal", "<!-- <!DOCTYPE p> --><p/>"),
        ]],
    ]
    write("fixtures.json", fixtures)
    write("altered-controls.json", {
        "source_corruptions": ["source_hash", "decoded_text", "packet_text", "portable_text"],
        "fragment_changes": [
            {"id": "tail_loss", "original": "<p>a<b>b</b>c</p>", "altered": "<p>a<b>b</b></p>", "target": "character_text"},
            {"id": "order_change", "original": "<p>A</p><p>B</p>", "altered": "<p>B</p><p>A</p>", "target": "ordered_tokens"},
            {"id": "attribute_loss", "original": '<p style="display:none">A</p>', "altered": "<p>A</p>", "target": "ordered_tokens"},
            {"id": "namespace_invention", "original": "<p>A</p>", "altered": '<p xmlns="http://www.w3.org/1999/xhtml">A</p>', "target": "expanded_tags"},
            {"id": "extra_unescape", "original": "<p>&lt;b&gt;A&lt;/b&gt;</p>", "altered": "<p><b>A</b></p>", "target": "ordered_tokens"},
            {"id": "ampersand_unescape", "original": "<p>A &amp; B</p>", "altered": "<p>A & B</p>", "target": "parse_failure"},
        ],
    })
    row = next(r for r in rows if "&amp;" in r["decoded_text"])
    offset = row["decoded_text"].index("&amp;")
    raw_offset = row["source_span"]["content_utf8"].index("&amp;amp;")
    structure = structures[row["fact_id"]]
    write("real-entity-example.json", {
        "fact_id": row["fact_id"], "source_concept": row["source_concept"],
        "raw_content_excerpt": row["source_span"]["content_utf8"][max(0,raw_offset-80):raw_offset+100],
        "decoded_fragment_excerpt": row["decoded_text"][max(0,offset-80):offset+100],
        "parsed_text_tokens": [t for t in structure["ordered_tokens"] if t[0] == "text" and "&" in t[1]],
        "steps": ["raw filing &amp;amp;", "decoded fragment &amp;", "fragment character content &"],
        "boundary": "The second parse interprets embedded XML, without mutating the stored decoded string or applying arbitrary recursive HTML unescaping.",
    })
    write("runtime-profile.json", {
        "ElementTree_version": m.ET.VERSION, "Expat_version": m.expat.EXPAT_VERSION,
        "parser_implementations_independent": False,
        "comparison": "ElementTree recursive node/text/tail traversal versus direct Expat event callbacks",
        "external_entities": "No declared entities/DTD admitted; parameter entities disabled; external handler refuses",
        "namespace_context": "No namespaces supplied by synthetic wrapper",
        "renderer_CSS_scripts_network": "not invoked", "schema_DTD_validation": "not_run",
    })
    write("source-support-ledger.json", {
        "classification": "PRIMARY_SPECIFICATION_AND_RETAINED_SOURCE",
        "identity": "source-ledger.json", "read_scope": "16 bounded technical/edition anchors",
        "allowed": "Finite XML structural records and explicit separation of evidence layers",
        "forbidden": ["full DTR/XHTML validity", "rendered text equivalence", "sanitization", "financial interpretation", "installed XBRL admission"],
    })
    write("claim-support-ledger.json", {"claims": [
        {"claim": "DTR text blocks add XML-node and XHTML-fragment duties beyond ordinary string facets.",
         "class": "PRIMARY_SOURCE", "anchors": ["dtr_import-05-trusted.body", "dtr_import-06-trusted.body"]},
        {"claim": "A wrapper admits a content sequence, unlike the exactly-one-root document grammar.",
         "class": "LOCAL_ARGUMENT_FROM_PRIMARY_RULE", "anchors": ["xml_document", "xml_content", "xml_parsed_entities"]},
        {"claim": "XML references, line endings and attribute normalization can change spelling at the parsing boundary.",
         "class": "PRIMARY_RULE_WITH_DISCRIMINATORS", "anchors": ["xml_references", "xml_line_endings", "xml_attributes", "xml_predefined_entities"], "evidence": "fixtures.json"},
        {"claim": "All selected retained fragments admit the local parse and agree under both extraction paths.",
         "class": "FINITE_CHECKED_OBSERVATION", "evidence": "occurrences.json"},
        {"claim": "XHTML 1.0 document rules do not establish an edition-specific DTR fragment verdict.",
         "class": "SCOPED_SOURCE_BOUNDARY", "anchors": ["xhtml_document_conformance", "dtr_import-06-trusted.body"]},
    ]})
    write("backward-snowball-ledger.json", {"scope": "Specification prerequisites",
        "leads": [
            {"source": "XML 1.0", "status": "Fifth Edition technical parsing sections read; historical edition correspondence unclaimed"},
            {"source": "XHTML 1.0 Second Edition", "status": "Document conformance and XML differences read conditionally; no automatic fragment validator"},
            {"source": "XHTML DTDs / HTML 4 / XML Namespaces", "status": "No new acquisition; full XHTML conformance and generic namespace-processor correctness unclaimed"},
            {"source": "DTR 2020 and 2022 annotations", "status": "Both retained type definitions read directly"},
        ]})
    write("forward-snowball-ledger.json", {"scope": "Fixed-version technical question", "new_queries": 0,
        "status": "Edition/status statements inspected; later corrections and full fragment-processing policy remain unverified"})
    write("citation-venue-ledger.json", {"sources": [
        {"title": "Extensible Markup Language (XML) 1.0 (Fifth Edition)", "date": "2008-11-26", "status": "W3C Recommendation"},
        {"title": "XHTML 1.0: The Extensible HyperText Markup Language (Second Edition)", "date": "2002-08-01", "status": "W3C Recommendation; checked conditional document rules"},
        ], "citation_metrics": "not applicable", "current_errata_completeness": "not established"})
    write("omission-risk-ledger.json", {"risks": [
        {"risk": "Repeated decoding invents markup or invalid ampersands", "response": "Raw, decoded and parsed layers separately bound; actual &amp;amp; example and altered controls"},
        {"risk": "Mixed content loses tail text, comments or PIs", "response": "Explicit tree nodes/text/tails plus event comparison and adversarial mixed-content fixtures"},
        {"risk": "Agreement mistaken for independent parser proof", "response": "Both paths use Expat; runtime-profile records this limit"},
        {"risk": "No namespace mistaken for XHTML invalidity", "response": "Record empty namespace observation; fragment context/edition remains unselected"},
        {"risk": "XML well-formedness called display or financial equivalence", "response": "Non-XHTML accepted fixture, preserved attributes and explicit not_run flags"},
        {"risk": "Unknown entity/declaration processed implicitly", "response": "Preparse conservative profile refusal; no fallback unescape or network retrieval"},
    ]})
    print(json.dumps({"constructed": True, "occurrences": len(rows), "fixtures": len(fixtures),
                      "anchors": len(anchors), "bindings": len(inputs),
                      "elements": sum(r["counts"]["elements"] for r in rows),
                      "attributes": sum(r["counts"]["attributes"] for r in rows)}))


if __name__ == "__main__":
    main()
