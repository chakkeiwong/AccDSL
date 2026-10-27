"""Constructed typed projections and recomputed native monetary comparators."""
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import json, sys
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT/'scripts'))
import method_monetary_effects_v1 as effects
import native_return_state_structure_v1 as structure
core = effects.core


def ref(key):
    return {'op':'ref', 'id':key}


def binary(op, a, b):
    return {'op':op, 'left':a, 'right':b}


def types(context):
    def t(d):
        return {'kind':'rational', 'context':deepcopy(context), 'dimensions':d, 'scale':'1/1'}
    return t({'currency:USD':1}), t({'goods:unit':1}), t({'currency:USD':1, 'goods:unit':-1})


def program(kind, context, accounts):
    money, units, price = types(context)
    zero = {'op':'const', 'type':money, 'value':'0/1'}
    def neg(x):
        return binary('sub', deepcopy(zero), x)
    if kind == 'settle':
        declarations = {'n':units, 'p':price, 'c':price, 'd':price, 'h':price,
                        'nrv':money, 'refund_before':money, 'recovery_before':money}
        calculations = [
            ('refund', binary('mul', ref('n'), ref('p')), ['n','p']),
            ('handling', binary('mul', ref('n'), ref('h')), ['n','h']),
            ('carrying', binary('min', binary('mul', ref('n'), binary('sub',ref('c'),ref('d'))), ref('nrv')), ['n','c','d','nrv']),
            ('tax_adjustment', binary('sub',ref('recovery_before'),ref('refund_before')), ['recovery_before','refund_before'])]
        postings = [
            ('refund_liability', ref('refund_before'), ['refund_before']),
            ('recovery_asset', neg(ref('recovery_before')), ['recovery_before']),
            ('inventory', ref('carrying'), ['n','c','d','nrv']),
            ('revenue', binary('sub',ref('refund'),ref('refund_before')), ['n','p','refund_before']),
            ('cogs', binary('sub',ref('recovery_before'),ref('carrying')), ['recovery_before','n','c','d','nrv']),
            ('selling_expense', ref('handling'), ['n','h']),
            ('cash', neg(ref('refund')), ['n','p']),
            ('cash', neg(ref('handling')), ['n','h'])]
        flows = [('refund', neg(ref('refund')), ['n','p']), ('handling',neg(ref('handling')),['n','h'])]
    elif kind == 'sell':
        declarations = {'proceeds':money, 'cost':money}
        calculations = []
        postings = [('cash',ref('proceeds'),['proceeds']), ('revenue',neg(ref('proceeds')),['proceeds']),
                    ('inventory',neg(ref('cost')),['cost']), ('cogs',ref('cost'),['cost'])]
        flows = [('external_sale',ref('proceeds'),['proceeds'])]
    else:
        raise ValueError('unsupported fixture method')
    return {'profile':effects.PROFILE, 'method_id':'constructed.'+kind, 'version':'1',
            'inputs':{k:{'type':v, 'role':'state' if k in ['refund_before','recovery_before','cost'] else 'reported_measurement',
                         'source_ref':'constructed-projection:'+kind+':'+k} for k,v in declarations.items()},
            'calculations':[{'id':key,'expression':exp,'requires':deps,'type':money} for key,exp,deps in calculations],
            'accounts':{key:deepcopy(money) for key in accounts}, 'cash_account':'cash',
            'postings':[{'id':'post.'+str(i),'account':account,'expression':exp,'requires':deps}
                        for i,(account,exp,deps) in enumerate(postings)],
            'flows':[{'id':'flow.'+str(i),'activity':'operating','origin':origin,'expression':exp,'requires':deps}
                     for i,(origin,exp,deps) in enumerate(flows)]}


def project(state, event):
    # This is a declared test projection, not a source-admission adapter.
    if event['kind'] == 'settle':
        c=state['component']
        raw={'n':event['actual_units'],'p':c['unit_refund'],'c':c['unit_cost'],
             'd':event['unit_deterioration'],'h':event['unit_handling'],'nrv':event['inventory_nrv'],
             'refund_before':c['refund'],'recovery_before':c['recovery']}
    else:
        raw={'proceeds':event['proceeds'],'cost':state['lots'][event['lot_id']]['carrying']}
    return {k:({'status':'unknown','reason':'native_input_unknown:'+k} if v=='unknown'
               else {'status':'known','value':v}) for k,v in raw.items()}


def run(definition, values):
    h=core.digest(definition)
    return effects.derive({h:definition},h,values)


def selected_cases():
    rows=json.loads((HERE.parent/'company-return-execution-20261024/trace.json').read_text())['trace']
    selected=[]
    for index,row in enumerate(rows):
        if row['event']['kind'] not in ['settle','sell']:
            continue
        assert index>0
        state=rows[index-1]['proposal']['after']
        selected.append((row['event']['kind']+'.retained',deepcopy(state),deepcopy(row['event'])))
    name,s,e=selected[0]
    for label,edits in [('nrv_cap',{'inventory_nrv':'5/1'}),('zero_nrv',{'inventory_nrv':'0/1'}),
                        ('zero_handling',{'unit_handling':'0/1','handling_cash':'0/1'}),
                        ('fractional',{'actual_units':'1/3','refund_cash':'20/3','handling_cash':'4/3'}),
                        ('unknown_nrv',{'inventory_nrv':'unknown'})]:
        event=deepcopy(e);event.update(edits)
        selected.append(('settle.'+label,deepcopy(s),event))
    state=deepcopy(s);state['tax_premises']['rate_enacted']='unknown'
    selected.append(('settle.unused_tax_unknown',state,deepcopy(e)))
    name,s,e=selected[1]
    for label,value in [('zero_proceeds','0/1'),('fractional_proceeds','7/3')]:
        event=deepcopy(e);event['proceeds']=value
        selected.append(('sell.'+label,deepcopy(s),event))
    return selected


def comparisons():
    result=[]
    for name,state,event in selected_cases():
        original=deepcopy((state,event))
        context={'entity':state['context']['entity'],'book_role':'retained-conditional-example',
                 'at':event['date']}
        definition=program(event['kind'],context,structure.native.ACCOUNTS)
        values=project(state,event);answer=run(definition,values)
        try:
            after,journal,flows=structure.native.transition(state,event)
            native={'status':'derived','journal':journal,
                    'flows':[{k:f[k] for k in ['activity','origin','amount']} for f in flows]}
            observed=[{k:f[k] for k in ['activity','origin','amount']} for f in answer.get('flows',[])]
            passed=answer['status']=='derived' and answer['journal']==journal and observed==native['flows']
            if event['kind']=='settle':
                amounts={x['id']:x['binding']['value'] for x in answer['diagnostics']['calculations']}
                passed=passed and amounts['carrying']==after['lots'][event['lot_id']]['carrying']
                passed=passed and amounts['tax_adjustment']==after['tax_adjustments'][-1]['amount']
        except structure.native.Rejected as exc:
            native={'status':exc.status,'reason':exc.reason}
            passed=answer['status']==exc.status
        result.append({'case':name,'before_sha256':core.digest(state),'event_sha256':core.digest(event),
                       'definition':definition,'values':values,'derived':answer,'native':native,
                       'passed':passed and (state,event)==original,
                       'provenance':'constructed typed projection of retained conditional state/event; not filing bytes'})
    return result
