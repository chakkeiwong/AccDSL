"""Prove full two-coupon viability with exact affine certificates."""
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
cv=load('viability_continuity',H.parent/'financial-assertion-continuity-20261027/verify.py');ep=cv.ep
sys.path.insert(0,str(H.parent/'exact-region-certificates-20261026'))
import regions as reg
import geometry as g
import proofcheck as pc
def digest(p):return sha256(p.read_bytes()).hexdigest()

def partitions(receipt):
    domain=[reg.H(-1,0,3),reg.H(1,0,-6),reg.H(0,-1,3),reg.H(0,1,-6)]
    low=reg.H(1,0,'-11/2');total=reg.H(1,1,-Q(receipt)-Q(21,4))
    return dict(pay_first=domain+[low],draw_first_viable=domain+[reg.opposite(low),total],infeasible=domain+[reg.opposite(low),reg.opposite(total)])

def guards(actions,receipt):
    variables={'I1':[Q(1),Q(0),Q(0)],'I2':[Q(0),Q(1),Q(0)],'R':[Q(0),Q(0),Q(receipt)]};out=[]
    for step in ep.steps('floating',True,*actions):
        for phase in ('pre','post'):
            for name,predicate in step[phase].items():
                for i,h in enumerate(reg.predicates(predicate,variables)):out.append(dict(event=step['key'],phase=phase,guard=name,part=i,predicate=h))
    return out

def empty_proof(hs):
    proof=g.produce(hs);assert pc.verify(hs,proof)=='empty';return proof

def make(receipt):
    regions=partitions(receipt);coverage=[];exclusions=[]
    for name,actions in [('pay_first',('pay','pay')),('draw_first_viable',('draw','pay'))]:
        for item in guards(actions,receipt):
            pred=item['predicate']
            if pred is True:proof=None
            else:proof=empty_proof(regions[name]+([] if pred is False else [reg.opposite(pred)]))
            coverage.append(dict(region=name,actions=list(actions),guard=item,proof=proof))
    for actions in product(('pay','draw'),repeat=2):
        instructions=guards(actions,receipt);false=[i for i,v in enumerate(instructions) if v['predicate'] is False]
        hs=regions['infeasible']+[v['predicate'] for v in instructions if type(v['predicate']) is dict]
        proof=None if false else empty_proof(hs)
        exclusions.append(dict(actions=list(actions),guards=instructions,false_guards=false,proof=proof))
    regions_proof={n:g.produce(hs) for n,hs in regions.items()}
    return dict(receipt=receipt,regions=regions,region_proofs=regions_proof,coverage=coverage,exclusions=exclusions,
                observation_policy=dict(first='draw iff first refined trigger is true; otherwise pay',second='pay',scope='derived viable region only',future_coupon_used_at_first=False),
                domain_changed=False,probability=None)

def verify(result):
    receipt=result['receipt'];assert type(receipt) is int and receipt in (6,7)
    assert set(result)=={'receipt','regions','region_proofs','coverage','exclusions','observation_policy','domain_changed','probability'}
    assert result['regions']==partitions(receipt) and set(result['region_proofs'])==set(result['regions'])
    for name,hs in result['regions'].items():
        got=pc.verify(hs,result['region_proofs'][name]);assert got==('empty' if name=='infeasible' and receipt==7 else 'nonempty')
    expected=[(name,list(actions),v) for name,actions in [('pay_first',('pay','pay')),('draw_first_viable',('draw','pay'))] for v in guards(actions,receipt)]
    assert len(result['coverage'])==len(expected)
    for record,(name,actions,item) in zip(result['coverage'],expected):
        assert set(record)=={'region','actions','guard','proof'} and record['region']==name and record['actions']==actions and record['guard']==item
        pred=item['predicate']
        if pred is True:assert record['proof'] is None
        else:assert pc.verify(result['regions'][name]+([] if pred is False else [reg.opposite(pred)]),record['proof'])=='empty'
    assert len(result['exclusions'])==4
    for record,actions in zip(result['exclusions'],product(('pay','draw'),repeat=2)):
        ins=guards(actions,receipt);false=[i for i,v in enumerate(ins) if v['predicate'] is False]
        assert record['actions']==list(actions) and record['guards']==ins and record['false_guards']==false
        if false:assert record['proof'] is None
        else:assert pc.verify(result['regions']['infeasible']+[v['predicate'] for v in ins if type(v['predicate']) is dict],record['proof'])=='empty'
    assert result['observation_policy']==dict(first='draw iff first refined trigger is true; otherwise pay',second='pay',scope='derived viable region only',future_coupon_used_at_first=False)
    assert result['domain_changed'] is False and result['probability'] is None
    return True

