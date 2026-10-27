"""Authored premises and expected values; no calculator import."""
from copy import deepcopy
CASES = []
def add(key, inp, detail=None, codes=(), refusal=None, prior=()):
    CASES.append(dict(id=key,input=deepcopy(inp),detail=deepcopy(detail),diagnostics=sorted(codes),status='unresolved' if codes else 'resolved',refusal=refusal,prior=list(prior)))
def changed(v, **kw): return dict(v,**kw)

route = dict(method_id='transition.route@1',initial_application='2023-01-01',adjusted_comparatives=['2022-01-01'],object_type='issued_group',requested='full',impracticable='no',reasonable_effort='documented',historical_evidence='contemporaneous',modified_information='available',direct_participation=False,prospective_mitigation=False,mitigation_used_before_transition=False)
def rd(routes, selected, date='2022-01-01'): return dict(transition_date=date,permitted_routes=routes,selected_route=selected,measurements_performed=False)
add('route.full',route,rd(['full'],'full'))
add('route.earlier',changed(route,adjusted_comparatives=['2022-01-01','2020-01-01','2021-01-01']),rd(['full'],'full','2020-01-01'))
add('route.later-estimate-contemporaneous-support',route,rd(['full'],'full'))
modified=changed(route,impracticable='yes',requested='modified',historical_evidence='permitted_transition')
add('route.modified',modified,rd(['modified','fair'],'modified'))
add('route.fair',changed(modified,requested='fair',modified_information='unavailable'),rd(['fair'],'fair'))
c5a=changed(route,requested='fair',direct_participation=True,prospective_mitigation=True,mitigation_used_before_transition=True)
add('route.c5a',c5a,rd(['full','fair'],'fair'))
add('route.acquisition-c5b',changed(modified,object_type='acquisition_asset'),rd(['modified','fair'],'modified'))
add('route.unknown-impracticability',changed(route,impracticable='unknown',requested='fair'),rd([],None),['IMPRACTICABILITY_UNRESOLVED'])
add('route.missing-workbook-alone',changed(modified,reasonable_effort='not_documented'),rd([],None),['IMPRACTICABILITY_UNRESOLVED'])
add('route.unknown-modified-information',changed(modified,modified_information='unknown'),rd(['fair'],None),['MODIFIED_INFORMATION_UNRESOLVED'])
add('route.historical-unknown',changed(route,historical_evidence='unknown'),rd(['full'],None),['HISTORICAL_EVIDENCE_UNRESOLVED'])
for key,inp,code in [
 ('route.fair-without-exception',changed(route,requested='fair'),'ROUTE_NOT_PERMITTED'),
 ('route.c5a-missing-condition',changed(c5a,mitigation_used_before_transition=False),'ROUTE_NOT_PERMITTED'),
 ('route.acquisition-not-c5a',changed(c5a,object_type='acquisition_asset'),'ROUTE_NOT_PERMITTED'),
 ('route.hindsight',changed(route,historical_evidence='hindsight'),'HINDSIGHT_FORBIDDEN'),
 ('route.no-modified-information',changed(modified,modified_information='unavailable'),'ROUTE_NOT_PERMITTED'),
 ('route.full-missing-history',changed(route,historical_evidence='permitted_transition'),'FULL_HISTORICAL_SUPPORT_REQUIRED')]: add(key,inp,refusal=code)

recovery = dict(method_id='transition.recovery@1',underlying_recognition='2020-07-01',treaty_entry='2020-10-01',transition_date='2022-01-01',mode='transition',remaining_coverage=True,recognition_admission='admitted',covered_group='group.B',coverage_allocation='admitted',group_loss='20',covered_loss='20',expected_share='3/5',measured_held_asset='50')
def rec(amount, exception=True): return dict(loss_recovery=amount,measured_held_asset='50',held_asset_derived=False,timing_exception=exception)
add('recovery.transition',recovery,rec('12'))
add('recovery.partial-coverage',changed(recovery,covered_loss='10'),rec('6'))
add('recovery.ordinary-on-time',changed(recovery,treaty_entry='2020-06-01',mode='ordinary_initial'),rec('12',False))
add('recovery.unknown-allocation',changed(recovery,coverage_allocation='unknown'),rec(None),['COVERAGE_ALLOCATION_UNRESOLVED'])
add('recovery.unknown-admission',changed(recovery,recognition_admission='unknown'),rec(None),['LOSS_RECOVERY_ADMISSION_UNRESOLVED'])
add('recovery.ordinary-too-late',changed(recovery,mode='ordinary_initial'),refusal='LOSS_RECOVERY_TIMING')
add('recovery.excess-covered-loss',changed(recovery,covered_loss='21'),refusal='INVALID_RECOVERY_INPUT')

