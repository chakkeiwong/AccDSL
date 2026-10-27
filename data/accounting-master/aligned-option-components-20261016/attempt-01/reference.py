"""Keep actual and hypothetical call components separate through inventory basis."""
from copy import deepcopy
from datetime import date
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
CONTEXT=dict(entity='P',book='P-separate',currency='CU',quantity_unit='unit',rule='EU2023/1803-original-IFRS9',designation_date='2025-01-01',expiry='2025-12-31')
FINDINGS={'actual_terms_admitted','aligned_terms_match_item','complete_component_values','intrinsic_hedge_qualifies','forecast_highly_probable','transaction_related_inventory','reserve_recoverable','zero_discount_admitted','no_other_cash_or_earnings','no_fees','pretax_only'}
CLOSING_FINDINGS={'all_units_received','inventory_recognition','nrv_supported','complete_costs'}

class Refusal(Exception):
    def __init__(self,reason,status='rejected'):self.reason=reason;self.status=status
def fail(reason,status='rejected'):raise Refusal(reason,status)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def num(x,key,positive=False):
    if x is None:fail('missing_'+key,'unresolved')
    try:
        if not isinstance(x,str):raise ValueError()
        v=Q(x)
        if str(v)!=x:raise ValueError()
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if v<0 or positive and v<=0:fail('number_domain')
    return v
def identity(x):
    if not isinstance(x,str) or not x.strip() or x!=x.strip():fail('identity')
    return x
def findings(x,keys):
    shape(x,keys,'finding_shape')
    for key in sorted(keys):
        if x[key] is None:fail('missing_'+key,'unresolved')
        if x[key] is False:fail('outside_'+key,'unsupported')
        if x[key] is not True:fail('finding_encoding')
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

