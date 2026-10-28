"""Original face110/book100 bridge: explicit finite family and native reports."""
import argparse
from copy import deepcopy
from dataclasses import replace
from datetime import datetime,timezone
from fractions import Fraction as Q
from hashlib import sha256
from itertools import product
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3];H=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'scripts'))
import z3
from rational_solver_v1 import Problem,Budget,q,solve
SOURCE=ROOT/'data/accounting-master/literature-closure-20261026/runtime-integration.py'
spec=importlib.util.spec_from_file_location('retained_book_contract_factory',SOURCE)
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
program=base.program
PLAN='docs/plans/company-state-book-contract-failure-20261028.md'
ANCHOR='docs/design/proposal/manuscript-release-prep-v552r2-20261027/simulation/25-interactions.tex'
BUDGET=Budget(10,10000,100,100,10000,1000,1000000)
def fmt(value):return base.fmt(value)
def dump(path,value):path.write_text(json.dumps(value,indent=2)+chr(10))

def bridge(book=100,discount_evidence=None):
    face,discount=z3.Ints('promised_face unamortized_discount')
    p=Problem('Original SIM-F026 finite book-to-contract bridge','synthetic unweighted hypotheses')
    p.variables=dict(face=face,discount=discount);p.finite=dict(face=[100,110],discount=[0,10])
    p.add('supplied no-fee/no-accrued-interest measurement bridge',face-discount==q(book))
    if discount_evidence is not None:p.add('separately supplied discount evidence',discount==q(discount_evidence))
    p.outputs=dict(face=face,discount=discount,book=q(book),hypothetical_proceeds=face/q(Q(21,20)))
    p.provenance=dict(observed_book=str(book),discount_evidence=None if discount_evidence is None else str(discount_evidence),gross_return='21/20',probability=None,source_admission=False,domain_exhaustive_for_real_company=False)
    return p

