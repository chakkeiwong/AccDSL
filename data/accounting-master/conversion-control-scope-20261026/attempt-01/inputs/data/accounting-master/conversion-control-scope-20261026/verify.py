"""Bounded authority integrity and dependency routing; never posting admission."""
from pathlib import Path
from copy import deepcopy as cp
import hashlib,json,platform,resource,subprocess,sys,time,traceback
import fitz
import dependencies as d
H=Path(__file__).resolve().parent;R=H.parents[2];S=H/'source-attempt-02';OUT=Path(sys.argv[1]);OUT.mkdir(exist_ok=False);resource.setrlimit(resource.RLIMIT_CPU,(120,120));start=time.monotonic();checks=[];cases=[];controls=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,x,y=True):
 checks.append({'name':n,'pass':x==y})
 if x!=y:raise AssertionError(n+': '+repr(x)[:250]+' != '+repr(y)[:250])
def assess(status,at='2028-01-01'):return {'status':status,'evidence':['hypothetical-assessment-only'] if status!='unknown' else [],'subject':['holder','issuer'],'as_of':at}
def base():
 def control(at,status):return {'as_of':at,'elements':{k:assess(status,at) for k in d.CONTROL},'reviews':{k:assess('yes',at) for k in d.REVIEWS}}
 before=control('2027-12-31','yes');before['elements']['power']=assess('no','2027-12-31')
 return {'profile':d.PROFILE,'context':{'holder':'holder','issuer':'issuer','basis':'conditional_AASB_design','period_start':'2028-01-01'},'conversion_date':'2028-01-01','votes':{'received':120,'total':160},'control_before':before,'control_after':control('2028-01-01','yes'),'report':'consolidated','assessments':{k:assess('yes' if k=='business' else 'no') for k in d.GENERAL},'separate_policy':'unknown','measurements':{},'authority':{'status':'unresolved','evidence':[],'period_start':'2028-01-01','basis':'conditional_AASB_design'}}
def test(n,mutate,routes,missing=(),timing=None):
 b=base();mutate(b);before=cp(b);got=d.evaluate(b);ck(n+'/routes',got['routes'],routes);ck(n+'/immutable',b,before)
 for key in missing:ck(n+'/missing/'+key,key in got['missing'])
 if timing is not None:ck(n+'/timing',got['timing'],timing)
 ck(n+'/never_admit',[got[k] for k in ('source_admission','accounting_admission','posting_authorized')],[False]*3)
 cases.append({'id':n,'input':b,'result':got});return got

def reject(n,fn):
 b=base();fn(b)
 try:d.evaluate(b)
 except (ValueError,TypeError,KeyError):controls.append(n);ck(n,True)
 else:ck(n,False)
anchors={
'aasb10-2026.pdf':[(1,'before 1 January 2027'),(6,'variable returns'),(7,'current ability'),(8,'investment management services'),(9,'main purpose and activities'),(14,'practical ability'),(15,'exercisable when decisions'),(16,'not all rights'),(17,'majority of the voting rights'),(19,'Potential voting rights'),(20,'need not have occurred'),(22,'agent'),(27,'reassess'),(31,'eliminate in full')],
'aasb127-2022.pdf':[(1,'1 January 2022'),(5,'does not mandate'),(6,'same accounting for each category'),(6,'11A')],
'aasb3-2026.pdf':[(1,'before 1 January 2027'),(6,'does not give rise to goodwill'),(7,'earlier or later than the closing date'),(22,'if the concentration test is not met'),(23,'substantive process'),(24,'an acquired contract is an input'),(11,'32'),(12,'previously held equity interest')],
'aasb2024-4b.pdf':[(5,'before 1 January 2028'),(6,'2028')],
'aasb2014-10.pdf':[(5,'Sale or Contribution of Assets')],
'aasb2026-3.pdf':[(5,'1 January 2027'),(5,'1 January 2028')],
'aasb2026-4.pdf':[(5,'AASB 2026-2'),(5,'1 January 2028')]}
source={Path(__file__).resolve(),H/'dependencies.py',H/'control-scope.md',H/'fetch.py',R/'docs/plans/accounting-conversion-control-scope-20261026.md',R/'scripts/group_period_report_v1.py',R/'scripts/native_group_binding_v1.py',R/'data/accounting-master/contingent-conversion-authority-20261026/source-attempt-02/aasb18-appendix-d.pdf'}|set(p for p in S.iterdir() if p.is_file())
lock={str(p.relative_to(R)):sha(p) for p in source}
for p in source:
 q=OUT/'inputs'/p.relative_to(R);q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(p.read_bytes())
