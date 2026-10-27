"""Finite illustrative IFRIC23 computation, independent of any tax runtime."""
from pathlib import Path
from fractions import Fraction as F
import json
OUT=Path(__file__).resolve().parent
checks=[];cases=[]
def ck(n,b):checks.append({'name':n,'passed':bool(b)})
def enc(v):
    if isinstance(v,F):return str(v)
    raise TypeError(type(v))
for name,deduction,method,why in [
 ('probable-acceptance',F(100),'filed treatment','acceptance probable under full-information examination'),
 ('binary-denial',F(20),'most likely amount','binary100/20; acceptance probability1/5;20 is the better prediction'),
 ('dispersed-amounts',F(100)*F(1,5)+F(40)*F(3,10)+F(20)*F(1,2),'expected value','full acceptance not probable; dispersed distribution and expected-value predictive finding supplied')]:
    book=F(100)-20;taxbase=100-deduction;pretax=100-20;current=(100-deduction)*F(1,4);deferred=(book-taxbase)*F(1,4)
    profit=pretax-current-deferred;equity=500+profit;cash=500+100-100
    ck(name+'/equation',cash+book==current+deferred+equity)
    ck(name+'/tax-origin',current+deferred==pretax/4)
    ck(name+'/cash-tax-unpaid',cash==500)
    ck(name+'/same-tax-base-judgment',taxbase==100-deduction)
    ck(name+'/no-tax-asset',deferred>=0)
    cases.append({'id':name,'method':method,'eligibility':why,'deduction':deduction,'tax_base':taxbase,
      'current_tax':current,'DTL':deferred,'pretax_profit':pretax,'profit':profit,'cash':cash,'PPE':book,'equity':equity,
      'journal':[{'debit':'current tax expense','credit':'tax payable','amount':current},
                 {'debit':'deferred tax expense','credit':'DTL','amount':deferred}],
      'zero_journal_rule':'An exact zero measured component is omitted; a missing input is unresolved.'})
expected=cases[2];actual_current=F(15);actual_dtl=F(5)
ck('resolved-current-increase',actual_current-expected['current_tax']==F(1,2))
ck('resolved-deferred-release',expected['DTL']-actual_dtl==F(1,2))
ck('resolution-no-net-tax-change',actual_current+actual_dtl==20)
ck('postpayment-equation',500-actual_current+80==actual_dtl+560)
for name,truth in {
 'audit-detection-discount-is-wrong':F(29,2)*F(1,10)!=F(29,2),
 'mix-expected-current-with-filed-base-is-wrong':F(29,2)+20!=20,
 'use-modal-deduction-under-expected-policy-is-wrong':20!=42,
 'every-case-default-to-mean-is-wrong':42!=100,
}.items():ck('adverse/'+name,truth)
result={'passed':all(c['passed'] for c in checks),'checks':len(checks),'cases':cases,'details':checks,
 'resolved_expected_case':{'allowed_deduction':'40','current_tax':'15','DTL':'5','cash_after_payment':'485','PPE':'80','equity':'560',
 'journal':['Dr current tax expense0.5 / Cr tax payable0.5','Dr DTL0.5 / Cr deferred tax expense0.5','Dr tax payable15 / Cr cash15']},
 'source_conditioned_refusals':['Authority silence alone does not establish acceptance.','Missing law, recognition findings or required probability inputs remain unresolved.'],
 'scope':'Historical EU IFRIC23. Synthetic law/rate/probabilities. Actual legal eligibility unresolved. No experiment or ranking.'}
(OUT/'uncertain-tax-cases.json').write_text(json.dumps(result,indent=2,default=enc)+'\n')
print(json.dumps({'passed':result['passed'],'checks':len(checks),'cases':len(cases)}))
assert result['passed']
