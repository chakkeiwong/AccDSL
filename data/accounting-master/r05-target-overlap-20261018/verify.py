"""Finite documentary/exact illustration checker. Default replay is read-only."""
import argparse
import copy
from datetime import date, datetime, timedelta, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys

sys.dont_write_bytecode = True
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
os.environ["GIT_OPTIONAL_LOCKS"] = "0"
UNIT = Path(__file__).resolve().parent
ROOT = UNIT.parents[2]
BASE = ROOT / "data/accounting-master"
PRIOR = BASE / "r03-insurance-termination-basis-20261018"
INTEGRATION = BASE / "early-conversion-integration-20261018"
PLAN = ROOT / "docs/plans/accounting-r05-target-overlap-20261018.md"
SUPPLEMENT = INTEGRATION / "r05-target-overlap-supplement.json"
CONTROLS = ["docs/plans/accounting-master-current.md", "docs/plans/accounting-master-checkpoint.md",
            "docs/plans/accounting-mission-requirements.md", "data/accounting-master/next-plan.md"]
E3 = ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/sections/future-validation.tex"
INPUT_NAMES = ["r05-vintage-admission-20261018", "r05-dependent-loss-source-20261018",
               "protocol-delta-refresh-20261018", "future-validation-20261015"]


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text())


def bind(path):
    return {"path": str(path.relative_to(ROOT)), "sha256": sha(path)}


def write_new(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2)
        handle.write("\n")


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def dirty():
    raw = subprocess.check_output(["git", "status", "--porcelain=v1", "--untracked-files=no", "-z"],
                                  cwd=ROOT, text=True)
    rows = [r for r in raw.split("\0") if r]
    assert all(row[:2] == " M" for row in rows), "unexpected staged/renamed path"
    return {row[3:]: sha(ROOT / row[3:]) for row in rows}


def prepare():
    assert not (UNIT / "protection.json").exists(), "one-time preparation"
    prior = subprocess.run([sys.executable, str(PRIOR / "verify.py")], cwd=ROOT,
                           check=True, capture_output=True, text=True)
    assert json.loads(prior.stdout)["status"] == "read-only replay passed"
    paths = {ROOT / name for name in load(PRIOR / "protection.json")["protected"]}
    paths.update(ROOT / name for name in load(PRIOR / "completion.json")["bindings"])
    paths.add(PRIOR / "completion.json")
    for name in INPUT_NAMES:
        paths.update(p for p in (BASE / name).rglob("*") if p.is_file())
    paths.update([PLAN, UNIT / "verify.py", E3, UNIT / "target-sheets.json", UNIT / "synthetic-inputs.json"])
    paths.difference_update(ROOT / name for name in CONTROLS)
    current = dirty()
    assert len(current) == 36 and git("diff", "--cached", "--name-only") == ""
    snapshots = {}
    for name in CONTROLS:
        target = UNIT / "controls-before" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write((ROOT / name).read_bytes())
        snapshots[str(target.relative_to(ROOT))] = sha(target)
    write_new(UNIT / "protection.json", {
        "started_utc": datetime.now(timezone.utc).isoformat(), "head": git("rev-parse", "HEAD"),
        "branch": git("branch", "--show-current"), "index_sha256": sha(ROOT / ".git/index"),
        "tracked_dirty": current, "protected": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        "control_snapshots": snapshots,
    })
    e3text = E3.read_text()
    start = e3text.index("\\hypertarget{e3.")
    end = e3text.index("\\hypertarget{e4.", start)
    passage = e3text[start:end]
    write_new(UNIT / "input-bindings.json", {
        "frozen_e3": bind(E3), "e3_passage_sha256": hashlib.sha256(passage.encode()).hexdigest(),
        "inspected_inputs": [bind(BASE / name) for name in [
            "r05-vintage-admission-20261018/admission-note.md",
            "r05-vintage-admission-20261018/reconciliation.json",
            "r05-dependent-loss-source-20261018/admission-note.md",
            "r05-dependent-loss-source-20261018/derivation.md",
            "future-validation-20261015/protocol-ledger.md",
            "protocol-delta-refresh-20261018/result.md"]],
        "reading_scope": "E3 subsection; selected admission, intent and covariance passages. Reconciliation is a structural data join, not fresh report reading.",
        "prior_read_only_replay": json.loads(prior.stdout),
    })
    print(json.dumps({"prepared": True, "protected_files": len(paths), "tracked_dirty": len(current)}))


