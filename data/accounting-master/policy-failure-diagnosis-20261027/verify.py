"""All pay/draw paths at one exact certified financial witness."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy as cp
from hashlib import sha256
from datetime import datetime,timezone
from itertools import product
import importlib.util,json,os,platform,resource,subprocess,sys,time,traceback

H=Path(__file__).resolve().parent;R=H.parents[2]
def load(name,p):
    s=importlib.util.spec_from_file_location(name,p);v=importlib.util.module_from_spec(s);s.loader.exec_module(v);return v
cv=load('diagnosis_continuity',H.parent/'financial-assertion-continuity-20261027/verify.py')
ep=cv.ep
sys.path.insert(0,str(H.parent/'exact-region-certificates-20261026'))
import regions as reg
def digest(p):return sha256(p.read_bytes()).hexdigest()
def evaluate(symbolic,values):return cv.substitute(symbolic,values)
def classification(steps):
    failures=[]
    for index,step in enumerate(steps):
        for phase in ('pre','post'):
            for guard,ok in step[phase].items():
                if not ok:failures.append(dict(event_index=index,event=step['key'],phase=phase,guard=guard))
    return dict(accepted=not failures,first_failure=failures[0] if failures else None,all_guard_failures=failures)

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat()
    checks=[];controls=[];cases=[];pins={}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+chr(10))
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def refuse(n,fn):
        try:fn()
        except (ValueError,KeyError,TypeError,AssertionError) as err:
            controls.append(dict(name=n,reason=str(err)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'policy-existence-certificates-20261027/attempt-01';C=H.parent/'financial-assertion-continuity-20261027/attempt-01'
        for source in (B,C):
            ck('protected_pass:'+source.parent.name,json.loads((source/'verification.json').read_text())['status']=='PASS')
            for n,v in json.loads((source/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        files=[B/'cases.json',B/'verification.json',C/'verification.json',Path(reg.__file__),H/'verify.py',H/'contract.md',R/'docs/plans/accounting-policy-failure-diagnosis-20261027.md',H.parent/'revised-source-actor-messages-20261027/attempt-02/cases.json',H.parent/'certified-observation-policy-20261026/attempt-01/rows.json',H.parent/'symbolic-path-composition-20261026/attempt-01/cases.json']
        for p in files:pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        cert=next(v['result'] for v in json.loads((B/'cases.json').read_text()) if v['case']=='between:numeric_and_reported_receipt')
        actor=next(v['result'] for v in json.loads(files[-3].read_text()) if v['case']=='between:numeric_and_reported_receipt')
        source_rows=json.loads(files[-2].read_text());lookup={r['row_id']:r for r in source_rows};ar={r['id']:r for r in actor['rows']}
        edges=cert['certificate']['forward']+cert['certificate']['backward'];cited=[lookup[ar[v['row']]['support']] for v in edges]
        pay=next(r for r in cited if r['status']=='refused2' and r['a1']=='draw' and r['a2']=='pay')
        draw=next(r for r in cited if r['status']=='refused2' and r['a1']=='draw' and r['a2']=='draw')
        ck('same_second_stage_witness',pay['witness']==draw['witness'] and pay['job'][:4]==draw['job'][:4] and pay['receipt']==draw['receipt'])
        mode,right,ix,iy,a1,a2,receipt=pay['job'];point=list(map(Q,pay['witness']))
        def affine(coeff):return coeff[0]*point[0]+coeff[1]*point[1]+coeff[2]
        coupons=[affine(reg.coupon(mode,axis,index)) for axis,index in ((0,ix),(1,iy))]
        ck('direct_coupon_formula',coupons==[min(Q(6),max(Q(3),100*v)) for v in point])
        ck('protected_point_and_world',mode=='floating' and right is True and receipt==6 and coupons==[Q(95,16),Q(43,8)])
        saved=[v for v in json.loads(files[-1].read_text()) if v['chart']=='alpha'];by={(r['mode'],r['right'],*r['actions']):r['steps'] for r in saved}
        plans=[]
        for Rvalue in (6,7):
            for actions in product(('pay','draw'),repeat=2):plans.append(dict(case='witness_R'+str(Rvalue)+':'+':'.join(actions),mode=mode,right=right,coupons=list(map(str,coupons)),receipt=Rvalue,actions=list(actions),expected_accepted=Rvalue==7 and actions==('draw','pay')))
        plans.extend([dict(case='protected_fixed_viable',mode='fixed',right=True,coupons=['5','5'],receipt=6,actions=['pay','pay'],expected_accepted=True),dict(case='protected_floating_viable',mode='floating',right=True,coupons=['6','5'],receipt=6,actions=['draw','pay'],expected_accepted=True)])
        save('inputs-and-expectations.json',dict(certificate_case='between:numeric_and_reported_receipt',source_row=pay,matching_draw_row=draw,point=list(map(str,point)),plans=plans))
        for item in plans:
            key=(item['mode'],item['right'],*item['actions']);symbolic=by[key];expected=ep.steps(*key)
            ck(item['case']+':independent_symbolic',cv.canonical(symbolic)==cv.canonical(expected))
            values=dict(I1=Q(item['coupons'][0]),I2=Q(item['coupons'][1]),R=Q(item['receipt']))
            steps=evaluate(symbolic,values);status=classification(steps)
            ck(item['case']+':expected_acceptance',status['accepted']==item['expected_accepted'])
            ck(item['case']+':independent_numeric',steps==evaluate(expected,values))
            ck(item['case']+':state_balance',all(sum(Q(v) for v in state['book'].values())==0 for state in cv.states(steps)))
            ck(item['case']+':continuous',cv.continuous([],steps))
            d1,d2=[int(a=='draw') for a in item['actions']]
            final=Q(11,2)+values['R']-values['I1']-values['I2']-Q(d1,4)+Q(3*d2,4)
            ck(item['case']+':cash',str(final)==steps[-1]['after']['book']['cash'])
            cases.append(dict(**item,**status,steps=steps,algebraic_final_cash=str(final),executed_through=5 if status['accepted'] else status['first_failure']['event_index'],continuation_after_refusal='algebraic_only_not_executed'))
        actual=[v for v in cases if v['case'].startswith('witness_R6')]
        ck('all_four_paths_at_same_point',len(actual)==4 and {tuple(v['actions']) for v in actual}==set(product(('pay','draw'),repeat=2)) and len({tuple(v['coupons']) for v in actual})==1)
        ck('economic_impossibility_witness',not any(v['accepted'] for v in actual))
        path=next(v for v in actual if v['actions']==['draw','pay'])
        ck('exact_shortfall',path['algebraic_final_cash']=='-1/16')
        threshold=sum(coupons)+Q(1,4)-Q(11,2)
        ck('conditional_receipt_threshold',threshold==Q(97,16))
        def verify_diagnostic(candidate):
            assert len(candidate)==len(cases)
            for item,record in zip(plans,candidate):
                for k,v in item.items():assert record[k]==v
                values=dict(I1=Q(item['coupons'][0]),I2=Q(item['coupons'][1]),R=Q(item['receipt']))
                expected=evaluate(ep.steps(item['mode'],item['right'],*item['actions']),values)
                assert record['steps']==expected
                for k,v in classification(expected).items():assert record[k]==v
                assert record['algebraic_final_cash']==expected[-1]['after']['book']['cash']
            return True
        ck('saved_diagnostic_checker',verify_diagnostic(cases))
        for name,change in [('omit_action',lambda z:z.pop()),('change_coupon',lambda z:z[0]['coupons'].__setitem__(0,'5')),('false_acceptance',lambda z:z[0].update(accepted=True)),('suppress_failure',lambda z:z[0].update(first_failure=None)),('fake_cash',lambda z:z[0].update(algebraic_final_cash='0')),('erase_guard',lambda z:z[0]['steps'][1]['pre'].update(cash_to_pay=True)),('different_receipt',lambda z:z[0].update(receipt=7))]:
            bad=cp(cases);change(bad);refuse(name,lambda v=bad:verify_diagnostic(v))
        save('diagnosis.json',dict(scope='one_exact_point_refutes_universal_feasibility',source_row_id=pay['row_id'],point=list(map(str,point)),coupons=list(map(str,coupons)),receipt=6,all_actions_fail=True,draw_pay_shortfall='1/16',conditional_draw_pay_receipt_threshold=str(threshold),actual_assumption_change=False,information_repair_sufficient=False,other_points_unclassified=True))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',cases=len(cases),assertions=len(checks),controls=len(controls),protected_files=len(pins),finding='one economically infeasible receipt-6 point; information refinement alone cannot repair it')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('cases.json',cases)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact rational diagnostic',data_version='source-lock.json',plan='docs/plans/accounting-policy-failure-diagnosis-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
