"""Independently derive documentary financing cases; no builder import."""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import hashlib,json,subprocess,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 start=time.monotonic();checks=[];data=json.loads((OUT/'cases.json').read_text());sources=json.loads((OUT/'source-support.json').read_text());cases={c['id']:c for c in data['cases']}
 def check(name,ok,detail=None):checks.append({'name':name,'passed':bool(ok),'detail':detail})
 for src in sources['authorities']:
  check('source-pdf:'+src['id'],sha(ROOT/src['pdf'])==src['pdf_sha256']);check('source-text:'+src['id'],sha(ROOT/src['text'])==src['text_sha256']);text=(ROOT/src['text']).read_text()
  for span in src['spans']:
   s=text[span['start']:span['end']];check('source-span:'+src['id']+span['id'],s==span['text'] and hashlib.sha256(s.encode()).hexdigest()==span['sha256'])
  check('historical-only:'+src['id'],src['current_authority_claim'] is False)
 for c in cases.values():
  ledger=defaultdict(Q,{k:Q(v) for k,v in c['opening'].items()});check(c['id']+':opening-balanced',sum(ledger.values())==0);opening_cash=ledger['cash'];opening_equity=-ledger['capital'];oci=owner=basis=Q(0);flows=defaultdict(Q);seen=set()
  for e in c['events']:
   name=c['id']+':'+e['id'];check(name+':distinct-event',e['id'] not in seen);seen.add(e['id'])
   movement=defaultdict(Q)
   for p in e['postings']:movement[p['account']]+=Q(p['debit_signed'])
   check(name+':balanced',sum(movement.values())==0)
   for k,v in movement.items():ledger[k]+=v
   flow={k:Q(v) for k,v in e['cash_flows'].items()};check(name+':cash-classification-total',sum(flow.values())==movement['cash'])
   oci+=Q(e['oci']);owner+=Q(e['owner_equity_change']);basis+=Q(e['direct_basis_equity_change'])
   for k,v in flow.items():flows[k]+=v
   profit=-ledger['income']-ledger['expense'];assets=ledger['cash']+ledger['inventory']+max(ledger['derivative'],0);liabilities=-ledger['debt']+max(-ledger['derivative'],0);equity=-ledger['capital']-ledger['reserve']+profit
   check(name+':balance-sheet',assets==liabilities+equity);check(name+':equity-bridge',equity==opening_equity+profit+oci+owner+basis);check(name+':cash-bridge',ledger['cash']==opening_cash+sum(flows.values()))
   expected={k:Q(v) for k,v in e['expected_report'].items()};actual={'cash':ledger['cash'],'inventory':ledger['inventory'],'derivative_net':ledger['derivative'],'debt':-ledger['debt'],'reserve':-ledger['reserve'],'pretax_profit':profit,'oci':oci,'comprehensive_pretax':profit+oci,'owner_equity_change':owner,'direct_basis_equity_change':basis,'assets':assets,'liabilities':liabilities,'pretax_equity':equity,'equity_bridge':opening_equity+profit+oci+owner+basis,**flows}
   check(name+':entire-report',actual==expected)
  check(c['id']+':tax-unknown',c['tax_status']=='uncomputed' and c['pretax_only'])
 def lines(case,event):return {p['account']:Q(p['debit_signed']) for p in next(e for e in cases[case]['events'] if e['id']==event)['postings']}
 def final(case):return {k:Q(v) for k,v in cases[case]['events'][-1]['expected_report'].items()}
 # Discount using an annuity identity independent of the builder's summation.
 def pv(rate):return Q(50)*(1-(1+rate)**-10)/rate+Q(1000)*(1+rate)**-10
 old=pv(Q(11,200));market=pv(Q(1,25));equity=Q(1700)-market
 v=cases['repurchase-exact']['valuation'];check('repurchase:annuity-old',Q(v['old_pv'])==old);check('repurchase:annuity-market',Q(v['current_pv'])==market)
 check('repurchase:source-displays',round(old)==962 and round(market)==1081)
 check('repurchase:exact-entry',lines('repurchase-exact','repurchase')=={'debt':old,'expense':market-old,'capital':equity,'cash':Q(-1700)})
 check('repurchase:source-rounded-entry',lines('repurchase-rounded','repurchase')=={'debt':Q(962),'expense':Q(119),'capital':Q(619),'cash':Q(-1700)})
 check('repurchase:full-loss-veto',1700-962!=119)
 face=Q(1000);old_shares=face/25;new_shares=face/20;loss=(new_shares-old_shares)*40
 check('inducement:source400',loss==400);check('inducement:immediate-entry',lines('immediate-inducement','amend-and-convert')=={'debt':Q(960),'expense':loss,'capital':-(960+loss)})
 check('inducement:50-shares',cases['immediate-inducement']['events'][0]['state']['shares_issued']==new_shares)
 check('inducement:later-price-veto',(new_shares-old_shares)*50!=loss);check('inducement:carrying-not-face',face!=960)
 check('inducement:joint-equity',final('immediate-inducement')['pretax_equity']==2000 and final('immediate-inducement')['cash']==2000)
 for c in cases.values():
  prior_effective=prior_ineffective=Q(0)
  for e in c['events']:
   state=e['state']
   if 'cumulative_D' not in state:continue
   d=Q(state['cumulative_D']);h=Q(state['cumulative_H']);effective=(1 if d>=0 else -1)*min(abs(d),abs(h));ineffective=d-effective
   check(c['id']+':'+e['id']+':offset-domain',d*h<=0)
   check(c['id']+':'+e['id']+':lower-of',Q(state['effective'])==effective and Q(state['ineffective'])==ineffective)
   p=lines(c['id'],e['id']);check(c['id']+':'+e['id']+':effective-change',-p.get('reserve',0)==effective-prior_effective)
   check(c['id']+':'+e['id']+':ineffective-change',-p.get('income',0)-p.get('expense',0)==ineffective-prior_ineffective)
   prior_effective=effective;prior_ineffective=ineffective
 check('hedge:cumulative-not-incremental',min(15,14)-min(12,10)==4 and min(15-12,14-10)==3)
 check('inventory:basis-journal',lines('cash-flow-inventory','basis-adjust')=={'reserve':Q(14),'inventory':Q(-14)})
 e=next(e for e in cases['cash-flow-inventory']['events'] if e['id']=='basis-adjust');check('inventory:basis-not-OCI',Q(e['oci'])==0 and Q(e['direct_basis_equity_change'])==-14)
 f=final('cash-flow-inventory');check('inventory:full-financials',(f['pretax_profit'],f['oci'],f['direct_basis_equity_change'],f['pretax_equity'],f['cash'],f['reserve'],f['inventory'],f['operating'])==(31,14,-14,231,231,0,0,31))
 s=next(e for e in cases['cash-flow-inventory']['events'] if e['id']=='settle-derivative');check('inventory:reserve-survives-settlement',Q(s['expected_report']['reserve'])==14)
 f=final('cash-flow-interest');check('interest:full-financials',(f['pretax_profit'],f['oci'],f['operating'],f['cash'],f['pretax_equity'],f['reserve'])==(-10,0,-10,190,190,0))
 check('discontinued:expected-keeps-reserve',final('cash-flow-discontinued-expected')['reserve']==10)
 check('discontinued:cancelled-releases',final('cash-flow-cancelled')['reserve']==0 and final('cash-flow-cancelled')['pretax_profit']==10)
 f=final('cash-flow-unrecoverable-loss');check('loss:partial-release',(f['reserve'],f['pretax_profit'],f['oci'])==(-6,-4,-6))
 f=final('fair-value-debt');check('fair-value:full-financials',(f['cash'],f['derivative_net'],f['debt'],f['pretax_profit'],f['oci'],f['operating'],f['financing'],f['pretax_equity'])==(79,8,0,-13,0,-21,-100,87))
 check('fair-value:EIR',Q(121)/110-1==Q(1,10));check('fair-value:old-EIR-veto',110*(1+Q(21,100))!=121)
 # Eligibility/measurement judgments cannot be inferred from favorable arithmetic.
 def eligible(facts):
  required=['instrument_eligible','external','item_eligible','reliable','inception_documented','economic_relationship','credit_not_dominant','ratio_admitted','highly_probable']
  if any(facts.get(k) is False for k in required):return 'ineligible'
  if any(facts.get(k) is None for k in required):return 'unresolved'
  return 'eligible'
 good={k:True for k in ['instrument_eligible','external','item_eligible','reliable','inception_documented','economic_relationship','credit_not_dominant','ratio_admitted','highly_probable']}
 check('eligibility:positive',eligible(good)=='eligible')
 for k in good:
  check('eligibility:false:'+k,eligible({**good,k:False})=='ineligible');check('eligibility:unknown:'+k,eligible({**good,k:None})=='unresolved')
 def derivative_classification(alternatives):
  if any(x=='non_equity' for x in alternatives):return 'financial_asset_or_liability'
  if not alternatives or any(x=='unknown' for x in alternatives):return 'unresolved'
  return 'equity'
 check('cash-alternative:equity-veto',derivative_classification(['equity','non_equity'])=='financial_asset_or_liability')
 check('cash-alternative:unknown',derivative_classification(['equity','unknown'])=='unresolved')
 check('cash-alternative:all-equity',derivative_classification(['equity','equity'])=='equity')
 def reform(facts):
  if facts.get('direct_reform') is False or facts.get('economic_equivalence') is False:return 'ordinary_modification_analysis'
  if facts.get('direct_reform') is None or facts.get('economic_equivalence') is None:return 'unresolved'
  return 'reform_expedient_then_additional_changes' if facts.get('additional_changes') else 'reform_expedient'
 check('reform:one-coupon-equality-only',Q(4,100)==Q(38,1000)+Q(2,1000))
 for label,facts,want in [('unknown',{'direct_reform':True,'economic_equivalence':None},'unresolved'),('unrelated',{'direct_reform':False,'economic_equivalence':True},'ordinary_modification_analysis'),('not-equivalent',{'direct_reform':True,'economic_equivalence':False},'ordinary_modification_analysis'),('qualified',{'direct_reform':True,'economic_equivalence':True},'reform_expedient'),('additional',{'direct_reform':True,'economic_equivalence':True,'additional_changes':True},'reform_expedient_then_additional_changes')]:check('reform:'+label,reform(facts)==want)
 def release_admission(current,event,processed):
  if event['id'] in processed:return 'replay_no_additional_entry'
  if Q(event['amount'])!=current:return 'reserve_amount_mismatch'
  return 'candidate_release'
 check('basis:valid-release',release_admission(Q(14),{'id':'basis','amount':'14'},set())=='candidate_release')
 check('basis:replay-preserves-zero',release_admission(Q(0),{'id':'basis','amount':'14'},{'basis'})=='replay_no_additional_entry')
 check('basis:new-id-still-overdraws',release_admission(Q(0),{'id':'basis-again','amount':'14'},{'basis'})=='reserve_amount_mismatch')
 check('protected295',sha(ROOT/'docs/design/proposal/manuscript-real-package-20261015/accounting-product-proposal.pdf')=='fc496a3d2bb1b6453e474afbfe8ca6742ced3ecbec460bf6672bbe85a665c2c8')
 check('index-preserved',subprocess.check_output(['git','diff','--cached','--raw','--no-abbrev'],cwd=ROOT)==(ROOT/'data/accounting-master/remaining-phases-audit-20261014/unrelated-index-before.txt').read_bytes())
 result={'passed':all(c['passed'] for c in checks),'check_count':len(checks),'checks':checks,'wall_seconds':time.monotonic()-start,'evidence_class':'deterministic documentary arithmetic and explicit semantic screens; no runtime or valuation calibration'}
 (OUT/'independent-checks.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'passed':result['passed'],'checks':len(checks),'failed':[c['name'] for c in checks if not c['passed']]}));raise SystemExit(not result['passed'])
if __name__=='__main__':main()
