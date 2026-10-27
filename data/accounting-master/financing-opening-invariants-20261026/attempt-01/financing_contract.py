"""Selected financing state/history contracts over the preserved typed engines."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import json, sys

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import declared_company_program_v2 as runtime
import method_requirements_v3 as guarded
import declared_financing_methods_v1 as h
engine=runtime.engine;core=runtime.core
PROFILE='SelectedFinancingContract/1'
HISTORY='SuppliedFinancingOpeningHistory/1'
CALL='SelectedFinancingCall/1'
FLAGS=dict(source_admission=False,accounting_admission=False,production_ready=False,durable=False)
DATE={'kind':'date','context':{}}
FIELDS=['original_face','outstanding','arrears','missed_amount','due','matured','missed','old_shares','new_shares']
METHODS=['mature','equity','settle_due','observe_missed','settle_late']
RESIDUALS=['Supplied synthetic zero-coupon promise; one accretion interval; no fees, tax, penalties, acceleration or accounting admission',
           'Opening history completeness is supplied, not independently established',
           'Missed payment does not establish legal default; no carry or rights-changing events in this selection']

def digest(value):return core.digest(value)
def ordered(value):return sha256(json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def ref(n):return {'op':'ref','id':n}
def const(t,v):return {'op':'const','type':deepcopy(t),'value':v}
def op(kind,a,b):return {'op':kind,'left':deepcopy(a),'right':deepcopy(b)}
def all_of(*args):return {'op':'all','args':list(args)}
def negate(a):return {'op':'not','arg':a}

def declaration(name,bindings,rows):
    inputs={k:h.declaration(x['type'],k) for k,x in bindings.items()}
    manifest=dict(profile=guarded.PROFILE,method_id=name,version='1',inputs=inputs,
                  requirements=rows,required_known=list(inputs),capabilities=[],residual_prerequisites=RESIDUALS)
    guarded.compile_manifest(manifest)
    return dict(manifest=manifest,bindings=bindings)

def rule(name,predicate,requires,guard=None,guard_requires=None):
    return dict(id=name,guard=const(core.BOOL,True) if guard is None else guard,
                guard_requires=guard_requires or [],predicate=predicate,requires=requires,
                admission_refs=[],on_false='invalid',on_unknown='unresolved')

def source(phase,kind,typ,**kw):return dict(phase=phase,kind=kind,type=deepcopy(typ),**kw)

def make_contract(program,roles):
    book=program['opening'];money=engine.money_type(book)
    field_types={n:deepcopy(book['memory_types']['/debt_terms/'+n]) for n in FIELDS}
    bindings={n:source('book','memory',field_types[n],pointer='/debt_terms/'+n) for n in FIELDS}
    bindings.update(as_of=source('book','date',DATE),debt=source('book','balance',money,account=roles['debt']),
                    cash=source('book','balance',money,account=roles['cash']))
    rows=[];zero=const(money,'0/1');face=ref('original_face');remaining=ref('outstanding')
    for n in ['original_face','outstanding','arrears','missed_amount','old_shares','new_shares']:
        rows.append(rule(n+'_nonnegative',op('le',const(field_types[n],'0/1'),ref(n)),[n]))
    rows.extend([rule('positive_face',op('lt',zero,face),['original_face']),
                 rule('claim_bounded',op('le',remaining,face),['outstanding','original_face']),
                 rule('arrears_bounded',op('le',ref('arrears'),remaining),['arrears','outstanding']),
                 rule('missed_bounded',op('le',ref('missed_amount'),face),['missed_amount','original_face']),
                 rule('cash_nonnegative',op('le',zero,ref('cash')),['cash']),
                 rule('debt_credit',op('le',ref('debt'),zero),['debt']),
                 rule('carrying_bounded',op('le',op('sub',zero,ref('debt')),remaining),['debt','outstanding'])])
    mature=ref('matured');unmature=negate(ref('matured'));missed=ref('missed');not_missed=negate(missed)
    for n,expr,deps in [
        ('unmatured_claim_is_face',op('eq',remaining,face),['outstanding','original_face']),
        ('unmatured_by_due',op('le',ref('as_of'),ref('due')),['as_of','due']),
        ('unmatured_not_missed',op('eq',missed,const(core.BOOL,False)),['missed'])]:
        rows.append(rule(n,expr,deps,unmature,['matured']))
    rows.extend([rule('maturity_date',op('le',ref('due'),ref('as_of')),['due','as_of'],mature,['matured']),
                 rule('mature_carrying_equals_claim',op('eq',ref('debt'),op('sub',zero,remaining)),['debt','outstanding'],mature,['matured'])])
    for n in ['arrears','missed_amount']:
        rows.append(rule('not_missed_'+n,op('eq',ref(n),zero),[n],not_missed,['missed']))
    for n,expr,deps in [
        ('missed_requires_maturity',op('eq',mature,const(core.BOOL,True)),['matured']),
        ('missed_after_due',op('lt',ref('due'),ref('as_of')),['due','as_of']),
        ('positive_historical_miss',op('lt',zero,ref('missed_amount')),['missed_amount']),
        ('remaining_bounded_by_miss',op('le',remaining,ref('missed_amount')),['outstanding','missed_amount']),
        ('arrears_equal_remaining',op('eq',ref('arrears'),remaining),['arrears','outstanding'])]:
        rows.append(rule(n,expr,deps,missed,['missed']))
    rows.append(rule('unpaid_after_due_requires_observation',op('eq',missed,const(core.BOOL,True)),['missed'],
      all_of(op('lt',ref('due'),ref('as_of')),op('lt',zero,remaining)),['due','as_of','outstanding']))
    snapshot=declaration('selected.financing.snapshot',bindings,rows)
    transitions={}
    for method in METHODS:
        bs={}
        for phase in ['before','after']:
            for n,t in field_types.items():bs[phase+'_'+n]=source(phase,'memory',t,pointer='/debt_terms/'+n)
            for n in ['cash','debt','capital','interest']:
                bs[phase+'_'+n]=source(phase,'balance',money,account=roles[n])
        entry=program['registry']['entries'][method]
        for n,t in entry['event_inputs'].items():
            if n!='approved':bs['event_'+n]=source('event','input',t,name=n)
        targets={n:ref('before_'+n) for n in FIELDS+['cash','debt','capital','interest']}
        if method=='mature':
            targets.update(matured=const(core.BOOL,True),debt=op('sub',zero,ref('before_original_face')),
              interest=op('add',ref('before_interest'),op('add',ref('before_original_face'),ref('before_debt'))))
        elif method=='equity':
            amount=op('mul',ref('event_shares'),ref('event_price'))
            targets.update(new_shares=op('add',ref('before_new_shares'),ref('event_shares')),
              cash=op('add',ref('before_cash'),amount),capital=op('sub',ref('before_capital'),amount))
        elif method=='observe_missed':
            targets.update(missed=const(core.BOOL,True),missed_amount=ref('before_outstanding'),arrears=ref('before_outstanding'))
        else:
            amount=ref('event_amount')
            targets.update(outstanding=op('sub',ref('before_outstanding'),amount),
              cash=op('sub',ref('before_cash'),amount),debt=op('add',ref('before_debt'),amount))
            if method=='settle_late':targets['arrears']=op('sub',ref('before_arrears'),amount)
        def refs(expr):
            if type(expr) is not dict:return set()
            if expr.get('op')=='ref':return {expr['id']}
            found=set()
            for value in expr.values():
                if type(value) is dict:found.update(refs(value))
                elif type(value) is list:
                    for item in value:found.update(refs(item))
            return found
        rows=[rule(n+'_transition',op('eq',ref('after_'+n),expr),sorted({'after_'+n}|refs(expr))) for n,expr in targets.items()]
        transitions[method]=declaration('selected.financing.'+method,bs,rows)
    result=dict(profile=PROFILE,context=deepcopy(book['context']),roles=deepcopy(roles),
      account_classes=deepcopy(book['accounts']),memory_schema=book['memory_schema'],
      memory_types=deepcopy(book['memory_types']),registry_sha256=digest(program['registry']),
      mapping_sha256=digest(program['mapping']),schemas_sha256=digest(program['schemas']),
      snapshot=snapshot,transitions=transitions,residuals=deepcopy(RESIDUALS))
    return result

def evaluate(spec,books,event=None):
    values={}
    for n,b in spec['bindings'].items():
        if b['phase']=='event':
            record=event['inputs'][b['name']];typ=record['type'];value=record['value']
        else:
            book=books[b['phase']]
            if b['kind']=='memory':
                found,raw=engine.binding.located(book['memory'],b['pointer']);core.need(found,'missing_memory_leaf')
                typ=book['memory_types'][b['pointer']]
            elif b['kind']=='balance':raw=book['balances'][b['account']];typ=engine.money_type(book)
            else:raw=book['date'];typ=DATE
            value=engine.known(deepcopy(raw))
        core.need(typ==b['type']==spec['manifest']['inputs'][n]['type'],'binding_type_mismatch:'+n)
        values[n]=deepcopy(value)
    manifest=spec['manifest'];key=digest(manifest)
    return guarded.assess({key:manifest},key,values,[])

def validate_state(contract,book,schemas):
    engine.validate_book(book,schemas)
    core.need(book['context']==contract['context'],'selected_context')
    core.need(book['accounts']==contract['account_classes'],'selected_account_classes')
    core.need(book['memory_schema']==contract['memory_schema'],'selected_memory_schema')
    core.need(book['memory_types']==contract['memory_types'],'selected_memory_types')
    core.need(book['cash_account']==contract['roles']['cash'],'selected_cash_role')
    core.need(set(book['memory']['debt_terms'])==set(FIELDS),'selected_debt_term_fields')
    return evaluate(contract['snapshot'],{'book':book})

def snapshot(contract,book,schemas):
    try:return validate_state(contract,book,schemas)
    except (ValueError,KeyError,TypeError,RecursionError,OverflowError) as exc:
        return dict(status='invalid',reason=str(exc)[:300],**FLAGS)

def transition(contract,method,before,event,after,schemas):
    try:
        core.need(method in contract['transitions'],'selected_method')
        for book in [before,after]:
            checked=validate_state(contract,book,schemas)
            if checked['status']!='requirements_satisfied':return dict(status=checked['status'],reason='snapshot',assessment=checked,**FLAGS)
        # Explicit frame: these fields are not modified by the five selected events.
        for n in ['context','period','accounts','cash_account','memory_schema','memory_types']:
            core.need(before[n]==after[n],'preserved_book_field:'+n)
        for n in before['memory']:
            if n!='debt_terms':core.need(before['memory'][n]==after['memory'][n],'preserved_memory:'+n)
        mutable={contract['roles'][n] for n in ['cash','debt','capital','interest']}
        for n in before['balances']:
            if n not in mutable:core.need(before['balances'][n]==after['balances'][n],'preserved_account:'+n)
        core.need(after['date']==event['date'],'event_date')
        core.need(after['seen']==before['seen']+[event['id']],'event_identity_history')
        core.need(after['flows'][:len(before['flows'])]==before['flows'],'preserved_cash_flow_history')
        return evaluate(contract['transitions'][method],{'before':before,'after':after},event)
    except (ValueError,KeyError,TypeError,RecursionError,OverflowError) as exc:
        return dict(status='invalid',reason=str(exc)[:300],**FLAGS)

def make_call(contract,program,history,selection):
    return dict(profile=CALL,contract_sha256=digest(contract),program_sha256=digest(program),
                program_order_sha256=ordered(program),history_sha256=digest(history),selection=selection)

def admit(contract,program,history,selection,call):
    stage='call'
    try:
        core.need(call==make_call(contract,program,history,selection),'stale_financing_call')
        core.need(selection==digest(contract),'independent_selected_contract')
        core.need(contract['profile']==PROFILE,'contract_profile')
        stage='selected_program'
        for key in ['registry','schemas','mapping']:
            core.need(digest(program[key])==contract[key+'_sha256'],'selected_'+key)
        runtime.validate(program)
        stage='snapshot';checked=validate_state(contract,program['opening'],program['schemas'])
        if checked['status']!='requirements_satisfied':return dict(status=checked['status'],failed_stage=stage,assessment=checked,**FLAGS)
        stage='opening_history'
        if history is None or history.get('status')!='complete':
            return dict(status='unresolved',failed_stage=stage,reason='complete_supplied_opening_history_required',**FLAGS)
        core.closed(history,['profile','status','book_sha256','debt_terms','provenance'],'opening_history')
        core.need(history['profile']==HISTORY,'opening_history_profile')
        engine.text(history['provenance'],'history_provenance')
        core.need(history['book_sha256']==digest(program['opening']),'history_book_binding')
        core.need(history['debt_terms']==program['opening']['memory']['debt_terms'],'opening_history_facts')
        return dict(status='selected_opening_satisfied',failed_stage=None,assessment=checked,
                    history_sha256=digest(history),**FLAGS)
    except (ValueError,KeyError,TypeError,AttributeError,RecursionError,OverflowError) as exc:
        return dict(status='invalid',failed_stage=stage,reason=str(exc)[:300],**FLAGS)

def execute(contract,program,history,selection,call):
    admission=admit(contract,program,history,selection,call)
    result=dict(profile=PROFILE,admission=admission,**FLAGS)
    if admission['status']!='selected_opening_satisfied':
        return dict(result,status=admission['status'],failed_stage=admission['failed_stage'])
    current=deepcopy(program['opening']);opening=deepcopy(current)
    trace=[];used=set(current['seen']);stop=None
    for i,command in enumerate(program['commands']):
        try:
            identity=runtime.identity(command);core.need(identity not in used,'duplicate_command_identity')
            if command['kind']=='event':
                request=runtime.call(current,program['registry'],command)
                proposed=runtime.methods.propose(current,request)
                if proposed['status']!='proposed':
                    stop=dict(index=i,status=proposed['status'],reason=proposed.get('reason','typed_transition'),diagnostic_proposal=proposed)
                    break
                after=proposed['transition']['after']
                check=transition(contract,command['method_key'],current,command['event'],after,program['schemas'])
            else:
                core.need(command['kind']=='report','selected_report_or_event_only')
                core.need(current['date']<=command['cutoff']<current['period']['end_exclusive'],'report_chronology')
                after=deepcopy(current);after['date']=command['cutoff']
                proposed=runtime.reports.report(runtime.reports.request(opening,after,program['schemas'],program['mapping'],
                                                command['equity_movements'],command['notes']))
                core.need(proposed['status']=='reported','report:'+proposed.get('reason',proposed['status']))
                check=snapshot(contract,after,program['schemas'])
            if check['status']!='requirements_satisfied':
                stop=dict(index=i,status=check['status'],reason='selected_postcondition',diagnostic_proposal=proposed,assessment=check)
                break
            entry=dict(index=i,command=deepcopy(command),before_sha256=digest(current),
                       result=proposed,assessment=check,after_sha256=digest(after))
            core.need(len(core.canonical(trace+[entry]))<=runtime.MAX_TRACE_BYTES,'trace_size_limit')
            trace.append(entry)
            current=deepcopy(after);used.add(identity)
        except (ValueError,KeyError,TypeError,RecursionError,OverflowError) as exc:
            stop=dict(index=i,status='invalid',reason=str(exc)[:300]);break
    return dict(result,status='stopped_selected_provisional' if stop else 'complete_selected_provisional',
                current=current,trace=trace,stop=stop,remaining_commands=deepcopy(program['commands'][len(trace):]))
