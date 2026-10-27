"""Full-account same-period continuation of a conditional financial tax state."""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import json
import shared_tax_state_v1 as tax

book=tax.book
returns=book.returns
lease=book.lease
caller=book.caller
core=tax.core
ROOT=Path(__file__).resolve().parents[1]
HERE=ROOT/'data/accounting-master/shared-tax-continuation-20261024'
LOCK='b30d4a97cdfb3e7ae16fd9146281b23a21ef67caa447ae1433b990df294eccf9'
PROFILE='ConditionalSharedTaxContinuation/1'
STATE='SyntheticReturnLeaseTaxBook/1'
ACCOUNTS=book.ACCOUNTS+['income_tax_payable']
CONTEXT=book.CONTEXT
FLAGS={**tax.FLAGS,'method_eligible':False}
Refused=book.Refused
need=book.need
digest=book.digest
fmt=book.fmt
amount=book.amount


def protected():
    raw=(HERE/'source-lock.json').read_bytes()
    need(sha256(raw).hexdigest()==LOCK,'source_lock_changed')
    for name,h in json.loads(raw).items():
        need(sha256((ROOT/name).read_bytes()).hexdigest()==h,'protected_source_changed:'+name)
    book.protected();tax.protected()


def schema():
    shape=book.schema();p=shape['properties']
    p['profile']={'const':STATE}
    p['balances']=returns.structure.author.closed({k:deepcopy(p['other_inventory']) for k in ACCOUNTS})
    return shape


# Preserve the original semantic checks and selected numerical adapters with
# explicit successor schema/registry globals. No projection or runtime patching.
def invariant(state):
    caller.bounded(state);returns.structure.validate(state,schema())
    need(state['context']==CONTEXT,'declared_context_only','unsupported')
    now=lease.day(state['date']);start=lease.day(state['period']['start']);end=lease.day(state['period']['end_exclusive'])
    need(start<=now<end,'state_date_outside_period')
    need(start<=lease.day(state['tax_closed_until'])<=now,'tax_close_date')
    b={k:amount(v) for k,v in state['balances'].items()}
    need(sum(b.values())==0,'shared_book_unbalanced')
    need(b['cash']>=0,'shared_cash_shortage','funding_failure')
    c=state['component'];lots=state['lots']
    need(amount(state['other_inventory'])>=0,'negative_other_inventory')
    need(b['inventory']==amount(state['other_inventory'])+sum(amount(l['carrying']) for l in lots.values()),'inventory_allocation')
    need(b['refund_liability']==-amount(c['refund']) and b['recovery_asset']==amount(c['recovery']),'return_allocation')
    if c['settled']:need(amount(c['refund'])==amount(c['recovery'])==0,'settled_rights_remain')
    for key,l in lots.items():
        need(key==l['id'] and l['component_id']==c['id'],'lot_identity')
        need(amount(l['units'])>=0 and amount(l['carrying'])>=0 and amount(l['tax_base'])==amount(l['carrying']),'lot_amount_or_tax_method')
        need(lease.day(l['acquired'])<=now,'future_lot')
        need((amount(l['units'])==amount(l['carrying'])==amount(l['tax_base'])==0) if l['disposed'] else amount(l['units'])>0,'lot_disposition')
    need(state['lease_membership'] is True,'lease_membership_unresolved','unresolved')
    ids=set();rou=Q(0);liability=Q(0)
    for item in state['leases']:
        comp=lease.typed(item['component'],lease.types.COMPONENTS['lease']);key=comp['lease_id']
        need(key not in ids and bool(comp['rights']),'lease_identity_or_empty_rights');ids.add(key)
        a=sum(r['rou'] for r in comp['rights']);l=sum(r['liability'] for r in comp['rights'])
        lease.financial.check_component('lease',comp,{'rou':a,'lease_liability':-l})
        need(all(lease.day(r['last_measurement_date'])<=now for r in comp['rights']),'future_lease_measurement')
        rou+=a;liability+=l
    need(b['rou']==rou and b['lease_liability']==-liability,'lease_allocation')
    need(len(state['seen'])==len(set(state['seen'])),'duplicate_event_history')
    taxids=[a['event_id'] for a in state['tax_adjustments']]
    need(len(taxids)==len(set(taxids)) and set(taxids)<=set(state['seen']),'tax_adjustment_history')
    for a in state['tax_adjustments']:need(start<=lease.day(a['date'])<=now,'tax_adjustment_date')
    for f in state['flows']:
        need(f['entity']==CONTEXT['entity'] and f['event_id'] in state['seen'],'flow_owner_or_event')
        need(start<=lease.day(f['date'])<=now,'flow_date')
    return state


