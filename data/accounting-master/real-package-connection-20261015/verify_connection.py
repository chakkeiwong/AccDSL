"""Independent documentary verification; no builder import or product execution."""
from collections import defaultdict
from copy import deepcopy
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,re,subprocess,time,traceback
from jsonschema import Draft202012Validator,FormatChecker

OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
def sha(x):return hashlib.sha256(x).hexdigest()
def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def number(x):
 q=Q(int(x['n']),int(x['d']))
 assert x=={'n':str(q.numerator),'d':str(q.denominator)}
 return q
def walk(x,predicate):
 if isinstance(x,dict):
  if predicate(x):yield x
  else:
   for v in x.values():yield from walk(v,predicate)
 elif isinstance(x,list):
  for v in x:yield from walk(v,predicate)
def refs(x):return walk(x,lambda v:set(v)=={'kind','schema','digest'})
def blobs(x):return walk(x,lambda v:v.get('kind')=='blob')
def pointer(x,p):
 for part in p.strip('/').split('/'):
  part=part.replace('~1','/').replace('~0','~');x=x[int(part)] if isinstance(x,list) else x[part]
 return x

class Check:
 def __init__(self):
  self.data=json.loads((OUT/'portable-exchanges.json').read_text());self.schemas=json.loads((OUT/'record-schemas.json').read_text())
  self.registry=self.data['record_registry'];self.alias=self.data['aliases'];self.checks=[];self.derived={};self.cache={}
 def record(self,r):
  if isinstance(r,str):r=self.alias[r]
  v=self.registry[r['digest']];assert (v['kind'],v['schema'])==(r['kind'],r['schema']);return v
 def body(self,r):return self.record(r)['body']
 def raw(self,b):
  if b['digest'] not in self.cache:self.cache[b['digest']]=(ROOT/self.data['blobs'][b['digest']]['path']).read_bytes()
  return self.cache[b['digest']]
 def source(self,key):return json.loads(self.raw(self.body(key)['blob']))
 def test(self,name,fn):
  try:
   result=fn();assert result is not False;self.checks.append({'name':name,'passed':True})
  except Exception as e:self.checks.append({'name':name,'passed':False,'error':str(e)[:600] or traceback.format_exc(limit=2)[-600:]})
 def equal(self,name,a,b):self.test(name,lambda:a==b)
 def closure(self,r,active=None,done=None):
  active=set() if active is None else active;done=set() if done is None else done;d=r['digest']
  assert d not in active,'cycle'
  if d in done:return done
  active.add(d)
  for child in self.record(r)['dependencies']:self.closure(child,active,done)
  active.remove(d);done.add(d);return done
 def validate_record(self,d,r):
  assert set(r)=={'kind','schema','key','revision','body','dependencies'} and r['revision']==0
  assert r['schema']==self.schemas['schema_ids'][r['kind']]
  Draft202012Validator(self.schemas['$defs'][r['kind']],format_checker=FormatChecker()).validate(r['body'])
  assert sha(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+canonical(r))==d,'digest'
  ds={canonical(x):x for x in refs(r['body'])};assert r['dependencies']==[ds[k] for k in sorted(ds)]
  for x in ds.values():self.body(x)
  for x in blobs(r):assert sha(self.raw(x))==x['digest'] and len(self.raw(x))==x['byte_length']
  for x in walk(r,lambda x:set(x)=={'n','d'}):number(x)
 def structural(self):
  for d,r in self.registry.items():self.test('record:'+r['key'],lambda d=d,r=r:self.validate_record(d,r))
  for r in self.alias.values():self.test('acyclic:'+self.record(r)['key'],lambda r=r:self.closure(r))
  self.equal('mode',self.data['runtime_executed'],False)
  expected={'annual':'ec74758cd767465362c641cf2fd5d8fedd477aed2bf7f62117e67610435dcb88','interim':'2f7629f0733f75b3155dd52f7ae6a8724468e3cde1a9ce32fbce96d98f1ec27e','later':'eb08113db1fa3b847936c68ddf7bd9c31b5d708c14794c94355fd38ac3846850'}
  for k,d in expected.items():self.equal('source-hash:'+k,self.body('source.'+k)['original_blob']['digest'],d)
  self.equal('inventory-original-hash',self.body('package-original')['blob']['digest'],'df9ee3d69abb66dc033ecc83deb6320ce3312688feabed62410bc771a3ef41e0')
  self.equal('separate-jpmorgan-hash',self.body('jpmorgan.source')['original_blob']['digest'],'95ca23db9e9e64045860a3f8c0f0a5de85a28146690955868bd3d304625f2d86')
  self.equal('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT),(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
  self.equal('protected-294-pdf',sha((ROOT/'docs/design/proposal/manuscript-corporate-portable-20261015/accounting-product-proposal.pdf').read_bytes()),'38c4edc2c7508e303be5c05e894768e3ab14be7c0653ae6b7cce28ded8b23a43')
 def sources(self):
  mapping=self.source('package-map');pkg=self.body('apple.package')
  counts={'reference_frontier':70,'package_obligations':7,'note_dispositions':23,'material_assertions':32,'additional_frontier':7}
  for cat,n in counts.items():
   rows=[self.body(r) for r in pkg['inventory_refs'] if self.body(r)['category']==cat];self.equal('inventory-count:'+cat,len(rows),n)
   self.equal('inventory-pointers:'+cat,[x['pointer'] for x in rows],[f'/{cat}/{i}' for i in range(n)])
   for i,x in enumerate(rows):
    item=pointer(self.source(self.record(x['file_ref'])['key']),x['pointer']);self.equal('inventory-retained:'+cat+str(i),item,mapping[cat][i])
    if cat=='additional_frontier':self.equal('frontier-id:'+str(i),x['item_id'],item['frozen']['id'])
  for r in pkg['assertion_refs']:
   b=self.body(r);s=self.raw(b['extraction_blob']).decode();actual=s[b['start']:b['end']]
   self.equal('quote:'+self.record(r)['key'],actual,b['quote']);self.equal('quote-hash:'+self.record(r)['key'],sha(actual.encode()),b['span_sha256'])
   orig=next(x for x in mapping['material_assertions'] if 'assertion.'+x['id']==self.record(r)['key'])['source']
   self.equal('assertion-source:'+self.record(r)['key'],self.body(b['source_ref'])['original_blob']['digest'],orig['original_sha256'])
  for r in self.registry.values():
   if r['kind']!='Observation':continue
   b=r['body'];d=json.loads(self.raw(self.body(b['reading_file_ref'])['blob']));row=pointer(d,b['pointer']);ctx=self.body(b['context_ref'])
   self.equal('literal:'+r['key'],b['literal'],row['literal'])
   expected={'tag':'reported_dash','literal':row['literal']} if row['value'] is None else {'tag':'known_displayed','amount':{'n':str(Q(row['value']).numerator),'d':str(Q(row['value']).denominator)}}
   self.equal('amount:'+r['key'],b['value'],expected)
   parent=pointer(d,b['pointer'].rsplit('/',1)[0]) if b['pointer'].endswith(('/opening','/comparison')) else row
   self.equal('unit:'+r['key'],ctx['unit'],parent['unit'])
   self.equal('period:'+r['key'],ctx['period'],row.get('date',row.get('period','FY'+row.get('fiscal_year','2024'))))
   self.equal('reading-source:'+r['key'],self.body(b['source_ref'])['reading_file_ref'],b['reading_file_ref'])
  report=self.body('apple.reported-statements')
  for k,n in [('annual_refs',102),('interim_refs',100),('annual_opening_refs',27),('interim_comparison_refs',27)]:self.equal('report-count:'+k,len(report[k]),n)
  for k in ['annual_opening_refs','interim_comparison_refs']:
   self.test('only-stock-comparisons:'+k,lambda k=k:all(self.body(self.body(r)['context_ref'])['measurement_kind']=='instant balance' for r in report[k]))
  allowed=self.body(report['view_ref'])['source_refs']
  self.test('report-original-view-only',lambda:all(self.body(r)['source_ref'] in allowed for k in ['annual_refs','annual_opening_refs','interim_refs','interim_comparison_refs'] for r in report[k]))
  self.equal('no-recursive-closure',pkg['recursive_closure'],False);self.equal('no-complete-semantics',pkg['semantics_complete'],False)
  self.equal('unknown-actual-feasibility',self.body('apple.family')['feasibility']['tag'],'unknown')
  for k in ['annual','interim','later']:
   self.test('unknown-clocks:'+k,lambda k=k:all(self.body('source.'+k)[t]['tag']=='unknown' for t in ['public_at','ingested_at','reviewed_at']))
  for r in self.body('apple.connected')['later_comparative_refs']:
   b=self.body(r);self.equal('later-view:'+b['row_id'],b['source_ref'],self.alias['source.later'])
  for key in ['original-segment-detail.output','later-segment-detail.output']:
   b=self.body(key);eligible=self.body(b['view_ref'])['source_refs']
   self.test('segment-eligibility:'+key,lambda b=b,eligible=eligible:all(x['observation_ref'] is None or self.body(x['observation_ref'])['source_ref'] in eligible for x in b['items']))
  self.equal('later-cost',number(self.body('later-segment-detail.output')['items'][0]['value']['amount']),-89587)
  self.equal('later-marketing',number(self.body('later-segment-detail.output')['items'][1]['value']['amount']),-9802)
  self.test('original-detail-unknown',lambda:all(x['value']['tag']=='unknown' for x in self.body('original-segment-detail.output')['items']))
 def admission(self,r):
  op=r['operation'];a=r['arguments'];signature=self.body(r['signature_ref']);view=self.body(r['view_ref'])
  if a['tag']!=op:return 'OPERATION_TAG_MISMATCH'
  if signature['operation']!=op or signature['profile_ref']!=r['profile_ref']:return 'SIGNATURE_MISMATCH'
  if r['profile_ref']!=self.data['profile_ref']:return 'PROFILE_MISMATCH'
  if a['value'].get('view_ref',r['view_ref'])!=r['view_ref']:return 'VIEW_MISMATCH'
  issuer=a['value'].get('issuer',view['issuer'])
  if issuer!=view['issuer']:return 'ISSUER_CONTEXT_MISMATCH'
  for key in ['package_ref','family_ref','connected_ref','basis_ref','source_ref']:
   if key in a['value'] and self.body(a['value'][key]).get('issuer',issuer)!=issuer:return 'ISSUER_CONTEXT_MISMATCH'
  if op=='history.query@1':
   if not 0<=number(a['value']['alpha'])<=1:return 'ALPHA_OUTSIDE_DOMAIN'
   if (a['value']['information_mode']=='named_sources')!=(a['value']['cutoff'] is None):return 'CUTOFF_MODE_MISMATCH'
  if op=='scenario.project@1':
   if self.body(a['value']['history_ref'])['basis_ref']!=a['value']['basis_ref']:return 'BASIS_MISMATCH'
   if any(a['value'][k] is not None and a['value'][k] not in [1,2] for k in ['capital_period','expense_period']):return 'SETTLEMENT_PERIOD_OUTSIDE_DOMAIN'
  return None
 def exchanges(self):
  for x in self.data['exchanges']:
   req=self.body(x['request_ref']);res=self.body(x['response_ref']);raw=self.raw(self.body(x['submission_ref'])['blob_ref']);name=x['id']
   try:submitted=json.loads(raw);error=self.admission(submitted['body'])
   except json.JSONDecodeError:error='INVALID_JSON'
   self.equal('submission-binding:'+name,res['submission_ref'],x['submission_ref'])
   self.equal('world-preserved:'+name,x['world_before'],x['world_after'])
   self.test('no-mutation:'+name,lambda res=res:req['expected_head'] is None and res['receipt_ref'] is None and res['commit_observation']=='not_committed')
   if error:
    self.equal('rejection-code:'+name,res['diagnostics'][0]['code'],error)
    self.test('rejection-empty:'+name,lambda res=res:all(res[k] is None for k in ['request_ref','operation','input_view_ref','payload','coverage']))
    self.equal('rejection-status:'+name,res['statuses']['structural_validity'],'invalid');continue
   self.equal('exact-request-bytes:'+name,raw,canonical(self.record(x['request_ref'])))
   self.equal('request-response:'+name,res['request_ref'],x['request_ref'])
   self.equal('view-response:'+name,res['input_view_ref'],req['view_ref'])
   self.equal('operation-response:'+name,res['operation'],req['operation'])
   self.equal('payload-tag:'+name,res['payload']['tag'],req['operation'])
   allowed=self.body(req['signature_ref'])['payload_kinds']
   self.test('payload-kinds:'+name,lambda res=res,allowed=allowed:all(r['kind'] in allowed for r in res['payload']['result_refs']))
   coverage=res['coverage'];regions=[r for k in ['completed','unresolved','unsupported','infeasible','cancelled'] for r in coverage[k]]
   self.equal('domain-request:'+name,self.body(coverage['domain_ref'])['request_ref'],x['request_ref'])
   scopes=[self.body(r)['scope'] for r in regions];self.equal('distinct-scopes:'+name,len(scopes),len(set(scopes)))
   self.test('coverage-domain:'+name,lambda regions=regions,coverage=coverage:all(self.body(r)['domain_ref']==coverage['domain_ref'] for r in regions))
   if res['disposition'] in ['partial','unsupported']:self.test('unresolved-obligations:'+name,lambda res=res:len(res['unresolved'])>0)
   if req['operation']=='history.query@1' and req['arguments']['value']['information_mode']!='named_sources':
    self.test('clock-refusal:'+name,lambda res=res:all(item['value']['tag']=='unknown' for r in res['payload']['result_refs'] for item in self.body(r)['items']))
  self.equal('reported-complete',self.body('result.reported-statements')['disposition'],'completed')
  self.equal('connected-partial',self.body('result.connected-partial')['disposition'],'partial')
  self.equal('unsupported-probability',self.body('result.probability-refused')['disposition'],'unsupported')
  self.equal('unsupported-depreciation',self.body('result.unsupported-depreciation')['disposition'],'unsupported')
 def relationships(self):
  annual={r['id']:r for r in self.source('annual-readings')['rows']}
  for name in ['annual','interim']:
   data=self.source(name+'-readings');rows={r['id']:r for r in data['rows']};values={k:Q(r['value']) if r['value'] is not None else None for k,r in rows.items()}
   for r in rows.values():
    old=r.get('opening' if name=='annual' else 'comparison')
    if old and r['statement']=='balance':values['opening.'+r['id'].split('.',1)[1]]=Q(old['value'])
   def value(k):
    if k not in values:return Q(k)
    if values[k] is None:
     assert name=='annual' and k=='cash_flow.debt_issuance' and rows[k]['literal']=='—'
     return Q(0) # Only the explicitly preserved displayed arithmetic convention.
    return values[k]
   for r in self.source(name+'-relations')['relations']:
    if 'terms' not in r:
     self.equal(name+':'+r['id'],Q(annual[r['annual_row']]['value']),values[r['interim_row']]);continue
    calculated=sum(Q(t['coefficient'])*value(t['row']) for t in r['terms']);target=value(r['target'])
    self.equal(name+':'+r['id']+':computed',calculated,Q(r['computed']));self.equal(name+':'+r['id']+':target',target,Q(r['target_value']));self.equal(name+':'+r['id']+':residual',calculated-target,Q(r['residual']))
    if r['residual']!='0':self.test(name+':residual-not-journal:'+r['id'],lambda r=r:'explanatory' in r['diagnostic_role'])
  self.equal('cash-population-772',Q(annual['cash_flow.opening']['value'])-Q(annual['balance.cash']['opening']['value']),772)
 def journal_totals(self,h):
  totals=defaultdict(Q)
  for journal in h['journals']:
   assert sum(number(x['signed_amount']) for x in journal['lines'])==0,'unbalanced journal'
   for x in journal['lines']:totals[x['account']]+=number(x['signed_amount'])
  return totals
 def derive_difference(self,alpha,expense_row='operations.products_cost',liability_row='balance.other_liabilities_current',duplicate=False,tax=0):
  left=self.journal_totals(self.body('conditional.H1'));right=self.journal_totals(self.body('conditional.H2'))
  d={k:right[k]-left[k] for k in left.keys()|right.keys()};rows={r['id']:r for r in self.source('annual-readings')['rows']};v={k:Q(0) for k in rows}
  v['operations.products_cost']=d['retirement_loss'];v[expense_row]+=d['expense']
  v['operations.cost']=v['operations.products_cost']+v['operations.services_cost'];v['operations.gross_margin']=-v['operations.cost']
  v['operations.operating_expenses']=v['operations.research']+v['operations.selling'];v['operations.operating_income']=v['operations.gross_margin']-v['operations.operating_expenses']
  v['operations.pretax']=v['operations.operating_income'];v['operations.tax']=Q(tax);profit=v['operations.pretax']-v['operations.tax']
  for key in ['operations.net_income','comprehensive.net_income','comprehensive.comprehensive_income','equity.net_income','equity.retained_closing','equity.closing','balance.retained','balance.equity','cash_flow.net_income']:v[key]=profit
  for kind in ['basic','diluted']:v['operations.eps_'+kind]=1000*profit/Q(rows['operations.shares_'+kind]['value'])
  v['balance.ppe']=d['ppe_cost']+d['accumulated_depreciation'];v['balance.cash']=d['cash'];v['balance.assets_current']=d['cash'];v['balance.assets_noncurrent']=v['balance.ppe'];v['balance.assets']=v['balance.assets_current']+v['balance.assets_noncurrent']
  v['balance.other_liabilities_current']=-d['capital_payable']+tax;v[liability_row]+=-d['expense_liability']
  v['balance.liabilities_current']=v['balance.other_liabilities_current']+v['balance.payables'];v['balance.liabilities']=v['balance.liabilities_current'];v['balance.liabilities_equity']=v['balance.liabilities']+profit
  v['cash_flow.other_adjustments']=d['retirement_loss']+alpha*d['expense']
  wc='cash_flow.payables' if liability_row=='balance.payables' else 'cash_flow.other_liabilities';v[wc]=(1 if duplicate else 1-alpha)*d['expense']+tax
  v['cash_flow.depreciation']=d['depreciation_expense'];v['cash_flow.operating']=profit+v['cash_flow.other_adjustments']+v[wc]+v['cash_flow.depreciation']
  v['cash_flow.ppe_payments']=d['cash'];v['cash_flow.investing']=d['cash'];v['cash_flow.change']=v['cash_flow.operating']+v['cash_flow.investing'];v['cash_flow.closing']=v['cash_flow.change']
  return v
 def accounting(self):
  originals=self.source('asset-histories')['histories']
  for i,name in enumerate(['H1','H2']):
   h=self.body('conditional.'+name);original=originals[i]
   for authored,retained in zip(h['journals'][:-1],original['journals']):
    self.equal('journal-original:'+name+authored['event'],[(x['account'],number(x['signed_amount'])) for x in authored['lines']],[(x['account'],Q(x['debit'])-Q(x['credit'])) for x in retained['postings']])
   totals=self.journal_totals(h);self.equal('capital-obligation:'+name,-totals['capital_payable'],number(h['capital_liability']));self.equal('expense-obligation:'+name,-totals['expense_liability'],number(h['expense_liability']))
   self.equal('expense-domain:'+name,number(h['expense_liability']),2000-1000*i)
   self.equal('no-actual-admission:'+name,h['actual_history_admission'],False)
  for ref in self.body('apple.connected')['difference_refs']:
   b=self.body(ref);alpha=number(b['alpha']);actual={r['row_id']:number(r['value']) for r in b['row_differences']};expected=self.derive_difference(alpha)
   self.equal('all-row-differences:'+str(alpha),actual,expected);self.equal('row-equality:'+str(alpha),b['all_displayed_rows_equal'],not any(expected.values()))
   self.equal('absolute-base-still-unknown:'+str(alpha),b['absolute_feasibility']['tag'],'unknown')
  cases={'different_expense_rows':{'expense_row':'operations.research'},'different_liability_rows':{'liability_row':'balance.payables'},'duplicated_noncash_addback':{'duplicate':True},'different_tax_consequences':{'tax':100}}
  for name,args in cases.items():
   computed={k:v for k,v in self.derive_difference(Q(1),**args).items() if v};expected={k:Q(v) for k,v in self.source('conditional-repair')['counterexamples'][name].items()}
   self.equal('counterexample:'+name,computed,expected)
  self.equal('gross-class-no-cancellation',self.source('conditional-repair')['counterexamples']['different_gross_asset_classes'],{'machinery_gross':1000,'buildings_gross':-1000,'gross_total':0})
  for ref in self.body('apple.connected')['settlement_refs']:
   b=self.body(ref);h=self.body(b['history_ref']);start={'capital_liability':number(h['capital_liability']),'expense_liability':number(h['expense_liability'])};balances=dict(start);cash=Q(0);cfo=Q(0);cfi=Q(0)
   for period in b['periods']:
    n=period['period'];posted=defaultdict(Q)
    for journal in period['journals']:
     self.equal('settlement-balanced:'+self.record(ref)['key']+str(n)+journal['event'],sum(number(x['signed_amount']) for x in journal['lines']),0)
     for x in journal['lines']:posted[x['account']]+=number(x['signed_amount'])
    for kind in ['capital','expense']:
     k=kind+'_liability';scheduled=start[k] if n==b[kind+'_period'] else Q(0);self.equal('schedule:'+self.record(ref)['key']+str(n)+kind,posted[k],scheduled);balances[k]-=posted[k]
    amount=posted['cash'];e={k:number(v) for k,v in period['effects'].items()}
    self.equal('settlement-cash:'+self.record(ref)['key']+str(n),amount,-posted['capital_liability']-posted['expense_liability'])
    expected={k:Q(0) for k in e};expected.update({k:amount for k in ['cash','assets','liabilities','cash_change']});expected.update(capital_liability_close=balances['capital_liability'],expense_liability_close=balances['expense_liability'],operating=-posted['expense_liability'],investing=-posted['capital_liability'])
    self.equal('all-settlement-effects:'+self.record(ref)['key']+str(n),e,expected)
    cash+=amount;cfo+=e['operating'];cfi+=e['investing']
   self.equal('eventual-joint-total:'+self.record(ref)['key'],cash,-3082);self.equal('joint-components:'+self.record(ref)['key'],(cfo,cfi),(-start['expense_liability'],-start['capital_liability']))
   self.equal('no-forecast-admission:'+self.record(ref)['key'],b['forecast_admission'],False)
  missing=self.body('unknown-settlement-dates.output');known={x['name']:number(x['value']['amount']) for x in missing['items'] if x['value']['tag']=='conditional_derived'}
  self.equal('unknown-dates-preserve-eventual',known,{'eventual_operating':Q(-2000),'eventual_investing':Q(-1082),'eventual_cash_change':Q(-3082)})
  self.equal('mixed-marginals-invalid',min(-2000,-1000)+min(-1082,-2082),-4082)
  self.derived['joint_settlement_pairs']=[[-2000,-1082],[-1000,-2082]];self.derived['mixed_extrema_rejected']=-4082
 def conflict(self):
  source=self.source('conflict-support');review=self.source('conflict-review')
  for anchor in source['anchors']:
   raw=(ROOT/anchor['source_text']).read_bytes();normalized=' '.join(raw.decode().split())
   self.equal('conflict-anchor-hash:'+anchor['id'],sha(raw),anchor['source_text_sha256'])
   self.equal('conflict-quote:'+anchor['id'],normalized[anchor['normalized_start']:anchor['normalized_end']],anchor['quote'])
  stale=set(review['changed_inputs']);deps=review['dependencies']
  for _ in range(len(deps)):
   stale|={key for key,values in deps.items() if any(v in stale for v in values)}
  calculated=stale&set(deps);proposal=self.body('jpmorgan.supersede_counterfactual_prior')
  self.equal('transitive-stale',set(proposal['stale_nodes']),calculated);self.equal('reusable-conflict',set(proposal['reusable_nodes']),set(deps)-calculated)
  self.equal('literal-preserved',proposal['literal_page'],156);self.equal('navigation-located',(proposal['navigation_printed_page'],proposal['navigation_physical_page']),(163,165))
  self.equal('same-offset-not-reconciliation',158-156,165-163)
  self.test('no-cross-company-dependency',lambda:all(not self.registry[d]['key'].startswith('jpmorgan') for d in self.closure(self.alias['apple.connected'])))
 def mutations(self):
  req=self.body('request.query-difference.1');variants=[]
  r=deepcopy(req);r['arguments']['tag']='source.prepare@1';variants.append(('tag',r,'OPERATION_TAG_MISMATCH'))
  r=deepcopy(req);r['signature_ref']=self.alias['signature.source.prepare@1'];variants.append(('signature',r,'SIGNATURE_MISMATCH'))
  r=deepcopy(req);r['arguments']['value']['issuer']='JPMorgan';variants.append(('issuer',r,'ISSUER_CONTEXT_MISMATCH'))
  r=deepcopy(req);r['arguments']['value']['view_ref']=self.alias['view.later'];variants.append(('view',r,'VIEW_MISMATCH'))
  r=deepcopy(req);r['arguments']['value']['alpha']={'n':'-1','d':'2'};variants.append(('alpha',r,'ALPHA_OUTSIDE_DOMAIN'))
  r=deepcopy(req);r['arguments']['value']['cutoff']='2024-09-29T00:00:00Z';variants.append(('cutoff',r,'CUTOFF_MODE_MISMATCH'))
  for name,r,expected in variants:self.equal('mutation-admission:'+name,self.admission(r),expected)
  d,r=next(iter(self.registry.items()));mut=deepcopy(r);mut['revision']=1
  self.test('mutation-digest-rejected',lambda:sha(('accdsl.portable.v1/'+r['schema']).encode()+b'\0'+canonical(mut))!=d)
  b=self.body('source.annual')['original_blob'];self.test('mutation-source-byte-rejected',lambda:sha(self.raw(b)+b'!')!=b['digest'])
  observed=deepcopy(self.body('annual.cash_flow.debt_issuance'));observed['value']={'tag':'known_displayed','amount':{'n':'0','d':'1'}}
  self.test('mutation-dash-to-zero-rejected',lambda:observed['value']!={'tag':'reported_dash','literal':'—'})
  h=deepcopy(self.body('conditional.H1'));h['journals'][0]['lines'][0]['signed_amount']={'n':'5637','d':'1'}
  def unbalanced():
   try:self.journal_totals(h)
   except AssertionError:return True
   return False
  self.test('mutation-unbalanced-journal-rejected',unbalanced)
  wrong=self.derive_difference(Q(1));wrong['cash_flow.other_adjustments']=Q(1000)
  self.test('mutation-report-row-rejected',lambda:wrong!=self.derive_difference(Q(1)))
  self.test('mutation-later-source-in-original-rejected',lambda:self.alias['source.later'] not in self.body('view.annual')['source_refs'])

def main():
 start=time.monotonic();v=Check()
 for name in ['structural','sources','relationships','exchanges','accounting','conflict','mutations']:v.test('phase:'+name,lambda name=name:getattr(v,name)())
 failed=[x for x in v.checks if not x['passed']];result={'passed':not failed,'checks':v.checks,'derived':v.derived,'check_count':len(v.checks),'failed_count':len(failed),'wall_seconds':time.monotonic()-start,'evidence_class':'documentary exact arithmetic and specification integrity; no runtime or accounting admission'}
 (OUT/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['passed','check_count','failed_count','wall_seconds']}));print(json.dumps(failed[:15],indent=2));raise SystemExit(bool(failed))
if __name__=='__main__':main()
