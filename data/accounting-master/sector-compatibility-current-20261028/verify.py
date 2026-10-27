"""Bounded sector regression and independent retained capital arithmetic."""
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import ast, gzip, importlib.util, json, os, subprocess, sys, time

HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]; BASE=HERE.parent
def read(p): return json.loads(p.read_text())
def digest(p): return sha256(p.read_bytes()).hexdigest()
def load(name,p):
    sys.path.insert(0,str(p.parent));spec=importlib.util.spec_from_file_location(name,p)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def main():
    assert len(sys.argv)==2 and len(Path(sys.argv[1]).parts)==1 and sys.argv[1] not in {'.','..'}
    out=HERE/sys.argv[1];out.mkdir(exist_ok=False);start=time.monotonic();checks=[];lock={};success=False;artifacts=[]
    def check(name,actual,expected=True):
        checks.append(dict(name=name,passed=actual==expected));assert actual==expected,name
    def protect(p,expected=None):
        key=str(p.relative_to(ROOT));h=digest(p)
        if expected is not None:check('identity:'+key,h,expected)
        if key in lock:check('consistent:'+key,h,lock[key])
        lock[key]=h
    def save(name,value):
        p=out/(name+'.json.gz');p.write_bytes(gzip.compress(json.dumps(value,separators=(',',':')).encode(),mtime=0))
        check('roundtrip:'+name,json.loads(gzip.decompress(p.read_bytes())),value);artifacts.append(dict(path=p.name,sha256=digest(p),bytes=p.stat().st_size))
    try:
        check('CPU-only',os.environ.get('CUDA_VISIBLE_DEVICES'),'-1')
        for p in [Path(__file__),HERE/'compatibility.md',ROOT/'docs/plans/accounting-sector-compatibility-20261028.md']:protect(p)
        pkg=ROOT/'docs/design/proposal/manuscript-reference-v555r1-20261027'; manifest=read(pkg/'package-manifest.json');protect(pkg/'package-manifest.json')
        package_hashes={x['path']:x['sha256'] for x in manifest['files']}
        for component in ['insurance-paa-dated-book','bank-interfaces']:
            d=pkg/'companions'/component
            for p in d.iterdir():
                if p.is_file():protect(p,package_hashes[str(p.relative_to(pkg))])
            data=read(d/'component.json');check(component+':archive',digest(d/data['archive']),data['archive_sha256'])
        paa=BASE/'insurance-paa-dated-book-20261027'
        for p in [paa/'bridge.py',paa/'authored.py',paa/'contract.md',paa/'authored-expectations.json',paa/'attempt-01/cases.json',paa/'attempt-01/controls.json',paa/'source-lock.json']:protect(p)
        for name,h in read(paa/'source-lock.json').items():protect(ROOT/name,h)
        bridge=load('current_sector_paa_bridge',paa/'bridge.py');cases=read(paa/'attempt-01/cases.json');expectations=read(paa/'authored-expectations.json');outputs=[]
        for row in cases:
            before=deepcopy(row['request']);actual=bridge.propose(row['request']);label=row['id']
            check(label+':complete native result',actual,row['result']);check(label+':input unchanged',row['request'],before)
            report=actual['execution']['trace'][-1]['result'];expected=expectations[label]
            check(label+':complete report',report,row['report'])
            for field,value in expected['financial'].items():check(label+':independent report:'+field,report[field],value)
            check(label+':independent closing balances',actual['execution']['current']['balances'],expected['closing'])
            for field,value in expected['cash'].items():check(label+':independent cash:'+field,report['cash_flows'][field],value)
            for flag in bridge.FLAGS:check(label+':no admission:'+flag,actual[flag],False)
            outputs.append(dict(id=label,request=row['request'],result=actual))
        check('seven complete PAA cases',len(outputs),7);save('paa-cases',outputs);controls=[]
        for row in read(paa/'attempt-01/controls.json'):
            key='request' if 'request' in row else 'compiled';body=deepcopy(row[key]);before=deepcopy(body)
            actual=bridge.propose(body) if key=='request' else bridge.program.run(body)
            check(row['id']+':complete refusal',actual,row['result']);check(row['id']+':input unchanged',body,before)
            controls.append(dict(id=row['id'],input=body,result=actual))
        check('twenty-one refusal controls',len(controls),21);save('paa-controls',controls)
        profiles=[]
        for name,attempt,profile in [('bank','attempt-03','BankComponents/1'),('bank-v2','attempt-02','BankComponents/2'),('bank-assessment','attempt-03','BankAssessment/1')]:
            folder=BASE/'extended-method-exchanges-20261015'/name
            for p in [folder/'semantic-contract.md',folder/'verify_exchanges.py',folder/attempt/'record-schemas.json',folder/attempt/'portable-exchanges.json']:protect(p)
            packet=read(folder/attempt/'portable-exchanges.json');pr=[r for r in packet['record_registry'].values() if r['kind']=='Profile']
            check(profile+':one profile',len(pr),1);check(profile+':identity',pr[0]['body']['profile_id'],profile)
            profiles.append(dict(profile=profile,operations=pr[0]['body']['operations'],schema=pr[0]['schema'],contract=str((folder/'semantic-contract.md').relative_to(ROOT))))
            if name=='bank-assessment':bank=packet
        exact=BASE/'exact-bank-profile-adoption-20261026'
        for leaf in ['semantic-contract.md','record-schemas.json','successor.py','adapted_methods.py','ordinary-comparisons.json','timing-comparisons.json','checks.json']:protect(exact/leaf)
        profiles.append(dict(profile='BankAssessmentExactTime/1',contract=str((exact/'semantic-contract.md').relative_to(ROOT)),owner=str((exact/'successor.py').relative_to(ROOT)),scope='Pinned financial definitions with explicit exact-clock envelope conversion'))
        extract=BASE/'bank-interface-consolidation-20261027/worked-case-extract.json';protect(extract);rows=read(extract)
        protect(ROOT/rows['source'],rows['sha256']);calculations=[]
        for row in rows['rows']:
            label=row['case'];b={k:Q(v) for k,v in row['balances'].items()};basis=bank['record_registry'][row['input_ref']['digest']]['body'];native=bank['record_registry'][row['output_ref']['digest']]['body']
            for category in ['amounts','ratios']:
                check(label+':complete '+category+' names',set(row[category]),set(native[category]))
                for key,field in native[category].items():
                    q=field['value'];value=None if q is None else str(Q(int(q['n']),int(q['d'])))
                    check(label+':extracted '+category+':'+key,row[category][key],dict(value=value,status=field['status'],diagnostics=field['diagnostics']))
                    for reference in field['dependency_refs']:
                        check(label+':retained dependency:'+reference['digest'],reference['digest'] in bank['record_registry'])
            check(label+':no posting',native['accounting_effect'],'none')
            check(label+':balanced book',sum(b.values()),Q(0));G=b['loans'];A=-b['allowance'];W=b['goodwill'];E=-(b['stock']+b['retained']+b['interest_income']+b['deposit_expense']+b['loss_expense']);T=min(A,G/80);X=A-T;RWA=G-X
            amounts=dict(book_equity=E,gross_loans=G,allowance=A,goodwill=W,cap_base=G,cap=G/80,admitted_allowance=T,excess_allowance=X,rwa=RWA,cet1=E-W,tier1=E-W,tier2=T,total_capital=E-W+T)
            ratios=dict(cet1_ratio=(E-W)/RWA,tier1_ratio=(E-W)/RWA,total_ratio=(E-W+T)/RWA)
            average=basis['average_ref']
            if average is None:
                check(label+':missing average unresolved',row['ratios']['leverage_ratio']['status'],'unresolved');check(label+':no invented leverage',row['ratios']['leverage_ratio']['value'],None)
            else:
                q=bank['record_registry'][average['digest']]['body']['amount'];M=Q(int(q['n']),int(q['d']));amounts['leverage_denominator']=M-W;ratios['leverage_ratio']=(E-W)/(M-W)
            for key,value in amounts.items():check(label+':amount:'+key,Q(row['amounts'][key]['value']),value)
            for key,value in ratios.items():check(label+':ratio:'+key,Q(row['ratios'][key]['value']),value)
            calculations.append(dict(case=label,amounts={k:str(v) for k,v in amounts.items()},ratios={k:str(v) for k,v in ratios.items()},unpaid_withdrawal=row['unpaid_withdrawal']))
        check('five retained bank cases',len(calculations),5);save('bank-calculations',calculations);save('profile-identities',profiles)
        for f,h in lock.items():check('unchanged:'+f,digest(ROOT/f),h)
        success=True
    finally:
        (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n');(out/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
        m=dict(passed=success,git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/sector-compatibility-current-20261028/verify.py '+sys.argv[1],environment=sys.version,cpu_gpu='CPU only; GPU intentionally hidden',random_seeds='N/A deterministic engineering regression',wall_seconds=time.monotonic()-start,utc=datetime.now(timezone.utc).isoformat(),data_version=digest(out/'source-lock.json'),artifacts=artifacts,plan_file='docs/plans/accounting-sector-compatibility-20261028.md',result_file='data/accounting-master/sector-compatibility-current-20261028/result.md')
        (out/'run-manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(passed=success,checks=len(checks),failed=[x['name'] for x in checks if not x['passed']],locked_files=len(lock),artifacts=len(artifacts),wall_seconds=m['wall_seconds'])))

if __name__=='__main__':main()
