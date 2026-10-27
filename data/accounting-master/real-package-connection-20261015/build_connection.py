"""Author finite real-source/conditional exchanges; no product endpoint runs."""
from pathlib import Path
from fractions import Fraction as Q
from copy import deepcopy
import hashlib,json

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
REG={};ALIASES={};BLOBS={};EX=[]
def enc(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def sid(k):return {'OperationRequest':'accdsl.operation.request.v1','OperationResult':'accdsl.operation.result.v1','Submission':'accdsl.real.submission.v1'}.get(k,'accdsl.real.'+k.lower()+'.v1')
def obj(p):return {'type':'object','properties':p,'required':list(p),'additionalProperties':False}
def arr(t,n=0):return {'type':'array','items':t,'minItems':n}
def maybe(t):return {'oneOf':[t,{'type':'null'}]}
TEXT={'type':'string','minLength':1};BOOL={'type':'boolean'};INT={'type':'integer','minimum':0}
ID={'type':'string','pattern':'^[A-Za-z0-9_.:@/-]+$'}
DIGEST={'type':'string','pattern':'^[a-f0-9]{64}$'}
RAT=obj({'n':{'type':'string','pattern':'^(0|-?[1-9][0-9]*)$'},'d':{'type':'string','pattern':'^[1-9][0-9]*$'}})
def ref(k=None):return obj({'kind':{'const':k} if k else ID,'schema':{'const':sid(k)} if k else ID,'digest':DIGEST})
BLOB=obj({'kind':{'const':'blob'},'algorithm':{'const':'sha256'},'digest':DIGEST,'byte_length':INT})
UNKNOWN=obj({'tag':{'const':'unknown'},'reason':TEXT,'obligation_refs':arr(ref('Obligation'),1)})
KNOWN=obj({'tag':{'const':'known_displayed'},'amount':RAT})
DERIVED=obj({'tag':{'const':'conditional_derived'},'amount':RAT,'basis_ref':ref('ConditionalBasis')})
DASH=obj({'tag':{'const':'reported_dash'},'literal':TEXT})
VALUE={'oneOf':[KNOWN,DASH,UNKNOWN,DERIVED]}
def rat(v):q=Q(str(v));return {'n':str(q.numerator),'d':str(q.denominator)}
def known(v):return {'tag':'known_displayed','amount':rat(v)}
def unknown(reason,ob):return {'tag':'unknown','reason':reason,'obligation_refs':ob}
def refs(x):
 if isinstance(x,dict):
  if set(x)=={'kind','schema','digest'}:yield x
  else:
   for v in x.values():yield from refs(v)
 elif isinstance(x,list):
  for v in x:yield from refs(v)
def add(k,key,b):
 ds={enc(r):r for r in refs(b)}
 r={'kind':k,'schema':sid(k),'key':key,'revision':0,'body':b,'dependencies':[ds[x] for x in sorted(ds)]}
 d=hashlib.sha256(('accdsl.portable.v1/'+sid(k)).encode()+b'\0'+enc(r)).hexdigest()
 REG[d]=r;out={'kind':k,'schema':sid(k),'digest':d};ALIASES[key]=out;return out
def body(r):return REG[r['digest']]['body']
def blob(path):
 p=ROOT/path if isinstance(path,str) else path;data=p.read_bytes();d=hashlib.sha256(data).hexdigest()
 BLOBS[d]={'path':str(p.relative_to(ROOT)),'byte_length':len(data)}
 return {'kind':'blob','algorithm':'sha256','digest':d,'byte_length':len(data)}
def saveblob(name,data):
 p=OUT/'bytes'/name;p.parent.mkdir(exist_ok=True,parents=True);p.write_bytes(data);return blob(p)
def read(path):return json.loads((ROOT/path).read_text())

S={}
S['Obligation']=obj({'issuer':TEXT,'code':ID,'affected_queries':arr(ID,1),'reason':TEXT,'support_refs':arr(ref())})
S['EvidenceFile']=obj({'role':ID,'blob':BLOB})
S['SourceVersion']=obj({'issuer':TEXT,'version':ID,'original_blob':BLOB,'reading_file_ref':ref('EvidenceFile'),'public_at':UNKNOWN,'ingested_at':UNKNOWN,'reviewed_at':UNKNOWN,'supersedes_refs':arr(ref('SourceVersion'))})
S['Context']=obj({'issuer':TEXT,'perimeter':TEXT,'basis':TEXT,'period':TEXT,'unit':TEXT,'measurement_kind':TEXT})
S['Observation']=obj({'source_ref':ref('SourceVersion'),'reading_file_ref':ref('EvidenceFile'),'pointer':TEXT,'row_id':TEXT,'context_ref':ref('Context'),'literal':TEXT,'value':{'oneOf':[KNOWN,DASH]},'precision':TEXT,'admission':{'const':'author_reading_no_human_admission'}})
S['InventoryItem']=obj({'category':ID,'item_id':TEXT,'file_ref':ref('EvidenceFile'),'pointer':TEXT,'disposition':TEXT,'remaining_facts':TEXT})
S['Assertion']=obj({'issuer':TEXT,'source_ref':ref('SourceVersion'),'extraction_blob':BLOB,'start':INT,'end':INT,'quote':TEXT,'span_sha256':DIGEST,'note_id':ID,'proposed_consequence':TEXT,'obligation_ref':ref('Obligation'),'admission':{'const':'proposed_only'}})
S['Package']=obj({'issuer':TEXT,'source_refs':arr(ref('SourceVersion'),1),'evidence_file_refs':arr(ref('EvidenceFile'),1),'inventory_refs':arr(ref('InventoryItem'),1),'assertion_refs':arr(ref('Assertion'),1),'recursive_closure':{'const':False},'semantics_complete':{'const':False},'obligation_refs':arr(ref('Obligation'),1)})
S['View']=obj({'issuer':TEXT,'view_id':ID,'source_refs':arr(ref('SourceVersion'),1),'parent_ref':maybe(ref('View')),'mode':{'const':'named_retained_sources'},'historical_admission':{'const':False}})
S['FamilyQuestion']=obj({'issuer':TEXT,'package_ref':ref('Package'),'view_ref':ref('View'),'target':{'const':'actual_whole_company_histories_compatible_with_sources'},'obligation_refs':arr(ref('Obligation'),1),'formulation_complete':{'const':False},'feasibility':UNKNOWN,'measure_ref':{'type':'null'}})
S['StatementReport']=obj({'issuer':TEXT,'package_ref':ref('Package'),'view_ref':ref('View'),'annual_refs':arr(ref('Observation'),1),'annual_opening_refs':arr(ref('Observation'),1),'interim_refs':arr(ref('Observation'),1),'interim_comparison_refs':arr(ref('Observation'),1),'relation_file_refs':arr(ref('EvidenceFile'),2),'amount_meaning':{'const':'reported_displayed_tokens'},'history_admission':{'const':False},'obligation_refs':arr(ref('Obligation'),1)})
LINE=obj({'account':ID,'signed_amount':RAT})
S['ConditionalBasis']=obj({'issuer':TEXT,'family_ref':ref('FamilyQuestion'),'asset_evidence_ref':ref('EvidenceFile'),'repair_evidence_ref':ref('EvidenceFile'),'note_refs':arr(ref('Assertion'),1),'assumptions':arr(TEXT,1),'hypothetical_q':RAT,'alpha_lower':RAT,'alpha_upper':RAT,'base_feasibility':UNKNOWN,'posting_permission':{'const':False}})
S['ConditionalHistory']=obj({'basis_ref':ref('ConditionalBasis'),'branch':{'enum':['H1','H2']},'journals':arr(obj({'event':ID,'lines':arr(LINE,1)}),1),'capital_liability':RAT,'expense_liability':RAT,'actual_history_admission':{'const':False}})
S['DifferenceReport']=obj({'basis_ref':ref('ConditionalBasis'),'history_refs':arr(ref('ConditionalHistory'),2),'alpha':RAT,'row_differences':arr(obj({'row_id':TEXT,'value':RAT}),102),'all_displayed_rows_equal':BOOL,'absolute_feasibility':UNKNOWN})
EFFECT_NAMES='profit oci comprehensive_income equity cash assets liabilities capital_liability_close expense_liability_close operating investing financing cash_change'.split()
S['SettlementResult']=obj({'basis_ref':ref('ConditionalBasis'),'history_ref':ref('ConditionalHistory'),'capital_period':INT,'expense_period':INT,'periods':arr(obj({'period':INT,'journals':arr(obj({'event':ID,'lines':arr(LINE,1)})),'effects':obj({k:RAT for k in EFFECT_NAMES})}),2),'funding':{'const':'conditional_sufficient_unrestricted_cash'},'base_feasibility':UNKNOWN,'forecast_admission':{'const':False}})
S['NamedQueryResult']=obj({'view_ref':ref('View'),'query':ID,'items':arr(obj({'name':TEXT,'value':VALUE,'observation_ref':maybe(ref('Observation'))}),1),'obligation_refs':arr(ref('Obligation')),'target_layer':{'enum':['source_content','actual_history','conditional_difference','conditional_settlement']}})
S['ConnectedResult']=obj({'issuer':TEXT,'package_ref':ref('Package'),'view_ref':ref('View'),'family_ref':ref('FamilyQuestion'),'statement_report_ref':ref('StatementReport'),'conditional_basis_ref':ref('ConditionalBasis'),'difference_refs':arr(ref('DifferenceReport'),3),'settlement_refs':arr(ref('SettlementResult'),6),'later_view_ref':ref('View'),'later_comparative_refs':arr(ref('Observation'),1),'actual_history':UNKNOWN,'obligation_refs':arr(ref('Obligation'),1)})
S['ConflictSource']=obj({'issuer':TEXT,'original_blob':BLOB,'support_file_ref':ref('EvidenceFile'),'anchor_blobs':arr(BLOB,4),'review_file_ref':ref('EvidenceFile')})
S['ConflictProposal']=obj({'issuer':TEXT,'source_ref':ref('ConflictSource'),'action':{'enum':['propose_navigation','reject_refuted_alternative','supersede_counterfactual_prior']},'literal_page':INT,'navigation_printed_page':INT,'navigation_physical_page':INT,'stale_nodes':arr(ID),'reusable_nodes':arr(ID),'counterfactual_prior':BOOL,'old_view_preserved':{'const':True},'accounting_permission':{'const':False},'human_admission':{'const':False}})
S['SchemaLock']=obj({'schema_blob':BLOB,'semantic_blob':BLOB})
S['Profile']=obj({'name':{'const':'RealDisclosureConnection/1'},'lock_ref':ref('SchemaLock'),'operations':arr(ID,1),'effects':{'const':'candidate_or_read_only'}})
S['OperationSignature']=obj({'operation':ID,'profile_ref':ref('Profile'),'argument_definition':ID,'payload_kinds':arr(ID,1),'effect':{'const':'candidate_or_read_only'}})
S['Environment']=obj({'mode':{'const':'documentary_exact_rational'},'runtime_executed':{'const':False}})
S['Decoder']=obj({'encoding':{'const':'accdsl.portable.v1'}})
S['Submission']=obj({'blob_ref':BLOB,'media_type':{'const':'application/json'},'transport':{'const':'authored_fixture'},'decoder_ref':ref('Decoder')})
S['Domain']=obj({'request_ref':ref('OperationRequest'),'meaning':{'const':'requested_claim_scope_not_history_mass'}})
S['Region']=obj({'domain_ref':ref('Domain'),'scope':ID})
A={
 'source.prepare@1':obj({'package_ref':ref('Package'),'view_ref':ref('View')}),
 'history.query@1':obj({'family_ref':ref('FamilyQuestion'),'view_ref':ref('View'),'query':{'enum':['connected_result','reported_statements','segment_components','actual_history','probability','conditional_difference']},'information_mode':{'enum':['named_sources','investor_information','system_as_of']},'cutoff':maybe({'type':'string','format':'date-time'}),'alpha':RAT,'issuer':TEXT}),
 'scenario.project@1':obj({'basis_ref':ref('ConditionalBasis'),'history_ref':ref('ConditionalHistory'),'view_ref':ref('View'),'query':{'enum':['settlement','depreciation']},'capital_period':maybe(INT),'expense_period':maybe(INT),'issuer':TEXT}),
 'report.build@1':obj({'connected_ref':ref('ConnectedResult'),'view_ref':ref('View'),'issuer':TEXT}),
 'review.propose@1':obj({'source_ref':ref('ConflictSource'),'action':{'enum':['propose_navigation','reject_refuted_alternative','supersede_counterfactual_prior']},'issuer':TEXT})}
S['OperationRequest']=obj({'operation':{'enum':list(A)},'request_id':ID,'workspace_key':ID,'profile_ref':ref('Profile'),'signature_ref':ref('OperationSignature'),'view_ref':ref('View'),'arguments':{'oneOf':[obj({'tag':{'const':k},'value':v}) for k,v in A.items()]},'execution':obj({'mode':{'const':'specification_example'},'budget':obj({'operation_count':INT,'elapsed_seconds':INT}),'environment_ref':ref('Environment')}),'expected_head':{'type':'null'}})
STATUS=obj({'structural_validity':{'enum':['valid','invalid']},'mathematical_status':{'enum':['defined','unresolved']},'computation_status':{'enum':['complete','partial','not_computed']},**{k:{'const':v} for k,v in {'empirical_justification':'not_established','capability_status':'specified_only_no_runtime','accounting_validity':'not_assessed','forecast_validity':'not_assessed','product_readiness':'not_implemented','human_acceptance':'pending'}.items()}})
DIAG=obj({'code':ID,'stage':TEXT,'record_ref':maybe(ref()),'source_locator':maybe(TEXT),'field_path':TEXT,'affected_query_branch_ids':arr(ID),'dependency_path':arr(ref()),'observed':TEXT,'expected_rule':TEXT,'retry_advice':TEXT,'blocking_diagnostic_ids':arr(ID)})
S['OperationResult']=obj({'submission_ref':ref('Submission'),'request_ref':maybe(ref('OperationRequest')),'operation':maybe(ID),'input_view_ref':maybe(ref('View')),'disposition':{'enum':['completed','partial','unsupported','rejected']},'statuses':STATUS,'payload':maybe(obj({'tag':ID,'result_refs':arr(ref()),'additional_commit':{'const':False}})),'diagnostics':arr(DIAG),'coverage':maybe(obj({'domain_ref':ref('Domain'),**{k:arr(ref('Region')) for k in ['completed','unresolved','unsupported','infeasible','cancelled']},'relation':{'const':'disjoint_exhaustive'}})),'unresolved':arr(ref('Obligation')),'continuation_ref':{'type':'null'},'commit_observation':{'const':'not_committed'},'receipt_ref':{'type':'null'},'evidence_mode':{'const':'specification_example'}})
for op,schema in A.items():S['Arguments.'+op]=schema

def main():
 OUT.mkdir(parents=True,exist_ok=True)
 (OUT/'record-schemas.json').write_text(json.dumps({'$schema':'https://json-schema.org/draft/2020-12/schema','schema_ids':{k:sid(k) for k in S},'$defs':S},indent=2)+'\n')
 lock=add('SchemaLock','schema-lock',{'schema_blob':blob(OUT/'record-schemas.json'),'semantic_blob':blob('docs/design/proposal/architecture/real-package-connection-20261015.md')})
 profile=add('Profile','profile',{'name':'RealDisclosureConnection/1','lock_ref':lock,'operations':list(A),'effects':'candidate_or_read_only'})
 kinds={'source.prepare@1':['Package'],'history.query@1':['ConnectedResult','StatementReport','NamedQueryResult','DifferenceReport'],'scenario.project@1':['SettlementResult','NamedQueryResult'],'report.build@1':['StatementReport'],'review.propose@1':['ConflictProposal']}
 signatures={op:add('OperationSignature','signature.'+op,{'operation':op,'profile_ref':profile,'argument_definition':'Arguments.'+op,'payload_kinds':kinds[op],'effect':'candidate_or_read_only'}) for op in A}
 env=add('Environment','environment',{'mode':'documentary_exact_rational','runtime_executed':False});decoder=add('Decoder','decoder',{'encoding':'accdsl.portable.v1'})
 def evidence(key,path):return add('EvidenceFile',key,{'role':key,'blob':blob(path)})
 base='data/accounting-master/'
 paths={'package-map':base+'p17-completion-20261014/P17-02/connected-package-map.json','package-original':'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json','annual-readings':base+'apple-statement-network-20261013/statement-readings.json','interim-readings':base+'apple-interim-network-20261013/statement-readings.json','annual-relations':base+'apple-statement-network-20261013/relationship-ledger.json','interim-relations':base+'apple-interim-network-20261013/relationship-ledger.json','later-segments':base+'p17-completion-20261014/P17-02/retrospective-segment-readings.json','asset-histories':base+'apple-assets-20261008/asset-history.json','conditional-repair':base+'apple-coupled-completion-20261013/conditional-repair.json','settlement-paths':base+'apple-settlement-paths-20261013/settlement-paths.json','missing-bindings':base+'apple-history-compatibility-20261013/missing-bindings.json','note-bindings':base+'apple-coupled-completion-20261013/source-bindings.json','conflict-support':base+'jpmorgan-reference-conflict-20261013/source-support.json','conflict-review':base+'jpmorgan-reference-conflict-20261013/review-fixture.json'}
 files={k:evidence(k,p) for k,p in paths.items()}
 def obligation(key,reason,queries,issuer='Apple',support=()):return add('Obligation',key,{'issuer':issuer,'code':key,'affected_queries':queries,'reason':reason,'support_refs':list(support)})
 clock=obligation('EXACT_BYTE_CLOCKS_UNRESOLVED','No accepted exact-version publication/ingestion/review clock is established by these retained content dossiers.',['historical_information'])
 recursive=obligation('PACKAGE_REFERENCE_AND_SEMANTIC_FRONTIER','Known reference frontier and all notes retain specific missing bodies and meanings.',['actual_history','prepare'],support=[files['package-map']])
 feasible=obligation('FEASIBLE_COMPANY_REMAINDER_UNESTABLISHED','Equal relative row differences do not construct a complete feasible issuer history.',['actual_history','conditional_difference','settlement'],support=[files['conditional-repair'],files['missing-bindings']])
 terms=obligation('ACTUAL_EVENTS_AND_MAPPING_UNADMITTED','Actual events, expense/liability classification, tax bases, cohort memory and settlement dates are missing.',['actual_history','settlement','depreciation'],support=[files['missing-bindings']])
 law=obligation('NO_ADMITTED_MEASURE','No probability measure over actual or conditional history alternatives is admitted.',['probability'])
 annual=read(paths['annual-readings']);interim=read(paths['interim-readings']);later=read(paths['later-segments']);mapping=read(paths['package-map'])
 sources={}
 for label,issuer,path,file in [('annual','Apple',annual['rows'][0]['source'],files['annual-readings']),('interim','Apple',interim['source'],files['interim-readings']),('later','Apple',later['source'],files['later-segments'])]:
  sources[label]=add('SourceVersion','source.'+label,{'issuer':issuer,'version':label,'original_blob':blob(path),'reading_file_ref':file,'public_at':unknown('EXACT_BYTE_CLOCKS_UNRESOLVED',[clock]),'ingested_at':unknown('EXACT_BYTE_CLOCKS_UNRESOLVED',[clock]),'reviewed_at':unknown('EXACT_BYTE_CLOCKS_UNRESOLVED',[clock]),'supersedes_refs':[]})
 views={}
 for label in ['annual','interim','later','combined']:
  views[label]=add('View','view.'+label,{'issuer':'Apple','view_id':label,'source_refs':list(sources.values())[:2] if label=='combined' else [sources[label]],'parent_ref':None,'mode':'named_retained_sources','historical_admission':False})
 inventory=[]
 for category in ['reference_frontier','package_obligations','note_dispositions','material_assertions','additional_frontier']:
  for i,item in enumerate(mapping[category]):
   frozen=item.get('frozen',item)
   status=next((item[k] for k in ['frozen_document_status','frozen_status','frozen_disposition','frozen_translation_status'] if k in item),frozen.get('status','retained_original_row'))
   inventory.append(add('InventoryItem',f'inventory.{category}.{i}',{'category':category,'item_id':str(frozen.get('id',i)),'file_ref':files['package-map'],'pointer':f'/{category}/{i}','disposition':status,'remaining_facts':str(item.get('remaining_facts',item.get('current_disposition',item.get('proposed_consequence','Exact retained entry controls; no completeness upgrade.'))))}))
 assertions=[];note_obligations=[]
 notes={r['id']:r for r in mapping['note_dispositions']}
 for item in mapping['material_assertions']:
  src=item['source'];note=notes[item['note_id']]
  ob=obligation('NOTE_'+item['id'],note['remaining_facts'],['actual_history','conditional_difference'],support=[files['package-map']]);note_obligations.append(ob)
  assertions.append(add('Assertion','assertion.'+item['id'],{'issuer':'Apple','source_ref':sources['annual' if src['source_id']=='annual' else 'interim'],'extraction_blob':blob(src['extraction_path']),'start':src['start'],'end':src['end'],'quote':src['quote'],'span_sha256':src['span_sha256'],'note_id':item['note_id'],'proposed_consequence':item['proposed_consequence'],'obligation_ref':ob,'admission':'proposed_only'}))
 package=add('Package','apple.package',{'issuer':'Apple','source_refs':[sources['annual'],sources['interim']],'evidence_file_refs':[files[k] for k in paths if not k.startswith('conflict')],'inventory_refs':inventory,'assertion_refs':assertions,'recursive_closure':False,'semantics_complete':False,'obligation_refs':[recursive,clock,feasible,terms]+note_obligations})
 observations={};openings={}
 def observation(key,source,file,pointer,row_id,row,value,literal,period=None):
  c=add('Context','context.'+key,{'issuer':'Apple','perimeter':row.get('entity','Apple Inc. consolidated'),'basis':row.get('basis','issuer reportable-segment presentation'),'period':period or row.get('period','FY'+row.get('fiscal_year','2024')),'unit':row['unit'],'measurement_kind':row.get('measurement_kind','segment displayed amount')})
  return add('Observation',key,{'source_ref':source,'reading_file_ref':file,'pointer':pointer,'row_id':row_id,'context_ref':c,'literal':literal,'value':{'tag':'reported_dash','literal':literal} if value is None else known(value),'precision':row.get('precision','displayed integer; unrounded equality not established'),'admission':'author_reading_no_human_admission'})
 for label,data in [('annual',annual),('interim',interim)]:
  observations[label]=[];openings[label]=[]
  for i,r in enumerate(data['rows']):
   observations[label].append(observation(label+'.'+r['id'],sources[label],files[label+'-readings'],f'/rows/{i}',r['id'],r,r['value'],r['literal']))
   old=r.get('opening') if label=='annual' else r.get('comparison')
   if old and r['statement']=='balance':openings[label].append(observation(label+'.opening.'+r['id'],sources[label],files[label+'-readings'],f'/rows/{i}/'+('opening' if label=='annual' else 'comparison'),'opening.'+r['id'],r,old['value'],old['literal'],old.get('date',old.get('period'))))
 segment_refs=[]
 for i,r in enumerate(later['rows']):
  if r['fiscal_year']=='2024':segment_refs.append(observation('later.segment.'+str(i),sources['later'],files['later-segments'],f'/rows/{i}',r['segment']+'.'+r['label'],r,r['value'],r['literal']))
 family=add('FamilyQuestion','apple.family',{'issuer':'Apple','package_ref':package,'view_ref':views['combined'],'target':'actual_whole_company_histories_compatible_with_sources','obligation_refs':[recursive,feasible,terms],'formulation_complete':False,'feasibility':unknown('FEASIBLE_COMPANY_REMAINDER_UNESTABLISHED',[feasible]),'measure_ref':None})
 report=add('StatementReport','apple.reported-statements',{'issuer':'Apple','package_ref':package,'view_ref':views['combined'],'annual_refs':observations['annual'],'annual_opening_refs':openings['annual'],'interim_refs':observations['interim'],'interim_comparison_refs':openings['interim'],'relation_file_refs':[files['annual-relations'],files['interim-relations']],'amount_meaning':'reported_displayed_tokens','history_admission':False,'obligation_refs':[feasible,terms,recursive]})
 basis=add('ConditionalBasis','conditional.basis',{'issuer':'Apple','family_ref':family,'asset_evidence_ref':files['asset-histories'],'repair_evidence_ref':files['conditional-repair'],'note_refs':[r for r in assertions if body(r)['note_id'] in ['annual.note.1','annual.note.5','annual.note.6','annual.note.7','annual.note.8']],'assumptions':read(paths['asset-histories'])['assumptions']+read(paths['conditional-repair'])['note_conditions']+read(paths['settlement-paths'])['assumptions']+['Retirement loss and the distinct expense both map to operations.products_cost. Capital payable and expense liability both map to balance.other_liabilities_current, a non-tax bucket.','All other report primitives, shares, distributions and OCI remain fixed; current and deferred tax match. Alpha allocates the expense-liability change once between cash_flow.other_adjustments and cash_flow.other_liabilities.'],'hypothetical_q':rat(2000),'alpha_lower':rat(0),'alpha_upper':rat(1),'base_feasibility':unknown('FEASIBLE_COMPANY_REMAINDER_UNESTABLISHED',[feasible]),'posting_permission':False})
 histories=[]
 for i,h in enumerate(read(paths['asset-histories'])['histories']):
  journals=[{'event':j['event'],'lines':[{'account':p['account'],'signed_amount':rat(p['debit']-p['credit'])} for p in j['postings']]} for j in h['journals']]
  expense=2000-1000*i;journals.append({'event':'conditional_separate_expense_liability','lines':[{'account':'expense','signed_amount':rat(expense)},{'account':'expense_liability','signed_amount':rat(-expense)}]})
  histories.append(add('ConditionalHistory','conditional.'+h['id'],{'basis_ref':basis,'branch':h['id'],'journals':journals,'capital_liability':rat(h['unpaid_additions']),'expense_liability':rat(expense),'actual_history_admission':False}))
 diffs=[]
 for alpha in [Q(0),Q(1,2),Q(1)]:
  values={r['id']:Q(0) for r in annual['rows']};values['cash_flow.other_adjustments']=1000*(1-alpha);values['cash_flow.other_liabilities']=-1000*(1-alpha)
  diffs.append(add('DifferenceReport','difference.'+str(alpha).replace('/','_'),{'basis_ref':basis,'history_refs':histories,'alpha':rat(alpha),'row_differences':[{'row_id':k,'value':rat(v)} for k,v in values.items()],'all_displayed_rows_equal':not any(values.values()),'absolute_feasibility':unknown('FEASIBLE_COMPANY_REMAINDER_UNESTABLISHED',[feasible])}))
 settlements=[]
 for label,capital_period,expense_period in [('both_first',1,1),('capital_first',1,2),('expense_first',2,1)]:
  for h in histories:
   hb=body(h);capital=Q(hb['capital_liability']['n'])/Q(hb['capital_liability']['d']);expense=Q(hb['expense_liability']['n'])/Q(hb['expense_liability']['d']);periods=[]
   for n in [1,2]:
    cp=capital if n==capital_period else Q(0);ep=expense if n==expense_period else Q(0);journals=[]
    for kind,amount in [('capital',cp),('expense',ep)]:
     if amount:journals.append({'event':'settle_'+kind,'lines':[{'account':kind+'_liability','signed_amount':rat(amount)},{'account':'cash','signed_amount':rat(-amount)}]})
    effects={k:rat(0) for k in EFFECT_NAMES}
    effects.update({k:rat(-cp-ep) for k in ['cash','assets','liabilities','cash_change']})
    effects.update(capital_liability_close=rat(capital if n<capital_period else 0),expense_liability_close=rat(expense if n<expense_period else 0),operating=rat(-ep),investing=rat(-cp))
    periods.append({'period':n,'journals':journals,'effects':effects})
   settlements.append(add('SettlementResult','settlement.'+label+'.'+hb['branch'],{'basis_ref':basis,'history_ref':h,'capital_period':capital_period,'expense_period':expense_period,'periods':periods,'funding':'conditional_sufficient_unrestricted_cash','base_feasibility':unknown('FEASIBLE_COMPANY_REMAINDER_UNESTABLISHED',[feasible]),'forecast_admission':False}))
 connected=add('ConnectedResult','apple.connected',{'issuer':'Apple','package_ref':package,'view_ref':views['combined'],'family_ref':family,'statement_report_ref':report,'conditional_basis_ref':basis,'difference_refs':diffs,'settlement_refs':settlements,'later_view_ref':views['later'],'later_comparative_refs':segment_refs,'actual_history':unknown('FEASIBLE_COMPANY_REMAINDER_UNESTABLISHED',[feasible,terms]),'obligation_refs':[recursive,clock,feasible,terms,law]+note_obligations})
 # Exact read/candidate exchanges preserve all store domains.
 world={'accounting_heads':[],'committed_journals':[],'committed_receipts':[],'review_heads':[],'review_receipts':[],'work_heads':[],'import_heads':[],'published_records':[]}
 def exchange(key,op,args,outputs=(),disposition='completed',ob=(),code=None,view=None,invalid=False,scopes=None,corrupt=False,tag=None):
  view=view or views['combined'];issuer=args.get('issuer','Apple')
  req=add('OperationRequest','request.'+key,{'operation':op,'request_id':key,'workspace_key':issuer+'-documentary','profile_ref':profile,'signature_ref':signatures[op],'view_ref':view,'arguments':{'tag':op,'value':args},'execution':{'mode':'specification_example','budget':{'operation_count':10000,'elapsed_seconds':60},'environment_ref':env},'expected_head':None})
  raw=enc(REG[req['digest']])
  if corrupt:raw=raw[:-1]
  if tag:
   submitted=deepcopy(REG[req['digest']]);submitted['body']['arguments']['tag']=tag;raw=enc(submitted)
  sub=add('Submission','submission.'+key,{'blob_ref':saveblob(key+'.json',raw),'media_type':'application/json','transport':'authored_fixture','decoder_ref':decoder})
  coverage=None
  if not invalid:
   domain=add('Domain','domain.'+key,{'request_ref':req,'meaning':'requested_claim_scope_not_history_mass'})
   scopes=scopes or [(key,'unsupported' if disposition=='unsupported' else 'unresolved' if disposition=='partial' else 'completed')]
   groups={k:[] for k in ['completed','unresolved','unsupported','infeasible','cancelled']}
   for claim,group in scopes:groups[group].append(add('Region','region.'+key+'.'+claim,{'domain_ref':domain,'scope':claim}))
   coverage={'domain_ref':domain,**groups,'relation':'disjoint_exhaustive'}
  status={k:v['const'] for k,v in STATUS['properties'].items() if 'const' in v};status.update(structural_validity='invalid' if invalid else 'valid',mathematical_status='defined' if disposition=='completed' else 'unresolved',computation_status='not_computed' if invalid or disposition=='unsupported' else 'partial' if disposition=='partial' else 'complete')
  diag=[] if code is None else [{'code':code,'stage':'binding' if invalid else 'query','record_ref':None if invalid else req,'source_locator':None,'field_path':'arguments','affected_query_branch_ids':[key],'dependency_path':[],'observed':code,'expected_rule':'real-package-connection-20261015','retry_advice':'new_request_after_input_repair','blocking_diagnostic_ids':[]}]
  res=add('OperationResult','result.'+key,{'submission_ref':sub,'request_ref':None if invalid else req,'operation':None if invalid else op,'input_view_ref':None if invalid else view,'disposition':disposition,'statuses':status,'payload':None if invalid else {'tag':op,'result_refs':list(outputs),'additional_commit':False},'diagnostics':diag,'coverage':coverage,'unresolved':list(ob),'continuation_ref':None,'commit_observation':'not_committed','receipt_ref':None,'evidence_mode':'specification_example'})
  EX.append({'id':key,'request_ref':req,'submission_ref':sub,'response_ref':res,'world_before':deepcopy(world),'world_after':deepcopy(world)})
 def query(key,query,outputs,**kw):
  view=kw.pop('view',views['combined']);mode=kw.pop('mode','named_sources');alpha=kw.pop('alpha',1)
  return exchange(key,'history.query@1',{'family_ref':family,'view_ref':view,'query':query,'information_mode':mode,'cutoff':'2024-09-29T00:00:00Z' if mode!='named_sources' else None,'alpha':rat(alpha),'issuer':'Apple'},outputs,view=view,**kw)
 exchange('prepare-package','source.prepare@1',{'package_ref':package,'view_ref':views['combined']},[package],disposition='partial',ob=[recursive])
 query('connected-partial','connected_result',[connected],disposition='partial',ob=body(connected)['obligation_refs'],scopes=[('reported_statement_tokens','completed'),('conditional_relative_calculations','completed'),('actual_history_and_private_terms','unresolved'),('historical_byte_availability','unresolved'),('recursive_source_semantics','unresolved')])
 query('reported-statements','reported_statements',[report])
 exchange('report-connected','report.build@1',{'connected_ref':connected,'view_ref':views['combined'],'issuer':'Apple'},[report],disposition='partial',ob=[feasible,terms,recursive])
 for label,mode in [('investor-byte-unknown','investor_information'),('system-byte-unknown','system_as_of')]:
  output=add('NamedQueryResult',label+'.output',{'view_ref':views['combined'],'query':'reported_statements','items':[{'name':'eligible_report_values','value':unknown('EXACT_BYTE_CLOCKS_UNRESOLVED',[clock]),'observation_ref':None}],'obligation_refs':[clock],'target_layer':'source_content'})
  query(label,'reported_statements',[output],mode=mode,disposition='partial',ob=[clock])
 for label,view in [('original-segment-detail',views['annual']),('later-segment-detail',views['later'])]:
  items=[];obs=[]
  for name in ['Cost of sales','Selling and marketing']:
   r=next(r for r in segment_refs if body(r)['row_id']=='Americas.'+name);obs.append(r)
   items.append({'name':'Americas.'+name,'value':body(r)['value'] if view==views['later'] else unknown('NOT_DISCLOSED_IN_SELECTED_ORIGINAL',[terms]),'observation_ref':r if view==views['later'] else None})
  out=add('NamedQueryResult',label+'.output',{'view_ref':view,'query':'segment_components','items':items,'obligation_refs':[] if view==views['later'] else [terms],'target_layer':'source_content'})
  query(label,'segment_components',[out],view=view,disposition='completed' if view==views['later'] else 'partial',ob=[] if view==views['later'] else [terms])
 for label,qry,ob in [('actual-history-unknown','actual_history',feasible),('probability-refused','probability',law)]:
  out=add('NamedQueryResult',label+'.output',{'view_ref':views['combined'],'query':qry,'items':[{'name':qry,'value':unknown(body(ob)['code'],[ob]),'observation_ref':None}],'obligation_refs':[ob],'target_layer':'actual_history'})
  query(label,qry,[out],disposition='partial' if qry=='actual_history' else 'unsupported',ob=[ob],code=body(ob)['code'])
 for d in diffs:query('query-'+REG[d['digest']]['key'],'conditional_difference',[d],alpha=Q(body(d)['alpha']['n'])/Q(body(d)['alpha']['d']))
 for s in settlements:
  b=body(s);exchange(REG[s['digest']]['key'],'scenario.project@1',{'basis_ref':basis,'history_ref':b['history_ref'],'view_ref':views['combined'],'query':'settlement','capital_period':b['capital_period'],'expense_period':b['expense_period'],'issuer':'Apple'},[s])
 for label,qry,cp,ep,disp in [('unknown-settlement-dates','settlement',None,None,'partial'),('unsupported-depreciation','depreciation',1,1,'unsupported')]:
  items=[{'name':'requested_future_quantity','value':unknown('ACTUAL_EVENTS_AND_MAPPING_UNADMITTED',[terms]),'observation_ref':None}]
  if qry=='settlement':
   for name,amount in [('eventual_operating',-2000),('eventual_investing',-1082),('eventual_cash_change',-3082)]:
    items.append({'name':name,'value':{'tag':'conditional_derived','amount':rat(amount),'basis_ref':basis},'observation_ref':None})
  out=add('NamedQueryResult',label+'.output',{'view_ref':views['combined'],'query':qry,'items':items,'obligation_refs':[terms,feasible],'target_layer':'conditional_settlement'})
  exchange(label,'scenario.project@1',{'basis_ref':basis,'history_ref':histories[0],'view_ref':views['combined'],'query':qry,'capital_period':cp,'expense_period':ep,'issuer':'Apple'},[out],disposition=disp,ob=[terms,feasible],scopes=[('eventual_conditional_amounts','completed'),('period_timing','unresolved')] if qry=='settlement' else None)
 for label,alpha in [('negative-alpha',-1),('excess-alpha',2)]:
  query(label,'conditional_difference',[],alpha=alpha,disposition='rejected',invalid=True,code='ALPHA_OUTSIDE_DOMAIN')
 for label,cp,ep in [('zero-period',0,1),('outside-horizon',1,3)]:
  exchange(label,'scenario.project@1',{'basis_ref':basis,'history_ref':histories[0],'view_ref':views['combined'],'query':'settlement','capital_period':cp,'expense_period':ep,'issuer':'Apple'},disposition='rejected',invalid=True,code='SETTLEMENT_PERIOD_OUTSIDE_DOMAIN')
 for label,opts in [('truncated-request',{'corrupt':True,'code':'INVALID_JSON'}),('operation-tag-mismatch',{'tag':'report.build@1','code':'OPERATION_TAG_MISMATCH'})]:
  exchange(label,'source.prepare@1',{'package_ref':package,'view_ref':views['combined']},disposition='rejected',invalid=True,**opts)
 # Separate company conflict proposal, with source-specific bytes and no money.
 conflict=read(paths['conflict-support']);review=read(paths['conflict-review'])
 anchor_blobs=[blob(a['source_text']) for a in conflict['anchors']]
 conflict_source=add('ConflictSource','jpmorgan.conflict-source',{'issuer':'JPMorgan','original_blob':blob(conflict['source_pdf']),'support_file_ref':files['conflict-support'],'anchor_blobs':anchor_blobs,'review_file_ref':files['conflict-review']})
 jpclock=obligation('JPMORGAN_EXACT_BYTE_CLOCKS_UNRESOLVED','Named retained source comparison; no exact historical byte clock established.',['historical_information'],issuer='JPMorgan')
 jpsource=add('SourceVersion','jpmorgan.source',{'issuer':'JPMorgan','version':'2023-10K','original_blob':blob(conflict['source_pdf']),'reading_file_ref':files['conflict-support'],'public_at':unknown('JPMORGAN_EXACT_BYTE_CLOCKS_UNRESOLVED',[jpclock]),'ingested_at':unknown('JPMORGAN_EXACT_BYTE_CLOCKS_UNRESOLVED',[jpclock]),'reviewed_at':unknown('JPMORGAN_EXACT_BYTE_CLOCKS_UNRESOLVED',[jpclock]),'supersedes_refs':[]})
 jpview=add('View','jpmorgan.view',{'issuer':'JPMorgan','view_id':'retained-source','source_refs':[jpsource],'parent_ref':None,'mode':'named_retained_sources','historical_admission':False})
 for action in ['propose_navigation','reject_refuted_alternative','supersede_counterfactual_prior']:
  out=add('ConflictProposal','jpmorgan.'+action,{'issuer':'JPMorgan','source_ref':conflict_source,'action':action,'literal_page':156,'navigation_printed_page':163,'navigation_physical_page':165,'stale_nodes':review['expected_stale_for_new_view'] if action=='supersede_counterfactual_prior' else [],'reusable_nodes':review['expected_reusable_if_other_dependencies_unchanged'],'counterfactual_prior':action=='supersede_counterfactual_prior','old_view_preserved':True,'accounting_permission':False,'human_admission':False})
  exchange('jpmorgan-'+action,'review.propose@1',{'source_ref':conflict_source,'action':action,'issuer':'JPMorgan'},[out],view=jpview)
 exchange('cross-company-rejected','report.build@1',{'connected_ref':connected,'view_ref':jpview,'issuer':'JPMorgan'},disposition='rejected',code='ISSUER_CONTEXT_MISMATCH',invalid=True,view=jpview)
 (OUT/'portable-exchanges.json').write_text(json.dumps({'evidence_mode':'specification_example','runtime_executed':False,'record_registry':REG,'aliases':ALIASES,'blobs':BLOBS,'exchanges':EX,'source_inputs':paths,'profile_ref':profile},indent=2)+'\n')
 print(json.dumps({'records':len(REG),'blobs':len(BLOBS),'exchanges':len(EX),'inventory':len(inventory),'annual_rows':len(observations['annual']),'interim_rows':len(observations['interim']),'later_comparatives':len(segment_refs)}))

if __name__=='__main__':main()
