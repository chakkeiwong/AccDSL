"""Observe exact local bytes now; never infer an earlier public release."""
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path

U=Path(__file__).resolve().parent
R=U.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
bind=lambda p:{'path':str(p.relative_to(R)),'sha256':sha(p)}

def main():
    assert os.environ['CUDA_VISIBLE_DEVICES']=='-1'
    assert not (U/'observations.json').exists()
    coverage=R/'data/financial-report-benchmark/coverage.json'
    historical=R/'data/accounting-master/r05-vintage-admission-20261018/reconciliation.json'
    rows=json.loads(coverage.read_text())['rows']
    old={r['document_id']:r for r in json.loads(historical.read_text())['rows']}
    observations=[]
    for index,row in enumerate(rows):
        previous=old[row['document_id']]
        assert previous['as_of_admission'] is False and previous['selected_byte_available_at'] is None
        path=R/row['local_path']
        start=datetime.now(timezone.utc)
        digest=hashlib.sha256(path.read_bytes()).hexdigest()
        end=datetime.now(timezone.utc)
        assert start<=end and digest==row['sha256'],row['document_id']
        observations.append({'document_id':row['document_id'],'issuer_id':row['issuer_id'],
            'original':{'path':row['local_path'],'sha256':digest},'source_url':row['source_url'],
            'coverage_pointer':f'/rows/{index}',
            'read_started_utc':start.isoformat(),'read_finished_utc':end.isoformat(),
            'observation':'exact bytes read by the research process within these local-clock bounds',
            'historical_selected_byte_available_at':None,'historical_as_of_admission':False,
            'first_public_release_verified':False,'prospective_information_policy_admission':False,
            'forecast_issued':False})
    value={'scope':'current local byte observation; not a public historical timestamp certificate',
        'coverage':bind(coverage),'historical_ledger':bind(historical),'rows':observations,
        'clock':'Python datetime.now(timezone.utc); session clock cross-check recorded separately',
        'user_decision':{'question':'For E3, which evidence route should the plan develop? Historical comparisons still need exact source vintages and an assumption connecting past and future performance. Prospective confirmation requires forecasts fixed before future fiscal years and waiting for those outcomes.',
                         'answer':'Historical development, then prospective confirmation (recommended)',
                         'source':'user reply in this session,23October2026',
                         'selected_route':'historical_development_then_prospective_confirmation'},
        'all_prior_design_choices_preserved':True,'empirical_execution':False}
    with (U/'observations.json').open('x') as f:json.dump(value,f,indent=2);f.write('\n')
    print(json.dumps({'observed_files':len(observations),'issuers':len({r['issuer_id'] for r in observations}),
        'first_read_started_utc':observations[0]['read_started_utc'],
        'last_read_finished_utc':observations[-1]['read_finished_utc'],
        'historical_admissions':0,'prospective_policy_admissions':0}))

if __name__=='__main__':main()
