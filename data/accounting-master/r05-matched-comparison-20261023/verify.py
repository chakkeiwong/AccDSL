"""Read-only finite mathematics and immutable record replay."""
import hashlib
import json
import os
from pathlib import Path
import runpy
from reference import check as reference_check

U=Path(__file__).resolve().parent
R=U.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text())

def check():
    assert os.environ['CUDA_VISIBLE_DEVICES']=='-1'
    runpy.run_path(str(R/'data/accounting-master/r05-prospective-inputs-20261023/verify.py'))['check']()
    cases=reference_check()
    assert cases['passed_case_count']==12 and cases['refused_case_count']==4
    checks={'exact_cases':12,'invalid_weight_refusals':4,'independent_CDF_score_comparisons':20,
            'actual_issuer_forecasts':0,'historical_vintage_admissions':0,'whole_rows_closed':0,'readiness':'not_ready'}
    if (U/'completion.json').exists():
        complete=load(U/'completion.json');assert complete['checks']==checks
        assert load(U/'reference-results.json')==cases
        for name,digest in complete['bindings'].items():assert sha(R/name)==digest,name
    return cases,checks

if __name__=='__main__':print(json.dumps({'status':'read-only checks passed',**check()[1]}))
