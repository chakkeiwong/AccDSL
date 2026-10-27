"""Finite typed-domain declaration/value checks; no full dimensional validation."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import re
import xml.etree.ElementTree as ET

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


m = imported("typed_source_helpers", B / "r06-numeric-lexical-20261020/compare.py")
t = imported("typed_date_helpers", B / "r06-text-semantics-20261020/compare.py")
p = imported("typed_period_comparator", B / "r06-context-periods-20261020/compare.py")
load, bind, digest = m.load, m.bind, m.digest
MAP = B / "native-offline-resolution-20261018/resource-map.json"
PACKET = B / "native-full-portable-20261018/native-packet.json"
PORTABLE = B / "native-full-portable-20261018/portable-records.json"
X = "{http://www.xbrl.org/2003/instance}"
D = "{http://xbrl.org/2005/xbrldt}"
I = "{http://xbrl.org/2006/xbrldi}"
XMLBASE = "{http://www.w3.org/XML/1998/namespace}base"
XS = m.XS
AXIS_LOCAL = "RevenueRemainingPerformanceObligationExpectedTimingOfSatisfactionStartDateAxis"
AXIS = "{http://fasb.org/us-gaap/2024}" + AXIS_LOCAL
DOMAIN = AXIS + ".domain"


def global_index():
    result = {}
    for resource in load(MAP):
        path = resource["retained_path"]
        raw = (R / path).read_bytes()
        assert digest(raw) == resource["expected_blob"]["digest"]
        root, scopes = m.schema(path)
        if root.tag != XS + "schema":
            continue
        namespace = root.get("targetNamespace")
        for element in root:
            if element.tag == XS + "element" and element.get("name"):
                name = "{" + namespace + "}" + element.get("name")
                result.setdefault(name, []).append((resource, root, scopes, element))
    return result


def anchor(path, name):
    raw = (R / path).read_bytes()
    needle = ("name='" + name + "'").encode()
    offset = 0
    found = []
    for line_number, line in enumerate(raw.splitlines(keepends=True), 1):
        if needle in line:
            piece = line.strip()
            assert piece.startswith(b"<xs:element ") and piece.endswith(b"/>")
            start = offset + line.index(piece)
            found.append({"source_path": path, "source_sha256": digest(raw),
                          "byte_start": start, "byte_end": start+len(piece),
                          "slice_sha256": digest(piece), "text": piece.decode(),
                          "first_line": line_number, "last_line": line_number})
        offset += len(line)
    assert len(found) == 1
    m.checked_anchor(found[0])
    return found[0]


def declared(index):
    assert len(index[AXIS]) == 1
    resource, root, scopes, axis = index[AXIS][0]
    assert axis.get("abstract") == "true"
    assert m.expanded(axis.get("substitutionGroup"), scopes[id(axis)]) == D + "dimensionItem"
    ref = axis.get(D + "typedDomainRef")
    assert re.fullmatch(r"#[A-Za-z_][A-Za-z0-9_.-]*", ref)
    assert all(XMLBASE not in e.attrib for e in root.iter())
    targets = [e for e in root if e.get("id") == ref[1:]]
    assert len(targets) == 1
    domain = targets[0]
    assert domain.tag == XS + "element"
    assert domain.get("abstract", "false") in ("false", "0")
    assert "{" + root.get("targetNamespace") + "}" + domain.get("name") == DOMAIN
    assert len(index[DOMAIN]) == 1 and index[DOMAIN][0][3] is domain
    dtype = m.expanded(domain.get("type"), scopes[id(domain)])
    assert dtype == XS + "date"
    assert len(domain) == 0 and "fixed" not in domain.attrib and "default" not in domain.attrib
    assert domain.get("nillable") == "true"
    # Dimension declaration's periodType/nillable do not define the typed value.
    return {"axis": AXIS, "domain": DOMAIN, "domain_type": dtype,
            "axis_attributes": dict(axis.attrib), "domain_attributes": dict(domain.attrib),
            "typedDomainRef": ref, "resolved_retained_uri": resource["logical_uri"] + ref,
            "resource_binding": resource,
            "axis_anchor": anchor(resource["retained_path"], axis.get("name")),
            "domain_anchor": anchor(resource["retained_path"], domain.get("name")),
            "resolver_profile": "same document bare fragment; XML Base absent; unique global nonabstract target",
            "installed_DTS_membership": "not_verified"}


def typed_value(node, scopes, declaration):
    if node.tag != I + "typedMember" or set(node.attrib) != {"dimension"}:
        return {"status": "outside_scope", "reason": "typed container attribute/profile"}
    token = node.get("dimension")
    try:
        name = m.expanded(m.collapse(token), scopes[id(node)])
    except (KeyError, ValueError):
        return {"status": "unresolved_axis"}
    if name != declaration["axis"]:
        return {"status": "wrong_typed_axis"}
    if len(node) != 1 or (node.text or "").strip():
        return {"status": "invalid_single_child_content"}
    child = node[0]
    if (child.tail or "").strip():
        return {"status": "invalid_single_child_content"}
    if child.tag != declaration["domain"]:
        return {"status": "wrong_domain_element"}
    if child.attrib or len(child):
        return {"status": "outside_scope", "reason": "non-nil attribute-free simple child required by local profile"}
    interpretation = t.base_interpretation(child.text or "", "date")
    if interpretation["status"] != "supported":
        return {"status": interpretation["status"], "date": interpretation}
    return {"status": "supported", "axis_token": token, "axis": name, "domain": child.tag,
            "raw_date_text": child.text, "date": interpretation,
            "period_endpoint_shift_applied": False, "full_schema_validation": "not_run"}


def parse_fixture(xml):
    # Keep namespace scopes for every element, including prefix-rebinding fixtures.
    from io import StringIO
    root, scopes, pending, stack = None, {}, [], []
    for event, item in ET.iterparse(StringIO(xml), events=("start-ns", "start", "end")):
        if event == "start-ns":
            pending.append(item)
        elif event == "start":
            if root is None:
                root = item
            scope = dict(stack[-1]) if stack else {}
            scope.update(pending)
            pending.clear()
            scopes[id(item)] = scope
            stack.append(scope)
        else:
            stack.pop()
    return root, scopes


def derive():
    declaration = declared(global_index())
    relative = str(m.INSTANCE.relative_to(R))
    root, scopes = m.schema(relative)
    source = m.INSTANCE.read_bytes()
    packet = load(PACKET)
    packet_contexts = {r["id"]: r for r in packet["contexts"]}
    portable = load(PORTABLE)
    portable_contexts = {r["body"]["xml_id"]: r["body"] for r in portable if r["kind"] == "XbrlContextEvidence"}
    records = []
    for context in root.findall(X + "context"):
        for container_name in ("segment", "scenario"):
            container = context.find(X + "entity/" + X + "segment") if container_name == "segment" else context.find(X + "scenario")
            if container is None:
                continue
            for node in container:
                if node.tag != I + "typedMember":
                    continue
                ident = context.get("id")
                candidate = typed_value(node, scopes, declaration)
                assert candidate["status"] == "supported", ident
                pc = packet_contexts[ident]
                p.span_check(pc["span"], source)
                members = [x for x in pc["dimensions_and_qualifiers"] if x["reading"]["name"] == I + "typedMember"]
                assert len(members) == 1 and members[0]["container"] == container_name
                original = members[0]["reading"]
                assert original["attributes"] == node.attrib and original["text"] == node.text
                assert len(original["children"]) == 1
                assert original["children"][0] == {"name": node[0].tag, "attributes": node[0].attrib,
                    "text": node[0].text, "children": [], "tail": node[0].tail}
                values = [x for x in portable_contexts[ident]["dimensions"] if x["form"] == "typed"]
                assert len(values) == 1
                frozen = values[0]
                assert frozen["container"] == container_name
                assert frozen["axis_token"] == node.get("dimension")
                assert frozen["axis_qname"] == {"namespace_uri": "http://fasb.org/us-gaap/2024", "local_name": AXIS_LOCAL}
                assert frozen["member_token"] is None and frozen["member_qname"]["tag"] == "Unknown"
                span = frozen["source_span"]
                raw = source[span["byte_start"]:span["byte_end"]]
                wrapper = '<w xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:us-gaap="http://fasb.org/us-gaap/2024">' + raw.decode() + "</w>"
                parsed, fragment_scopes = parse_fixture(wrapper)
                assert len(parsed) == 1 and typed_value(parsed[0], fragment_scopes, declaration) == candidate
                facts = [f for f in packet["facts"] if f["source_context_id"] == ident]
                assert all(f["financial_context"]["financial_time"]["tag"] == "Unknown" for f in facts)
                original_date = candidate["date"]["value"]
                direct_date = "%04d-%02d-%02d" % tuple(original_date[k] for k in ("year", "month", "day"))
                wrong_role = p.boundary(node[0].text, "instant")
                assert wrong_role["implied_boundary"][:10] != direct_date
                records.append({"context_id": ident, "container": container_name,
                    "source_context_span": pc["span"],
                    "typed_member_span": span | {"slice_sha256": digest(raw), "raw_utf8": raw.decode()},
                    "source_tree": original, "portable_dimension_unchanged": frozen,
                    "interpretation": candidate,
                    "facts": [{"fact_id": f["id"], "concept": f["expanded_concept"]} for f in facts],
                    "role_discriminator": {"schema_calendar_date": direct_date,
                        "same_token_as_xbrli_instant": wrong_role["implied_boundary"],
                        "second_interpretation_applies_to_actual_typed_value": False},
                    "dimensional_hypercube_validity": "not_run"})
    assert len(records) == 4 and sum(len(r["facts"]) for r in records) == 8
    return declaration, records


def check():
    count = 0
    def require(condition, label):
        nonlocal count
        assert condition, label
        count += 1
    ledger = load(U / "source-ledger.json")
    for binding in ledger["bindings"]:
        require(bind(R / binding["path"]) == binding, binding["path"])
    for a in ledger["anchors"]:
        path = R / a["source"]["path"]
        require(bind(path) == a["source"], a["id"])
        require("\n".join(path.read_text().splitlines()[a["first_line"]-1:a["last_line"]]) == a["excerpt"], a["id"])
    declaration, rows = derive()
    require(declaration == load(U / "declarations.json"), "exact declaration record")
    require(rows == load(U / "occurrences.json"), "four exact records")
    fixtures = load(U / "fixtures.json")
    for fixture in fixtures:
        node, scopes = parse_fixture(fixture["xml"])
        result = typed_value(node, scopes, declaration)
        require(result["status"] == fixture["expected_status"], fixture["id"])
        if "expected_date" in fixture:
            require(result["date"]["normalized"] == fixture["expected_date"], fixture["id"] + " date")
    index = global_index()
    controls = load(U / "declaration-controls.json")
    for control in controls:
        # Re-copy only the selected schema tree and rebuild its namespace maps.
        resource, root, scopes, axis = index[AXIS][0]
        changed = deepcopy(root)
        remapped = {id(new): scopes[id(old)] for old, new in zip(root.iter(), changed.iter())}
        axis_copy = next(e for e in changed if e.get("name") == AXIS_LOCAL)
        domain_copy = next(e for e in changed if e.get("name") == AXIS_LOCAL + ".domain")
        target = axis_copy if control["target"] == "axis" else domain_copy
        if control.get("duplicate"):
            changed.append(deepcopy(domain_copy))
        else:
            target.set(control["attribute"], control["value"])
        altered = {AXIS: [(resource, changed, remapped, axis_copy)],
                   DOMAIN: [(resource, changed, remapped, domain_copy)]}
        try:
            declared(altered)
        except (AssertionError, KeyError, TypeError):
            require(True, control["id"])
        else:
            raise AssertionError("unsupported declaration accepted: " + control["id"])
    return {"assertions": count, "typed_occurrences": len(rows),
            "fact_context_joins": sum(len(r["facts"]) for r in rows),
            "axis_declarations": 1, "domain_declarations": 1, "resources_inspected": len(load(MAP)),
            "fixtures": len(fixtures), "declaration_changes_rejected": len(controls),
            "source_anchors": len(ledger["anchors"]), "input_bindings": len(ledger["bindings"]),
            "new_acquisitions": 0, "upstream_executed": False,
            "schema_validation": "not_run", "hypercube_validation": "not_run", "whole_rows_closed": 0}
