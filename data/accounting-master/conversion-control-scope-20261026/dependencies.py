"""Selected source-labelled dependency analysis, never accounting admission."""
from datetime import date
from fractions import Fraction
PROFILE='ConversionScopeDependencies/1'
CONTROL=('power','variable_returns','ability_to_affect_returns')
REVIEWS=('relevant_activities','substantive_and_potential_rights','other_party_rights','principal_agent','timing')
GENERAL=('investment_entity','service_subsidiary','consolidation_exemption','business','common_control')

def need(p,s):
 if not p:raise ValueError(s)
def assessment(v,context,at=None):
 need(type(v)==dict and set(v)=={'status','evidence','subject','as_of'},'assessment_fields')
 need(v['status'] in ('yes','no','unknown'),'status')
 need(v['subject']==[context['holder'],context['issuer']],'assessment_subject')
 date.fromisoformat(v['as_of']);need(at is None or v['as_of']==at,'assessment_date')
 need(type(v['evidence'])==list and all(type(s)==str and s.strip() for s in v['evidence']),'evidence_list')
 need(v['status']=='unknown' or bool(v['evidence']),'missing_evidence')
 return v['status']
def control(record,context):
 need(set(record)=={'as_of','elements','reviews'},'control_record')
 date.fromisoformat(record['as_of']);need(set(record['elements'])==set(CONTROL) and set(record['reviews'])==set(REVIEWS),'control_population')
 elements=[assessment(v,context,record['as_of']) for v in record['elements'].values()]
 reviews=[assessment(v,context,record['as_of']) for v in record['reviews'].values()]
 if any(x!='yes' for x in reviews):return 'unresolved'
 if 'no' in elements:return 'not_controlled_under_supplied_assessments'
 if 'unknown' in elements:return 'unresolved'
 return 'controlled_under_supplied_assessments'

def evaluate(body):
 need(set(body)=={'profile','context','conversion_date','votes','control_before','control_after','report','assessments','separate_policy','measurements','authority'},'body_fields')
 need(body['profile']==PROFILE,'profile');ct=body['context'];need(set(ct)=={'holder','issuer','basis','period_start'},'context')
 need(all(type(v)==str and v.strip() for v in ct.values()) and ct['holder']!=ct['issuer'],'context_values')
 need(ct['basis']=='conditional_AASB_design','basis');date.fromisoformat(ct['period_start']);conversion=date.fromisoformat(body['conversion_date'])
 votes=body['votes'];need(set(votes)=={'received','total'},'votes');need(all(type(x)==int for x in votes.values()) and 0<=votes['received']<=votes['total'] and votes['total']>0,'vote_range')
 before=control(body['control_before'],ct);after=control(body['control_after'],ct)
 need(date.fromisoformat(body['control_before']['as_of'])<conversion<=date.fromisoformat(body['control_after']['as_of']),'control_date_order')
 need(body['report'] in ('separate','consolidated'),'report')
 need(set(body['assessments'])==set(GENERAL),'general_population')
 a={k:assessment(v,ct,body['control_after']['as_of']) for k,v in body['assessments'].items()}
 need(body['separate_policy'] in ('unknown','cost','AASB9','equity_method'),'separate_policy')
 need(type(body['measurements'])==dict and all(type(k)==str and type(v)==str and v.strip() for k,v in body['measurements'].items()),'measurement_evidence')
 auth=body['authority'];need(set(auth)=={'status','evidence','period_start','basis'},'authority_fields');need(auth['status'] in ('unresolved','supplied_for_review'),'authority_status');need(auth['period_start']==ct['period_start'] and auth['basis']==ct['basis'],'authority_context');need(type(auth['evidence'])==list and all(type(x)==str and x.strip() for x in auth['evidence']),'authority_evidence')
 need(auth['status']=='unresolved' or bool(auth['evidence']),'authority_evidence_missing')
 missing=['actual_contract_terms','actual_source_admission','accounting_authority_admission'];routes=[]
 if auth['status']=='unresolved':missing.append('dated_entity_specific_authority_chain')
 if before=='unresolved':missing.append('preconversion_control_assessment')
 timing='unresolved' if before=='unresolved' or after=='unresolved' else 'already_controlled_before_conversion' if before.startswith('controlled') else 'gain_of_control_possible_at_or_before_after_assessment' if after.startswith('controlled') else 'no_control_established'
 if after=='unresolved':routes=['control_unresolved'];missing.append('postconversion_control_assessment')
 elif not after.startswith('controlled'):
  routes=['other_interest_scope_assessment'];missing+=['joint_control_or_significant_influence_or_financial_asset_scope']
 else:
  if timing!='already_controlled_before_conversion':missing.append('evidenced_actual_control_acquisition_date')
  ie=a['investment_entity'];service=a['service_subsidiary']
  fv=ie=='yes' and service=='no'
  if ie=='unknown' or (ie=='yes' and service=='unknown'):
   routes=['investment_entity_exception_unresolved'];missing+=['investment_entity_and_service_subsidiary_assessment']
  elif fv:
   routes=['investment_entity_fair_value_scope'];missing.append('fair_value_at_required_dates')
  elif body['report']=='separate':
   if body['separate_policy']=='unknown':routes=['separate_policy_unresolved'];missing.append('consistent_category_measurement_policy')
   else:routes=['separate_'+body['separate_policy']];missing.append({'cost':'supported_initial_cost','AASB9':'AASB9_classification_and_measurement','equity_method':'equity_method_inputs'}[body['separate_policy']])
  elif a['consolidation_exemption']=='unknown':routes=['consolidation_exemption_unresolved'];missing.append('complete_consolidation_exemption_assessment')
  elif a['consolidation_exemption']=='yes':routes=['supplied_consolidation_exemption'];missing.append('separate_statement_requirements_and_policy')
  else:
   routes=['consolidation_scope'];missing+=['acquisition_period_membership','uniform_policies_and_dates','intragroup_eliminations','NCI_ownership_and_return_rights']
   if timing=='already_controlled_before_conversion':routes+=['continued_control_conversion'];missing+=['conversion_effects_on_existing_group_and_NCI']
   elif a['business']=='unknown' or a['common_control']=='unknown':routes+=['acquisition_route_unresolved'];missing+=['business_and_common_control_assessments']
   elif a['common_control']=='yes':routes+=['common_control_outside_AASB3'];missing+=['applicable_common_control_policy']
   elif a['business']=='no':routes+=['asset_acquisition'];missing+=['asset_liability_recognition_and_relative_fair_values']
   else:routes+=['business_combination'];missing+=['acquirer_identification','acquisition_date_identifiable_net_assets','consideration_measurement','NCI_measurement','previous_interest_measurement','goodwill_or_bargain_purchase_analysis']
 measurement_fields={'fair_value_at_required_dates','supported_initial_cost','AASB9_classification_and_measurement','equity_method_inputs','acquisition_date_identifiable_net_assets','consideration_measurement','NCI_measurement','previous_interest_measurement','asset_liability_recognition_and_relative_fair_values'}
 measurements=body['measurements'];need(set(measurements)<=measurement_fields,'unsupported_measurement_field')
 missing=[x for x in missing if x not in measurements]
 return {'profile':PROFILE,'source_admission':False,'accounting_admission':False,'posting_authorized':False,'control_before':before,'control_after':after,'timing':timing,'routes':routes,'missing':sorted(set(missing)),'vote_fraction_descriptive':str(Fraction(votes['received'],votes['total'])),'scope':'Dependency routing under supplied source-labelled assessments; no fact adjudication or journal measurement.'}
