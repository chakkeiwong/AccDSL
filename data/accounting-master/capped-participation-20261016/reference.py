"""Exact two-class EPS with fixed rights and additive gross conversion effects."""
from datetime import date
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
CONTEXT=dict(entity='synthetic-issuer',book='group',currency='CU',ordinary_class='O',participating_class='P',
    start='2025-01-01',end_exclusive='2026-01-01',rule='EU2023/1803-original-IAS33')
FINDINGS={'equity_classification_admitted','senior_period_entitlement_complete','residual_profit_only','rights_fixed',
    'no_other_dividends_or_attribution','total_equals_continuing','independent_gross_effects','inventory_complete','full_period_constant_population'}
SERIES_FINDINGS={'all_direct_and_consequential_effects_complete','time_weighting_complete','no_conditional_exercise'}

class Refusal(Exception):
    def __init__(self,status,reason):self.status=status;self.reason=reason
def fail(reason,status='rejected'):raise Refusal(status,reason)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def num(x,name,signed=False,positive=False):
    if x is None:fail('missing_'+name,'unresolved')
    try:
        if not isinstance(x,str):raise ValueError()
        v=Q(x)
        if str(v)!=x:raise ValueError()
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if (not signed and v<0) or (positive and v<=0):fail('number_domain')
    return v
def findings(x,keys):
    shape(x,keys,'finding_shape')
    for k in sorted(keys):
        if x[k] is None:fail('missing_'+k,'unresolved')
        if x[k] is False:fail('outside_'+k,'unsupported')
        if x[k] is not True:fail('finding_encoding')
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

def allocation(earnings,n,preferred_count,weight,senior,total_cap):
    m=preferred_count*weight;surplus=max(earnings-senior,Q(0));uncapped=surplus*m/(n+m)
    participation=min(total_cap-senior,uncapped);preferred=senior+participation;ordinary=earnings-preferred
    return dict(earnings=earnings,preferred=preferred,ordinary=ordinary,denominator=n,eps=ordinary/n,
        preferred_eps=preferred/preferred_count,residual_participation=participation,cap_binds=uncapped>=total_cap-senior)

def calculate(r,reader=lambda p:p.read_bytes()):
    empty=dict(basic=None,diluted=None,selected=[],trace=[],mutations=[])
    try:
        lock={x['path']:x['sha256'] for x in json.loads((OUT/'input-lock.json').read_text())['files']}
        try:raw=reader(ROOT/SOURCE)
        except FileNotFoundError:fail('source_unavailable','unresolved')
        if hashlib.sha256(raw).hexdigest()!=lock[SOURCE]:fail('source_changed')
        shape(r,{'wire','operation','context','earnings','ordinary_shares','preferred_shares','residual_weight','senior_entitlement','total_preferred_cap','findings','series'},'request_shape')
        if r['wire']!='CappedParticipationEPS/1':fail('wire')
        if r['operation']!='report':fail('report_only')
        if r['context']!=CONTEXT:fail('context')
        findings(r['findings'],FINDINGS)
        E=num(r['earnings'],'earnings',True);n=num(r['ordinary_shares'],'ordinary_shares',positive=True)
        count=num(r['preferred_shares'],'preferred_shares',positive=True);weight=num(r['residual_weight'],'residual_weight')
        f=num(r['senior_entitlement'],'senior_entitlement');cap=num(r['total_preferred_cap'],'total_preferred_cap')
        if cap<f:fail('cap_below_senior')
        if n.denominator!=1 or count.denominator!=1:fail('whole_period_share_population','unsupported')
        if not isinstance(r['series'],list):fail('series_shape')
        candidates=[];seen=set()
        for item in r['series']:
            shape(item,{'id','gross_after_tax_adjustment','ordinary_share_increment','start','end_exclusive','findings'},'series_shape')
            id=item['id']
            if not isinstance(id,str) or not id.strip() or id!=id.strip() or id in seen:fail('series_identity')
            seen.add(id);findings(item['findings'],SERIES_FINDINGS)
            for k in ('start','end_exclusive'):
                try:
                    if date.fromisoformat(item[k]).isoformat()!=item[k]:raise ValueError()
                except (ValueError,TypeError):fail('date_encoding')
                if item[k]!=CONTEXT[k]:fail('partial_period_series','unsupported')
            a=num(item['gross_after_tax_adjustment'],'gross_after_tax_adjustment',True)
            if a<0:fail('negative_gross_effect','unsupported')
            b=num(item['ordinary_share_increment'],'ordinary_share_increment',positive=True)
            candidates.append((a/b,id,a,b))
        candidates.sort();basic=allocation(E,n,count,weight,f,cap);current=basic;selected=[];trace=[]
        for ratio,id,a,b in candidates:
            candidate=allocation(E+a,n+b,count,weight,f,cap)
            include=candidate['eps']<current['eps']
            if include!=(a<current['eps']*b):fail('derived_threshold_identity')
            trace.append(dict(id=id,gross_increment_per_share=ratio,ordinary_numerator_increment=candidate['ordinary']-current['ordinary'],
                before=current,if_included=candidate,included=include,reason='strictly_dilutive' if include else 'equal_or_antidilutive'))
            if include:E+=a;n+=b;current=candidate;selected.append(id)
        return encode(dict(status='conditional_complete',reason='fixed_rights_additive_gross_family',basic=basic,diluted=current,selected=selected,trace=trace,mutations=[]))
    except Refusal as e:return dict(status=e.status,reason=e.reason,**empty)
