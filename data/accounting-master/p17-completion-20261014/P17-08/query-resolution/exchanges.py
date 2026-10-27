"""Author exact request/expected-result exchanges; validate mathematical contrasts."""
from pathlib import Path
from fractions import Fraction as F
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4]
case=json.loads((OUT/'query-cases.json').read_text())
deps=json.loads((OUT/'dependency-manifest.json').read_text())['dependencies']
request_context={'schema':'query-resolution-documentary.v1','purpose':'specified request/result oracle, no runtime execution','layer':'conditional mathematical consequence','unit':'currency units','evidence':'authored-case@1','economic_scope':'explicitly_limited','dependency_manifest_sha256':hashlib.sha256((OUT/'dependency-manifest.json').read_bytes()).hexdigest()}
rows=[]
def add(i,request,expected):
 rows.append({'id':i,'request':dict(request_context,**request),'expected':expected})
add('Q01',{'model':'rounded-debt-real@1','query':'future-interest','operation_order':['exact_constraints','project'],'budget':{'declared_cells':1}}, {'status':'exact_image','existence':'witness','declared_search':'complete','formulation_complete':True,'lower':{'value':'4.975','included':True,'attained':True,'witness':{'F':'99.5','V':'0'}},'upper':{'value':'7.035','included':False,'attained':False,'witness':None},'proof':'query-resolution-supplement-20261014.md:Finite cases and derivation'})
add('Q02',{'model':'rounded-debt-real@1','query':'future-interest-cents','operation_order':['exact_constraints','project','round_nearest_half_away'],'quantum':'0.01','budget':{'declared_cells':1}}, {'status':'exact_finite_image','minimum':'4.98','maximum':'7.03','step':'0.01','count':206,'both_attained':True,'witnesses':'rounded-witnesses.json','input_domain_unchanged':True})
add('Q03',{'model':'rounded-debt-integer-principal@1','query':'future-interest','operation_order':['restrict_principals_to_cents','exact_constraints','project'],'input_quantum':'0.01','budget':{'assignments':1000050}}, {'status':'exact_finite_image','minimum':'4.975','maximum':'7.0343','both_attained':True,'maximum_witness':{'F':'0','V':'100.49'},'equivalent_to_real_model':False})
add('Q04',{'model':'single-value-enclosure@1','query':'one_posting','enclosure':['1.0049','1.0051'],'rounding':'nearest_half_away','quantum':'0.01'}, {'status':'rounding_unresolved','posting':None,'diagnostic_possible_outputs':['1.00','1.01'],'next_action':'refine_enclosure_within_budget_or_retain_unresolved'})
add('Q05',{'model':'same_range_as_exact_set@1','query':'all_possible_rounded_values','exact_set':['1.0049','1.0051'],'endpoints_included':[True,True],'rounding':'nearest_half_away','quantum':'0.01'}, {'status':'exact_finite_image','values':['1.00','1.01'],'one_actual_posting_established':False})
add('Q06',{'model':'rounded-debt-real@1','query':'future-interest-cents','rounding':None,'quantum':'0.01'}, {'status':'ROUNDING_RULE_UNRESOLVED','value':None,'family_effect':'unchanged'})
add('Q07',{'model':'zero-principal@1','query':'fixed_share','F':'0','V':'0','expression':'F/(F+V)'}, {'status':'UNDEFINED_MATHEMATICS','value':None,'reason':'denominator is established zero'})
add('Q08',{'model':'possibly-zero-principal@1','query':'fixed_share','expression':'F/(F+V)','nonzero_guard':'not_established'}, {'status':'PRECONDITION_UNRESOLVED','value':None,'family_effect':'unchanged'})
add('Q09',{'model':'two-cell-family@1','query':'full_range','budget':{'declared_cells':0},'partition':['timely@1','late@1']}, {'status':'BUDGET_EXHAUSTED','existence':'unknown','declared_search':'not_started','formulation_complete':True,'unresolved_regions':['timely@1','late@1'],'full_range':None})
add('Q10',{'model':'two-cell-family@1','query':'year1_equity','budget':{'declared_cells':1},'visited':['timely@1'],'unvisited':['late@1']}, {'status':'BUDGET_EXHAUSTED','existence':'witness','declared_search':'partial','formulation_complete':True,'known_values':{'timely@1':'83'},'unresolved_regions':['late@1'],'full_range':None})
add('Q11',{'model':'two-valid-treaty-histories@1','query':'year1_equity','reuse_projection':'terminal_cash@1','old_outputs':['terminal_cash'],'new_outputs':['year1_equity'],'retained_detail':['timely@1','late@1']}, {'status':'RESOLUTION_REVALIDATION_REQUIRED','old_projection_value':'88.3','new_value':None,'detail_preserved':True,'next_action':'refine_under_new_query_version'})
add('Q12',{'model':'bank-funded-summary@1','query':'funded_allowance','gross_loan':'100','original_credit_history':None,'original_detail_status':'never_preserved'}, {'status':'DETAIL_UNAVAILABLE','measurement_status':'unresolved','allowance':None,'fabricated_stage':None})
add('Q13',{'model':'two-valid-treaty-histories@1','query':'year1_equity_mean','law':'timing-hypotheses-authored@1','posterior':['3/11','8/11'],'evaluated':['timely@1'],'unresolved':['late@1']}, {'status':'unresolved','known_contribution':'249/11','known_mass':'3/11','unresolved_mass':'8/11','unconditional_mean':None,'successful_conditional_mean':None})
add('Q14',{'model':'two-valid-treaty-histories@1','query':'year1_equity_mean_conditional_on_success','law':'timing-hypotheses-authored@1','conditioning_event':['timely@1']}, {'status':'exact_conditional_value','value':'83','conditioning_mass':'3/11','answers_unconditional_query':False})
add('Q15',{'model':'wrong-pool-proposal@1','query':'accounting_equity','treatment':'net_profitable_and_onerous_groups'}, {'status':'TREATMENT_UNSUPPORTED','law_atom_added':False,'accounting_value':None,'retained_proposal':True})
add('Q16',{'model':'rounded-debt-real@2','query':'future-interest','resume_from':'rounded-debt-real@1/receipt@1','changed_dependency':'new admitted evidence narrows F'}, {'status':'STALE_CONTINUATION','new_result':None,'old_result_preserved':True,'next_action':'new_request_or_explicit_frozen_query'})
add('Q17',{'model':'symbolic-rate-principal@1','query':'interest','expression':'unknown_rate*unknown_principal','backend':'rational-affine@1'}, {'status':'OPERATION_UNSUPPORTED','value':None,'original_expression_retained':True,'partial_linearization_admitted':False})
(OUT/'request-result-exchanges.json').write_text(json.dumps({'schema':'query-resolution-exchanges.v1','examples':rows},indent=2)+'\n')
# Validate the substantive receipt relations using independently checked case outputs.
checks=[]
def ck(n,v):checks.append({'name':n,'passed':bool(v)})
lookup={r['id']:r for r in rows};q1=lookup['Q01']['expected'];q2=lookup['Q02']['expected']
ck('strict_supremum_never_has_witness',not q1['upper']['attained'] and q1['upper']['witness'] is None)
ck('rounding_count_matches_discrete_image',(F(q2['maximum'])-F(q2['minimum']))/F(q2['step'])+1==q2['count'])
ck('integer_max_below_real_supremum',F(lookup['Q03']['expected']['maximum'])<F(q1['upper']['value']))
ck('one_value_vs_set_same_enclosure',lookup['Q04']['expected']['posting'] is None and len(lookup['Q05']['expected']['values'])==2)
ck('partial_witness_not_full_range',lookup['Q10']['expected']['existence']=='witness' and lookup['Q10']['expected']['full_range'] is None)
ck('known_contribution_has_original_mass',F(lookup['Q13']['expected']['known_contribution'])==F(83)*F('3/11'))
ck('partial_mass_conserved',F(lookup['Q13']['expected']['known_mass'])+F(lookup['Q13']['expected']['unresolved_mass'])==1)
ck('success_conditioning_declared',lookup['Q14']['request']['conditioning_event']==['timely@1'] and not lookup['Q14']['expected']['answers_unconditional_query'])
ck('changed_query_refuses_old_scalar',lookup['Q11']['expected']['new_value'] is None and lookup['Q11']['expected']['detail_preserved'])
ck('invalid_treatment_not_probability_atom',not lookup['Q15']['expected']['law_atom_added'])
ck('missing_original_risk_does_not_reset_stage',lookup['Q12']['expected']['allowance'] is None and lookup['Q12']['expected']['fabricated_stage'] is None)
ck('revision_preserves_old_result',lookup['Q16']['expected']['old_result_preserved'])
ck('not_a_solver_execution',all(r['request']['purpose']=='specified request/result oracle, no runtime execution' for r in rows))
result={'passed':all(r['passed'] for r in checks),'check_count':len(checks),'checks':checks,'receipt_count':len(rows),'scope':'Authored semantic receipt comparisons, not API execution'}
(OUT/'exchange-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'receipts':len(rows),'checks':len(checks),'passed':result['passed']}))
if not result['passed']:raise SystemExit(1)
