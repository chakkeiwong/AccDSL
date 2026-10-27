"""Reuse saved conditional histories; add explicitly chosen network relations."""
from pathlib import Path
from copy import deepcopy
import json,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import retained_network_history_v1 as adapter
BUDGET={'max_slots':4,'max_formula_nodes':10000,'max_integer_assignments':1,
        'max_cells':1,'elapsed_ms':5000,'solver_timeout_ms':1000,'solver_rlimit':1000000}

def fixture(mode='closing',map_opening=False):
    old=json.loads((ROOT/'data/accounting-master/retained-statement-history-20261025/exchanges/both_contexts.json').read_text())
    prior=old['request'];selected=list(prior['balance_request']['selected_relations'])
    selected+=prior['cash_request']['source_request']['selected_relations']
    source_request=adapter.network.fixture(selected,True)
    request=source_request['statement_request']
    if mode=='opening':
        selected += [r['id'] for r in request['relations'] if '.opening:' in r['id']]
    elif mode=='equity':
        selected += ['annual.capital','annual.retained','annual.aoci']
        selected += [r['id'] for r in request['relations'] if r['id'].startswith('annual.equity_to_balance:')]
    elif mode in ['full','numeric']:
        selected=adapter.network.supported_selection(request)
        if mode=='numeric':
            selected=adapter.network.numeric_selection(request,old['result']['balance_parent']['preserved_report'])
    else:assert mode=='closing'
    source_request=adapter.network.fixture(selected,True)
    parent=adapter.network.assess(source_request,adapter.attachment.measurement_budget(BUDGET))
    assert parent['status'] in ['conditionally_feasible','unresolved'],parent.get('reason')
    histories={}
    for group in ['annual','interim']:
        previous=old['result']['attachments'][group+'.cash_closing']['definition']
        h=deepcopy(previous['history']);bindings=deepcopy(previous['bindings'])
        context=h['value_type']['context'];key=adapter.context_key(context)
        for name,binding in bindings.items():binding['quantity']=parent['definition']['observations'][name]['type']['quantity']
        if map_opening:
            by_alias={v['aliases'][0]:k for k,v in parent['source_mapping'].items()}
            prior_alias={v['aliases'][0]:k for k,v in old['result']['balance_parent']['source_mapping'].items()}
            for alias,name in by_alias.items():
                target=None
                if alias.startswith(group+'.opening.'):
                    caption=alias.removeprefix(group+'.opening.')
                    target=group+'.balance.'+caption
                elif alias.startswith(group+'.equity.') and alias.endswith(('_opening','_closing')):
                    caption=alias.removeprefix(group+'.equity.').rsplit('_',1)[0]
                    if caption in ['capital','retained','aoci']:target=group+'.balance.'+caption
                if target in prior_alias:
                    mapping=deepcopy(previous['bindings'][prior_alias[target]])
                    mapping['quantity']=parent['definition']['observations'][name]['type']['quantity']
                    mapping['premise']={'id':'proposed_opening_caption:'+alias,'status':'proposed',
                        'meaning':'Test the explicit hypothesis that this source caption has the same population as the named synthetic balance field at its original time; not an admitted mapping.'}
                    bindings[name]=mapping
        histories[key]={'history':h,'bindings':bindings}
    return {'profile':adapter.PROFILE,'source_request':source_request,'histories':histories}
