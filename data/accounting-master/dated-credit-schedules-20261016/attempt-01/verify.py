"""Independent authored examples, rational certificates and atomic refusals."""
from copy import deepcopy
from datetime import datetime,timezone
from decimal import Decimal,localcontext
from fractions import Fraction as Q
from math import gcd
import hashlib,json,os,shutil,subprocess,sys,time
sys.dont_write_bytecode=True
from reference import OUT,ROOT,SOURCE,EVENT_FINDINGS,calculate
from bounds import I,factor,day,solve_rate

def interval(w):return I(Q(w['lower']),Q(w['upper']))
def dec(q):q=Q(q);return Decimal(q.numerator)/Decimal(q.denominator)

def main():
    started=time.monotonic();nums=[int(p.name.split('-')[-1]) for p in OUT.glob('attempt-[0-9][0-9]')]
    attempt=OUT/('attempt-%02d'%(max(nums,default=0)+1));attempt.mkdir()
    for name in ('reference.py','bounds.py','verify.py','authored-cases.json','input-lock.json'):shutil.copy2(OUT/name,attempt/name)
    checks=[];exchanges=[];adverse=[];certificates=[];roots=[]
    def check(name,ok,detail=None):checks.append(dict(name=name,passed=bool(ok),detail=detail))
    for row in json.loads((OUT/'input-lock.json').read_text())['files']:
        check('protected/'+row['path'],hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'])
    cases=json.loads((OUT/'authored-cases.json').read_text())['cases']
    for c in cases:
        req=deepcopy(c['request']);before=deepcopy(req);r=calculate(req);prefix=c['id']+'/'
        exchanges.append(dict(id=c['id'],request=req,result=r));check(prefix+'status',r['status']=='conditional_complete',r['reason'])
        check(prefix+'repeatable-readonly',before==req and r==calculate(req) and r['mutations']==[] and not r['posts'])
        if r['status']!='conditional_complete':continue
        check(prefix+'financial-close',r['financial_derecognized'])
        for key,target in [('cash',c['expected']['final_cash']),('profit',c['expected']['final_profit'])]:check(prefix+'final-'+key,interval(r['closing'][key]).contains(Q(target)))
        check(prefix+'initial-shortfall',interval(r['initial_credit_shortfall']).contains(Q(c['expected']['initial_shortfall'])))
        stages={s['id']:s for s in r['stages']}
        with localcontext() as dc:
            dc.prec=80;f=(Decimal(11)/10)**(Decimal(181)/365)
            for id,expected in c['expected']['stages'].items():
                for key,target in expected.items():
                    v=interval(stages[id][key])
                    if isinstance(target,str):check(prefix+id+'/'+key,v.contains(Q(target)),dict(target=target,actual=stages[id][key]))
                    else:
                        x=dec(target['f_coefficient'])*f+dec(target['constant'])
                        check(prefix+id+'/'+key+'/independent-decimal',v.contains(Q(x)),dict(expression=target,decimal=str(x),actual=stages[id][key]))
            for s in r['stages']:
                target=sum((dec(v)/(1+dec(req['acquisition']['rate']))**(Decimal((day(d)-day(s['date'])).days)/365) for d,v in s['expected'].items()),Decimal(0))
                check(prefix+s['id']+'/decimal-pv-diagnostic',interval(s['net']).contains(Q(target)) or abs(dec(interval(s['net']).lo)-target)<Decimal('1e-65'))
        for s in r['stages']:
            name=prefix+s['id']+'/'
            for key in ('gross','allowance','net','cash','interest','impairment','catchup','profit','equity','direct_gross','direct_net'):
                v=interval(s[key]);check(name+key+'-bounded',v.width<=Q(req['numerical']['max_width']) and str(v.width)==s[key]['width'])
            check(name+'net-conservation',(interval(s['gross'])-interval(s['allowance'])-interval(s['net'])).contains(0))
            check(name+'financial-equation',(interval(s['cash'])+interval(s['net'])-interval(s['equity'])).contains(0))
            check(name+'income-origins',(interval(s['profit'])-interval(s['interest'])-interval(s['impairment'])-interval(s['catchup'])).contains(0))
        for j in r['journals']:check(prefix+j['id']+'/journal-enclosure',sum((interval(x) for x in j['entries'].values()),I.point(0)).contains(0))
        check(prefix+'cash-origins',Q(req['opening_cash'])+sum(Q(x['amount']) for x in r['cash_flows'])==Q(c['expected']['final_cash']))
        check(prefix+'cash-profit-identity',Q(c['expected']['final_cash'])-Q(req['opening_cash'])==Q(c['expected']['final_profit']))
        check(prefix+'gross-allowance-cleared',all(interval(r['closing'][k])==I.point(0) for k in ('gross','allowance','net')))
        rebuilt={}
        for j in r['journals']:
            for k,v in j['entries'].items():rebuilt[k]=rebuilt.get(k,I.point(0))+interval(v)
        check(prefix+'independent-journal-cash',rebuilt['cash'].contains(Q(c['expected']['final_cash'])-Q(req['opening_cash'])))
        check(prefix+'independent-journal-gross',rebuilt['gross'].contains(0))
        check(prefix+'independent-journal-profit',(-sum((v for k,v in rebuilt.items() if k in ('interest','impairment','catchup')),I.point(0))).contains(Q(c['expected']['final_profit'])))
    for rate in ('-1/10','0','1/10','2'):
        for days in (0,1,181,184,365,366,730,1096):
            v=factor(Q(rate),days,18);g=gcd(days,365);p=days//g;q=365//g;target=(1+Q(rate))**p
            ok=v.lo**q<=target<=v.hi**q
            certificates.append(dict(rate=rate,days=days,p=p,q=q,bounds=v.wire(),endpoint_power_inequalities=ok))
            check('factor/'+rate+'/'+str(days),ok and v.width<=Q(1,10**18))
    fl={'2026-01-01':Q(55),'2027-01-01':Q(121,2)}
    for carrying,label in [(100,'integral-fees-included'),(102,'fee-omitted-counterexample')]:
        root=solve_rate(fl,'2025-01-01',carrying,'0','1/2','1/1000000000000',18);roots.append(dict(label=label,result=root))
        check('root/'+label,interval(root['rate']).width<=Q(1,10**12) and interval(root['low_pv_residual']).lo>=0 and interval(root['high_pv_residual']).hi<=0)
    check('fee-changes-rate',interval(roots[0]['result']['rate']).contains(Q(1,10)) and interval(roots[1]['result']['rate']).hi<Q(1,10))
    for name,fl,st,carry,low,high in [('negative',{'2026-01-01':Q(90)},'2025-01-01',100,'-1/2','0'),('zero',{'2026-01-01':Q(100)},'2025-01-01',100,'-1/2','1/2'),('irregular',{'2025-06-30':Q(40),'2026-03-15':Q(70)},'2025-01-01',100,'0','1/2')]:
        root=solve_rate(fl,st,carry,low,high,'1/1000000000000',18);roots.append(dict(label=name,result=root))
        check('root/'+name,interval(root['rate']).width<=Q(1,10**12) and interval(root['low_pv_residual']).lo>=0 and interval(root['high_pv_residual']).hi<=0)
    try:solve_rate({'2026-01-01':Q(-10),'2027-01-01':Q(120)},'2025-01-01',100,'0','1/2','1/1000',18);rejected=False
    except ValueError:rejected=True
    check('sign-changing-root-refused',rejected)
    base=cases[0]['request']
    def add(name,change,baseline=base):
        q=deepcopy(baseline);change(q);before=deepcopy(q);r=calculate(q);adverse.append(dict(id=name,request=q,result=r))
        check('adverse/'+name,r['status'] in ('rejected','unresolved','unsupported'),r['reason'])
        check('atomic/'+name,before==q and r['closing'] is None and r['stages']==r['journals']==r['cash_flows']==r['mutations']==[])
    for key in base['acquisition']['findings']:
        for val in (None,False):add('acquisition/'+key+'/'+str(val),lambda q,k=key,v=val:q['acquisition']['findings'].update({k:v}))
    for key in EVENT_FINDINGS:
        for val in (None,False):add('event/'+key+'/'+str(val),lambda q,k=key,v=val:q['events'][0]['findings'].update({k:v}))
    mods=[('wire',lambda q:q.update(wire='POCIAnnualTerminal/1')),('posting',lambda q:q.update(operation='post')),('unknown-price',lambda q:q['acquisition'].update(price=None)),
        ('decimal',lambda q:q['acquisition'].update(rate='0.1')),('rate-minus-one',lambda q:q['acquisition'].update(rate='-1')),('omit-cost',lambda q:q['acquisition'].update(cost='0')),
        ('future-info',lambda q:q['events'][0].update(information_date='2026-01-01')),('unknown-recovery',lambda q:q['events'][0]['writeoff'].update(no_reasonable_recovery=None)),
        ('no-recovery-false',lambda q:q['events'][0]['writeoff'].update(no_reasonable_recovery=False)),('portion-has-cash',lambda q:q['events'][0]['writeoff'].update(portion_expected_cash='1')),
        ('too-large-portion',lambda q:q['events'][0]['writeoff'].update(fraction='1/2')),('future-over-contract',lambda q:q['events'][2].update(expected={'2027-01-01':'121/2'})),
        ('wrong-cash',lambda q:q['events'][1].update(amount='45')),('early-close',lambda q:q['events'][1].update(close=True)),('unclosed-terminal',lambda q:q['events'][-1].update(close=False)),
        ('duplicate-id',lambda q:q['events'][1].update(id='july')),('mixed-context',lambda q:q['events'][0]['context'].update(currency='USD')),('wrong-calendar',lambda q:q['context'].update(calendar='ACT/ACT')),
        ('missed-cash',lambda q:q['events'][1].update(date='2026-01-02')),('low-scale',lambda q:q['numerical'].update(scale=3)),('future-horizon',lambda q:q['acquisition']['contract'].update({'2050-01-01':'1'})),
        ('too-tight-width',lambda q:q['numerical'].update(max_width='1/1000000000000000000000000000000')),('negative-cash',lambda q:q['events'][1].update(amount='-1'))]
    for n,f in mods:add(n,f)
    add('fee-omitted',lambda q:q['acquisition'].update(fee_received='0'),cases[4]['request'])
    add('delayed-writeoff-with-positive-cash',lambda q:q['events'][0]['findings'].update(no_writeoff_required_after_event=False))
    add('full-expected-cash',lambda q:q['events'][0]['writeoff'].update(fraction='1'))
    add('approximate-rate',lambda q:q['numerical'].update(initial_pv_tolerance='1/1000000'))
    def missing(_):raise FileNotFoundError(SOURCE)
    for name,reader,status in [('missing',missing,'unresolved'),('changed',lambda _:b'changed','rejected')]:
        r=calculate(base,reader);check('source/'+name,r['status']==status and r['closing'] is None)
    result=dict(attempt=attempt.name,recorded_utc=datetime.now(timezone.utc).isoformat(),checks=len(checks),failures=sum(not x['passed'] for x in checks),failed=[x for x in checks if not x['passed']],cases=len(cases),adverse_inputs=len(adverse),factor_certificates=len(certificates),root_cases=len(roots),source_challenges=2,
        git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),command='CUDA_VISIBLE_DEVICES=-1 python3 data/accounting-master/dated-credit-schedules-20261016/verify.py',environment=sys.executable+'; standard library; rational interval arithmetic',gpu_status='intentionally hidden' if os.environ.get('CUDA_VISIBLE_DEVICES')=='-1' else 'not hidden',random_seeds='N/A deterministic',data_version='authored-cases.json/input-lock.json',wall_seconds=round(time.monotonic()-started,3),plan='docs/plans/accounting-dated-credit-schedules-20261016.md',result=str((OUT/'result.md').relative_to(ROOT)),outputs=[str((attempt/f).relative_to(ROOT)) for f in ('checks.json','exchanges.json','adverse.json','factor-certificates.json','root-brackets.json')])
    for name,value in [('checks.json',dict(summary=result,checks=checks)),('exchanges.json',exchanges),('adverse.json',adverse),('factor-certificates.json',certificates),('root-brackets.json',roots),('run-manifest.json',result)]:
        (attempt/name).write_text(json.dumps(value,indent=2)+'\n')
    (OUT/'run-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('attempt','checks','failures','cases','adverse_inputs','factor_certificates','root_cases','wall_seconds','failed')}))
    if result['failures']:raise SystemExit(1)
if __name__=='__main__':main()
