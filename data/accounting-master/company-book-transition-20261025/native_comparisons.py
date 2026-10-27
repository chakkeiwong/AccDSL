"""Test-only reversible projections, not general native method admission."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module


ex=load('book_comparison_examples','data/accounting-master/company-book-transition-20261025/examples.py')
engine=ex.engine
prior=load('book_prior_monetary','data/accounting-master/typed-monetary-effects-20261024/examples.py')
tax=load('book_prior_payment','data/accounting-master/shared-tax-continuation-20261024/examples.py')


def native_classes(native):
    return {**{k:'asset' for k in native.ASSETS},**{k:'liability' for k in native.LIABILITIES},
            **{k:'equity' for k in native.EQUITY},**{k:('income' if k=='revenue' else 'expense') for k in native.INCOME}}


def prefix_flows(state,book):
    return [{**deepcopy(row),'id':engine.digest(['native-prefix',i,row]),
             'book':book['context']['book'],'currency':book['context']['currency']}
            for i,row in enumerate(state['flows'])]


def export_native(capsule,after,lot_id=None):
    # Preserve the exact captured complement; only declared mapped fields change.
    result=deepcopy(capsule)
    for key in ['balances','date','seen']:result[key]=deepcopy(after[key])
    result['flows']=[{k:v for k,v in row.items() if k not in ['id','book','currency']} for row in after['flows']]
    if lot_id is not None:result['lots'][lot_id]=deepcopy(after['memory']['selected_lot'])
    return result


def payment_projection(state,operation):
    book,request=ex.fixture(amount=operation['event']['amount'])
    # Recontextualize every typed node explicitly; no native invariant is changed.
    context={**deepcopy(state['context']),'book':state['context']['book_role'],'mode':'synthetic'}
    context.pop('book_role');context={k:context[k] for k in ['entity','book','currency','case_id','mode']}
    old=engine.type_context(book);new={k:v for k,v in context.items() if k!='currency'}
    def replace(value):
        if type(value) is dict:
            if value.get('kind')=='rational' and value.get('context')==old:value['context']=deepcopy(new)
            for child in value.values():replace(child)
        elif type(value) is list:
            for child in value:replace(child)
    replace(book);replace(request)
    book['context']=context;request['method']['context']=deepcopy(context)
    classes=native_classes(prior.structure.native)
    classes.update(rou='asset',lease_liability='liability',other_gains='income',income_tax_payable='liability')
    assert set(classes)==set(state['balances'])
    book.update(accounts={k:{'classification':classes[k]} for k in state['balances']},
                balances=deepcopy(state['balances']),cash_account='cash',period=deepcopy(state['period']),
                date=state['date'],seen=deepcopy(state['seen']))
    book['flows']=prefix_flows(state,book)
    outstanding=engine.monetary.fmt(-Q(state['balances']['income_tax_payable']))
    book['memory']['loan'].update(outstanding=outstanding,last_date=state['date'])
    request['method']['account_map']={'cash':'cash','liability':'income_tax_payable'}
    request['method']['monetary']['definition']['flows'][0].update(activity='operating',origin='explicit_conditional_current_tax_payment')
    event=operation['event'];request['event'].update(id=event['id'],date=event['date'])
    finding=event['authorization'];request['event']['inputs']['approved']['value']={k:v for k,v in finding.items() if k!='provenance'}
    ex.rehash(book,request)
    return book,request


def sale_projection(state,event):
    native=prior.structure.native;native.invariant(state)
    assert len(state['lots'])==1 and event['fraction']=='1/1'
    lot=deepcopy(state['lots'][event['lot_id']]);classes=native_classes(native)
    context={'entity':state['context']['entity'],'book':state['context']['book_role'],
             'currency':state['context']['currency'],'case_id':state['context']['case_id'],'mode':'synthetic'}
    book={'profile':engine.BOOK,'context':context,'period':deepcopy(state['period']),'date':state['date'],
          'accounts':{k:{'classification':classes[k]} for k in state['balances']},'balances':deepcopy(state['balances']),
          'cash_account':'cash','seen':deepcopy(state['seen'])}
    money=engine.money_type(book);units={**deepcopy(money),'dimensions':{'goods:unit':1}}
    scalar_types={'id':{'kind':'text','context':{}},'component_id':{'kind':'text','context':{}},
                  'units':units,'carrying':money,'tax_base':money,'acquired':{'kind':'date','context':{}},'disposed':engine.core.BOOL}
    shape=ex.record({'selected_lot':ex.record({k:ex.scalar(t['kind']) for k,t in scalar_types.items()}),
                     'other_inventory':ex.scalar('rational'),'tax_closed_until':ex.scalar('date')})
    book.update(memory_schema=engine.digest(shape),memory={'selected_lot':lot,'other_inventory':state['other_inventory'],'tax_closed_until':state['tax_closed_until']},
                memory_types={**{'/selected_lot/'+k:deepcopy(t) for k,t in scalar_types.items()},
                              '/other_inventory':deepcopy(money),'/tax_closed_until':{'kind':'date','context':{}}})
    book['flows']=prefix_flows(state,book)
    identity='constructed.sell';zero=ex.const(money,'0/1');day={'kind':'date','context':{}}
    types={'inventory':money,'cost':money,'other':money,'proceeds':money,'disposed':engine.core.BOOL,
           'complete':engine.core.BOOL,'closed_until':day,'event_date':day}
    pre=ex.conditions(identity,types,[
        ('inventory',ex.binary('eq',ex.ref('inventory'),ex.binary('add',ex.ref('cost'),ex.ref('other'))),['inventory','cost','other'],'invalid'),
        ('proceeds',ex.binary('le',zero,ex.ref('proceeds')),['proceeds'],'invalid'),
        ('live',{'op':'not','arg':ex.ref('disposed')},['disposed'],'invalid'),
        ('performance',ex.ref('complete'),['complete'],'unsupported'),
        ('clock',ex.binary('le',ex.ref('closed_until'),ex.ref('event_date')),['closed_until','event_date'],'invalid')])
    post=ex.conditions(identity,{'inventory':money,'cost':money,'other':money},[
        ('inventory',ex.binary('eq',ex.ref('inventory'),ex.binary('add',ex.ref('cost'),ex.ref('other'))),['inventory','cost','other'],'invalid')])
    amounts=prior.program('sell',engine.type_context(book),['cash','inventory','revenue','cogs'])
    inputs=ex.record({});input_hash=engine.digest(inputs)
    operations=[{'id':key,'op':'replace','path':['selected_lot',key],
                 'value':{'kind':'literal','value':True if key=='disposed' else '0/1'}} for key in ['units','carrying','tax_base','disposed']]
    bindings={'inventory':ex.account('inventory'),'cost':ex.mem('/selected_lot/carrying'),'other':ex.mem('/other_inventory'),
              'proceeds':ex.event('proceeds'),'disposed':ex.mem('/selected_lot/disposed'),'complete':ex.event('complete'),
              'closed_until':ex.mem('/tax_closed_until'),'event_date':ex.event('event_date')}
    method={'profile':engine.METHOD,'id':identity,'version':'1','context':deepcopy(context),
            'account_map':{k:k for k in amounts['accounts']},
            'preconditions':{'manifest':pre,'bindings':bindings},
            'postconditions':{'manifest':post,'bindings':{k:bindings[k] for k in ['inventory','cost','other']}},
            'monetary':{'definition':amounts,'bindings':{'cost':bindings['cost'],'proceeds':bindings['proceeds']}},
            'memory':{'definition':{'profile':engine.memory.PROFILE,'state_schema':book['memory_schema'],
                                   'input_schema':input_hash,'operations':operations},'input_bindings':{}},
            'residual_prerequisites':['Test-only projection; native invariant and source complement remain explicit.']}
    values={'proceeds':(money,event['proceeds']),'complete':(engine.core.BOOL,event['performance_complete']),'event_date':(day,event['date'])}
    request={'profile':engine.PROFILE,'method':method,'event':{'id':event['id'],'date':event['date'],
             'inputs':{k:{'type':deepcopy(t),'value':engine.known(v),'provenance':'Explicit projection from retained synthetic event'} for k,(t,v) in values.items()}},
             'schemas':{book['memory_schema']:shape,input_hash:inputs}}
    ex.rehash(book,request);return book,request


def comparisons():
    rows=[]
    origin=tax.origin();seed=tax.m.run(tax.m.request(origin,[]));assert seed['status']=='complete'
    for amount in ['1/4','1/2']:
        before=deepcopy(seed['after']);operation=tax.payment(amount)
        expected=tax.m.transition(before,operation,origin['assessed_until'])
        book,request=payment_projection(before,operation);result=engine.propose(book,request)
        assert result['status']=='proposed',result
        restored=export_native(before,result['after']);tax.m.invariant(restored)
        report=tax.m.statements(restored,seed['native_report'])
        checks={'complete_native_state':restored==expected['after'], 'complete_journal':result['journal']==expected['journal'],
                'complete_new_flows':restored['flows'][len(before['flows']):]==expected['flows'],
                'complete_native_report':report==tax.m.statements(expected['after'],seed['native_report']),
                'cash_arithmetic':Q(restored['balances']['cash'])==Q(before['balances']['cash'])-Q(amount),
                'liability_arithmetic':Q(restored['balances']['income_tax_payable'])==Q(before['balances']['income_tax_payable'])+Q(amount),
                'provisional_apply':engine.apply(book,request,result)['status']=='applied_provisional'}
        rows.append({'case':'native_payment.'+amount,'checks':checks,'book':book,'request':request,'proposal':result,
                     'native_before':before,'native_expected':expected,'native_restored':restored,'report':report})
    for name,before,event in prior.selected_cases():
        if event['kind']!='sell':continue
        expected,journal,flows=prior.structure.native.transition(before,event)
        book,request=sale_projection(before,event);result=engine.propose(book,request)
        assert result['status']=='proposed',result
        restored=export_native(before,result['after'],event['lot_id']);prior.structure.native.invariant(restored)
        checks={'complete_native_state':restored==expected,'complete_journal':result['journal']==journal,
                'complete_new_flows':restored['flows'][len(before['flows']):]==flows,
                'cash_arithmetic':Q(restored['balances']['cash'])==Q(before['balances']['cash'])+Q(event['proceeds']),
                'inventory_arithmetic':Q(restored['balances']['inventory'])==Q(before['balances']['inventory'])-Q(before['lots'][event['lot_id']]['carrying']),
                'lot_depletion':all(restored['lots'][event['lot_id']][k]=='0/1' for k in ['units','carrying','tax_base']),
                'provisional_apply':engine.apply(book,request,result)['status']=='applied_provisional'}
        rows.append({'case':name,'checks':checks,'book':book,'request':request,'proposal':result,
                     'native_before':before,'native_expected':expected,'native_restored':restored})
    return rows


if __name__=='__main__':
    import json
    rows=comparisons();(HERE/'native-comparisons.json').write_text(json.dumps(rows,indent=2)+'\n')
    checks=[(r['case'],k) for r in rows for k,v in r['checks'].items() if not v]
    print(json.dumps({'cases':len(rows),'comparisons':sum(len(r['checks']) for r in rows),'failures':checks}))
    raise SystemExit(bool(checks))
