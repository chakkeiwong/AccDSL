"""Finite common period book; selected tax operations, no annual-readiness claim."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import period_vintage_continuation_v1 as root
import following_deferred_assessment_v1 as deferred

book=root.book;core=root.core;losses=root.losses;require=root.require
native=root.continuation;caller=root.caller;tax=root.boundary.prior.first.tax
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/reusable-annual-interface-20261025'
LOCK='62a5483e4d7243292aac605461e1558e07cc9e6edfb692951f1fcf1936f65272'
PROFILE='AnnualProgram/1';STATE='PeriodBook/1'
CURRENT_MODEL='cumulative_period_vintage_no_credits_v1'
FLAGS={**root.FLAGS,'annual_ready':False,'general_annual_execution':False}
UNRESOLVED=['Actual source and accounting admission','Complete fiscal event coverage',
    'General recurrence evidence and independent domain review','Whole-company and sector coverage']

def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)
    tax.protected();losses.protected()

def request(origin,operations):
    return {'profile':PROFILE,'root_request':deepcopy(origin),
        'root_sha256':book.digest(origin),'operations':deepcopy(operations)}

def seed(result):
    require(result['current_period_tax']==result['current_period_deferred_tax']=='unassessed','root_not_unassessed','unsupported')
    rows=[]
    for old in result['period_vintages']:
        rows.append({'id':old['id'],'origin':{'kind':'imported','sha256':old['prior_vintage_sha256']},
            'period':deepcopy(old['period']),'opening_payable':old['opening_payable'],'new_assessment':'0/1',
            'settlements':deepcopy(old['settlements']),'closing_payable':old['closing_payable']})
    loss_ids=set();stack=[result]
    while stack:
        value=stack.pop()
        if type(value) is dict:
            if value.get('profile')=='ConditionalTaxLossLedger/1':loss_ids.update(lot['id'] for lot in value['lots'])
            stack.extend(value.values())
        elif type(value) is list:stack.extend(value)
    return {'profile':STATE,'opening':deepcopy(result['opening']),'after':deepcopy(result['after']),
        'account_classes':deepcopy(root.boundary.classes(result['boundary_result']['prior_result'])),
        'opening_loss':deepcopy(result['loss_state']),'loss_state':deepcopy(result['loss_state']),
        'known_loss_ids':sorted(loss_ids),
        'historical_vintages':deepcopy(result['tax_vintages']),'opening_vintages':deepcopy(rows),
        'period_vintages':rows,'current_assessments':[],'deferred_assessments':[],
        'period_archive':[],'recognition_archive':deepcopy(result['archive']),
        'findings':deepcopy(result['findings']),'finding_status':deepcopy(result['finding_status']),
        'prior_findings':deepcopy(result['prior_findings']),
        'unassessed_native_events':deepcopy(result['unassessed_native_events']),
        'period_rights':sorted([list(pair) for pair in {(x['component']['lease_id'],r['right_id'])
            for financial in [result['opening'],result['after']]+[t['result']['after'] for t in result['trace']]
            for x in financial['leases'] for r in x['component']['rights']}]),
        'current_period_tax':'unassessed','current_period_deferred_tax':'unassessed'}

def invariant(state):
    require(state['profile']==STATE,'state_profile')
    financial=state['after'];native.invariant(financial);losses.validate_state(state['loss_state'])
    require(state['opening']['period']==financial['period'],'opening_period')
    require(state['opening_loss']['cursor']==financial['period']['start'],'loss_opening_cursor')
    require(len(set(state['known_loss_ids']))==len(state['known_loss_ids']),'duplicate_loss_identity')
    require({v['id'] for v in state['loss_state']['lots']}<=set(state['known_loss_ids']),'missing_loss_identity')
    rows=state['period_vintages'];ids=[v['id'] for v in rows]
    require(len(set(ids))==len(ids),'duplicate_vintage')
    openings={v['id']:v for v in state['opening_vintages']}
    history={v['id']:v for v in state['historical_vintages']}
    current=state['current_assessments'][-1] if state['current_assessments'] else None
    expected_ids=list(openings)+([current['vintage_id']] if current else [])
    require(ids==expected_ids,'vintage_population_or_order')
    paid_by_event={};metadata={}
    for v in rows:
        core.closed(v,['id','origin','period','opening_payable','new_assessment','settlements','closing_payable'],'period_vintage')
        require(v['period']==financial['period'],'vintage_period')
        opening,new,closing=[losses.tax.numeric(v[k]) for k in ['opening_payable','new_assessment','closing_payable']]
        require(min(opening,new,closing)>=0,'negative_vintage_balance')
        if v['id'] in openings:
            original=openings[v['id']]
            require(v['origin']==original['origin'] and v['opening_payable']==original['opening_payable'] and new==0,'carried_vintage_changed')
            if v['origin']['kind']=='imported':require(v['origin']['sha256']==book.digest(history[v['id']]),'historical_vintage_digest')
            else:
                require(v['origin']['kind']=='archive','vintage_origin')
                archive=state['period_archive'][v['origin']['index']]
                prior=next(a for a in archive['period_vintages'] if a['id']==v['id'])
                require(v['origin']['sha256']==book.digest(prior) and v['opening_payable']==prior['closing_payable'],'archived_vintage_digest')
        else:
            require(current is not None and v['id']==current['vintage_id'] and opening==0,'current_vintage_identity')
            first=state['current_assessments'][0]
            require(v['origin']=={'kind':'assessment','id':first['id'],'sha256':first['operation_sha256']},'assessment_origin')
            require(new==Q(current['tax_amount']),'current_assessment_amount')
        seen=set();last=None;paid=Q(0)
        for s in v['settlements']:
            core.closed(s,['event_id','date','amount','payment_amount','operation_sha256','financial_result_sha256'],'settlement')
            key=s['event_id'];day=core.scalar(s['date'],'date');amount=losses.tax.numeric(s['amount']);total=losses.tax.numeric(s['payment_amount'])
            require(key not in seen and key in financial['seen'],'settlement_identity')
            require(core.scalar(financial['period']['start'],'date')<=day<=core.scalar(financial['date'],'date'),'settlement_date')
            require(last is None or last<=day,'settlement_chronology')
            require(amount>0 and total>=amount,'positive_settlement')
            meta=(s['date'],total,s['operation_sha256'],s['financial_result_sha256'])
            require(all(type(h) is str and len(h)==64 and all(c in '0123456789abcdef' for c in h) for h in meta[2:]),'settlement_digest')
            require(key not in metadata or metadata[key]==meta,'settlement_metadata')
            metadata[key]=meta;paid_by_event[key]=paid_by_event.get(key,Q(0))+amount
            seen.add(key);last=day;paid+=amount
        require(opening+new-paid==closing,'vintage_conservation')
    require(sum(Q(v['closing_payable']) for v in rows)==-Q(financial['balances']['income_tax_payable']),'aggregate_payable')
    flows=[f for f in financial['flows'] if f['origin']=='explicit_conditional_current_tax_payment']
    require(len(flows)==len({f['event_id'] for f in flows}) and {f['event_id'] for f in flows}==set(paid_by_event),'tax_flow_population')
    for f in flows:
        key=f['event_id'];day,total,_,_=metadata[key]
        require(f['activity']=='operating' and f['date']==day and -Q(f['amount'])==paid_by_event[key]==total,'tax_flow_amount')
    expense=Q(financial['balances']['current_tax'])
    require(expense==(Q(current['tax_amount']) if current else 0),'current_expense_identity')
    require(state['loss_state']['cursor']==(current['interval']['end_exclusive'] if current else state['opening_loss']['cursor']),'loss_assessment_cursor')
    return state

def population(state):
    classes=state['account_classes'];rights={tuple(pair) for pair in state['period_rights']}
    for financial in [state['opening'],state['after']]:
        rights.update((x['component']['lease_id'],r['right_id']) for x in financial['leases'] for r in x['component']['rights'])
    for a in state['current_assessments']:
        rights.update((r['lease_id'],r['right_id']) for r in a['population']['lease_rights'])
    return {'pretax_accounts':[k for k in classes['income'] if k not in ['current_tax','deferred_tax']],
        'basis_accounts':[k for k in classes['assets']+classes['liabilities'] if k not in ['dta','dtl']]+['income_tax_payable'],
        'lease_rights':[{'lease_id':a,'right_id':b} for a,b in sorted(rights)]}

def assessment(state,operation):
    e=operation['event']
    core.closed(e,['id','mode','model','interval','information','allocations','loss_policy'],'current_assessment')
    core.text(e['id'],'assessment_id');require(e['id'] not in state['after']['seen'],'duplicate_assessment')
    core.closed(e['model'],['profile','selected'],'model');require(e['model']['profile']==CURRENT_MODEL,'model_not_implemented','unsupported')
    losses.affirmative(e['model']['selected'],'model_selection')
    mode=e['mode'];require(mode in ['first','replace'],'assessment_mode')
    existing=state['current_assessments']
    require(bool(existing)==(mode=='replace'),'assessment_mode_mismatch')
    interval=e['interval'];core.closed(interval,['start','end_exclusive','activity_through'],'interval')
    start,end,through=[core.scalar(interval[k],'date') for k in ['start','end_exclusive','activity_through']]
    financial=state['after'];previous_end=existing[-1]['interval']['end_exclusive'] if existing else financial['period']['start']
    require(interval['start']==financial['period']['start']==state['opening_loss']['cursor'],'cumulative_start')
    require(start<end and core.scalar(previous_end,'date')<=end<=core.scalar(financial['period']['end_exclusive'],'date'),'assessment_endpoint')
    require(through==end-timedelta(days=1) and core.scalar(financial['date'],'date')<=through,'activity_after_assessment')
    pop=population(state);values=tax.assess(e['information'],pop)
    for k in ['jurisdiction','regime']:require(values[k]==state['opening_loss'][k],'loss_scope_changed:'+k)
    require(state['opening_loss']['context']==financial['context'],'loss_context_changed')
    calc=tax.reconcile(financial,interval,values,pop,e['allocations'])
    generation=e['loss_policy']['generation']
    if generation is not None:
        require(generation['id'] not in state['known_loss_ids'],'reused_historical_loss_id')
    loss_result=tax.replacement_losses(state['opening_loss'],interval,calc,e['loss_policy'],e['id'],
        book.digest({'operation_sha256':book.digest(operation),'calculation':calc}),state['loss_state'])
    amount=Q(loss_result['conditional_gross_current_tax']);old=Q(financial['balances']['current_tax']);delta=amount-old
    result=deepcopy(state);rows=result['period_vintages']
    if mode=='first':
        require(old==0,'new_period_tax_already_recorded')
        key='assessment:'+e['id'];require(key not in {v['id'] for v in rows},'duplicate_vintage')
        rows.append({'id':key,'origin':{'kind':'assessment','id':e['id'],'sha256':book.digest(operation)},
            'period':deepcopy(financial['period']),'opening_payable':'0/1','new_assessment':book.fmt(amount),
            'settlements':[],'closing_payable':book.fmt(amount)})
    else:
        key=existing[-1]['vintage_id'];row=next(v for v in rows if v['id']==key)
        paid=sum(Q(s['amount']) for s in row['settlements']);remaining=amount-paid
        require(remaining>=0,'tax_receivable_or_refund_required','unsupported')
        row['new_assessment']=book.fmt(amount);row['closing_payable']=book.fmt(remaining)
    journal={k:'0/1' for k in financial['balances']}
    journal.update(current_tax=book.fmt(delta),income_tax_payable=book.fmt(-delta))
    after=result['after'];after['balances']={k:book.fmt(Q(v)+Q(journal[k])) for k,v in financial['balances'].items()}
    after['date']=interval['activity_through'];after['seen'].append(e['id'])
    result['loss_state']=deepcopy(loss_result['after']);result['unassessed_native_events']=[]
    result['known_loss_ids']=sorted(set(result['known_loss_ids'])|{v['id'] for v in loss_result['after']['lots']})
    result['current_assessments'].append({'id':e['id'],'vintage_id':key,'mode':mode,
        'operation_sha256':book.digest(operation),'interval':deepcopy(interval),'population':pop,
        'calculation':calc,'loss_result':loss_result,'tax_amount':book.fmt(amount)})
    result['current_period_tax']='conditionally_assessed'
    result['current_period_deferred_tax']='stale' if result['deferred_assessments'] else 'unassessed'
    return result,journal,[],{'kernel':'explicit_cumulative_period_tax','population':pop,'calculation':calc,'loss_result':loss_result}

def event_transition(state,operation):
    kind=operation['kind'];financial=state['after'];rows=deepcopy(state['period_vintages'])
    endpoint=state['current_assessments'][-1]['interval']['end_exclusive'] if state['current_assessments'] else financial['period']['start']
    if kind=='native':
        proposed=native.transition(financial,operation,endpoint)
    else:
        require(kind=='allocated_tax_payment','unsupported_operation','unsupported')
        e=operation['event'];core.closed(e,['id','date','amount','authorization','allocations'],'payment')
        require(type(e['allocations']) is list and bool(e['allocations']),'nonempty_allocations')
        by_id={v['id']:v for v in rows};seen=set();total=losses.tax.numeric(e['amount']);allocated=Q(0)
        require(total>0,'positive_payment')
        for a in e['allocations']:
            core.closed(a,['vintage_id','amount'],'allocation');key=a['vintage_id'];core.text(key,'vintage_id')
            require(key in by_id,'unknown_vintage');require(key not in seen,'duplicate_allocation');seen.add(key)
            n=losses.tax.numeric(a['amount']);require(n>0,'positive_allocation')
            require(n<=Q(by_id[key]['closing_payable']),'allocation_exceeds_vintage');allocated+=n
        require(allocated==total,'allocation_sum_mismatch')
        kernel={'kind':'tax_payment','event':{k:deepcopy(v) for k,v in e.items() if k!='allocations'}}
        proposed=native.transition(financial,kernel,endpoint);h=book.digest(proposed)
        for a in e['allocations']:
            v=by_id[a['vintage_id']];v['closing_payable']=book.fmt(Q(v['closing_payable'])-Q(a['amount']))
            v['settlements'].append({'event_id':e['id'],'date':e['date'],'amount':a['amount'],
                'payment_amount':book.fmt(total),'operation_sha256':book.digest(operation),'financial_result_sha256':h})
        proposed['details']={'kernel':'explicit_period_vintage_payment','financial_result_sha256':h}
    result=deepcopy(state);result['after']=proposed['after'];result['period_vintages']=rows
    rights={tuple(pair) for pair in result['period_rights']}
    rights.update((x['component']['lease_id'],r['right_id']) for x in proposed['after']['leases'] for r in x['component']['rights'])
    result['period_rights']=[list(pair) for pair in sorted(rights)]
    if kind=='native':
        result['unassessed_native_events'].append(operation['event']['event']['id'])
        if result['current_assessments']:result['current_period_tax']='activity_after_assessment'
    result['current_period_deferred_tax']='stale' if result['deferred_assessments'] else 'unassessed'
    return result,proposed['journal'],proposed['flows'],proposed['details']

def deferred_population(result):
    state=result['after'];classes=result['account_classes'];rows=[]
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
        add('inventory/lot/'+tax.info.pointer(key),'asset','inventory',Q(lot['carrying']),lot=key)
    for lease in sorted(state['leases'],key=lambda x:x['component']['lease_id']):
        c=lease['component'];lid=c['lease_id']
        for r in sorted(c['rights'],key=lambda x:x['right_id']):
            rid=r['right_id'];root='lease/'+tax.info.pointer(lid)+'/'+tax.info.pointer(rid)
            add(root+'/asset','asset','rou',Q(r['rou']),lid,rid)
            add(root+'/liability','liability','lease_liability',Q(r['liability']),lid,rid)
    for lot in sorted(result['loss_state']['lots'],key=lambda x:x['id']):
        add('loss/'+tax.info.pointer(lot['id']),'loss',None,Q(lot['remaining']),lot=lot['id'])
    require(len({r['id'] for r in rows})==len(rows),'population_collision')
    return rows

def number(value,label):
    result=losses.declaration(value,'rational');require(result is not None,label+':unknown','unresolved')
    require(result>=0,label+':negative');return result

def deferred_measurement(body,result,pop):
    data=body['measurement']
    core.closed(data,['at','state_sha256','jurisdiction','regime','account_bases','lease_bases'],'measurement')
    core.scalar(data['at'],'date')
    require(data['at']==result['after']['date'],'measurement_date')
    require(data['state_sha256']==book.digest(result['after']),'measurement_state_digest')
    for key in ['jurisdiction','regime']:
        value=losses.declaration(data[key],'text')
        require(value is not None,'measurement_scope_unknown:'+key,'unresolved')
        require(value==result['loss_state'][key],'measurement_scope_changed:'+key)
    accounts=population(result)['basis_accounts']
    lease_keys=['lease/'+tax.info.pointer(r['lease_id'])+'/'+tax.info.pointer(r['right_id'])+'/'+r['kind']
                for r in pop if r['lease_id'] is not None]
    require(type(data['account_bases']) is dict and set(data['account_bases'])==set(accounts),'complete_measurement_accounts')
    require(type(data['lease_bases']) is dict and set(data['lease_bases'])==set(lease_keys),'complete_measurement_rights')
    return {'accounts':{k:number(v,'account_base:'+k) for k,v in data['account_bases'].items()},
            'leases':{k:number(v,'lease_base:'+k) for k,v in data['lease_bases'].items()}}

def deferred_calculate(body,result):
    pop=deferred_population(result);measured=deferred_measurement(body,result,pop);items=body['items'];require(type(items) is list,'item_list')
    mapped={}
    for item in items:
        core.closed(item,['id','tax_base','rate','recognized_deduction','recorded_dta','recorded_dtl','route','support'],'deferred_item')
        core.text(item['id'],'item_id');require(item['id'] not in mapped,'duplicate_item');mapped[item['id']]=item
    require(set(mapped)=={r['id'] for r in pop},'complete_item_population')
    core.closed(body['findings'],deferred.FINDINGS,'deferred_findings')
    for k in deferred.FINDINGS:losses.affirmative(body['findings'][k],k)
    capacity=number(body['recovery_capacity'],'recovery_capacity')
    observations=[];bases={k:Q(0) for k in measured['accounts']}
    used=Q(0);asset=Q(0);liability=Q(0);old_a=Q(0);old_l=Q(0)
    for row in pop:
        item=mapped[row['id']];core.closed(item['support'],deferred.SUPPORT,'item_support')
        for k in deferred.SUPPORT:losses.affirmative(item['support'][k],row['id']+':'+k)
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
            key='lease/'+tax.info.pointer(row['lease_id'])+'/'+tax.info.pointer(row['right_id'])+'/'+row['kind']
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



def deferred_step(state,operation):
    e=operation['event'];core.closed(e,['id','model','measurement','findings','recovery_capacity','items'],'deferred_assessment')
    core.text(e['id'],'assessment_id');require(e['id'] not in state['after']['seen'],'duplicate_assessment')
    core.closed(e['model'],['profile','selected'],'model')
    require(e['model']['profile']==deferred.MODEL,'model_not_implemented','unsupported')
    losses.affirmative(e['model']['selected'],'model_selection')
    require(bool(state['current_assessments']) and state['current_period_tax']=='conditionally_assessed','current_assessment_required','unresolved')
    last=state['current_assessments'][-1]
    require(core.scalar(state['after']['date'],'date')<=core.scalar(last['interval']['activity_through'],'date'),'activity_after_current_assessment','unresolved')
    calc=deferred_calculate(e,state);after=deepcopy(state['after']);balances=after['balances']
    da=Q(calc['desired_dta'])-Q(calc['recorded_dta']);dl=Q(calc['desired_dtl'])-Q(calc['recorded_dtl'])
    journal={k:'0/1' for k in balances};journal.update(dta=book.fmt(da),dtl=book.fmt(-dl),deferred_tax=book.fmt(dl-da))
    after['balances']={k:book.fmt(Q(v)+Q(journal[k])) for k,v in balances.items()};after['seen'].append(e['id'])
    result=deepcopy(state);result['after']=after
    result['deferred_assessments'].append({'id':e['id'],'operation_sha256':book.digest(operation),
        'current_assessment_sha256':last['operation_sha256'],'post_state_sha256':book.digest(after),
        'measurement':deepcopy(e['measurement']),'findings':deepcopy(e['findings']),
        'recovery_capacity':deepcopy(e['recovery_capacity']),'calculation':calc})
    result['current_period_deferred_tax']='conditionally_assessed'
    return result,journal,[],{'kernel':'fresh_period_deferred_measurement','calculation':calc}

def carry_step(state,operation):
    e=operation['event'];core.closed(e,['id','model','next_period','findings'],'provisional_carry')
    core.text(e['id'],'carry_id');financial=state['after']
    require(e['id'] not in financial['seen'],'duplicate_carry')
    core.closed(e['model'],['profile','selected'],'model')
    require(e['model']['profile']==root.boundary.MODEL,'model_not_implemented','unsupported')
    losses.affirmative(e['model']['selected'],'provisional_carry_selected')
    findings=root.carry.findings_status(e['findings'])
    require(state['current_period_tax']==state['current_period_deferred_tax']=='conditionally_assessed','assessments_incomplete','unresolved')
    last=state['current_assessments'][-1];recognition=state['deferred_assessments'][-1]
    require(recognition['post_state_sha256']==book.digest(financial) and recognition['current_assessment_sha256']==last['operation_sha256'],'deferred_measurement_stale','unresolved')
    period=e['next_period'];core.closed(period,['start','end_exclusive'],'next_period')
    start=core.scalar(period['start'],'date');end=core.scalar(period['end_exclusive'],'date')
    require(period['start']==financial['period']['end_exclusive'],'noncontiguous_next_period')
    require(start<end,'next_period_end')
    require(last['interval']['end_exclusive']==state['loss_state']['cursor']==period['start'],'assessment_or_loss_incomplete','unresolved')
    require(core.scalar(financial['date'],'date')==start-timedelta(days=1),'closing_day_incomplete')
    report=root.carry.statements(state['opening'],financial,state['account_classes']);profit=Q(report['recorded_profit'])
    after=deepcopy(financial);after['balances']['retained']=book.fmt(Q(financial['balances']['retained'])-profit)
    for key in state['account_classes']['income']:after['balances'][key]='0/1'
    journal={k:book.fmt(Q(after['balances'][k])-Q(v)) for k,v in financial['balances'].items()}
    after['period']=deepcopy(period);after['date']=period['start'];after['tax_closed_until']=period['start']
    after['flows']=[];after['tax_adjustments']=[];after['opening_interest_paid']='0/1'
    after['tax_premises']['opening_dta']=after['balances']['dta'];after['tax_premises']['opening_dtl']=book.fmt(-Q(after['balances']['dtl']))
    after['seen'].append(e['id']);after['prior_years'].append({'period':deepcopy(financial['period']),
        'closing_sha256':book.digest(financial),'report_sha256':book.digest(report)})
    archive={k:deepcopy(v) for k,v in state.items() if k not in ['period_archive','historical_vintages','recognition_archive']}
    archive.update(report=report,carry_operation=deepcopy(operation),carry_journal=journal)
    result=deepcopy(state);index=len(result['period_archive']);result['period_archive'].append(archive)
    rows=[{'id':v['id'],'origin':{'kind':'archive','index':index,'sha256':book.digest(v)},
        'period':deepcopy(period),'opening_payable':v['closing_payable'],'new_assessment':'0/1',
        'settlements':[],'closing_payable':v['closing_payable']} for v in state['period_vintages']]
    result.update(opening=deepcopy(after),after=after,opening_loss=deepcopy(state['loss_state']),
        period_vintages=rows,opening_vintages=deepcopy(rows),current_assessments=[],deferred_assessments=[],
        findings=deepcopy(e['findings']),finding_status=findings,prior_findings=deepcopy(state['findings']),
        unassessed_native_events=[],current_period_tax='unassessed',current_period_deferred_tax='unassessed',
        period_rights=sorted([list(pair) for pair in {(x['component']['lease_id'],r['right_id'])
            for x in after['leases'] for r in x['component']['rights']}]))
    return result,journal,[],{'kernel':'provisional_period_carry','carried_profit':book.fmt(profit),'report':report}

def transition(state,operation):
    invariant(state);core.closed(operation,['kind','event'],'operation')
    if operation['kind']=='current_assessment':result,journal,flows,details=assessment(state,operation)
    elif operation['kind']=='deferred_assessment':result,journal,flows,details=deferred_step(state,operation)
    elif operation['kind']=='provisional_carry':result,journal,flows,details=carry_step(state,operation)
    else:result,journal,flows,details=event_transition(state,operation)
    invariant(result)
    require(sum(Q(v) for v in journal.values())==0,'journal_unbalanced')
    require(all(Q(result['after']['balances'][k])-Q(v)==Q(journal[k]) for k,v in state['after']['balances'].items()),'journal_effect')
    require(Q(journal['cash'])==sum(Q(f['amount']) for f in flows),'cash_flow_mismatch')
    return {'after':result,'journal':journal,'flows':flows,'details':details,
        'before_sha256':book.digest(state),'operation_sha256':book.digest(operation)}

def run(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();caller.bounded(body)
        core.closed(body,['profile','root_request','root_sha256','operations'],'annual_program')
        require(body['profile']==PROFILE,'profile');require(body['root_sha256']==book.digest(body['root_request']),'root_digest')
        require(type(body['operations']) is list,'operations_list')
        prior=root.run(body['root_request'])
        base.update(root_result=prior,request_sha256=book.digest(body),source_bundle_sha256=LOCK,
            implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(prior['status']=='complete_provisional','root_incomplete','unresolved' if prior['status']=='stopped_provisional' else prior['status'])
        current=seed(prior);invariant(current);trace=[];stop=None
        for i,op in enumerate(body['operations']):
            try:
                result=transition(current,op);trace.append({'operation':deepcopy(op),'result':result});current=result['after']
            except (native.Refused,native.lease.Refused,losses.Refused) as exc:
                stop={'index':i,'status':exc.status,'reason':exc.reason};break
            except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OverflowError,RecursionError) as exc:
                stop={'index':i,'status':'invalid','reason':str(exc)[:350]};break
        report=root.carry.statements(current['opening'],current['after'],current['account_classes'])
        report.update(scope='Finite reusable period book under selected conditional models',unresolved=deepcopy(UNRESOLVED))
        return {**base,'status':'stopped_provisional' if stop else 'complete_provisional','period_book':current,
            'conditional_current_assessed':current['current_period_tax']=='conditionally_assessed',
            'conditional_deferred_assessed':current['current_period_deferred_tax']=='conditionally_assessed',
            'deferred_asset_recognized':current['current_period_deferred_tax']=='conditionally_assessed' and Q(current['after']['balances']['dta'])>0,
            'trace':trace,'stop':stop,'remaining_operations':deepcopy(body['operations'][len(trace):]),
            'recorded_statements':report,'unresolved':deepcopy(UNRESOLVED)}
    except (native.Refused,native.lease.Refused,losses.Refused) as exc:return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,OSError,AssertionError,OverflowError,RecursionError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}

def apply(body,result):
    expected=run(body)
    try:
        require(expected['status'] in ['complete_provisional','stopped_provisional'],'no_valid_prefix')
        require(caller.canonical(expected)==caller.canonical(result),'complete_result_mismatch')
        return {**deepcopy(expected),'status':'applied_provisional'}
    except (ValueError,TypeError,OverflowError,RecursionError) as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
