"""Freeze this documentary increment and preserve its existing control snapshot."""
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PRIOR = ROOT/'data/accounting-master/zero-cost-collar-20261017'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    assert not path.exists(), path
    path.write_text(json.dumps(value, indent=2)+'\n')


def main():
    assert not (OUT/'review-delta.json').exists(), 'Do not repeat frozen closeout'
    ms = json.loads((OUT/'manuscript-checks.json').read_text())
    assert ms['failures'] == 0
    assert json.loads((OUT/'attempt-01/checks.json').read_text())['failures'] == 0
    review = json.loads((OUT/'rendered-review.json').read_text())
    assert review['status'] == 'incremental_author_inspection_complete'
    assert review['pdf_sha256'] == ms['pdf_sha256']
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        assert sha(ROOT/row['path']) == row['sha256'], row['path']
    run = json.loads((OUT/'attempt-01/manifest.json').read_text())
    for path, digest in run['executed_artifacts'].items():
        assert sha(ROOT/path) == digest, path
    index = subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'], cwd=ROOT)
    controls = []
    for name in ('docs/plans/accounting-master-current.md',
                 'docs/plans/accounting-master-checkpoint.md',
                 'data/accounting-master/next-plan.md'):
        snapshot = OUT/'controls-before'/name
        assert snapshot.exists() and sha(snapshot) == sha(ROOT/name), name
        controls.append(dict(path=name, sha256=sha(snapshot)))
    write(OUT/'preservation.json', dict(date=datetime.now(timezone.utc).isoformat(),
        controls=controls, controls_policy='Existing pre-run snapshots verified; never overwritten',
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        index_sha256=hashlib.sha256(index).hexdigest()))
    prior = json.loads((PRIOR/'assessment-successor.json').read_text())
    new = deepcopy(prior)
    delta = ('OriginMatchedCessation/1 preserves one named partial stop in a documented '
        'exact-match multi-origin purchase history. Relationship cumulative lower-of '
        'remains governing; original dates/prices, frozen reserve, post-stop profit, '
        'signed loss/cancellation releases and gross inventory/cash joins reconcile. '
        '1846 deterministic checks pass. General heterogeneous attribution, shared '
        'ineffectiveness and opposed active gains remain open.')
    new.update(date='2026-10-17', candidate_version='3.41', candidate_pdf=ms['pdf'],
        candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor=str((PRIOR/'assessment-successor.json').relative_to(ROOT)),
        predecessor_sha256=sha(PRIOR/'assessment-successor.json'), assessment_scope=delta)
    affected = {'MC02','MC05','MC16','MC17','MC24','MC26','MC29','MC30',
                'MC32','MC33','MC34','MC35','G2','G3','G7','G8','G10'}
    evidence = [dict(path=str(path.relative_to(ROOT)),sha256=sha(path)) for path in
        (OUT/'result.md',OUT/'attempt-01/checks.json',OUT/'semantic-contract.md',
         OUT/'contract-addendum.md',OUT/'manuscript-result.md',OUT/'source-reading.md',
         OUT/'rendered-review.json')]
    for row in new['rows']:
        row.update(previous_candidate_version=prior['candidate_version'], candidate_version='3.41',
            candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
            delta_assessment=delta if row['id'] in affected else 'Inherited judgment; not freshly reviewed.')
        if row['id'] in affected:
            row.setdefault('evidence_updates',[]).extend(deepcopy(evidence))
    for row in new['interactions']:
        if row['id'] == 'I03':
            row['delta'] += (' The finite origin-matched cessation joins named stopped '
                'reserve to gross cash and inventory; it supplies no general unmatched allocation, FX or tax join.')
    checks = [dict(name=a['id'],passed=all(a[key] == b[key] for key in
        ('id','label','original_obligation','acceptance','recorded_status','historical_status')))
        for a,b in zip(prior['rows'],new['rows'])]
    checks.extend([dict(name='all53',passed=len(prior['rows']) == len(new['rows']) == 53),
        dict(name='six-interactions',passed=len(new['interactions']) == 6 and
            all(all(a[key] == b[key] for key in ('id','question','status'))
                for a,b in zip(prior['interactions'],new['interactions'])))])
    assert all(row['passed'] for row in checks)
    write(OUT/'assessment-successor.json',new)
    write(OUT/'assessment-checks.json',dict(checks=len(checks),failures=0,detail=checks))
    previous_operations = json.loads((PRIOR/'operation-successor.json').read_text())
    operations = deepcopy(previous_operations)
    ledger = ROOT/'data/accounting-master/method-residual-reconciliation-20261016/residual-ledger.json'
    operations.update(candidate_version='3.41',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor=str((PRIOR/'operation-successor.json').relative_to(ROOT)),
        predecessor_sha256=sha(PRIOR/'operation-successor.json'),
        original_ledger=str(ledger.relative_to(ROOT)),original_ledger_sha256=sha(ledger))
    for row in operations['rows']:
        if row['id'] == 'P17-05.05':
            assert row['operation'] == 'Benchmark/hedges'
            row['current_increment'] = delta
            row['evidence'].extend(deepcopy(evidence))
            row['full_requirement_closed'] = False
    operation_checks = []
    for before, after in zip(previous_operations['rows'],operations['rows']):
        unchanged = {key:value for key,value in after.items() if key not in ('evidence','current_increment')}
        original = {key:value for key,value in before.items() if key not in ('evidence','current_increment')}
        operation_checks.append(dict(name=before['id'],passed=unchanged == original))
    assert len(operations['rows']) == len(previous_operations['rows']) == 46
    assert all(row['passed'] for row in operation_checks)
    write(OUT/'operation-successor.json',operations)
    write(OUT/'operation-checks.json',dict(checks=len(operation_checks),failures=0,detail=operation_checks))
    candidate = (ROOT/ms['pdf']).parent
    excluded = {'baseline-sources','baseline-render','controls-before','render-attempt-01','__pycache__'}
    files = [path for path in OUT.rglob('*') if path.is_file() and
             not any(part in excluded for part in path.relative_to(OUT).parts)]
    files += [path for path in candidate.rglob('*') if path.is_file() and path.suffix in {'.tex','.bib','.lark'}]
    files += [ROOT/ms['pdf'],ROOT/'docs/plans/accounting-origin-matched-cessation-20261017.md']
    write(OUT/'review-delta.json',dict(version='3.41',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor_delta=str((PRIOR/'review-delta.json').relative_to(ROOT)),
        predecessor_sha256=sha(PRIOR/'review-delta.json'),
        files=[dict(path=str(path.relative_to(ROOT)),sha256=sha(path)) for path in sorted(set(files))],
        scope='This increment and predecessor pointer; no repeated frozen closeout or transitive archive claim',
        readiness='not_ready',independent_review='pending',human_acceptance='pending'))
    assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT) == index
    frozen = json.loads((OUT/'review-delta.json').read_text())
    integrity = [sha(ROOT/row['path']) == row['sha256'] for row in frozen['files']]
    integrity.append(sha(ROOT/frozen['predecessor_delta']) == frozen['predecessor_sha256'])
    for row in json.loads((OUT/'render-manifest.json').read_text())['pages']:
        integrity.append(sha(ROOT/row['path']) == row['sha256'])
    assert all(integrity)
    write(OUT/'review-delta-checks.json',dict(checks=len(integrity),failures=0,delta_sha256=sha(OUT/'review-delta.json')))
    print(json.dumps(dict(version='3.41',assessment_checks=len(checks),operation_checks=len(operation_checks),
        fixed_files=len(frozen['files']),integrity_checks=len(integrity),failures=0)))


if __name__ == '__main__':
    main()
