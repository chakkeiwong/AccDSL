"""Read-only capture of exact selected prerequisite definitions and source bindings."""
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch
import json,os,platform,subprocess,sys,time
os.environ['CUDA_VISIBLE_DEVICES']='-1';sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
sys.path[:0]=[str(ROOT/'scripts'),str(ROOT/'tests')]
import typed_return_transition_v1 as native
import piecewise_method_family_v1 as family
from test_typed_return_transition_v1 import fixtures,raw_args
from test_conditional_history_family_v1 import domain
from test_piecewise_method_family_v1 import BUDGET
PLAN='docs/plans/accounting-method-family-prerequisites-audit-20261024.md'

def sha(p):return sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')

def capture(state,event):
    original=native.requirements.assess;captured={}
    def observe(registry,selected,values,available):
        captured.update(manifest=deepcopy(registry[selected]),values=deepcopy(values),
                        available=deepcopy(available),selected_digest=selected)
        return original(registry,selected,values,available)
    args=raw_args(state,event)
    with patch.object(native.requirements,'assess',side_effect=observe):
        result,lineage=native.prerequisite_manifest(state,event,args[1],args[3])
    return {**captured,'result':result,'lineage':lineage,
            'state_raw_sha256':args[1],'event_raw_sha256':args[3]}

def run():
    checks=[];rows=[]
    def check(n,v):checks.append({'name':n,'passed':bool(v)})
    selected=fixtures.selected_cases()[:2]
    for name,state,event in selected:
        captured=capture(state,event)
        context={'entity':state['context']['entity'],'book_role':'legal','at':event['date']}
        method=fixtures.program(event['kind'],context,native.structure.native.ACCOUNTS)
        mapped={};unmapped=[]
        for key,item in captured['manifest']['inputs'].items():
            if key in method['inputs']:
                check(event['kind']+'_type_'+key,item['type']==method['inputs'][key]['type'])
                mapped[key]={'method_input':key,'type':item['type'],'raw_source':captured['lineage'][key]}
            else:unmapped.append({'input':key,'type':item['type'],'role':item['role'],
                                  'value':captured['values'][key],'raw_source':captured['lineage'][key]})
        check(event['kind']+'_complete_input_partition',set(mapped)|{x['input'] for x in unmapped}==set(captured['manifest']['inputs']))
        check(event['kind']+'_original_satisfied',captured['result']['status']=='requirements_satisfied')
        check(event['kind']+'_all_guards_explicit_true',all(r['guard']==native.constant(True,native.core.BOOL)
                                                        for r in captured['manifest']['requirements']))
        rows.append({'kind':event['kind'],'capture':captured,'method':method,'mapped':mapped,
            'fixed_or_unresolved_external_inputs':unmapped,
            'method_only_inputs':sorted(set(method['inputs'])-set(mapped))})
    _,state,event=selected[0];over=deepcopy(event)
    amount=Q(state['component']['sold_units'])+1
    over.update(actual_units=native.monetary.fmt(amount),
        refund_cash=native.monetary.fmt(amount*Q(state['component']['unit_refund'])),
        handling_cash=native.monetary.fmt(amount*Q(event['unit_handling'])))
    captured=capture(state,over);method=rows[0]['method'];values=fixtures.project(state,over)
    d={'profile':family.PROFILE,'method':method,'selected_method_digest':native.core.digest(method),
       'domains':{k:domain(v['value']) for k,v in values.items()},'measurements':[],
       'obligations':[],'branch_limit':16}
    numerical=family.assess(d,BUDGET)
    check('over_quantity_balanced_monetary_witness',numerical['status']=='conditional_family_witness')
    check('over_quantity_native_prerequisite_invalid',captured['result']['status']=='invalid')
    failed=[r for r in captured['result']['findings'] if r['consequence']=='invalid']
    check('quantity_predicate_is_specific_failure',[x['id'] for x in failed]==['quantities'])
    checks_data=[]
    for label,edit,expected in [('false_rights',False,'unsupported'),('unknown_rights','unknown','unresolved')]:
        e=deepcopy(event);e['all_rights_closed']=edit;got=capture(state,e)
        check(label,got['result']['status']==expected)
        checks_data.append({'case':label,'capture':got,'expected':expected})
    locks=json.loads((ROOT/'data/accounting-master/typed-return-composition-20261024/dependency-lock.json').read_text())
    names=[PLAN,'scripts/typed_return_transition_v1.py','scripts/method_requirements_v3.py',
           'scripts/method_requirements_v2.py','scripts/method_requirements_v1.py',
           'scripts/method_input_binding_v1.py','scripts/piecewise_method_family_v1.py',
           'tests/test_typed_return_transition_v1.py',
           'data/accounting-master/typed-monetary-effects-20261024/examples.py',
           'data/accounting-master/company-return-execution-20261024/trace.json']
    for n in names:locks[n]=sha(ROOT/n)
    for n,h in locks.items():check('protected:'+n,sha(ROOT/n)==h)
    return {'passed':all(x['passed'] for x in checks),'checks':checks,'selected':rows,
        'counterexample':{'request':d,'budget':BUDGET,'numerical':numerical,'prerequisites':captured,
                          'sold_units':state['component']['sold_units'],'actual_units':over['actual_units']},
        'external_fact_cases':checks_data,'source_lock':locks,
        'remaining_native_conditions':['structural schema','event identity/lot state','funding',
            'native book invariants','memory transition','accounting/source authority'],
        'scope':'Selected prerequisites only; no full native execution or actual-company admission'}

def main():
    mode=sys.argv[1] if len(sys.argv)==2 else '--check';assert mode in ['--check','--record','--replay']
    assert mode!='--record' or not (HERE/'audit.json').exists()
    started=time.monotonic();r=run();assert r['passed'],[x for x in r['checks'] if not x['passed']]
    if mode=='--record':
        dump(HERE/'audit.json',r)
        dump(HERE/'probe-manifest.json',{'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'command':'python3 -B '+str(HERE.relative_to(ROOT)/'probe.py')+' --record',
            'environment':platform.python_version()+'; Z3 '+family.z3.get_version_string(),
            'cpu_gpu':'CPU only; CUDA_VISIBLE_DEVICES=-1','random_seeds':'N/A: deterministic exact prerequisites',
            'wall_seconds':time.monotonic()-started,'data_version':r['source_lock'],'plan':PLAN,
            'result':str(HERE.relative_to(ROOT)/'result.md'),
            'output':{'audit.json':sha(HERE/'audit.json'),'probe.py':sha(HERE/'probe.py')}})
    if mode=='--replay':
        old=json.loads((HERE/'audit.json').read_text())
        for value in [r,old]:value['counterexample']['numerical'].pop('wall_seconds',None)
        assert r==old
    print(json.dumps({'mode':mode,'passed':True,'checks':len(r['checks']),'sources':len(r['source_lock']),
        'inputs':[{ 'kind':x['kind'],'total':len(x['capture']['manifest']['inputs']),
                    'method_mapped':len(x['mapped']),'external':len(x['fixed_or_unresolved_external_inputs'])} for x in r['selected']],
        'counterexample':{'sold':r['counterexample']['sold_units'],'actual':r['counterexample']['actual_units'],
                           'numeric':r['counterexample']['numerical']['status'],
                           'prerequisite':r['counterexample']['prerequisites']['result']['status']}}))

if __name__=='__main__':main()
