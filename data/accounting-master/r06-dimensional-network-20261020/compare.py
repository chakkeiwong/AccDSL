"""Finite retained-source relationship reconstruction, not a schema validator."""
from collections import Counter, defaultdict
from fractions import Fraction
import importlib.util
from pathlib import Path
import re
from urllib.parse import urljoin, urldefrag, urlparse

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"
spec = importlib.util.spec_from_file_location("dimension_source_helpers", B / "r06-numeric-lexical-20261020/compare.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
load, bind = m.load, m.bind
XS = m.XS
XL = "{http://www.w3.org/1999/xlink}"
LINK = "{http://www.xbrl.org/2003/linkbase}"
XBRLI = "{http://www.xbrl.org/2003/instance}"
DT = "{http://xbrl.org/2005/xbrldt}"
XML = "{http://www.w3.org/XML/1998/namespace}"
AR = "http://xbrl.org/int/dim/arcrole/"
MAP = B / "native-offline-resolution-20261018/resource-map.json"
NEXT = {"all": "hypercube-dimension", "notAll": "hypercube-dimension",
        "hypercube-dimension": "dimension-domain",
        "dimension-domain": "domain-member", "domain-member": "domain-member"}


def boolean(raw):
    value = m.collapse(raw)
    assert value in ("true", "false", "1", "0"), ("boolean", raw)
    return value in ("true", "1")


def attributes(raw):
    allowed = {XL+k for k in ("type", "arcrole", "from", "to", "title", "show", "actuate")}
    allowed |= {"order", "use", "priority", DT+"closed", DT+"usable", DT+"contextElement", DT+"targetRole"}
    assert set(raw) <= allowed, ("unreviewed attribute", set(raw)-allowed)
    assert raw[XL+"type"] == "arc"
    arcrole = raw[XL+"arcrole"]
    assert arcrole.startswith(AR) and arcrole[len(AR):] in set(NEXT) | {"dimension-default"}
    use = m.collapse(raw.get("use", "optional"))
    assert use in ("optional", "prohibited")
    priority = m.collapse(raw.get("priority", "0"))
    assert re.fullmatch(r"[+-]?[0-9]+", priority)
    nonexempt = {}
    for key, raw_value in raw.items():
        if key.startswith(XL) or key in ("use", "priority"):
            continue
        value = m.collapse(raw_value)
        if key == "order":
            assert re.fullmatch(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)", value)
            number = Fraction(value)
            # Actual retained orders are integers 0..690. Restrict numerical
            # equivalence to exact binary64 integers, avoiding an invented
            # arbitrary-precision XPath 1.0 numeric comparison.
            assert number.denominator == 1 and abs(number) <= 2**53, "order outside reviewed X-Equal profile"
            nonexempt[key] = str(number.numerator)
        elif key in (DT+"closed", DT+"usable"):
            nonexempt[key] = boolean(value)
        elif key == DT+"contextElement":
            assert value in ("segment", "scenario")
            nonexempt[key] = value
        else:
            assert key == DT+"targetRole" and urlparse(value).scheme, "targetRole must be absolute"
            nonexempt[key] = value
    short = arcrole[len(AR):]
    if DT+"targetRole" in raw:
        assert short in NEXT, "default arcs have no targetRole semantics"
    if DT+"closed" in raw or DT+"contextElement" in raw:
        assert short in ("all", "notAll")
    if DT+"usable" in raw:
        assert short in ("dimension-domain", "domain-member")
    if short in ("all", "notAll"):
        assert DT+"contextElement" in raw
    return {"arcrole": short, "priority": int(priority), "use": use,
            "nonexempt_attributes": nonexempt,
            "target_role": nonexempt.get(DT+"targetRole"),
            "usable": nonexempt.get(DT+"usable", True),
            "closed": nonexempt.get(DT+"closed", False),
            "context_element": nonexempt.get(DT+"contextElement")}


def equivalence_key(arc):
    p = arc["interpreted"]
    return (arc["link_name"], arc["role"], arc["arc_name"], p["arcrole"],
            arc["source_node"], arc["target_node"],
            tuple(sorted(p["nonexempt_attributes"].items())))


def effective(arcs):
    groups = defaultdict(list)
    for arc in arcs:
        groups[equivalence_key(arc)].append(arc)
    records, selected = [], []
    for members in groups.values():
        highest = max(a["interpreted"]["priority"] for a in members)
        top = [a for a in members if a["interpreted"]["priority"] == highest]
        prohibited = any(a["interpreted"]["use"] == "prohibited" for a in top)
        chosen = None if prohibited else min(top, key=lambda a: a["id"])
        records.append({"members": [a["id"] for a in members], "highest_priority": highest,
                        "highest_members": [a["id"] for a in top],
                        "prohibited": prohibited, "selected": chosen["id"] if chosen else None})
        if chosen:
            selected.append(chosen)
    return records, selected


def following(arcs, arc):
    p = arc["interpreted"]
    if p["arcrole"] not in NEXT:
        return []
    role = p["target_role"] or arc["role"]
    return [a for a in arcs if a["role"] == role and a["source_node"] == arc["target_node"]
            and a["interpreted"]["arcrole"] == NEXT[p["arcrole"]]]


def consecutive(arcs, head):
    seen, pending = {}, [head]
    while pending:
        a = pending.pop()
        if a["id"] in seen:
            continue
        seen[a["id"]] = a
        pending.extend(following(arcs, a))
    return [seen[k] for k in sorted(seen)]


def directed_cycle(arcs):
    graph = defaultdict(set)
    for a in arcs:
        graph[a["source_node"]].add(a["target_node"])
    active, done = set(), set()
    def visit(node):
        if node in active:
            return True
        if node in done:
            return False
        active.add(node)
        if any(visit(child) for child in sorted(graph.get(node, ()))):
            return True
        active.remove(node)
        done.add(node)
        return False
    return any(visit(node) for node in sorted(graph))


def dimension_domain(arcs, axis, role):
    roots = [a for a in arcs if a["source_node"] == axis and a["role"] == role
             and a["interpreted"]["arcrole"] == "dimension-domain"]
    evidence = defaultdict(list)
    for root in roots:
        for a in consecutive(arcs, root):
            evidence[a["target_node"]].append({"arc": a["id"], "usable": a["interpreted"]["usable"]})
    return {"axis": axis, "role": role, "roots": [a["id"] for a in roots],
            "members": dict(sorted(evidence.items())),
            "valid_members": sorted(n for n, v in evidence.items() if all(a["usable"] for a in v)),
            "excluded_members": sorted(n for n, v in evidence.items() if not all(a["usable"] for a in v))}


def derive():
    resources = load(MAP)
    roots, all_ids, declarations, roles = {}, {}, {}, {}
    for resource in resources:
        path = R / resource["retained_path"]
        assert m.digest(path.read_bytes()) == resource["expected_blob"]["digest"]
        assert path.stat().st_size == resource["expected_blob"]["byte_length"]
        root, scopes = m.schema(resource["retained_path"])
        assert not any(XML+"base" in e.attrib for e in root.iter()), "XML Base outside retained profile"
        uri = resource["logical_uri"]
        parent = {id(c): p for p in root.iter() for c in p}
        roots[uri] = (resource, root, scopes, parent)
        for e in root.iter():
            if e.get("id"):
                ident = uri+"#"+e.get("id")
                assert ident not in all_ids
                all_ids[ident] = (e, scopes[id(e)])
        if root.tag == XS+"schema":
            ns = root.get("targetNamespace")
            for e in root:
                if e.tag != XS+"element" or not e.get("id"):
                    continue
                ident = uri+"#"+e.get("id")
                declarations[ident] = {
                    "node": ident, "qname": "{"+ns+"}"+e.get("name"),
                    "source_file": resource["retained_path"], "attributes": dict(e.attrib),
                    "substitution_group": m.expanded(e.get("substitutionGroup"), scopes[id(e)])
                    if e.get("substitutionGroup") else None}
        for e in root.iter(LINK+"roleType"):
            roles[uri+"#"+e.get("id")] = {"role": e.get("roleURI"),
                "used_on": [m.expanded(c.text.strip(), scopes[id(c)]) for c in e if c.tag == LINK+"usedOn"]}
    def resolve(uri, href):
        base, frag = urldefrag(urljoin(uri, href))
        assert frag and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_.-]*", frag), ("unreviewed locator", href)
        ident = base+"#"+frag
        assert ident in all_ids, ("unresolved", ident)
        return ident
    arcs, links, transitions = [], [], []
    for uri, (resource, root, scopes, parent) in roots.items():
        for li, link in enumerate(root.iter(LINK+"definitionLink")):
            assert link.get(XL+"type") == "extended"
            role = link.get(XL+"role")
            ancestor = parent[id(link)]
            assert ancestor.tag == LINK+"linkbase"
            role_refs = defaultdict(list)
            for ref in ancestor:
                if ref.tag == LINK+"roleRef":
                    role_refs[ref.get("roleURI")].append(resolve(uri, ref.get(XL+"href")))
            labels = defaultdict(list)
            for child in link:
                if child.tag == LINK+"loc":
                    assert child.get(XL+"type") == "locator"
                    labels[child.get(XL+"label")].append(resolve(uri, child.get(XL+"href")))
            assert all(len(nodes) == 1 for nodes in labels.values()), "multi-locator label outside retained profile"
            ids = []
            for ci, child in enumerate(link):
                if child.tag != LINK+"definitionArc":
                    continue
                p = attributes(dict(child.attrib))
                source = labels[child.get(XL+"from")][0]
                target = labels[child.get(XL+"to")][0]
                assert source in declarations and target in declarations
                a = {"id": "arc-%04d" % (len(arcs)+1), "source_file": resource["retained_path"],
                     "logical_uri": uri, "link_index": li, "child_index": ci,
                     "link_name": link.tag, "arc_name": child.tag, "role": role,
                     "source_node": source, "target_node": target,
                     "source_qname": declarations[source]["qname"], "target_qname": declarations[target]["qname"],
                     "raw_attributes": dict(child.attrib), "interpreted": p}
                s, t = declarations[source], declarations[target]
                sg, tg, kind = s["substitution_group"], t["substitution_group"], p["arcrole"]
                allowed_categories = {
                    "all": (XBRLI+"item", DT+"hypercubeItem"), "notAll": (XBRLI+"item", DT+"hypercubeItem"),
                    "hypercube-dimension": (DT+"hypercubeItem", DT+"dimensionItem"),
                    "dimension-domain": (DT+"dimensionItem", XBRLI+"item"),
                    "dimension-default": (DT+"dimensionItem", XBRLI+"item"),
                    "domain-member": (XBRLI+"item", XBRLI+"item")}
                assert (sg, tg) == allowed_categories[kind], ("endpoint category", a["id"])
                for d in (s, t):
                    if d["substitution_group"] in (DT+"dimensionItem", DT+"hypercubeItem"):
                        assert boolean(d["attributes"]["abstract"])
                if kind in ("dimension-default", "dimension-domain"):
                    assert DT+"typedDomainRef" not in s["attributes"], "explicit dimension required"
                if p["target_role"]:
                    tr = p["target_role"]
                    matches = role_refs[tr]
                    assert len(matches) == 1 and matches[0] in roles, ("targetRole ref", tr)
                    declaration = roles[matches[0]]
                    assert declaration["role"] == tr and LINK+"definitionLink" in declaration["used_on"]
                    transitions.append({"arc": a["id"], "source_role": role, "target_role": tr,
                                        "role_declaration": matches[0]})
                arcs.append(a)
                ids.append(a["id"])
            links.append({"source_file": resource["retained_path"], "link_index": li,
                          "role": role, "arcs": ids})
    groups, selected = effective(arcs)
    endpoint_groups = defaultdict(list)
    for a in arcs:
        endpoint_groups[equivalence_key(a)[:-1]].append(a["id"])
    drs = []
    for a in selected:
        if a["interpreted"]["arcrole"] in ("all", "notAll"):
            members = consecutive(selected, a)
            drs.append({"head": a["id"], "role": a["role"], "arcs": [x["id"] for x in members],
                        "directed_cycle": directed_cycle(members)})
    base_sets = defaultdict(list)
    for a in selected:
        base_sets[(a["role"], a["interpreted"]["arcrole"])].append(a)
    cycles = [{"role": role, "arcrole": kind, "directed_cycle": directed_cycle(rows)}
              for (role, kind), rows in sorted(base_sets.items())]
    default_members = defaultdict(set)
    for a in selected:
        if a["interpreted"]["arcrole"] == "dimension-default":
            default_members[a["source_node"]].add(a["target_node"])
    domains = [dimension_domain(selected, axis, role) for axis, role in sorted({
        (a["source_node"], a["role"]) for a in selected if a["interpreted"]["arcrole"] == "dimension-domain"})]
    for t in transitions:
        a = next(x for x in selected if x["id"] == t["arc"])
        t["next_arcs"] = [x["id"] for x in following(selected, a)]
    used = {a[k] for a in arcs for k in ("source_node", "target_node")}
    return {"resources": len(resources), "links": links, "raw_arcs": arcs,
            "same_base_and_endpoint_groups": [v for v in endpoint_groups.values() if len(v)>1],
            "equivalence_groups": groups, "effective_arc_ids": [a["id"] for a in selected],
            "target_role_transitions": transitions, "consecutive_sets": drs,
            "base_set_directed_cycles": cycles, "dimension_domains": domains,
            "global_defaults": {k: sorted(v) for k,v in sorted(default_members.items())},
            "endpoint_declarations": {n: declarations[n] for n in sorted(used)},
            "full_schema_validation": "not_run", "installed_DTS_correspondence": "not_checked"}


