"""Conditional joint earnings and the explicit IAS33.57 option dependency."""
from datetime import date
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE='docs/design/research/p08-v3-preparation/eu-2023-1803-original.txt'
CONTEXT=dict(entity='synthetic-issuer',book='group',currency='CU',ordinary_class='O',
    start='2025-01-01',end_exclusive='2026-01-01',rule='EU2023/1803-original-IAS33')
COMMON={'total_equals_continuing','nonparticipating_ordinary','inventory_complete','whole_period','no_other_earnings_effects'}
WORLD_FINDINGS=COMMON|{'bonus_terms_complete','tax_effects_complete','independent_interest_savings'}
OPTION_FINDINGS=COMMON|{'similarity_admitted','no_service_proceeds','contingent_option_not_in_basic','no_other_dependencies'}

class Refusal(Exception):
    def __init__(self,reason,status='rejected'):self.reason=reason;self.status=status
def fail(reason,status='rejected'):raise Refusal(reason,status)
def shape(x,keys,reason):
    if not isinstance(x,dict) or set(x)!=set(keys):fail(reason)
def num(x,key,signed=False,positive=False,integer=False):
    if x is None:fail('missing_'+key,'unresolved')
    try:
        if not isinstance(x,str):raise ValueError()
        v=Q(x)
        if str(v)!=x:raise ValueError()
    except (ValueError,ZeroDivisionError):fail('number_encoding')
    if not signed and v<0 or positive and v<=0 or integer and v.denominator!=1:fail('number_domain')
    return v
def findings(x,keys):
    shape(x,keys,'finding_shape')
    for key in sorted(keys):
        if x[key] is None:fail('missing_'+key,'unresolved')
        if x[key] is False:fail('outside_'+key,'unsupported')
        if x[key] is not True:fail('finding_encoding')
def identity(x):
    if not isinstance(x,str) or not x.strip() or x!=x.strip():fail('series_identity')
    return x
def encode(x):
    if isinstance(x,Q):return str(x)
    if isinstance(x,list):return [encode(v) for v in x]
    if isinstance(x,dict):return {k:encode(v) for k,v in x.items()}
    return x

