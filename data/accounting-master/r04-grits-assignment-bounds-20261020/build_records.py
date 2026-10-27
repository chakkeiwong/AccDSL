"""One-time supporting records for the completed bounded local searches."""
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import sys

sys.dont_write_bytecode=True
os.environ['CUDA_VISIBLE_DEVICES']='-1'
U=Path(__file__).resolve().parent
R=U.parents[2]

def bind(p):return {'path':str(p.relative_to(R)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(name,value):
    with (U/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')

def main():
    assert not (U/'source-ledger.json').exists(),'one-time supporting record construction'
    metric=R/'data/accounting-master/r04-pubtablesv2-20261019/sources/05-metric.py'
    oracle=R/'data/accounting-master/r04-grits-theory-20261020/compare.py'
    anchors=[]
    for name,p,start,end,meaning in [
        ('internal_ties',metric,145,170,'Diagonal then skip-first then skip-second tie policy in inner DP.'),
        ('outer_ties',metric,211,244,'Same outer DP tie policy and traceback.'),
        ('identity_shortcut',metric,306,328,'Current shortcut included in the local oracle.'),
        ('row_shortcut',metric,339,368,'Current row-identity shortcut included.'),
        ('pair_upper',metric,364,396,'Pair upper from row/column relaxations, feasible lower from selected paths.'),
        ('cell_reward',metric,399,415,'Single-character str rewards reduce to exact equality.'),
        ('assignment_matrices',metric,603,622,'Lower and upper scores populate distinct float32 matrices.'),
        ('assignment_selection',metric,624,634,'Only lower matrix is optimized; same indices select upper entries.'),
        ('assignment_return',metric,635,644,'Selected upper scores are summed and returned.'),
        ('local_grid_oracle',oracle,22,104,'Project-local mathematical DP and exhaustive oracle; not acquired runtime.'),
    ]:
        anchors.append({'id':name,**bind(p),'first_line':start,'last_line':end,
            'excerpt':'\n'.join(p.read_text().splitlines()[start-1:end]),'supports':meaning})
    write('source-ledger.json',{'date':'2026-10-20','created_utc':datetime.now(timezone.utc).isoformat(),
        'new_acquisitions':0,'repository':'kensho-technologies/grits',
        'commit':'8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1',
        'bindings':[bind(p) for p in [metric,oracle,
            R/'data/accounting-master/r04-grits-theory-20261020/result.md',
            R/'data/accounting-master/r04-pubtablesv2-20261019/source-ledger.json']],
        'anchors':anchors,'reading_scope':'Listed spans, inherited full-source and theory reading explicitly preserved.'})
    spec=importlib.util.spec_from_file_location('assignment_local_checks',U/'compare.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    write('claim-support-ledger.json',{'summary':m.SUMMARY,'claims':[
        {'claim':'Returned upper sum uses the lower-selected assignment.','class':'IMPLEMENTATION_EVIDENCE','anchors':['assignment_selection','assignment_return']},
        {'claim':'That sum bounds exact score on the fixed assignment, not in general the globally optimized assignment.','class':'PROJECT_DERIVATION','evidence':'derivation.md'},
        {'claim':'Two real binary-grid collections have identical solver input but require different tie resolutions to retain a global bound.','class':'PROJECT_DERIVATION','evidence':'tie-witness.json'},
        {'claim':'No unique lower-maximizer violation was found in the predeclared domain.','class':'PROJECT_DERIVATION','evidence':'search-result.json'},
        {'claim':'Separate optimization on valid upper entries gives a mathematical global bound.','class':'PROJECT_DERIVATION','evidence':'derivation.md','limit':'Numerical enclosure/solver certification remains required.'},
    ]})
    write('source-support-ledger.json',{'classification':'IMPLEMENTATION_OR_SOFTWARE plus PROJECT_DERIVATION',
        'source':'Pinned retained current metric and previously reviewed local mathematical oracle',
        'read_scope':'source-ledger.json','publication_status':'Software source and local derivation; no new paper',
        'retraction_status':'N/A new software inquiry; inherited paper dispositions remain frozen',
        'allowed':'Exact source computation and finite/global-bound scope proof',
        'forbidden':'Installed solver tie behavior, historical results or empirical error rates'})
    write('citation-venue-ledger.json',{'citation_count':'not available; not queried','venue_metric':'not applicable',
        'scope':'No new literature ranking; prior GriTS technical source evidence preserved.'})
    write('backward-snowball-ledger.json',{'route':['current Hungarian matching source','current pair heuristic/shortcuts','prior GriTS theory derivation','independent finite substructure oracle'],
        'disposition':'All needed mathematical obligations shown locally; no new imported theorem.'})
    write('forward-snowball-ledger.json',{'query':'No new citation search in this bounded proof inquiry',
        'next_lead':'Float32 score-matrix conversion and summation can alter lower/upper direction outside integer witnesses',
        'scope':'Requires separate evidence contract; no numerical enclosure guarantee inferred here.'})
    write('omission-risk-ledger.json',{'items':[
        {'gap':'Actual SciPy tie resolution','status':'unexecuted','disposition':'Two-order proof avoids depending on it.'},
        {'gap':'All input table populations','status':'not tested','disposition':'18,496 canonical synthetic collection pairs are not a probability distribution.'},
        {'gap':'Float32 rounding and solver certification','status':'open','disposition':'Small integer witness exact; general directed-bound implementation still needed.'},
        {'gap':'Historical benchmark metric version','status':'open','disposition':'No claim published scores changed.'},
        {'gap':'Manuscript defect','status':'none identified','disposition':'No global multi-table upper-bound theorem located in the retained manuscript discussion.'},
    ]})
    print(json.dumps({'constructed':True,'anchors':len(anchors),'new_acquisitions':0}))

if __name__=='__main__':main()
