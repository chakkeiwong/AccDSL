"""One-time exact illustration and source record construction."""
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
    assert not (U/'source-ledger.json').exists(),'one-time construction'
    spec=importlib.util.spec_from_file_location('local_binary32_model',U/'compare.py')
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    anchors=[]
    for name,start,end,meaning in [
        ('exact_reward',399,415,'Normalized LCS and equality shortcut.'),
        ('one_cell_identity',306,328,'One-cell nonnegative reward takes identity alignment.'),
        ('matrix_precision',603,622,'Lower and upper stored in float32 before assignment.'),
        ('selection_and_sums',624,644,'Assignment on stored lower values; selected sums cast to Python float afterward.')]:
        p=m.METRIC;anchors.append({'id':name,**bind(p),'first_line':start,'last_line':end,
            'excerpt':'\n'.join(p.read_text().splitlines()[start-1:end]),'supports':meaning})
    write('source-ledger.json',{'date':'2026-10-20','created_utc':datetime.now(timezone.utc).isoformat(),
        'new_acquisitions':0,'repository':'kensho-technologies/grits',
        'commit':'8a281a3e2fd4cfa600d1c1f70f33b5eccc6294f1',
        'bindings':[bind(p) for p in [m.METRIC,
            R/'data/accounting-master/r04-grits-assignment-bounds-20261020/completion.json',
            R/'data/accounting-master/r04-pubtablesv2-20261019/source-ledger.json']],
        'anchors':anchors,'scope':'Selected pinned code plus independent stdlib IEEE-binary32 model; no native execution.'})
    result=m.compute();write('witnesses.json',result)
    write('claim-support-ledger.json',{'summary':m.SUMMARY,'claims':[
        {'claim':'Selected source stores pair lower and upper values in float32.','class':'IMPLEMENTATION_EVIDENCE','anchors':['matrix_precision']},
        {'claim':'Nearest binary32 conversion is not direction-preserving for bounds.','class':'PROJECT_DERIVATION','evidence':'witnesses.json','scope':'Exact signed representation comparisons.'},
        {'claim':'One-cell LCS examples isolate representation from alignment heuristics.','class':'PROJECT_DERIVATION','anchors':['exact_reward','one_cell_identity'],'evidence':'witnesses.json'},
        {'claim':'Local outward rational conversion encloses these exact values but does not certify the full program.','class':'PROJECT_DERIVATION','evidence':'numerical-contract.md'},
        {'claim':'Two distinct abstract rational weights collapse to the same stored value.','class':'PROJECT_DERIVATION','evidence':'witnesses.json','limit':'No realizing grid or installed assignment claimed.'},
    ]})
    write('source-support-ledger.json',{'classification':'IMPLEMENTATION_OR_SOFTWARE plus PROJECT_DERIVATION',
        'source':'Retained metric plus standard-library binary32 representation model','identity':'source-ledger.json',
        'read_scope':'Four listed source spans','publication_status':'Software and local arithmetic, no new paper',
        'retraction_status':'N/A new paper; inherited original source dispositions unchanged',
        'allowed':'Representation counterexamples and proposed certification conditions',
        'forbidden':'NumPy/SciPy runtime behavior, historical-score impact or error frequencies'})
    write('citation-venue-ledger.json',{'citation_count':'not available; not queried','venue_metric':'not applicable',
        'criterion':'Exact rational error, not citation or software popularity.'})
    write('backward-snowball-ledger.json',{'route':['current float32 matrices','one-cell normalized-LCS reward','prior fixed/global assignment distinction'],
        'disposition':'No new paper; local exact derivation supports the claim.'})
    write('forward-snowball-ledger.json',{'query':'No new citation search for this arithmetic inquiry',
        'next_action':'Consolidate metric findings into an explicit proposed evaluation profile, preserving unresolved population/weight/margin/confidence choices.'})
    write('omission-risk-ledger.json',{'items':[
        {'gap':'Native conversion/reduction implementation','status':'held','risk':'struct model is not an installed conformance test'},
        {'gap':'Certified entire metric/assignment solver','status':'unimplemented','risk':'One-ULP final padding or float64 alone is insufficient'},
        {'gap':'Magnitude and frequency in real reports','status':'unverified','risk':'Finite representation census is not dataset evidence'},
        {'gap':'Threshold and tolerance choices','status':'unselected','risk':'No numerical or model-ranking default follows'},
    ]})
    print(json.dumps({'constructed':True,'anchors':len(anchors),'domain':result['rational_domain'],'examples':result['examples'][:2]}))

if __name__=='__main__':main()
