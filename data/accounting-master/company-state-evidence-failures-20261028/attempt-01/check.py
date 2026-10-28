"""Original source timing, repeated evidence and all-history conflict discriminators."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
from fractions import Fraction as Q
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[3]; HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'tests'))
import test_company_state_information_views as fixtures
views=fixtures.views; native=views.intersection.native
PLAN='docs/plans/company-state-evidence-failures-20261028.md'
def dump(p,d):p.write_text(json.dumps(d,indent=2)+chr(10))
def ratio(q):return str(q.numerator)+'/'+str(q.denominator)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True)
 out=ap.parse_args().output.resolve();out.mkdir(parents=True,exist_ok=False);start=time.monotonic()
 checks=[];cases=[];base,sources,saved=fixtures.packet();original=deepcopy(sources[0]);corrected=fixtures.correction(original)
 budget=saved['views'][0]['native_result']['budget']; known={r['witness']['["measurement","held"]']:r for r in saved['views'][0]['independent_replays']}
 files=[Path(__file__),Path(fixtures.__file__),Path(views.__file__),Path(views.chronology.__file__),Path(views.intersection.__file__),Path(native.__file__),ROOT/PLAN,
 ROOT/'data/accounting-master/unified-program-20261028/failure-map.json',ROOT/'data/accounting-master/company-state-information-bridge-20261028/attempt-01/exact-results.json']
 locks={str(p.resolve().relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}
 def ck(n,a,e):checks.append(dict(name=n,passed=a==e,actual=a,expected=e))
 def run(label,rows,query,expected,ids=None,amount=None):
  before=deepcopy((base,rows,query));r=views.select(base,rows,query)
  ck(label+'/status',r['status'],expected);ck(label+'/input immutable',(base,rows,query)==before,True)
  for f in ['source_admission','actual_actor_knowledge','forecast_admission']:ck(label+'/'+f,r[f],False)
  ck(label+'/probability absent',r['probability_model'],None)
  if ids is not None:ck(label+'/selected ids',r.get('selected_ids'),ids)
  item=dict(id=label,input=dict(base=base,sources=rows,query=query),result=r)
  if amount is not None and r['status']=='selected_conditional_inputs':
   definition=r['attachment']['definition'];ck(label+'/quantity',definition['measurements']['observations']['held']['interval']['lower'],amount)
   a=native.assess(definition,budget);ck(label+'/native feasible',a['status'],'conditional_attachment_witness')
   replay=native.replay_witness(definition,budget,known[amount]['witness'])
   ck(label+'/full known history',replay,known[amount]['replay'])
   ck(label+'/cash history preserved',[(x['event_id'],x['postings'].get('paa.cash','0/1')) for x in replay['history']['events']],[(x['event_id'],x['postings'].get('paa.cash','0/1')) for x in known['6/1']['replay']['history']['events']])
   item.update(native_assessment=a,replay=replay)
  cases.append(item);return r
 # SIM-F003: exact public/system/actor cutoffs, with full native histories.
 r0=run('before correction',[original,corrected],fixtures.query(219),'selected_conditional_inputs',['H_report'],'6/1')
 for label,q,ids,amount in [
  ('at publication',fixtures.query(220),['H_correction'],'5/1'),
  ('as originally reported',fixtures.query(230,mode='original'),['H_report'],'6/1'),
  ('system before receipt',fixtures.query(230,'system',system=221),['H_report'],'6/1'),
  ('system at receipt',fixtures.query(230,'system',system=222),['H_correction'],'5/1'),
  ('public future but ingested',fixtures.query(219,'system',system=230),['H_report'],'6/1'),
  ('actor before receipt',fixtures.query(222,'actor',actor='treasury'),['H_report'],'6/1'),
  ('actor at receipt',fixtures.query(223,'actor',actor='treasury'),['H_correction'],'5/1')]:
  run(label,[original,corrected],q,'selected_conditional_inputs',ids,amount)
 for amount in ['4/1','7/1']:
  other=fixtures.correction(original,amount=amount)
  r=run('changed future amount '+amount,[original,other],fixtures.query(219),'selected_conditional_inputs',['H_report'],'6/1')
  ck('future amount '+amount+'/same policy evidence',r['policy_evidence'],r0['policy_evidence'])
  ck('future amount '+amount+'/same attachment',r['attachment']['definition'],r0['attachment']['definition'])
  ck('future amount '+amount+'/future absent from projection','H_correction' in json.dumps(r['policy_evidence']),False)
  ck('future amount '+amount+'/audit retains future',r['source_records']['H_correction'],other)
 unknown=deepcopy(corrected);unknown['published']=fixtures.clock(219,221)
 r=run('uncertain publication',[original,unknown],fixtures.query(220),'unresolved_information_view')
 ck('uncertain publication keeps both',r['possible_selected'],['H_correction','H_report'])
 ck('uncertain publication no attachment','attachment' in r,False)
 ck('uncertain publication no policy projection','policy_evidence' in r,False)
 r=run('unknown investor receipt',[original,corrected],fixtures.query(230,'actor',actor='investor'),'unresolved_information_view')
 ck('unknown receipt no attachment','attachment' in r,False)
 # SIM-F015: two provider identities, one disclosure identity/dependence group.
 single=run('one provider',[original],fixtures.query(230),'selected_conditional_inputs',['H_report'],'6/1')
 vendor=deepcopy(original);vendor['id']='vendor_B_H_report'
 double=run('two providers',[original,vendor],fixtures.query(230),'selected_conditional_inputs',['H_report','vendor_B_H_report'],'6/1')
 ck('two providers identical source bytes',double['source_records']['H_report']['source_sha256'],double['source_records']['vendor_B_H_report']['source_sha256'])
 ck('two providers shared dependence group',double['dependence_groups'],{'filing-A':['H_report','vendor_B_H_report']})
 ck('two providers same full intervals', {k:v['interval'] for k,v in double['attachment']['definition']['measurements']['observations'].items()}, {k:v['interval'] for k,v in single['attachment']['definition']['measurements']['observations'].items()})
 ck('two providers both provenance records',set(double['source_records'])=={'H_report','vendor_B_H_report'},True)
 reversed_=run('two providers reversed',[vendor,original],fixtures.query(230),'selected_conditional_inputs',['H_report','vendor_B_H_report'],'6/1')
 ck('provider order immaterial',reversed_,double)
 repeated=run('same identity twice',[original,original],fixtures.query(230),'selected_conditional_inputs',['H_report'],'6/1')
 ck('same identity duplicate marker',repeated['duplicate_records'],['H_report'])
 ck('same identity complete definition',repeated['attachment']['definition'],single['attachment']['definition'])
 bad=deepcopy(original);bad['content']='different bytes for same source id'
 r=run('identity collision',[original,bad],fixtures.query(230),'invalid')
 ck('identity collision reason',r['reason'],'source_identity_collision')
 noisy=deepcopy(original);noisy['role']='noisy_report'
 noisy2=deepcopy(vendor);noisy2['role']='noisy_report'
 r=run('duplicated noisy evidence',[noisy,noisy2],fixtures.query(230),'unsupported')
 ck('noisy evidence needs model',r['reason'],'nonhard_evidence_requires_likelihood')
 ck('noisy evidence no attachment','attachment' in r,False)
 # SIM-F016: all retained histories excluded, rather than select a convenient type.
 impossible=fixtures.correction(original,key='outside_all_histories',amount='9/1',day=220)
 impossible['supersedes']=[];impossible['lineage']='outside_all_histories'
 conflict=run('outside complete domain',[impossible],fixtures.query(230),'conditional_conflict',['outside_all_histories'])
 ck('conflict no attached definition','definition' in conflict['attachment'],False)
 ck('conflict retained domain',conflict['attachment']['conflicts'][0]['model_interval'],base['measurements']['observations']['held']['interval'])
 ck('conflict source retained',conflict['source_records']['outside_all_histories'],impossible)
 ck('conflict no native assessment',any(c['id']=='outside complete domain' and 'native_assessment' in c for c in cases),False)
 conflicting=deepcopy(vendor);conflicting['interval'].update(lower='5/1',upper='5/1')
 r=run('conflicting provider interpretation',[original,conflicting],fixtures.query(230),'conditional_conflict',['H_report','vendor_B_H_report'])
 ck('conflicting provider retains two assertions',len(r['attachment']['conflicts'][0]['sources']),2)
 ck('conflicting provider no definition','definition' in r['attachment'],False)
 # Exact probability examples are independent mathematical warnings, not native probabilities.
 prior=Q(1,2);l1=Q(4,5);l0=Q(1,5)
 one=prior*l1/(prior*l1+(1-prior)*l0)
 false_independence=prior*l1*l1/(prior*l1*l1+(1-prior)*l0*l0)
 ck('SIM-F015 one disclosure posterior',ratio(one),'4/5')
 ck('SIM-F015 wrong independent duplication',ratio(false_independence),'16/17')
 ck('SIM-F015 odds unjustifiably squared',ratio(false_independence/(1-false_independence)),'16/1')
 zero_normalizer=prior*0+(1-prior)*0
 ck('SIM-F016 no posterior normalizer',ratio(zero_normalizer),'0/1')
 ck('SIM-F016 every retained type contradicted',[t for t,likelihood in [(0,Q(0)),(1,Q(0))] if likelihood>0],[])
 for path,h in locks.items():ck('unchanged/'+path,sha256((ROOT/path).read_bytes()).hexdigest(),h)
 failures=[c['name'] for c in checks if not c['passed']]
 result=dict(status='fail' if failures else 'pass',checks=len(checks),cases=len(cases),full_native_replays=sum('replay' in c for c in cases),failures=failures,
 scope='Synthetic exact source views, duplicate hard constraints and conflicts; no actual source admission or posterior engine')
 dump(out/'checks.json',checks);dump(out/'cases.json',cases);dump(out/'verification.json',result)
 dump(out/'run-manifest.json',dict(git_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 command='python3 -B '+str(Path(__file__).relative_to(ROOT))+' --output '+str(out.relative_to(ROOT)),environment=sys.version,platform=platform.platform(),
 cpu_gpu='CPU only; no GPU imports or detection',random_seeds='N/A deterministic exact arithmetic',data_version='Protected insurance family and explicit hypothetical evidence dates and roles',
 wall_seconds=time.monotonic()-start,utc=datetime.now(timezone.utc).isoformat(),source_hashes=locks,plan=PLAN,result=str(out.relative_to(ROOT))))
 print(json.dumps(result));return bool(failures)
if __name__=='__main__':raise SystemExit(main())