register=[]
try:
 acquired=json.loads((S/'acquisition.json').read_text())
 for row in acquired:
  ck('HTTP/'+row['name'],row['returncode'],0);ck('bytes/'+row['name'],sha(S/row['name']),row['sha256'])
 for name,items in anchors.items():
  doc=fitz.open(S/name);read=[]
  for page,term in items:
   text=' '.join(doc[page-1].get_text().split());ck('anchor/'+name+'/'+str(page)+'/'+term,term.lower() in text.lower());read.append({'physical_page':page,'anchor':term})
  register.append({'source':name,'sha256':sha(S/name),'pages':len(doc),'inspected_anchors':read,'authority_scope':'conditional technical support; full2027/2028 edition admission unresolved','official_url':next(x['url'] for x in acquired if x['name']==name)})
 test('business_combination',lambda b:None,['consolidation_scope','business_combination'],('acquisition_date_identifiable_net_assets','NCI_measurement','dated_entity_specific_authority_chain'))
 test('unknown_power',lambda b:b['control_after']['elements'].update(power=assess('unknown')),['control_unresolved'],('postconversion_control_assessment',))
 test('votes_do_not_override_no_power',lambda b:b['control_after']['elements'].update(power=assess('no')),['other_interest_scope_assessment'],('joint_control_or_significant_influence_or_financial_asset_scope',))
 test('potential_rights_unreviewed',lambda b:b['control_after']['reviews'].update(substantive_and_potential_rights=assess('unknown')),['control_unresolved'])
 test('before_control_unknown',lambda b:b['control_before']['reviews'].update(timing=assess('unknown','2027-12-31')),['consolidation_scope','business_combination'],('preconversion_control_assessment','evidenced_actual_control_acquisition_date'),timing='unresolved')
 test('control_before_conversion',lambda b:b['control_before']['elements'].update(power=assess('yes','2027-12-31')),['consolidation_scope','continued_control_conversion'],('conversion_effects_on_existing_group_and_NCI',),timing='already_controlled_before_conversion')
 for policy,key in [('cost','supported_initial_cost'),('AASB9','AASB9_classification_and_measurement'),('equity_method','equity_method_inputs')]:
  test('separate_'+policy,lambda b,p=policy:b.update(report='separate',separate_policy=p),['separate_'+policy],(key,))
 test('separate_unknown',lambda b:b.update(report='separate'),['separate_policy_unresolved'],('consistent_category_measurement_policy',))
 test('investment_entity',lambda b:b['assessments'].update(investment_entity=assess('yes')),['investment_entity_fair_value_scope'],('fair_value_at_required_dates',))
 test('investment_entity_separate',lambda b:(b.update(report='separate',separate_policy='cost'),b['assessments'].update(investment_entity=assess('yes'))),['investment_entity_fair_value_scope'])
 test('service_subsidiary',lambda b:b['assessments'].update(investment_entity=assess('yes'),service_subsidiary=assess('yes')),['consolidation_scope','business_combination'])
 test('service_unknown',lambda b:b['assessments'].update(investment_entity=assess('yes'),service_subsidiary=assess('unknown')),['investment_entity_exception_unresolved'])
 test('exemption',lambda b:b['assessments'].update(consolidation_exemption=assess('yes')),['supplied_consolidation_exemption'])
 test('exemption_unknown',lambda b:b['assessments'].update(consolidation_exemption=assess('unknown')),['consolidation_exemption_unresolved'])
 test('business_unknown',lambda b:b['assessments'].update(business=assess('unknown')),['consolidation_scope','acquisition_route_unresolved'])
 test('asset_group',lambda b:b['assessments'].update(business=assess('no')),['consolidation_scope','asset_acquisition'],('asset_liability_recognition_and_relative_fair_values',))
 test('common_control',lambda b:b['assessments'].update(common_control=assess('yes')),['consolidation_scope','common_control_outside_AASB3'],('applicable_common_control_policy',))
 known=test('cost_evidence',lambda b:(b.update(report='separate',separate_policy='cost'),b['measurements'].update(supported_initial_cost='hypothetical_cost_analysis')),['separate_cost']);ck('cost_evidence_only_discharges_named_item','supported_initial_cost' not in known['missing'])
 test('zero_votes_does_not_rewrite_supplied_control',lambda b:b.update(votes={'received':0,'total':160}),['consolidation_scope','business_combination'])
 for name,fn in [
 ('missing_control_evidence',lambda b:b['control_after']['elements']['power'].update(evidence=[])),
 ('wrong_subject',lambda b:b['control_after']['elements']['power'].update(subject=['issuer','holder'])),
 ('wrong_assessment_date',lambda b:b['control_after']['elements']['power'].update(as_of='2027-01-01')),
 ('missing_potential_review',lambda b:b['control_after']['reviews'].pop('substantive_and_potential_rights')),
 ('invalid_votes',lambda b:b['votes'].update(total=0)),
 ('boolean_vote_count',lambda b:b['votes'].update(received=True)),
 ('bad_status',lambda b:b['assessments']['business'].update(status='probably')),
 ('invented_admission',lambda b:b['authority'].update(status='admitted')),
 ('wrong_authority_period',lambda b:b['authority'].update(period_start='2026-01-01')),
 ('measurement_erases_authority',lambda b:b['measurements'].update(accounting_authority_admission='yes')),
 ('extra_field',lambda b:b.update(assume_control=True)),
 ('undated_conversion',lambda b:b.update(conversion_date='2028'))]:reject(name,fn)
 for path,h in lock.items():ck('protected/'+path,sha(R/path),h)
 result={'status':'PASS','sources':len(register),'official_downloads':len(acquired),'scenarios':len(cases),'controls':len(controls),'assertions':len(checks),'protected_files':len(lock),'source_admission':False,'accounting_admission':False,'scope':'Bounded primary-source support and conditional dependency routing only; no actual financial measurement or authority admission.'}
except Exception:result={'status':'FAIL','assertions':len(checks),'error':traceback.format_exc()}
finally:
 for name,x in [('verification.json',result),('checks.json',checks),('cases.json',cases),('controls.json',controls),('source-lock.json',lock),('source-register.json',register)]:(OUT/name).write_text(json.dumps(x,indent=2)+'\n')
 (OUT/'run-manifest.json').write_text(json.dumps({'git':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'command':'CUDA_VISIBLE_DEVICES=-1 PYTHONDONTWRITEBYTECODE=1 timeout 120s python3 '+str(Path(__file__).relative_to(R))+' '+str(OUT),'python':platform.python_version(),'environment':'CPU only; GPU intentionally hidden; existing PyMuPDF extraction','seeds':'N/A deterministic','data':'retained official standards and explicit synthetic assessment cases','wall_seconds':time.monotonic()-start,'plan':'docs/plans/accounting-conversion-control-scope-20261026.md','result':str(OUT/'verification.json')},indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if result['status']!='PASS':sys.exit(1)
