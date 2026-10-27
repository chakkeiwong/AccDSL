"""Saved-source validation and independent displayed arithmetic, once per attempt."""
from pathlib import Path
from hashlib import sha256
from fractions import Fraction as Q
from copy import deepcopy
from datetime import datetime,timezone
import json,zipfile,xml.etree.ElementTree as E,sys,time,platform
import source_reading_v2 as reading
H=Path(__file__).resolve().parent;R=H.parents[2];B=H.parent
def read(p):return json.loads(p.read_text())
def sha(p):return sha256(p.read_bytes()).hexdigest()
def enc(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False)
def dump(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def main():
 started=time.monotonic();out=H/'attempt-01';out.mkdir(exist_ok=False);checks=[]
 def check(ok,name):checks.append(dict(name=name,passed=bool(ok)));assert ok,name
 inherited=read(H/'source-inspection-01/source-lock.json');lock=dict(inherited)
 for n,h in inherited.items():check(sha(R/n)==h,'original_identity:'+n)
 for p in [H/'source-inspection-01/facts.json',H/'source-inspection-01/links.json',H/'selected-binding.json',H/'source_reading_v2.py',Path(__file__),H/'repair-note.md']:
  lock[str(p.relative_to(R))]=sha(p)
 facts=read(H/'source-inspection-01/facts.json');binding=read(H/'selected-binding.json');before=enc(facts)
 archive=R/'docs/design/cases/apple/continuation-20261007/sources/annual-2024-taxonomy-trusted-v1.zip'
 with zipfile.ZipFile(archive) as z:raw=z.read('aapl-20240928_htm.xml')
 check(sha256(raw).hexdigest()==binding['instance_sha256'],'instance_identity')
 root=E.fromstring(raw);by_id={n.attrib['id']:n for n in root if 'id' in n.attrib}
 for f in facts:
  check(E.tostring(by_id[f['id']],encoding='unicode')==f['raw_xml'],'original_fact_bytes:'+f['id'])
  check(by_id[f['id']].text==f['value'] and by_id[f['id']].tag==f['concept'],'original_fact_value:'+f['id'])
  check(f['decimals']==by_id[f['id']].attrib.get('decimals'),'original_accuracy:'+f['id'])
 selected=reading.select(facts,binding)
 check(selected['status']=='reported_value_alternative' and selected['displayed_value_usd_million']=='0/1','selected_reported_zero')
 check(not selected['exact_economic_zero'] and selected['original_literal']=='—' and selected['source_admission'] is False,'reading_boundaries')
 check(enc(facts)==before,'selection_nonmutation')
 controls=[]
 def refusal(name,change):
  fs=deepcopy(facts);bs=deepcopy(binding);change(fs,bs)
  try:reading.select(fs,bs)
  except (reading.Refusal,KeyError,TypeError,ValueError) as exc:controls.append(dict(name=name,refused=True,reason=str(exc)));return
  raise AssertionError('accepted_mutation:'+name)
 def f(fs):return next(x for x in fs if x['id']=='f-325')
 for field,value in [('concept','{http://fasb.org/us-gaap/2024}RepaymentsOfLongTermDebt'),('unit','EUR'),('nil',True),('decimals','INF'),('value','1'),('pdf_label','Other'),('presentation_role','wrong'),('calculation_weight','-1.0'),('raw_xml','altered'),('archive_sha256','0'*64),('instance_sha256','0'*64),('pdf_sha256','0'*64)]:
  refusal('changed_'+field,lambda fs,bs,k=field,v=value:f(fs).__setitem__(k,v))
 refusal('wrong_period',lambda fs,bs:f(fs)['context'].__setitem__('period',{'startDate':'2022-09-25','endDate':'2023-09-30'}))
 refusal('wrong_issuer',lambda fs,bs:f(fs)['context']['entity'].__setitem__('identifier','wrong'))
 refusal('added_dimension',lambda fs,bs:f(fs)['context'].__setitem__('dimensions',['segment']))
 refusal('added_context_child',lambda fs,bs:f(fs)['context'].__setitem__('other_children',['scenario']))
 refusal('missing_occurrence',lambda fs,bs:fs.remove(f(fs)))
 refusal('duplicate_occurrence',lambda fs,bs:fs.append(deepcopy(f(fs))))
 refusal('stale_selection',lambda fs,bs:bs.__setitem__('occurrence_ids',['f-326']))
 refusal('stale_record_identity',lambda fs,bs:bs['complete_record_sha256'].__setitem__('f-325','0'*64))
 check(len(controls)==20,'twenty_controls')
 all_values={}
 for context in ['c-1','c-19','c-20']:
  chosen=[x for x in facts if x['context_ref']==context and not x['nil']];values={}
  for x in chosen:
   name=x['concept'].rsplit('}',1)[-1];values.setdefault(name,set()).add(Q(x['value'])/1000000)
  check(all(len(v)==1 for v in values.values()),'duplicate_occurrences_agree:'+context)
  values={k:next(iter(v)) for k,v in values.items()};all_values[context]=values
 names=['PaymentsRelatedToTaxWithholdingForShareBasedCompensation','PaymentsOfDividends','PaymentsForRepurchaseOfCommonStock','ProceedsFromIssuanceOfLongTermDebt','RepaymentsOfLongTermDebt','ProceedsFromRepaymentsOfCommercialPaper','ProceedsFromPaymentsForOtherFinancingActivities']
 signs=[-1,-1,-1,1,-1,1,1];gold=[-121983,-108488,-110749];cash_rows=[]
 for context,total in zip(['c-1','c-19','c-20'],gold):
  vals=all_values[context];terms=[v*vals[n] for n,v in zip(names,signs)]
  check(sum(terms)==total==vals['NetCashProvidedByUsedInFinancingActivities'],'complete_financing_sum:'+context)
  cash_rows.append(dict(context=context,signed_terms=[str(x) for x in terms],sum_usd_million=str(sum(terms)),reported_total_usd_million=str(total)))
 check([all_values[c]['ProceedsFromIssuanceOfLongTermDebt'] for c in ['c-1','c-19','c-20']]==[Q(0),Q(5228),Q(5465)],'three_year_issuance_match')
 report=read(B/'statement-context-coverage-20261024/statements.json')['CompanyOperationsDraft/1:combined']
 def amount(alias):
  b=report['observations'][alias]['observation']['record']['body'];v=b['value'];check(v['tag']=='known_displayed','displayed_operand:'+alias);return Q(int(v['amount']['n']),int(v['amount']['d']))
 aliases=['award_tax','dividends','repurchases','debt_issuance','debt_repayments','commercial_paper','financing_other']
 for name,sign,alias in zip(names,signs,aliases):
  if alias=='debt_issuance':continue
  check(amount('annual.cash_flow.'+alias)==sign*all_values['c-1'][name],'original_signed_cashflow:'+alias)
 closing=amount('annual.balance.debt_current')+amount('annual.balance.debt_noncurrent')
 opening=amount('annual.opening.debt_current')+amount('annual.opening.debt_noncurrent')
 repayment=amount('annual.cash_flow.debt_repayments');residual=closing-opening-Q(selected['displayed_value_usd_million'])-repayment
 check((closing,opening,repayment,residual)==(Q(96662),Q(105103),Q(-9958),Q(1517)),'independent_debt_movement')
 for rid in ['annual.financing_cash','annual.diagnostic:term_debt']:
  original=next(r for r in report['relations'] if r['id']==rid);check(original['arithmetic']['status']=='unresolved','old_relation_unchanged:'+rid)
 check(report['observations']['annual.cash_flow.debt_issuance']['observation']['record']['body']['value']['tag']=='reported_dash','original_dash_not_coerced')
 for n,h in lock.items():check(sha(R/n)==h,'protected_after:'+n)
 dump(out/'reading.json',selected);dump(out/'controls.json',controls);dump(out/'source-lock.json',lock)
 dump(out/'consequences.json',dict(financing_comparatives=cash_rows,current_financing=dict(original_status='unresolved',supplementary_status='displayed_difference',lhs='-121983/1',rhs='-121983/1',residual='0/1'),term_debt=dict(original_status='unresolved',supplementary_status='explanatory_difference',opening='105103/1',closing='96662/1',issuance='0/1',repayment='-9958/1',residual='1517/1',role='explanatory only; no inferred journal or attribution'),source_network_updated=False,exact_latent_interval=None))
 dump(out/'verification.json',dict(passed=True,checks=checks,facts=len(facts),controls=len(controls),protected_files=len(lock)))
 dump(out/'run-manifest.json',dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),git_commit='unavailable',command='CUDA_VISIBLE_DEVICES=-1 python3 -B data/accounting-master/debt-dash-source-20261027/verify.py',python=sys.version,executable=sys.executable,platform=platform.platform(),cpu_gpu='CPU only; GPU intentionally hidden; no numerical framework imported',random_seeds='N/A exact source matching and rational arithmetic',wall_seconds=time.monotonic()-started,data_version=sha(out/'source-lock.json'),plan='docs/plans/accounting-debt-dash-source-20261027.md',result='data/accounting-master/debt-dash-source-20261027/result.md',artifacts=['reading.json','controls.json','consequences.json','verification.json']))
 print(json.dumps(dict(passed=True,facts=len(facts),controls=len(controls),checks=len(checks),financing='-121983',debt_residual='1517')))
if __name__=='__main__':main()