def report_body(face,owner):
    body,m=base.make('fixed',owner);book=body['opening']
    book['balances']={k:'0/1' for k in book['balances']}
    book['balances'].update({m['cash']:'20/1',m['inventory']:'100/1',m['debt']:'-100/1',m['capital']:'-20/1'})
    book['memory']['terms']['face']=fmt(face)
    body['registry']['entries']={'coupon':body['registry']['entries']['coupon']}
    body['commands']=[dict(kind='report',id='observed.book',cutoff='2027-01-01',equity_movements=[],notes=[dict(id='contract',label='Book and contract are separate',status='unresolved',reason='Finite supplied histories; no real contract or measurement admission and no pricing transaction')])]
    body['name']='book100-face'+str(face)+'-'+owner
    return body,m

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True,type=Path)
    out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
    checks=[];solver_results=[];native_results=[];formulae=[];oracle=[]
    def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
    def sr(name,p,obj=None,extra=(),budget=BUDGET):
        r=solve(p,budget,obj,extra=extra);solver_results.append(dict(id=name,result=r));return r
    for name,book,evidence in [('unknown_face',100,None),('discount10_selects_face110',100,10),('explicit_no_discount_selects100',100,0),('declared_domain_conflict',95,None)]:
        p=bridge(book,evidence)
        formulae.append(dict(id=name,constraints=[dict(label=n,expression=e.sexpr()) for n,e in p.constraints],outputs={k:v.sexpr() for k,v in p.outputs.items()},provenance=p.provenance))
        expected=[[face,discount] for face,discount in product([100,110],[0,10]) if face-discount==book and (evidence is None or discount==evidence)]
        found=[]
        for face,discount in product([100,110],[0,10]):
            r=sr(name+'/'+str(face)+'/'+str(discount),p,extra=[p.variables['face']==face,p.variables['discount']==discount])
            ck(name+'/'+str(face)+'/'+str(discount)+'/feasible',r['feasibility'],'Feasible' if [face,discount] in expected else 'Infeasible')
            ck(name+'/'+str(face)+'/'+str(discount)+'/complete',r['coverage']['complete'],True)
            if r['feasibility']=='Feasible':found.append([face,discount])
        ck(name+'/exact joint family',found,expected)
        oracle.append(dict(id=name,enumerated_family=expected,prices=[dict(face=face,discount=discount,book=book,hypothetical_proceeds=fmt(Q(face)*Q(20,21)),probability=None) for face,discount in expected]))
        r=sr(name+'/proceeds bounds',p,p.outputs['hypothetical_proceeds'])
        ck(name+'/aggregate feasibility',r['feasibility'],'Feasible' if expected else 'Infeasible')
        if expected:
            expected_prices=[Q(face)*Q(20,21) for face,_ in expected]
            ck(name+'/price bounds',[r['bounds'][key]['value'] for key in ['lower','upper']],[str(min(expected_prices)),str(max(expected_prices))])
    p=bridge();r=sr('zero budget',p,p.outputs['hypothetical_proceeds'],budget=replace(BUDGET,max_cells=0))
    ck('budget unknown',r['feasibility'],'Unknown');ck('budget incomplete',r['coverage']['complete'],False)
    ck('budget formula preserved',bool(r['coverage']['unvisited']['retained_formula']),True)
    ck('budget remainder retained',r['coverage']['unresolved']>0,True)
    ck('original promised110 minus carrying100',110-100,10)
    ck('correct conditional proceeds',fmt(Q(110)*Q(20,21)),'2200/21')
    ck('value differs from book and promise',Q(2200,21) not in [100,110],True)
    ck('wrong face substitution value',fmt(Q(100)*Q(20,21)),'2000/21')
    ck('wrong reconstruction price error',fmt(Q(2200,21)-Q(2000,21)),'200/21')
    ck('calibrating rate to book changes supplied law',Q(110,100)!=Q(21,20),True)
    old=base.native.Engine.apply;base.native.Engine.apply=lambda *a,**k:(_ for _ in ()).throw(AssertionError('legacy posting fallback forbidden'))
    try:
        for owner in ['alpha','beta']:
            reports=[]
            for face in [100,110]:
                b,m=report_body(face,owner);before=deepcopy(b);r=program.run(b);name=owner+'/face'+str(face)
                ck(name+'/complete',r['status'],'complete_provisional')
                ck(name+'/input unchanged',program.digest(b),program.digest(before))
                ck(name+'/replay',program.verify(b,r),True)
                native_results.append(dict(id=name,input=b,result=r))
                if r['status']!='complete_provisional':continue
                ck(name+'/complete unchanged book',r['current'],b['opening'])
                ck(name+'/face memory',r['current']['memory']['terms']['face'],fmt(face))
                ck(name+'/carrying debt',r['current']['balances'][m['debt']],'-100/1')
                ck(name+'/no pricing cash or journal event',[r['current']['balances'][m['cash']],r['current']['flows'],[x['command']['kind'] for x in r['trace']]],['20/1',[],['report']])
                report=r['trace'][0]['result'];reports.append(report)
                ck(name+'/balance sheet',report['balance_sheet'],dict(total_assets='120/1',total_liabilities='100/1',equity_including_profit='20/1'))
                ck(name+'/income',report['income'],dict(income='0/1',expenses='0/1',profit='0/1'))
                ck(name+'/cash bridge',[report['cash_flows'][k] for k in ['opening_cash','closing_cash','net_movement']],['20/1','20/1','0/1'])
                ck(name+'/reconciliations',report['reconciliations'],dict(balance_sheet='0/1',cash='0/1',equity='0/1'))
                ck(name+'/admission',[report[k] for k in ['source_admission','accounting_admission','fiscal_complete']],[False]*3)
            ck(owner+'/same reported amounts different promises',[reports[0][k] for k in ['balance_sheet','income','cash_flows','equity']],[reports[1][k] for k in ['balance_sheet','income','cash_flows','equity']])
            b,m=report_body(110,owner);b['opening']['memory']['terms']['face']='100/1';r=program.run(b)
            native_results.append(dict(id=owner+'/deliberately_replace_face_by_book',input=b,result=r))
            ck(owner+'/wrong substituted report can balance',r['status'],'complete_provisional')
            ck(owner+'/independent promised amount rejects',r['current']['memory']['terms']['face']=='110/1',False)
    finally:base.native.Engine.apply=old
    fm=ROOT/'data/accounting-master/unified-program-20261028/failure-map.json'
    original=[x['original_row'] for x in json.loads(fm.read_text())['rows'] if x['original_row']['id']=='SIM-F026']
    ck('original target',[x['discriminating_case'] for x in original],['Face110 and carrying amount100'])
    ck('manuscript interaction anchor','face 110, carrying amount 100 and proceeds different from both' in (ROOT/ANCHOR).read_text(),True)
    paths={Path(__file__),ROOT/PLAN,ROOT/ANCHOR,fm}
    paths.update(Path(x.__file__).resolve() for x in list(sys.modules.values()) if getattr(x,'__file__',None) and Path(x.__file__).resolve().is_relative_to(ROOT))
    hashes={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}
    failed=[x for x in checks if not x['passed']]
    verdict=dict(status='fail' if failed else 'pass',checks=len(checks),solver_cases=len(solver_results),native_report_cases=len(native_results),failed=failed,original_rows=['SIM-F026'],native_pricing_or_repayment=False,source_admission=False)
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command=[sys.executable,*sys.argv],environment=dict(python=platform.python_version(),z3=z3.get_version_string()),cpu_gpu='CPU-only exact rational/Z3/native report; no accelerator imports',random_seeds='N/A deterministic finite domain',data_version='Original SIM-F026 plus explicit finite no-fee/no-accrued-interest bridge and pricing assumption',utc=datetime.now(timezone.utc).isoformat(),wall_seconds=time.monotonic()-start,plan_file=PLAN,result_file=str((H/'result.md').relative_to(ROOT)),source_hashes=hashes)
    for name,obj in [('verification',verdict),('checks',checks),('solver-results',solver_results),('native-results',native_results),('independent-enumeration',oracle),('formulae',formulae),('original-rows',original),('run-manifest',manifest)]:dump(out/(name+'.json'),obj)
    (out/'check.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(verdict));return bool(failed)
if __name__=='__main__':raise SystemExit(main())

