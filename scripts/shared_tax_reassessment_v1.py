"""Explicit cumulative replacement on the actual continued financial book."""
from copy import deepcopy
from datetime import timedelta
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import shared_tax_continuation_v1 as continuation

tax=continuation.tax
losses=tax.losses
info=losses.tax.information
core=tax.core
book=tax.book
require=losses.require
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/shared-tax-reassessment-20261024'
LOCK='39d6f22f41a2efb6d14fa414f13378a99536efed37c95e47a113c6dbd85e0171'
PROFILE='ConditionalSharedTaxReassessment/1'
MODEL='cumulative_replacement_no_credits_v1'
FLAGS={**continuation.FLAGS,'cash_refund':False,'deferred_asset_recognized':False}


def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    require(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        require(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)


def population(result):
    original=result['origin']['accrual_request']['loss_request']['reconciliation_request']['information_request']['report_request']
    states=[original['opening'],result['native_report']['execution']['after'],result['after']]
    states += [r['result']['after'] for r in result['trace']]
    rights=sorted({(a['component']['lease_id'],r['right_id']) for s in states for a in s['leases'] for r in a['component']['rights']})
    classes=result['native_report']['account_classes']
    return {'pretax_accounts':[k for k in classes['income'] if k not in ['current_tax','deferred_tax']],
            'basis_accounts':[k for k in classes['assets']+classes['liabilities'] if k not in ['dta','dtl']]+['income_tax_payable'],
            'lease_rights':[{'lease_id':a,'right_id':b} for a,b in rights]}


def fields(pop):
    result={k:'text' for k in info.GLOBAL_TEXT}
    result.update({k:'boolean' for k in info.GLOBAL_FINDINGS});result['rate']='rational'
    for k in pop['pretax_accounts']:
        result['income/'+info.pointer(k)+'/treatment']='text'
        result['income/'+info.pointer(k)+'/current_adjustment']='rational'
    for k in pop['basis_accounts']:
        for when in ['opening','closing']:result['basis/'+info.pointer(k)+'/'+when]='rational'
    for r in pop['lease_rights']:
        root='lease/'+info.pointer(r['lease_id'])+'/'+info.pointer(r['right_id'])
        for when in ['opening','closing']:
            for side in ['asset','liability']:result[root+'/'+when+'_'+side+'_tax_base']='rational'
        for k in ['deduction_timing','modification_gain_treatment']:result[root+'/'+k]='text'
    return result


def assess(declarations,pop):
    require(type(declarations) is dict,'information_map');catalog=fields(pop)
    require(set(declarations)<=set(catalog),'undeclared_information')
    values={};missing=[];false=[]
    for key,kind in catalog.items():
        if key not in declarations:missing.append(key);continue
        value=losses.declaration(declarations[key],kind)
        if value is not None and kind=='text':require(value!='unknown','unknown_must_be_explicit:'+key)
        if value is not None and key=='rate':require(value>=0,'negative_rate')
        if value is None:missing.append(key)
        elif kind=='boolean' and value is False:false.append(key)
        else:values[key]=value
    require(not false,'false_findings:'+','.join(false),'unsupported')
    require(not missing,'missing_declarations:'+','.join(missing),'unresolved')
    require(values['rate']>=0,'negative_rate')
    return values


def reconcile(closing,interval,values,pop,allocations):
    require(type(allocations) is list,'allocation_list')
    totals={k:Q(0) for k in pop['pretax_accounts']};ids=set();used=set()
    native={a['event_id']:a for a in closing['tax_adjustments'] if interval['start']<=a['date']<interval['end_exclusive']}
    for item in allocations:
        core.closed(item,['id','account','amount','origin'],'allocation');core.text(item['id'],'allocation_id')
        require(item['id'] not in ids,'duplicate_allocation');ids.add(item['id'])
        require(type(item['account']) is str and item['account'] in totals,'allocation_account')
        quantity=losses.tax.numeric(item['amount']);origin=item['origin'];require(type(origin) is dict,'allocation_origin')
        if origin.get('kind')=='native_return':
            core.closed(origin,['kind','event_id'],'native_origin');key=origin['event_id']
            require(key in native and key not in used,'native_adjustment_identity')
            require(quantity==Q(native[key]['amount']),'native_adjustment_amount');used.add(key)
        else:
            core.closed(origin,['kind','reference'],'assumption_origin')
            require(origin['kind']=='assumption','allocation_origin_kind');core.text(origin['reference'],'assumption_reference')
        totals[item['account']]+=quantity
    require(used==set(native),'incomplete_native_adjustments')
    for k,v in totals.items():require(v==values['income/'+info.pointer(k)+'/current_adjustment'],'adjustment_sum:'+k)
    bases={}
    for when in ['opening','closing']:
        for side,account in [('asset','rou'),('liability','lease_liability')]:
            total=sum(values['lease/'+info.pointer(r['lease_id'])+'/'+info.pointer(r['right_id'])+'/'+when+'_'+side+'_tax_base'] for r in pop['lease_rights'])
            aggregate=values['basis/'+account+'/'+when]
            require(total==aggregate,'lease_basis_mismatch:'+when+':'+side)
            bases[when+'_'+side]={'rights':book.fmt(total),'account':book.fmt(aggregate)}
    pretax=-sum(Q(closing['balances'][k]) for k in pop['pretax_accounts'])
    adjustment=sum(totals.values())
    return {'pretax_income':book.fmt(pretax),'signed_adjustments':book.fmt(adjustment),
            'taxable_profit':book.fmt(pretax+adjustment),'rate':book.fmt(values['rate']),
            'adjustment_totals':{k:book.fmt(v) for k,v in totals.items()},
            'native_adjustment_ids':sorted(used),'basis_reconciliations':bases}


def replacement_losses(opening,interval,calculation,policy,identity,calculation_digest,superseded):
    losses.validate_state(opening)
    core.closed(policy,['model','utilization_cap','uses','generation'],'loss_policy')
    core.closed(policy['model'],['profile','selected'],'loss_model')
    require(policy['model']['profile']==losses.MODEL,'loss_model')
    losses.affirmative(policy['model']['selected'],'loss_model_selected')
    losses.affirmative(opening['opening_inventory'],'complete_opening_loss_inventory')
    cap=losses.declaration(policy['utilization_cap'],'rational')
    require(cap is not None,'cap_unknown','unresolved');require(cap>=0,'negative_cap')
    require(type(policy['uses']) is list,'usage_list')
    require(opening['cursor']==interval['start'],'original_loss_cursor')
    require(identity not in opening['seen'],'duplicate_loss_step')
    end=core.scalar(interval['end_exclusive'],'date');usage_day=core.scalar(interval['activity_through'],'date')
    taxable=Q(calculation['taxable_profit']);rate=Q(calculation['rate'])
    after=deepcopy(opening);lots={lot['id']:lot for lot in after['lots']}
    movements={lot['id']:{'opening':losses.amount(lot['remaining']),'generated':Q(0),'used':Q(0),'expired':Q(0)} for lot in after['lots']}
    expiries={}
    for lot in after['lots']:
        if losses.amount(lot['remaining'])==0:continue
        losses.affirmative(lot['eligible'],'lot_eligibility:'+lot['id'])
        limit=losses.expiry(lot['expiry']);require(limit!='unknown','lot_expiry_unknown:'+lot['id'],'unresolved')
        expiries[lot['id']]=limit
    used_ids=set();total_used=Q(0)
    for use in policy['uses']:
        core.closed(use,['lot_id','amount'],'loss_use');core.text(use['lot_id'],'used_id')
        key=use['lot_id'];require(key in lots,'unknown_original_loss_lot')
        require(key not in used_ids,'duplicate_usage');used_ids.add(key)
        used=losses.amount(use['amount']);require(used>0,'positive_loss_use')
        lot=lots[key];limit=expiries.get(key)
        require(losses.amount(lot['remaining'])>=used,'lot_overuse')
        require(limit is None or limit>usage_day,'expired_lot_use')
        lot['remaining']=book.fmt(losses.amount(lot['remaining'])-used)
        lot['used']=book.fmt(losses.amount(lot['used'])+used)
        movements[key]['used']=used;total_used+=used
    require(total_used<=cap and total_used<=max(Q(0),taxable),'usage_exceeds_cap_or_profit')
    for lot in after['lots']:
        limit=expiries.get(lot['id'])
        if limit is not None and limit<=end:
            remaining=losses.amount(lot['remaining']);lot['remaining']='0/1'
            lot['expired']=book.fmt(losses.amount(lot['expired'])+remaining)
            movements[lot['id']]['expired']=remaining
    if taxable<0:
        require(not policy['uses'],'negative_profit_cannot_use_losses');g=policy['generation']
        core.closed(g,['id','eligible','expiry'],'generation');core.text(g['id'],'generation_id')
        require(g['id'] not in lots and g['id'] not in {lot['id'] for lot in superseded['lots']},'reused_provisional_loss_id')
        losses.affirmative(g['eligible'],'generated_eligibility')
        limit=losses.expiry(g['expiry']);require(limit!='unknown','generated_expiry_unknown','unresolved')
        require(limit is None or limit>end,'generated_expiry_before_availability')
        generated=-taxable;key=g['id']
        after['lots'].append({'id':key,'origin_reference':'sha256:'+calculation_digest+'#/calculation/taxable_profit',
            'available_from':interval['end_exclusive'],'expiry':deepcopy(g['expiry']),
            'original':book.fmt(generated),'remaining':book.fmt(generated),'used':'0/1','expired':'0/1','eligible':deepcopy(g['eligible'])})
        movements[key]={'opening':Q(0),'generated':generated,'used':Q(0),'expired':Q(0)}
    else:require(policy['generation'] is None,'positive_cannot_generate')
    for lot in after['lots']:movements[lot['id']]['closing']=losses.amount(lot['remaining'])
    totals={key:sum(row[key] for row in movements.values()) for key in ['opening','generated','used','expired','closing']}
    require(totals['opening']+totals['generated']==totals['used']+totals['expired']+totals['closing'],'loss_conservation')
    after['cursor']=interval['end_exclusive'];after['seen'].append(identity)
    after['history'].append({'step_id':identity,'start':interval['start'],'end_exclusive':interval['end_exclusive'],
        'reconciliation_sha256':calculation_digest,**{key:book.fmt(v) for key,v in totals.items()}})
    losses.validate_state(after)
    taxable_after=max(Q(0),taxable-total_used)
    return {'after':after,'movements':{k:{n:book.fmt(v) for n,v in row.items()} for k,row in movements.items()},
            'totals':{k:book.fmt(v) for k,v in totals.items()},'taxable_profit_before_losses':book.fmt(taxable),
            'taxable_profit_after_losses':book.fmt(taxable_after),'conditional_gross_current_tax':book.fmt(taxable_after*rate),
            'usage_day':interval['activity_through'],'expiry_rule':losses.MODEL,
            'scope':'replacement from original loss opening; provisional closing ledger is superseded'}


def request(continuation_request,identity,model,interval,declarations,allocations,loss_policy):
    original=continuation_request['origin']['accrual_request']['loss_request']['state']
    return {'profile':PROFILE,'continuation_request':deepcopy(continuation_request),
        'continuation_sha256':book.digest(continuation_request),'id':identity,'model':deepcopy(model),
        'interval':deepcopy(interval),'information':deepcopy(declarations),'allocations':deepcopy(allocations),
        'original_loss_opening_sha256':book.digest(original),'loss_policy':deepcopy(loss_policy)}


def propose(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();continuation.caller.bounded(body)
        core.closed(body,['profile','continuation_request','continuation_sha256','id','model','interval',
                          'information','allocations','original_loss_opening_sha256','loss_policy'],'request')
        require(body['profile']==PROFILE,'profile');core.text(body['id'],'reassessment_id')
        require(body['continuation_sha256']==book.digest(body['continuation_request']),'continuation_digest')
        core.closed(body['model'],['profile','selected'],'model')
        require(body['model']['profile']==MODEL,'cumulative_model_required')
        continued=continuation.run(body['continuation_request'])
        base.update(request_sha256=book.digest(body),continuation_result=continued,
                    source_bundle_sha256=LOCK,implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        require(continued['status'] in ['complete','stopped'],'continuation:'+continued['status'],continued['status'])
        require(continued['status']=='complete','requested_continuation_incomplete','unresolved')
        losses.affirmative(body['model']['selected'],'cumulative_model_selected')
        origin=continued['origin'];closing=continued['after'];interval=body['interval']
        original=origin['accrual_request']['loss_request']['state']
        require(body['original_loss_opening_sha256']==book.digest(original),'original_loss_opening_digest')
        core.closed(interval,['start','end_exclusive','activity_through'],'interval')
        start,end,through=[core.scalar(interval[k],'date') for k in ['start','end_exclusive','activity_through']]
        require(interval['start']==closing['period']['start']==original['cursor'],'cumulative_start')
        require(core.scalar(origin['assessed_until'],'date')<end<=core.scalar(closing['period']['end_exclusive'],'date'),'later_endpoint')
        require(through==end-timedelta(days=1),'exclusive_endpoint')
        require(core.scalar(closing['date'],'date')<=through,'recorded_events_after_assessment')
        require(body['id'] not in closing['seen'] and body['id'] not in original['seen'] and
                body['id'] not in origin['loss_state']['seen'],'reused_assessment_id')
        pop=population(continued);base['population']=pop
        values=assess(body['information'],pop)
        for key in ['jurisdiction','regime']:
            require(values[key]==original[key],'tax_scope_changed:'+key)
        require(original['context']==closing['context'],'loss_context_changed')
        calculation=reconcile(closing,interval,values,pop,body['allocations'])
        base['calculation']=calculation
        calc_digest=book.digest({'request_sha256':base['request_sha256'],'calculation':calculation})
        loss_result=replacement_losses(original,interval,calculation,body['loss_policy'],body['id'],calc_digest,origin['loss_state'])
        base['replacement_loss_result']=loss_result
        old=Q(closing['balances']['current_tax']);new=Q(loss_result['conditional_gross_current_tax'])
        old_payable=-Q(closing['balances']['income_tax_payable']);paid=old-old_payable
        actual=sum(Q(e['amount']) for e in origin['settlements'])
        actual+=sum(Q(t['operation']['event']['amount']) for t in continued['trace'] if t['operation']['kind']=='tax_payment')
        require(old>=0 and old_payable>=0 and paid==actual>=0,'prior_tax_payment_identity')
        delta=new-old;payable=new-paid
        base['financial_calculation']={'previous_expense':book.fmt(old),'replacement_expense':book.fmt(new),
            'actual_paid':book.fmt(paid),'incremental_expense':book.fmt(delta),'replacement_payable':book.fmt(payable)}
        require(payable>=0,'tax_receivable_or_refund_route_required','unsupported')
        after=deepcopy(closing);after['balances']['current_tax']=book.fmt(new)
        after['balances']['income_tax_payable']=book.fmt(-payable)
        after['date']=interval['activity_through'];after['seen'].append(body['id'])
        continuation.invariant(after)
        journal={k:'0/1' for k in continuation.ACCOUNTS}
        journal['current_tax']=book.fmt(delta);journal['income_tax_payable']=book.fmt(-delta)
        statements=continuation.statements(after,continued['native_report'])
        return {**base,'status':'proposed','after':after,'journal':journal,'recorded_statements':statements,
                'assessed_until':interval['end_exclusive'],'loss_state':deepcopy(loss_result['after']),
                'superseded':{'assessment_request_sha256':book.digest(origin['accrual_request']),
                              'loss_state_sha256':book.digest(origin['loss_state']),
                              'assessment_end_exclusive':origin['assessed_until']}}
    except (losses.Refused,continuation.Refused,continuation.lease.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OSError,RecursionError,OverflowError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}


def apply(body,result):
    expected=propose(body)
    try:
        require(expected['status']=='proposed','proposal_not_available')
        require(continuation.caller.canonical(result)==continuation.caller.canonical(expected),'complete_result_mismatch')
        return {'profile':PROFILE,**FLAGS,'status':'applied','after':deepcopy(expected['after']),
                'loss_state':deepcopy(expected['loss_state']),'assessed_until':expected['assessed_until']}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}
