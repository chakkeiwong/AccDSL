"""Conditional period summary with explicitly paired intragroup cash flows."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import company_book_reports_v1 as reports
import compatible_book_composition_v1 as composition

core=composition.core;engine=composition.engine
PROFILE='GroupPeriodReport/1'
FLAGS={**composition.FLAGS,'fiscal_complete':False,'notes_complete':False}
PINS={'company_book_reports_v1.py': '7418f0a6fc7169ac1b297b47891cb2f6f9075b3f2231366ea9f241589a753100', 'compatible_book_composition_v1.py': '282a7aa8072d6d3369f332b2ee19cbc85aa468b2fda4e0a4b038c258c146aa4b'}
number=composition.number;fmt=composition.fmt;total=composition.total

def prepare(body):
    for filename,h in PINS.items():
        core.need(sha256(Path(__file__).with_name(filename).read_bytes()).hexdigest()==h,'dependency_hash:'+filename)
    engine.binding.bounded(body);engine.memory.bounded(body)
    core.closed(body,['profile','opening','closing','legal_reports','internal_cash_pairs'],'group_period')
    core.need(body['profile']==PROFILE,'period_profile')
    opening=composition.compose(body['opening']);closing=composition.compose(body['closing'])
    for name,result in [('opening',opening),('closing',closing)]:
        core.need(result['status']=='worksheet_composed',name+'_worksheet:'+result.get('reason','invalid'))
    a,b=body['opening'],body['closing']
    for key in ['chart','account_maps','compatibility','control_edge_id']:
        core.need(core.canonical(a[key])==core.canonical(b[key]),'period_compatibility:'+key)
    for key in ['context','control_edges','obligations']:
        core.need(core.canonical(a['world'][key])==core.canonical(b['world'][key]),'period_world:'+key)
    core.need(set(a['books'])==set(b['books']),'period_book_population')
    for key in a['books']:
        for field in ['entity','book','currency','sector','source_ref','view_ref']:
            core.need(a['world']['books'][key][field]==b['world']['books'][key][field],'period_handle:'+field)
    core.need(type(body['legal_reports']) is dict and set(body['legal_reports'])==set(a['books']),'exact_legal_reports')
    legal={}
    for key,request in body['legal_reports'].items():
        core.need(core.canonical(request['opening'])==core.canonical(a['books'][key]),'legal_opening_binding')
        core.need(core.canonical(request['closing'])==core.canonical(b['books'][key]),'legal_closing_binding')
        result=reports.report(request)
        core.need(result['status']=='reported','legal_report:'+result.get('reason','invalid'))
        legal[key]=result
    core.need(type(body['internal_cash_pairs']) is list and len(body['internal_cash_pairs'])<=128,'cash_pair_limit')
    return opening,closing,legal

def report(body):
    try:
        opening,closing,legal=prepare(body)
        flows={};all_flows=[]
        for owner,result in legal.items():
            for flow in result['cash_flows']['gross_origins']:
                flows[(owner,flow['id'])]=flow
                all_flows.append({'owner':owner,'flow':deepcopy(flow)})
        ids=set();removed=set();pairs=[]
        for pair in body['internal_cash_pairs']:
            core.closed(pair,['id','payer','payee','premise'],'cash_pair')
            for key in ['id','premise']:composition.world.text(pair[key],'cash_pair_'+key)
            core.need(pair['id'] not in ids,'duplicate_cash_pair');ids.add(pair['id'])
            selected=[]
            for side in ['payer','payee']:
                ref=pair[side];core.closed(ref,['owner','flow_id','expected_flow_sha256'],'cash_reference')
                for field in ['owner','flow_id']:composition.world.text(ref[field],'cash_reference_'+field)
                composition.world.digest(ref['expected_flow_sha256'],'cash_reference_digest')
                key=(ref['owner'],ref['flow_id']);core.need(key in flows,'missing_cash_flow')
                core.need(key not in removed,'reused_cash_flow');removed.add(key)
                flow=flows[key];core.need(core.digest(flow)==ref['expected_flow_sha256'],'stale_cash_flow')
                selected.append(flow)
            payer,payee=selected
            core.need(pair['payer']['owner']!=pair['payee']['owner'],'cross_book_cash_pair')
            core.need(payer['date']==payee['date'],'cash_pair_date')
            core.need(payer['currency']==payee['currency'],'cash_pair_currency')
            core.need(number(payer['amount'])<0<number(payee['amount']) and total(number(f['amount']) for f in selected)==0,'opposite_full_cash_pair')
            pairs.append({**deepcopy(pair),'payer_flow':deepcopy(payer),'payee_flow':deepcopy(payee)})
        retained=[row for row in all_flows if (row['owner'],row['flow']['id']) not in removed]
        def activities(rows):
            result={}
            for activity in ['operating','investing','financing']:
                values=[number(r['flow']['amount']) for r in rows if r['flow']['activity']==activity]
                receipt=total(x for x in values if x>0);payment=-total(x for x in values if x<0)
                result[activity]={'receipts':fmt(receipt),'payments':fmt(payment),'net':fmt(receipt-payment)}
            return result
        grouped=activities(retained)
        cash0=total(number(r['cash_flows']['opening_cash']) for r in legal.values())
        cash1=total(number(r['cash_flows']['closing_cash']) for r in legal.values())
        profit=total(number(r['income']['profit']) for r in legal.values())
        movements=total(number(r['equity']['direct_movements']) for r in legal.values())
        eq0=number(opening['adjusted_totals']['equity_including_profit']);eq1=number(closing['adjusted_totals']['equity_including_profit'])
        checks={'cash':total([cash1,-cash0,-total(number(v['net']) for v in grouped.values())]),
                'profit':total([profit,-number(closing['adjusted_totals']['profit'])]),
                'equity':total([eq0,movements,profit,-eq1])}
        core.need(all(v==0 for v in checks.values()),'group_period_reconciliation')
        return {'profile':PROFILE,**FLAGS,'status':'period_reported','request_sha256':core.digest(body),
            'opening_worksheet':opening,'closing_worksheet':closing,'legal_reports':legal,
            'raw_cash_flows':{'activities':activities(all_flows),'origins':all_flows},
            'internal_cash_pairs':pairs,'cash_flows':{'activities':grouped,'origins':retained,
                'opening_cash':fmt(cash0),'closing_cash':fmt(cash1),'net_movement':fmt(cash1-cash0)},
            'equity':{'opening':fmt(eq0),'direct_movements':fmt(movements),'profit':fmt(profit),'closing':fmt(eq1)},
            'reconciliations':{k:fmt(v) for k,v in checks.items()},
            'scope':'Constructed compatible period with supplied internal transfer pairs; no complete consolidated statements',
            'unresolved':['Truth and completeness of supplied internal-transfer pairs','Source and accounting admission',
                          'Stable full-ownership scope only; no NCI, goodwill, FX, tax or intragroup profit methods',
                          'Indirect operating cash-flow bridge and complete notes'],
            'dependency_sha256':deepcopy(PINS),'implementation_sha256':sha256(Path(__file__).read_bytes()).hexdigest()}
    except Exception as exc:return {'profile':PROFILE,**FLAGS,'status':'invalid','reason':str(exc)[:350] or type(exc).__name__}

def verify(body,result):
    try:return core.canonical(report(body))==core.canonical(result)
    except Exception:return False
