#!/usr/bin/env python3
"""Independent source/arithmetical checks of the authored case supplement."""
from datetime import date
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import time
from bs4 import BeautifulSoup

ROOT=Path(__file__).resolve().parents[3]
OPS=Path(__file__).resolve().parent
CASE=ROOT/'docs/design/cases/apple/continuation-20261007/case-supplement-v1.json'
start=time.monotonic()
c=json.loads(CASE.read_text())
checks=[]

def check(ok, label):
    checks.append({'check':label,'passed':bool(ok)})

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

# Recompute every original hash and every quote/span from the actual input.
seen=set()
def walk(x):
    if isinstance(x,dict):
        if all(k in x for k in ['extraction_path','extraction_sha256','original_path','original_sha256','start','end']):
            k=(x['extraction_path'],x['start'],x['end'])
            if k not in seen:
                seen.add(k)
                p=ROOT/x['extraction_path']; t=p.read_text(); span=t[x['start']:x['end']]
                check(sha(p)==x['extraction_sha256'] and sha(ROOT/x['original_path'])==x['original_sha256'],f'source hashes {k}')
                check(0<=x['start']<x['end']<=len(t),f'span bounds {k}')
                if 'quote' in x:check(span==x['quote'],f'exact quote {k}')
                if 'span_sha256' in x:check(hashlib.sha256(span.encode()).hexdigest()==x['span_sha256'],f'span hash {k}')
        for v in x.values():walk(v)
    elif isinstance(x,list):
        for v in x:walk(v)
walk(c)
old=json.loads((ROOT/c['baseline']['path']).read_text())
check(sha(ROOT/c['baseline']['path'])==c['baseline']['sha256'],'frozen P02 input')
check({r['id'] for r in c['reference_frontier']}=={r['id'] for r in old['external']['exhibit_inventory']},'all 70 baseline exhibit identities accounted for')
check(len(c['reference_frontier'])==len({r['id'] for r in c['reference_frontier']})==70,'no duplicate or missing exhibit rows')
check({n['note_id'] for n in c['note_dispositions']}=={n['id'] for n in old['notes']},'all 23 notes have explicit residuals')
check(len(c['package_obligations'])==7,'seven additional obligations preserved')
check(all(x['remaining_facts'] and x['proposed_consequence'] for x in c['material_assertions']),'each selected assertion has a consequence and unresolved facts')
check(len(c['effective_observation_overrides'])==2 and all(x['measurement']=='cash_and_cash_equivalents_as_reported' for x in c['effective_observation_overrides']),'cash correction supplied as usable observation overrides')

# Independently read the original quarterly inline facts, retaining raw context.
soup=BeautifulSoup((ROOT/'docs/design/cases/apple/interim-2025q1.html').read_text(),'lxml')
contexts={e['id']:e for e in soup.find_all('xbrli:context')}
def fact(name, instant=None, period=None):
    found=[]
    for f in soup.find_all('ix:nonfraction',attrs={'name':name}):
        ctx=contexts[f['contextref']]
        if ctx.find('xbrli:segment') or ctx.find('xbrli:scenario'):continue
        if instant:
            el=ctx.find('xbrli:instant')
            if not el or el.get_text()!=instant:continue
        if period:
            a=ctx.find('xbrli:startdate');b=ctx.find('xbrli:enddate')
            if not a or not b or (a.get_text(),b.get_text())!=period:continue
        literal=f.get_text('',strip=True).replace(',','')
        if literal in ['—','–','-']:v=Fraction(0)
        else:v=Fraction(literal)
        v*=10**int(f.get('scale','0'))
        if f.get('sign')=='-':v=-v
        found.append(v)
    assert found and len(set(found))==1,(name,found)
    return found[0]/1000000
