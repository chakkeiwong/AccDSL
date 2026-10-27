"""Authored reverse-event construction; source captions are never legal accounts."""
from pathlib import Path
from copy import deepcopy
from fractions import Fraction as Q
import importlib.util,sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import retained_statement_history_v1 as adapter
spec=importlib.util.spec_from_file_location('source_cash_examples_for_statements',ROOT/'data/accounting-master/retained-source-history-20261025/examples.py')
cash_examples=importlib.util.module_from_spec(spec);spec.loader.exec_module(cash_examples)
BUDGET=cash_examples.BUDGET;attachment=adapter.attachment;rat=cash_examples.rat
ASSETS=['cash','securities_current','receivables','vendor_receivables','inventory',
        'other_assets_current','securities_noncurrent','ppe','other_assets_noncurrent']
LIABILITIES=['payables','other_liabilities_current','deferred_revenue','commercial_paper',
             'debt_current','debt_noncurrent','other_liabilities_noncurrent']
EQUITY=['capital','retained','aoci']

def values(report,alias):
    amount=report['observations'][alias]['observation']['record']['body']['value']['amount']
    return Q(int(amount['n']),int(amount['d']))

def balance_request(cash_request,selection=None):
    group=cash_request['source_request']['selected_relations'][0].split('.')[0]
    selected=list(selection or [k for k in adapter.balance.SUPPORTED if k.startswith(group+'.')])
    return {'profile':adapter.balance.PROFILE,'statement_request':deepcopy(cash_request['source_request']['statement_request']),
        'selected_relations':selected,'rounding_hypothesis':adapter.balance.rounding_hypothesis(),
        'identity_hypotheses':{k:adapter.balance.identity_hypothesis(k) for k in selected}}

def snapshot_binding(obs,terms,context,group):
    return {'kind':'snapshot','quantity':obs['type']['quantity'],
        'terms':[{'kind':'account','field':name,'coefficient':cash_examples.coefficient(coef,context)} for name,coef in terms.items()],
        'premise':cash_examples.premise('source_caption_mapping:'+group,
            'Signed synthetic accounts represent the selected reported caption amounts for this conditional test only; no legal-chart or accounting admission.') }

