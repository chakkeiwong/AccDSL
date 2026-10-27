"""Bind scoped judgments and refresh only the three authorized live controls."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
UNIT = str(OUT.relative_to(ROOT))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + "\n")


def records():
    report = json.loads((OUT / "manuscript-checks.json").read_text())
    checks = json.loads((OUT / "ordered-eps/attempt-01/summary.json").read_text())
    assert report["failures"] == checks["failures"] == 0
    assert report["pdf_sha256"] == "5fe60ada56afce6900d57bc5ddecad05090521e3a2d56dc2884987f51d673d54"
    review = dict(pdf_sha256=report["pdf_sha256"], pages=report["rendered_pages"],
        contact_sheets=["render-attempt-01/contact-01.png", "render-attempt-02/contact-02.png"],
        full_page_inspection=[175, 176, 330, 331],
        final_page_176="reinspected after directional-reference repair",
        other_nine_pages="byte-identical to inspected preceding render",
        findings=["Nearly empty last appendix page repaired", "Incorrect above reference repaired"],
        final_disposition="no clipping or unresolved local visual finding on inspected pages",
        human_comprehension="pending", independent_technical_review="pending",
        scope="ten selected pages; all-page text-bound check; not whole-document human acceptance")
    write("rendered-review.json", review)
    prior_path = ROOT / "data/accounting-master/r08-assessment-20261016/assessment.json"
    previous = json.loads(prior_path.read_text())
    current = deepcopy(previous)
    current.update(candidate_version="3.15", candidate_pdf=report["candidate_pdf"],
        candidate_pdf_sha256=report["pdf_sha256"], predecessor=str(prior_path.relative_to(ROOT)),
        predecessor_sha256=sha(prior_path), assessment_scope="scoped EPS/integrity delta; other judgments carried forward",
        source_protection="All 53 original rows and acceptance wording retained; no whole-row closure")
    affected = {"MC02", "MC04", "MC05", "MC16", "MC17", "MC19", "MC24", "MC25", "MC28", "MC30", "MC32", "MC34", "MC35", "G2", "G4", "G7", "G12", "G13", "G15", "G18"}
    for row in current["rows"]:
        row["previous_candidate_version"] = row["candidate_version"]
        row.update(candidate_version="3.15", candidate_pdf=report["candidate_pdf"], candidate_pdf_sha256=report["pdf_sha256"])
        if row["id"] in affected:
            row["evidence_updates"].append("OrderedEPS/1: finite independent-additive report, exact sign/tie/date/refusal checks and protected manuscript integration; see " + UNIT + "/requirements-successor.md")
            row["delta_assessment"] = "bounded documentary evidence added; inherited residuals remain"
        else:
            row["delta_assessment"] = "inherited judgment preserved; not re-reviewed in this unit"
    assert len(current["rows"]) == 53
    for old, new in zip(previous["rows"], current["rows"]):
        assert all(old[key] == new[key] for key in ("id", "label", "original_obligation", "acceptance"))
    for interaction in current["interactions"]:
        if interaction["id"] == "I03":
            interaction["delta"] = "OrderedEPS selector is now specified; company conversion/tax/share join remains next."
    write("assessment-successor.json", current)
    old_packet_path = ROOT / "data/accounting-master/review-packet-20261016/packet.json"
    old_packet = json.loads(old_packet_path.read_text())
    old_entries = [dict(path=item["path"], recorded=item["sha256"], current=sha(ROOT / item["path"])) for item in old_packet["evidence_files"]]
    mismatches = [item for item in old_entries if item["recorded"] != item["current"]]
    assert len(mismatches) == 3
    write("old-packet-integrity.json", dict(packet=str(old_packet_path.relative_to(ROOT)),
        packet_sha256=sha(old_packet_path), evidence_count=len(old_entries), mismatches=mismatches,
        disposition="preserved unchanged; three live-control references stale; successor uses snapshots"))
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    index = subprocess.check_output(["git", "diff", "--cached", "--raw", "--no-abbrev"], cwd=ROOT)
    protected = json.loads((OUT / "preservation-manifest.json").read_text())
    assert head == protected["head"] and hashlib.sha256(index).hexdigest() == protected["cached_raw_sha256"]
    manifest = dict(recorded_utc=datetime.now(timezone.utc).isoformat(), git_commit=head,
        index_sha256=hashlib.sha256(index).hexdigest(), index_entries=len(index.splitlines()),
        plan="docs/plans/accounting-continuation-integrity-and-eps-20261016.md",
        result=UNIT + "/result.md", environment=dict(python=sys.version.split()[0], platform=platform.platform(),
            jsonschema=importlib.metadata.version("jsonschema"), cpu_gpu="CPU only; CUDA_VISIBLE_DEVICES=-1; no GPU initialization",
            tex="existing LuaLaTeX/latexmk, trusted font-cache context; no installation"),
        commands=["CUDA_VISIBLE_DEVICES=-1 python3 " + UNIT + "/ordered-eps/verify.py",
            "python3 " + UNIT + "/prepare_manuscript.py",
            "latexmk -lualatex -g -interaction=nonstopmode -halt-on-error accounting-product-proposal.tex",
            "CUDA_VISIBLE_DEVICES=-1 python3 " + UNIT + "/check_manuscript.py",
            "python3 " + UNIT + "/finalize_records.py records"],
        data_version="frozen authored-input-lock.json; historical EU2023/1803-original-IAS33; protected Version3.14",
        random_seeds="N/A: deterministic exact rational enumeration",
        wall_seconds=dict(reference_verification=checks["wall_seconds"], manuscript_build=None),
        wall_time_limit="Build wall time was not captured; process exit/log and exact PDF are retained.",
        candidate_pdf=report["candidate_pdf"], candidate_pdf_sha256=report["pdf_sha256"], pages=report["pages"],
        outputs=[UNIT + "/ordered-eps/attempt-01", UNIT + "/manuscript-checks.json", UNIT + "/rendered-review.json", UNIT + "/assessment-successor.json"],
        files=[dict(path=str(p.relative_to(ROOT)), sha256=sha(p)) for p in sorted((OUT / "ordered-eps").glob("*")) if p.is_file()],
        readiness="not_ready", independent_review="pending", human_domain_acceptance="pending")
    write("run-manifest.json", manifest)
    # Normalize spacing in newly authored operational prose; frozen inputs stay untouched.
    for name in ("result.md", "requirements-successor.md", "r03-route-successor.md"):
        p = OUT / name
        text = p.read_text()
        import re
        text = re.sub(r"\b(Version|attempt|all|All|The|pages|EPS|six|five|seven|eight)(?=\d)", r"\1 ", text)
        p.write_text(text)
    print(json.dumps(dict(assessment_rows=len(current["rows"]), affected_rows=len(affected),
        old_packet_mismatches=len(mismatches), head=head, index_entries=len(index.splitlines()))))


def controls():
    report = json.loads((OUT / "manuscript-checks.json").read_text())
    pdf, digest = report["candidate_pdf"], report["pdf_sha256"]
    packet = ROOT / "data/accounting-master/review-packet-ordered-eps-20261016/packet.json"
    packet_hash = sha(packet) if packet.is_file() else "pending: packet assembly follows this control snapshot"
    checkpoint = f"""# Accounting master checkpoint

