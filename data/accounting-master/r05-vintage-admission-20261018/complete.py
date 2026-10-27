"""One-time documentary recording; subsequent invocation is read-only."""
import argparse
from datetime import datetime, timezone
import json
import os
import platform
import subprocess
import sys
import time

os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

from reconcile import (
    ROOT, OUT, BASE, PLAN, PDF, INTEGRATION, CONTROLS, construct, load, binding,
)
from check import require, validate, fixtures, preservation

PREFIX = str(OUT.relative_to(ROOT)) + "/"
SUPPLEMENT = INTEGRATION + "r05-vintage-admission-supplement.json"
SNAPSHOT = INTEGRATION + "controls-r05-vintage-admission-before/"
ARTIFACTS = ["reconciliation.json", "admission-note.md", "checks.json", "result.md",
             "reconcile.py", "check.py", "complete.py"]


def write_new(path, value):
    with (ROOT / path).open("x", encoding="utf-8") as handle:
        if isinstance(value, str):
            handle.write(value)
        else:
            json.dump(value, handle, indent=2, ensure_ascii=False)
            handle.write("\n")


def result_text(summary, checks, rejected, inputs):
    return f"""# R05 active-panel vintage/exposure result

18 October 2026. Documentary reconciliation completed and author-checked.
Plan: {PLAN}. Exact source anchors: reconciliation.json.
Admission and next-action detail: admission-note.md.

The join retains {summary['active_reports']} ordered active records and excludes
{len(summary['excluded_registry_reports'])} superseded registry reports.
All selected original bytes, prior publication-unit manifest bindings and joined
source identities pass direct hash checks. There are {len(inputs)} input-file
bindings, {len(checks)} structural/source checks and {len(rejected)} rejected
corruption probes. These counts describe documentary checks, not independent
scientific observations.

The original 56 filing-date / 136 unverified assessments remain verbatim.
Twelve later official filing events and 35 attributed publication declarations
are separate, disjoint additions. Their three-role union covers 103 reports;
89 have none of these roles in this inquiry. Ten alternate-source date
candidate reports are recorded separately. No date is transferred to selected
bytes: all 192 availability values stay null; historical admissions remain zero.

Thirty-one author pilot annotations join four exact selected versions.
Forty JPMorgan semantic assertions join four different complete 10-K sources;
their selected annual counterparts are verified separately. Exposure is a
nonexhaustive lower bound, and every family has acquisition/QA exposure.
No candidate role becomes an admitted test split or independent gold label.

| Decision | Primary criterion status | Veto diagnostic status | Main uncertainty | Next justified action | What is not concluded |
| --- | --- | --- | --- | --- | --- |
| Complete the bounded documentary join | 192 ordered, identity-bound rows; original metadata and separate roles retained | All recorded checks pass; injected identity/time/exclusion/label/split errors are rejected | Unlisted exposure is unknown; exact selected-byte historical availability remains unestablished | Preserve this result and investigate dependent-loss uncertainty sources | Historical validation eligibility, predictive accuracy, model ranking, new default or whole-requirement closure |
| Keep E1–E6/B0–B3 admissions distinct | Missing task inputs and concrete internal actions are recorded per protocol/rung | Missing inputs block their dependent runs; no global continuation veto | Target-specific data, law, independent labels, inferential population, uncertainty and cost remain unselected | Continue source/protocol and independent-oracle preparation | Rejection of the research direction, empirical execution or professional engagement |

Preflight repairs were confined to new tooling: one transcribed expected
operation hash omitted characters and was corrected against the unchanged
frozen file and prior R08 supplement; the role-status check initially expected
a short enum and was repaired to preserve the source's full qualified string.
No source, frozen assessment or existing runtime was changed by these failures.

Post-run red-team: the 103 date-role count could be misread as an eligible
historical sample. It is not: filing metadata, events and declarations do not
prove unchanged selected-byte availability. The four separately annotated
complete 10-Ks could also be mistaken for the selected annual PDFs; their
different paths/hashes are explicit and corruption-checked. Independent
accounting/implementability/human acceptance remains pending.

The manuscript remains Version 3.44, 396 pages, not_ready. Its 53 obligations,
six interactions and 46 operation rows are preserved without whole-row closure.
Only the four live controls may be refreshed. No benchmark/model/sampler,
controller, upstream import, installation, GPU computation, commit, outreach,
publication or fee is part of this result.

Environment: standard-library CPU file/JSON/hash checks;
CUDA_VISIBLE_DEVICES=-1 intentionally hides GPU devices; no framework import.
No stochastic comparison occurred; no ranking is statistically supported or
attempted. The next primary-source inquiry concerns dependent forecast-loss
comparison and its limits for nine purposively chosen issuers and overlapping
forecast horizons. Proper-score definitions alone do not select that procedure.
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", action="store_true")
    args = parser.parse_args()
    tick = time.monotonic()
    started = datetime.now(timezone.utc).isoformat()
    if args.record:
        for name in ["reconciliation.json", "checks.json", "result.md",
                     "run-manifest.json", "completion.json"]:
            require(not (OUT / name).exists(), "ALREADY_RECORDED:" + name)
        require(not (ROOT / SUPPLEMENT).exists(), "SUPPLEMENT_EXISTS")
        require(not (ROOT / SNAPSHOT).exists(), "SNAPSHOT_EXISTS")
        document, data, inputs = construct()
        checks, rejected = validate(document, data), fixtures(document, data)
        state = preservation()
        assessment = load(INTEGRATION + "assessment-successor.json")
        operations = load(INTEGRATION + "operation-successor.json")
        require((len(assessment["rows"]), len(assessment["interactions"]), len(operations["rows"]))
                == (53, 6, 46), "FROZEN_OBLIGATION_COUNTS")
        require(assessment["readiness"] == operations["readiness"] == "not_ready", "READINESS")
        snapshots = []
        for name in CONTROLS:
            target = SNAPSHOT + name
            (ROOT / target).parent.mkdir(parents=True, exist_ok=True)
            with (ROOT / target).open("xb") as handle:
                handle.write((ROOT / name).read_bytes())
            snapshots.append({"live_before": binding(name), "snapshot": binding(target)})
        write_new(PREFIX + "reconciliation.json", document)
        write_new(PREFIX + "checks.json", {
            "all_passed": True, "checks": checks, "rejected_corruptions": rejected,
            "summary": document["summary"], "preservation": state,
        })
        write_new(PREFIX + "result.md", result_text(document["summary"], checks, rejected, inputs))
        manifest = {
            "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
            "wall_seconds": time.monotonic() - tick,
            "command": sys.executable + " " + PREFIX + "complete.py --record",
            **state,
            "git_baseline": load(BASE + "r06-duty-reconciliation-20261018/run-manifest.json")["git_baseline"],
            "environment": {
                "python_executable": sys.executable, "python_version": platform.python_version(),
                "conda_environment_path": str(__import__("pathlib").Path(sys.executable).parent.parent),
                "imports": "standard library and the local documentary checker only",
            },
            "cpu_gpu_status": "CPU file/JSON/hash checks; GPU intentionally hidden by CUDA_VISIBLE_DEVICES=-1; no framework import",
            "data_version": "active target-panel-v2 / 192 coverage records; exact inputs below",
            "random_seeds": "N/A: deterministic documentary reconciliation",
            "plan_file": PLAN, "result_file": PREFIX + "result.md",
            "inputs": inputs, "output_directory": PREFIX,
            "artifacts": [binding(PREFIX + name) for name in ARTIFACTS],
        }
        write_new(PREFIX + "run-manifest.json", manifest)
        completion = {
            "recorded_utc": datetime.now(timezone.utc).isoformat(),
            "control_snapshots": snapshots, "manifest": binding(PREFIX + "run-manifest.json"),
            "artifacts": [binding(PREFIX + name) for name in ARTIFACTS],
            "record_wall_seconds": time.monotonic() - tick,
        }
        write_new(PREFIX + "completion.json", completion)
        write_new(SUPPLEMENT, {
            "candidate_pdf": binding(PDF),
            "protected_assessment": binding(INTEGRATION + "assessment-successor.json"),
            "protected_integration": binding(INTEGRATION + "integration-bindings.json"),
            "protected_operations": binding(INTEGRATION + "operation-successor.json"),
            "additional_evidence": [binding(PREFIX + name) for name in
                                    ["completion.json", "result.md", "checks.json", "run-manifest.json", "admission-note.md"]],
            "scope": "R05 selected-panel vintage/exposure reconciliation; 192 ordered rows, separate 56 metadata/12 events/35 declarations; zero byte-vintage admissions",
            "all_original_obligations": 53, "interactions": 6, "operations": 46,
            "whole_rows_closed": 0, "readiness": "not_ready",
            "independent_domain_human_acceptance": "pending",
        })
    # Replay runs in a fresh process; it neither records nor refreshes controls.
    run = subprocess.run([sys.executable, str(OUT / "check.py")], cwd=ROOT,
                         capture_output=True, text=True, check=True)
    completion, supplement = load(PREFIX + "completion.json"), load(SUPPLEMENT)
    bindings = [completion["manifest"]] + completion["artifacts"]
    bindings += [supplement[key] for key in [
        "candidate_pdf", "protected_assessment", "protected_integration", "protected_operations"]]
    bindings += supplement["additional_evidence"]
    for row in completion["control_snapshots"]:
        require(row["live_before"]["sha256"] == row["snapshot"]["sha256"], "SNAPSHOT_IDENTITY")
        bindings.append(row["snapshot"])
    for row in bindings:
        require(binding(row["path"]) == row, "COMPLETION_BINDING:" + row["path"])
    print(json.dumps({"completion": "recorded and verified" if args.record else "read-only replay passed",
                      "completion_bindings": len(bindings), **json.loads(run.stdout),
                      "whole_rows_closed": 0}))


if __name__ == "__main__":
    main()
