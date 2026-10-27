"""Freeze the structural JPMorgan section map and relocated live controls."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
read = lambda p: json.loads(p.read_text())
rel = lambda p: str(p.relative_to(ROOT))


def save(name, data):
    with (OUT / name).open("x") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def verify(mapping):
    bad = [p for p, h in mapping.items()
           if not (ROOT / p).is_file() or sha(ROOT / p) != h]
    assert not bad, bad[:5]


def main():
    started, tick = datetime.now(timezone.utc).isoformat(), time.monotonic()
    base = read(OUT / "baseline.json")
    priorpath = ROOT / base["prior_manifest"]
    prior = read(priorpath)
    assert sha(priorpath) == base["prior_manifest_sha256"] == read(
        priorpath.with_name("completion.json"))["manifest_sha256"]
    reloc = {x["historical_path"]: x["preserved_path"]
             for x in base["pointer_relocations"]}
    inherited = {reloc.get(p, p): h for p, h in prior["artifact_hashes"].items()}
    verify(inherited)

    checks = read(OUT / "checks.json")
    assert checks["passed"] == 24 and checks["failed"] == 0
    assert checks["checker_sha256"] == sha(OUT / "check_sections.py")
    verify(checks["inputs"])
    pdf = base["pdf"]
    assert sha(ROOT / pdf["path"]) == pdf["sha256"]

    pointers = {p: sha(ROOT / p) for p in reloc}
    for p in pointers:
        body = (ROOT / p).read_text()
        for token in [
            "Version 2.26",
            pdf["sha256"],
            "not_ready",
            "accounting-package-section-map-20261011/result.md",
            "24",
        ]:
            assert token in body, (p, token)

    current = (ROOT / "docs/plans/accounting-master-current.md").read_text()
    previous = (ROOT / reloc["docs/plans/accounting-master-current.md"]).read_text()
    gaps = lambda s: [x for x in s.splitlines() if re.match(r"^\| G\d+ ", x)]
    assert len(gaps(current)) == 18 and gaps(current) == gaps(previous)
    for label, target in [
        ("Latest substantive result", OUT / "result.md"),
        ("Current manuscript", ROOT / pdf["path"]),
    ]:
        line = next(x for x in current.splitlines() if x.startswith(label + ": "))
        link = re.search(r"\]\(([^)]+)\)", line).group(1)
        assert (ROOT / "docs/plans" / link).resolve() == target.resolve()

    plan = "docs/plans/accounting-package-section-map-20261011.md"
    cmd = ["git", "diff", "--check", "--", *pointers, rel(OUT), plan]
    subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                   text=True).strip()
    assert head == base["git_commit"]

    save("closeout-checks.json", dict(
        passed=True,
        prior_references=len(inherited),
        documentary_checks=24,
        current_pointer_hashes=pointers,
        eighteen_gap_rows_unchanged=True,
        current_links_correct=True,
        scoped_diff_check="passed",
        manuscript_unchanged=True,
    ))

    hashes = dict(inherited)
    hashes.update(checks["inputs"])
    hashes.update(pointers)
    hashes.update({rel(p): sha(p) for p in OUT.rglob("*")
                   if p.is_file() and "__pycache__" not in p.parts
                   and p.name not in {"run-manifest.json", "completion.json"}})
    hashes[plan] = sha(ROOT / plan)
    hashes[base["prior_manifest"]] = sha(priorpath)
    hashes[rel(priorpath.with_name("completion.json"))] = sha(
        priorpath.with_name("completion.json"))
    verify(hashes)

    save("run-manifest.json", dict(
        recorded_at=datetime.now(timezone.utc).isoformat(),
        unit="JPMorgan omitted-section structural map E01/MC01/MC03/MC05/MC28/MC30/MC33–35",
        git_commit=head,
        git_worktree="Unrelated dirty work preserved; no commit or push",
        plan=plan,
        result=rel(OUT / "result.md"),
        pdf=pdf,
        manuscript_changed=False,
        artifact_hashes=hashes,
        prior_manifest=base["prior_manifest"],
        prior_manifest_sha256=base["prior_manifest_sha256"],
        pointer_relocations=base["pointer_relocations"],
        commands=[
            dict(command="CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 "
                         + rel(OUT / "check_sections.py"),
                 exit_code=0, wall_seconds=checks["wall_seconds"]),
            dict(command=cmd, exit_code=0),
            dict(command="CUDA_VISIBLE_DEVICES=-1 /home/chakwong/miniconda3/envs/tfgpu/bin/python3 "
                         + rel(Path(__file__)), started_at=started, exit_code=0),
        ],
        environment=dict(
            python_executable=sys.executable,
            python_prefix=sys.prefix,
            python_version=sys.version,
            platform=platform.platform(),
            conda_env="tfgpu executable selected directly",
            CUDA_VISIBLE_DEVICES="-1",
            cpu_gpu_status="CPU only; no model imports",
        ),
        data_version="JPMorgan selected annuals, complete issuer 10-K candidates and regulator event records 2022–2025",
        random_seeds="N/A documentary source preparation",
        wall_seconds=dict(validation=checks["wall_seconds"],
                          closeout_through_manifest=time.monotonic() - tick,
                          full_interactive_elapsed=None),
        network_requests=0,
        model_weights_downloaded=False,
        full_readiness="not_ready",
        independent_reader="pending",
        human_acceptance="pending",
        domain_acceptance="pending",
        distribution_admission=False,
        new_pdf_review=False,
    ))
    verify(hashes)
    save("completion.json", dict(
        status="bounded_source_unit_complete",
        manifest_sha256=sha(OUT / "run-manifest.json"),
        manifest_bound_files=len(hashes),
        pdf=pdf,
        checks=24,
        full_readiness="not_ready",
        next_work="Semantic annotation of omitted JPMorgan Item 1/1A and ending filing sections",
    ))
    print(json.dumps(dict(
        manifest_bound_files=len(hashes),
        manifest_sha256=sha(OUT / "run-manifest.json"),
        checks=24,
        pages=pdf["pages"],
    )) )


if __name__ == "__main__":
    assert os.environ.get("CUDA_VISIBLE_DEVICES") == "-1"
    assert not (OUT / "completion.json").exists()
    main()
