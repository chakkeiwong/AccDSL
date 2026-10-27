"""Freeze this documentary increment without re-running predecessor closeouts."""
from copy import deepcopy
from datetime import datetime,timezone
from pathlib import Path
import hashlib
import json
import shutil
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PRIOR=ROOT/'data/accounting-master/rate-interval-propagation-20261017'
SOURCE=ROOT/'data/accounting-master/dependent-eps-source-selection-20261017'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p,value):
    assert not p.exists(),p
    p.write_text(json.dumps(value,indent=2)+'\n')


def main():
    assert not (OUT/'review-delta.json').exists(),'Do not rerun frozen closeout'
    ms=json.loads((OUT/'manuscript-checks.json').read_text())
    assert ms['failures']==0
    assert json.loads((OUT/'attempt-01/checks.json').read_text())['failures']==0
    assert json.loads((SOURCE/'selection-checks.json').read_text())['passed']
    review=json.loads((OUT/'rendered-review.json').read_text())
    assert review['status']=='incremental_author_inspection_complete' and review['pdf_sha256']==ms['pdf_sha256']
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        assert sha(ROOT/row['path'])==row['sha256'],row['path']
    index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
    controls=[]
    for name in ('docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md'):
        dest=OUT/'controls-before'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/name,dest)
        controls.append(dict(path=name,sha256=sha(dest)))
    write(OUT/'preservation.json',dict(date=datetime.now(timezone.utc).isoformat(),controls=controls,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        index_sha256=hashlib.sha256(index).hexdigest()))
    prior=json.loads((PRIOR/'assessment-successor.json').read_text());new=deepcopy(prior)
    delta='Primary IAS 33 examples preserve the unresolved nonadditive-selection boundary. ParticipatingTaxEPS/1 now specifies the source-supported ordinary-only distribution-tax allocation, including signed prior-period reversals and profit/equity recognition-location equivalence. 624 deterministic checks pass. Wider tax rights, actual law and diluted selection remain open.'
    new.update(date='2026-10-17',candidate_version='3.39',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor=str((PRIOR/'assessment-successor.json').relative_to(ROOT)),predecessor_sha256=sha(PRIOR/'assessment-successor.json'),
        assessment_scope=delta)
    affected={'MC02','MC05','MC06','MC16','MC17','MC24','MC26','MC29','MC30','MC32','MC33','MC34','MC35','G2','G3','G7','G8','G10'}
    evidence=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in
        (OUT/'result.md',OUT/'attempt-01/checks.json',OUT/'derivation.md',OUT/'manuscript-result.md',SOURCE/'source-reading.md',SOURCE/'result.md')]
    for row in new['rows']:
        row.update(previous_candidate_version=prior['candidate_version'],candidate_version='3.39',
            candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
            delta_assessment=delta if row['id'] in affected else 'Inherited judgment; not freshly reviewed.')
        if row['id'] in affected:row.setdefault('evidence_updates',[]).extend(deepcopy(evidence))
    for row in new['interactions']:
        if row['id']=='I06':
            row['delta']+=' ParticipatingTaxEPS/1 separately attributes hypothetical distribution-tax benefits in basic EPS; it creates no tax or dividend journal and is not a new company-law treatment.'
    checks=[dict(name=a['id'],passed=all(a[k]==b[k] for k in ('id','label','original_obligation','acceptance','recorded_status','historical_status')))
        for a,b in zip(prior['rows'],new['rows'])]
    checks.extend([dict(name='all53',passed=len(new['rows'])==53),dict(name='six-interactions',passed=len(new['interactions'])==6 and
        all(all(a[k]==b[k] for k in ('id','question','status')) for a,b in zip(prior['interactions'],new['interactions'])))])
    assert all(c['passed'] for c in checks)
    write(OUT/'assessment-successor.json',new)
    write(OUT/'assessment-checks.json',dict(checks=len(checks),failures=0,detail=checks))
    ledger=ROOT/'data/accounting-master/method-residual-reconciliation-20261016/residual-ledger.json'
    operations=deepcopy(json.loads(ledger.read_text()))
    operations.update(candidate_version='3.39',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor=str(ledger.relative_to(ROOT)),predecessor_sha256=sha(ledger))
    for row in operations['rows']:
        if row['id']=='P17-05.04':
            row['current_increment']=delta;row['evidence'].extend(deepcopy(evidence));row['full_requirement_closed']=False
    assert len(operations['rows'])==46
    write(OUT/'operation-successor.json',operations)
    candidate=(ROOT/ms['pdf']).parent
    excluded={'baseline-sources','baseline-render','controls-before','render-attempt-01','__pycache__'}
    files=[p for p in OUT.rglob('*') if p.is_file() and not any(x in excluded for x in p.relative_to(OUT).parts)]
    files += [p for p in SOURCE.iterdir() if p.is_file()]
    files += [p for p in candidate.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}]
    files += [ROOT/ms['pdf'],ROOT/'docs/plans/accounting-participating-tax-allocation-20261017.md',
              ROOT/'docs/plans/accounting-dependent-eps-source-selection-20261017.md']
    write(OUT/'review-delta.json',dict(version='3.39',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor_delta=str((PRIOR/'review-delta.json').relative_to(ROOT)),predecessor_sha256=sha(PRIOR/'review-delta.json'),
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(set(files))],
        scope='This increment and predecessor pointer; no repeated frozen closeout or transitive archive claim',
        readiness='not_ready',independent_review='pending',human_acceptance='pending'))
    assert subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==index
    frozen=json.loads((OUT/'review-delta.json').read_text())
    integrity=[sha(ROOT/r['path'])==r['sha256'] for r in frozen['files']]
    integrity.append(sha(ROOT/frozen['predecessor_delta'])==frozen['predecessor_sha256'])
    for r in json.loads((OUT/'render-manifest.json').read_text())['pages']:
        integrity.append(sha(ROOT/r['path'])==r['sha256'])
    assert all(integrity)
    write(OUT/'review-delta-checks.json',dict(checks=len(integrity),failures=0,delta_sha256=sha(OUT/'review-delta.json')))
    print(json.dumps(dict(version='3.39',assessment_checks=len(checks),fixed_files=len(frozen['files']),integrity_checks=len(integrity),failures=0)))


if __name__=='__main__':main()
