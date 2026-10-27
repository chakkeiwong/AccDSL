"""Source-bound dimensional applicability; no installed or generic schema claim."""
from collections import Counter, defaultdict, deque
from copy import deepcopy
import importlib.util
from pathlib import Path

U = Path(__file__).resolve().parent
R = U.parents[2]
B = R / "data/accounting-master"


def imported(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


n = imported("fact_dimension_network", B / "r06-dimensional-network-20261020/compare.py")
t = imported("fact_typed_dates", B / "r06-typed-domain-dates-20261020/compare.py")
m = n.m
load, bind = m.load, m.bind
X, DT, DI = n.XBRLI, n.DT, "{http://xbrl.org/2006/xbrldi}"
NETWORK = B / "r06-dimensional-network-20261020/network.json"
TYPED = B / "r06-typed-domain-dates-20261020/occurrences.json"


def inherited(arcs, head):
    """Reach primary descendants, keeping the original has-hypercube separate."""
    start = (head["source_node"], head["role"])
    paths, pending = {start: []}, deque([start])
    while pending:
        source, role = pending.popleft()
        for a in arcs:
            if (a["source_node"], a["role"], a["interpreted"]["arcrole"]) != (source, role, "domain-member"):
                continue
            state = (a["target_node"], a["interpreted"]["target_role"] or role)
            if state not in paths:
                paths[state] = paths[(source, role)] + [a["id"]]
                pending.append(state)
    return [{"primary_node": node, "inheritance_end_role": role, "path": path,
             "origin_role": head["role"], "has_hypercube": head["id"]}
            for (node, role), path in sorted(paths.items())]


def domain_with_paths(arcs, axis, role):
    domain = n.dimension_domain(arcs, axis, role)
    queue = deque((a, [a["id"]]) for a in arcs if a["source_node"] == axis
                  and a["role"] == role and a["interpreted"]["arcrole"] == "dimension-domain")
    seen, paths = set(), {}
    while queue:
        arc, path = queue.popleft()
        if arc["id"] in seen:
            continue
        seen.add(arc["id"])
        paths.setdefault(arc["target_node"], path)
        for next_arc in n.following(arcs, arc):
            queue.append((next_arc, path+[next_arc["id"]]))
    domain["member_paths"] = paths
    return domain


def cube_profile(arcs, head, declarations, defaults):
    dimensions = []
    for hd in n.following(arcs, head):
        axis = hd["target_node"]
        decl = declarations[axis]
        role = hd["interpreted"]["target_role"] or hd["role"]
        typed = DT+"typedDomainRef" in decl["attributes"]
        domain = None if typed else domain_with_paths(arcs, axis, role)
        dimensions.append({"axis": axis, "qname": decl["qname"], "hypercube_dimension_arc": hd["id"],
                           "domain_role": role, "kind": "typed" if typed else "explicit",
                           "domain": domain, "default": defaults.get(axis)})
    assert len({d["axis"] for d in dimensions}) == len(dimensions), "multiple axis paths outside current profile"
    return {"has_hypercube": head["id"], "cube": head["target_node"], "origin_role": head["role"],
            "compositor": head["interpreted"]["arcrole"], "closed": head["interpreted"]["closed"],
            "container": head["interpreted"]["context_element"], "dimensions": dimensions}


def context_errors(dimensions, defaults):
    errors = []
    axes = [d["axis"] for d in dimensions]
    if len(axes) != len(set(axes)):
        errors.append("RepeatedDimensionInInstanceError")
    for d in dimensions:
        if d["kind"] == "explicit" and d["member"] == defaults.get(d["axis"]):
            errors.append("DefaultValueUsedInInstanceError")
    return errors


def evaluate_cube(profile, dimensions, closure="selected_container"):
    selected = [d for d in dimensions if d["container"] == profile["container"]]
    supplied = {d["axis"]: d for d in selected}
    expected = {d["axis"] for d in profile["dimensions"]}
    closed_inputs = selected if closure == "selected_container" else dimensions
    unexpected = sorted({d["axis"] for d in closed_inputs}-expected) if profile["closed"] else []
    results = []
    for d in profile["dimensions"]:
        observation = supplied.get(d["axis"])
        if d["kind"] == "typed":
            supported = bool(observation and observation["kind"] == "typed" and observation["typed_content_supported"])
            results.append({"axis": d["axis"], "kind": "typed", "supported": supported,
                            "value_source": "reported" if observation else "missing",
                            "typed_scope": "finite reviewed date content; full schema not_run"})
            continue
        member = observation.get("member") if observation and observation["kind"] == "explicit" else (
            d["default"] if observation is None else None)
        supported = member is not None and member in d["domain"]["valid_members"]
        results.append({"axis": d["axis"], "kind": "explicit", "member": member,
                        "value_source": "reported" if observation else ("default" if member else "missing"),
                        "supported": supported,
                        "membership_path": d["domain"]["member_paths"].get(member) if supported else None})
    valid = not unexpected and all(d["supported"] for d in results)
    return {"has_hypercube": profile["has_hypercube"], "container": profile["container"],
            "closed": profile["closed"], "unexpected_dimensions": unexpected,
            "dimension_checks": results, "hypercube_valid_under_scoped_rules": valid,
            "compositor": profile["compositor"],
            "relation_satisfied": valid if profile["compositor"] == "all" else not valid}


def combine(role_checks):
    return {role: all(c["relation_satisfied"] for c in checks) for role, checks in role_checks.items()}


def derive():
    network = load(NETWORK)
    assert network == n.derive(), "frozen network replay"
    arcs = [a for a in network["raw_arcs"] if a["id"] in set(network["effective_arc_ids"])]
    defaults = {k: v[0] for k,v in network["global_defaults"].items()}
    index = t.global_index()
    declarations, nodes = {}, {}
    for qname, values in index.items():
        assert len(values) == 1, ("ambiguous declaration", qname)
        resource, root, scopes, element = values[0]
        if not element.get("id"):
            continue
        node = resource["logical_uri"]+"#"+element.get("id")
        nodes[qname] = node
        declarations[node] = {"qname": qname, "attributes": dict(element.attrib),
                             "substitution_group": m.expanded(element.get("substitutionGroup"), scopes[id(element)])
                             if element.get("substitutionGroup") else None}
    source_root, scopes = m.schema(str(m.INSTANCE.relative_to(R)))
    source_bytes = m.INSTANCE.read_bytes()
    packet = load(t.PACKET)
    packet_contexts = {c["id"]: c for c in packet["contexts"]}
    portable_contexts = {r["body"]["xml_id"]:r["body"] for r in load(t.PORTABLE) if r["kind"]=="XbrlContextEvidence"}
    typed_rows = {r["context_id"]: r for r in load(TYPED)}
    typed_declaration = t.declared(index)
    contexts = []
    for context in source_root.findall(X+"context"):
        ident = context.get("id")
        original = packet_contexts[ident]
        portable = portable_contexts[ident]
        t.p.span_check(original["span"], source_bytes)
        dimensions, qualifiers, containers = [], [], []
        for cname in ("segment", "scenario"):
            container = context.find(X+"entity/"+X+"segment") if cname=="segment" else context.find(X+"scenario")
            if container is None:
                continue
            containers.append(cname)
            for child in container:
                if child.tag not in (DI+"explicitMember", DI+"typedMember"):
                    qualifiers.append({"container": cname, "tag": child.tag})
                    continue
                kind = "explicit" if child.tag == DI+"explicitMember" else "typed"
                assert set(child.attrib) == {"dimension"}
                axis_token = child.get("dimension")
                axis_qname = m.expanded(m.collapse(axis_token), scopes[id(child)])
                axis = nodes[axis_qname]
                decl = declarations[axis]
                assert decl["substitution_group"] == DT+"dimensionItem" and n.boolean(decl["attributes"]["abstract"])
                assert (DT+"typedDomainRef" in decl["attributes"]) == (kind=="typed")
                d = {"container": cname, "kind": kind, "axis_token": axis_token,
                     "axis_qname": axis_qname, "axis": axis}
                if kind == "explicit":
                    assert len(child)==0
                    member_token = child.text
                    member_qname = m.expanded(m.collapse(member_token), scopes[id(child)])
                    member = nodes[member_qname]
                    assert declarations[member]["substitution_group"] == X+"item"
                    d.update(member_token=member_token, member_qname=member_qname, member=member)
                else:
                    checked = t.typed_value(child, scopes, typed_declaration)
                    assert checked == typed_rows[ident]["interpretation"] and checked["status"]=="supported"
                    d.update(member=None, member_token=None, member_qname=None,
                             typed_content_supported=True, typed_evidence_context=ident)
                dimensions.append(d)
        assert not qualifiers, "non-dimensional qualifiers outside current context profile"
        assert len(dimensions) == len(original["dimensions_and_qualifiers"]) == len(portable["dimensions"])
        for d, frozen in zip(dimensions, portable["dimensions"]):
            assert (d["container"],d["kind"],d["axis_token"]) == (frozen["container"],frozen["form"],frozen["axis_token"])
            assert frozen["axis_qname"] == {"namespace_uri":d["axis_qname"][1:].split("}")[0],
                                           "local_name":d["axis_qname"].split("}")[1]}
            if d["kind"] == "explicit":
                assert frozen["member_token"] == d["member_token"]
                assert frozen["member_qname"] == {"namespace_uri":d["member_qname"][1:].split("}")[0],
                                                  "local_name":d["member_qname"].split("}")[1]}
            else:
                assert frozen["member_token"] is None and frozen["member_qname"]["tag"] == "Unknown"
        contexts.append({"context_id":ident,"source_span":original["span"],"containers":containers,
                         "dimensions":dimensions, "qualifiers":qualifiers,
                         "context_rule_errors":context_errors(dimensions, defaults)})
    by_context = {c["context_id"]:c for c in contexts}
    heads = [a for a in arcs if a["interpreted"]["arcrole"] in ("all","notAll")]
    profiles = {a["id"]:cube_profile(arcs,a,declarations,defaults) for a in heads}
    applications, inheritance_records = defaultdict(dict), []
    for head in heads:
        witnesses = inherited(arcs, head)
        inheritance_records.append({"has_hypercube":head["id"],"primary_paths":witnesses})
        for w in witnesses:
            applications[w["primary_node"]].setdefault(head["id"], w)
    facts, polymorphism = [], []
    for row in load(m.COVERAGE)["occurrences"]:
        ident, qname = row["fact_id"], row["source_concept"]
        node = nodes[qname]
        context = by_context[row["source_context_id"]]
        applied, roles, both_roles = [], defaultdict(list), defaultdict(list)
        for head_id, witness in sorted(applications[node].items()):
            profile = profiles[head_id]
            checks = evaluate_cube(profile, context["dimensions"])
            both = evaluate_cube(profile, context["dimensions"], "both_containers")
            assert checks == both, ("closure ambiguity affects actual fact", ident, head_id)
            for d in profile["dimensions"]:
                if d["domain"] and node in d["domain"]["valid_members"]:
                    polymorphism.append({"fact_id":ident,"has_hypercube":head_id,"axis":d["axis"]})
            roles[profile["origin_role"]].append(checks)
            both_roles[profile["origin_role"]].append(both)
            applied.append({"has_hypercube":head_id, "inheritance_path":witness["path"],
                            "inheritance_end_role":witness["inheritance_end_role"],
                            "origin_role":profile["origin_role"]})
        passes = combine(roles)
        errors = context["context_rule_errors"]
        status = ("context_rule_failure" if errors else "no_applicable_hypercube_in_retained_network"
                  if not passes else "passes_scoped_dimensional_rules" if any(passes.values())
                  else "fails_all_applicable_roles")
        facts.append({"fact_id":ident,"concept":qname,"declaration_node":node,
                      "context_id":context["context_id"], "applicable_hypercubes":applied,
                      "role_checks":dict(roles), "role_outcomes":passes, "status":status,
                      "closure_interpretations_agree":passes==combine(both_roles),
                      "financial_admission":False})
    assert len(contexts)==193 and len(facts)==1127
    return {"contexts":contexts,"cube_profiles":list(profiles.values()),
            "primary_inheritance":inheritance_records,"facts":facts,
            "primary_polymorphism_findings":polymorphism}


def fixture_checks():
    done = []
    def expect(name, value):
        assert value, name
        done.append(name)
    arc = n.fixture_arc
    head = arc("h", source="P", target="H", kind="all", **{DT+"contextElement":"segment"})
    forward = arc("pq", source="P", target="Q", **{DT+"targetRole":"urn:s"})
    next_arc = arc("qr", source="Q", target="R", role="urn:s")
    wrong = arc("wrong", source="Q", target="WRONG")
    paths = inherited([head,forward,next_arc,wrong],head)
    expect("role_directed_primary_inheritance", {p["primary_node"] for p in paths} == {"P","Q","R"})
    expect("origin_role_preserved", all(p["origin_role"]=="urn:r" for p in paths))
    expect("transitive_inheritance_path", next(p for p in paths if p["primary_node"]=="R")["path"]==["pq","qr"])
    dd = arc("d",source="D",target="M",kind="dimension-domain")
    foreign = arc("foreign",source="D",target="FOREIGN",kind="dimension-domain",role="urn:other")
    domain = domain_with_paths([dd,foreign],"D","urn:r")
    dimension = {"axis":"D","kind":"explicit","domain":domain,"default":"M"}
    profile = {"has_hypercube":"h","container":"segment","closed":True,"compositor":"all","dimensions":[dimension]}
    value = {"axis":"D","kind":"explicit","member":"M","container":"segment"}
    expect("valid_explicit_member",evaluate_cube(profile,[value])["relation_satisfied"])
    expect("foreign_role_member_rejected",not evaluate_cube(profile,[dict(value,member="FOREIGN")])["relation_satisfied"])
    expect("implicit_default",evaluate_cube(profile,[])["relation_satisfied"])
    expect("explicit_default_prohibited",context_errors([value],{"D":"M"})==["DefaultValueUsedInInstanceError"])
    expect("duplicate_across_containers",context_errors([value,dict(value,container="scenario")],{})==["RepeatedDimensionInInstanceError"])
    no_default=deepcopy(profile);no_default["dimensions"][0]["default"]=None
    expect("missing_required_dimension",not evaluate_cube(no_default,[])["relation_satisfied"])
    expect("wrong_container",not evaluate_cube(no_default,[dict(value,container="scenario")])["relation_satisfied"])
    extra={"axis":"E","kind":"explicit","member":"X","container":"segment"}
    expect("closed_rejects_extra",not evaluate_cube(profile,[value,extra])["relation_satisfied"])
    expect("open_allows_extra",evaluate_cube(dict(profile,closed=False),[value,extra])["relation_satisfied"])
    bad_default=deepcopy(profile);bad_default["dimensions"][0]["default"]="ABSENT"
    expect("default_not_in_domain",not evaluate_cube(bad_default,[])["relation_satisfied"])
    other_container=dict(extra,container="scenario")
    expect("closure_wording_discriminator", evaluate_cube(profile,[value,other_container])["relation_satisfied"]
           and not evaluate_cube(profile,[value,other_container],"both_containers")["relation_satisfied"])
    typed=deepcopy(profile);typed["dimensions"]=[{"axis":"T","kind":"typed"}]
    tv={"axis":"T","kind":"typed","typed_content_supported":True,"container":"segment"}
    expect("typed_missing_no_default",not evaluate_cube(typed,[])["relation_satisfied"])
    expect("typed_supported_content",evaluate_cube(typed,[tv])["relation_satisfied"])
    expect("typed_content_failure",not evaluate_cube(typed,[dict(tv,typed_content_supported=False)])["relation_satisfied"])
    expect("notAll_inverts_cube",not evaluate_cube(dict(profile,compositor="notAll"),[value])["relation_satisfied"])
    expect("notAll_invalid_cube_satisfies",evaluate_cube(dict(no_default,compositor="notAll"),[])["relation_satisfied"])
    role_checks={"one":[{"relation_satisfied":True},{"relation_satisfied":False}],"two":[{"relation_satisfied":True}]}
    expect("conjunction_within_role",combine(role_checks)=={"one":False,"two":True})
    expect("alternative_role_disjunction",any(combine(role_checks).values()))
    empty=dict(profile,dimensions=[])
    expect("closed_empty_cube",evaluate_cube(empty,[])["relation_satisfied"] and not evaluate_cube(empty,[value])["relation_satisfied"])
    expect("open_empty_cube",evaluate_cube(dict(empty,closed=False),[value])["relation_satisfied"])
    return done


def check():
    ledger=load(U/"source-ledger.json")
    count=0
    for b in ledger["bindings"]:
        assert bind(R/b["path"])==b
        count+=1
    for a in ledger["anchors"]:
        path=R/a["source"]["path"]
        assert bind(path)==a["source"]
        assert "\n".join(path.read_text().splitlines()[a["first_line"]-1:a["last_line"]])==a["excerpt"]
        count+=2
    result=derive()
    assert result==load(U/"dimensional-facts.json")
    fixtures=fixture_checks()
    assert fixtures==load(U/"fixture-results.json")
    count+=2+len(fixtures)
    assert not result["primary_polymorphism_findings"]
    assert all(not c["context_rule_errors"] for c in result["contexts"])
    assert all(f["status"] in ("passes_scoped_dimensional_rules","no_applicable_hypercube_in_retained_network") for f in result["facts"])
    count+=3
    statuses=Counter(f["status"] for f in result["facts"])
    return {"assertions":count,"contexts":len(result["contexts"]),"facts":len(result["facts"]),
            "explicit_occurrences":sum(d["kind"]=="explicit" for c in result["contexts"] for d in c["dimensions"]),
            "typed_occurrences":sum(d["kind"]=="typed" for c in result["contexts"] for d in c["dimensions"]),
            "fact_outcomes":dict(statuses),"cube_profiles":len(result["cube_profiles"]),
            "applicable_cube_evaluations":sum(len(f["applicable_hypercubes"]) for f in result["facts"]),
            "failed_alternative_roles":sum(not x for f in result["facts"] for x in f["role_outcomes"].values()),
            "fixture_checks":len(fixtures),"source_anchors":len(ledger["anchors"]),"input_bindings":len(ledger["bindings"]),
            "new_acquisitions":0,"upstream_executed":False,"full_schema_validation":"not_run",
            "installed_DTS_correspondence":"not_checked","financial_admission":False,"whole_rows_closed":0}
