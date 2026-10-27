"""Independently specified expected routes and dependencies for finite cases."""
from copy import deepcopy
from hashlib import sha256
import json
PROFILE='ConditionalDebtRelationshipScope/1'
def digest(x):return sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
DEFAULT={'renegotiated':'yes','original_terms':'no','creditor_existing_shareholder':'no',
 'acts_as_owner':'no','common_control_before_after':'no','equity_distribution_or_contribution':'no',
 'liability_extinguished':'yes','partial_extinguishment':'no','remaining_terms_modified':'no',
 'creditor_gains_control':'no','acquired_business':'yes','settles_preexisting_relationship':'no'}
BASE=['actual_source_and_period_authority','tax_method']
DEBTOR=BASE+['debtor_equity_classification','equity_fair_value_or_unreliability_then_liability_fair_value',
 'extinguishment_date_measurement','extinguished_carrying_amount','gain_loss_presentation']
CREDITOR=BASE+['creditor_asset_derecognition','creditor_prior_classification_and_oci','new_share_recognition_and_measurement']
def request(role='debtor',changes=None,availability='2026-10-27T00:00:00Z'):
    f={**DEFAULT,**(changes or {})};subject='S' if role=='debtor' else 'P'
    c=dict(debtor='S',creditor='P',subject=subject,actor='researcher',
           at='2026-10-27T00:00:00Z',cutoff='2026-10-27T01:00:00Z')
    s=dict(text='Synthetic debtor-own-share exchange premises; no actual company evidence.',
           rationale='Explicit fixture assertions to discriminate rule scope; not an assessment of facts.',
           subject=subject,actor='researcher',at=c['at'],available_at=availability,assertions_sha256=digest(f))
    p=dict(context=c,perspective=role,transaction='debt_for_debtor_own_shares',prior_instrument='debt',
           assertions=f,source=s,evidence_sha256=digest(s))
    return dict(profile=PROFILE,payload=p,expected_payload_sha256=digest(p))
def bind(r):
    p=r['payload'];p['source']['assertions_sha256']=digest(p['assertions']);p['evidence_sha256']=digest(p['source']);r['expected_payload_sha256']=digest(p);return r
def expected(r,status,route,deps,excluded=()):
    p=r['payload']
    return dict(profile=PROFILE,source_admission=False,accounting_admission=False,
      posting_authorized=False,report_authorized=False,request_sha256=digest(r),
      scope_assessment='supplied_assertions_only',context=deepcopy(p['context']),
      perspective=p['perspective'],assertions=deepcopy(p['assertions']),source=deepcopy(p['source']),
      debt_as_prior_equity=False,measurements={},journals=[],report=None,
      status=status,route=route,dependencies=sorted(deps),exclusions=list(excluded))
def cases():
    rows=[]
    def add(name,r,status,route,deps,excluded=()):rows.append(dict(id=name,request=r,expected=expected(r,status,route,deps,excluded)))
    add('debtor_full',request(),'conditional_scope','debtor_int19_method_required',DEBTOR)
    add('creditor_noncontrol',request('creditor'),'conditional_scope','creditor_method_required',CREDITOR+['noncontrolling_investment_relationship_and_method'],['interpretation19_does_not_address_creditor'])
    add('original_terms',request(changes={'original_terms':'yes'}),'conditional_scope','debtor_int19_excluded',BASE+['alternative_debtor_method'],['original_terms'])
    add('owner_capacity',request(changes={'creditor_existing_shareholder':'yes','acts_as_owner':'yes'}),'conditional_scope','debtor_int19_excluded',BASE+['alternative_debtor_method'],['existing_shareholder_acting_as_owner'])
    add('shareholder_alone',request(changes={'creditor_existing_shareholder':'yes'}),'conditional_scope','debtor_int19_method_required',DEBTOR)
    add('common_control_equity',request(changes={'common_control_before_after':'yes','equity_distribution_or_contribution':'yes'}),'conditional_scope','debtor_int19_excluded',BASE+['alternative_debtor_method'],['common_control_equity_substance'])
    add('common_control_alone',request(changes={'common_control_before_after':'yes'}),'conditional_scope','debtor_int19_method_required',DEBTOR)
    add('unknown_substance',request(changes={'common_control_before_after':'yes','equity_distribution_or_contribution':'unknown'}),'unresolved','debtor_scope_unresolved',BASE+['scope_fact:common_control_equity_substance'])
    add('known_exclusion_unknown_other',request(changes={'original_terms':'yes','common_control_before_after':'yes','equity_distribution_or_contribution':'unknown'}),'conditional_scope','debtor_int19_excluded',BASE+['alternative_debtor_method','unresolved_other_exclusion:common_control_equity_substance'],['original_terms'])
    add('unknown_renegotiation',request(changes={'renegotiated':'unknown'}),'unresolved','debtor_scope_unresolved',BASE+['scope_fact:renegotiated'])
    add('no_renegotiation',request(changes={'renegotiated':'no'}),'conditional_scope','debtor_int19_not_established',BASE+['renegotiated_exchange_not_established'])
    add('partial_modified',request(changes={'partial_extinguishment':'yes','remaining_terms_modified':'yes'}),'conditional_scope','debtor_int19_method_required',DEBTOR+['consideration_allocation','remaining_liability_modification_assessment','remaining_modification_substantiality'])
    add('partial_unknown_terms',request(changes={'partial_extinguishment':'yes','remaining_terms_modified':'unknown'}),'conditional_scope','debtor_int19_method_required',DEBTOR+['consideration_allocation','remaining_liability_modification_assessment','remaining_terms_unknown'])
    add('unknown_extent',request(changes={'partial_extinguishment':'unknown'}),'conditional_scope','debtor_int19_method_required',DEBTOR+['extinguishment_extent_unknown'])
    for v in ['no','unknown']:
        add('not_extinguished_'+v,request(changes={'liability_extinguished':v}),'conditional_scope','debtor_int19_method_required',DEBTOR+['extinguishment_not_established:'+v])
    add('creditor_acquisition',request('creditor',{'creditor_gains_control':'yes','settles_preexisting_relationship':'yes'}),'conditional_scope','creditor_method_required',CREDITOR+['acquisition_scope_and_measurements','separate_books_method','separate_relationship_transaction_and_settlement'],['interpretation19_does_not_address_creditor'])
    add('creditor_nonbusiness',request('creditor',{'creditor_gains_control':'yes','acquired_business':'no'}),'conditional_scope','creditor_method_required',CREDITOR+['nonbusiness_acquisition_method'],['interpretation19_does_not_address_creditor'])
    add('creditor_unknown_business',request('creditor',{'creditor_gains_control':'yes','acquired_business':'unknown'}),'conditional_scope','creditor_method_required',CREDITOR+['acquired_business_assessment'],['interpretation19_does_not_address_creditor'])
    add('creditor_unknown_control_relationship',request('creditor',{'creditor_gains_control':'unknown','settles_preexisting_relationship':'unknown'}),'conditional_scope','creditor_method_required',CREDITOR+['control_assessment','preexisting_relationship_assessment'],['interpretation19_does_not_address_creditor'])
    for role in ['debtor','creditor']:
        add('late_'+role,request(role,availability='2026-10-27T02:00:00Z'),'unresolved','source_unavailable',['source_after_cutoff'])
        add('unknown_availability_'+role,request(role,availability=None),'unresolved','source_unavailable',['source_availability_unknown'])
    return rows