Updated 16 October 2026 (Asia/Hong_Kong). Full readiness is **not_ready**.
The current proposal is **Version 3.15, 353 pages**:
`{pdf}`
SHA256 `{digest}`.
Runtime, empirical campaigns, installation and the former controller remain held.

## Current result and next work

OrderedEPS/1 attempt 01 passes 13,325 documentary checks, zero failures:
12 independently authored examples, 52 adverse inputs and 3,240 additive cases
checked against 25,920 subsets. It specifies exact ordered multi-series EPS
under fixed independent effects, preserves signed continuing-operation control,
and refuses incomplete or unsupported inputs. It is a report, not a book mutation.
Broader participating rights, interacting instruments and real admission remain open.

Version 3.15 preserves all 112 actual Version 3.14 source files and all inherited
equations/citations/qualifications. Its 344 preservation/structural checks pass.
Ten changed/boundary pages received incremental visual inspection. The layout
and directional-reference repairs are preserved; human comprehension remains pending.
Result, manifest, all-53 scoped successor and residual route:
`{UNIT}/`.

The old review packet has three stale live-control hashes and remains unchanged.
The successor uses immutable input snapshots at
`data/accounting-master/review-packet-ordered-eps-20261016/packet.json`
SHA256 `{packet_hash}`.
Its verification after this live-control change is recorded in
`{UNIT}/packet-verification-after-controls.json`.
Independent technical and human/domain review remain pending.

