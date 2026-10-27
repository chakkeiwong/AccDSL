"""Explicit typed translation of the frozen E03 conditional examples."""
from copy import deepcopy
from fractions import Fraction
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'scripts'))
import method_requirements_v3 as guarded
import company_book_transition_v1 as engine
core=engine.core
NUMBER=dict(kind='rational',context={},dimensions={},scale='1/1')
SCOPE='Conditional translation of retained E03 examples; no actual legal/accounting admission'
class Unsupported(ValueError):pass

def const(typ,value):return dict(op='const',type=deepcopy(typ),value=value)
def op(kind,a,b):return dict(op=kind,left=a,right=b)
def both(*args):return dict(op='all',args=list(args))
def either(*args):return dict(op='any',args=list(args))
def inverse(arg):return dict(op='not',arg=arg)

class Builder:
    def __init__(self,facts):self.facts=facts;self.inputs={};self.values={}
    def value(self,name,typ,value):
        self.inputs[name]=dict(type=deepcopy(typ),role='caller_finding' if typ==core.BOOL else 'assumption',source_ref='supplied:E03:'+name)
        self.values[name]=dict(status='unknown',reason='Required conditional finding or exact boundary order missing') if value is None else engine.known(value)
        return dict(op='ref',id=name)
    def boolean(self,key):
        raw=self.facts.get(key)
        core.need(raw is None or type(raw) is bool,'supplied_boolean:'+key)
        return self.value(key,core.BOOL,raw)
    def number(self,key,unit=False):
        raw=self.facts.get(key)
        if raw is None:return self.value(key,NUMBER,None)
        core.need(type(raw) in (str,int),'exact_numeric_input:'+key)
        try:q=Fraction(raw)
        except (ValueError,ZeroDivisionError):raise core.Invalid('exact_rational:'+key)
        core.need(q>=0 and (not unit or q<=1),'numeric_domain:'+key)
        return self.value(key,NUMBER,str(q.numerator)+'/'+str(q.denominator))
    def authority(self):
        actor=self.facts.get('notice_actor')
        if actor=='trustee':return const(core.BOOL,True)
        if actor is None:return self.value('unknown_notice_authority',core.BOOL,None)
        if actor!='holders':raise Unsupported('notice_actor')
        edition=self.facts.get('indenture')
        if edition not in (None,'2013','2018'):raise Unsupported('indenture_edition')
        share=self.number('holder_principal_fraction',True)
        threshold=self.value('selected_holder_threshold',NUMBER,None if edition is None else {'2013':'1/4','2018':'33/100'}[edition])
        return op('le',threshold,share)
    def notice(self):
        return both(self.boolean('written_notice'),self.boolean('required_recipients_received'),
                    self.boolean('notice_validity_established'),self.authority())
    def elapsed(self,key,limit):
        days=self.number(key);boundary=const(NUMBER,str(limit)+'/1')
        unknown=self.value(key+'_boundary_order',core.BOOL,None)
        return either(op('lt',deepcopy(boundary),deepcopy(days)),
                      both(op('eq',days,boundary),unknown))
    def expression(self,method):
        b=self.boolean
        if method=='event_clause':
            kind=self.facts.get('kind');applicable=b('selected_clause_applicable')
            if kind in ('principal','premium'):value=both(b('due_and_payable'),b('unpaid'))
            elif kind=='interest':value=both(b('due_and_payable'),b('continuously_unpaid'),self.elapsed('days_after_due',30))
            elif kind=='covenant':value=both(b('eligible_covenant'),b('breach_continuing'),self.notice(),self.elapsed('days_after_valid_notice',90))
            elif kind=='bankruptcy':value=b('specified_qualifying_event_established')
            else:raise Unsupported('default_clause')
            return both(applicable,value)
        if method=='notice':return self.notice()
        if method=='new_acceleration':
            event=b('event_occurs_and_continues');automatic=b('specified_automatic_category')
            if self.facts.get('specified_automatic_category') is True:route=automatic
            else:route=either(automatic,both(b('declaration_made'),self.notice()))
            return both(b('acceleration_rule_applicable'),event,route)
        if method=='after_rescission':
            existing=b('existing_acceleration')
            rescinded=both(*[b(k) for k in ['requisite_majority_established','required_deposit_established',
              'all_relevant_events_cured_or_waived','other_rescission_conditions_established','rescission_effected']])
            return both(existing,inverse(rescinded))
        if method=='amendment_consent':
            if self.facts.get('change') not in ['stated_maturity','principal','interest_rate','payment_currency',
              'payment_suit_right','protected_vote_threshold','protected_conversion_right']:raise Unsupported('amendment_route')
            return both(b('protected_change_applies'),b('each_affected_holder_consented'))
        if method=='majority_waiver':
            return both(inverse(b('payment_or_individually_protected_default')),b('requisite_majority_established'),
                        b('waiver_effected'),b('other_waiver_conditions_established'))
        if method=='cross_series':return b('target_series_event_established_from_own_terms')
        raise Unsupported('method')

def assess(method,facts):
    try:
        core.need(type(facts) is dict,'facts_record')
        builder=Builder(facts);expr=builder.expression(method)
        manifest=dict(profile=guarded.PROFILE,method_id='conditional.remedy.'+method,version='1',inputs=builder.inputs,
          requirements=[dict(id='selected_condition',guard=const(core.BOOL,True),guard_requires=[],predicate=expr,
            requires=list(builder.inputs),admission_refs=[],on_false='invalid',on_unknown='unresolved')],
          required_known=[],capabilities=[],residual_prerequisites=[SCOPE])
        key=core.digest(manifest);evaluation=guarded.assess({key:manifest},key,builder.values,[])
        if 'findings' not in evaluation:
            return dict(status='invalid_input',evaluation=evaluation,source_admission=False,accounting_admission=False)
        truth=evaluation['findings'][0]['body_truth']
        return dict(status={'true':'satisfied','false':'not_satisfied','unknown':'unresolved'}[truth],
          manifest=manifest,values=builder.values,evaluation=evaluation,facts_sha256=core.digest(facts),
          source_admission=False,accounting_admission=False)
    except Unsupported as exc:return dict(status='unsupported',reason=str(exc),source_admission=False,accounting_admission=False)
    except (ValueError,KeyError,TypeError,RecursionError,OverflowError) as exc:
        return dict(status='invalid_input',reason=str(exc)[:300],source_admission=False,accounting_admission=False)
