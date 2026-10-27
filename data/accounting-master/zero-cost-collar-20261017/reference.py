"""Signed collar components, gross cash and basis: documentary reference only."""
from datetime import date
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
FINDINGS={'external_contracts','not_net_written','eligible_designation','highly_probable_purchase',
    'combined_risk_alignment','complete_valuation','zero_discount_no_carry','credit_not_dominant',
    'continuing_qualification','recoverable_reserves','inventory_recognition','pretax_no_other_flows'}


class Refusal(Exception):
    def __init__(self,status,reason):self.status,self.reason=status,reason


def need(ok,reason,status='rejected'):
    if not ok:raise Refusal(status,reason)


def fields(x,keys,reason):need(type(x) is dict and set(x)==set(keys.split()),reason)


def rational(x):
    need(x is not None,'unknown_amount','unresolved');need(type(x) is str,'rational_type')
    try:v=Q(x)
    except (ValueError,ZeroDivisionError):raise Refusal('rejected','rational_value')
    need(str(v)==x,'noncanonical_rational');return v


def day(x):
    need(type(x) is str,'date')
    try:v=date.fromisoformat(x)
    except ValueError:raise Refusal('rejected','date')
    need(v.isoformat()==x,'date');return v


def evaluate(r,*,source_root=ROOT):
    empty=dict(result=None,stages=[],journals=[],flows=[],posts=False,mutations=[])
    try:
        for item in json.loads((OUT/'input-lock.json').read_text())['files']:
            p=Path(source_root)/item['path'];need(p.is_file(),'missing_source','unresolved')
            need(hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'source_changed')
        fields(r,'wire operation context opening_cash quantity opening_spot call put findings quotes closing','request_fields')
        need(r['wire']=='AlignedZeroCostCollar/1','wire');need(r['operation']=='report','operation','unsupported')
        c=r['context'];fields(c,'entity book currency underlying start expiry information_date rule','context_fields')
        need(all(type(v) is str and v.strip() for v in c.values()),'context_value')
        need(c['rule']=='EU2023/1803-original-IFRS9','source_profile')
        start,expiry,cutoff=(day(c[k]) for k in ('start','expiry','information_date'))
        need(start<expiry<=cutoff,'context_dates')
        need(type(r['findings']) is dict and set(r['findings'])==FINDINGS,'finding_fields')
        for k,v in r['findings'].items():
            need(v is not None,'missing_finding/'+k,'unresolved');need(type(v) is bool,'finding_type')
            need(v,'unsupported_finding/'+k,'unsupported')
        capital=rational(r['opening_cash']);q=rational(r['quantity']);spot0=rational(r['opening_spot'])
        need(capital>0 and q>0 and spot0>=0,'opening_domain')
        legs={}
        for name in ('call','put'):
            leg=r[name];fields(leg,'id quantity strike expiry underlying premium','leg_fields')
            need(type(leg['id']) is str and leg['id'].strip(),'leg_id')
            need(rational(leg['quantity'])==q and leg['expiry']==c['expiry'] and leg['underlying']==c['underlying'],'leg_alignment','unsupported')
            strike=rational(leg['strike']);premium=rational(leg['premium'])
            need(strike>0 and premium>0,'leg_domain')
            legs[name]=dict(strike=strike,premium=premium,id=leg['id'])
        call,put=legs['call'],legs['put']
        need(call['id']!=put['id'],'leg_collision')
        need(put['strike']<call['strike'] and put['strike']<=spot0<=call['strike'],'strike_opening_domain','unsupported')
        need(call['premium']==put['premium'],'nonzero_net_premium','unsupported')

        balances=dict(cash=capital,capital=-capital,call_asset=Q(0),put_liability=Q(0),inventory=Q(0),intrinsic_reserve=Q(0),time_reserve=Q(0))
        journals=[];flows=[];stages=[]
        def journal(id,d,changes):
            need(sum(changes.values())==0,'journal_balance')
            for k,v in changes.items():balances[k]+=v
            need(sum(balances.values())==0,'ledger_balance')
            journals.append(dict(id=id,date=d,entries={k:str(v) for k,v in changes.items() if v}))
        def cashflow(id,d,amount,account):
            need(balances['cash']+amount>=0,'funding_shortfall','unsupported')
            journal(id,d,dict(cash=amount,**{account:-amount}))
            flows.append(dict(id=id,date=d,amount=str(amount)))
        def snapshot(id,d):
            stages.append(dict(id=id,date=d,balances={k:str(v) for k,v in balances.items()},
                intrinsic=str(-balances['intrinsic_reserve']),time=str(-balances['time_reserve']),
                call=str(balances['call_asset']),put=str(-balances['put_liability'])))
        cashflow('call-premium',c['start'],-call['premium'],'call_asset')
        cashflow('put-premium',c['start'],put['premium'],'put_liability');snapshot('inception',c['start'])
        need(type(r['quotes']) is list and len(r['quotes'])>0,'quotes')
        previous=start;last=None
        for i,m in enumerate(r['quotes']):
            fields(m,'date spot call_time put_time call_value put_value item_change call_id put_id facts_available_on','quote_fields')
            d=day(m['date']);available=day(m['facts_available_on'])
            need(previous<d<=expiry,'quote_date');need(d<=available<=cutoff,'quote_information')
            need(m['call_id']==call['id'] and m['put_id']==put['id'],'quote_leg')
            s,tc,tp,vc,vp,h=(rational(m[k]) for k in ('spot','call_time','put_time','call_value','put_value','item_change'))
            need(min(s,tc,tp,vc,vp)>=0,'quote_domain')
            ic=q*max(s-call['strike'],0);ip=q*max(put['strike']-s,0)
            need(vc==ic+tc and vp==ip+tp,'component_value_mismatch')
            ri=ic-ip;rt=tc-tp
            need(h==-ri,'hedged_item_not_matched','unsupported')
            if d==expiry:need(tc==tp==0,'expiry_time_value')
            journal(f'measure-{i}',m['date'],dict(call_asset=vc-balances['call_asset'],
                put_liability=-vp-balances['put_liability'],intrinsic_reserve=-ri-balances['intrinsic_reserve'],
                time_reserve=-rt-balances['time_reserve']))
            snapshot(f'measure-{i}',m['date']);previous=d;last=(s,vc,vp,ri,rt)
        need(previous==expiry,'missing_expiry','unsupported')
        x=r['closing'];fields(x,'date quantity supplier_cash call_receipt put_payment','closing_fields')
        need(x['date']==c['expiry'],'closing_date');need(rational(x['quantity'])==q,'purchase_quantity')
        supplier,receipt,payment=(rational(x[k]) for k in ('supplier_cash','call_receipt','put_payment'))
        s,vc,vp,ri,rt=last
        need(supplier==q*s,'supplier_cash_mismatch');need(receipt==vc and payment==vp,'settlement_mismatch')
        cashflow('supplier',x['date'],-supplier,'inventory')
        cashflow('call-settlement',x['date'],receipt,'call_asset')
        cashflow('put-settlement',x['date'],-payment,'put_liability')
        journal('intrinsic-basis',x['date'],dict(intrinsic_reserve=ri,inventory=-ri))
        journal('time-basis',x['date'],dict(time_reserve=rt,inventory=-rt));snapshot('closed',x['date'])
        need(balances['inventory']>=0,'inventory_domain')
        result=dict(context=dict(c),cash=str(balances['cash']),inventory=str(balances['inventory']),profit='0',
            capital=str(capital),intrinsic_reserve=str(-balances['intrinsic_reserve']),time_reserve=str(-balances['time_reserve']),
            call_asset=str(balances['call_asset']),put_liability=str(-balances['put_liability']))
        empty.update(status='conditional_complete',reason=None,result=result,stages=stages,journals=journals,flows=flows)
    except Refusal as e:empty.update(status=e.status,reason=e.reason)
    return empty