def main():
    resource.setrlimit(resource.RLIMIT_CPU,(120,120));attempt=sys.argv[1];assert attempt in ('01','02','03')
    A=H/('attempt-'+attempt);A.mkdir(exist_ok=False);start=time.monotonic();started=datetime.now(timezone.utc).isoformat();checks=[];controls=[];results=[];points=[];pins={}
    def save(n,v):(A/n).write_text(json.dumps(v,indent=2)+chr(10))
    def ck(n,v):
        checks.append(dict(name=n,passed=bool(v)))
        if not v:raise AssertionError(n)
    def refuse(n,fn):
        try:fn()
        except (ValueError,AssertionError,KeyError,TypeError,IndexError) as err:controls.append(dict(name=n,reason=str(err)));ck('reject:'+n,True)
        else:ck('reject:'+n,False)
    try:
        ck('cpu_hidden',os.environ.get('CUDA_VISIBLE_DEVICES')=='-1')
        B=H.parent/'policy-failure-diagnosis-20261027/attempt-01'
        ck('diagnosis_pass',json.loads((B/'verification.json').read_text())['status']=='PASS')
        for n,v in json.loads((B/'source-lock.json').read_text()).items():ck('source:'+n,digest(R/n)==v);pins[n]=v
        for p in list(B.glob('*.json'))+[Path(g.__file__),Path(pc.__file__),H/'verify.py',H/'contract.md',R/'docs/plans/accounting-financing-viability-boundary-20261027.md']:
            pins[str(p.relative_to(R))]=digest(p)
        save('source-lock.json',pins)
        for n in ('verify.py','contract.md'):(A/n).write_bytes((H/n).read_bytes())
        saved=[v for v in json.loads((H.parent/'symbolic-path-composition-20261026/attempt-01/cases.json').read_text()) if v['chart']=='alpha' and v['mode']=='floating' and v['right']]
        for v in saved:ck('independent_path:'+':'.join(v['actions']),v['steps']==cv.canonical(ep.steps('floating',True,*v['actions'])))
        point_inputs=[('first_equality','11/2','6',6,True),('just_above_first','551/100','6',6,False),('sum_equality','23/4','11/2',6,True),('just_above_sum','23/4','551/100',6,False),('prior_witness','95/16','43/8',6,False),('max_receipt7','6','6',7,True),('min','3','3',6,True),('prior_viable','6','5',6,True)]
        save('inputs-and-expectations.json',dict(receipts=[6,7],coupon_domain=['3','6'],right=True,expected_R6_infeasible='I1>11/2 and I1+I2>45/4',expected_R7_infeasible='empty',points=point_inputs,assumptions_changed=False))
        for receipt in (6,7):
            result=make(receipt);ck('continuous_region_'+str(receipt),verify(result));results.append(result)
        for name,a,z,receipt,want in point_inputs:
            v=dict(I1=Q(a),I2=Q(z),R=Q(receipt));accepted=[]
            for actions in product(('pay','draw'),repeat=2):
                steps=cv.substitute(ep.steps('floating',True,*actions),v)
                if all(all(step[phase].values()) for step in steps for phase in ('pre','post')):accepted.append(actions)
            formula=not (v['I1']>Q(11,2) and v['I1']+v['I2']>v['R']+Q(21,4))
            ck(name+':boundary',bool(accepted)==formula==want)
            rule=('draw' if v['I1']>Q(11,2) else 'pay','pay')
            ck(name+':observation_rule',(rule in accepted)==formula)
            points.append(dict(case=name,coupons=[a,z],receipt=receipt,accepted_actions=accepted,rule=rule,viable=formula))
        ck('coupon_min_endpoint',reg.coupon('floating',0,0)==[Q(0),Q(0),Q(3)])
        ck('coupon_max_endpoint',reg.coupon('floating',0,10)==[Q(0),Q(0),Q(6)])
        base=results[0]
        for name,change in [('omit_region',lambda z:z['regions'].pop('infeasible')),('omit_action',lambda z:z['exclusions'].pop()),('omit_guard',lambda z:z['coverage'].pop()),('adopt_restricted_domain',lambda z:z.update(domain_changed=True)),('invent_probability',lambda z:z.update(probability=0.5)),('future_information',lambda z:z['observation_policy'].update(future_coupon_used_at_first=True)),('weaken_boundary',lambda z:z['regions']['infeasible'][-1].update(strict=False))]:
            bad=cp(base);change(bad);refuse(name,lambda z=bad:verify(z))
        bad=cp(base);item=next(v for v in bad['coverage'] if v['proof'] is not None);item['proof']['weights']={};refuse('empty_proof_weights',lambda:verify(bad))
        bad=cp(base);bad['region_proofs']['infeasible']['point']=['3','3'];refuse('wrong_region_witness',lambda:verify(bad))
        bad=cp(results[1]);bad['region_proofs']['infeasible']={'kind':'witness','point':['6','6']};refuse('invent_R7_failure',lambda:verify(bad))
        for n,v in pins.items():ck('preserved:'+n,digest(R/n)==v)
        summary=dict(status='PASS',receipt_domains=2,action_region_exclusions=8,guard_implications=sum(len(v['coverage']) for v in results),point_checks=len(points),assertions=len(checks),controls=len(controls),protected_files=len(pins),finding='exact committed-right viability boundary; original refined first trigger suffices on viable region')
    except Exception:
        summary=dict(status='FAIL',error=traceback.format_exc(),assertions=len(checks));save('failure.json',summary)
    finally:
        for n,v in [('verification.json',summary),('checks.json',checks),('controls.json',controls),('region-certificates.json',results),('point-examples.json',points)]:save(n,v)
        save('run-manifest.json',dict(command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+attempt,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',started_utc=started,wall_seconds=time.monotonic()-start,seeds='N/A exact affine proof',data_version='source-lock.json',plan='docs/plans/accounting-financing-viability-boundary-20261027.md',result=str((H/'result.md').relative_to(R)),artifacts=str(A.relative_to(R))))
        print(json.dumps(summary),flush=True)
    sys.exit(summary['status']!='PASS')
if __name__=='__main__':main()