def preservation():
    baseline = load(UNIT / "protection.json")
    assert git("rev-parse", "HEAD") == baseline["head"]
    assert git("branch", "--show-current") == baseline["branch"]
    assert sha(ROOT / ".git/index") == baseline["index_sha256"]
    assert git("diff", "--cached", "--name-only") == ""
    current = dirty()
    assert current.keys() == baseline["tracked_dirty"].keys()
    for name, expected in baseline["tracked_dirty"].items():
        if name not in CONTROLS:
            assert current[name] == expected, name
    for group in ("protected", "control_snapshots"):
        for name, expected in baseline[group].items():
            assert sha(ROOT / name) == expected, name
    assessment = load(INTEGRATION / "assessment-successor.json")
    operations = load(INTEGRATION / "operation-successor.json")
    assert (len(assessment["rows"]), len(assessment["interactions"]), len(operations["rows"])) == (53, 6, 46)
    assert assessment["readiness"] == operations["readiness"] == "not_ready"
    return baseline


def timestamp(value):
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        raise ValueError("missing timezone")
    return result


TARGET_FIELDS = ("issuer", "start", "end_exclusive", "concept", "basis", "perimeter", "unit", "presentation", "outcome_version")


def target_key(cell):
    return tuple(cell[k] for k in TARGET_FIELDS)


def check_fixture(cell):
    """Selected synthetic scalar gates only; not a complete proposed-schema validator."""
    try:
        if not all(cell[k] for k in TARGET_FIELDS):
            raise ValueError("incomplete target identity")
        if cell["concept"] != "operating_cash_flow":
            raise ValueError("wrong primary target")
        if date.fromisoformat(cell["start"]) >= date.fromisoformat(cell["end_exclusive"]):
            raise ValueError("invalid flow interval")
        origin = timestamp(cell["origin"])
        if timestamp(cell["input_available"]) > origin:
            raise ValueError("unavailable predictor")
        if timestamp(cell["outcome_available"]) <= origin:
            raise ValueError("known outcome is not this future-outcome fixture")
        if cell["scale"] is None or Fraction(cell["scale"]) <= 0:
            raise ValueError("unavailable/nonpositive scale")
        if timestamp(cell["scale_available"]) > origin:
            raise ValueError("future scale")
        if cell["law_kind"] != "probability" or not cell["law_complete"] or not cell["finite_first_moment"]:
            raise ValueError("no admitted CRPS law")
        if not cell["paired_target_match"] or not cell["paired_information_match"]:
            raise ValueError("unmatched comparison")
        if cell["comparator"] != "FIXED-locked":
            raise ValueError("changed locked comparator")
    except (KeyError, TypeError, ZeroDivisionError) as error:
        raise ValueError("missing or invalid fixture field") from error