def memory_program(kind):
    _,builder=returns.checked_builders();definition,schemas=builder.program(kind)
    shape=schema();inputs=deepcopy(schemas[definition['input_schema']]);inputs['properties']['balances']=deepcopy(shape['properties']['balances'])
    h,k=digest(shape),digest(inputs);definition['state_schema']=h;definition['input_schema']=k
    return definition,{h:shape,k:inputs}

def return_effect(state,event):
    returns.structure.validate(event,returns.event_schema())
    need(event['kind'] in ['settle','sell'],'selected_return_methods_only','unsupported')
    if event['kind']=='settle':need(event['lot_id'] not in state['lots'],'duplicate_lot')
    else:
        need(event['lot_id'] in state['lots'],'unknown_lot')
        need(not state['lots'][event['lot_id']]['disposed'],'lot_disposed')
    assessed,lineage=returns.prerequisite_manifest(state,event,digest(state),digest(event))
    need(assessed['status']=='requirements_satisfied','return_prerequisites:'+assessed['status'],assessed['status'])
    builder,_=returns.checked_builders()
    context={'entity':CONTEXT['entity'],'book_role':'legal','at':event['date']}
    definition=builder.program(event['kind'],context,ACCOUNTS)
    values=builder.project(state,event)
    if event['kind']=='settle':
        paths={'n':('event','/actual_units'),'p':('before','/component/unit_refund'),
          'c':('before','/component/unit_cost'),'d':('event','/unit_deterioration'),
          'h':('event','/unit_handling'),'nrv':('event','/inventory_nrv'),
          'refund_before':('before','/component/refund'),'recovery_before':('before','/component/recovery')}
    else:
        token=event['lot_id'].replace('~','~0').replace('/','~1')
        paths={'proceeds':('event','/proceeds'),'cost':('before','/lots/'+token+'/carrying')}
    monetary_lineage={}
    for key,(origin,pointer) in paths.items():
        h=digest(state if origin=='before' else event)
        definition['inputs'][key]['source_ref']='sha256:'+h+'#'+pointer
        monetary_lineage[key]={'source':origin,'sha256':h,'pointer':pointer}
    amounts=returns.monetary.derive({digest(definition):definition},digest(definition),values)
    need(amounts['status']=='derived','return_amounts:'+amounts['status'],amounts['status'])
    balances={k:fmt(amount(v)+amount(amounts['journal'][k])) for k,v in state['balances'].items()}
    _,memory_builder=returns.checked_builders();inputs=memory_builder.inputs_for(state,event,amounts);inputs['balances']=balances
    mem,schemas=memory_program(event['kind']);staged=returns.memory.stage({digest(mem):mem},digest(mem),schemas,state,inputs)
    need(staged['status']=='staged','return_memory:'+staged.get('reason',staged['status']))
    return staged['after'],amounts['journal'],inputs['flows'],{'prerequisites':assessed,'prerequisite_lineage':lineage,'monetary_definition':digest(definition),'monetary_lineage':monetary_lineage,'memory_definition':digest(mem)}

def lease_effect(state,event):
    caller.closed(event,['id','date','method','lease_id','parameters'])
    method=event['method'];need(method in lease.FOOTPRINT,'selected_lease_methods_only','unsupported')
    selected=[i for i,x in enumerate(state['leases']) if x['component']['lease_id']==event['lease_id']]
    need(len(selected)==1,'unknown_lease');index=selected[0]
    comp=lease.typed(state['leases'][index]['component'],lease.types.COMPONENTS['lease'])
    params=lease.typed(event['parameters'],lease.types.EVENTS[method][1])
    after,j,cash,oci,equity=lease.financial.derive('lease',comp,method,params,event['date'],lease.original_need)
    need(set(j)<=lease.FOOTPRINT[method] and all(v==0 for v in [*oci.values(),*equity.values()]),'kernel_footprint_changed','unsupported')
    journal={k:fmt(j.get(k,Q(0))) for k in ACCOUNTS}
    flows=[{'entity':CONTEXT['entity'],'activity':k,'origin':method+':'+event['lease_id'],'amount':fmt(v),'date':event['date'],'event_id':event['id']} for k,v in cash.items() if v]
    z=deepcopy(state);z['leases'][index]['component']=lease.encode(after)
    z['balances']={k:fmt(amount(v)+amount(journal[k])) for k,v in state['balances'].items()}
    z['date']=event['date'];z['seen'].append(event['id']);z['flows'].extend(flows)
    return z,journal,flows,{'kernel':'original_corporate_lease','method':method}