def fixture_arc(ident, source="P", target="Q", role="urn:r", kind="domain-member", **extra):
    raw = {XL+"type": "arc", XL+"arcrole": AR+kind, XL+"from": "from", XL+"to": "to", "order": "1"}
    raw.update(extra)
    return {"id": ident, "link_name": LINK+"definitionLink", "arc_name": LINK+"definitionArc",
            "role": role, "source_node": source, "target_node": target,
            "interpreted": attributes(raw), "raw_attributes": raw}


def fixture_checks():
    outcomes = []
    def expect(name, truth):
        assert truth, name
        outcomes.append(name)
    a = fixture_arc("a")
    for name, b, wanted in [
        ("higher_optional", fixture_arc("b", priority="2"), ["b"]),
        ("higher_prohibited", fixture_arc("b", priority="2", use="prohibited"), []),
        ("lower_prohibition", fixture_arc("b", priority="-1", use="prohibited"), ["a"]),
        ("tied_prohibition", fixture_arc("b", use="prohibited"), []),
        ("tied_optional", fixture_arc("b"), ["a"]),
        ("decimal_equivalence", fixture_arc("b", order="1.0"), ["a"]),
        ("different_order", fixture_arc("b", order="2"), ["a", "b"]),
        ("different_role", fixture_arc("b", role="urn:s"), ["a", "b"]),
        ("different_node", fixture_arc("b", target="other#Q"), ["a", "b"]),
    ]:
        expect(name, [x["id"] for x in effective([a,b])[1]] == wanted)
    high = fixture_arc("c", priority="3")
    expect("higher_optional_overrides_prohibition",
           [x["id"] for x in effective([a, fixture_arc("b", priority="2", use="prohibited"), high])[1]] == ["c"])
    absent = fixture_arc("z")
    del absent["raw_attributes"]["order"]
    absent["interpreted"] = attributes(absent["raw_attributes"])
    expect("absent_order_preserved", equivalence_key(a) != equivalence_key(absent))
    yes = fixture_arc("yes", **{DT+"usable":"true"})
    one = fixture_arc("one", **{DT+"usable":"1"})
    expect("boolean_value_equivalence", equivalence_key(yes) == equivalence_key(one))
    switch = fixture_arc("switch", target="A", **{DT+"targetRole": "urn:s"})
    same = fixture_arc("same", source="A", target="WRONG")
    right = fixture_arc("right", source="A", target="RIGHT", role="urn:s")
    expect("target_role_switch", [x["id"] for x in following([switch,same,right], switch)] == ["right"])
    no_switch = fixture_arc("no", target="A")
    expect("same_role_without_switch", [x["id"] for x in following([no_switch,same,right], no_switch)] == ["same"])
    root = fixture_arc("domain", source="D", target="A", kind="dimension-domain", **{DT+"usable": "false"})
    child = fixture_arc("child", source="A", target="B")
    expect("unusable_parent_does_not_prune_child", dimension_domain([root,child], "D", "urn:r")["valid_members"] == ["B"])
    other = fixture_arc("other", source="D", target="A", kind="dimension-domain", order="2")
    expect("false_path_vetoes_true_path", dimension_domain([root,child,other], "D", "urn:r")["excluded_members"] == ["A"])
    default = fixture_arc("default", source="D", target="M", kind="dimension-default")
    expect("default_does_not_add_member", dimension_domain([root,child,default], "D", "urn:r")["valid_members"] == ["B"])
    expect("directed_cycle_detected", directed_cycle([a, fixture_arc("back", source="Q", target="P")]))
    expect("diamond_is_not_directed_cycle", not directed_cycle([
        a, fixture_arc("b", target="R"), fixture_arc("c", source="Q", target="S"),
        fixture_arc("d", source="R", target="S")]))
    for name, extra in [("unknown_attribute", {"invented":"true"}), ("bad_boolean", {DT+"usable":"yes"}),
                        ("relative_target_role", {DT+"targetRole":"role/local"}), ("fractional_order_outside_profile", {"order":"0.1"}),
                        ("bad_priority", {"priority":"1.5"}), ("bad_use", {"use":"required"})]:
        try:
            fixture_arc("bad", **extra)
        except AssertionError:
            expect(name, True)
        else:
            raise AssertionError(name)
    return outcomes


