"""Scoped names and exact global declaration spans; no schema validation."""
from io import BytesIO
import hashlib
import xml.etree.ElementTree as ET
from xml.parsers import expat

XS = "http://www.w3.org/2001/XMLSchema"
XML = "http://www.w3.org/XML/1998/namespace"


def require(condition, label):
    if not condition:
        raise ValueError(label)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def tag_end(raw, start):
    quote = None
    for index in range(start, len(raw)):
        char = raw[index]
        if quote is not None:
            if char == quote:
                quote = None
        elif char in (34, 39):
            quote = char
        elif char == 62:
            return index + 1
    raise ValueError("UNCLOSED_TAG")


def parse_source(raw, path):
    require(b"<!DOCTYPE" not in raw, "DTD_NOT_ADMITTED")
    pending = {}
    scopes = {}
    stack = [{"xml": XML}]
    root = None
    for event, value in ET.iterparse(BytesIO(raw), events=("start-ns", "start", "end")):
        if event == "start-ns":
            prefix, uri = value
            pending[prefix or ""] = uri
        elif event == "start":
            scope = dict(stack[-1])
            scope.update(pending)
            pending.clear()
            scopes[value] = scope
            stack.append(scope)
            if root is None:
                root = value
        else:
            stack.pop()
    require(root is not None, "EMPTY_XML")
    parser = expat.ParserCreate(namespace_separator="}")
    spans = []
    depth = 0
    current = None

    def expanded(name):
        return "{" + name if "}" in name else name

    def start(name, attributes):
        nonlocal depth, current
        depth += 1
        if depth == 2:
            begin = parser.CurrentByteIndex
            opening_end = tag_end(raw, begin)
            current = (expanded(name), {expanded(k): v for k, v in attributes.items()},
                       begin, opening_end, raw[opening_end - 2:opening_end] == b"/>")

    def end(name):
        nonlocal depth, current
        if depth == 2:
            tag, attributes, begin, opening_end, empty = current
            finish = opening_end if empty else tag_end(raw, parser.CurrentByteIndex)
            spans.append((tag, attributes, begin, finish))
            current = None
        depth -= 1

    def reject_doctype(*args):
        raise ValueError("DTD_NOT_ADMITTED")

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    parser.StartDoctypeDeclHandler = reject_doctype
    parser.Parse(raw, True)
    require(len(spans) == len(root), "PARSER_GLOBAL_COUNT")
    locations = {}
    for element, (tag, attributes, begin, finish) in zip(root, spans):
        require(element.tag == tag and element.attrib == attributes, "PARSER_GLOBAL_ALIGNMENT")
        locations[element] = (begin, finish)
    return {"path": path, "raw": raw, "sha256": digest(raw), "root": root, "scopes": scopes,
            "locations": locations, "namespace": root.get("targetNamespace", "")}


def qname(token, source, element):
    require(isinstance(token, str) and bool(token.strip()), "MISSING_QNAME")
    parts = token.strip().split(":")
    require(len(parts) <= 2 and all(parts), "MALFORMED_QNAME_REFERENCE")
    prefix, local = parts if len(parts) == 2 else ("", parts[0])
    scope = source["scopes"][element]
    require(not prefix or prefix in scope, "UNBOUND_PREFIX")
    namespace = scope.get(prefix, "")
    return "{" + namespace + "}" + local if namespace else local


def global_index(sources):
    index = {}
    for source in sources:
        if source["root"].tag != "{" + XS + "}schema":
            continue
        for element in source["root"]:
            kind = element.tag.removeprefix("{" + XS + "}")
            if not element.tag.startswith("{" + XS + "}") or not element.get("name"):
                continue
            name = ("{" + source["namespace"] + "}" if source["namespace"] else "") + element.get("name")
            index.setdefault((kind, name), []).append((source, element))
    return index


def anchor(source, element):
    begin, finish = source["locations"][element]
    raw = source["raw"]
    return {"source_path": source["path"], "source_sha256": source["sha256"],
            "byte_start": begin, "byte_end": finish, "slice_sha256": digest(raw[begin:finish]),
            "first_line": raw[:begin].count(b"\n") + 1,
            "last_line": raw[:finish].count(b"\n") + 1,
            "text": raw[begin:finish].decode("utf-8")}


def type_node(index, name):
    if name.startswith("{" + XS + "}"):
        return {"type": name, "status": "builtin_reference_only", "edges": []}
    matches = index.get(("complexType", name), []) + index.get(("simpleType", name), [])
    if len(matches) != 1:
        return {"type": name, "status": "unresolved",
                "reason": "missing_definition" if not matches else "ambiguous_definition",
                "candidate_count": len(matches), "edges": []}
    source, element = matches[0]
    node = {"type": name, "definition_kind": element.tag.split("}")[-1],
            "anchor": anchor(source, element), "edges": [], "status": "retained_derivation",
            "derivation_attributes": {}, "derivation_children": []}
    content = element.find("{" + XS + "}simpleContent") if node["definition_kind"] == "complexType" else element
    if content is None:
        return dict(node, status="unresolved", reason="unsupported_non_simple_content")
    methods = [e for e in content if e.tag in {"{" + XS + "}" + k for k in ("extension", "restriction", "list", "union")}]
    if len(methods) != 1:
        return dict(node, status="unresolved", reason="unsupported_derivation_count")
    method = methods[0]
    node["derivation"] = method.tag.split("}")[-1]
    node["derivation_attributes"] = dict(method.attrib)
    node["derivation_children"] = [{"tag": e.tag, "attributes": dict(e.attrib)}
                                    for e in method if e.tag != "{" + XS + "}annotation"]
    if method.find("{" + XS + "}simpleType") is not None:
        return dict(node, status="unresolved", reason="unsupported_inline_simple_type")
    attributes = {"extension": "base", "restriction": "base", "list": "itemType", "union": "memberTypes"}
    attribute = attributes[node["derivation"]]
    tokens = method.get(attribute, "").split()
    if not tokens or (attribute != "memberTypes" and len(tokens) != 1):
        return dict(node, status="unresolved", reason="missing_or_multiple_type_reference")
    try:
        node["edges"] = [{"role": attribute, "lexical_token": token,
                          "target": qname(token, source, method)} for token in tokens]
    except ValueError as error:
        return dict(node, status="unresolved", reason=str(error), edges=[])
    return node
