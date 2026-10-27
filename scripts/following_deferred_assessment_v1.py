"""Fresh conditional deferred recognition after following-period current tax."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import following_tax_reassessment_v1 as prior
import shared_deferred_assessment_v1 as original
book=prior.book;core=prior.core;losses=prior.losses;require=prior.require
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/following-deferred-assessment-20261024'
LOCK='8604b8e3acf201e398b35b1056b5119ffd637c089c12dd5d839fed9221e3051f'
PROFILE='FollowingPeriodDeferredAssessment/1'
MODEL='fresh_single_pool_gross_profit_loss_v1'
FINDINGS=original.FINDINGS;SUPPORT=original.SUPPORT
FLAGS={**prior.FLAGS,'conditional_deferred_assessed':False}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'Other allocation,recovery,offset and credit models','Subsequent continuation and repeated carry',
    'Annual completeness']

def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)

def request(previous,identity,model,measurement,findings,capacity,items):
    return {'profile':PROFILE,'prior_request':deepcopy(previous),'prior_sha256':book.digest(previous),
        'id':identity,'model':deepcopy(model),'measurement':deepcopy(measurement),
        'findings':deepcopy(findings),'recovery_capacity':deepcopy(capacity),'items':deepcopy(items)}

def population(result):
    state=result['after'];classes=prior.first.classes(result['continuation_result']['assessment_result']['carry_result']);rows=[]
    def add(identity,kind,account,carrying,lease=None,right=None,lot=None):
        rows.append({'id':identity,'kind':kind,'account':account,'carrying':book.fmt(carrying),
                     'lease_id':lease,'right_id':right,'lot_id':lot})
    for kind in ['assets','liabilities']:
        for account in classes[kind]+(['income_tax_payable'] if kind=='liabilities' else []):
            if account in ['dta','dtl','inventory','rou','lease_liability']:continue
            amount=Q(state['balances'][account])*(1 if kind=='assets' else -1)
            require(amount>=0,'unsupported_contra_balance:'+account,'unsupported')
            add('account/'+account,'asset' if kind=='assets' else 'liability',account,amount)
    add('inventory/other','asset','inventory',Q(state['other_inventory']))
    for key,lot in sorted(state['lots'].items()):
        add('inventory/lot/'+prior.tax.info.pointer(key),'asset','inventory',Q(lot['carrying']),lot=key)
    for lease in sorted(state['leases'],key=lambda x:x['component']['lease_id']):
        c=lease['component'];lid=c['lease_id']
        for r in sorted(c['rights'],key=lambda x:x['right_id']):
            rid=r['right_id'];root='lease/'+prior.tax.info.pointer(lid)+'/'+prior.tax.info.pointer(rid)
            add(root+'/asset','asset','rou',Q(r['rou']),lid,rid)
            add(root+'/liability','liability','lease_liability',Q(r['liability']),lid,rid)
    for lot in sorted(result['loss_state']['lots'],key=lambda x:x['id']):
        add('loss/'+prior.tax.info.pointer(lot['id']),'loss',None,Q(lot['remaining']),lot=lot['id'])
    require(len({r['id'] for r in rows})==len(rows),'population_collision')
    return rows

def number(value,label):
    result=losses.declaration(value,'rational');require(result is not None,label+':unknown','unresolved')
    require(result>=0,label+':negative');return result

def measurement(body,result,pop):
    data=body['measurement']
    core.closed(data,['at','state_sha256','jurisdiction','regime','account_bases','lease_bases'],'measurement')
    core.scalar(data['at'],'date')
    require(data['at']==result['after']['date'],'measurement_date')
    require(data['state_sha256']==book.digest(result['after']),'measurement_state_digest')
    for key in ['jurisdiction','regime']:
        value=losses.declaration(data[key],'text')
        require(value is not None,'measurement_scope_unknown:'+key,'unresolved')
        require(value==result['loss_state'][key],'measurement_scope_changed:'+key)
    accounts=result['population']['basis_accounts']
    lease_keys=['lease/'+prior.tax.info.pointer(r['lease_id'])+'/'+prior.tax.info.pointer(r['right_id'])+'/'+r['kind']
                for r in pop if r['lease_id'] is not None]
    require(type(data['account_bases']) is dict and set(data['account_bases'])==set(accounts),'complete_measurement_accounts')
    require(type(data['lease_bases']) is dict and set(data['lease_bases'])==set(lease_keys),'complete_measurement_rights')
    return {'accounts':{k:number(v,'account_base:'+k) for k,v in data['account_bases'].items()},
            'leases':{k:number(v,'lease_base:'+k) for k,v in data['lease_bases'].items()}}

def calculate(body,result):
    pop=population(result);measured=measurement(body,result,pop);items=body['items'];require(type(items) is list,'item_list')
    mapped={}
    for item in items:
        core.closed(item,['id','tax_base','rate','recognized_deduction','recorded_dta','recorded_dtl','route','support'],'deferred_item')
        core.text(item['id'],'item_id');require(item['id'] not in mapped,'duplicate_item');mapped[item['id']]=item
    require(set(mapped)=={r['id'] for r in pop},'complete_item_population')
    core.closed(body['findings'],FINDINGS,'deferred_findings')
    for k in FINDINGS:losses.affirmative(body['findings'][k],k)
    capacity=number(body['recovery_capacity'],'recovery_capacity')
    observations=[];bases={k:Q(0) for k in measured['accounts']}
    used=Q(0);asset=Q(0);liability=Q(0);old_a=Q(0);old_l=Q(0)
    for row in pop:
        item=mapped[row['id']];core.closed(item['support'],SUPPORT,'item_support')
        for k in SUPPORT:losses.affirmative(item['support'][k],row['id']+':'+k)
        route=losses.declaration(item['route'],'text');require(route is not None,'route_unknown','unresolved')
        require(route=='profit_or_loss','allocation_route_not_implemented','unsupported')
        base=number(item['tax_base'],'tax_base');rate=number(item['rate'],'rate')
        recognized=number(item['recognized_deduction'],'recognized_deduction')
        recorded_a=number(item['recorded_dta'],'recorded_dta');recorded_l=number(item['recorded_dtl'],'recorded_dtl')
        require(recorded_a==0 or recorded_l==0,'opposite_recorded_balances_on_one_item')
        carrying=Q(row['carrying'])
        if row['kind']=='loss':
            require(base==0,'loss_has_no_separate_base');difference=-carrying
        else:
            difference=carrying-base if row['kind']=='asset' else base-carrying
            bases[row['account']]+=base
        if row['lease_id'] is not None:
            key='lease/'+prior.tax.info.pointer(row['lease_id'])+'/'+prior.tax.info.pointer(row['right_id'])+'/'+row['kind']
            require(base==measured['leases'][key],'lease_base_mismatch:'+row['id'])
        if row['account']=='inventory' and row['lot_id'] is not None:
            require(base==Q(result['after']['lots'][row['lot_id']]['tax_base']),'lot_base_mismatch')
        deductible=max(-difference,Q(0));taxable=max(difference,Q(0))
        require(recognized<=deductible,'recognized_exceeds_deduction')
        a=rate*recognized;l=rate*taxable
        used+=recognized;asset+=a;liability+=l;old_a+=recorded_a;old_l+=recorded_l
        observations.append({**row,'tax_base':book.fmt(base),'rate':book.fmt(rate),
            'taxable_difference':book.fmt(taxable),'deductible_difference':book.fmt(deductible),
            'recognized_deduction':book.fmt(recognized),'unrecognized_deduction':book.fmt(deductible-recognized),
            'desired_dta':book.fmt(a),'desired_dtl':book.fmt(l),
            'recorded_dta':book.fmt(recorded_a),'recorded_dtl':book.fmt(recorded_l)})
    for account,base in bases.items():
        require(base==measured['accounts'][account],'account_base_mismatch:'+account)
    require(used<=capacity,'recovery_capacity_reused')
    require(old_a==Q(result['after']['balances']['dta']) and old_l==-Q(result['after']['balances']['dtl']),'recorded_allocation_mismatch')
    return {'items':observations,'desired_dta':book.fmt(asset),'desired_dtl':book.fmt(liability),
        'recorded_dta':book.fmt(old_a),'recorded_dtl':book.fmt(old_l),'recovery_capacity':book.fmt(capacity),
        'recognized_deductions':book.fmt(used),'unused_capacity':book.fmt(capacity-used),
        'account_bases':{k:book.fmt(v) for k,v in bases.items()}}


def propose(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();prior.continuation.caller.bounded(body)
        core.closed(body,['profile','prior_request','prior_sha256','id','model','measurement',
            'findings','recovery_capacity','items'],'deferred_request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'assessment_id')
        require(body['prior_sha256']==book.digest(body['prior_request']),'prior_digest')
        core.closed(body['model'],['profile','selected'],'model')
        require(body['model']['profile']==MODEL,'model_not_implemented','unsupported')
        losses.affirmative(body['model']['selected'],'model_selection')
        previous=prior.propose(body['prior_request'])
        base.update(prior_result=previous,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(previous['status']=='proposed','prior:'+previous['status'],previous['status'])
        require(body['id'] not in previous['after']['seen'],'duplicate_assessment')
        calc=calculate(body,previous);after=deepcopy(previous['after']);b=after['balances']
        da=Q(calc['desired_dta'])-Q(calc['recorded_dta']);dl=Q(calc['desired_dtl'])-Q(calc['recorded_dtl'])
        journal={k:'0/1' for k in b};journal.update(dta=book.fmt(da),dtl=book.fmt(-dl),deferred_tax=book.fmt(dl-da))
        require(sum(Q(v) for v in journal.values())==0,'journal_unbalanced')
        after['balances']={k:book.fmt(Q(v)+Q(journal[k])) for k,v in b.items()}
        after['seen'].append(body['id'])
        prior.continuation.vintage_invariant(after,previous['tax_vintages'])
        require(all(after[k]==v for k,v in previous['after'].items() if k not in ['balances','seen']),'state_boundary')
        initial=previous['continuation_result']['assessment_result']
        report=prior.carry.statements(previous['opening'],after,prior.first.classes(initial['carry_result']))
        report.update(scope='Fresh conditional following-period deferred assessment',unresolved=deepcopy(UNRESOLVED))
        archived=initial['carry_result']['archive']
        return {**base,'status':'proposed','conditional_current_assessed':True,'conditional_deferred_assessed':True,
            'deferred_asset_recognized':Q(calc['desired_dta'])>0,'calculation':calc,
            'measurement':deepcopy(body['measurement']),'journal':journal,'after':after,
            'opening':deepcopy(previous['opening']),'loss_state':deepcopy(previous['loss_state']),
            'tax_vintages':deepcopy(previous['tax_vintages']),'assessed_until':previous['assessed_until'],
            'recorded_statements':report,'findings':deepcopy(body['findings']),
            'prior_findings':deepcopy(previous['findings']),'recovery_capacity':deepcopy(body['recovery_capacity']),
            'historical_recognition':{'calculation':deepcopy(archived['prior_deferred_calculation']),
                'findings':deepcopy(archived['prior_deferred_findings']),
                'capacity':deepcopy(archived['prior_recovery_capacity']),
                'interpretation':'Prior-period evidence only; fresh measurement and capacity are required'},
            'current_period_tax':'conditionally_assessed','current_period_deferred_tax':'conditionally_assessed',
            'unresolved':deepcopy(UNRESOLVED)}
    except (prior.carry.continuation.Refused,prior.carry.continuation.lease.Refused,losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,AssertionError,RecursionError,OverflowError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}


def apply(body,proposal):
    expected=propose(body)
    try:
        require(expected['status']=='proposed','no_deferred_proposal')
        require(prior.continuation.caller.canonical(proposal)==prior.continuation.caller.canonical(expected),'complete_proposal_mismatch')
        return {**deepcopy(expected),'status':'applied'}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}

