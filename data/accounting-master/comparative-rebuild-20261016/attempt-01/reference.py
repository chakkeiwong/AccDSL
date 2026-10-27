"""Reconstruct a fixed comparative profile with explicit edition/time binding."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
LOCK=json.loads((OUT/'input-lock-v2.json').read_text())['files']
FIXTURE='data/accounting-master/p17-completion-20261014/P17-04/error-estimate/fixture.json'
CATALOG='data/accounting-master/comparative-rebuild-20261016/synthetic-editions-v2.json'
TRUE_FINDINGS={'authority_profile_admitted','original_information_reliable',
    'information_available_at_authorization','reasonably_obtainable','original_misapplication',
    'material_error','fully_practicable','no_hindsight','tax_facts_admitted'}
EPS_FINDINGS={'public_shares','public_filing','voluntary_eps'}
POSITION=('cash','ppe','current_payable','dtl','equity')


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def day(value):
    need(isinstance(value,str),'date_encoding')
    try:d=date.fromisoformat(value)
    except ValueError:raise Refusal('rejected','date_encoding')
    need(d.isoformat()==value,'date_encoding');return d


def encode(value):
    if isinstance(value,Q):return str(value)
    if isinstance(value,dict):return {k:encode(v) for k,v in value.items()}
    if isinstance(value,list):return [encode(v) for v in value]
    return value


def annual_path(inputs,corrected,through):
    # Reconstruct from inputs; expected arrays and the monthly comparator are never consumed.
    capital=Q(inputs['capital']);cost=Q(inputs['cost']);income=Q(inputs['annual_cash_income'])
    life=Q(inputs['correct_life_months'] if corrected else inputs['old_life_months'])
    dep=(cost-Q(inputs['residual']))*12/life
    deduction=Q(inputs['tax_deduction']);rate=Q(inputs['tax_rate'])
    cash=capital;ppe=Q(0);taxbase=Q(0);dtl=Q(0);payable=Q(0);equity=capital
    rows={};flows={}
    for year in range(2023,through+1):
        opening_cash=cash;opening_dtl=dtl;opening_payable=payable;opening_equity=equity
        investing=-cost if year==2023 else Q(0)
        if year==2023:ppe=cost;taxbase=cost
        cash+=income-opening_payable+investing
        ppe-=dep;taxbase-=deduction
        pretax=income-dep;current=(income-deduction)*rate
        dtl=(ppe-taxbase)*rate;deferred=dtl-opening_dtl
        need(ppe>=0 and taxbase>=0 and dtl>=0,'different_asset_tax_method','unsupported')
        net=pretax-current-deferred;equity+=net;payable=current
        row=dict(depreciation=dep,ppe=ppe,tax_base=taxbase,dtl=dtl,pretax_profit=pretax,
                 current_tax=current,deferred_expense=deferred,net_profit=net,cash=cash,
                 current_payable=payable,equity=equity)
        need(cash+ppe==payable+dtl+equity,'balance_sheet_bridge')
        indirect=net+dep+deferred+(payable-opening_payable)
        direct=income-opening_payable
        need(indirect==direct,'operating_cash_bridge')
        need(cash-opening_cash==direct+investing,'cash_rollforward')
        rows[str(year)]=row
        flows[str(year)]=dict(opening_cash=opening_cash,cash_receipts=income,tax_paid=opening_payable,
            operating_direct=direct,operating_indirect=indirect,investing=investing,financing=Q(0),
            closing_cash=cash,opening_equity=opening_equity,profit=net,closing_equity=equity)
    return rows,flows


def calculate(request,resolve_bytes=None):
    result=dict(wire='ComparativeRestatement/1',status='rejected',reason=None,
                selected_edition=None,report=None,mutations=[])
    try:
        need(isinstance(request,dict) and set(request)=={'wire','operation','context','selector','public_cutoff','system_cutoff','findings'},'request_shape')
        need(request['wire']=='ComparativeRestatement/1' and request['operation']=='report','report_only')
        pubcut,syscut=day(request['public_cutoff']),day(request['system_cutoff'])
        reader=resolve_bytes or (lambda p:p.read_bytes());payloads={}
        for item in LOCK:
            try:payload=reader(ROOT/item['path'])
            except OSError:raise Refusal('unresolved','input_bytes_missing')
            need(isinstance(payload,bytes),'input_bytes_type')
            need(hashlib.sha256(payload).hexdigest()==item['sha256'],'input_bytes_changed')
            payloads[item['path']]=payload
        fixture=json.loads(payloads[FIXTURE]);catalog=json.loads(payloads[CATALOG])
        need(request['context']==catalog['context'],'context_mismatch')
        selector=request['selector']
        need(isinstance(selector,dict) and set(selector)=={'mode','year','edition'},'selector_shape')
        mode=selector['mode'];year=selector['year'];edition=selector['edition']
        need(mode in ('edition','latest_available'),'selection_method','unsupported')
        need(type(year) is int and year in (2023,2024,2025),'year_profile','unsupported')
        need((mode=='edition' and isinstance(edition,str) and bool(edition)) or
             (mode=='latest_available' and edition is None),'selector_identity')
        f=request['findings'];fields=TRUE_FINDINGS|EPS_FINDINGS|{'material_earliest_opening_effect'}
        need(isinstance(f,dict) and set(f)==fields,'findings_shape')
        for key in sorted(fields):need(f[key] is None or type(f[key]) is bool,'finding_type')
        # Validate immutable authored chronology; public and knowledge times remain independent cutoffs.
        for item in catalog['editions']:
            need(day(item['authorized'])<=day(item['published'])<=day(item['ingested']),'edition_chronology')
            need(item['context']==catalog['context'],'edition_context')
        if mode=='edition':
            matches=[x for x in catalog['editions'] if x['id']==edition]
            need(len(matches)==1,'edition_unknown')
            need(year in matches[0]['years'],'edition_year_mismatch')
        else:matches=[x for x in catalog['editions'] if year in x['years']]
        admitted=[x for x in matches if day(x['published'])<=pubcut and day(x['ingested'])<=syscut]
        need(bool(admitted),'no_available_edition','unresolved')
        selected=max(admitted,key=lambda x:(day(x['published']),day(x['ingested']),x['id']))
        for key in EPS_FINDINGS:
            need(f[key] is not None,'missing_'+key,'unresolved')
            need(f[key] is False,'eps_profile_required','unsupported')
        need(f['authority_profile_admitted'] is not None,'missing_authority_profile_admitted','unresolved')
        need(f['authority_profile_admitted'] is True,'finding_authority_profile_admitted','unsupported')
        need(f['tax_facts_admitted'] is not None,'missing_tax_facts_admitted','unresolved')
        need(f['tax_facts_admitted'] is True,'finding_tax_facts_admitted','unsupported')
        corrected=selected['kind']=='restated'
        if corrected:
            for key in sorted(TRUE_FINDINGS):
                need(f[key] is not None,'missing_'+key,'unresolved')
                need(f[key] is True,'finding_'+key,'unsupported')
            need(f['material_earliest_opening_effect'] is not None,'missing_material_earliest_opening_effect','unresolved')
            need(day(catalog['discovery'])>day(fixture['authorization']['2024']),'prior_error_timing')
            need(day(catalog['discovery'])<=day(catalog['correction_accepted'])<=day(selected['authorized']),'correction_chronology')
            need(day(catalog['correction_accepted'])<=syscut,'correction_unknown','unresolved')
        original,original_flows=annual_path(fixture['inputs'],False,selected['current_year'])
        rows,flows=annual_path(fixture['inputs'],corrected,selected['current_year'])
        presented={str(y):rows[str(y)] for y in selected['years']}
        presented_flows={str(y):flows[str(y)] for y in selected['years']}
        third=None;corrections={};opening_adjustment=None;bridge=None;earliest=None
        if corrected:
            first=selected['opening_year'];prev=str(first-1);comparative=str(first);current=str(selected['current_year'])
            earliest=dict(date=str(first)+'-01-01',**{k:rows[prev][k] for k in POSITION})
            if f['material_earliest_opening_effect']:third=deepcopy(earliest)
            opening_adjustment={k:rows[prev][k]-original[prev][k] for k in POSITION}
            correction={k:rows[comparative][k]-original[comparative][k] for k in fixture['columns']}
            current_opening={k:rows[comparative][k]-original[comparative][k] for k in POSITION}
            need(opening_adjustment['equity']+correction['net_profit']==current_opening['equity'],'opening_comparative_bridge')
            need(rows[comparative]['equity']+rows[current]['net_profit']==rows[current]['equity'],'current_equity_bridge')
            corrections=dict(comparative=correction,earliest_opening=opening_adjustment,current_opening=current_opening)
            bridge=dict(original_current_opening_equity=original[comparative]['equity'],
                earliest_opening_correction=opening_adjustment['equity'],
                comparative_profit_correction=correction['net_profit'],
                corrected_current_opening_equity=rows[comparative]['equity'],
                current_profit=rows[current]['net_profit'],closing_equity=rows[current]['equity'],
                current_profit_prior_error_charge=Q(0),cash_correction=Q(0))
        report=dict(context=deepcopy(catalog['context']),source_kind='authored_synthetic_edition',
            requested_year=year,current_year=selected['current_year'],treatment=selected['kind'],
            statements=presented,cash_equity_flows=presented_flows,earliest_opening=earliest,
            third_statement=third,corrections=corrections,equity_bridge=bridge,
            eps='outside_supplied_private_profile',posts_correction=False,
            data_inputs_sha256=hashlib.sha256(payloads[FIXTURE]).hexdigest(),
            catalog_sha256=hashlib.sha256(payloads[CATALOG]).hexdigest())
        result.update(status='conditional_complete',selected_edition=deepcopy(selected),report=encode(report))
    except Refusal as exc:result.update(status=exc.status,reason=exc.reason)
    return result