opening = dict(method_id='transition.opening@1',transition_date='2022-01-01',groups=[dict(group_id='group.A',fcf='90',fair_value='110',old_liability='105'),dict(group_id='group.B',fcf='120',fair_value='100',old_liability='115')],other_assets='500',old_held_asset='0',new_held_asset='0',embedded_recovery='0',tax='uncomputed',fx='absent',accumulated_oci='excluded')
opd = dict(groups=[dict(group_id='group.A',csm='20',loss_component='0',liability='110'),dict(group_id='group.B',csm='0',loss_component='20',liability='120')],old_equity='280',new_equity='270',opening_equity_change='-10',liability='230',cash_change='0',current_profit='0',held_asset='0')
add('opening.groupwise',opening,opd)
add('opening.with-embedded-recovery',changed(opening,old_held_asset='45',new_held_asset='50',embedded_recovery='12'),changed(opd,old_equity='325',new_equity='320',opening_equity_change='-5',held_asset='50'),prior=['recovery.transition'])

triangle = dict(method_id='triangle.inspect@1',triangle_id='triangle.3',valuation_date='2022-12-31',origins=[2020,2021,2022],cumulative=[['100','150','180'],['120','180',None],['140',None,None]],structural_missing=[[False,False,False],[False,False,True],[False,True,True]],development_unit='year',tail_factor='1',observation_model='volume_chainladder_no_tail')
add('triangle.perfect-fit',triangle,dict(factors=['3/2','6/5'],point_reserve='148',observed_cells=6,parameter_count=5,residual_degrees=1,raw_dispersion='0',predictive_status='dispersion_unresolved',triangle_sha256='INPUT_SHA',risk_adjustment=None),['DISPERSION_UNRESOLVED'])
add('triangle.unadmitted-tail',changed(triangle,tail_factor='11/10'),refusal='UNSUPPORTED_TAIL')

def draw(key,mean,outs,failure=None):
    return dict(draw_id='draw.'+key,fit_id='fit.'+key,probability='1/2',mean_per_cell=mean,failure=failure,outcomes=[dict(probability=p,cells=xs) for p,xs in outs])
law = dict(method_id='estimation.predict@1',triangle_id='triangle.3',process_law_id='law.A',conditioning='full_triangle',horizon='lifetime_payments',fit_dependence='shared',failure_policy='retain_all_attempts',threshold='8',draws=[draw('low','2',[('1/2',['0']),('1/2',['4'])]),draw('high','8',[('1/2',['4']),('1/2',['12'])])])
def pred(mu,var,tail,dist): return dict(attempted_draws=2,failed_draw_ids=[],known_mass='1',unresolved_mass='0',known_mean_contribution=mu,mean=mu,variance=var,tail_probability=tail,full_distribution=[dict(amount=x,probability=p) for x,p in dist],calibration='not_evaluated')
add('predict.law-A',law,pred('5','19','1/4',[('0','1/4'),('4','1/2'),('12','1/4')]))
add('predict.law-B',changed(law,process_law_id='law.B',draws=[draw('low','2',[('4/5',['1']),('1/5',['6'])]),draw('high','8',[('4/5',['6']),('1/5',['16'])])]),pred('5','19','1/10',[('1','2/5'),('6','1/2'),('16','1/10')]))
shared = changed(law,process_law_id='law.A.shared-two',draws=[draw('low','2',[('1/4',['0','0']),('1/4',['0','4']),('1/4',['4','0']),('1/4',['4','4'])]),draw('high','8',[('1/4',['4','4']),('1/4',['4','12']),('1/4',['12','4']),('1/4',['12','12'])])])
add('predict.shared-fit-two-cells',shared,pred('10','56','3/8',[('0','1/8'),('4','1/4'),('8','1/4'),('16','1/4'),('24','1/8')]))
add('predict.failed-fit-retained',changed(law,draws=[law['draws'][0],draw('high','8',[],'FIT_DENOMINATOR_ZERO')]),dict(attempted_draws=2,failed_draw_ids=['draw.high'],known_mass='1/2',unresolved_mass='1/2',known_mean_contribution='1',mean=None,variance=None,tail_probability=None,full_distribution=[],calibration='not_evaluated'),['FAILED_DRAW_MASS_UNRESOLVED'])
badmass=deepcopy(law); badmass['draws'][0]['probability']='2/3'
add('predict.invalid-mass',badmass,refusal='INVALID_LAW_MASS')
badmean=deepcopy(law); badmean['draws'][0]['outcomes'][0]['cells']=['1']
add('predict.wrong-process-mean',badmean,refusal='PROCESS_MEAN_MISMATCH')

