from copy import deepcopy
from pathlib import Path
import importlib.util
import sys

ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import native_company_sale_v1 as adapter
spec=importlib.util.spec_from_file_location('native_sale_prior_cases',ROOT/'data/accounting-master/typed-monetary-effects-20261024/examples.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)


def start():
    _,state,event=next(x for x in prior.selected_cases() if x[2]['kind']=='sell')
    return state,event


def two_lots():
    state,event=start();selected=state['lots'][event['lot_id']]
    selected.update(carrying='15/1',tax_base='15/1')
    second=deepcopy(selected);second.update(id='unsold',units='1/2',carrying='5/1',tax_base='5/1')
    state['lots']['unsold']=second
    return state,event


def cases():
    rows=[]
    for name,state,event in prior.selected_cases():
        if event['kind']=='sell':rows.append((name,state,event))
    state,event=two_lots();rows.append(('two_lots',state,event))
    state,event=two_lots();event['lot_id']='unsold';rows.append(('sell_other_lot',state,event))
    for name,value in [('unknown_performance','unknown'),('false_performance',False)]:
        state,event=start();event['performance_complete']=value;rows.append((name,state,event))
    for name,field,value in [('fractional','fraction','1/2'),('unknown_proceeds','proceeds','unknown'),
                             ('negative_proceeds','proceeds','-1/1'),('wrong_method','method','wrong'),
                             ('missing_lot','lot_id','absent'),('before_state','date','2025-07-01'),
                             ('period_endpoint','date','2026-01-01'),('duplicate','id','return_settlement')]:
        state,event=start();event[field]=value;rows.append((name,state,event))
    for name in ['negative_cash','wrong_inventory','wrong_refund','wrong_tax_base','negative_units','disposed_stock','wrong_lot_identity']:
        state,event=start();lot=state['lots'][event['lot_id']]
        if name=='negative_cash':state['balances']['original_equity']=adapter.native.fmt(adapter.native.q(state['balances']['original_equity'])+455);state['balances']['cash']='-1/1'
        elif name=='wrong_inventory':state['other_inventory']='1/1'
        elif name=='wrong_refund':state['component']['refund']='1/1'
        elif name=='wrong_tax_base':lot['tax_base']='19/1'
        elif name=='negative_units':lot['units']='-1/1'
        elif name=='disposed_stock':lot['disposed']=True
        else:lot['id']='mismatch'
        rows.append((name,state,event))
    state,event=start();state['date']='2025-06-01';state['flows']=[];event['date']='2025-06-15'
    rows.append(('before_tax_close',state,event))
    return rows


def compare():
    from fractions import Fraction as Q
    rows=[]
    for name,state,event in cases():
        original=deepcopy((state,event));body=adapter.request(state,event);observed=adapter.propose(state,body)
        try:
            after,journal,flows=adapter.native.transition(state,event)
            expected={'status':'proposed','after':after,'journal':journal,'flows':flows}
            checks={'status':observed['status']=='proposed','entire_native_state':observed.get('after')==after,
                    'entire_journal':observed.get('journal')==journal,'entire_flows':observed.get('flows')==flows,
                    'cash_arithmetic':Q(observed.get('after',state)['balances']['cash'])==Q(state['balances']['cash'])+Q(event['proceeds']),
                    'inventory_arithmetic':Q(observed.get('after',state)['balances']['inventory'])==Q(state['balances']['inventory'])-Q(state['lots'][event['lot_id']]['carrying']),
                    'unselected_lots':all(observed.get('after',state)['lots'][k]==v for k,v in state['lots'].items() if k!=event['lot_id']),
                    'provisional_apply':adapter.apply(state,body,observed)['status']=='applied_provisional'}
        except adapter.native.Rejected as exc:
            expected={'status':exc.status,'reason':exc.reason}
            checks={'status':observed['status']==exc.status,'no_applied_state':'after' not in observed,
                    'reason':observed.get('reason')==exc.reason}
        checks['immutable_inputs']=(state,event)==original
        checks['flags_false']=all(observed[k] is False for k in adapter.FLAGS)
        rows.append({'case':name,'state':state,'event':event,'expected':expected,'observed':observed,'checks':checks})
    return {'cases':rows,'checks':[{'name':r['case']+':'+k,'passed':bool(v)} for r in rows for k,v in r['checks'].items()]}


if __name__=='__main__':
    import json
    r=compare();bad=[c['name'] for c in r['checks'] if not c['passed']]
    print(json.dumps({'cases':len(r['cases']),'checks':len(r['checks']),'failures':bad}))
    if bad:
        print(json.dumps([{k:r[k] for k in ['case','observed']} for r in r['cases'] if not all(r['checks'].values())])[:1800])
    raise SystemExit(bool(bad))
