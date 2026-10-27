"""Independent rational derivation and journal replay of documentary cases."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
from collections import defaultdict
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
data=json.loads((OUT/'cases.json').read_text())
checks=[];results={}
def check(name,truth):checks.append({'check':name,'passed':bool(truth)})
def equal(name,a,b):check(name,F(a)==F(b))
def compact(d):return {k:str(v) for k,v in d.items()}
# Arithmetic comes from the predeclared physical/contractual inputs, not expected fields.
def target(key):
    if key=='restoration-cost-increase':
        pre=80+(50-20);imp=max(F(0),pre-F(90));dep=(pre-imp)/4
        return {'P1':(100,90,50,140,-imp,0),'P2':(100,90-dep,50,140-dep,-imp-dep,0)}
    if key=='restoration-cost-decrease':
        gain=max(0,80-30-30);return {'P1':(100,0,30,50+gain,gain,0)}
    if key=='restoration-revaluation-increase':
        loss=max(0,(85-50)-20);return {'P1':(100,150,85,200-20-loss,-loss,-20)}
    if key=='restoration-revaluation-decrease':
        release=80-30;excess=max(0,release-40);reverse=min(15,release-excess)
        profit=excess+reverse;oci=release-profit
        return {'P1':(100,25,30,45+profit+oci,profit,oci)}
    if key=='restoration-lifetime':
        d1=F(120)/2;i1=F(20)/10;estimate=33-(20+i1);d2=120-d1+estimate;i2=F(33)/10;paid=33+i2
        return {'P1':(100,d2,33,200-d1-i1,-d1-i1,0),
                'P2':(100-paid,0,0,100-paid,-d1-i1-d2-i2,0)}
    if key=='restoration-exhausted-life':return {'P1':(100,0,25,75,-5,0)}
    if key=='assurance-population':
        reserve=100*(F(3,4)*0+F(1,5)*10+F(1,20)*40);paid=100;remain=250;reimb=F(1,4)*remain
        profit=2000-600-reserve+reserve/4+(reserve-paid-remain)-(reserve-paid-remain)/4
        cash=1000+2000-paid+F(paid)/4;equity=1600+profit
        return {'P1':(cash,reimb,remain,equity,profit,0),'P2':(cash-remain+reimb,0,0,equity,profit,0)}
    if key=='mixed-contract-modification':
        construction=(100+40)*F(40,100);visits=3*5;revenue=construction+visits
        cost=40+3*2;profit=revenue-cost;cash=100+120+50-cost;liability=170-revenue
        return {'P1':(cash,0,liability,100+profit,profit,0),'P2':(100+170-100-6*2,0,0,158,58,0)}
    if key=='production-wip':
        material_rate=F(1000,100);equiv=80+20*F(1,2);variable_rate=450/equiv;fixed_rate=F(600,120)
        idle=600-equiv*fixed_rate;unit=material_rate+variable_rate+fixed_rate
        wip=20*material_rate+20*F(1,2)*(variable_rate+fixed_rate);finished=30*unit
        profit=50*30-50*unit-idle;cash=3000-1000-450-600+1500
        return {'P1':(cash,wip+finished,0,3000+profit,profit,0),'P2':(3850,0,0,3850,850,0)}
    if key=='joint-products':
        a=F(300)*240/(240+360);b=300-a;cost=a*F(30,60)+b*F(10,40);revenue=30*4+10*9
        return {'P1':(500-300+revenue,300-cost,0,500+revenue-cost,revenue-cost,0)}
    if key=='immaterial-byproduct':return {'P1':(500-300+20,300-20,0,500,0,0)}
    if key=='deferred-supplier':
        principal=F(121)/(F(11,10)**2);i1=principal/10;i2=(principal+i1)/10
        return {'P1':(250,0,principal+i1,100+150-principal-i1,150-principal-i1,0),
                'P2':(250-121,0,0,100+150-principal-i1-i2,150-principal-i1-i2,0)}
    raise ValueError(key)
asset_names={'cash','ppe','inventory','reimbursement','wip','finished','product_A','product_B','main_product','byproduct'}
liability_names={'provision','supplier','contract_liability'}
for c in data['cases']:
    key=c['id'];b=defaultdict(F,{a:F(v) for a,v in c['opening'].items()});opening_equity=sum(b[a] for a in asset_names)-sum(-b[a] for a in liability_names)
    equal(key+'/opening-balanced',sum(b.values()),0)
    t=target(key);ids=set();snap={}
    for event in c['events']:
        check(key+'/'+event['event']+'/unique',event['event'] not in ids);ids.add(event['event'])
        equal(key+'/'+event['event']+'/balanced',sum(F(v) for v in event['debit'].values()),sum(F(v) for v in event['credit'].values()))
        check(key+'/'+event['event']+'/positive',all(F(v)>0 for v in list(event['debit'].values())+list(event['credit'].values())))
        for a,v in event['debit'].items():b[a]+=F(v)
        for a,v in event['credit'].items():b[a]-=F(v)
        profit=-sum(v for a,v in b.items() if a.startswith(('income.','expense.')))
        oci=-sum(v for a,v in b.items() if a.startswith('oci.'))
        assets=sum(b[a] for a in asset_names if a!='cash');liabilities=-sum(b[a] for a in liability_names)
        snap[event['period']]=(b['cash'],assets,liabilities,opening_equity+profit+oci,profit,oci)
        equal(key+'/'+event['event']+'/equation',b['cash']+assets-liabilities,opening_equity+profit+oci)
    for period,got in snap.items():
        for n,a,v in zip(['cash','assets','liabilities','equity','profit','oci'],got,t[period]):equal(key+'/'+period+'/independent-'+n,a,v)
        ex=c['expected'][period]
        expected=[ex['cash'],sum(F(v) for v in ex['other_assets'].values()),sum(F(v) for v in ex['liabilities'].values()),ex['equity'],ex['cumulative_profit'],ex['cumulative_oci']]
        for n,a,v in zip(['cash','assets','liabilities','equity','profit','oci'],got,expected):equal(key+'/'+period+'/authored-'+n,a,v)
        check(key+'/'+period+'/not-after-tax',c['tax'].startswith('uncomputed'))
    for a,v in c['expected'][list(snap)[-1]]['other_assets'].items():equal(key+'/final-account/'+a,b[a],v)
    for a,v in c['expected'][list(snap)[-1]]['liabilities'].items():equal(key+'/final-account/'+a,-b[a],v)
    results[key]={p:compact(dict(zip(['cash','other_assets','liabilities','pretax_equity','cumulative_profit','cumulative_oci'],v))) for p,v in snap.items()}

# Explicit arithmetic counterexamples; these verify target discrimination, not runtime refusal.
negatives={
 'asset-negative-after-decrease':30-(80-30)!=0,
 'cost-increase-without-impairment':80+(50-20)!=90,
 'wrong-revalued-floor':max(0,50-25)+15!=25,
 'all-release-in-OCI':50!=25,
 'unwind-capitalized':F(2)+F(33,10)!=0,
 'warranty-zero':0!=100*(F(1,5)*10+F(1,20)*40),
 'warranty-original-reserve-after-payment':400-100!=250,
 'net-warranty-liability':250-F(125,2)!=250,
 'old-construction-progress':140*F(1,2)!=56,
 'no-mixed-catchup':50!=56,
 'all-promises-construction':170*F(2,5)!=56+5,
 'all-fixed-production-capitalized':600!=450,
 'all-WIP-fully-converted':20*(10+5+5)!=300,
 'joint-weight-by-mass':300*F(60,100)!=120,
 'supplier-inventory-at-invoice':121!=100,
 'supplier-straight-interest':F(21,2)!=10,
}
for n,v in negatives.items():check('adverse/'+n,v)

# Combine only the explicitly compatible EU year-one operation contributions.
selected=['production-wip','joint-products','immaterial-byproduct','deferred-supplier','restoration-lifetime']
combined={k:sum(F(results[s]['P1'][k]) for s in selected) for k in results[selected[0]]['P1']}
equal('combined/pretax-equation',combined['cash']+combined['other_assets'],combined['liabilities']+combined['pretax_equity'])
equal('combined/opening-equity-bridge',4300+combined['cumulative_profit'],combined['pretax_equity'])
equal('combined/cash-direct',4200+(1500-2050)+(210-300)+(20-300)+150,combined['cash'])
results['combined-EU-P1']={**compact(combined),'tax':'uncomputed','after_tax_equity':'unresolved','opening_equity':'4300','opening_cash':'4200','includes':selected}
for s in json.loads((OUT/'source-manifest.json').read_text())['files']:
    check('source/'+s['path'],hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest()==s['sha256'])
result={'passed':all(c['passed'] for c in checks),'checks':len(checks),'failures':[c for c in checks if not c['passed']],
        'classification':'independent author arithmetic; no product runtime or independent person review','details':checks}
(OUT/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n')
(OUT/'checked-statements.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps({k:result[k] for k in ['passed','checks','failures']}))
assert result['passed']