def exact_checks():
    count = 0

    def require(condition, message):
        nonlocal count
        count += 1
        assert condition, message

    sheets = load(UNIT / "target-sheets.json")
    require(sheets["selected_design"] is None, "no design selected")
    require(set(sheets["unselected"]) == {"deployment_population", "weights", "improvement_margin", "confidence_level",
                                           "inference_procedure", "sample_size", "empirical_execution"}, "unselected fields")
    require(all(v is None for k, v in sheets["unselected"].items() if k != "empirical_execution"), "silent default")
    require(sheets["unselected"]["empirical_execution"] is False, "execution held")
    require([s["id"] for s in sheets["sheets"]] == ["finite_panel", "repeated_origins", "future_issuers"], "three distinct questions")
    e3 = sheets["frozen_e3"]
    require(e3["primary_target"] == "operating_cash_flow", "E3 primary")
    require(e3["secondary_joint_target"] == ["closing_cash", "financial_debt"], "E3 secondary")
    require(len(e3["baseline_ladder"]) == 6, "baseline ladder")
    require(e3["effect_orientation"] == "candidate_minus_locked_comparator", "orientation")
    vintage = load(BASE / "r05-vintage-admission-20261018/reconciliation.json")
    require(len(vintage["rows"]) == 192, "source reports")
    require(all(r["selected_byte_available_at"] is None and r["as_of_admission"] is False for r in vintage["rows"]), "vintages remain unadmitted")
    inputs = load(UNIT / "input-bindings.json")
    for item in [inputs["frozen_e3"], *inputs["inspected_inputs"]]:
        require(bind(ROOT / item["path"]) == item, item["path"])
    text = E3.read_text()
    passage = text[text.index("\\hypertarget{e3."):text.index("\\hypertarget{e4.")]
    require(hashlib.sha256(passage.encode()).hexdigest() == inputs["e3_passage_sha256"], "unchanged E3")

    data = load(UNIT / "synthetic-inputs.json")
    cells = data["cells"]
    require(len(cells) == 6 and len({r["id"] for r in cells}) == 6, "six unique observations")
    require(all(r["issuer"].startswith("SYN-") for r in cells), "fictional data")
    daysets = {}
    for cell in cells:
        check_fixture(cell)
        require(True, "fixture gates")
        start, end = date.fromisoformat(cell["start"]), date.fromisoformat(cell["end_exclusive"])
        daysets[cell["id"]] = {start + timedelta(days=k) for k in range((end-start).days)}
    pairs = []
    for left, right in itertools.combinations(cells, 2):
        start = max(date.fromisoformat(left["start"]), date.fromisoformat(right["start"]))
        end = min(date.fromisoformat(left["end_exclusive"]), date.fromisoformat(right["end_exclusive"]))
        days = max(0, (end-start).days)
        require(days == len(daysets[left["id"]] & daysets[right["id"]]), "independent overlap check")
        relations = []
        for condition, name in [
            (left["issuer"] == right["issuer"], "shared_issuer"),
            (days > 0, "calendar_intersection"),
            (target_key(left) == target_key(right), "same_target_outcome"),
            (left["outcome_version"] == right["outcome_version"], "shared_outcome_source"),
            (left["fit_id"] == right["fit_id"], "shared_fitting"),
            (left["scenario_id"] == right["scenario_id"], "shared_scenario")]:
            if condition:
                relations.append(name)
        pairs.append({"left": left["id"], "right": right["id"], "calendar_intersection_days": days,
                      "relations": relations, "covariance": "not estimated", "absence_means_independence": False})
    by_pair = {(p["left"], p["right"]): p for p in pairs}
    require(by_pair[("A1", "A2")]["calendar_intersection_days"] == 184, "rolling overlap")
    require(by_pair[("A1", "A3")]["calendar_intersection_days"] == 92, "nested overlap")
    require("same_target_outcome" in by_pair[("A1", "A4")]["relations"], "repeated target")
    require("shared_issuer" not in by_pair[("A1", "B1")]["relations"] and by_pair[("A1", "B1")]["calendar_intersection_days"] == 365, "cross-issuer calendar")
    require(by_pair[("A1", "C1")]["relations"] == ["shared_fitting"], "disjoint targets can share fitting")
    require(timestamp(cells[3]["origin"]).date() > date.fromisoformat(cells[3]["start"]), "partly elapsed origin")

    losses = data["weight_example"]["losses"]
    equal_cell = sum(Fraction(r["difference"]) for r in losses) / len(losses)
    groups = {}
    for row in losses:
        groups.setdefault(row["issuer"], []).append(Fraction(row["difference"]))
    equal_issuer = sum(sum(v)/len(v) for v in groups.values()) / len(groups)
    require(equal_cell == Fraction(data["weight_example"]["equal_cell_expected"]), "equal cell derivation")
    require(equal_issuer == Fraction(data["weight_example"]["equal_issuer_expected"]), "equal issuer derivation")
    require(equal_cell < 0 < equal_issuer, "weight sign reversal")

    coverage = data["coverage_example"]
    require([r["id"] for r in coverage["rows"]] == coverage["eligible_ids"], "full eligibility denominator")
    paired = [r for r in coverage["rows"] if r["candidate_score"] is not None and r["comparator_score"] is not None]
    require([r["id"] for r in paired] == coverage["paired_ids"], "common coverage")
    mean = sum(Fraction(r["candidate_score"])-Fraction(r["comparator_score"]) for r in paired)/len(paired)
    require(mean == Fraction(coverage["paired_mean_expected"]), "paired descriptive mean")
    require(coverage["full_eligible_effect"] is None and len(paired) == 2 and len(coverage["rows"]) == 4, "no missingness inference")
    require(data["release_example"]["exact_selected_byte_available"] is None and data["release_example"]["predictor_admitted"] is False, "no day-to-byte admission")

    fixtures = [
        ("missing target identity", "perimeter", None), ("wrong target concept", "concept", "closing_cash"),
        ("empty flow interval", "start", "2022-01-01"), ("future predictor", "input_available", "2021-01-01T00:00:00Z"),
        ("unknown selected-byte time", "input_available", None), ("known outcome fixture", "outcome_available", "2020-01-01T00:00:00Z"),
        ("missing scale", "scale", None), ("zero scale", "scale", "0"), ("negative scale", "scale", "-1"),
        ("future scale", "scale_available", "2021-01-01T00:00:00Z"), ("set is not a law", "law_kind", "unweighted_set"),
        ("unresolved mass", "law_complete", False), ("unchecked first moment", "finite_first_moment", False),
        ("wrong paired target", "paired_target_match", False), ("unmatched information", "paired_information_match", False),
        ("changed comparator", "comparator", "chosen_after_test")]
    rejected = []
    for name, key, value in fixtures:
        changed = copy.deepcopy(cells[0])
        changed[key] = value
        try:
            check_fixture(changed)
        except (ValueError, AttributeError):
            rejected.append(name)
        else:
            raise AssertionError(name)
        require(True, name)
    return {"scope": "documentary and exact synthetic only; not an empirical or inference-method validation",
            "checks": count, "target_sheets": 3, "synthetic_observations": len(cells), "pairs": pairs,
            "weight_results": {"equal_cell": str(equal_cell), "equal_issuer": str(equal_issuer)},
            "coverage": {"eligible": 4, "paired": 2, "paired_mean": str(mean), "full_effect": None},
            "rejected_fixtures": rejected, "procedure_admitted": False, "whole_rows_closed": 0}


