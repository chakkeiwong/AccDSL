"""Finite documentary XML-fragment diagnostic; no rendering or schema validation."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.parsers import expat

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"
COVERAGE = B / "native-concept-type-coverage-20261018/coverage.json"
TEXT = B / "r06-text-semantics-20261020/occurrences.json"
INSTANCE = B / "taxonomy-reuse-20261007/archive/aapl-20240928_htm.xml"
WRAPPER = "_accdsl_fragment"
REFUSAL = re.compile(r"<!DOCTYPE\b|<!ENTITY\b|<\?xml(?:\s|\?)", re.I)


def load(path):
    return json.loads(path.read_text())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bind(path):
    return {"path": str(path.relative_to(R)), "sha256": digest(path.read_bytes())}


def emit(tokens, token):
    # Expat is free to split character callbacks. Only adjacent text coalesces.
    if token[0] == "text":
        if not token[1]:
            return
        if tokens and tokens[-1][0] == "text":
            tokens[-1][1] += token[1]
            return
    tokens.append(token)


def tree_records(root):
    tokens, nodes = [], []

    def visit(node, path):
        if node.tag is ET.Comment:
            kind = "comment"
            emit(tokens, ["comment", node.text or ""])
            record = {"kind": kind, "path": path, "text": node.text, "tail": node.tail}
        elif node.tag is ET.ProcessingInstruction:
            kind = "pi"
            target, _, data = (node.text or "").partition(" ")
            emit(tokens, ["pi", target, data])
            record = {"kind": kind, "path": path, "target": target, "data": data,
                      "text": node.text, "tail": node.tail}
        else:
            kind = "element"
            attrs = [[k, v] for k, v in node.attrib.items()]
            emit(tokens, ["start", node.tag, sorted(attrs)])
            record = {"kind": kind, "path": path, "tag": node.tag,
                      "attributes": attrs, "text": node.text, "tail": node.tail}
        nodes.append(record)
        if kind == "element":
            emit(tokens, ["text", node.text or ""])
            for i, child in enumerate(node):
                visit(child, path + [i])
                emit(tokens, ["text", child.tail or ""])
            emit(tokens, ["end", node.tag])

    emit(tokens, ["text", root.text or ""])
    for i, node in enumerate(root):
        visit(node, [i])
        emit(tokens, ["text", node.tail or ""])
    return nodes, tokens


def event_records(wrapped):
    # Independent extraction path, but the same underlying Expat parser family.
    parser = expat.ParserCreate(namespace_separator="}")
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    parser.ExternalEntityRefHandler = lambda *args: 0
    tokens = []
    depth = 0

    def expanded(name):
        return "{" + name if "}" in name else name

    def start(name, attrs):
        nonlocal depth
        if depth:
            emit(tokens, ["start", expanded(name),
                          sorted([[expanded(k), v] for k, v in attrs.items()])])
        depth += 1

    def end(name):
        nonlocal depth
        depth -= 1
        if depth:
            emit(tokens, ["end", expanded(name)])

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.CharacterDataHandler = lambda value: emit(tokens, ["text", value])
    parser.CommentHandler = lambda value: emit(tokens, ["comment", value])
    parser.ProcessingInstructionHandler = lambda target, data: emit(tokens, ["pi", target, data])
    parser.Parse(wrapped, True)
    return tokens


def namespace(name):
    return name[1:].split("}", 1)[0] if name.startswith("{") else ""


def fragment(text):
    refused = REFUSAL.search(text)
    if refused:
        return {"status": "outside_local_profile", "reason": "declaration marker",
                "marker": refused.group(0), "offset": refused.start()}
    wrapped = "<" + WRAPPER + ">" + text + "</" + WRAPPER + ">"
    parser = ET.XMLParser(target=ET.TreeBuilder(insert_comments=True, insert_pis=True))
    tree_error = None
    event_error = None
    try:
        root = ET.fromstring(wrapped, parser=parser)
    except ET.ParseError as error:
        tree_error = str(error)
    try:
        independent = event_records(wrapped)
    except expat.ExpatError as error:
        event_error = str(error)
    assert (tree_error is None) == (event_error is None), "parser acceptance mismatch"
    if tree_error is not None:
        return {"status": "rejected_local_XML", "tree_error": tree_error,
                "event_error": event_error, "broader_DTR_validity": "not_determined"}
    nodes, tokens = tree_records(root)
    assert tokens == independent, "tree/event inventory mismatch"
    elements = [n for n in nodes if n["kind"] == "element"]
    character_text = "".join(t[1] for t in tokens if t[0] == "text")
    return {
        "status": "accepted_local_XML",
        "wrapper": {"tag": WRAPPER, "supplied_namespaces": {}, "root_text": root.text,
                    "top_level_nodes": len(root)},
        "nodes": nodes, "ordered_tokens": tokens, "event_extraction_matches": True,
        "counts": {"elements": len(elements),
                   "attributes": sum(len(n["attributes"]) for n in elements),
                   "comments": sum(n["kind"] == "comment" for n in nodes),
                   "processing_instructions": sum(n["kind"] == "pi" for n in nodes),
                   "nonempty_text_slots": sum(bool(n["text"]) for n in elements) + bool(root.text),
                   "nonempty_tail_slots": sum(bool(n["tail"]) for n in nodes)},
        "expanded_tags": dict(sorted(Counter(n["tag"] for n in elements).items())),
        "element_namespaces": dict(sorted(Counter(namespace(n["tag"]) for n in elements).items())),
        "attribute_namespaces": dict(sorted(Counter(namespace(k) for n in elements
                                                    for k, v in n["attributes"]).items())),
        "character_text": character_text,
        "character_utf8_sha256": digest(character_text.encode()),
        "fragment_utf8_sha256": digest(text.encode()),
        "character_text_is_display_text": False,
        "full_XHTML_conformance": "not_run", "schema_XBRL_validation": "not_run",
    }


def checked_source(row, actual, source_bytes):
    span = row["source_span"]
    piece = source_bytes[span["byte_start"]:span["byte_end"]]
    assert len(piece) == span["byte_length"]
    assert digest(piece) == span["slice_sha256"]
    assert piece.decode() == span["raw_utf8"]
    assert span["raw_utf8"].split(">", 1)[1].rsplit("<", 1)[0] == span["content_utf8"]
    assert actual.tag == row["source_concept"]
    assert actual.attrib == row["source_attributes"]
    assert len(actual) == 0
    assert actual.text == row["decoded_text"]
    assert row["packet_candidate_value"]["tag"] == "UnvalidatedText"
    assert row["portable_candidate_value"]["tag"] == "Text"
    assert actual.text == row["packet_candidate_value"]["text"] == row["portable_candidate_value"]["text"]
    # Check the source content by exactly one XML parsing step, without html.unescape.
    parsed = ET.fromstring("<" + WRAPPER + ">" + span["content_utf8"] + "</" + WRAPPER + ">")
    assert len(parsed) == 0 and parsed.text == actual.text
    assert row["validation_status"] == "not_run" and not row["portable_value_mutated"]


def derive():
    coverage = load(COVERAGE)
    all_text = load(TEXT)
    selected = {r["fact_id"]: r for r in all_text
                if any("XHTML" in s for s in r["nonfacet_semantic_obligations"])}
    source_bytes = INSTANCE.read_bytes()
    facts = {e.get("id"): e for e in ET.fromstring(source_bytes) if e.get("id")}
    rows, structures = [], {}
    for row in coverage["occurrences"]:
        ident = row["fact_id"]
        if ident not in selected:
            continue
        prior = selected[ident]
        assert row["decoded_text"] == prior["decoded_text"]
        assert row["source_span"] == prior["source_span"]
        checked_source(row, facts[ident], source_bytes)
        result = fragment(row["decoded_text"])
        assert result["status"] == "accepted_local_XML", ident
        structures[ident] = result
        rows.append({
            "fact_id": ident, "source_concept": row["source_concept"],
            "source_context_id": row["source_context_id"],
            "source_span": row["source_span"], "decoded_text": row["decoded_text"],
            "decoded_utf8_bytes": len(row["decoded_text"].encode()),
            "decoded_utf8_sha256": digest(row["decoded_text"].encode()),
            "packet_tag": row["packet_candidate_value"]["tag"],
            "portable_tag": row["portable_candidate_value"]["tag"],
            "structure_file": "structures/" + ident + ".json",
            "counts": result["counts"], "expanded_tags": result["expanded_tags"],
            "character_utf8_sha256": result["character_utf8_sha256"],
            "local_XML": result["status"], "full_XHTML_conformance": "not_run",
            "schema_XBRL_validation": "not_run", "source_values_mutated": False,
        })
    assert len(rows) == len(selected) == 56
    return rows, structures


def check():
    assertions = 0

    def require(test, label):
        nonlocal assertions
        assert test, label
        assertions += 1

    ledger = load(U / "source-ledger.json")
    for binding in ledger["bindings"]:
        require(bind(R / binding["path"]) == binding, binding["path"])
    for anchor in ledger["anchors"]:
        path = R / anchor["source"]["path"]
        require(bind(path) == anchor["source"], anchor["id"])
        text = "\n".join(path.read_text().splitlines()[anchor["first_line"]-1:anchor["last_line"]])
        require(text == anchor["excerpt"], anchor["id"] + " excerpt")
    rows, structures = derive()
    require(rows == load(U / "occurrences.json"), "all occurrence records")
    for row in rows:
        record = load(U / row["structure_file"])
        require(record == structures[row["fact_id"]], row["fact_id"] + " structure")
        require(record["element_namespaces"] == {"": record["counts"]["elements"]},
                row["fact_id"] + " observed empty element namespace")
        require(record["counts"]["comments"] == record["counts"]["processing_instructions"] == 0,
                row["fact_id"] + " comments/PIs absent")
    fixtures = load(U / "fixtures.json")
    for fixture in fixtures:
        result = fragment(fixture["input"])
        require(result["status"] == fixture["expected_status"], fixture["id"])
        if "expected_text" in fixture:
            require(result["character_text"] == fixture["expected_text"], fixture["id"] + " characters")
        if "expected_tags" in fixture:
            require(result["expanded_tags"] == fixture["expected_tags"], fixture["id"] + " tags")
        if "expected_counts" in fixture:
            for key, value in fixture["expected_counts"].items():
                require(result["counts"][key] == value, fixture["id"] + " " + key)
        if "expected_attrs" in fixture:
            attrs = [a for n in result["nodes"] if n["kind"] == "element" for a in n["attributes"]]
            require(attrs == fixture["expected_attrs"], fixture["id"] + " attributes")
    corruption_results = []
    original = rows[0]
    coverage = load(COVERAGE)
    source_row = next(r for r in coverage["occurrences"] if r["fact_id"] == original["fact_id"])
    source_bytes = INSTANCE.read_bytes()
    fact = next(e for e in ET.fromstring(source_bytes) if e.get("id") == original["fact_id"])
    for kind in ("source_hash", "decoded_text", "packet_text", "portable_text"):
        changed = json.loads(json.dumps(source_row))
        if kind == "source_hash":
            changed["source_span"]["slice_sha256"] = "0" * 64
        elif kind == "decoded_text":
            changed["decoded_text"] += "x"
        else:
            changed[kind.removesuffix("_text") + "_candidate_value"]["text"] += "x"
        try:
            checked_source(changed, fact, source_bytes)
        except AssertionError:
            corruption_results.append(kind)
        else:
            raise AssertionError("accepted corrupted " + kind)
    require(corruption_results == load(U / "altered-controls.json")["source_corruptions"],
            "four altered source layers rejected")
    for control in load(U / "altered-controls.json")["fragment_changes"]:
        a, b = fragment(control["original"]), fragment(control["altered"])
        require(a["status"] == "accepted_local_XML", control["id"] + " baseline")
        if control["target"] == "parse_failure":
            require(b["status"] == "rejected_local_XML", control["id"] + " rejection")
        else:
            require(a[control["target"]] != b[control["target"]], control["id"] + " distinction")
    require(sum(r["decoded_utf8_bytes"] for r in rows) == 941509, "total retained fragment bytes")
    amp = [r for r in rows if "&amp;" in r["decoded_text"]]
    require(len(amp) == 1 and amp[0]["decoded_text"].count("&amp;") == 1, "actual entity example")
    require(load(U / "real-entity-example.json")["fact_id"] == amp[0]["fact_id"], "bound real example")
    return {"assertions": assertions, "textblock_occurrences": len(rows),
            "decoded_utf8_bytes": sum(r["decoded_utf8_bytes"] for r in rows),
            "elements": sum(r["counts"]["elements"] for r in rows),
            "attributes": sum(r["counts"]["attributes"] for r in rows),
            "nonempty_tail_slots": sum(r["counts"]["nonempty_tail_slots"] for r in rows),
            "fixtures": len(fixtures),
            "source_corruptions_rejected": len(corruption_results),
            "fragment_alterations_distinguished": len(load(U / "altered-controls.json")["fragment_changes"]),
            "source_anchors": len(ledger["anchors"]), "input_bindings": len(ledger["bindings"]),
            "runtime_execution": False, "schema_XBRL_validation": "not_run",
            "full_XHTML_conformance": "not_run", "whole_rows_closed": 0}
