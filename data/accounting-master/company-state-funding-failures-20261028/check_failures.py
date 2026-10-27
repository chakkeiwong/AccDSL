"""Original dated-offer failures through the retained exact linear solver."""
import argparse
from copy import deepcopy
from datetime import datetime,timezone
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import z3
from rational_solver_v1 import Problem,Budget,q,solve
PLAN='docs/plans/company-state-funding-failures-20261028.md'
SOURCE='docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/14-refinancing-case.tex'
BUDGET=Budget(10,10000,100,100,10000,1000,1000000)

def problem(spec):
    p=Problem('Original refinancing chapter14; explicit dated offers','synthetic supplied case')
    bridge,face=z3.Reals('bridge_principal term_face');p.variables=dict(bridge_principal=bridge,term_face=face)
    sale=q(spec['sale']);price=q(spec['price']);active=spec['bridge'];term=spec['term']
    p.add('bridge_nonnegative',bridge>=0);p.add('term_nonnegative',face>=0)
    if active:
        p.add('bridge_cap',bridge<=q(spec.get('bridge_cap','30')))
        p.add('bridge_positive_net',bridge>=q(spec.get('bridge_fee','1')))
        if not spec.get('bridge_admitted',True):p.add('absent_bridge_offer',bridge==0)
    else:p.add('no_bridge',bridge==0)
    if term:
        p.add('term_cap',face<=40);p.add('term_nonnegative_proceeds',price*face>=2)
        inventory=q(20)*(q(1)-sale)
        p.add('term_settlement_inventory',inventory>=10)
        if not spec.get('term_admitted',True):p.add('absent_term_offer',face==0)
    else:p.add('no_term',face==0)
    amounts=[('day1_open',q(12)),('day3_wages',q(-10)),('day4_sale',q(15)*sale),
        ('day4_bridge',bridge-q(spec.get('bridge_fee','1')) if active else q(0)),
        ('day4_old_maturity',q(-32)),('day5_customer',q(18) if spec['history']=='H1' else q(0)),
        ('day5_term',price*face-2 if term else q(0)),
        ('day6_bridge_maturity',-bridge-1 if active else q(0)),
        ('day9_customer',q(18) if spec['history']=='H2' else q(0))]
    cash=q(0);prefixes=[]
    for event,amount in amounts:
        cash=cash+amount;prefixes.append((event,cash));p.add('cash_prefix/'+event,cash>=0)
    p.outputs=dict(bridge_principal=bridge,term_face=face,closing_cash=cash,remaining_inventory=q(20)*(1-sale))
    p.provenance=dict(source=SOURCE,case=deepcopy(spec),offer_admission='synthetic supplied facts only',
        nonanticipative_policy=False,accounting_postings=False)
    return p,prefixes