def calculate(r,reader=lambda p:p.read_bytes()):
    empty=dict(measurements=[],journals=[],cash_flows=[],closing=None,mutations=[])
    try:
        lock={x['path']:x['sha256'] for x in json.loads((OUT/'input-lock.json').read_text())['files']}
        try:raw=reader(ROOT/SOURCE)
        except FileNotFoundError:fail('source_unavailable','unresolved')
        if hashlib.sha256(raw).hexdigest()!=lock[SOURCE]:fail('source_changed')
        shape(r,{'wire','operation','context','opening_cash','opening_price','premium_cash','findings','item','actual','aligned','quotes','closing'},'request_shape')
        if r['wire']!='AlignedOptionComponents/1':fail('wire')
        if r['operation']!='report':fail('report_only')
        if r['context']!=CONTEXT:fail('context')
        findings(r['findings'],FINDINGS)
        capital=num(r['opening_cash'],'opening_cash');spot0=num(r['opening_price'],'opening_price',positive=True)
        shape(r['item'],{'id','quantity','hedged_price'},'item_shape');identity(r['item']['id'])
        quantity=num(r['item']['quantity'],'item_quantity',positive=True);hedged=num(r['item']['hedged_price'],'hedged_price',positive=True)
        terms={}
        for kind,expected in [('actual','purchased_call'),('aligned','hypothetical_call')]:
            row=r[kind];shape(row,{'id','kind','quantity','strike','initial_time_value','expiry'},'contract_shape')
            identity(row['id'])
            if row['kind']!=expected:fail('contract_kind','unsupported')
            if row['expiry']!=CONTEXT['expiry']:fail('expiry_binding')
            if num(row['quantity'],'option_quantity',positive=True)!=quantity:fail('quantity_binding')
            strike=num(row['strike'],'strike',positive=True);tv=num(row['initial_time_value'],'initial_time_value',positive=True)
            if spot0>strike:fail('nonzero_initial_intrinsic','unsupported')
            terms[kind]=(strike,tv)
        if r['actual']['id']==r['aligned']['id']:fail('contract_identity')
        if terms['aligned'][0]!=hedged:fail('aligned_item_terms')
        actual0=terms['actual'][1];aligned0=terms['aligned'][1]
        matched=terms['actual'][0]==terms['aligned'][0] and actual0==aligned0
        if actual0==aligned0 and not matched:fail('equal_initial_unmatched_terms','unsupported')
        branch='matched' if matched else 'higher_actual' if actual0>aligned0 else 'lower_actual'
        premium=num(r['premium_cash'],'premium_cash')
        if premium!=actual0:fail('actual_premium_identity')
        if capital<premium:fail('premium_funding_required','unsupported')
        books=dict(cash=capital,capital=-capital,option=Q(0),inventory=Q(0),intrinsic_reserve=Q(0),cost_reserve=Q(0),earnings=Q(0))
        journals=[];flows=[];measurements=[]
        def journal(id,date,entries):
            if sum(entries.values(),Q(0))!=0:fail('journal_balance')
            if any(entries.values()):
                for key,value in entries.items():books[key]+=value
                journals.append(dict(id=id,date=date,entries=entries))
        journal('premium',CONTEXT['designation_date'],dict(option=premium,cash=-premium));flows.append(dict(kind='actual_premium',amount=-premium))
        if not isinstance(r['quotes'],list) or not r['quotes']:fail('quotes_shape')
        last_date=CONTEXT['designation_date'];seen=set();priorV=premium;priorR=Q(0);priorC=Q(0);priorP=Q(0)
        for quote in r['quotes']:
            shape(quote,{'id','date','context','actual_id','aligned_id','price','actual_time_value','aligned_time_value','actual_option_value','aligned_option_value'},'quote_shape')
            id=identity(quote['id'])
            if id in seen:fail('duplicate_quote')
            seen.add(id)
            try:
                if date.fromisoformat(quote['date']).isoformat()!=quote['date']:raise ValueError()
            except (ValueError,TypeError):fail('date_encoding')
            if quote['date']<=last_date or quote['date']>CONTEXT['expiry']:fail('quote_chronology')
            if quote['context']!=CONTEXT:fail('quote_context')
            if quote['actual_id']!=r['actual']['id'] or quote['aligned_id']!=r['aligned']['id']:fail('quote_contract_binding')
            price=num(quote['price'],'price',positive=True);at=num(quote['actual_time_value'],'actual_time_value');ht=num(quote['aligned_time_value'],'aligned_time_value')
            if at>actual0 or ht>aligned0:fail('outside_common_loss_profile','unsupported')
            if matched and at!=ht:fail('matched_component_values')
            ai=quantity*max(price-terms['actual'][0],Q(0));hi=quantity*max(price-terms['aligned'][0],Q(0))
            av=num(quote['actual_option_value'],'actual_option_value');hv=num(quote['aligned_option_value'],'aligned_option_value')
            if av!=ai+at or hv!=hi+ht:fail('component_decomposition')
            R=min(ai,hi);ip=ai-R
            C=ht-aligned0 if branch in {'matched','higher_actual'} else -min(actual0-at,aligned0-ht)
            tp=at-actual0-C;P=ip+tp
            journal(id,quote['date'],dict(option=av-priorV,intrinsic_reserve=priorR-R,cost_reserve=priorC-C,earnings=priorP-P))
            measurements.append(dict(id=id,date=quote['date'],price=price,actual_intrinsic=ai,aligned_intrinsic=hi,actual_time_value=at,
                aligned_time_value=ht,actual_value=av,aligned_value=hv,intrinsic_reserve=R,cost_reserve=C,intrinsic_profit=ip,time_profit=tp,
                profit=P,cash=books['cash'],equity=capital+P+R+C,books=deepcopy(books)))
            last_date=quote['date'];priorV=av;priorR=R;priorC=C;priorP=P
        if last_date!=CONTEXT['expiry']:fail('expiry_measurement_required','unresolved')
        if at!=0 or ht!=0:fail('nonzero_expiry_time_value')
        c=r['closing'];shape(c,{'date','quantity','unit_price','supplier_cash','actual_settlement','findings'},'closing_shape');findings(c['findings'],CLOSING_FINDINGS)
        if c['date']!=last_date:fail('closing_date')
        q=num(c['quantity'],'purchase_quantity',positive=True);p=num(c['unit_price'],'unit_price',positive=True);paid=num(c['supplier_cash'],'supplier_cash');settlement=num(c['actual_settlement'],'actual_settlement')
        if q!=quantity or p!=price or paid!=q*p:fail('purchase_identity')
        if settlement!=av:fail('actual_settlement_identity')
        if books['cash']<paid:fail('supplier_funding_required','unsupported')
        journal('purchase',last_date,dict(inventory=paid,cash=-paid));flows.append(dict(kind='supplier_payment',amount=-paid))
        journal('settlement',last_date,dict(option=-settlement,cash=settlement));flows.append(dict(kind='actual_option_settlement',amount=settlement))
        journal('intrinsic_basis',last_date,dict(intrinsic_reserve=R,inventory=-R))
        journal('cost_basis',last_date,dict(cost_reserve=C,inventory=-C))
        closing=dict(cash=books['cash'],inventory=books['inventory'],profit=P,equity=capital+P,supplier_cost=paid,
            intrinsic_basis_transfer=R,cost_basis_transfer=C,books=books)
        return encode(dict(status='conditional_complete',reason='actual_and_aligned_components',branch=branch,measurements=measurements,
            journals=journals,cash_flows=flows,closing=closing,mutations=[],posts=False))
    except Refusal as e:return dict(status=e.status,reason=e.reason,**empty)
