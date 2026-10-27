"""Conditional gross deferred assessment; no legal or annual admission."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import shared_tax_reassessment_v1 as prior
book=prior.book;core=prior.core;losses=prior.losses;require=prior.require
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/shared-deferred-assessment-20261024'
LOCK='840c97b0ab432a5331e7dba31b9cacd57291d39f303ffaf678c765a55c33f33b'
PROFILE='ConditionalSharedDeferredAssessment/1'
MODEL='single_pool_gross_profit_loss_v1'
FINDINGS=['complete_scoped_population','no_unrepresented_tax_only_items_or_credits',
          'recorded_allocation_supported','single_recovery_pool_supported']
SUPPORT=['measurement_supported','recognition_supported','movement_allocation_supported']
FLAGS={**prior.FLAGS,'conditional_deferred_assessed':False,'annual_close_ready':False}

def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)

def request(previous,identity,model,findings,capacity,items):
    return {'profile':PROFILE,'prior_request':deepcopy(previous),'prior_sha256':book.digest(previous),
        'id':identity,'model':deepcopy(model),'findings':deepcopy(findings),
        'recovery_capacity':deepcopy(capacity),'items':deepcopy(items)}

def population(result):
    state=result['after'];classes=result['continuation_result']['native_report']['account_classes'];rows=[]
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
        add('inventory/lot/'+prior.info.pointer(key),'asset','inventory',Q(lot['carrying']),lot=key)
    for lease in sorted(state['leases'],key=lambda x:x['component']['lease_id']):
        c=lease['component'];lid=c['lease_id']
        for r in sorted(c['rights'],key=lambda x:x['right_id']):
            rid=r['right_id'];root='lease/'+prior.info.pointer(lid)+'/'+prior.info.pointer(rid)
            add(root+'/asset','asset','rou',Q(r['rou']),lid,rid)
            add(root+'/liability','liability','lease_liability',Q(r['liability']),lid,rid)
    for lot in sorted(result['loss_state']['lots'],key=lambda x:x['id']):
        add('loss/'+prior.info.pointer(lot['id']),'loss',None,Q(lot['remaining']),lot=lot['id'])
    require(len({r['id'] for r in rows})==len(rows),'population_collision')
    return rows

def number(value,label):
    result=losses.declaration(value,'rational');require(result is not None,label+':unknown','unresolved')
    require(result>=0,label+':negative');return result

def calculate(body,result):
    pop=population(result);items=body['items'];require(type(items) is list,'item_list')
    mapped={}
    for item in items:
        core.closed(item,['id','tax_base','rate','recognized_deduction','recorded_dta','recorded_dtl','route','support'],'deferred_item')
        core.text(item['id'],'item_id');require(item['id'] not in mapped,'duplicate_item');mapped[item['id']]=item
    require(set(mapped)=={r['id'] for r in pop},'complete_item_population')
    core.closed(body['findings'],FINDINGS,'deferred_findings')
    for k in FINDINGS:losses.affirmative(body['findings'][k],k)
    capacity=number(body['recovery_capacity'],'recovery_capacity')
    observations=[];bases={k:Q(0) for k in prior.population(result['continuation_result'])['basis_accounts']}
    used=Q(0);asset=Q(0);liability=Q(0);old_a=Q(0);old_l=Q(0)
    declarations=body['prior_request']['information']
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
            key='lease/'+prior.info.pointer(row['lease_id'])+'/'+prior.info.pointer(row['right_id'])+'/closing_'+row['kind']+'_tax_base'
            require(base==losses.declaration(declarations[key],'rational'),'lease_base_mismatch:'+row['id'])
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
        require(base==losses.declaration(declarations['basis/'+account+'/closing'],'rational'),'account_base_mismatch:'+account)
    require(used<=capacity,'recovery_capacity_reused')
    require(old_a==Q(result['after']['balances']['dta']) and old_l==-Q(result['after']['balances']['dtl']),'recorded_allocation_mismatch')
    return {'items':observations,'desired_dta':book.fmt(asset),'desired_dtl':book.fmt(liability),
        'recorded_dta':book.fmt(old_a),'recorded_dtl':book.fmt(old_l),'recovery_capacity':book.fmt(capacity),
        'recognized_deductions':book.fmt(used),'unused_capacity':book.fmt(capacity-used),
        'account_bases':{k:book.fmt(v) for k,v in bases.items()}}

def propose(body):
    result={'profile':PROFILE,**FLAGS}
    try:
        protected();prior.continuation.caller.bounded(body)
        core.closed(body,['profile','prior_request','prior_sha256','id','model','findings','recovery_capacity','items'],'deferred_request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'assessment_id')
        require(body['prior_sha256']==book.digest(body['prior_request']),'prior_digest')
        core.closed(body['model'],['profile','selected'],'model')
        require(body['model']['profile']==MODEL,'model_not_implemented','unsupported')
        losses.affirmative(body['model']['selected'],'model_selection')
        previous=prior.propose(body['prior_request'])
        result.update(prior_result=previous,request_sha256=book.digest(body),
            source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(previous['status']=='proposed','prior:'+previous['status'],previous['status'])
        require(body['id'] not in previous['after']['seen'],'duplicate_assessment')
        calc=calculate(body,previous);after=deepcopy(previous['after']);b=after['balances']
        da=Q(calc['desired_dta'])-Q(calc['recorded_dta']);dl=Q(calc['desired_dtl'])-Q(calc['recorded_dtl'])
        journal={k:'0/1' for k in b};journal.update(dta=book.fmt(da),dtl=book.fmt(-dl),deferred_tax=book.fmt(dl-da))
        require(sum(Q(v) for v in journal.values())==0,'journal_unbalanced')
        after['balances']={k:book.fmt(Q(v)+Q(journal[k])) for k,v in b.items()};after['seen'].append(body['id'])
        prior.continuation.invariant(after)
        require(all(after[k]==v for k,v in previous['after'].items() if k not in ['balances','seen']),'state_boundary')
        report=prior.continuation.statements(after,previous['continuation_result']['native_report'])
        report['scope']='Conditional gross deferred-tax assessment on recorded shared book'
        report['unresolved']=['Source and accounting admission','Complete fiscal event coverage',
            'Other allocation, recovery and offset models','New-period assessment and integration with repeated carry','Annual completeness']
        return {**result,'status':'proposed','conditional_deferred_assessed':True,
            'deferred_asset_recognized':Q(calc['desired_dta'])>0,'calculation':calc,
            'journal':journal,'after':after,'loss_state':deepcopy(previous['loss_state']),
            'assessed_until':previous['assessed_until'],'recorded_statements':report,
            'findings':deepcopy(body['findings']),'recovery_capacity':deepcopy(body['recovery_capacity'])}
    except (prior.continuation.Refused,prior.continuation.lease.Refused,losses.Refused) as exc:
        return {**result,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,RecursionError,OverflowError,AssertionError) as exc:
        return {**result,'status':'invalid','reason':str(exc)[:350]}

def apply(body,proposal):
    expected=propose(body)
    try:
        require(expected['status']=='proposed','no_deferred_proposal')
        require(prior.continuation.caller.canonical(proposal)==prior.continuation.caller.canonical(expected),'complete_proposal_mismatch')
        return {'profile':PROFILE,**FLAGS,'status':'applied','conditional_deferred_assessed':True,
            'deferred_asset_recognized':expected['deferred_asset_recognized'],
            'after':deepcopy(expected['after']),'loss_state':deepcopy(expected['loss_state']),
            'prior_result':deepcopy(expected['prior_result']),'calculation':deepcopy(expected['calculation']),
            'findings':deepcopy(expected['findings']),'unresolved':deepcopy(expected['recorded_statements']['unresolved']),
            'request_sha256':expected['request_sha256']}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
