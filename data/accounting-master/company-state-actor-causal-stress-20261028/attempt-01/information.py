"""Supplied dated loan-type assertions; source hashes are not authentication."""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
p=ROOT/'data/accounting-master/exact-information-time-20261026/projection.py'
s=importlib.util.spec_from_file_location('actor_exact_time',p)
clock=importlib.util.module_from_spec(s);s.loader.exec_module(clock)
PROFILE='SuppliedLoanTypeView/1'
RECORD={'id','source_sha256','loan_id','loan_type','authored','effective','published','access'}
def view(records,sources,actor,loan,cutoff,max_records=16):
    result=dict(profile=PROFILE,actor=actor,loan_id=loan,decision_at=cutoff,
                source_admission=False,actual_knowledge_verified=False,
                observation=None,unresolved=[],withheld=[],accepted=[])
    try:
        if type(actor) is not str or not actor or type(loan) is not str or not loan:raise ValueError('actor_loan_identity')
        at=clock.instant(cutoff)
        if type(max_records) is not int or not 0<=max_records<=16:raise ValueError('bounded_record_limit')
        if type(records) is not list or type(sources) is not dict:raise ValueError('input_shape')
        unique={}
        for row in records:
            if type(row) is not dict or set(row)!=RECORD:raise ValueError('record_fields')
            key=row['id']
            if type(key) is not str or not key:raise ValueError('assertion_identity')
            if key in unique and row!=unique[key]:raise ValueError('identity_collision')
            unique[key]=deepcopy(row)
        if len(unique)>max_records:return {**result,'status':'unresolved_budget','unresolved':list(unique)}
        facts=set()
        for ident,row in unique.items():
            h=row['source_sha256']
            if type(h) is not str or h not in sources or type(sources[h]) is not str:raise ValueError('source_missing')
            if sha256(sources[h].encode()).hexdigest()!=h:raise ValueError('source_bytes_changed')
            if row['loan_id']!=loan:raise ValueError('loan_identity_mismatch')
            if row['loan_type'] not in ['fixed','floating',None]:raise ValueError('unsupported_loan_type')
            if type(row['access']) is not dict:raise ValueError('access_map')
            access=row['access'].get(actor)
            if access is None:
                result['unresolved'].append(dict(id=ident,reason='actor_access_unknown'));continue
            if type(access) is not dict or set(access)!={'route','at'}:raise ValueError('access_shape')
            if access['route'] not in ['private_delivery','public_document']:raise ValueError('access_route')
            required=['authored','effective']+(['published'] if access['route']=='public_document' else [])
            if any(row[k] is None for k in required) or access['at'] is None:
                result['unresolved'].append(dict(id=ident,reason='required_clock_unknown'));continue
            times={k:clock.instant(row[k]) for k in required};seen=clock.instant(access['at'])
            if seen<times['authored']:raise ValueError('access_before_authorship')
            if access['route']=='public_document' and (times['published']<times['authored'] or seen<times['published']):
                raise ValueError('public_access_chronology')
            if seen>at or times['authored']>at or times['effective']>at or ('published' in times and times['published']>at):
                result['withheld'].append(ident);continue
            if row['loan_type'] is None:
                result['unresolved'].append(dict(id=ident,reason='loan_type_unknown'));continue
            facts.add(row['loan_type']);result['accepted'].append(ident)
        if len(facts)>1:return {**result,'status':'conflict'}
        if result['unresolved']:return {**result,'status':'unresolved'}
        observation=dict(debt='100',loan_type=next(iter(facts)) if facts else None)
        return {**result,'status':'known' if facts else 'not_available','observation':observation}
    except (ValueError,TypeError,KeyError,OverflowError) as exc:
        return {**result,'status':'invalid','reason':str(exc)}
