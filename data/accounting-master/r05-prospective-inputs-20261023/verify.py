"""Replay source observations without observing new times or writing files."""
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import runpy

U=Path(__file__).resolve().parent
R=U.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())

def check():
    assert os.environ['CUDA_VISIBLE_DEVICES']=='-1'
    runpy.run_path(str(R/'data/accounting-master/r05-eu-ifrs18-20261023/verify.py'))['check']()
    data=load(U/'observations.json')
    for key in ('coverage','historical_ledger'):
        assert sha(R/data[key]['path'])==data[key]['sha256']
    coverage=load(R/data['coverage']['path'])['rows']
    old=load(R/data['historical_ledger']['path'])['rows']
    assert len(data['rows'])==len(coverage)==len(old)==192
    assert all(r['as_of_admission'] is False and r['selected_byte_available_at'] is None for r in old)
    starts=[];ends=[]
    for row,source in zip(data['rows'],coverage):
        assert row['document_id']==source['document_id']
        assert row['issuer_id']==source['issuer_id']
        assert row['original']['path']==source['local_path']
        assert sha(R/row['original']['path'])==row['original']['sha256']==source['sha256']
        a=datetime.fromisoformat(row['read_started_utc']);b=datetime.fromisoformat(row['read_finished_utc'])
        assert a.tzinfo is not None and b.tzinfo is not None and a<=b
        starts.append(a);ends.append(b)
        assert row['historical_selected_byte_available_at'] is None
        for key in ('historical_as_of_admission','first_public_release_verified','prospective_information_policy_admission','forecast_issued'):
            assert row[key] is False
    assert all(ends[i]<=starts[i+1] for i in range(len(ends)-1))
    clock=load(U/'clock-crosscheck.json')
    parse=lambda s:datetime.strptime(s,'%Y-%m-%d %H:%M:%S UTC').replace(tzinfo=starts[0].tzinfo)
    assert parse(clock['session_clock_before'])<=starts[0]<=ends[-1]<=parse(clock['session_clock_after'])
    assert clock['process_first_read_started_utc']==data['rows'][0]['read_started_utc']
    assert clock['process_last_read_finished_utc']==data['rows'][-1]['read_finished_utc']
    assert data['user_decision']['selected_route']=='historical_development_then_prospective_confirmation'
    assert data['empirical_execution'] is False
    checks={'observed_originals':192,'issuers':9,'historical_vintage_admissions':0,
            'prospective_policy_admissions':0,'forecasts_issued':0,'whole_rows_closed':0,'readiness':'not_ready'}
    if (U/'completion.json').exists():
        complete=load(U/'completion.json');assert complete['checks']==checks
        for name,digest in complete['bindings'].items():assert sha(R/name)==digest,name
    return checks

if __name__=='__main__':print(json.dumps({'status':'read-only checks passed',**check()}))
