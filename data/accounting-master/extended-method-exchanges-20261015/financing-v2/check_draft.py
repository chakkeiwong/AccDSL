"""Small deterministic pre-packet diagnostic; retain each attempt separately."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import subprocess
import time
import traceback

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[3]

def main():
    started=time.monotonic(); checks=[]
    def check(name,fn):
        try: fn(); checks.append({'name':name,'passed':True})
        except Exception as e: checks.append({'name':name,'passed':False,'error':str(e),'traceback':traceback.format_exc()})
    for path in OUT.glob('*.py'):
        check('compile:'+path.name,lambda path=path:compile(path.read_text(),str(path),'exec'))
    from authored_cases import CASES
    from schema_design import schemas, ACCOUNTS, CASH, OCI_MOVEMENTS, EQUITY_MOVEMENTS, COMPONENTS, EVENTS
    from financial_checks import derive,check_component
    from jsonschema import Draft202012Validator
    for name,s in schemas()['$defs'].items():
        check('schema:'+name,lambda s=s:Draft202012Validator.check_schema(s))
    def require(ok,code,status='rejected'):
        assert ok,(code,status)
    def vector(v,keys):return {k:Fraction(v.get(k,0)) for k in keys}
    methods=set()
    for ca in CASES:
        c=ca['opening_component']; b=vector(ca['opening_balances'],ACCOUNTS)
        check(ca['id']+':opening',lambda c=c,b=b,ca=ca:check_component(ca['tag'],c,b))
        for i,s in enumerate(ca['steps'],1):
            def transition(c=c,b=b,s=s,ca=ca):
                after,j,cash,oci,equity=derive(ca['tag'],c,s['method'],s['parameters'],s['event_date'],require)
                assert after==s['after'],{k:(after.get(k),s['after'].get(k)) for k in after if after[k]!=s['after'].get(k)}
                assert j=={k:v for k,v in s['journal'].items() if v},(j,s['journal'])
                assert cash==vector(s['cash_change'],CASH)
                assert oci==vector(s['oci_change'],OCI_MOVEMENTS)
                assert equity==vector(s['equity_change'],EQUITY_MOVEMENTS)
                after_b={k:b[k]+j.get(k,0) for k in ACCOUNTS}
                assert sum(after_b.values())==0
                check_component(ca['tag'],after,after_b)
            check(ca['id']+':'+str(i)+':'+s['method'],transition)
            c=s['after'];b={k:b[k]+s['journal'].get(k,0) for k in ACCOUNTS}; methods.add(s['method'])
    def coverage(): assert methods==set(EVENTS),(methods^set(EVENTS))
    check('all-methods-authored',coverage)
    pins=json.loads((OUT.parent/'protected-inputs.json').read_text())
    for p in pins['files']:
        def preserved(p=p):
            for k in ['path','snapshot']:
                assert hashlib.sha256((ROOT/p[k]).read_bytes()).hexdigest()==p['sha256'],p[k]
        check('preserved:'+p['path'],preserved)
    def git_preserved():
        idx=subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)
        assert hashlib.sha256(idx).hexdigest()==pins['index_sha256']
        assert len(idx.splitlines())==pins['index_entries']==100
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==pins['git_commit']
    check('head-and-unrelated-index-preserved',git_preserved)
    result={'purpose':'pre-packet deterministic diagnostic; no runtime or accounting promotion',
        'cases':len(CASES),'methods':len(methods),'checks':checks,'failed':sum(not c['passed'] for c in checks),
        'wall_seconds':time.monotonic()-started,'cpu_gpu':'CPU-only Python; no GPU framework imported'}
    n=1
    while (OUT/f'draft-validation-{n:02}.json').exists(): n+=1
    path=OUT/f'draft-validation-{n:02}.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'artifact':path.name,'cases':len(CASES),'methods':len(methods),'checks':len(checks),
        'failed':result['failed'],'failures':[c for c in checks if not c['passed']]}))
    return bool(result['failed'])

if __name__=='__main__':raise SystemExit(main())
