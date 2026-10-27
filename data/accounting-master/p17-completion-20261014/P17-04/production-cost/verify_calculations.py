"""Independent closed-form and signed per-resource accounting reconstructions."""
from fractions import Fraction as F
from pathlib import Path
from copy import deepcopy
import hashlib,json,time
OUT=Path(__file__).resolve().parent;start=time.perf_counter()
fixture=json.loads((OUT/'fixture.json').read_text());I={k:F(v) for k,v in fixture['inputs'].items()}
checks=[];outputs={};journals={}
def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
def serial(x):
    if isinstance(x,F):return str(x)
    if isinstance(x,dict):return {k:serial(v) for k,v in x.items()}
    if isinstance(x,list):return [serial(v) for v in x]
    return x
fixed=I['fixed_cash']+I['depreciation'];abnormal=I['destroyed_kits']*I['materials_per_good'];other=I['administration']+I['selling']
for case in fixture['scenarios']:
    name=case['id'];q=F(case['good_units']);s=F(case['sold']);n=I['normal_capacity']
    rate=fixed/max(q,n);allocated=q*rate;unallocated=fixed-allocated
    unit=I['materials_per_good']+I['labor_per_good']+I['variable_per_good']+rate if q else None
    sold=s*unit if q else F(0);stock=(q-s)*unit if q else F(0)
    inventory_expense=sold+unallocated+abnormal;profit=s*I['price']-inventory_expense-other
    cash=I['cash']+s*I['price']-(q*(I['materials_per_good']+I['labor_per_good']+I['variable_per_good'])+abnormal+I['fixed_cash']+other)
    ppe=I['ppe']-I['depreciation'];net=cash+ppe+stock;dep_stock=(q-s)*I['depreciation']/max(q,n)
    row=dict(zip(fixture['columns'],[unit,allocated,unallocated,sold,stock,inventory_expense,profit,cash,ppe,net,cash-I['cash'],dep_stock]))
    for col,expected in zip(fixture['columns'],case['expected']):check(name+':expected:'+col,row[col]==(None if expected is None else F(expected)),str(row[col]))
    check(name+':cost-conservation',stock+sold+unallocated+abnormal+other==4*q+fixed+abnormal+other)
    check(name+':net-assets',net==I['cash']+I['ppe']+profit)
    check(name+':direct-indirect-cash',cash-I['cash']==profit+I['depreciation']-stock)
    check(name+':net-inventory-cash-equivalent',cash-I['cash']==profit+(I['depreciation']-dep_stock)-(stock-dep_stock))
    check(name+':fixed-cap',0<=allocated<=fixed)
    check(name+':nrv',unit is None or unit<=I['nrv'])
    check(name+':yield-population',q+I['destroyed_kits']==q+6)
    # Independent ledger allocates each incurred fixed component across units.
    ledger={'cash':I['cash'],'ppe_cost':I['ppe'],'opening_net_assets':-I['cash']-I['ppe']};events=[]
    def post(event,debits,credits):
        check(name+':journal:'+event,sum(debits.values())==sum(credits.values()))
        for a,v in debits.items():ledger[a]=ledger.get(a,F(0))+v
        for a,v in credits.items():ledger[a]=ledger.get(a,F(0))-v
        events.append({'id':name+':'+event,'debits':debits,'credits':credits})
    post('purchase-kits',{'raw_materials':(q+I['destroyed_kits'])*I['materials_per_good']},{'cash':(q+I['destroyed_kits'])*I['materials_per_good']})
    post('abnormal-loss',{'abnormal_expense':abnormal},{'raw_materials':abnormal})
    post('good-material-use',{'finished_goods':q*I['materials_per_good']},{'raw_materials':q*I['materials_per_good']})
    post('direct-labor',{'finished_goods':q*I['labor_per_good']},{'cash':q*I['labor_per_good']})
    post('variable-overhead',{'finished_goods':q*I['variable_per_good']},{'cash':q*I['variable_per_good']})
    post('fixed-cash',{'production_clearing':I['fixed_cash']},{'cash':I['fixed_cash']})
    post('factory-depreciation',{'production_clearing':I['depreciation']},{'accumulated_depreciation':I['depreciation']})
    allocated_components=[]
    for component in [I['fixed_cash'],I['depreciation']]:
        # Individual units receive normal-capacity share unless that exceeds actual component cost.
        parts=[min(component/n,component/q) for _ in range(int(q))] if q else []
        allocated_components.append(sum(parts,F(0)))
    allocated_independent=sum(allocated_components)
    post('clear-production-cost',{'finished_goods':allocated_independent,'unallocated_expense':fixed-allocated_independent},{'production_clearing':fixed})
    post('period-costs',{'admin_selling_expense':other},{'cash':other})
    batch_cost=ledger['finished_goods'];remove=sum((batch_cost/q for _ in range(int(s))),F(0)) if q else F(0)
    post('sale',{'cash':s*I['price']},{'revenue':s*I['price']})
    post('remove-stock',{'sold_stock_expense':remove},{'finished_goods':remove})
    ledger_profit=-sum(v for a,v in ledger.items() if a.endswith('_expense') or a=='revenue')
    check(name+':ledger-balanced',sum(ledger.values())==0)
    for account,want in [('cash',cash),('finished_goods',stock),('raw_materials',F(0)),('production_clearing',F(0)),('accumulated_depreciation',-I['depreciation'])]:check(name+':ledger:'+account,ledger[account]==want)
    check(name+':ledger-profit',ledger_profit==profit)
    check(name+':ledger-independent-fixed',allocated_independent==allocated)
    check(name+':ledger-independent-depreciation-stock',(allocated_components[1]*(q-s)/q if q else F(0))==dep_stock)
    outputs[name]=row;journals[name]={'ledger':ledger,'events':events}

