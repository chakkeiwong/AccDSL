"""Bind the completed insurance service and finance origins and preserve the full obligation ledger."""
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
PRIOR=ROOT/'data/accounting-master/dated-credit-schedules-20261016'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def write(p,value):
    assert not p.exists(),p
    p.write_text(json.dumps(value,indent=2)+'\n')


def verify_delta(path):
    d=json.loads(path.read_text());checks=[]
    for item in d['files']:
        checks.append(dict(name=item['path'],passed=sha(ROOT/item['path'])==item['sha256']))
    checks.append(dict(name='predecessor',passed=sha(ROOT/d['predecessor_delta'])==d['predecessor_sha256']))
    render=json.loads((path.parent/'render-manifest.json').read_text())
    for item in render['pages']:
        checks.append(dict(name='render/'+str(item['page']),passed=sha(ROOT/item['path'])==item['sha256']))
    return dict(checks=len(checks),failures=sum(not x['passed'] for x in checks),detail=checks,delta_sha256=sha(path))


def main():
    prior_check=verify_delta(PRIOR/'review-delta.json')
    assert prior_check['failures']==0
    if (OUT/'predecessor-integrity.json').exists():
        assert json.loads((OUT/'predecessor-integrity.json').read_text())==prior_check
    else:write(OUT/'predecessor-integrity.json',prior_check)
    controls=[]
    for name in ('docs/plans/accounting-master-current.md','docs/plans/accounting-master-checkpoint.md','data/accounting-master/next-plan.md'):
        dest=OUT/'controls-before'/name
        dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert sha(dest)==sha(ROOT/name)
        else:shutil.copy2(ROOT/name,dest)
        controls.append(dict(path=name,sha256=sha(dest)))
    index=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
    preservation=dict(recorded_utc=datetime.now(timezone.utc).isoformat(),
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        index_sha256=hashlib.sha256(index).hexdigest(),controls=controls)
    if (OUT/'preservation.json').exists():
        old=json.loads((OUT/'preservation.json').read_text())
        assert all(old[k]==preservation[k] for k in ('git_commit','index_sha256','controls'))
    else:write(OUT/'preservation.json',preservation)
    prior=json.loads((PRIOR/'assessment-successor.json').read_text());new=deepcopy(prior)
    ms=json.loads((OUT/'manuscript-checks.json').read_text())
    review=json.loads((OUT/'rendered-review.json').read_text())
    assert ms['failures']==0 and ms['pdf_sha256']==review['pdf_sha256']
    assert review['status']=='incremental_author_inspection_complete'
    new.update(date='2026-10-16',candidate_version='3.34',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor=str((PRIOR/'assessment-successor.json').relative_to(ROOT)),predecessor_sha256=sha(PRIOR/'assessment-successor.json'),
        assessment_scope='Insurance loss-service/finance allocation and frozen origin-specific OCI treatment; all53 original obligations and acceptance states retained.')
    affected={'MC02','MC04','MC05','MC11','MC13','MC16','MC19','MC22','MC24','MC25','MC26','MC27','MC28','MC30','MC32','MC33','MC34','MC35','G2','G4','G7','G12','G13','G17','G18'}
    evidence=[dict(path=str((OUT/n).relative_to(ROOT)),sha256=sha(OUT/n)) for n in
        ('result.md','attempt-02/checks.json','semantic-contract.md','manuscript-result.md')]
    delta='InsuranceOrigins/1 checks multiperiod loss allocations, held recovery non-duplication, both frozen B135 switch directions and homogeneous paragraph91 OCI origins. Eleven cases and88 adverse requests preserve actual-vs-frozen assumptions and source limits. Mixed-origin early termination and wider compositions remain open.'
    for row in new['rows']:
        row.update(previous_candidate_version=prior['candidate_version'],candidate_version='3.34',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
            delta_assessment=delta if row['id'] in affected else 'Inherited judgment; not freshly reviewed.')
        if row['id'] in affected:row.setdefault('evidence_updates',[]).extend(deepcopy(evidence))
    for item in new['interactions']:
        if item['id'] in ():item['delta']=delta
    checks=[dict(name=a['id'],passed=all(a[k]==b[k] for k in ('id','label','original_obligation','acceptance','recorded_status','historical_status')))
        for a,b in zip(prior['rows'],new['rows'])]
    checks.extend([dict(name='all53',passed=len(new['rows'])==53),dict(name='six-interactions',passed=len(new['interactions'])==6 and
        all(all(a[k]==b[k] for k in ('id','question','status')) for a,b in zip(prior['interactions'],new['interactions'])))])
    assert all(c['passed'] for c in checks)
    write(OUT/'assessment-successor.json',new)
    write(OUT/'assessment-checks.json',dict(checks=len(checks),failures=0,detail=checks))
    excluded={'baseline-sources','controls-before','__pycache__'}
    files=[p for p in OUT.rglob('*') if p.is_file() and not any(x in excluded or x.startswith('render-attempt-') for x in p.relative_to(OUT).parts)]
    candidate=(ROOT/ms['pdf']).parent
    files += [p for p in candidate.rglob('*') if p.is_file() and p.suffix in {'.tex','.bib','.lark'}]
    files += [ROOT/ms['pdf'],ROOT/'docs/plans/accounting-insurance-service-finance-origins-20261016.md']
    write(OUT/'review-delta.json',dict(version='3.34',candidate_pdf=ms['pdf'],candidate_pdf_sha256=ms['pdf_sha256'],
        predecessor_delta=str((PRIOR/'review-delta.json').relative_to(ROOT)),predecessor_sha256=sha(PRIOR/'review-delta.json'),
        files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in sorted(set(files))],
        scope='Fixed new evidence and predecessor delta; render hashes in manifests; mutable controls excluded; no transitive archive claim.',
        independent_review='pending',human_acceptance='pending',readiness='not_ready'))
    checked=verify_delta(OUT/'review-delta.json');assert checked['failures']==0
    write(OUT/'review-delta-checks.json',checked)
    print(json.dumps(dict(assessment_checks=len(checks),fixed_files=len(files),integrity_checks=checked['checks'],failures=0)))


if __name__=='__main__':main()
