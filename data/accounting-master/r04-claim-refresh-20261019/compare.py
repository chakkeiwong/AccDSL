"""Coverage and binding checks only; no scientific truth certification."""
import hashlib
import json
from pathlib import Path
import sys
UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
BASE=ROOT/'data/accounting-master'
SECTIONS=ROOT/'docs/design/proposal/manuscript-early-conversion-20261018/sections'

def bind(p):return {'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def write(name,data):
 with (UNIT/name).open('x') as f:json.dump(data,f,indent=2);f.write(chr(10))
def read(name):return json.loads((UNIT/name).read_text())
def unit_result(unit):
 return BASE/unit/('source-reading.md' if unit=='zero-weight-cgu-publisher-followup-20261018' else 'result.md')

def expected():
 return {
  'scope':'Documentary claim correspondence through exact 3.44; not a fresh primary-source or comprehensive literature audit',
  'version':'3.44','readiness':'not_ready',
  'transitions':[
   {'version':'3.37','kind':'validation/dependency integration','family':None},
   {'version':'3.38','kind':'substantive numerical target','family':'rate'},
   {'version':'3.39','kind':'substantive basic-EPS target','family':'participating_tax'},
   {'version':'3.40','kind':'substantive signed-collar target','family':'collar'},
   {'version':'3.41','kind':'substantive named-origin target','family':'cessation'},
   {'version':'3.42','kind':'readability repair; no new numerical target','family':None},
   {'version':'3.43','kind':'navigation repair; no new numerical target','family':None},
   {'version':'3.44','kind':'bounded source/policy clarification; arithmetic preserved','family':'early_conversion'}],
  'families':[
   {'id':'rate','version':'3.38','section':'rate-interval-propagation.tex',
    'claim':'One certified original-rate bracket propagates through the admitted dated performing/POCI recurrences.',
    'source_basis':['retained historical IFRS9 target','local monotonicity/interval induction','supplied schedule and ACT/365F'],
    'evidence':['rate-interval-propagation-20261017/source-reading.md','rate-interval-propagation-20261017/result.md'],
    'alternative':'Independent remaining-cash PV and compounded-origin expressions; exact quadratic oracle for selected case.',
    'limits':['nonnegative initial receipts and positive time exponents','all quantities share one unknown rate','marginal bounds are not jointly attainable endpoint journals','no mixed-sign root-selection or forecast-calibration claim'],
    'stronger_inference_admitted':False},
   {'id':'participating_tax','version':'3.39','section':'participating-tax-allocation.tex',
    'claim':'Under fixed rights and ordinary-only benefit, hypothetical participating distributions alter the basic ordinary numerator.',
    'source_basis':['retained June2017 IFRSIC decision/example','local payout-cancellation algebra','supplied tax/rights/recognition findings'],
    'evidence':['participating-tax-allocation-20261017/semantic-contract.md','participating-tax-allocation-20261017/result.md'],
    'alternative':'Actual-distribution and residual-allocation steps reconcile to rights-based closed form under stated assumptions.',
    'limits':['basic EPS only','negative residual is not a tax-loss recognition rule','full actual benefit distributed under admitted pattern','no cap/seniority/changing-rights or general dependent dilution'],
    'stronger_inference_admitted':False},
   {'id':'collar','version':'3.40','section':'zero-cost-collar.tex',
    'claim':'Aligned purchased-call/written-put history preserves signed intrinsic and cost reserves and gross cash origins.',
    'source_basis':['retained historical IFRS9.B6.5.31-32 and qualification clauses','local terminal payoff identities','supplied aligned marks and no-carry/zero-discount profile'],
    'evidence':['zero-cost-collar-20261017/semantic-contract.md','zero-cost-collar-20261017/result.md'],
    'alternative':'Independent terminal payoff clamp; separate per-date finite mark witnesses.',
    'limits':['per-date witnesses are not a joint dynamic probability law','equal premiums do not prove eligibility','no valuation/calibration algorithm','unmatched component and stopped-origin allocation unresolved'],
    'stronger_inference_admitted':False},
   {'id':'cessation','version':'3.41','section':'origin-matched-cessation.tex',
    'claim':'One stopped portion of a pre-existing exact origin match can preserve frozen reserve, continuing reserve and profit histories.',
    'source_basis':['retained historical IFRS9 lower-of/cessation/basis rules','local D=Rc+F+P and cash/inventory identities','supplied exact linear match and continuing qualification'],
    'evidence':['origin-matched-cessation-20261017/source-reading.md','origin-matched-cessation-20261017/result.md','origin-matched-cessation-20261017/contract-addendum.md'],
    'alternative':'Direct named-origin split versus the rejected aggregate nominal fraction shortcut.',
    'limits':['one stop; exact match; same weak sign; no historical ineffectiveness','no general uniqueness theorem','no acquired-cost/new-designation/multiple-stop general allocation','later hedge discriminator does not invalidate this narrower match'],
    'stronger_inference_admitted':False},
   {'id':'early_conversion','version':'3.44','section':'eps-lifecycle.tex',
    'claim':'A selected practice interpretation transfers conversion-date carrying amount for unchanged original holder exercise of an equity-classified option.',
    'source_basis':['BDO June2026 section4.5 secondary technical interpretation','retained IAS32.AG32 explicit maturity wording','IFRIC19 exclusion and IAS8 hierarchy as bounded context','supplied original terms/classification/tax'],
    'evidence':['early-conversion-source-20261018/source-reading.md','early-conversion-integration-20261018/result.md'],
    'alternative':'General extinguishment analysis if the unchanged original-equity-right conditions do not hold.',
    'limits':['BDO is not express AG32 early-exercise wording','IFRIC19 exclusion does not supply measurement','actual company/authority/tax admission separate','company exchange remains maturity-only'],
    'stronger_inference_admitted':False}],
  'supplemental_units':[
   {'unit':'r03-eps-order-discriminator-20261018','role':'local exact inequivalence; no general selector'},
   {'unit':'r03-marginal-eps-stability-20261019','role':'local exact final-deletion instability; no replacement selector'},
   {'unit':'r03-hedge-attribution-discriminator-20261018','role':'local lower-of shortcut rejection and weak-cap nonuniqueness; no IFRS alternatives admitted'},
   {'unit':'r03-insurance-termination-basis-20261018','role':'failed supporting-source route; combined91/B135 still unresolved'},
   {'unit':'zero-weight-cgu-publisher-followup-20261018','role':'retrieved source does not address all-zero eligible weights'},
   {'unit':'r05-vintage-admission-20261018','role':'192 byte-vintage admissions remain false; metadata roles separate'},
   {'unit':'r05-dependent-loss-source-20261018','role':'bounded source/code reading; scalar tests not E3 panel inference'},
   {'unit':'r05-target-overlap-20261018','role':'unselected target sheets and synthetic overlap; no estimand/procedure admission'},
   {'unit':'r06-normative-schema-20261018','role':'exact instance-copy correspondence under three declared adjustments'},
   {'unit':'r06-unitless-semantics-20261019','role':'seven source-defined interpretations; no PSVI/frozen-Value promotion'},
   {'unit':'r06-companion-schemas-20261019','role':'three structural/presentation correspondences; raw/text differences preserved'}],
  'open_conditions':['four historical blocked originals: McCarthy, Imielinski/Lipski, Tamer, Caiani',
                     'broad backward/forward and consequential competitor coverage',
                     'current correction/retraction inquiry across the full source collection',
                     'independent technical/domain and human acceptance',
                     'source-specific general EPS/hedge/CGU/insurance interpretation gaps',
                     'target-specific empirical and installed-runtime evidence'],
  'comprehensive_survey':False,'independent_acceptance':False,'manuscript_changed':False,'whole_rows_closed':0}

def check():
 d=read('claim-supplement.json');assert d==expected();checks=1
 assert [r['version'] for r in d['transitions']]==['3.'+str(i) for i in range(37,45)];checks+=1
 ids={r['id'] for r in d['families']};assert len(ids)==5
 assert {r['family'] for r in d['transitions'] if r['family']}==ids;checks+=1
 for r in d['families']:
  assert (SECTIONS/r['section']).is_file() and len(r['source_basis'])>=3 and len(r['limits'])==4
  assert not r['stronger_inference_admitted'];checks+=2
  for name in r['evidence']:assert (BASE/name).is_file();checks+=1
 for r in d['supplemental_units']:assert unit_result(r['unit']).is_file();checks+=1
 assert len(d['supplemental_units'])==11;checks+=1
 ledger=read('source-ledger.json')
 for b in ledger['bindings']:assert bind(ROOT/b['path'])==b;checks+=1
 assert ledger['new_acquisitions']==0;checks+=1
 for forbidden in ('comprehensive_survey','independent_acceptance','manuscript_changed'):
  assert d[forbidden] is False;checks+=1
 return {'status':'bounded claim refresh checked','transitions':8,'substantive_families':5,
         'supplemental_units':11,'bindings':len(ledger['bindings']),'structural_assertions':checks,
         'new_acquisitions':0,'whole_rows_closed':0,'literature_complete':False}

if __name__=='__main__':
 if sys.argv[1:]==['--build']:
  d=expected()
  if (UNIT/'claim-supplement.json').exists():assert read('claim-supplement.json')==d
  else:write('claim-supplement.json',d)
  files={SECTIONS/r['section'] for r in d['families']}
  files.add(SECTIONS/'company-eps-records.tex')
  files.update(BASE/n for r in d['families'] for n in r['evidence'])
  files.update(unit_result(r['unit']) for r in d['supplemental_units'])
  files.update(BASE/n for n in ['source-protocol-reuse-refresh-20261016/claim-successor.md',
                              'consequential-literature-20261015/result.md','protocol-delta-refresh-20261018/change-inventory.md',
                              'protocol-delta-refresh-20261018/result.md'])
  write('source-ledger.json',{'new_acquisitions':0,'bindings':[bind(p) for p in sorted(files)],
         'reading_scope':'Current method sections and selected source/contract/result records; supplemental units mostly inherited result-level evidence, not a fresh primary full-text audit.',
         'original_ledgers_changed':False,'code_or_experiment_rerun':False})
  print(json.dumps({'families':5,'transitions':8,'supplemental_units':11,'bindings':len(files)}))
 else:print(json.dumps(check()))