# Wrong targets can preserve a balanced trial balance.
low=outputs['low'];high=outputs['high'];wrong={}
bad_unit=F(4)+fixed/60;bad_stock=20*bad_unit;bad_profit=400-40*bad_unit-abnormal-other
check('low-actual-denominator-stock-overstated',bad_stock-low['inventory']==24)
check('low-actual-denominator-profit-overstated',bad_profit-low['profit']==24)
check('low-wrong-book-still-balances',low['cash']+low['ppe']+bad_stock==1600+bad_profit)
wrong['low_actual_denominator']={'stock':bad_stock,'profit':bad_profit,'cash':low['cash']}
bad_high_allocation=150*fixed/100;variance_credit=bad_high_allocation-fixed
bad_high_stock=30*F('29/5');bad_high_profit=1200-120*F('29/5')-abnormal-other+variance_credit
check('high-normal-rate-creates-unincurred-cost',bad_high_allocation==270 and variance_credit==90)
check('high-with-variance-credit-still-balances',high['cash']+high['ppe']+bad_high_stock==1600+bad_high_profit)
check('high-net-stock-profit-overstatement',bad_high_stock-high['inventory']==18 and bad_high_profit-high['profit']==18)
wrong['high_uncapped_with_variance_credit']={'allocated':bad_high_allocation,'invented_credit':variance_credit,'stock':bad_high_stock,'profit':bad_high_profit}
excluded_unit=F('29/5')+(abnormal+other)/60;excluded_stock=20*excluded_unit;excluded_profit=400-40*excluded_unit-72
check('excluded-costs-deferred',excluded_stock-low['inventory']==10 and excluded_profit-low['profit']==10)
check('excluded-costs-still-balance',low['cash']+540+excluded_stock==1600+excluded_profit)
check('partial-depreciation-addback-wrong',low['profit']+48-low['inventory']!=low['cash_change'])
check('sellthrough-constant-production-cash',outputs['low_sellthrough']['cash']-low['cash']==200)
check('sellthrough-profit-and-stock',outputs['low_sellthrough']['profit']-low['profit']==84 and low['inventory']==116)
check('same-unit-cost-different-utilization-profit',low['unit_cost']==outputs['normal']['unit_cost'] and low['unallocated_fixed']!=outputs['normal']['unallocated_fixed'])

def admit(a,q,s,resource_ids):
    if not a.get('capacity_id'):return 'CAPACITY_UNRESOLVED'
    if not a.get('cost_population_complete'):return 'COST_POPULATION_UNRESOLVED'
    if not a.get('homogeneous_good_units') or not a.get('no_wip'):return 'DIFFERENT_COST_MODEL_REQUIRED'
    if q<0 or s<0 or s>q:return 'INVALID_QUANTITY'
    if len(resource_ids)!=len(set(resource_ids)):return 'DUPLICATE_COST_RESOURCE'
    if not a.get('sale_admitted') and s:return 'REVENUE_UNRESOLVED'
    if not a.get('nrv_admitted'):return 'MEASUREMENT_UNRESOLVED'
    if a.get('after_tax_requested') and a['tax']=='UNCOMPUTED_PRETAX_ONLY':return 'TAX_UNSUPPORTED'
    return 'PRETAX_CASE_ADMITTED'
base=fixture['admission']
adverse=[('valid',{},60,40,['a','b'],'PRETAX_CASE_ADMITTED'),('capacity',{'capacity_id':None},60,40,['a'],'CAPACITY_UNRESOLVED'),('costs',{'cost_population_complete':False},60,40,['a'],'COST_POPULATION_UNRESOLVED'),('wip',{'no_wip':False},60,40,['a'],'DIFFERENT_COST_MODEL_REQUIRED'),('joint',{'homogeneous_good_units':False},60,40,['a'],'DIFFERENT_COST_MODEL_REQUIRED'),('oversell',{},60,61,['a'],'INVALID_QUANTITY'),('negative',{},-1,0,['a'],'INVALID_QUANTITY'),('duplicate',{},60,40,['a','a'],'DUPLICATE_COST_RESOURCE'),('sale',{'sale_admitted':False},60,40,['a'],'REVENUE_UNRESOLVED'),('nrv',{'nrv_admitted':False},60,40,['a'],'MEASUREMENT_UNRESOLVED'),('tax',{'after_tax_requested':True},60,40,['a'],'TAX_UNSUPPORTED')]
for name,patch,q,s,ids,want in adverse:check('admission:'+name,admit(base|patch,q,s,ids)==want)
result={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'wall_seconds':time.perf_counter()-start,'fixture_sha256':hashlib.sha256((OUT/'fixture.json').read_bytes()).hexdigest()}
(OUT/'calculation-checks.json').write_text(json.dumps(result,indent=2)+chr(10))
(OUT/'computed.json').write_text(json.dumps(serial({'scenarios':outputs,'journals':journals,'wrong_targets':wrong}),indent=2)+chr(10))
print(json.dumps({'passed':result['passed'],'check_count':len(checks),'failed':[c['name'] for c in checks if not c['passed']]}))
if not result['passed']:raise SystemExit(1)
