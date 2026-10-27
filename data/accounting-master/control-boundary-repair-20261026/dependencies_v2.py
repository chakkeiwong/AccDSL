"""Control endpoint and interval dependencies; never accounting admission."""
from copy import deepcopy
from datetime import date
from hashlib import sha256
from pathlib import Path
import re
import baseline

PROFILE='ConversionScopeDependencies/2'
BASE_SHA='3d1bd10d71949357da34c030b4d6fad755a1c933c877699b70296d7c4a1b1553'
CONTROL=baseline.CONTROL
REVIEWS=baseline.REVIEWS
GENERAL=baseline.GENERAL

def calendar(value):
    if type(value) is not str or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',value):
        raise ValueError('canonical_calendar_date')
    date.fromisoformat(value)

def closed(value,fields,label):
    if type(value) is not dict or set(value)!=set(fields):
        raise ValueError(label+'_fields')

def evaluate(body):
    if sha256(Path(baseline.__file__).read_bytes()).hexdigest()!=BASE_SHA:
        raise ValueError('baseline_hash')
    closed(body,['profile','context','conversion_date','votes','control_before','control_after','report','assessments','separate_policy','measurements','authority'],'body')
    if body['profile']!=PROFILE:raise ValueError('profile')
    calendar(body['conversion_date'])
    closed(body['context'],['holder','issuer','basis','period_start'],'context')
    calendar(body['context']['period_start'])
    closed(body['authority'],['status','evidence','period_start','basis'],'authority')
    calendar(body['authority']['period_start'])
    closed(body['assessments'],GENERAL,'assessments')
    assertions=list(body['assessments'].values())
    for key in ['control_before','control_after']:
        row=body[key]
        closed(row,['as_of','elements','reviews'],'control')
        calendar(row['as_of'])
        closed(row['elements'],CONTROL,'elements')
        closed(row['reviews'],REVIEWS,'reviews')
        assertions+=list(row['elements'].values())+list(row['reviews'].values())
    for row in assertions:
        closed(row,['status','evidence','subject','as_of'],'assessment')
        calendar(row['as_of'])
    request=deepcopy(body);request['profile']=baseline.PROFILE
    original=baseline.evaluate(request)
    result=deepcopy(original);result['profile']=PROFILE
    statuses={'controlled_under_supplied_assessments':'yes',
              'not_controlled_under_supplied_assessments':'no','unresolved':'unknown'}
    a=statuses[original['control_before']];b=statuses[original['control_after']]
    alternatives={('yes','yes'):['continuous_control','loss_and_regain'],
                  ('yes','no'):['loss','loss_gain_loss_or_more'],
                  ('no','yes'):['gain','gain_loss_gain_or_more'],
                  ('no','no'):['no_control_throughout','gain_and_loss']}
    possible=[]
    for x in (['yes','no'] if a=='unknown' else [a]):
        for y in (['yes','no'] if b=='unknown' else [b]):possible+=alternatives[x,y]
    result['possible_history_classes']=sorted(set(possible))
    result['interval_history']='unresolved'
    result['required_transitions']=['at_least_one_gain'] if (a,b)==('no','yes') else ['at_least_one_loss'] if (a,b)==('yes','no') else []
    result['timing']=('endpoint_control_unresolved' if 'unknown' in (a,b) else
                      'controlled_at_both_assessments' if (a,b)==('yes','yes') else
                      'gain_between_assessments' if (a,b)==('no','yes') else
                      'loss_between_assessments' if (a,b)==('yes','no') else
                      'not_controlled_at_either_assessment')
    missing=set(original['missing'])
    missing.add('complete_control_history_between_assessments')
    missing.discard('evidenced_actual_control_acquisition_date')
    missing.discard('conversion_effects_on_existing_group_and_NCI')
    routes=list(original['routes'])
    if routes and routes[0]=='consolidation_scope':
        routes=['consolidation_scope','control_history_unresolved']
        # A new acquisition, uninterrupted control, and loss/regain must not
        # be silently selected from two snapshots. Retain their conditional
        # requirements separately and with their applicability predicates.
        acquisition_keys={'business_and_common_control_assessments','applicable_common_control_policy',
          'asset_liability_recognition_and_relative_fair_values','acquirer_identification',
          'acquisition_date_identifiable_net_assets','consideration_measurement','NCI_measurement',
          'previous_interest_measurement','goodwill_or_bargain_purchase_analysis'}
        missing-=acquisition_keys
    result['routes']=routes
    requirements=[]
    def candidate(name,when,fields):
        requirements.append(dict(route=name,when=when,missing=sorted(set(fields)),
                                 supplied_measurement_references={k:v for k,v in body['measurements'].items() if k in fields}))
    if any('gain' in h for h in possible):
        candidate('gain_of_control_assessment','if a gain of control occurs',[
          'evidenced_control_gain_date','reporting_context_and_entity_status_at_gain',
          'business_and_common_control_assessments_at_gain','applicable_acquisition_policy',
          'acquisition_date_measurement_and_previous_interest_analysis'])
    if any('loss' in h for h in possible):
        candidate('loss_of_control_assessment','if a loss of control occurs',[
          'evidenced_control_loss_date','reporting_context_and_entity_status_at_loss',
          'deconsolidation_or_investment_measurement_method',
          'consideration_retained_interest_NCI_and_OCI_analysis'])
    if 'continuous_control' in possible:
        candidate('continued_control_conversion','if control is uninterrupted and conversion changes ownership',[
          'evidence_of_uninterrupted_control','conversion_effects_on_existing_group_and_NCI'])
    # These are requirements for a possible consolidated acquisition, not a
    # decision that one occurred or that the current entity status held then.
    if any('gain' in h for h in possible):
        arow=body['assessments']
        business=arow['business']['status'];common=arow['common_control']['status']
        branch='acquisition_route_unresolved'
        fields=['business_and_common_control_assessments_at_gain']
        if common=='yes':branch='common_control_outside_AASB3';fields=['applicable_common_control_policy']
        elif common=='no' and business=='no':branch='asset_acquisition';fields=['asset_liability_recognition_and_relative_fair_values']
        elif common=='no' and business=='yes':
            branch='business_combination';fields=['acquirer_identification','acquisition_date_identifiable_net_assets','consideration_measurement','NCI_measurement','previous_interest_measurement','goodwill_or_bargain_purchase_analysis']
        candidate(branch,'if consolidation follows a gain and current business/common-control assessments also apply at that gain',fields)
    # A supplied reference is a claimed evidence location, not a verified
    # measurement. Keep prerequisites visible instead of deleting them.
    for key in body['measurements']:
        if key not in original['missing']:missing.add(key)
    result['missing']=sorted(missing)
    result['conditional_dependencies']=requirements
    result['measurement_references_for_review']=deepcopy(body['measurements'])
    result['scope']='Dependency routing under supplied endpoint assessments; interval history and all source/measurement admission remain unresolved.'
    return result
