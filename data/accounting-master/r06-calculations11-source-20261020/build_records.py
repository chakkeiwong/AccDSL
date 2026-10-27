"""One-time source contract construction; no actual report calculation."""
import importlib.util
import json
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
B=R/"data/accounting-master"


def write(name,value):
    with (U/name).open("x",encoding="utf-8") as handle:
        json.dump(value,handle,indent=2)
        handle.write("\n")


def main():
    assert not (U/"examples.json").exists(),"one-time construction"
    spec=importlib.util.spec_from_file_location("calc11_source_examples",U/"compare.py")
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    examples=m.examples()
    calc=U/"sources/02-calc11.visible.txt"
    oim=U/"sources/03-oim.visible.txt"
    xml=U/"sources/04-xbrlxml.visible.txt"
    history=U/"sources/01-history.visible.txt"
    status=U/"sources/06-status.visible.txt"
    sections=[
        ("release_history",history,18,44),
        ("calc2_development_status",status,16,28),
        ("error_classes_and_OIM_precondition",calc,115,178),
        ("separate_networks_optional_old_arc",calc,179,225),
        ("binding_order_and_interval_sums",calc,226,243),
        ("rounding_modes_closed_intervals",calc,244,285),
        ("truncation_and_excess_digits",calc,286,322),
        ("duplicate_rules_and_nil",calc,323,351),
        ("interval_arithmetic_and_schema_publication",calc,352,391),
        ("corrected_errata",calc,392,414),
        ("OIM_processor_and_datatypes",oim,237,280),
        ("OIM_facts_and_numeric_text_types",oim,299,325),
        ("OIM_dimensions_and_type_limits",oim,326,400),
        ("OIM_equality",oim,437,478),
        ("OIM_duplicate_classes",oim,490,528),
        ("XML_twelve_compatibility_constraints",xml,151,189),
        ("XML_custom_attributes_and_fact_mapping",xml,190,221),
        ("XML_dimension_mapping",xml,235,279),
        ("XML_footnote_mapping",xml,280,315),
    ]
    anchors=[{"id":ident,"source":m.bind(path),"first_line":start,"last_line":end,
        "excerpt":"\n".join(path.read_text().splitlines()[start-1:end])}
        for ident,path,start,end in sections]
    inputs=set((U/"sources").glob("*"))
    inputs.update([B/"r06-calculation-bindings-20261020/calculation-bindings.json",
        B/"r06-calculation-bindings-20261020/checks.json",
        B/"r06-duplicate-facts-20261020/duplicate-facts.json",
        B/"r06-dimensional-facts-20261020/checks.json",
        B/"r06-typed-domain-dates-20261020/checks.json",
        B/"r06-numeric-accuracy-20261020/checks.json",
        B/"r06-enumeration-domain-20261020/extract_visible.py"])
    write("examples.json",examples)
    write("source-ledger.json",{"date":"2026-10-20","bindings":[m.bind(p) for p in sorted(inputs)],
        "anchors":anchors,"selected_editions":{"calculations11":"2023-02-22 corrected2024-02-14",
        "OIM":"2021-10-13","xBRL-XML":"2021-10-13"},
        "scope":"Source interpretation and authored exact examples; no actual report Calc1.1 validation",
        "contextual_interpretation":"Section5.4 linked duplicate-facts definition has no interval rule; examples use OIM6.2 as indicated by surrounding text",
        "normative_schema":"publication route timed out; appendix copy not substituted"})
    receipts=sorted((U/"sources").glob("*.receipt.json"))
    write("acquisitions.json",{"attempts":[m.bind(p) for p in receipts],
        "successful":sum(m.load(p)["exit_code"]==0 for p in receipts),
        "failures":[{"receipt":m.bind(p),"source":m.load(p)["source"],"exit_code":m.load(p)["exit_code"]}
                    for p in receipts if m.load(p)["exit_code"]],
        "new_sources_requested":6,"one_time_attempts_preserved":True})
    rules=[
        {"topic":"networks","old":"2003 summation-item only","optional11":"2023 arcrole separate; optional old-arc mode keeps distinguishable old results","anchor":"separate_networks_optional_old_arc"},
        {"topic":"precondition","old":"Retained XML/context/unit identity","optional11":"xBRL-XML2.1 compatibility; non-tuple incompatibility warning stops Calc1.1","anchor":"error_classes_and_OIM_precondition"},
        {"topic":"duplicates","old":"Duplicate total/component prevents binding","optional11":"OIM dimension grouping; consistent duplicate interval intersection, inconsistent pair error","anchor":"duplicate_rules_and_nil"},
        {"topic":"rounding","old":"Round contributions, weight, sum, round to total decimals","optional11":"One report-wide mode; overlap of weighted sum interval and total interval","anchor":"binding_order_and_interval_sums"},
        {"topic":"ties","old":"Previously defined exact nearest/ties-even map","optional11":"Closed nearest intervals allow either tie direction; broader than odd ties-even inverse","anchor":"rounding_modes_closed_intervals"},
        {"topic":"excess digits","old":"Finite actual values were grid-aligned","optional11":"Binding-specific excessDigits blocks further consistency check","anchor":"truncation_and_excess_digits"},
        {"topic":"nil","old":"Nil values excluded from contributor binding","optional11":"All-nil point ignored; mixed nil/non-nil duplicate set inconsistent","anchor":"duplicate_rules_and_nil"},
        {"topic":"results","old":"110 consistent bindings,164 nonbindings frozen","optional11":"No actual report result; warnings, inconsistencies and taxonomy-invalid errors kept distinct","anchor":"error_classes_and_OIM_precondition"},
    ]
    write("rule-comparison.json",rules)
    prerequisites=[
        ("2.1.1","non-dimensional segment/scenario","Prior dimension inquiry found none in193 contexts","reuse_with_source_binding"),
        ("2.1.2","single dimensional container","Prior inquiry found all dimensions in segment, no scenario","reuse_with_source_binding"),
        ("2.1.3","complex typed dimensions","Four retained values share direct xs:date domain","reuse_with_source_binding"),
        ("2.1.4","tuples","All1127 prior facts direct root children; check entire source for tuple use","inspect_exact_source"),
        ("2.1.5","fraction concept types","Prior coverage terminal types exist; inspect all paths","inspect_exact_type_coverage"),
        ("2.1.6","footnote resource roles","Not checked in this unit","inspect_footnote_resources"),
        ("2.1.7","zero precision","Prior accuracy inquiry found no actual precision attributes","reuse_with_source_binding"),
        ("2.1.8","instance linkbaseRef","Not checked in this unit","inspect_exact_source"),
        ("2.1.9","non-discoverable roleRef/arcroleRef","Retained map is not itself an installed schemaRef-only DTS certificate","inspect_references_and_reachability"),
        ("2.1.10","unlinked footnotes","Not checked in this unit; source names xbrli:footnote while mapping uses link:footnote","inspect_both_wording_and_actual_source"),
        ("2.1.11","non-root xml:base","Earlier graph checked resources; bind direct instance evidence","inspect_exact_source"),
        ("2.1.12","typed-dimension legacy types/derivation","The actual domain is direct xs:date","reuse_with_source_binding"),
        ("mapping3.2","OIM dimension equality","Pure unit absent; language on text facts; typed values, implied periods, only reported taxonomy dimensions","new_mapping_required"),
        ("mapping3.3","footnote-to-note facts","Inspect note IDs/language/XHTML and effective links before whole-report OIM claim","new_mapping_required"),
        ("5.4","Calc1.1 duplicate cross-reference","Contextual reading explicitly recorded; authoritative clarification not obtained","source_qualification"),
        ("AppendixA","normative schema publication copy","Trusted route timed out; embedded copy expressly non-normative","source_copy_pending"),
    ]
    write("prerequisites.json",{"actual_report_calculation_admitted":False,
        "rounding_mode_selected":False,"requirements":[{"source_section":s,"duty":d,"evidence":e,"next_action":a}
            for s,d,e,a in prerequisites]})
    write("source-support-ledger.json",{"classification":"PRIMARY_SPECIFICATION",
        "identity":"source-ledger.json","technical_read":"Entire Calc1.1 technical text plus linked OIM/XML technical dependencies",
        "allowed":"Edition-specific rule comparisons and interpreted finite examples",
        "forbidden":["actual Calc1.1 report acceptance","authoritative erratum","installed processor conformity","issuer rounding mode"]})
    write("claim-support-ledger.json",{"claims":[
        {"claim":"The old and new arcroles define separate networks; old-arc operation is optional and distinguishable.","anchors":["separate_networks_optional_old_arc"],"class":"SOURCE"},
        {"claim":"Same-precision unequal numeric duplicates remain inconsistent even when closed intervals touch.","anchors":["OIM_duplicate_classes","duplicate_rules_and_nil"],"class":"EXPLICIT_CONTEXTUAL_INTERPRETATION"},
        {"claim":"The literal5.4 link points to dimension-only duplicate identity, not its numeric consistency definition.","anchors":["duplicate_rules_and_nil","OIM_duplicate_classes"],"class":"CHECKED_SOURCE_WORDING"},
        {"claim":"Closed nearest intervals are broader at odd grid endpoints than the defined ties-even inverse.","anchors":["rounding_modes_closed_intervals"],"class":"SOURCE_PLUS_EXACT_EXAMPLE"},
        {"claim":"Report compatibility is a prerequisite; a missing normative schema copy is a separate source gap.","anchors":["error_classes_and_OIM_precondition","interval_arithmetic_and_schema_publication"],"class":"SOURCE"}]})
    write("backward-snowball-ledger.json",{"leads":[
        {"source":"OIM2021 and xBRL-XML2021","status":"Exact linked editions acquired and relevant technical text inspected"},
        {"source":"Handling Duplicate Facts WGN","status":"Referenced explanatory lead; OIM normative rule inspected; WGN not acquired within six-resource budget"},
        {"source":"DTR/LRR/HTML5.2/BCP47","status":"Conditional mapping dependencies; no generic implementation or complete review claimed"},
        {"source":"Normative calculation1.1 schema","status":"One trusted route timed out; embedded non-normative appendix inspected only"}]})
    write("forward-snowball-ledger.json",{"queries":"Official release-history and area-index pages retained",
        "current_page_observation":"1.1 corrected2024 recommendation;2.0 under development",
        "scope":"No exhaustive follow-up or filing-system adoption survey"})
    write("citation-venue-ledger.json",{"sources":["Calculations1.1 corrected2024","OIM2021","xBRL-XML2021"],
        "citation_metrics":"not applicable; primary standards","access_date":"2026-10-20"})
    write("omission-risk-ledger.json",{"risks":[
        {"risk":"Generic conformance claimed despite bad cross-reference","response":"Contextual reading explicitly labelled and admission withheld"},
        {"risk":"Old duplicate identity silently reused as OIM mapping","response":"Compatibility and OIM dimensions remain a separate next task"},
        {"risk":"Nearest tie endpoints treated as issuer process","response":"Specification interval is a permissive consistency set, not measurement evidence"},
        {"risk":"Schema timeout interpreted as unavailable","response":"Exact failed receipt retained; no absence claim"},
        {"risk":"Mixed nil set loses its inconsistency","response":"All-nil and mixed-nil fixtures have distinct outcomes"}]})
    print(json.dumps({"constructed":True,"examples":len(examples),"anchors":len(anchors),
        "bindings":len(inputs),"successful_documents":5,"attempts":len(receipts),"prerequisites":len(prerequisites)}))


if __name__=="__main__":
    main()