def record(baseline, checks):
    assert not (UNIT / "completion.json").exists() and not (UNIT / "controls-after").exists()
    assert not SUPPLEMENT.exists()
    assert load(UNIT / "checks.json") == checks
    for name in ("specification.md", "result.md", "review.md"):
        assert (UNIT / name).is_file(), name
    finished = datetime.now(timezone.utc)
    write_new(UNIT / "run-manifest.json", {
        "started_utc": baseline["started_utc"], "finished_utc": finished.isoformat(),
        "elapsed_wall_seconds": (finished-datetime.fromisoformat(baseline["started_utc"])).total_seconds(),
        "commands": [shlex.join([sys.executable, str(UNIT.relative_to(ROOT) / "verify.py"), flag]) for flag in ("--prepare", "--check", "--record")],
        "fresh_replay_command": shlex.join([sys.executable, str(UNIT.relative_to(ROOT) / "verify.py")]),
        "git_commit": baseline["head"], "index_sha256": baseline["index_sha256"], "staging": "empty; unchanged",
        "tracked_dirty_paths": len(baseline["tracked_dirty"]),
        "environment": {"python_executable": sys.executable, "python_version": platform.python_version(), "imports": "standard library only"},
        "cpu_gpu_status": "CPU only; CUDA_VISIBLE_DEVICES=-1 intentionally hides GPUs; no framework initialization",
        "data_version": "frozen 3.44 E3 and completed R05 inquiries; new fictional rational/calendar examples",
        "random_seeds": "N/A: exact documentary/rational/calendar checks", "plan": bind(PLAN),
        "result_file": str((UNIT / "result.md").relative_to(ROOT)), "output_directory": str(UNIT.relative_to(ROOT)),
        "input_bindings": bind(UNIT / "input-bindings.json"), "empirical_execution": False,
        "selections": load(UNIT / "target-sheets.json")["unselected"], "whole_rows_closed": 0,
    })
    snapshots = []
    for name in CONTROLS:
        target = UNIT / "controls-after" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as handle:
            handle.write((ROOT / name).read_bytes())
        snapshots.append({"live_path": name, **bind(target)})
    write_new(SUPPLEMENT, {
        "candidate_pdf": bind(ROOT / "docs/design/proposal/manuscript-early-conversion-20261018/accounting-product-proposal.pdf"),
        "protected_assessment": bind(INTEGRATION / "assessment-successor.json"),
        "protected_integration": bind(INTEGRATION / "integration-bindings.json"),
        "protected_operations": bind(INTEGRATION / "operation-successor.json"),
        "additional_evidence": [bind(UNIT / name) for name in ("target-sheets.json", "specification.md", "synthetic-inputs.json", "checks.json", "review.md", "result.md", "run-manifest.json")],
        "scope": "R05 proposed alternative E3 target/sampling/overlap specification; no selected population or inference procedure",
        "all_original_obligations": 53, "interactions": 6, "operations": 46, "whole_rows_closed": 0,
        "readiness": "not_ready", "independent_domain_human_acceptance": "pending",
    })
    paths = [p for p in UNIT.rglob("*") if p.is_file() and p.name != "completion.json"] + [PLAN, SUPPLEMENT]
    write_new(UNIT / "completion.json", {
        "recorded_utc": finished.isoformat(), "bindings": {str(p.relative_to(ROOT)): sha(p) for p in sorted(paths)},
        "controls_at_completion": snapshots, "control_replay_policy": "Immutable snapshots; live controls may advance in authorised successor units.",
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    for flag in ("prepare", "check", "record"):
        modes.add_argument("--" + flag, action="store_true")
    args = parser.parse_args()
    if args.prepare:
        prepare()
        return
    baseline = preservation()
    checks = exact_checks()
    if args.check:
        write_new(UNIT / "checks.json", checks)
        print(json.dumps({"status": "finite checks recorded", "checks": checks["checks"], "pairs": len(checks["pairs"]), "rejected_fixtures": len(checks["rejected_fixtures"])}))
        return
    if args.record:
        record(baseline, checks)
    assert load(UNIT / "checks.json") == checks
    completion = load(UNIT / "completion.json")
    for name, expected in completion["bindings"].items():
        assert sha(ROOT / name) == expected, name
    supplement = load(SUPPLEMENT)
    for key in ("candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"):
        item = supplement[key]
        assert bind(ROOT / item["path"]) == item
    assert (supplement["all_original_obligations"], supplement["interactions"], supplement["operations"],
            supplement["whole_rows_closed"], supplement["readiness"]) == (53, 6, 46, 0, "not_ready")
    print(json.dumps({"status": "recorded and verified" if args.record else "read-only replay passed",
                      "checks": checks["checks"], "target_sheets": 3, "synthetic_observations": 6,
                      "pairs": len(checks["pairs"]), "rejected_fixtures": len(checks["rejected_fixtures"]),
                      "protected_files": len(baseline["protected"]), "completion_bindings": len(completion["bindings"]),
                      "procedure_admissions": 0, "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
