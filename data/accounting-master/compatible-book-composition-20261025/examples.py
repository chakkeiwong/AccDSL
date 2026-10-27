"""Constructed paired books; independent expectations are literal fixture data."""
from copy import deepcopy
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'scripts'))
import compatible_book_composition_v1 as composition

EXPECTED_RAW={'cash':'150/1','investment':'100/1','receivable':'20/1','equipment':'50/1','payable':'-20/1','capital':'-300/1'}
EXPECTED_DELTAS={'cash':'0/1','investment':'-100/1','receivable':'-20/1','equipment':'0/1','payable':'20/1','capital':'100/1'}
EXPECTED_ADJUSTED={'cash':'150/1','investment':'0/1','receivable':'0/1','equipment':'50/1','payable':'0/1','capital':'-200/1'}

def fixture(chart_name='named'):
    shape={'type':'object','properties':{'origin':{'enum':['P-state','S-state']}},'required':['origin'],'additionalProperties':False}
    h=composition.core.digest(shape)
    classes={'cash':'asset','investment':'asset','receivable':'asset','equipment':'asset','payable':'liability','capital':'equity'}
    balances={'P':{'cash':'80/1','investment':'100/1','receivable':'20/1','capital':'-200/1'},
              'S':{'cash':'70/1','equipment':'50/1','payable':'-20/1','capital':'-100/1'}}
    books={};maps={};handles={};components={}
    for owner,amounts in balances.items():
        names={role:(owner+'.'+role if chart_name=='named' else owner+'.'+str(i+101)) for i,role in enumerate(amounts)}
        context={'entity':owner,'book':'legal','currency':'USD','case_id':'constructed-paired-books','mode':'synthetic'}
        book={'profile':composition.engine.BOOK,'context':context,'period':{'start':'2025-01-01','end_exclusive':'2026-01-01'},
              'date':'2025-12-31','accounts':{names[k]:{'classification':classes[k]} for k in amounts},
              'balances':{names[k]:v for k,v in amounts.items()},'cash_account':names['cash'],
              'memory_schema':h,'memory_types':{'/origin':{'kind':'text','context':{}}},'memory':{'origin':owner+'-state'},
              'seen':[owner+'-constructed-opening'],'flows':[]}
        books[owner]=book;maps[owner]={v:k for k,v in names.items()}
        handles[owner]={'entity':owner,'book':'legal','currency':'USD','sector':'corporate',
                        'state_ref':composition.core.digest(book),
                        'source_ref':composition.core.digest(['constructed-source',owner]),
                        'view_ref':composition.core.digest(['constructed-view',owner])}
        components[owner]={'owner':owner,'sector':'corporate','profile':'CompanyComposition/1','status':'conditional',
                            'obligation_ids':[],**{k:handles[owner][k] for k in ['state_ref','source_ref','view_ref']}}
    premise='Constructed example assumes P controls and fully owns S at the snapshot'
    w={'profile':composition.world.PROFILE,'context':{'world_id':'constructed-group','currency':'USD','calendar':'gregorian',
         'case_id':'constructed-paired-books','mode':'synthetic'},'books':handles,'components':components,'obligations':[],
       'control_edges':[{'id':'P-S','parent':'P','child':'S','ownership_fraction':'1/1','start':'2025-01-01',
                        'end_exclusive':'2026-01-01','control_premise':premise}]}
    def ref(owner,role):
        account=next(k for k,v in maps[owner].items() if v==role)
        return {'owner':owner,'account':account,'expected_balance':books[owner]['balances'][account]}
    eliminations=[{'id':'reciprocal','kind':'receivable_payable','positive':ref('P','receivable'),'negative':ref('S','payable'),
                   'premise':'Supplied matching principal20; same counterparties/date; no interest or impairment'},
                  {'id':'investment','kind':'investment_equity','positive':ref('P','investment'),'negative':ref('S','capital'),
                   'premise':'Supplied cost100 equals S capital100; no goodwill, NCI or acquisition adjustments'}]
    return {'profile':composition.PROFILE,'world':w,'books':books,'schemas':{h:shape},
            'chart':{k:{'classification':v} for k,v in classes.items()},'account_maps':maps,'eliminations':eliminations,
            'control_edge_id':'P-S','compatibility':{'measurement_basis':'Supplied same basis; USD units, not thousands',
            'accounting_policies':'Supplied identical policies for this constructed snapshot','full_ownership_premise':premise,
            'elimination_scope':'Only the two declared full-balance pairs; completeness is not assessed'}}

def rehash(body):
    for owner,book in body['books'].items():
        h=composition.core.digest(book);body['world']['books'][owner]['state_ref']=h
        body['world']['components'][owner]['state_ref']=h

def cases():
    output={}
    for chart in ['named','numbered']:
        request=fixture(chart);before=deepcopy(request);result=composition.compose(request)
        assert result['status']=='worksheet_composed',result
        assert request==before and result['books']==request['books']
        for key,expected in [('raw_balances',EXPECTED_RAW),('elimination_deltas',EXPECTED_DELTAS),('adjusted_balances',EXPECTED_ADJUSTED)]:
            assert result[key]==expected,(chart,key)
        assert result['raw_totals']=={'assets':'320/1','liabilities':'20/1','equity_including_profit':'300/1','profit':'0/1','balance_check':'0/1'}
        assert result['adjusted_totals']=={'assets':'200/1','liabilities':'0/1','equity_including_profit':'200/1','profit':'0/1','balance_check':'0/1'}
        assert composition.verify(request,result)
        output[chart]={'request':request,'result':result}
    return output
