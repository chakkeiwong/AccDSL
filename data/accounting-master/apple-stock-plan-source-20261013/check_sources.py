"""Recover three exact exhibit counterparts and check selected consequences."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import fitz

UNIT=Path(__file__).resolve().parent
ROOT=UNIT.parents[2]
if (UNIT/'completion.json').exists():
    raise SystemExit('Completed unit; preserve evidence.')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,x):(UNIT/n).write_text(json.dumps(x,indent=2,ensure_ascii=False)+'\n')
def norm(t):return ' '.join(t.split())
b=json.loads((UNIT/'baseline.json').read_text());checks={}
for p,h in b['dependencies'].items():checks['dependency:'+p]=sha(ROOT/p)==h
pdf=UNIT/'sources/filing-20220304.pdf';doc=fitz.open(pdf)
checks['31_filing_pages']=len(doc)==31
checks['source_hash']=sha(pdf)=='f1631780b18a86e2021506beae4b4e052665be790514a0b427be3381cc1ad92c'
texts={i+1:norm(p.get_text()) for i,p in enumerate(doc)}
checks['issuer_date']=all(x in texts[1] for x in ['Apple Inc.','March 4, 2022','001-36743'])
checks['signed_date']=all(x in texts[4] for x in ['March 4, 2022','Katherine Adams'])
checks['adoption_effectiveness']=all(x in texts[2] for x in ['shareholders approved','became effective upon shareholder approval','Exhibit 10.1'])
checks['vote_and_exhibits']=all(x in texts[3] for x in ['9,377,995,041','286,025,295','37,973,660','10.1','10.2','10.3'])
checks['linked_exhibit_pages']=[x['page'] for x in doc[2].get_links()]==[4,19,24]
front=json.loads((ROOT/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json').read_text())
dispositions=[]
for rid,ex,first,last,meaning in [
    ('annual.exhibit.10.13','10.1',5,19,'Plan text retained; selected clauses read; current amendments and individual grants unestablished'),
    ('annual.exhibit.10.14','10.2',20,24,'Time-based RSU form retained; selected vesting, share delivery and withholding clauses read; grant notice fields blank'),
    ('annual.exhibit.10.15','10.3',25,31,'Performance form retained; identity, notice, Exhibit A and selected clauses inspected; comprehensive performance method deferred')]:
    r=next(x for x in front['reference_frontier'] if x['id']==rid)
    checks[rid+':reference']=r['referenced_exhibit']==ex and r['referenced_date_or_period']=='3/4/22' and r['document_status']=='unresolved_target'
    checks[rid+':counterpart']='Exhibit '+ex in texts[first] and '2022 EMPLOYEE STOCK PLAN' in texts[first]
    dispositions.append({'reference_id':rid,'frozen_document_status':r['document_status'],
        'supplemental_document_status':'retained_counterpart_identity_checked','filing_exhibit':ex,
        'pdf_pages':[first,last],'semantic_disposition':meaning,'source':str(pdf.relative_to(ROOT)),
        'source_sha256':sha(pdf),'identity_basis':'Issuer, report/signature/approval date, exhibit index destinations, titles and form descriptions match the retained annual reference; no regulator-byte identity or historical availability claimed.'})

# Selected complete paragraphs are retained for exact reinspection.
specs=[
 ('approval',5,'This 2022 Employee Stock Plan was approved','The purpose','Approval date 2022-03-04; distinct from Board date.'),
 ('share_cap',11,'SECTION 5.','7','Formula510m plus specified 2014 availability/recycling, capped at1274374682; not an unconditional unused balance.'),
 ('share_count',12,'(b) Share Count.','(c) Share Limits.','Full-value ratio2; option/SAR1; disjoint recycling and cash-settlement rules.'),
 ('RSU_terms',14,'SECTION 9.','10','Agreement-specific schedule and settlement; plan permits cash/shares/mix and deferred timing.'),
 ('tax_and_board_date',17,'SECTION 14.','13','Withholding methods/conditions and409A clause; Board adoption2021-11-09 is labelled Effective Date for term calculation.'),
 ('grant_notice',20,'Exhibit 10.2','You do not have','Participant, number and timing fields are blank; no actual grant supplied.'),
 ('time_form_payment',22,'7. Timing and Manner','8. Effect','Shares equal vested units less Tax-Related Items, promptly and within2.5months, subject to express preconditions.'),
 ('time_form_tax',23,'11. Responsibility','12. Electronic','Withholding alternatives and statutory maximum language; no actual rate or payment computed.'),
 ('performance_blanks',30,'PERFORMANCE AWARD','For TSR','Target schedule contains blank percentile/payout fields; do not fill from convenience.'),
]
anchors=[]
for ident,n,start,end,interpretation in specs:
    t=texts[n];a=t.index(start)
    if end in ['7','10','13']:z=len(t)
    else:z=t.index(end,a+len(start))
    excerpt=t[a:z];checks['anchor:'+ident]=bool(excerpt)
    anchors.append({'id':ident,'pdf_page':n,'normalized_start':a,'normalized_end':z,
                    'normalization':'collapse whitespace','excerpt':excerpt,'interpretation':interpretation})
views=json.loads((UNIT/'proxy-source-views.json').read_text())
checks['retained_proxy_hash']=sha(ROOT/views['source'])==views['sha256']
v={r['id']:r for r in views['records']}
checks['proxy_specific_dates']=all(x in v['vesting']['normalized_text'] for x in ['October 1, 2023','April 1, 2026','three equal annual installments'])
checks['retirement_payment_not_accelerated']='not accelerated upon retirement' in v['retirement']['normalized_text']
capacity=[125973077,37387521,10612]
available=[1022428528,66924428,4110122]
checks['outstanding_sum']=sum(capacity)==163371210
checks['2014_award_split']=39984+37347537==37387521
checks['RSU_subpopulation']=125973077+37347537+10612==163331226
checks['all_awards_minus_options']=163371210-39984==163331226
checks['capacity_sum']=sum(available)==1093463078
for n in capacity+available+[163371210,1093463078,39984,37347537]:checks['proxy_amount:'+str(n)]=f'{n:,}' in v['capacity']['normalized_text']
checks['2014_director_scope_not_2022']=sum(capacity)!=capacity[0]
checks['capacity_is_not_awards']=sum(available)!=sum(capacity)
illustration={'RSUs':100,'shares_withheld':20,'net_shares_delivered':80,
    'full_value_initial_reserve_debit':200,'recycling_credit':40,'net_reserve_usage':160,
    'option_counterexample_gross_exercised':100,'option_net_delivery_if20withheld':80,
    'option_reserve_usage':100,
    'scope':'Hypothetical full-value award initially charged at ratio2; no dividends, substitutions, forfeitures or other adjustments. Option comparison uses the stated gross-count/no-recycling rule. No tax rate or dollar cash inferred.'}
checks['hypothetical_delivery']=illustration['RSUs']-illustration['shares_withheld']==illustration['net_shares_delivered']
checks['full_value_net_capacity']=200-2*20==160==2*80
checks['option_nonrecycling_difference']=100!=160 and 100!=80
checks['same_net_delivery_different_capacity']=illustration['net_shares_delivered']==illustration['option_net_delivery_if20withheld'] and illustration['net_reserve_usage']!=illustration['option_reserve_usage']
for name in ['filing-source-renders.json','annual-source-pages.json']:
    manifest=json.loads((UNIT/name).read_text());checks[name+':source']=sha(ROOT/manifest['source'])==manifest['source_sha256']
    for r in manifest['pages']:checks[name+':image:'+str(r['pdf_page'])]=sha(ROOT/r['image'])==r.get('sha256',r.get('image_sha256'))
for r in views['records']:
    checks['fragment:'+r['id']]=sha(ROOT/r['fragment'])==r['fragment_sha256']
    for im in r['images']:checks['view:'+r['id']]=sha(ROOT/im['path'])==im['sha256']
checks['supplement3']=len(dispositions)==3
checks['original_unresolved40']=sum(r['document_status']=='unresolved_target' for r in front['reference_frontier'])==40
save('reference-supplement.json',{'date':'2026-10-13','original_frontier':{'path':'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json','sha256':sha(ROOT/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'),'unresolved':40},'dispositions':dispositions,'residual_from_original_unresolved':37,'count_scope':'Three original unresolved targets now have retained counterparts in this supplement;37 others have no such disposition here. Original bytes and semantic-completeness status unchanged.','publication_limit':'No current amendment-chain completeness, exact historical byte availability, or corpus filing-date amendment.'})
save('source-claim-supplement.json',{'source':str(pdf.relative_to(ROOT)),'sha256':sha(pdf),'source_url':'https://d18rn0p25nwr6d.cloudfront.net/CIK-0000320193/1e8cf761-1736-43bb-81b0-4e8fe94bd0c8.pdf','source_class':'Filing counterpart on retained issuer-associated distribution host, identity matched to references; not regulator-byte comparison','anchors':anchors,'proxy_views':'proxy-source-views.json','source_review':'Selected operative sections and neighboring definitions inspected; full texts retained. Twelve filing images, one annual image and four derived proxy views read. No independent legal/ASC/tax determination.','clocks':{'board_adoption_effective_date_label':'2021-11-09','shareholder_approval_and_reported_plan_effectiveness':'2022-03-04','grant_dates':'Individual; blank in forms','current_version':'Amendment chain not established'},'unresolved':['Actual individual grant notices and applicability to each award','Current plan amendments and decisions','Tax rates and share withholding values','Accounting classification/expense and diluted EPS treatment','Detailed performance target fields and later forms','Historical exact-byte availability']})
save('capacity-checks.json',{'units':'individual shares/RSU units, not thousands or dollars','outstanding_by_plan':dict(zip(['2022','2014','director'],capacity)),'outstanding_total':sum(capacity),'available_by_plan':dict(zip(['2022','employee_purchase','director'],available)),'available_total':sum(available),'illustration':illustration,'interpretation':'Capacity is an authorisation constraint; outstanding awards and issued common shares are different populations.'})
failed=[k for k,v in checks.items() if not v];save('source-arithmetic-checks.json',{'passed':sum(checks.values()),'failed':failed,'checks':checks})
print(json.dumps({'passed':sum(checks.values()),'failed':failed,'counterparts':len(dispositions),'remaining_original_targets':37,'outstanding':sum(capacity),'capacity':sum(available)}))
raise SystemExit(bool(failed))