quarter=('2024-09-29','2024-12-28')
current=fact('us-gaap:LongTermDebtCurrent',instant='2024-12-28')
noncurrent=fact('us-gaap:LongTermDebtNoncurrent',instant='2024-12-28')
repay=fact('us-gaap:RepaymentsOfLongTermDebt',period=quarter)
operating=fact('us-gaap:NetCashProvidedByUsedInOperatingActivities',period=quarter)
investing=fact('us-gaap:NetCashProvidedByUsedInInvestingActivities',period=quarter)
financing=fact('us-gaap:NetCashProvidedByUsedInFinancingActivities',period=quarter)
actual={'quarter_current_plus_noncurrent_musd':current+noncurrent,
        'quarter_carrying_change_musd':current+noncurrent-96662,
        'quarter_carrying_reconciliation_residual_after_cash_repayments_musd':current+noncurrent-96662+repay,
        'quarter_cash_change_musd':operating+investing+financing,
        'quarter_closing_cash_including_restricted_musd':29943+operating+investing+financing}
for name,v in actual.items():check(v==c['calculation_results'][name],name+' independent inline-source arithmetic')
check(repay==1009,'repayment is 1009 million in the original quarterly fact')
check(financing==c['calculation_results']['quarter_financing_cash_sum_musd'],'financing components equal reported total')
expected={'annual_principal_to_carrying_musd':96662,'annual_current_plus_noncurrent_musd':96662,
          'annual_principal_maturity_sum_musd':97341,'annual_fy2025_principal_minus_current_carrying_musd':18,
          'annual_cash_less_reported_restricted_component_musd':27343,'annual_ppe_musd':45680,
          'quarter_ppe_musd':46069,'quarter_inventory_musd':6911,'annual_lease_liabilities_musd':12430,
          'annual_segment_to_consolidated_income_musd':123216,'quarter_segment_to_consolidated_income_musd':42832,
          'quarter_rsu_thousands':186756}
for name,v in expected.items():check(c['calculation_results'][name]==v,name+' independently inspected table result')
a={i['id']:i for i in c['material_assertions']}
check('included $2.6 billion held in escrow' in a['A07']['source']['quote'],'source contradicts exclusion metadata')
check(c['query']['facts'][0]['fiscal_year']==2025 and c['query']['facts'][1]['fiscal_year']==2026,'different fiscal buckets')
check(date(2025,9,27).weekday()==5 and (date(2025,9,27)-date(2024,9,28)).days==364,'52-week fiscal 2025 end date')
check(date(2025,5,24).weekday()==date(2025,11,15).weekday()==5,'both scheduled maturities are Saturday')
check(Fraction(c['query']['facts'][0]['coupon_eur'])==10937500,'EUR coupon arithmetic')
check(Fraction(c['query']['facts'][0]['principal_plus_coupon_eur'])==1260937500,'EUR final gross payment arithmetic')
check(c['coverage']['recursive_reference_closure'] is False and c['acceptance']['whole_proposal']=='not_ready','no closure or readiness promotion')
check(len(c['taxonomy']['members'])==6 and len(c['taxonomy']['declared_imports'])==10,'archive has six members and ten declared external schema imports')

baseline=json.loads((OPS/'baseline-manifest.json').read_text())
relocated={r['historical_path']:r for r in baseline['relocations']}
for p,h in baseline['p19_historical_artifact_hashes'].items():
    target=ROOT/p
    if sha(target)!=h and p in relocated:target=ROOT/relocated[p]['preserved_path']
    check(sha(target)==h,'P19 historical byte preservation '+p)
for p,h in baseline['input_hashes'].items():check(sha(ROOT/p)==h,'additional baseline preservation '+p)
result={'command':['python3',str(Path(__file__).relative_to(ROOT))],'wall_seconds':time.monotonic()-start,
        'artifact':str(CASE.relative_to(ROOT)),'artifact_sha256':sha(CASE),'checks':checks,
        'passed':sum(r['passed'] for r in checks),'failed':sum(not r['passed'] for r in checks),
        'limits':'Source/arithmetic/preservation checks; no full semantics, human admission, accounting compliance or runtime claim.'}
(OPS/'case-checks-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print({k:result[k] for k in ['passed','failed','wall_seconds']})
assert result['failed']==0,[x for x in checks if not x['passed']]