def request(origin, operations):
    return {'profile':PROFILE,'origin':deepcopy(origin),'origin_sha256':digest(origin),
            'operations':deepcopy(operations)}


def seed(origin, base):
    checked,native=tax._validate(origin,base)
    state=deepcopy(native['execution']['after']);state['profile']=STATE
    state['balances']=deepcopy(checked['balances']);state['date']=checked['date']
    state['seen'].append(checked['accrual_request']['id'])
    for event in checked['settlements']:
        state['seen'].append(event['id'])
        state['flows'].append({'entity':CONTEXT['entity'],'activity':'operating',
            'origin':'explicit_conditional_current_tax_payment','amount':fmt(-Q(event['amount'])),
            'date':event['date'],'event_id':event['id']})
    invariant(state)
    return state,native


def transition(state, operation, assessed_until):
    invariant(state);caller.closed(operation,['kind','event'])
    native=operation['kind']=='native'
    need(native or operation['kind']=='tax_payment','unsupported_operation','unsupported')
    if native:
        outer=operation['event'];caller.closed(outer,['profile','module','event'])
        need(outer['profile']==book.EVENT,'event_profile')
        need(outer['module'] in ['return','lease'],'unsupported_module','unsupported')
        event=outer['event']
    else:event=operation['event']
    need(type(event) is dict,'event_record');core.text(event.get('id'),'event_id')
    day=core.scalar(event['date'],'date')
    need(event['id'] not in state['seen'],'duplicate_event')
    need(lease.day(state['date'])<=day<lease.day(state['period']['end_exclusive']),'event_chronology')
    if native:
        need(day>=lease.day(assessed_until),'event_inside_assessed_interval')
        after,journal,flows,details=(return_effect if outer['module']=='return' else lease_effect)(state,event)
        writes={'balances','date','seen','flows'}|({'component','lots','tax_adjustments'} if outer['module']=='return' else {'leases'})
        need(all(journal[k]=='0/1' for k in ['income_tax_payable','current_tax','deferred_tax','dta','dtl']),
             'native_tax_footprint')
    else:
        core.closed(event,['id','date','amount','authorization'],'tax_payment')
        tax.losses.affirmative(event['authorization'],'cash_payment_authorization')
        paid=tax.losses.tax.numeric(event['amount']);need(paid>0,'positive_payment_required')
        need(paid<=-amount(state['balances']['income_tax_payable']),'payment_exceeds_payable')
        need(paid<=amount(state['balances']['cash']),'cash_shortage','funding_failure')
        journal={k:'0/1' for k in ACCOUNTS};journal['cash']=fmt(-paid);journal['income_tax_payable']=fmt(paid)
        flows=[{'entity':CONTEXT['entity'],'activity':'operating','origin':'explicit_conditional_current_tax_payment',
                'amount':fmt(-paid),'date':event['date'],'event_id':event['id']}]
        after=deepcopy(state);after['balances']={k:fmt(amount(v)+amount(journal[k])) for k,v in state['balances'].items()}
        after['date']=event['date'];after['seen'].append(event['id']);after['flows'].extend(flows)
        details={'kernel':'explicit_current_tax_payment'};writes={'balances','date','seen','flows'}
    need(all(state[k]==after[k] for k in state if k not in writes),'module_write_boundary')
    need(after['seen']==state['seen']+[event['id']] and after['flows']==state['flows']+flows,'append_history_boundary')
    need(sum(amount(v) for v in journal.values())==0,'journal_unbalanced')
    need(amount(journal['cash'])==sum(amount(f['amount']) for f in flows),'cash_flow_mismatch')
    invariant(after)
    return {'after':after,'journal':journal,'flows':flows,'details':details,
            'before_sha256':digest(state),'operation_sha256':digest(operation)}


