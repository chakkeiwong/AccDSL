"""Check exact dated clauses and conditional rights; no grant inference."""
import hashlib,json,re
from fractions import Fraction as F
from pathlib import Path
U=Path(__file__).resolve().parent;R=U.parents[2]
if (U/'completion.json').exists():raise SystemExit('Completed evidence.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(U/n).write_text(json.dumps(x,indent=2)+'\n')
b=json.loads((U/'baseline.json').read_text());targets=json.loads((U/'targets.json').read_text())
records=json.loads((U/'clauses.json').read_text());v=json.loads((U/'source-views.json').read_text());checks={}
for p,h in b['dependencies'].items():checks['dependency:'+p]=sha(R/p)==h
for x in targets:
    s=x['target_span'];t=(R/s['extraction_path']).read_text()[s['start']:s['end']]
    checks[x['id']+':original']=sha(R/s['original_path'])==s['original_sha256']
    checks[x['id']+':extraction']=sha(R/s['extraction_path'])==s['extraction_sha256']
    checks[x['id']+':span']=hashlib.sha256(t.encode()).hexdigest()==s['span_sha256']
    checks[x['id']+':retained']=t==(U/'sources'/f'{x["number"]}-span.txt').read_text()
    checks[x['id']+':located_not_new']=x['document_status']=='retained_target_located'
    row=next(q for q in records if q['id']==x['id']);norm=' '.join(t.split())
    checks[x['id']+':normalized']=hashlib.sha256(norm.encode()).hexdigest()==row['normalized_span_sha256']
    for k,z in row['clauses'].items():checks[x['id']+':anchor:'+k]=norm[z['start']:z['end']]==z['text']
    checks[x['id']+':blank_schedule']='[ ]' in row['clauses']['A']['text']
    checks[x['id']+':cap']='one hundred percent (100%)' in row['clauses']['A']['text']
    checks[x['id']+':committee']='final and binding' in row['clauses']['A']['text']
general=next(x for x in records if x['id'].endswith('10.20'))
checks['general_fraction']='Severance Fraction' in general['clauses']['8']['text']
checks['general_vesting_date']='on the Vesting Date the Award shall vest' in general['clauses']['8']['text']
for x in records:
    checks[x['id']+':delivery_after_date']='following the Vesting Date' in x['clauses']['7']['text']
    checks[x['id']+':delivery_limit']='two and one-half' in x['clauses']['7']['text']
    checks[x['id']+':cash_rights']='paid in cash' in x['clauses']['5']['text']
    if x is not general:
        t=x['clauses']['8']['text']
        for token in ['first anniversary','sixty (60)','ten (10)','continue to be eligible to vest','except as otherwise provided by the Committee']:
            checks[x['id']+':ceo:'+token]=token in t
        checks[x['id']+':no_severance_fraction']='Severance Fraction' not in t
checks['annual_hash']=sha(R/v['annual'])==v['annual_sha256']
for x in v['pages']:checks['image:'+str(x['pdf_page'])]=sha(R/x['path'])==x['sha256']
ceo=v['ceo2022'];checks['html_hash']=sha(R/ceo['original'])==ceo['sha256']
checks['fragment_hash']=sha(R/ceo['fragment'])==ceo['fragment_sha256']
for x in ceo['images']:checks['derived:'+x['path']]=sha(R/x['path'])==x['sha256']
q=1000;mult=F(3,2);fraction=F(3,5);credit=250
checks['general_units']=q*mult*fraction==900
checks['CEO_units']=q*mult==1500
checks['general_capped']=q*fraction==600
checks['CEO_capped']=q==1000
checks['conditional_unit_difference']=q*mult*(1-fraction)==600
checks['general_cash']=credit*mult*fraction==225
checks['CEO_cash']=credit*mult==375
checks['conditional_cash_difference']=credit*mult*(1-fraction)==150
# Logical eligibility illustration only; actual Committee decisions remain inputs.
def ordinary_retirement_conditions(age,years,anniversary):
    if None in (age,years,anniversary):return None
    return age>=60 and years>=10 and anniversary
for label,args,expected in [('all_met',(60,10,True),True),('before_anniversary',(60,10,False),False),
 ('age_short',(59,10,True),False),('service_short',(60,9,True),False),('unknown_service',(60,None,True),None)]:
    checks['retirement_boundary:'+label]=ordinary_retirement_conditions(*args) is expected
save('version-consequences.json',{'scope':'Hypothetical same target/performance; no actual grants, severance, amendment or Committee decision inferred.',
 'general':{'target':1000,'multiplier':'3/2','fraction':'3/5','units':900,'capped_units':600,'cash_credit':250,'gross_cash':225},
 'CEO':{'target':1000,'multiplier':'3/2','units':1500,'capped_units':1000,'cash_credit':250,'gross_cash':375},
 'timing':'Both inspected general/CEO forms anchor delivery after Vesting Date; proxy accelerated wording is not resolved for an actual grant.',
 'unchanged_unknowns':['applicable executed grant/amendments','actual grant fields and service facts','rank conversion','general TSR adjustments','tax/accounting/EPS'],
 'source_disposition':'Three already located targets receive selected substantive inspection, not three new acquisitions;40/3/37 document counts unchanged.'})
save('source-review.json',{'read':'Twelve annual PDF images and one derived CEO2022 view inspected; selected clauses3–5,7–8 and ExhibitA read; entire versions retained, not exhaustive legal review.',
 'manifest_sha256':sha(U/'source-views.json'),'version_dates':'Annual exhibit-list descriptions, not actual executed grant dates.',
 'boundary_correction':'Exact spans exclude next exhibits; selected2024 forms end at PDF90/107 although frozen locator includes following boundary page91/108.',
 'classification':'Timing/applicability unresolved; no established same-award contradiction.'})
failed=[k for k,x in checks.items() if not x];save('source-arithmetic-checks.json',{'checks':checks,'passed':sum(checks.values()),'failed':failed});print(json.dumps({'passed':sum(checks.values()),'failed':failed}));raise SystemExit(bool(failed))