def fixture(group='annual',conflicting=False):
    key=group+'.cash_closing';c=cash_examples.fixture([key]);b=balance_request(c,[group+'.balance:equity'] if conflicting else None)
    parent=adapter.balance.assess(b,attachment.measurement_budget(BUDGET))
    assert parent['status']=='conditionally_feasible',parent.get('reason')
    obs=adapter.convert_snapshots(parent);context=c['histories'][key]['history']['value_type']['context']
    aliases={k:v['aliases'][0] for k,v in parent['source_mapping'].items()}
    if conflicting:
        chosen=next(k for k,a in aliases.items() if a==group+'.balance.equity')
        return {'profile':adapter.PROFILE,'cash_request':c,'balance_request':b,
                'balance_bindings':{key:{chosen:snapshot_binding(obs[chosen],{'Capital':-1},context,group)}}}
    report=parent['preserved_report'];h=c['histories'][key]['history'];prefix=group+'.balance.'
    cash_open=values(report,group+'.cash_flow.opening');cash_close=values(report,group+'.cash_flow.closing')
    change=cash_close-cash_open
    signed={name:values(report,prefix+name)*(1 if name in ASSETS else -1) for name in ASSETS+LIABILITIES+EQUITY}
    assert sum(signed.values(),Q(0))==0,'explicit_source_leaf_sum'
    opening=deepcopy(signed);opening['cash']=cash_open
    # Invert the declared net contribution/distribution, not an unspecified residual.
    opening['capital']=signed['capital']+change
    assert sum(opening.values(),Q(0))==0
    h['accounts']={name:cash_examples.domain(value) for name,value in opening.items()}
    def coef(value):return cash_examples.coefficient(value,context)
    money=h['value_type'];first=h['dates'][0];last=h['dates'][-1]
    h['scope']['name']='hypothetical_source_caption_history:'+group
    h['scope']['exclusions']=['actual legal accounts and transactions','unselected statements and notes','cash classifications and accounting compliance']
    h['templates']={
        'contribution':{'event_type':deepcopy(money),'postings':{'cash':coef(1),'capital':coef(-1)},'memory':{},
            'premise':cash_examples.premise('contribution','Hypothetical cash capital contribution; no actual event asserted.'),'provenance':'constructed:contribution'},
        'distribution':{'event_type':deepcopy(money),'postings':{'cash':coef(-1),'capital':coef(1)},'memory':{},
            'premise':cash_examples.premise('capital_distribution','Hypothetical cash return of capital; no legal eligibility asserted.'),'provenance':'constructed:capital_distribution'}}
    h['events']=[{'id':'contribution','date':first,'template':'contribution','amount':cash_examples.domain(0,2000)},
                 {'id':'distribution','date':last,'template':'distribution','amount':cash_examples.domain(0,2000)}]
    h['measurements'][0]['terms'][0]['field']='cash'
    h['balance_premise']=cash_examples.premise('reverse_event_opening:'+group,
        'Closing leaf captions have explicit signed representations. Opening cash is the selected cash-statement amount; opening capital reverses the supplied net capital event, while all other leaf balances are assumed unchanged. This is not disclosed opening capital.')
    for binding in c['histories'][key]['bindings'].values():binding['terms'][0]['field']='cash'
    totals={name:{name:Q(1 if name in ASSETS else -1)} for name in signed}
    # The selected source equations determine only explicit caption sums.
    equations=[r for r in b['statement_request']['relations'] if r['id'] in b['selected_relations']]
    for row in equations:
        right=row['rhs'][0]['alias'].removeprefix(prefix)
        if right in totals:continue
        terms={}
        for source_term in row['lhs']:
            name=source_term['alias'].removeprefix(prefix)
            for leaf,value in totals[name].items():terms[leaf]=terms.get(leaf,Q(0))+Q(source_term['coefficient'])*value
        totals[right]=terms
    bindings={k:snapshot_binding(obs[k],totals[alias.removeprefix(prefix)],context,group) for k,alias in aliases.items()}
    return {'profile':adapter.PROFILE,'cash_request':c,'balance_request':b,'balance_bindings':{key:bindings}}

def witness(definition,extra=0):
    h=definition['history'];key=attachment.key;identify=attachment.history.identifier
    out={key('history',identify('opening_account',name)):row['interval']['lower'] for name,row in h['accounts'].items()}
    relation=definition['measurements']['relations'][0]
    opening=Q(h['accounts']['cash']['interval']['lower'])
    terminal=definition['measurements']['observations'][relation['closing']]['interval']
    closing=(Q(terminal['lower'])+Q(terminal['upper']))/2;change=closing-opening
    contribution=max(change,Q(0))+extra;distribution=max(-change,Q(0))+extra
    out[key('history',identify('event_amount','contribution'))]=rat(contribution)
    out[key('history',identify('event_amount','distribution'))]=rat(distribution)
    state={name:Q(row['interval']['lower']) for name,row in h['accounts'].items()}
    state['cash']+=change;state['capital']-=change
    for name,binding in definition['bindings'].items():
        typ=definition['measurements']['observations'][name]['type']
        if binding['kind']=='movement':value=change
        else:
            current=state if typ['time']['at']==h['dates'][-1] else {k:Q(v['interval']['lower']) for k,v in h['accounts'].items()}
            value=sum(Q(t['coefficient']['value'])*current[t['field']] for t in binding['terms'])
        out[key('measurement',name)]=rat(value)
    return out

def combined_fixture():
    annual=fixture('annual');interim=fixture('interim');result=deepcopy(annual)
    result['cash_request']['histories'].update(interim['cash_request']['histories'])
    a=result['cash_request']['source_request'];b=interim['cash_request']['source_request']
    a['selected_relations']+=b['selected_relations']
    for field in ['identity_hypotheses','mapping_hypotheses']:a[field].update(b[field])
    result['balance_request']['selected_relations']+=interim['balance_request']['selected_relations']
    result['balance_request']['identity_hypotheses'].update(interim['balance_request']['identity_hypotheses'])
    result['balance_bindings'].update(interim['balance_bindings'])
    return result
