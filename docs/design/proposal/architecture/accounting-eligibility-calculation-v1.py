"""Finite calculations for the eight saved document examples; no runtime API."""
from pathlib import Path
from decimal import Decimal
import hashlib, json, sys, time, platform
start = time.monotonic()
root = Path(__file__).resolve().parents[4]
p = root / 'docs/design/proposal/architecture'
read = lambda name: json.loads((p/name).read_text())
hashfile = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
f = read('accounting-eligibility-fixtures-v1.json')
checks=[]
def check(name, result): checks.append({'id':name, 'passed':bool(result)})
check('eight named cases', [c['id'] for c in f['cases']] == [f'E{i:02}' for i in range(1,9)])
summary=[]
for c in f['cases']:
 v={k:x['value'] for k,x in c['complete_inputs'].items()}
 findings={}
 if not v['C01']['within_retained_window']: findings['C01']='outside_scope'
 if v['C03']['party_to_contract'] is False: findings['C03']='ineligible'
 if v['C05']['rationale_available'] is None: findings['C05']='unresolved'
 if v['C07']['incremental'] is None: findings['C07']='unresolved'
 branch='not_applicable'
 if Decimal(v['C06']['price']) != Decimal(v['C06']['fair_value']):
  a=v['C09']['identical_instrument_active_market_quote']; b=v['C09']['technique_only_observable_market_data']
  branch='B5.1.2A(a)' if a is True or b is True else ('B5.1.2A(b)' if a is False and b is False else 'unknown')
  if branch=='unknown': findings.update(C09='unresolved', C10='unresolved')
  else: findings['C10']='outside_scope'
 status=next((s for s in f['status_precedence'] if s in findings.values()),'eligible')
 actual={x['condition']:x['status'] for x in c['condition_findings'] if x['status'] in f['status_precedence']}
 check(c['id']+' complete condition coverage',set(v)==set(f['condition_order']) and len(c['condition_findings'])==10)
 check(c['id']+' provenance', all(set(['value','unknown_reason','provenance','scope','version']) <= set(x) for x in c['complete_inputs'].values()))
 check(c['id']+' findings derived from facts',actual==findings)
 check(c['id']+' decision and branch',c['expected_assessment']['status']==status and c['expected_assessment']['valuation_branch']==branch)
 check(c['id']+' reasons retained',set(c['expected_assessment']['reasons'])==set(findings))
 balanced=sum(Decimal(x[1])-Decimal(x[2]) for x in c['limited_screen_input']['candidate_journal'])==0
 check(c['id']+' limited comparator arithmetic', balanced and c['limited_screen_input']['category']=='FVTPL')
 check(c['id']+' no mutation or posting',not c['expected_assessment']['posting_permitted'] and c['expected_assessment']['state_delta'] is None and set(c['no_mutation'].values())=={'unchanged'})
 check(c['id']+' noneligible has no journal',status=='eligible' or c['expected_assessment']['journal_proposal'] is None)
 summary.append({'case':c['id'],'limited_screen':'pass','assessment':status,'branch':branch})
orig=json.loads((root/'docs/design/proposal/methods/standards-fixtures-v1.json').read_text())
a01=next(x for x in orig['acquisitions'] if x['id']=='A01');a03=next(x for x in orig['acquisitions'] if x['id']=='A03')
check('A01 arithmetic retained',a01['journal']==f['cases'][0]['expected_assessment']['journal_proposal'] and sum(Decimal(x[1])-Decimal(x[2]) for x in a01['journal'])==0)
check('A03 retained unresolved',a03['observable_valuation_evidence'] is None and a03['journal']==[] and a03['expected']=='TREATMENT_UNRESOLVED')
snap=read('accounting-eligibility-inputs-v1.json')['inputs']
permitted={'data/accounting-master/deliverables/P16/'+s for s in ['architecture.json','result.md','progress.md']}
for name,digest in snap.items():
 if name not in permitted: check('preserved '+name,(root/name).is_file() and hashfile(root/name)==digest)
register=json.loads((root/'docs/design/proposal/methods/standards-source-register-v1.json').read_text())
s9=next(x for x in register['sources'] if x['id']=='S9')
for k in ['pdf','text']:check('S9 '+k+' source hash',hashfile(root/s9[k]['path'])==s9[k]['sha256'])
text=(root/s9['text']['path']).read_text();anchors=[]
for token in ['2.1     This','3.1.1   An','3.1.2   A','4.1.1    Unless','4.1.5   Despite','5.1.1      Except','B3.1.1   As','B3.1.3   A','transaction costs                        Incremental','B5.1.1     The','B5.1.2A The','(a)       at the measurement required','B5.4.8   Transaction']:
 offset=text.find(token);check('source anchor '+token,offset>=0)
 anchors.append({'text':token,'newline_line':text[:offset].count('\n')+1,'physical_pdf_page':text[:offset].count('\f')+1})
paths=[Path(__file__),p/'accounting-eligibility-dossier-v1.md',p/'accounting-eligibility-fixtures-v1.json',p/'accounting-eligibility-inputs-v1.json']+[root/s9[k]['path'] for k in ['pdf','text']]
result={'schema_version':'accdsl.eligibility.verification.v1','passed':all(x['passed'] for x in checks),'checks':checks,'total':len(checks),'passed_count':sum(x['passed'] for x in checks),'cases':summary,'source_anchors':anchors,'manifest':{'command':'PYTHONDONTWRITEBYTECODE=1 python3 docs/design/proposal/architecture/accounting-eligibility-calculation-v1.py','python':sys.version,'executable':sys.executable,'platform':platform.platform(),'environment':'existing system Python; standard library only','git_commit':'N/A: existing .git marker is unusable; no git initialized','CPU_GPU':'CPU document arithmetic; no GPU detection or framework imports','data_version':'saved synthetic assessment examples v1; hashes below','seeds':'N/A deterministic decimal arithmetic','plan_file':'data/accounting-master/runs/20261005T133743-c8a796f3/P16/replan-2/plan-0.response.json','result_file':'data/accounting-master/deliverables/P16/result.md','output_paths':['docs/design/proposal/architecture/accounting-eligibility-verification-v1.json'],'wall_seconds':time.monotonic()-start},'input_hashes':{str(x.relative_to(root)):hashfile(x) for x in paths},'limits':'Finite saved-input calculation only; no complete validator, runtime enforcement, accounting validity, statistical ranking or human acceptance.'}
with (p/'accounting-eligibility-verification-v1.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps({'passed':result['passed'],'checks':len(checks),'failures':[x for x in checks if not x['passed']]}))
