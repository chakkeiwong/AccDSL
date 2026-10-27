"""Small original-context probes; no cross-owner execution or durable commit."""
from pathlib import Path
from copy import deepcopy
from hashlib import sha256
from fractions import Fraction as Q
import ast,importlib.util,json,sys,time

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.dont_write_bytecode=True
sys.path[:0]=[str(ROOT/'scripts'),str(HERE.parent/'company-return-execution-20261024')]
from retained_execution_context import load,event_for
import native_returns as returns
import lease_shared_book_v1 as lease
CHECKS=[]

def check(name,value):CHECKS.append({'name':name,'passed':bool(value)})
def dump(name,value):(HERE/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n')
def load_file(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    start=time.monotonic()
    for path,digest in json.loads((HERE/'source-lock.json').read_text()).items():
        check('protected:'+path,sha256((ROOT/path).read_bytes()).hexdigest()==digest)
    assert all(c['passed'] for c in CHECKS),'source mismatch'
    author,packet,item,_=load();initial=item('opening')
    opening=returns.initialize(author,initial['books']['P'],initial['compound']['prior_interest_expensed'])
    event=deepcopy(author['events'][0]);before=deepcopy(opening)
    rp=returns.propose(opening,event);after=returns.apply(opening,event,rp)
    check('return_immutable',opening==before)
    check('return_selected_settlement',after['component']['settled'] and Q(after['balances']['cash'])==Q(opening['balances']['cash'])-48)
    check('return_full_journal',sum(Q(x) for x in rp['journal'].values())==0)
    check('return_gross_cash',sum(Q(f['amount']) for f in rp['flows'])==Q(rp['journal']['cash']))
    check('return_apply_is_uncommitted',rp['committed'] is False)
    duplicate=returns.run_prefix(after,[event]);check('return_duplicate_refused',duplicate['status']=='invalid' and duplicate['state']==after)
    lcase=json.loads((HERE.parent/'lease-shared-book-20261024/cases.json').read_text())[0]
    ls=deepcopy(lcase['opening']);le=deepcopy(lcase['events'][0]);original=deepcopy(ls)
    lr=lease.propose(ls,le);check('lease_positive',lr['status']=='proposed')
    la=lease.apply(ls,le,lr['proposal']);check('lease_immutable',ls==original)
    check('lease_delta_only',all(Q(la['balances'][k])==Q(ls['balances'][k])+Q(lr['proposal']['journal'][k]) for k in ls['balances']))
    wrong=deepcopy(ls);wrong['context']['currency']='EUR';bad=lease.propose(wrong,le)
    check('lease_currency_rebind_refused',bad['status']=='unsupported' and bad['proposal'] is None)
    empty=deepcopy(ls);empty['collection_complete']='unknown';missing=lease.propose(empty,le)
    check('lease_unknown_membership_retained',missing['status']=='unresolved')
    check('native_state_shapes_differ',set(ls)!=set(opening) and set(ls['balances'])!=set(opening['balances']))
    folder=HERE.parent/'sector-company-composition-20261016'
    sector=load_file('module_audit_sector',folder/'reference.py')
    sr=json.loads((folder/'authored-cases.json').read_text())['cases'][0]['request'];copy=deepcopy(sr)
    result=sector.calculate(sr)
    check('sector_request_unchanged',sr==copy)
    check('sector_report_present',result.get('report') is not None)
    check('sector_has_no_posting',result.get('posts') is False and result.get('mutations')==[])
    wrong=deepcopy(sr);wrong['operation']='post';refusal=sector.calculate(wrong)
    check('sector_post_request_refused',refusal.get('report') is None and refusal.get('posts') is False and refusal.get('mutations')==[])
    tree=ast.parse((ROOT/'scripts/company_persistence_v1.py').read_text())
    coupling=[]
    for n in ast.walk(tree):
        if isinstance(n,ast.FunctionDef) and n.name in ['create_run','_replay']:
            calls=[x for x in ast.walk(n) if isinstance(x,ast.Call) and isinstance(x.func,ast.Name) and x.func.id=='Engine']
            check('store_fixed_engine:'+n.name,len(calls)==1);coupling.append({'method':n.name,'line':n.lineno,'fixed_engine_calls':[x.lineno for x in calls]})
    outputs={'return':{'request':event,'before':opening,'proposal':rp,'after':after,'duplicate':duplicate},
             'lease':{'request':le,'before':ls,'response':lr,'after':la,'wrong_currency':bad,'unknown_membership':missing},
             'sector':{'request':sr,'report_response':result,'posting_refusal':refusal},'persistence_static_coupling':coupling}
    runtime={}
    for module in list(sys.modules.values()):
        name=getattr(module,'__file__',None)
        if name:
            path=Path(name).resolve()
            if path.is_file() and path.is_relative_to(ROOT) and path.suffix=='.py':
                runtime[str(path.relative_to(ROOT))]=sha256(path.read_bytes()).hexdigest()
    outputs['executed_local_code_sha256']=runtime
    report={'passed':all(c['passed'] for c in CHECKS),'checks':CHECKS,'source_files':26,'probe_groups':4,
            'scope':'original-context capability distinctions; no generic composition or durability claim'}
    if '--record' in sys.argv:
        assert not (HERE/'probe-results.json').exists() and not (HERE/'probe-checks.json').exists(),'record once'
        assert report['passed'];dump('probe-results.json',outputs);dump('probe-checks.json',report)
    elif '--replay' in sys.argv:
        assert report==json.loads((HERE/'probe-checks.json').read_text())
        assert outputs==json.loads((HERE/'probe-results.json').read_text())
    print(json.dumps({'passed':report['passed'],'checks':len(CHECKS),'failed':[c['name'] for c in CHECKS if not c['passed']],
                      'probe_groups':4,'source_files':26,'seconds':round(time.monotonic()-start,3)}))
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
