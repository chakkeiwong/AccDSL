"""Extend fixed review evidence without recopying immutable predecessor inputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PACKET = ROOT / 'data/accounting-master/review-packet-company-tax-20261016'
PREVIOUS = ROOT / 'data/accounting-master/review-packet-ordered-eps-20261016'
CONTROLS = {'docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md'}


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, value):
    assert not p.exists(), str(p)
    p.write_text(json.dumps(value, indent=2) + '\n')


def assemble():
    started = time.monotonic()
    assert not PACKET.exists()
    prior = json.loads((PREVIOUS / 'packet.json').read_text())
    prior_manifest = json.loads((PREVIOUS / 'run-manifest.json').read_text())
    assert sha(PREVIOUS / 'packet.json') == prior_manifest['packet_sha256']
    entries = {}
    for item in prior['evidence_files']:
        assert sha(ROOT / item['snapshot_path']) == item['sha256']
        entries[item['origin_path']] = dict(item, inherited_snapshot=True)
    chosen = {ROOT / p for p in CONTROLS}
    chosen.update(ROOT / p for p in (
        'docs/plans/accounting-company-eps-join-20261016.md',
        'docs/plans/accounting-compound-tax-basis-20261016.md',
        'docs/plans/accounting-compound-tax-rollforward-20261016.md'))
    directories = [ROOT / 'data/accounting-master' / n for n in (
        'company-eps-join-20261016', 'compound-tax-basis-20261016', 'company-tax-assessment-20261016')]
    excluded = {'baseline-sources', 'controls-before', '__pycache__', 'source-attempts', 'manuscript-attempt-01'}
    for directory in directories:
        for p in directory.rglob('*'):
            parts = p.relative_to(directory).parts
            if p.is_file() and not any(x in excluded or x.startswith('render-attempt-') for x in parts) and p.suffix in {'.md','.json','.py','.tex','.log'}:
                chosen.add(p)
        render = directory / 'render-manifest.json'
        if render.exists():
            chosen.update(ROOT / item['path'] for item in json.loads(render.read_text())['pages'])
    ms = json.loads((directories[1] / 'manuscript-checks.json').read_text())
    candidate = ROOT / ms['pdf']
    chosen.update(p for p in candidate.parent.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark','.pdf','.log'})
    PACKET.mkdir()
    for source in sorted(chosen):
        origin = str(source.relative_to(ROOT))
        snapshot = PACKET / 'inputs' / origin
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, snapshot)
        assert sha(source) == sha(snapshot)
        entries[origin] = dict(origin_path=origin, snapshot_path=str(snapshot.relative_to(ROOT)), sha256=sha(snapshot),
            bytes=snapshot.stat().st_size, inherited_snapshot=False,
            role='frozen_live_control' if origin in CONTROLS else 'fixed_review_input')
    record = dict(created_utc=datetime.now(timezone.utc).isoformat(), candidate_version='3.17',
        candidate_origin=ms['pdf'], candidate_pdf=entries[ms['pdf']]['snapshot_path'], candidate_pdf_sha256=sha(candidate),
        predecessor=str((PREVIOUS / 'packet.json').relative_to(ROOT)), predecessor_sha256=sha(PREVIOUS / 'packet.json'),
        evidence_files=sorted(entries.values(), key=lambda x:x['origin_path']),
        review_questions=[
            'Verify maturity-company legal/group tax, NCI, cash and daily share/EPS reconciliation against independent expectations.',
            'Verify IAS12.23 issue-date equity charge; preserve later fiscal/earnings and early-conversion source gaps.',
            'Preserve all53 MC/G obligations, all original domain rows, R03 route and R04/R06/R07/R08 limits.',
            'Check the exact manuscript addition and preserved source argument; human comprehension remains separately pending.'],
        status='prepared_for_independent_review', independent_review='pending', human_domain_acceptance='pending', mission_readiness='not_ready',
        resolver='Use snapshot_path. Inherited entries retain their original immutable snapshot locations; no listed input resolves through a live control.',
        scope='Exact listed review inputs and inherited fixed snapshots, not a complete transitive archive of all cited sources or dependencies.',
        nonclaims=['runtime conformance','current-law compliance','human acceptance','empirical validation','whole-mission readiness'])
    write(PACKET / 'packet.json', record)
    write(PACKET / 'run-manifest.json', dict(created_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip(),
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-tax-assessment-20261016/packet.py assemble',
        interpreter=sys.executable, environment='tfgpu Python standard library; filesystem only; no framework import',
        gpu_status='intentionally hidden with CUDA_VISIBLE_DEVICES=-1', random_seeds='N/A deterministic file binding',
        data_version='3.17 candidate and accepted company/tax evidence plus fixed predecessor inputs',
        plan='data/accounting-master/company-tax-assessment-20261016/audit.md',
        result='data/accounting-master/company-tax-assessment-20261016/requirements-successor.md',
        wall_seconds=round(time.monotonic()-started,3), packet_sha256=sha(PACKET / 'packet.json'),
        inputs=len(entries), new_snapshots=len(chosen), output=str((PACKET / 'packet.json').relative_to(ROOT))))
    print(json.dumps(dict(inputs=len(entries), new_snapshots=len(chosen), sha256=sha(PACKET / 'packet.json'))))


def verify(tag):
    packet = json.loads((PACKET / 'packet.json').read_text())
    manifest = json.loads((PACKET / 'run-manifest.json').read_text())
    checks = []
    def check(name, ok):
        checks.append(dict(name=name, passed=bool(ok)))
    check('packet-binding', sha(PACKET / 'packet.json') == manifest['packet_sha256'])
    check('predecessor-packet', sha(ROOT / packet['predecessor']) == packet['predecessor_sha256'])
    differences = []
    for item in packet['evidence_files']:
        check(item['snapshot_path'], sha(ROOT / item['snapshot_path']) == item['sha256'])
        if not item['inherited_snapshot'] and sha(ROOT / item['origin_path']) != item['sha256']:
            differences.append(item['origin_path'])
    check('candidate', sha(ROOT / packet['candidate_pdf']) == packet['candidate_pdf_sha256'])
    saved = json.loads((OUT / 'preservation.json').read_text())
    check('git-head', subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip() == saved['head'])
    check('git-index', hashlib.sha256(subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'], cwd=ROOT)).hexdigest() == saved['cached_raw_sha256'])
    for item in saved['controls']:
        check('old-control/'+item['path'], sha(OUT / 'controls-before' / item['path']) == item['sha256'])
    if tag == 'after-controls':
        check('actual-live-checkpoint-change', 'docs/plans/accounting-master-checkpoint.md' in differences)
        check('only-live-controls-changed', set(differences) <= CONTROLS)
    result = dict(checks=len(checks), failures=sum(not c['passed'] for c in checks), detail=checks,
                  live_origin_differences=differences, packet_sha256=sha(PACKET / 'packet.json'),
                  scope='listed fixed input integrity only; no independent content acceptance')
    write(OUT / ('packet-verification-'+tag+'.json'), result)
    print(json.dumps({k:result[k] for k in ('checks','failures','live_origin_differences')}))
    if result['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    assemble() if sys.argv[1] == 'assemble' else verify(sys.argv[1])