def calculate(r,reader=lambda p:p.read_bytes()):
    empty=dict(basic=None,worlds=[],diluted=None,selected=None,trace=[],mutations=[])
    try:
        lock={x['path']:x['sha256'] for x in json.loads((OUT/'input-lock.json').read_text())['files']}
        try:raw=reader(ROOT/SOURCE)
        except FileNotFoundError:fail('source_unavailable','unresolved')
        if hashlib.sha256(raw).hexdigest()!=lock[SOURCE]:fail('source_changed')
        if not isinstance(r,dict):fail('request_shape')
        wire=r.get('wire')
        if wire not in {'ConsequentialEPSWorlds/1','ContingentOptionEPS/1'}:fail('wire')
        if r.get('context')!=CONTEXT:fail('context')
        if wire=='ConsequentialEPSWorlds/1':
            shape(r,{'wire','operation','context','pretax_before_bonus','bonus_threshold','bonus_rate','tax_rate','ordinary_shares','findings','series'},'request_shape')
            if r['operation']!='worlds':fail('nonadditive_selection_not_specified','unsupported')
            findings(r['findings'],WORLD_FINDINGS)
            P=num(r['pretax_before_bonus'],'pretax_before_bonus',signed=True)
            H=num(r['bonus_threshold'],'bonus_threshold');q=num(r['bonus_rate'],'bonus_rate');t=num(r['tax_rate'],'tax_rate')
            n=num(r['ordinary_shares'],'ordinary_shares',positive=True,integer=True)
            if q>1 or t>=1:fail('rate_domain')
            if P<0 and t!=0:fail('loss_tax_recognition_not_specified','unsupported')
            if not isinstance(r['series'],list) or len(r['series'])!=2:fail('two_series_required','unsupported')
            series=[];seen=set()
            for row in r['series']:
                shape(row,{'id','interest_saved','incremental_shares'},'series_shape')
                id=identity(row['id'])
                if id in seen:fail('series_identity')
                seen.add(id)
                series.append((id,num(row['interest_saved'],'interest_saved'),num(row['incremental_shares'],'incremental_shares',positive=True)))
            series.sort();worlds=[]
            for size in range(3):
                for subset in combinations(series,size):
                    p=P+sum((s[1] for s in subset),Q(0));shares=n+sum((s[2] for s in subset),Q(0))
                    bonus=q*max(p-H,Q(0));tax=t*(p-bonus);earnings=p-bonus-tax
                    worlds.append(dict(assumed=[s[0] for s in subset],pretax_before_bonus=p,bonus=bonus,tax=tax,
                        earnings=earnings,shares=shares,eps=earnings/shares))
            basic=worlds[0]
            return encode(dict(status='conditional_worlds_complete',reason='joint_consequences_only',basic=basic,worlds=worlds,
                diluted=None,selected=None,trace=[],mutations=[],selection_status='not_evaluated'))
        shape(r,{'wire','operation','context','earnings','ordinary_shares','average_market_price','findings','similar','contingent','condition'},'request_shape')
        if r['operation']!='report':fail('report_only')
        findings(r['findings'],OPTION_FINDINGS)
        E=num(r['earnings'],'earnings',signed=True);n=num(r['ordinary_shares'],'ordinary_shares',positive=True,integer=True)
        market=num(r['average_market_price'],'average_market_price',positive=True)
        terms={}
        for key in ('similar','contingent'):
            row=r[key];shape(row,{'id','count','strike'},'option_shape');id=identity(row['id'])
            count=num(row['count'],'count',positive=True,integer=True);strike=num(row['strike'],'strike')
            terms[key]=(id,max(Q(0),count*(market-strike)/market))
        if terms['similar'][0]==terms['contingent'][0]:fail('series_identity')
        c=r['condition'];shape(c,{'kind','observed','required','observed_date','agreement_start','contingency_end'},'condition_shape')
        if c['kind']!='store_count':fail('condition_kind','unsupported')
        for key in ('observed_date','agreement_start','contingency_end'):
            try:
                if date.fromisoformat(c[key]).isoformat()!=c[key]:raise ValueError()
            except (TypeError,ValueError):fail('date_encoding')
        if c['observed_date']!='2025-12-31':fail('period_end_observation')
        if c['agreement_start']!=CONTEXT['start']:fail('partial_period_agreement','unsupported')
        if c['contingency_end']<CONTEXT['end_exclusive']:fail('expired_contingency','unsupported')
        observed=num(c['observed'],'observed',integer=True);required=num(c['required'],'required',positive=True,integer=True)
        satisfied=observed>=required
        def value(shares):return dict(earnings=E,shares=shares,eps=E/shares)
        basic=value(n);current=basic;selected=[];trace=[];similar_assumed=False
        for key in ('similar','contingent'):
            id,b=terms[key];candidate=value(n+b)
            if key=='contingent' and not satisfied:reason='condition_not_satisfied'
            elif key=='contingent' and not similar_assumed:reason='similar_not_assumed'
            elif b==0:reason='no_increment'
            elif candidate['eps']>=current['eps']:reason='not_strictly_dilutive'
            else:reason='selected'
            trace.append(dict(id=id,role=key,incremental_shares=b,before=current,if_assumed=candidate,reason=reason))
            if reason=='selected':
                n+=b;current=candidate;selected.append(id)
                if key=='similar':similar_assumed=True
        return encode(dict(status='conditional_complete',reason='IAS33_57_dependency',basic=basic,worlds=[],diluted=current,
            selected=selected,trace=trace,mutations=[],period_end_condition_satisfied=satisfied))
    except Refusal as e:return dict(status=e.status,reason=e.reason,**empty)
