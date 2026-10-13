"""Exact conditional consequences; no historical return/rank engine."""
from fractions import Fraction as F
import hashlib,json
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed evidence.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());v=json.loads((U/'source-views.json').read_text());checks={}
for p,h in b['dependencies'].items():checks['dependency:'+p]=sha(R/p)==h
checks['proxy_hash']=sha(R/v['proxy'])==v['proxy_sha256']
checks['filing_hash']=sha(R/v['filing'])==v['filing_sha256']
proxy={x['printed_page']:x['normalized_text'] for x in v['proxy_pages']}
for x in v['proxy_pages']:
    checks['fragment:'+str(x['printed_page'])]=sha(R/x['source_fragment'])==x['fragment_sha256']
    for im in x['images']:checks['image:'+im['path']]=sha(R/im['path'])==im['sha256']
filing={}
for x in v['filing_pages']:
    checks['text:'+str(x['pdf_page'])]=sha(R/x['text'])==x['text_sha256']
    checks['filing_image:'+str(x['pdf_page'])]=sha(R/x['image'])==x['image_sha256']
    filing[x['pdf_page']]=' '.join((R/x['text']).read_text().split())
anchors=[('notice',25,'Target No. of Units'),('blank_schedule',30,'[ ]'),
 ('linear',30,'linearly interpolated'),('negative_cap',30,'one hundred percent (100%)'),
 ('rounding',30,'nearest whole unit'),('tie_rule',30,'greater than such other'),
 ('bankruptcy',31,'Ending Price will be treated as $0'),('reinvestment',31,'reinvested in additional shares'),
 ('twenty_days',31,'twenty (20) consecutive trading days'),('committee',31,'final and binding'),
 ('continued_employment',26,'continued active employment'),('cash_DER',26,'paid in cash'),
 ('DER_percentage',26,'percentage of the total target number of RSUs'),
 ('vesting_date_after_death',27,'on the Vesting Date the Award shall vest'),
 ('fraction',27,'number of days remaining'),('amendment',29,'amendment must be in writing')]
for key,n,t in anchors:checks['anchor:'+key]=t in filing[n]
for token in ['October 1, 2023','October 1, 2026','85th Percentile or above 200%','55th Percentile 100%','25th Percentile 25%','Below 25th 0%','September 27, 2020','153%']:
    checks['proxy_schedule:'+token]=token in proxy[52]
checks['timing_distinction']='pro-rata accelerated vesting' in proxy[53] and 'on the Vesting Date the Award shall vest' in filing[27]
checks['prior_result_scope']='70.77' in proxy[53] and '54.09%' in proxy[53]
def m(p):
    p=F(p)
    if p<0 or p>100:raise ValueError('percentile outside declared scale')
    if p<25:return F(0)
    if p<55:return F(1,4)+(p-25)/40
    if p<85:return 1+(p-55)/30
    return F(2)
def g(p,r):return min(m(p),1) if F(r)<0 else m(p)
expected={'0':F(0),'24.9':F(0),'25':F(1,4),'40':F(5,8),'55':F(1),'70':F(3,2),'85':F(2),'100':F(2)}
for p,x in expected.items():checks['schedule:'+p]=m(p)==x
for p in [-1,101]:
    try:m(p);checks['reject_invalid:'+str(p)]=False
    except ValueError:checks['reject_invalid:'+str(p)]=True
checks['left_slope']=F(1-F(1,4),55-25)==F(1,40)
checks['right_slope']=F(2-1,85-55)==F(1,30)
checks['cap_negative']=1000*g(70,F(-18,100))==1000
checks['zero_return_not_negative']=1000*g(70,0)==1500
checks['positive_return']=1000*g(70,F(1,10))==1500
checks['cap_does_not_raise_low_payout']=1000*g(40,-1)==625
begin=sum([F(100)]*20)/20;end=sum([F(80)]*19+[F(120)])/20
true_return=(end-begin)/begin;endpoint_return=F(120-100,100)
checks['averaged_prices']=begin==100 and end==82
checks['negative_average_return']=true_return==F(-18,100)
checks['endpoint_wrong_sign']=endpoint_return==F(1,5) and true_return<0
checks['wrong_endpoint_changes_award']=1000*g(70,endpoint_return)-1000*g(70,true_return)==500
checks['discrete_uncertainty']={1000*m(F('24.9')),1000*m(25)}=={0,250}
checks['hull_creates_impossible_amount']=125 not in {1000*m(F('24.9')),1000*m(25)}
fraction=F(3,5);target=1000;dividend=F(1,4);credit=target*dividend
checks['surviving_uncapped']=target*g(70,0)*fraction==900
checks['surviving_capped']=target*g(70,-1)*fraction==600
checks['DER_credit']=credit==250
checks['DER_full']=credit*g(70,0)==375
checks['DER_partial']=credit*g(70,0)*fraction==225
checks['DER_partial_capped']=credit*g(70,-1)*fraction==150
save('method-consequences.json',{'schedule_scope':'Disclosed October2023 named-executive schedule; percentile is supplied, not estimated',
 'schedule_examples':{p:str(x) for p,x in expected.items()},'hypothetical':{'target_units':1000,'percentile':70,'beginning_average':'100','ending_average':'82','return':str(true_return),'wrong_endpoint_return':str(endpoint_return),'eligible_fraction':str(fraction),'one_preseverance_dividend':str(dividend),'full_uncapped_units':1500,'full_capped_units':1000,'partial_uncapped_units':900,'partial_capped_units':600,'DER_credit':250,'DER_full_uncapped':375,'DER_partial_uncapped':225,'DER_partial_capped':150},
 'unresolved':['actual grant applicability/amendments','rank conversion convention','general dividend/corporate-action computation','exact half-unit rounding','source-specific termination timing','actual October2026 outcome','tax/accounting/EPS'],
 'limits':'No historical market computation, probabilistic weighting, actual payouts, accounting valuation or runtime implementation.'})
save('source-review.json',{'review':'All seven form pages25–31 and five derived proxy views for printed pages51–53 visually inspected; selected operative clauses read against extracted text.',
 'source_views_sha256':sha(U/'source-views.json'),'anchors':[{'id':k,'pdf_page':n,'token':t} for k,n,t in anchors],
 'finding':'2022 form section8 vesting date and2025 proxy accelerated wording have unresolved actual-award applicability; preserve both.',
 'readiness':'not_ready; source-specific preparation, no legal/accounting determination'})
failed=[k for k,x in checks.items() if not x];save('source-arithmetic-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed})
print(json.dumps({'passed':sum(checks.values()),'failed':failed}))
raise SystemExit(bool(failed))
