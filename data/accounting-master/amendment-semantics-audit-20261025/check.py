"""Small debugging discriminator; no amendment engine or accounting claim."""
from copy import deepcopy
from pathlib import Path
from hashlib import sha256
import importlib.util
import json
import platform
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import declared_receivable_lifecycle_v1 as life
spec=importlib.util.spec_from_file_location('amendment_baseline_examples',ROOT/'data/accounting-master/declared-collection-state-growth-20261025/examples.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+chr(10))
def run():
    cases={}
    for chart in ['alpha','beta']:
        body,roles,_=ex.lifecycle_fixture(chart);body['commands']=body['commands'][:5]
        result=life.run(body);assert result['status']=='complete_provisional'
        before=result['current'];old=deepcopy(before);claim=before['memory']['claims']['invoice/a~1']
        assert claim['assessment_date']=='2027-02-28' and claim['overdue']=='20/1'
        altered=deepcopy(before);altered['date']='2027-03-10';altered['memory']['claims']['invoice/a~1']['due']='2027-04-30'
        try:life.control(altered,body['roles']);raise AssertionError('Expected incompatible historical assessment')
        except life.core.Invalid as exc:assert str(exc)=='overdue_snapshot'
        assert before==old and altered['balances']==before['balances']
        reset=deepcopy(altered);reset['memory']['claims']['invoice/a~1']['overdue']='0/1';life.control(reset,body['roles'])
        assert reset['memory']['claims']['invoice/a~1']['assessment_date']=='2027-02-28'
        assert reset['memory']['claims']['invoice/a~1']['overdue']!=claim['overdue']
        cases[chart]={'before_sha256':life.core.digest(before),'original_claim':claim,'overwrite_claim':altered['memory']['claims']['invoice/a~1'],
                      'overwrite_refusal':'overdue_snapshot','reset_claim':reset['memory']['claims']['invoice/a~1'],
                      'reset_consequence':'Validator accepts changed historical assessment; not a valid amendment semantics',
                      'balances_unchanged':True,'original_unchanged':True}
    evidence={'purpose':'Debugging discriminator for missing amendment semantics','cases':cases,'amendment_implemented':False,
              'finding':'Current due date cannot by itself preserve the basis of a prior assessment'}
    record='--record' in sys.argv
    if record:
        assert not (HERE/'evidence.json').exists();dump(HERE/'evidence.json',evidence)
        paths=['scripts/declared_receivable_lifecycle_v1.py','data/accounting-master/declared-collection-state-growth-20261025/examples.py',
               'docs/plans/accounting-amendment-semantics-audit-20261025.md',str(Path(__file__).relative_to(ROOT)),str((HERE/'evidence.json').relative_to(ROOT))]
        dump(HERE/'source-lock.json',{name:sha(ROOT/name) for name in paths})
        dump(HERE/'run-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B data/accounting-master/amendment-semantics-audit-20261025/check.py --record',
            'environment':sys.version,'platform':platform.platform(),'cpu_gpu':'CPU debugging; no GPU framework imported',
            'seeds':'N/A: deterministic','data_version':'Retained lifecycle prefix through February2027; date-only hypothetical overwrite',
            'plan':'docs/plans/accounting-amendment-semantics-audit-20261025.md','result':str((HERE/'result.md').relative_to(ROOT)),
            'artifacts':{str((HERE/n).relative_to(ROOT)):sha(HERE/n) for n in ['evidence.json','source-lock.json']}})
    else:
        assert evidence==json.loads((HERE/'evidence.json').read_text())
        for name,h in json.loads((HERE/'source-lock.json').read_text()).items():assert sha(ROOT/name)==h,name
    print(json.dumps({'passed':True,'mode':'record' if record else 'read_only_replay','cases':len(cases),'amendment_implemented':False}))
if __name__=='__main__':run()
