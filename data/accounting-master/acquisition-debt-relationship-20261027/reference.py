"""Conditional source-bound scope only; never posts or measures a transaction."""
from copy import deepcopy
from datetime import datetime
from hashlib import sha256
import json

PROFILE='ConditionalDebtRelationshipScope/1'
FACTS=('renegotiated','original_terms','creditor_existing_shareholder',
       'acts_as_owner','common_control_before_after',
       'equity_distribution_or_contribution','liability_extinguished',
       'partial_extinguishment','remaining_terms_modified',
       'creditor_gains_control','acquired_business',
       'settles_preexisting_relationship')
FLAGS=dict(source_admission=False,accounting_admission=False,
           posting_authorized=False,report_authorized=False)

def digest(x):
    return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def need(v,n):
    if not v:raise ValueError(n)

def fields(x,names,label):
    need(isinstance(x,dict) and set(x)==set(names),label+'_fields')

def text(x,label):
    need(isinstance(x,str) and bool(x.strip()) and len(x)<10000,label)

def moment(x):
    need(isinstance(x,str),'timestamp_type')
    d=datetime.fromisoformat(x.replace('Z','+00:00'))
    need(d.tzinfo is not None and d.utcoffset().total_seconds()==0,'timestamp_utc')
    return d

def both(a,b):
    if 'no' in (a,b):return 'no'
    if a==b=='yes':return 'yes'
    return 'unknown'

def derive(request):
    try:
        need(len(json.dumps(request,allow_nan=False))<60000,'request_size')
        fields(request,['profile','payload','expected_payload_sha256'],'envelope')
        need(request['profile']==PROFILE,'profile')
        p=request['payload'];need(digest(p)==request['expected_payload_sha256'],'payload_binding')
        fields(p,['context','perspective','transaction','prior_instrument','assertions','source','evidence_sha256'],'payload')
        need(p['transaction']=='debt_for_debtor_own_shares','transaction_scope')
        need(p['prior_instrument']=='debt','prior_debt_required')
        role=p['perspective'];need(role in ['debtor','creditor'],'perspective')
        c=p['context'];fields(c,['debtor','creditor','subject','actor','at','cutoff'],'context')
        for k in ['debtor','creditor','subject','actor']:text(c[k],'context_'+k)
        need(c['debtor']!=c['creditor'],'distinct_parties')
        need(c['subject']==c[role],'subject_perspective')
        need(moment(c['at'])<=moment(c['cutoff']),'event_after_cutoff')
        f=p['assertions'];fields(f,FACTS,'assertions')
        for k in FACTS:need(f[k] in ['yes','no','unknown'],'assertion_'+k)
        s=p['source'];fields(s,['text','rationale','subject','actor','at','available_at','assertions_sha256'],'source')
        text(s['text'],'source_text');text(s['rationale'],'source_rationale')
        need(s['subject']==c['subject'] and s['actor']==c['actor'],'source_context')
        need(moment(s['at'])==moment(c['at']),'source_event_date')
        need(s['assertions_sha256']==digest(f),'assertion_source_binding')
        need(p['evidence_sha256']==digest(s),'evidence_binding')
        out=dict(profile=PROFILE,**FLAGS,request_sha256=digest(request),
                 scope_assessment='supplied_assertions_only',
                 context=deepcopy(c),perspective=role,assertions=deepcopy(f),source=deepcopy(s),
                 debt_as_prior_equity=False,measurements={},journals=[],report=None)
        if s['available_at'] is None:
            return dict(out,status='unresolved',route='source_unavailable',exclusions=[],
                        dependencies=['source_availability_unknown'])
        if moment(s['available_at'])>moment(c['cutoff']):
            return dict(out,status='unresolved',route='source_unavailable',exclusions=[],
                        dependencies=['source_after_cutoff'])
        deps=['actual_source_and_period_authority','tax_method']
        if role=='creditor':
            deps+=['creditor_asset_derecognition','creditor_prior_classification_and_oci',
                   'new_share_recognition_and_measurement']
            if f['creditor_gains_control']=='yes':
                if f['acquired_business']=='yes':
                    deps+=['acquisition_scope_and_measurements','separate_books_method']
                elif f['acquired_business']=='no':deps+=['nonbusiness_acquisition_method']
                else:deps+=['acquired_business_assessment']
            elif f['creditor_gains_control']=='no':deps+=['noncontrolling_investment_relationship_and_method']
            else:deps+=['control_assessment']
            if f['settles_preexisting_relationship']=='yes':
                deps+=['separate_relationship_transaction_and_settlement']
            elif f['settles_preexisting_relationship']=='unknown':
                deps+=['preexisting_relationship_assessment']
            return dict(out,status='conditional_scope',route='creditor_method_required',
                        exclusions=['interpretation19_does_not_address_creditor'],dependencies=sorted(deps))
        exclusions={'original_terms':f['original_terms'],
                    'existing_shareholder_acting_as_owner':both(f['creditor_existing_shareholder'],f['acts_as_owner']),
                    'common_control_equity_substance':both(f['common_control_before_after'],f['equity_distribution_or_contribution'])}
        known=sorted(k for k,v in exclusions.items() if v=='yes')
        unknown=sorted(k for k,v in exclusions.items() if v=='unknown')
        if known:
            deps+=['alternative_debtor_method']
            deps+=['unresolved_other_exclusion:'+k for k in unknown]
            return dict(out,status='conditional_scope',route='debtor_int19_excluded',
                        exclusions=known,dependencies=sorted(deps))
        if f['renegotiated']=='no':
            return dict(out,status='conditional_scope',route='debtor_int19_not_established',
                        exclusions=[],dependencies=sorted(deps+['renegotiated_exchange_not_established']+
                                      ['unresolved_other_exclusion:'+k for k in unknown]))
        if unknown or f['renegotiated']=='unknown':
            deps+=['scope_fact:'+k for k in unknown]
            if f['renegotiated']=='unknown':deps+=['scope_fact:renegotiated']
            return dict(out,status='unresolved',route='debtor_scope_unresolved',
                        exclusions=[],dependencies=sorted(deps))
        deps+=['debtor_equity_classification','equity_fair_value_or_unreliability_then_liability_fair_value',
               'extinguishment_date_measurement','extinguished_carrying_amount','gain_loss_presentation']
        if f['liability_extinguished']!='yes':deps+=['extinguishment_not_established:'+f['liability_extinguished']]
        if f['partial_extinguishment']=='yes':
            deps+=['consideration_allocation','remaining_liability_modification_assessment']
            if f['remaining_terms_modified']=='yes':deps+=['remaining_modification_substantiality']
            elif f['remaining_terms_modified']=='unknown':deps+=['remaining_terms_unknown']
        elif f['partial_extinguishment']=='unknown':deps+=['extinguishment_extent_unknown']
        return dict(out,status='conditional_scope',route='debtor_int19_method_required',
                    exclusions=[],dependencies=sorted(deps))
    except Exception as exc:
        return dict(profile=PROFILE,status='invalid',**FLAGS,reason=str(exc)[:300] or type(exc).__name__)
