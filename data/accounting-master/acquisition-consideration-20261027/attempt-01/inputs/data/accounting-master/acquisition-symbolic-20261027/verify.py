"""Preserved deterministic expressions, scope bindings and adversarial controls."""
from pathlib import Path
from hashlib import sha256
from copy import deepcopy
from fractions import Fraction
from datetime import datetime,timezone
import json,sys,os,resource,time,platform,subprocess,traceback
import reference as m
from expected import expected
H=Path(__file__).resolve().parent;R=H.parents[2]
PRIOR=R/'data/accounting-master/control-group-boundary-20261027/attempt-02'
SAVED=json.loads((PRIOR/'cases.json').read_text())
AT='2025-07-01T00:00:00Z';END='2026-01-01T00:00:00Z'
def bind(b):b['expected_payload_sha256']=m.h.digest(b['payload']);return b
def fixture(election='proportional',prior='none',scope_id='gain'):
    sr=deepcopy(next(row['request'] for row in SAVED if row['id']==scope_id))
    fraction='1/1' if election=='none' else '3/4'
    for side in ['opening','closing']:sr['group_request'][side]['world']['control_edges'][0]['ownership_fraction']=fraction
    sr['expected_group_sha256']=m.h.digest(sr['group_request'])
    source=dict(text='Synthetic premise for a formal unknown-amount dependency test; not company measurement.',subject=['P','S'],actor='manager',available_at='2025-01-01T00:00:00Z')
    sid=m.h.digest(source)
    roles=['A','L','T','R','D','O','U']+(['V','M'] if election!='none' else [])+(['Q'] if election=='fair_value' else [])+(['P'] if prior=='equity' else [])
    kinds={'A':'recognised_assets','L':'assumed_liabilities','T':'consideration_transferred','P':'prior_equity_fair_value','Q':'nci_fair_value','R':'post_control_legal_profit','D':'post_control_expense_adjustment','O':'post_control_legal_oci','U':'post_control_oci_adjustment','V':'post_control_nci_distributions','M':'post_control_other_nci_changes'}
    amounts={role:dict(symbol=role,kind=kinds[role],currency='USD',unit='currency_unit',timing=dict(at=AT) if role in ['A','L','T','P','Q'] else dict(start=AT,end_exclusive=END),basis='Unknown amount; conditional selected measurement basis',evidence_sha256=sid) for role in roles}
    p=dict(scope_request=sr,route=dict(kind='ordinary_business_acquisition',evidence_sha256=sid),prior_interest=dict(kind=prior,evidence_sha256=sid),ownership=dict(fraction=fraction,rights='constant_ordinary_present_rights',nci_election=election,evidence_sha256=sid),acquisition=dict(at=AT,currency='USD',unit='currency_unit'),amounts=amounts,sources={sid:source})
    return bind(dict(profile=m.PROFILE,payload=p,expected_payload_sha256=''))
def source_change(b,key,value):
    p=b['payload'];sid=next(iter(p['sources']));source=p['sources'].pop(sid);source[key]=value;new=m.h.digest(source);p['sources'][new]=source
    for item in [p['route'],p['prior_interest'],p['ownership'],*p['amounts'].values()]:item['evidence_sha256']=new
    return bind(b)