def oracle(spec,b,f):
    # Literal cash events; does not call native formula construction.
    sale=F(spec['sale']);price=F(spec['price']);cash=F(12);steps=[('day1_open',cash)]
    for label,change in [('day3_wages',F(-10)),('day4_sale',15*sale),
        ('day4_bridge',b-F(spec.get('bridge_fee','1')) if spec['bridge'] else F(0)),
        ('day4_old_maturity',F(-32)),('day5_customer',F(18) if spec['history']=='H1' else F(0)),
        ('day5_term',price*f-2 if spec['term'] else F(0)),
        ('day6_bridge_maturity',-b-1 if spec['bridge'] else F(0)),
        ('day9_customer',F(18) if spec['history']=='H2' else F(0))]:
        cash+=change;steps.append((label,cash))
    eligible=(not spec['term'] or 20*(1-sale)>=10)
    offer=(not spec['bridge'] or spec.get('bridge_admitted',True)) and (not spec['term'] or spec.get('term_admitted',True))
    caps=(not spec['bridge'] or F(spec.get('bridge_fee','1'))<=b<=F(spec.get('bridge_cap','30'))) and (not spec['term'] or 0<=f<=40 and price*f>=2)
    return dict(prefixes=[dict(event=n,cash=str(c)) for n,c in steps],cash_ok=all(c>=0 for _,c in steps),
        eligibility=eligible,offers=offer,caps=caps,viable=all(c>=0 for _,c in steps) and eligible and offer and caps)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True)
    out=parser.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    checks=[];results=[];constraints=[]
    def check(name,actual,expected):checks.append(dict(name=name,passed=actual==expected,actual=actual,expected=expected))
    def spec(name,sale='0',history='H1',bridge=True,term=False,price='9/10',**extras):
        return dict(id=name,sale=sale,history=history,bridge=bridge,term=term,price=price,**extras)
    cases=[
        (spec('bridge only original'),'Infeasible',None,None),
        (spec('no admitted offers',bridge=False),'Infeasible',None,None),
        (spec('day5 term cannot fund day4',bridge=False,term=True),'Infeasible',None,None),
        (spec('unadmitted bridge',sale='1',bridge_admitted=False),'Infeasible',None,None),
        (spec('full sale H1',sale='1'),'Feasible','16','0'),
        (spec('full sale H2',sale='1',history='H2'),'Infeasible',None,None),
        (spec('full sale H2 term loses eligibility',sale='1',history='H2',term=True),'Infeasible',None,None),
        (spec('half sale H1',sale='1/2',term=True),'Feasible','47/2','85/9'),
        (spec('half sale H2',sale='1/2',history='H2',term=True),'Feasible','47/2','265/9'),
        (spec('half sale H1 price06',sale='1/2',term=True,price='3/5'),'Feasible','47/2','85/6'),
        (spec('half sale H2 price06',sale='1/2',history='H2',term=True,price='3/5'),'Infeasible',None,None),
        (spec('half sale H2 threshold',sale='1/2',history='H2',term=True,price='53/80'),'Feasible','47/2','40'),
        (spec('half sale H2 below threshold',sale='1/2',history='H2',term=True,price='6624/10000'),'Infeasible',None,None),
        (spec('half sale unadmitted term',sale='1/2',history='H2',term=True,term_admitted=False),'Infeasible',None,None)]
    for s,expected,b,f in cases:
        p,prefixes=problem(s);r=solve(p,BUDGET,p.outputs['term_face'])
        check(s['id']+'/feasibility',r['feasibility'],expected)
        check(s['id']+'/complete coverage',r['coverage']['complete'],True)
        constraints.append(dict(id=s['id'],constraints=[dict(label=n,expression=x.sexpr()) for n,x in p.constraints],provenance=p.provenance))
        record=dict(input=s,result=r)
        if b is not None:
            check(s['id']+'/minimum term face',r['bounds']['lower']['value'],f)
            witness=solve(p,BUDGET,extra=[p.variables['bridge_principal']==q(b),p.variables['term_face']==q(f)])
            check(s['id']+'/independent witness feasible',witness['feasibility'],'Feasible')
            o=oracle(s,F(b),F(f));check(s['id']+'/oracle viability',o['viable'],True)
            for item,(event,cash) in zip(o['prefixes'],prefixes):
                actual=z3.simplify(z3.substitute(cash,(p.variables['bridge_principal'],q(b)),(p.variables['term_face'],q(f))))
                check(s['id']+'/'+event,str(F(str(actual))),item['cash'])
            record.update(witness=witness,independent_cash=o)
        results.append(record)
    # Small exact oracles expose the original failures directly, not only solver status.
    check('SIM-F022 maximum net bridge cash',str(F(30)-1),'29')
    check('SIM-F022 gross amount needed',str(F(30)+1),'31')
    late=oracle(cases[2][0],F(0),F(40))
    check('SIM-F024 day4 prefix',next(x['cash'] for x in late['prefixes'] if x['event']=='day4_old_maturity'),'-30')
    check('SIM-F024 positive final cash cannot rescue prefix',late['cash_ok'],False)
    check('SIM-F024 final cash remains positive',F(late['prefixes'][-1]['cash'])>0,True)
    # Deliberately wrong comparators demonstrate that dropping a constraint changes the answer.
    wrong=spec('fee omitted mutation',bridge_fee='0');p,_=problem(wrong)
    # Retain only through old maturity: the original fee/cap question is day4.
    p.constraints=[(n,x) for n,x in p.constraints if not n.startswith('cash_prefix/day5') and not n.startswith('cash_prefix/day6') and not n.startswith('cash_prefix/day9')]
    r=solve(p,BUDGET,p.outputs['bridge_principal']);check('wrong fee-free comparator passes day4',r['feasibility'],'Feasible')
    check('wrong fee-free amount',r['bounds']['lower']['value'],'30');results.append(dict(input=wrong,result=r,role='target-changing mutation, not accepted offer'))
    p,_=problem(cases[2][0]);p.constraints=[(n,x) for n,x in p.constraints if not n.startswith('cash_prefix/') or n=='cash_prefix/day9_customer']
    r=solve(p,BUDGET,p.outputs['term_face']);check('wrong final-only comparator passes',r['feasibility'],'Feasible');results.append(dict(input=cases[2][0],result=r,role='wrong final-only liquidity target'))
    p,_=problem(cases[6][0]);p.constraints=[(n,x) for n,x in p.constraints if n!='term_settlement_inventory']
    r=solve(p,BUDGET,p.outputs['term_face']);check('wrong stale-inventory comparator passes',r['feasibility'],'Feasible')
    check('wrong stale-inventory face',r['bounds']['lower']['value'],'190/9');results.append(dict(input=cases[6][0],result=r,role='wrong omitted settlement eligibility'))
    original=json.loads((ROOT/'data/accounting-master/unified-program-20261028/failure-map.json').read_text())
    rows=[x['original_row'] for x in original['rows'] if x['original_row']['id'] in ['SIM-F022','SIM-F023','SIM-F024']]
    failed=[x['name'] for x in checks if not x['passed']]
    verification=dict(status='fail' if failed else 'pass',checks=len(checks),cases=len(cases),mutated_target_controls=3,failed=failed,
        original_rows=[x['id'] for x in rows],original_statuses_changed=False,production_event_engine=False,policy_nonanticipativity_tested=False)
    inputs=[Path(__file__),ROOT/PLAN,ROOT/SOURCE,ROOT/'data/accounting-master/simulation-monograph-20261026/arithmetic.json',ROOT/'data/accounting-master/unified-program-20261028/failure-map.json']
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_file() and Path(path).resolve().is_relative_to(ROOT):inputs.append(Path(path).resolve())
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=sys.version,
        cpu_gpu='CPU-only exact rational SMT; no accelerator imports',random_seeds='N/A deterministic feasibility',utc=datetime.now(timezone.utc).isoformat(),
        wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((HERE/'result.md').relative_to(ROOT)),data_version=SOURCE,
        source_hashes={str(x.relative_to(ROOT)):sha256(x.read_bytes()).hexdigest() for x in sorted(set(inputs))})
    for name,value in [('verification',verification),('checks',checks),('results',results),('constraints',constraints),('original-rows',rows),('run-manifest',manifest)]:
        (out/(name+'.json')).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(verification));return bool(failed)

if __name__=='__main__':raise SystemExit(main())