**Next:** execute the audited company/conversion/tax/share/EPS bridge in
`docs/plans/accounting-company-eps-join-20261016.md`. First inspect the independent
P5 calculation and explicit tax bases/share premises. The existing matured
convertible keeps its original terms; a new July issue is a separate extension.
Then continue ready methods in the scoped R03 route. Review pending is not a
continuation veto.

Prior documentary evidence remains P5 CompanyComposition/1: 681 checks;
P2 CorporateResiduals/1: 5,608; P3a2 FinancingComponents/2: 19,815, all with
zero reported failures within their scopes. R03 residual audits, R04/R06
reconciliation and the Version 3.14 R07/R08 records remain preserved historical
evidence. None closes the original corporate/financing/bank/group/insurance rows.

## Continuity

Current master: `docs/plans/accounting-master-current.md`.
Direct action: `data/accounting-master/next-plan.md`.
HEAD `03fea070f089821f4759e49a4466a3399b7fc078`, branch `main`.
The index is empty; cached raw-diff SHA256 is
`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.
The earlier HEAD/100-staged-entry descriptions are historical, not current.
No commit was made in this unit. Unrelated work and the index are preserved.
Earlier controls are snapshotted under `{UNIT}/snapshots/`.
Original requirements, catalog/controller/corpus records and frozen release
hashes remain unchanged. No publication, outreach or paid review is authorized.
"""
    master = f"""# Current accounting proposal master program

16 October 2026. Complete the governing proposal under MC01–MC35/G1–G18.
Current candidate: **Version 3.15, 353 pages; not_ready**. Exact PDF and hash
are in the master checkpoint. Runtime P00–P14, empirical work, installations
and the former controller remain held; current work is documentary.

## Current evidence

OrderedEPS/1 now has a closed independent-additive report contract, preserved
expected examples, signed/tie/date/refusal checks and an independent subset
enumeration: 13,325 checks, zero failures. The successor preserves all 112
baseline sources, adds the general derivation and report records, and passes
344 structural/preservation checks plus incremental visual inspection.
Evidence and the scoped all-53 assessment: `{UNIT}/`.
The prior P5 681-check, P2 5,608-check and P3a2 19,815-check results remain
conditional documentary evidence. All original-row promises still govern.

The prior review packet's three mutable-control references were stale. Its
successor snapshots every listed input, including R03 and R04/R06/R07/R08:
`data/accounting-master/review-packet-ordered-eps-20261016/packet.json`.
Use its snapshot paths. Binding verification after control refresh is in
`{UNIT}/packet-verification-after-controls.json`.

## Remaining execution

| Unit | Remaining deliverable | Next action |
|---|---|---|
| R03/P5 company join | Actual conversion, earnings/tax, share timing and EPS on the checked company; later hedge/sector joins | Execute `docs/plans/accounting-company-eps-join-20261016.md` after its final source/input audit |
| R03/P2 corporate | Wider mixed/loss-making contracts, comparative rebuild, closing methods and source-specific zero-weight CGU rule | Continue supported methods; retain exact refusal where authority is missing |
| R03 financing/sector | Broader participation/dependent conversion, repeated rebalancing/mixed-sign options, bank schedules/POCI/capital and insurance/FX/transition methods | Use `{UNIT}/r03-route-successor.md` and every predecessor original-row reconciliation; do not call a missing method an external-review blocker |
| R04 literature | Broad competitor/forward coverage, four blocked papers and theorem/source gaps; current EPS source/local derivation is recorded | Continue source-specific internal research when a new lead is available |
| R05 validation preparation | Target-specific future inference/forecast/actuarial protocols | Reconcile target/assumption changes; empirical execution remains held |
| R06 selected reuse | Exact transitive dependency/field-loss/fallback decisions and component-specific terms | Preserve the official XBRL route repair; runtime/platform and distribution admission remain unproved |
| R07 integration | Incremental successor evidence is delivered; full technical/semantic consistency and human comprehension remain distinct | Integrate subsequent methods with protected baselines and inspect changed/boundary pages |
| R08 assessment/review | All 53 rows and six interactions retain original obligations; exact snapshot packet prepared | Independent technical review and human/domain acceptance remain pending; continue internal preparation |

R01 corporate wire closure and R02 real-package connection have bounded prior
results. They still require whole-design reconciliation and broader runtime/source
closure; no earlier check count is a completion denominator. Original thirteen
corporate, five financing, seven bank, three group and eight insurance rows remain.
The full predecessor repair queue is
`data/accounting-master/convergence-audit-20261015/repair-queue.md`.

## Execution discipline

Audit each next phase before execution. Preserve the research question,
comparator, criterion, veto/repair roles, defaults and exact evidence. A failed
candidate triggers a retained repair. A missing required source/input blocks
its dependent claim only; continue independent ready work. Human/domain review
is an acceptance condition and does not stop feasible internal preparation.
MC35 requires that preparation before professional referral. No fees, outreach
or publication are authorized.

Preserve original requirement/acceptance text, catalog/controller/P19/corpus
records, old packets and unrelated dirty/staged work. Do not launch or reinitialize
the historical controller. Live controls are this file, the master checkpoint
and `data/accounting-master/next-plan.md`; earlier control bytes are under
`{UNIT}/snapshots/`. Current HEAD/index are in the checkpoint; the old
100-staged-entry descriptions are historical. No continuation veto has fired.
"""
    direct = f"""# Accounting proposal — direct next plan

16 October 2026. Version **3.15**, 353 pages; **not_ready**.
PDF: `{pdf}`
SHA256 `{digest}`.

Completed: OrderedEPS/1 finite independent-additive report, 13,325 checks with
zero failures; protected successor with all 112 baseline sources retained,
344 structural checks and ten-page incremental visual inspection. Results:
`{UNIT}/`. P5/P2/P3a2 predecessor evidence remains intact.

1. Continue `docs/plans/accounting-company-eps-join-20261016.md`: inspect P5's
   independent calculation, tax bases and share premises; lock independent
   expected statements before implementing the documentary join.
2. Connect a separately issued convertible's actual entries and tax to parent
   earnings, dated shares and read-only EPS, preserving the matured base debt.
3. Integrate only a passing joined result in a protected successor, refresh
   the original-row/MC assessment, and repair the next ready R03 phase.
4. Preserve the broader method/fact/authority residuals in
   `{UNIT}/r03-route-successor.md` and the original-row reconciliations.

The former packet has three stale control bindings; its immutable successor is
`data/accounting-master/review-packet-ordered-eps-20261016/packet.json`.
Verification after this control change:
`{UNIT}/packet-verification-after-controls.json`.
Independent technical/human/domain review remains pending and does not stop
internal work. Runtime/controller, installations, empirical campaigns,
publication, outreach and paid review remain held. No continuation veto fired.
Full program: `docs/plans/accounting-master-current.md`.
"""
    for path, text in (("docs/plans/accounting-master-checkpoint.md", checkpoint),
                       ("docs/plans/accounting-master-current.md", master),
                       ("data/accounting-master/next-plan.md", direct)):
        (ROOT / path).write_text(text)
    print(json.dumps(dict(refreshed_controls=3, version="3.15", next="company/conversion/tax/share/EPS join")))


if __name__ == "__main__":
    {"records": records, "controls": controls}[sys.argv[1]]()
