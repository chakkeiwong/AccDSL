"""Preserve original obligations and record the two completed documentary deltas."""
from copy import deepcopy
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
PREVIOUS = ROOT / 'data/accounting-master/continuation-integrity-eps-20261016/assessment-successor.json'
CONTROLS = ('docs/plans/accounting-master-current.md', 'docs/plans/accounting-master-checkpoint.md', 'data/accounting-master/next-plan.md')


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p, obj):
    assert not p.exists(), str(p)
    p.write_text(json.dumps(obj, indent=2) + '\n')


def main():
    start = time.monotonic()
    saved = []
    for name in CONTROLS:
        target = OUT / 'controls-before' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        assert not target.exists()
        shutil.copy2(ROOT / name, target)
        saved.append(dict(path=name, sha256=sha(target)))
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    index = subprocess.check_output(['git', 'diff', '--cached', '--raw', '--no-abbrev'], cwd=ROOT)
    write(OUT / 'preservation.json', dict(head=head, cached_raw_sha256=hashlib.sha256(index).hexdigest(), controls=saved))
    prior = json.loads(PREVIOUS.read_text())
    new = deepcopy(prior)
    ms = json.loads((ROOT / 'data/accounting-master/compound-tax-basis-20261016/manuscript-checks.json').read_text())
    assert ms['failures'] == 0
    new.update(candidate_version='3.17', candidate_pdf=ms['pdf'], candidate_pdf_sha256=ms['pdf_sha256'],
               predecessor=str(PREVIOUS.relative_to(ROOT)), predecessor_sha256=sha(PREVIOUS),
               assessment_scope='scoped company/EPS and initial-tax delta; unchanged rows inherited')
    affected = {'MC02','MC04','MC05','MC06','MC13','MC15','MC16','MC17','MC19','MC24','MC25','MC28','MC30','MC32','MC33','MC34','MC35',
                'G2','G4','G7','G12','G13','G15','G18'}
    evidence = [dict(path=p, sha256=sha(ROOT / p)) for p in (
        'data/accounting-master/company-eps-join-20261016/result.md',
        'data/accounting-master/company-eps-join-20261016/attempt-03/summary.json',
        'data/accounting-master/compound-tax-basis-20261016/result.md',
        'data/accounting-master/compound-tax-basis-20261016/attempt-01/summary.json',
        'data/accounting-master/compound-tax-basis-20261016/manuscript-result.md')]
    for row in new['rows']:
        row['previous_candidate_version'] = '3.15'
        row.update(candidate_version='3.17', candidate_pdf=ms['pdf'], candidate_pdf_sha256=ms['pdf_sha256'])
        row['delta_assessment'] = ('CompanyEPSJoin/1 maturity conversion/redemption, legal/group tax/NCI/cash and dated EPS are checked under matching fiscal bases. CompoundTaxBasis/1 separately checks the issue-date equity charge for the combined-proceeds tax base. Early-conversion measurement and subsequent differing-base tax/EPS are still open.'
            if row['id'] in affected else 'Inherited judgment preserved; not freshly reviewed in this unit.')
        if row['id'] in affected:
            row.setdefault('evidence_updates', []).extend(deepcopy(evidence))
    for item in new['interactions']:
        if item['id'] in ('I03', 'I06'):
            item['delta'] = 'Finite maturity company/EPS join delivered under matching fiscal bases. Initial combined-proceeds tax base separately derived; subsequent fiscal schedule, early conversion and wider FX/sector joins remain open.'
    checks = [dict(name='all-53-original-rows', passed=len(new['rows']) == 53),
              dict(name='six-original-interactions', passed=len(new['interactions']) == 6)]
    for a, b in zip(prior['rows'], new['rows']):
        checks.append(dict(name=a['id']+'/original-obligation', passed=all(a[k] == b[k] for k in ('id','label','original_obligation','acceptance'))))
    write(OUT / 'assessment-successor.json', new)
    write(OUT / 'assessment-checks.json', dict(checks=len(checks), failures=sum(not c['passed'] for c in checks), detail=checks))
    write(OUT / 'run-manifest.json', dict(recorded_utc=datetime.now(timezone.utc).isoformat(), git_commit=head,
        command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/company-tax-assessment-20261016/prepare.py',
        interpreter=sys.executable, environment='tfgpu Python; standard-library document maintenance only',
        gpu_status='intentionally hidden with CUDA_VISIBLE_DEVICES=-1', random_seeds='N/A deterministic obligation preservation',
        data_version='3.15 assessment plus accepted 3.16/3.17 evidence', wall_seconds=round(time.monotonic()-start, 3),
        plan='data/accounting-master/company-tax-assessment-20261016/audit.md',
        result='data/accounting-master/company-tax-assessment-20261016/requirements-successor.md',
        output_paths=['data/accounting-master/company-tax-assessment-20261016/assessment-successor.json','data/accounting-master/company-tax-assessment-20261016/assessment-checks.json']))
    print(json.dumps(dict(rows=53, checks=len(checks), failures=sum(not c['passed'] for c in checks), head=head)))


if __name__ == '__main__':
    main()