back = dict(method_id='backward.condition@1',triangle_id='triangle.backward',backward_law_id='joint.backward-v1',observed_y='3',prior=[dict(x='1',probability='1/2'),dict(x='2',probability='1/2')],forward=[dict(x='1',outcomes=[dict(y='1',probability='1/2'),dict(y='3',probability='1/2')]),dict(x='2',outcomes=[dict(y='3',probability='2/3'),dict(y='6',probability='1/3')])])
add('backward.joint-law',back,dict(condition_mass='7/12',posterior=[dict(x='1',probability='3/7'),dict(x='2',probability='4/7')],mean='11/7',variance='12/49',backward_law_status='derived_from_joint'))
add('backward.no-prior',changed(back,prior=None,backward_law_id='joint.unidentified'),dict(condition_mass=None,posterior=[],mean=None,variance=None,backward_law_status='unidentified'),['BACKWARD_LAW_UNIDENTIFIED'])
add('backward.zero-event',changed(back,observed_y='2'),dict(condition_mass='0',posterior=[],mean=None,variance=None,backward_law_status='zero_condition_mass'),['ZERO_CONDITION_MASS'])
reserve = dict(method_id='reserve.error@1',triangle_id='triangle.center',conditioning='latest_diagonal',center_conditioning='latest_diagonal',paid=['100'],simulated_ultimate=['130'],fitted_ultimate=['120'],center_kind='reserve')
add('reserve.correct-center',reserve,dict(simulated_reserve='30',fitted_reserve='20',reserve_error='10'))
add('reserve.full-triangle-target',changed(reserve,conditioning='full_triangle',center_conditioning='full_triangle'),dict(simulated_reserve='30',fitted_reserve='20',reserve_error='10'))
add('reserve.wrong-center',changed(reserve,center_kind='ultimate'),refusal='RESERVE_CENTER_REQUIRED')
add('reserve.mixed-target',changed(reserve,center_conditioning='full_triangle'),refusal='CONDITIONING_TARGET_MISMATCH')
cdr = dict(method_id='cdr.one-year@1',triangle_id='triangle.cdr',opening_date='2022-01-01',closing_date='2023-01-01',opening_reserve='100',payments='30',closing_reestimated_reserve='80',horizon='one_year_reestimation')
add('cdr.reestimated',cdr,dict(cdr='-10',opening_reserve='100',paid='30',closing_reserve='80',calibration='not_evaluated'))
dep = dict(method_id='dependence.stoploss@1',triangle_id='triangle.treaty',family_id='law.stoploss-family',parameter_min='0',parameter_max='1/2',selected_parameter=None,claim_high='40',attachment='60',marginal_high_probability='1/2',law_uncertainty='unweighted_set')
depd = dict(expectation_min='0',expectation_max='10',selected_expectation=None,independent_expectation='5',selected_joint_masses=[],second_high_after_high=None,second_high_after_zero=None,distribution_over_parameters=None)
add('dependence.unweighted-family',dep,depd)
add('dependence.independent-member',changed(dep,selected_parameter='1/4'),changed(depd,selected_expectation='5',selected_joint_masses=['1/4','1/4','1/4','1/4'],second_high_after_high='1/2',second_high_after_zero='1/2'))
add('dependence.comonotone-member',changed(dep,selected_parameter='1/2'),changed(depd,selected_expectation='10',selected_joint_masses=['1/2','0','0','1/2'],second_high_after_high='1',second_high_after_zero='0'))
add('dependence.outside-family',changed(dep,selected_parameter='3/4'),refusal='PARAMETER_OUTSIDE_FAMILY')
