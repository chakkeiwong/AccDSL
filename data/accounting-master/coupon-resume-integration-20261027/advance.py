"""Advance the current design and work queue while preserving historical evidence."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
import json
import os

H = Path(__file__).resolve().parent
R = H.parents[2]
OLD = H.parent / "gap-coupon-scope-refresh-20261027"
G = H.parent / "gap-coupon-resume-refresh-20261027"
NEXT = "docs/plans/accounting-credit-claim-continuity-20261027.md"
PLAN = "docs/plans/accounting-coupon-resume-integration-20261027.md"
RESULT = str((H / "result.md").relative_to(R))
INTERNAL = "data/accounting-master/coupon-program-resume-20261027/result.md"


def read(path):
    return json.loads(path.read_text())


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2) + chr(10))


assert not G.exists() and not (H / "advancement.json").exists()
v = read(H / "verification.json")
assert v["status"] == "PASS" and v["checks"] == 836 and (H / "author-review.md").exists()
assert (R / NEXT).is_file() and (R / PLAN).is_file() and (R / RESULT).is_file()
lock = read(H / "source-preservation.json")
S, T = R / lock["source"], R / lock["target"]
for group, base in [("sources", S), ("evidence", R), ("added", T), ("integration_inputs", H)]:
    for name, value in lock[group].items():
        assert digest(base / name) == value, name
for doc in v["documents"]:
    assert digest(T / (doc["document"] + ".pdf")) == doc["sha256"]
paths = ["scripts/accounting_master_catalog.json", "data/accounting-master/next-plan.json",
         "docs/plans/accounting-master-current.md", "data/accounting-master/next-plan.md",
         "MISSION_CONTROL.md", "docs/plans/accounting-master-checkpoint.md",
         "docs/plans/accounting-master-program.md", "docs/plans/accounting-mission-requirements.md",
         "docs/plans/accounting-product-design-checkpoint.md", "docs/README.md"]
before = {name: (R / name).read_bytes() for name in paths}
catalog, next_plan = [json.loads(before[name]) for name in paths[:2]]
a, b = catalog["active_execution_note"], next_plan["active_execution"]
assert a["current_candidate"] == b["current_candidate"] == "5.47;824 pages;not_ready"
assert a["active_work_plan"] == b["active_work_plan"] == "docs/plans/accounting-coupon-program-resume-20261027.md"
assert a["financing_next_plan"] == b["financing_next_plan"]
links = {name: str((R / name).resolve()) for name in ["docs/AccDSL-latest.pdf",
         "docs/AccDSL-latest.tex", "docs/AccDSL-simulation-foundations.pdf", "docs/AccDSL-simulation-foundations.tex"]}
assert all(Path(value).parent == S for value in links.values())
old_locks = {str(p.relative_to(R)): digest(p) for p in OLD.iterdir() if p.is_file()}
audit, packages = read(OLD / "audit-status.json"), read(OLD / "closure-packages.json")
protected_groups = deepcopy(audit["groups"])
audit["predecessor"] = str(OLD.relative_to(R))
audit["baseline"] = "Version 5.48 integrates selected same-period resumption; 5.47 preserved."
for title, evidence, disposition in [
    ("Selected coupon program resumption", INTERNAL, "16 cases, 48 chunk comparisons, 824 assertions and 18 controls; supplementary audit 493 assertions and 12 controls."),
    ("Selected resume manuscript integration", RESULT, "836 checks preserve 277 sources and 264 evidence files; covers and added pages reviewed; independent acceptance pending.")]:
    assert not any(d["evidence"] == evidence for d in audit["successor_deltas"])
    audit["successor_deltas"].append(dict(id="D" + str(len(audit["successor_deltas"]) + 1),
        title=title, requirements=["MC03", "MC05", "MC11", "MC12", "MC13", "MC18", "MC24", "MC25", "MC26", "MC28", "MC32", "MC33", "MC34"],
        evidence=evidence, sha256=digest(R / evidence), current_disposition=disposition))
for row in packages["packages"]:
    assert row["status"] == "open"
    if row["id"] in ["W05", "W11", "W12", "W13", "W16", "W17"]:
        row["existing_support"] += " Version 5.48 integrates selected same-period resumption; independent acceptance pending."
    if row["id"] in ["W09", "W16"]:
        row["next_action"] = "Execute accounting-credit-claim-continuity-20261027.md; reconcile every dated collection, removed portion, uncollected amount and modeled schedule revision."
    if row["id"] == "W05":
        row["next_action"] = "Selected coupon resume is checked; broader financing and cross-period methods remain open. Conversion allocation remains independently source-evidence-blocked."
    if row["id"] == "W11":
        row["next_action"] = "Retain selected resume semantics; audit other method families and explicit migration boundaries before generalizing the interface."
    if row["id"] == "W12":
        row["next_action"] = "Pure selected replay is checked; real store transactions, effect ownership and concurrent-writer recovery remain unimplemented and cannot close from this evidence."
    if row["id"] == "W13":
        row["next_action"] = "Preserve exact numerical and resource refusal distinctions; extend root/reset domains only with explicit certification and independent financial targets."
    if row["id"] == "W01":
        row["next_action"] = "Continue exact source spans, precision and dated availability; keep legal-book opening admission separate from consolidated disclosure."
    if row["id"] == "W03":
        row["next_action"] = "Extend source/message continuation only with explicit observation and permitted-policy semantics; retain unresolved histories when evidence is insufficient."
    if row["id"] == "W04":
        row["next_action"] = "Retain the checked date/replay counterexamples; audit compression only for explicitly named future methods, queries and resource scope."
    if row["id"] == "W17":
        row["next_action"] = "Version 5.48 integrates selected resumption; continue bounded consistency repairs and independent reader/domain/whole-document review."
counts = read(OLD / "verification.json")["counts"]
counts["successor_deltas"] = len(audit["successor_deltas"])
assert len(audit["successor_deltas"]) == 121
assert audit["groups"] == protected_groups and counts["closure_packages"] == len(packages["packages"]) == 18
base = str(G.relative_to(R))
docs = {d["document"]: d for d in v["documents"]}
changes = dict(updated="2026-10-27", current_candidate="5.48;825 pages;not_ready",
    latest_result=RESULT, latest_internal_result=INTERNAL, coupon_resume_result=INTERNAL,
    active_work_plan=NEXT, current_program=PLAN, current_audit=base + "/audit-status.json",
    remaining_work=base + "/remaining-work.md", full_gap_remaining_work=base + "/remaining-work.md",
    current_pdf=str((T / "accounting-product-proposal.pdf").relative_to(R)),
    current_pdf_sha256=docs["accounting-product-proposal"]["sha256"],
    standalone_pdf=str((T / "simulation-foundations.pdf").relative_to(R)),
    standalone_pdf_sha256=docs["simulation-foundations"]["sha256"],
    full_gap_plan=PLAN, full_gap_program=base + "/closure-program.md", closure_packages=base + "/closure-packages.json",
    failure_register=base + "/failure-register.json", latest_gap_program_result=base + "/result.md",
    gap_program_review=base + "/plan-review.md", gap_program_verification=base + "/verification.json",
    active_work_plans=[NEXT, a["financing_next_plan"]], gap_program_trace_counts=counts,
    next=["Execute " + NEXT, "Continue financing evidence " + a["financing_next_plan"], "Continue all 18 broad packages"],
    gap_program_next=["Check bank credit schedule continuity after write-off", "Continue financing evidence", "Continue broader source, language and reader work"],
    bank_next_plan=NEXT, current_internal_status="Selected coupon resumption integrated; bank claim-component continuity next; no whole requirement closure.")
for obj in (a, b):
    obj.update(changes)
    for key in ("latest_internal_results", "latest_results"):
        if key in obj:
            for result in (INTERNAL, RESULT):
                if result not in obj[key]:
                    obj[key].append(result)
if "completed_increments" in b:
    b["completed_increments"].append("Version 5.48: selected same-period resumption; 836 checks; not_ready.")
summary = chr(10).join([
    "Updated 27 October 2026. Governing candidate **5.48**, 825 main pages, not_ready.",
    "Simulation: 259 total / 238 body pages. Four stable PDF/TeX links select this candidate.",
    "Main SHA256: " + a["current_pdf_sha256"] + ".",
    "Simulation SHA256: " + a["standalone_pdf_sha256"] + ".", "",
    "Selected same-period resumption and supplementary prefix/resource checks",
    "are integrated. All 836 document checks pass, preserving",
    "277 sources and 264 evidence files. Both covers and all added pages reviewed.",
    "Independent reader, domain and whole-document acceptance remain pending.", "",
    "Result: " + RESULT + ".", "Method evidence: " + INTERNAL + ".",
    "Active execution plan: " + NEXT + ".", "Financing evidence plan: " + a["financing_next_plan"] + ".",
    "Full program: " + base + "/closure-program.md.", "Remaining work: " + base + "/remaining-work.md.", "",
    "All 53 obligations, six interactions, 46 operations and 18 packages remain open.",
    "S1–S5 partial; S6 held; E3 deferred. Measured conversion-to-control remains locally",
    "evidence-blocked. Continue independent ready work; no global continuation veto.", ""])
new = {paths[0]: json.dumps(catalog, indent=2) + chr(10), paths[1]: json.dumps(next_plan, indent=2) + chr(10)}
for name in paths[2:4]:
    new[name] = "# Current AccDSL master program" + chr(10)*2 + summary
for name in paths[4:9]:
    title, body = before[name].decode().split(chr(10), 1)
    new[name] = title + chr(10)*2 + "## Selected program resumption integrated — 27 October 2026" + chr(10)*2 + summary + chr(10) + body.lstrip(chr(10))
text = before[paths[9]].decode()
for old, replacement in [("Version 5.47, 824 pages", "Version 5.48, 825 pages"), ("**258 pages**", "**259 pages**"),
                         ("**237 body pages**", "**238 body pages**"), (str(OLD.relative_to(R)), base),
                         ("coupon-scope-integration-20261027/result.md", "coupon-resume-integration-20261027/result.md")]:
    assert old in text, old
    text = text.replace(old, replacement)
new[paths[9]] = text
snapshot = H / "control-before"
snapshot.mkdir(exist_ok=False)
for name, raw in before.items():
    assert (R / name).read_bytes() == raw, name
    target = snapshot / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(raw)
dump(snapshot / "stable-links.json", links)
G.mkdir(exist_ok=False)
for name, value in [("predecessor-lock.json", old_locks), ("audit-status.json", audit), ("closure-packages.json", packages)]:
    dump(G / name, value)
(G / "failure-register.json").write_bytes((OLD / "failure-register.json").read_bytes())
lines = ["# Full closure program after selected resume integration", "Version 5.48; all 18 packages remain open."]
for row in packages["packages"]:
    lines += ["", "## " + row["id"] + " — " + row["title"]]
    for key in ("requirements", "depends_on", "failure", "existing_support", "closure_evidence", "next_action", "limits", "status"):
        value = row[key]
        lines += ["", key + ": " + (", ".join(value) or "none" if isinstance(value, list) else value)]
(G / "closure-program.md").write_text(chr(10).join(lines) + chr(10))
(G / "remaining-work.md").write_text("# Remaining work" + chr(10)*2 + chr(10).join("- **" + r["id"] + " " + r["title"] + ":** " + r["next_action"] for r in packages["packages"]) + chr(10)*2 + "S1–S5 partial; S6 held; E3 deferred." + chr(10))
(G / "plan-review.md").write_text("Exact source preservation, complete chunk comparisons and supplementary prefix/resource checks support provisional 5.48. General methods, cross-period execution and durable persistence remain open. Ready bank work now checks nominal claim components without inventing legal outcomes. Stale next actions for disclosure, information and compression are restored to those packages' own closure criteria. Financing evidence and all original rows are preserved.\n")
(G / "result.md").write_text("One selected resume method delta (including its audit) and one integration delta added without duplicate credit. Original obligations, interactions, operations and all 18 package statuses are preserved. No whole requirement closes.\n")
dump(G / "verification.json", dict(status="PASS", counts=counts, original_rows_preserved=True, all_packages_open=True, whole_requirements_closed=0))
for name, text in new.items():
    assert (R / name).read_bytes() == before[name]
    tmp = (R / name).with_name(Path(name).name + ".v548.tmp")
    assert not tmp.exists()
    tmp.write_text(text)
    os.replace(tmp, R / name)
for name in links:
    stem = "simulation-foundations" if "simulation" in name else "accounting-product-proposal"
    target = T / (stem + Path(name).suffix)
    tmp = (R / name).with_name(Path(name).name + ".v548-link")
    assert not tmp.exists()
    tmp.symlink_to(os.path.relpath(target, (R / name).parent))
    os.replace(tmp, R / name)
    assert (R / name).resolve() == target
for name, text in new.items():
    assert (R / name).read_text() == text
for name, value in old_locks.items():
    assert digest(R / name) == value
dump(H / "advancement.json", dict(status="PASS", candidate=a["current_candidate"], counts=counts,
     next=NEXT, changed_controls=list(new), all_packages_open=True, mission_complete=False))
print(json.dumps(dict(status="PASS", candidate=a["current_candidate"], next=NEXT, counts=counts)))