def check():
    ledger = load(U / "source-ledger.json")
    assertions = 0
    for b in ledger["bindings"]:
        assert bind(R / b["path"]) == b
        assertions += 1
    for a in ledger["anchors"]:
        path = R / a["source"]["path"]
        assert bind(path) == a["source"]
        assert "\n".join(path.read_text().splitlines()[a["first_line"]-1:a["last_line"]]) == a["excerpt"]
        assertions += 2
    network = derive()
    assert network == load(U / "network.json")
    cases = fixture_checks()
    assert cases == load(U / "fixture-results.json")
    assertions += len(cases)+2
    assert not any(r["directed_cycle"] for r in network["consecutive_sets"])
    assert not any(r["directed_cycle"] for r in network["base_set_directed_cycles"])
    assert all(len(v) == 1 for v in network["global_defaults"].values())
    assertions += 3
    return {"assertions": assertions, "resources": network["resources"], "definition_links": len(network["links"]),
            "raw_arcs": len(network["raw_arcs"]), "effective_arcs": len(network["effective_arc_ids"]),
            "equivalence_groups": len(network["equivalence_groups"]),
            "nontrivial_equivalence_groups": sum(len(g["members"])>1 for g in network["equivalence_groups"]),
            "target_role_transitions": len(network["target_role_transitions"]),
            "consecutive_sets": len(network["consecutive_sets"]), "base_sets": len(network["base_set_directed_cycles"]),
            "dimension_domains": len(network["dimension_domains"]), "global_default_dimensions": len(network["global_defaults"]),
            "fixture_checks": len(cases), "source_anchors": len(ledger["anchors"]),
            "input_bindings": len(ledger["bindings"]), "new_acquisitions": 0,
            "upstream_executed": False, "full_schema_validation": "not_run",
            "financial_admission": False, "whole_rows_closed": 0}