def statements(state, native):
    classes=deepcopy(native['account_classes']);classes['liabilities'].append('income_tax_payable')
    all_accounts=sum(classes.values(),[])
    need(len(all_accounts)==len(set(all_accounts)) and set(all_accounts)==set(ACCOUNTS),'account_classification')
    b=state['balances']
    b0=native['cash_flows_recorded']['opening_cash']
    assets=sum(amount(b[k]) for k in classes['assets']);liabilities=-sum(amount(b[k]) for k in classes['liabilities'])
    profit=-sum(amount(b[k]) for k in classes['income']);equity=-sum(amount(b[k]) for k in classes['equity'])+profit
    cf={}
    for activity in ['operating','investing','financing']:
        values=[amount(f['amount']) for f in state['flows'] if f['activity']==activity]
        cf[activity]={'receipts':fmt(sum(v for v in values if v>=0)),
                      'payments':fmt(-sum(v for v in values if v<0)),'net':fmt(sum(values))}
    cash_change=amount(b['cash'])-amount(b0)
    prior=native['execution']['after']['balances']
    bridge=deepcopy(native['indirect_operating_recorded']['items'])
    bridge.update(recorded_profit=fmt(profit),depreciation=b['depreciation'],
                  deferred_tax_recorded=b['deferred_tax'],remove_lease_gain=b['other_gains'],
                  opening_interest_paid=fmt(-amount(state['opening_interest_paid'])),
                  change_income_tax_payable=fmt(-amount(b['income_tax_payable'])))
    for k in tax.losses.tax.information.reports.WORKING_CAPITAL:
        bridge['change_'+k]=fmt(amount(bridge['change_'+k])-(amount(b[k])-amount(prior[k])))
    indirect=sum(amount(v) for v in bridge.values())
    checks={'balance_sheet':assets-liabilities-equity,
            'equity':amount(native['equity_recorded']['opening'])+profit-equity,
            'direct_cash':cash_change-sum(amount(v['net']) for v in cf.values()),
            'indirect_cash':indirect-amount(cf['operating']['net'])}
    need(all(v==0 for v in checks.values()),'statement_reconciliation')
    return {'scope':'recorded completed prefix with conditional tax accrual',
            'balance_sheet':{'total_assets':fmt(assets),'total_liabilities':fmt(liabilities),
                             'equity_including_profit':fmt(equity)},'recorded_profit':fmt(profit),
            'cash_flows':{'activities':cf,'opening_cash':b0,'closing_cash':b['cash'],
                          'net_movement':fmt(cash_change),'gross_origins':deepcopy(state['flows'])},
            'indirect_operating':{'items':bridge,'net':fmt(indirect)},
            'reconciliations':{k:fmt(v) for k,v in checks.items()},
            'unresolved':['Post-assessment tax calculation','Financial-year carry',
                          'Source and accounting admission','Annual completeness']}


def run(body):
    base={'profile':PROFILE,**FLAGS}
    try:
        protected();caller.bounded(body);caller.closed(body,['profile','origin','origin_sha256','operations'])
        need(body['profile']==PROFILE,'profile');need(body['origin_sha256']==digest(body['origin']),'origin_digest')
        need(type(body['operations']) is list,'operation_list')
        base.update(request_sha256=digest(body),source_bundle_sha256=LOCK,
                    implementation_sha256=sha256(Path(__file__).read_bytes()).hexdigest())
        current,native=seed(body['origin'],base)
        base['native_report']=deepcopy(native);base['origin']=deepcopy(body['origin'])
        trace=[];status='complete';stop=None
        for index,operation in enumerate(body['operations']):
            try:
                result=transition(current,operation,body['origin']['assessed_until'])
                trace.append({'operation':deepcopy(operation),'status':'proposed','result':result})
                current=result['after']
            except (Refused,lease.Refused,tax.losses.Refused) as exc:
                status='stopped';stop={'index':index,'status':exc.status,'reason':exc.reason};break
            except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OverflowError,RecursionError) as exc:
                status='stopped';stop={'index':index,'status':'invalid','reason':str(exc)[:350]};break
        return {**base,'status':status,'after':current,'trace':trace,'stop':stop,
                'remaining_operations':deepcopy(body['operations'][len(trace):]),
                'assessed_until':body['origin']['assessed_until'],
                'loss_state':deepcopy(body['origin']['loss_state']),
                'recorded_statements':statements(current,native)}
    except (Refused,lease.Refused,tax.losses.Refused) as exc:
        return {**base,'status':exc.status,'reason':exc.reason}
    except (ValueError,TypeError,KeyError,AttributeError,AssertionError,OSError,OverflowError,RecursionError) as exc:
        return {**base,'status':'invalid','reason':str(exc)[:350]}


def apply(body,result):
    expected=run(body)
    try:
        need(expected['status'] in ['complete','stopped'],'no_valid_prefix')
        need(caller.canonical(result)==caller.canonical(expected),'complete_result_mismatch')
        return {'profile':PROFILE,**FLAGS,'status':'applied_prefix','after':deepcopy(expected['after']),
                'completed_operations':len(expected['trace']),'stop':deepcopy(expected['stop'])}
    except (ValueError,TypeError,RecursionError,OverflowError) as exc:
        return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350]}