def evaluate(expr,values):return Fraction(expr['constant'])+sum(Fraction(c)*values[s] for s,c in expr['coefficients'].items())
def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' and os.environ.get('PYTHONDONTWRITEBYTECODE')=='1'
    resource.setrlimit(resource.RLIMIT_CPU,(100,100));out=H/sys.argv[1];out.mkdir(exist_ok=False)
    started=datetime.now(timezone.utc).isoformat();clock=time.monotonic();checks=[];cases=[];controls=[]
    files={H/'reference.py',H/'verify.py',H/'expected.py',H/'contract.md',R/'docs/plans/accounting-acquisition-symbolic-20261027.md',PRIOR/'cases.json',PRIOR/'verification.json',PRIOR/'source-lock.json'}
    files.update(R/p for p in m.PINS)
    files.update(R/p for p in json.loads((PRIOR/'source-lock.json').read_text()))
    lock={str(p.relative_to(R)):sha256(p.read_bytes()).hexdigest() for p in files}
    for p in files:
        dest=out/'inputs'/p.relative_to(R);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(p.read_bytes())
    def ck(name,a,b=True):
        checks.append(dict(name=name,passed=a==b))
        if a!=b:raise AssertionError(name+': '+repr(a)[:160]+' != '+repr(b)[:160])
    def run(name,b,oracle=None,status='conditional_expressions',dependency=None,reason=None):
        before=deepcopy(b);r=m.derive(b);ck(name+'/status',r['status'],status);ck(name+'/immutable',b,before)
        ck(name+'/flags',[r[k] for k in m.FLAGS],[False]*len(m.FLAGS))
        ck(name+'/no_financial_report',not {'goodwill','bargain_gain','journals','cash_flows','balance_sheet','legal_reports'} & set(r))
        if status=='invalid':
            ck(name+'/reason',r['reason'],reason);controls.append(dict(id=name,request=b,result=r));return r
        ck(name+'/whole_scope',r['scope_result'],m.scope.scope(b['payload']['scope_request']))
        ck(name+'/descriptors',r['descriptors'],b['payload']['amounts'])
        ck(name+'/request_identity',r['request_sha256'],m.h.digest(b))
        ck(name+'/premises',r['premises'],{k:v for k,v in b['payload'].items() if k not in ['scope_request','amounts']})
        if oracle is not None:ck(name+'/all_expressions',r['expressions'],oracle)
        if dependency:ck(name+'/dependency',any(x.startswith(dependency) for x in r['dependencies']))
        if status=='unresolved':ck(name+'/no_expressions',r['expressions'],{})
        else:
            ck(name+'/unmeasured',r['dependencies'],['unmeasured:'+k for k in sorted(b['payload']['amounts'])])
            ck(name+'/recognition',r['recognition'],'not_assessed')
        cases.append(dict(id=name,request=b,result=r));return r
    def invalid(name,b,reason):return run(name,bind(b),status='invalid',reason=reason)
    try:
        for election in ['proportional','fair_value','none']:
            for prior in ['none','equity']:
                b=fixture(election,prior);r=run(election+'/'+prior,b,expected(election,prior))
                for t in [Fraction(0),Fraction(3),Fraction(400)]:
                    x={k:Fraction(v) for k,v in dict(A=120,L=20,T=t,P=7,Q=31,R=-1000,D=10,O=-20,U=5,V=4,M=-3).items()}
                    e={k:evaluate(v,x) for k,v in r['expressions'].items()}
                    q=0 if election=='none' else Fraction(1,4);nci=0 if election=='none' else (31 if election=='fair_value' else 25)
                    ck('substitution/excess/'+election+'/'+prior+'/'+str(t),e['acquisition_excess'],t+nci+(7 if prior=='equity' else 0)-100)
                    ck('substitution/acquisition_identity',e['acquisition_excess']+x['A']-x['L']-x['T']-e['nci_at_acquisition']-e['qualifying_prior_equity'],0)
                    ck('substitution/profit_allocation',e['owners_profit']+e['nci_profit'],x['R']-x['D'])
                    ck('substitution/oci_allocation',e['owners_oci']+e['nci_oci'],x['O']+x['U'])
                    ck('substitution/nci_roll',e['nci_closing'],nci+q*(-1025)-7 if q else 0)
                    if q:ck('substitution/negative_nci_preserved',e['nci_closing']<0)
        b=fixture();b['payload']['acquisition']['at']='2025-07-01T08:00:00+08:00';run('equivalent_exact_offset',bind(b),expected())
        b=fixture();b['payload']['amounts']['A']['symbol']='assets';oracle=expected()
        for expr in oracle.values():
            if 'A' in expr['coefficients']:expr['coefficients']['assets']=expr['coefficients'].pop('A')
        run('distinct_symbol_preserved',bind(b),oracle)
        for role in ['A','T','D','M']:
            b=fixture();del b['payload']['amounts'][role];run('missing/'+role,bind(b),status='unresolved',dependency='missing_amount:'+role)
        for prior in ['debt','unresolved']:
            b=fixture();b['payload']['prior_interest']['kind']=prior;run('prior/'+prior,bind(b),status='unresolved',dependency='prior_interest_and_separate_transaction_analysis:'+prior)
        for route in ['asset_acquisition','common_control','investment_entity','separate_report']:
            b=fixture();b['payload']['route']['kind']=route;run('route/'+route,bind(b),status='unresolved',dependency='acquisition_route:'+route)
        for avail,label,prefix in [(None,'unknown','source_availability_unknown:'),('2026-02-01T00:00:00Z','future','source_after_cutoff:')]:run('availability/'+label,source_change(fixture(),'available_at',avail),status='unresolved',dependency=prefix)
        for name in ['uninterrupted','loss_regain','unknown_prior']:
            match={'uninterrupted':'continuous-control','loss_regain':'loss-regain-matching-endpoints','unknown_prior':'unknown-before-control'}[name]
            candidates=[x['id'] for x in SAVED]
            if match not in candidates:raise AssertionError('missing_planned_baseline:'+match+' available:'+str(candidates))
            b=fixture(scope_id=match);run(name,b,status='unresolved',dependency='unresolved_control_history' if name=='unknown_prior' else 'single_gain_method_required')
        b=fixture();b['payload']['ownership']['rights']='participating_preference_rights';run('unsupported_rights',bind(b),status='unresolved',dependency='ownership_rights_method:')
        b=fixture();b['payload']['ownership']['nci_election']='unresolved';run('unknown_election',bind(b),status='unresolved',dependency='nci_measurement_election')
        b=fixture();b['payload']['amounts']['A']['basis']='changed';run('stale_envelope',b,status='invalid',reason='payload_binding')
        b=fixture('proportional','equity');b['payload']['amounts']['P']['kind']='debt_claim';invalid('debt_as_equity',b,'amount_kind:P')
        b=fixture();b['payload']['amounts']['T']['currency']='HKD';invalid('currency_mismatch',b,'amount_unit:T')
        b=fixture();b['payload']['acquisition']['currency']='HKD'
        for item in b['payload']['amounts'].values():item['currency']='HKD'
        invalid('wrong_book_currency',b,'book_currency_binding')
        b=fixture();b['payload']['amounts']['T']['unit']='thousands';invalid('unit_mismatch',b,'amount_unit:T')
        b=fixture();b['payload']['amounts']['A']['timing']['at']='2025-07-02T00:00:00Z';invalid('measurement_date',b,'amount_date:A')
        b=fixture();b['payload']['amounts']['R']['timing']['start']='2025-01-01T00:00:00Z';invalid('precontrol_profit_leak',b,'post_control_interval:R')
        b=fixture();b['payload']['amounts']['D']['timing']['end_exclusive']='2027-01-01T00:00:00Z';invalid('late_expense_leak',b,'post_control_interval:D')
        b=fixture();b['payload']['acquisition']['at']='2025-07-01T00:00:00.1Z';invalid('subday_rounding',b,'acquisition_control_date')
        b=fixture();b['payload']['ownership']['fraction']='1/2';invalid('ownership_scope_mismatch',b,'ownership_scope_binding')
        b=fixture();b['payload']['amounts']['L']['symbol']='A';invalid('aliased_unknowns',b,'duplicate_symbol')
        b=fixture();b['payload']['amounts']['T']['value']='80/1';invalid('invented_face_value',b,'amount_fields')
        invalid('wrong_actor',source_change(fixture(),'actor','analyst'),'source_actor')
        invalid('wrong_subject',source_change(fixture(),'subject',['X','S']),'source_subject')
        b=fixture();next(iter(b['payload']['sources'].values()))['text']='changed';invalid('source_tamper',b,'source_identity')
        b=fixture();b['payload']['amounts']['A']['evidence_sha256']='0'*64;invalid('missing_source',b,'missing_source')
        b=fixture('none');b['payload']['amounts']['V']=fixture()['payload']['amounts']['V'];invalid('nci_in_full_ownership',b,'no_nci_with_movements')
        b=fixture();b['payload']['amounts']['P']=fixture('proportional','equity')['payload']['amounts']['P'];invalid('prior_none_nonzero',b,'prior_none_with_amount')
        b=fixture();b['payload']['amounts']['Q']=fixture('fair_value')['payload']['amounts']['Q'];invalid('double_nci_measurement',b,'nci_election_with_amount')
        b=fixture();b['payload']['route']['extra']='assumed';invalid('open_schema',b,'route_fields')
        b=fixture();b['payload']['scope_request']['history_request']['actor']='analyst';invalid('stale_history',b,'scope:history_binding')
        for filename in ['unchanged','changed-control','partial-ownership']:
            saved=json.loads((PRIOR.parent/'baseline-attempt-01'/(filename+'.json')).read_text())
            ck('stable_report_baseline/'+filename,m.scope.group.report(saved['request']),saved['result'])
        for p,d in lock.items():ck('protected/'+p,sha256((R/p).read_bytes()).hexdigest(),d)
        result=dict(status='PASS',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),protected_files=len(lock),source_admission=False,accounting_admission=False,posting_authorized=False,report_authorized=False)
    except Exception:result=dict(status='FAIL',cases=len(cases),refusal_controls=len(controls),assertions=len(checks),error=traceback.format_exc())
    for name,obj in [('verification.json',result),('cases.json',cases),('controls.json',controls),('checks.json',checks),('source-lock.json',lock)]:
        (out/name).write_text(json.dumps(obj,indent=2)+'\n')
    manifest=dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),command='env CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 python3 '+str(Path(__file__).relative_to(R))+' '+sys.argv[1],environment=platform.python_version(),cpu_gpu='CPU; GPU intentionally hidden',random_seeds='N/A deterministic algebra',started_utc=started,wall_seconds=time.monotonic()-clock,data_version='source-lock.json',plan='docs/plans/accounting-acquisition-symbolic-20261027.md',result=str((H/'result.md').relative_to(R)),output=str(out.relative_to(R)))
    (out/'run-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps(result))
    if result['status']!='PASS':raise SystemExit(1)
if __name__=='__main__':main()
